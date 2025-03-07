---
id: 1132
title: Stopping Garbage Collection in .NET Core 3.0 (part II)
date: 2019-01-21T10:05:45+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/?p=1132
timeline_notification:
  - "1548065149"
description: "Ever wanted to tell the garbage collector to take a vacation? Here's how to put GC on pause in .NET Core 3.0, complete with event listeners and safety nets. Warning: contains dark runtime magic and questionable exception handling practices that we somehow got away with"
categories:
  - .NET Core
tags:
  - csharp
---
Let's see how it's implemented. For why it is implemented, see part I.

Thanks to [Mike](https://github.com/mjrousos) for reviewing this.

~~~csharp
using System;
using System.Diagnostics.Tracing;
using System.Runtime;
~~~
The FxCop code analyzers get upset if I don't declare this, which also impede me from using unsigned numeral types in interfaces.

~~~csharp
[assembly: CLSCompliant(true)]

namespace LNativeMemory
{
~~~
The first piece of the puzzle is to implement an event listener. It is a not-obvious (for me) class. I don't fully
understand the lifetime semantics, but the code below seems to do the right thing.

The interesting piece is `_started` and the method `Start()`. The constructor for `EventListener` allocates plenty of stuff. I don't want
to do those allocations after calling `TryStartNoGCRegion` because they would use part of the GC Heap that I want for my program.
Instead, I create it before such call, but then I make it 'switch on' just after the `Start()` method is called.
~~~csharp
    internal sealed class GcEventListener : EventListener
    {
        Action _action;
        EventSource _eventSource;
        bool _active = false;

        internal void Start() { _active = true; }
        internal void Stop() { _active = false; }
~~~
As described in part one, you pass a delegate at creation time, which is called when garbage collection is restarted.
~~~csharp
        internal GcEventListener(Action action) => _action = action ?? throw new ArgumentNullException(nameof(action));
~~~
We register to all the events coming from .NET. We want to call the delegate at the exact point when garbage collection is turned on again.
We don't have a clean way to do that (aka there is no runtime event we can hook up to, see [here](https://github.com/dotnet/coreclr/issues/21750),
so listening to every single GC event gives us the most chances of doing it right. Also it ties us the least to any pattern of events, which
might change in the future.
~~~csharp
        // from https://docs.microsoft.com/en-us/dotnet/framework/performance/garbage-collection-etw-events
        private const int GC_KEYWORD = 0x0000001;
        private const int TYPE_KEYWORD = 0x0080000;
        private const int GCHEAPANDTYPENAMES_KEYWORD = 0x1000000;

        protected override void OnEventSourceCreated(EventSource eventSource)
        {
            if (eventSource.Name.Equals("Microsoft-Windows-DotNETRuntime", StringComparison.Ordinal))
            {
                _eventSource = eventSource;
                EnableEvents(eventSource, EventLevel.Verbose, (EventKeywords)(GC_KEYWORD | GCHEAPANDTYPENAMES_KEYWORD | TYPE_KEYWORD));
            }
        }
~~~

For each event, I check if the garbage collector has exited the NoGC region. If it has, then let's invoke the delegate.


~~~csharp
        protected override void OnEventWritten(EventWrittenEventArgs eventData)
        {
            var eventName = eventData.EventName;
            if(_active && GCSettings.LatencyMode != GCLatencyMode.NoGCRegion)
            {
                _action?.Invoke();
            }
        }
    }
~~~
Now that we have our event listener, we need to hook it up. The code below implements what I described earlier.

1. Do your allocations for the event listener
2. Start the NoGc region
3. Start monitoring the runtime for the start of the NoGC region
~~~csharp
    public static class GC2
    {
        static private GcEventListener _evListener;

        public static bool TryStartNoGCRegion(long totalSize, Action actionWhenAllocatedMore)
        {

            _evListener = new GcEventListener(actionWhenAllocatedMore);
            var succeeded = GC.TryStartNoGCRegion(totalSize, disallowFullBlockingGC: false);
            _evListener.Start();

            return succeeded;
        }
~~~

As puzzling as this might be, I provisionally believe it to be correct. Apparently, even if the GC is not in a NoGC region, you still need to call
`EndNoGCRegion` if you have called `TryStartNoGCRegion` earlier, otherwise your next call to `TryStartNoGCRegion` will fail.
`EndNoGCRegion` will throw an exception, but that's OK. Your next call to `TryStartNoGCRegion` will now succeed.

Now read the above repeatedly until you got. Or just trust that it works somehow.


~~~csharp
        public static void EndNoGCRegion()
        {
            _evListener.Stop();

            try
            {
                GC.EndNoGCRegion();
            } catch (Exception)
            {

            }
        }
    }
~~~
This is used as the default behavior for the delegate in the wrapper class below.
I was made aware by the code analyzer that I shouldn't be throwing an OOF exception here. At first, I dismissed it, but then it hit me. It is right.

We are not running out of memory here. We simply have allocated more memory than what we declared we would. There is likely plenty of memory left
on the machine. Thinking more about it, I grew ashamed of my initial reaction. Think about a support engineer getting an OOM exception at that point
and trying to figure out why. So, always listen to Lint ...
~~~csharp
    public class OutOfGCHeapMemoryException : OutOfMemoryException {
        public OutOfGCHeapMemoryException(string message) : base(message) { }
        public OutOfGCHeapMemoryException(string message, Exception innerException) : base(message, innerException) { }
        public OutOfGCHeapMemoryException() : base() { }

    }


~~~
This is an utility class that implements the `IDisposable` pattern for this scenario. The size of the default ephemeral segment comes from
[here](https://docs.microsoft.com/en-us/dotnet/standard/garbage-collection/fundamentals#generations).
~~~csharp
    public sealed class NoGCRegion: IDisposable
    {
        static readonly Action defaultErrorF = () => throw new OutOfGCHeapMemoryException();
        const int safeEphemeralSegment = 16 * 1024 * 1024;

        public NoGCRegion(int totalSize, Action actionWhenAllocatedMore)
        {
            var succeeded = GC2.TryStartNoGCRegion(totalSize, actionWhenAllocatedMore);
            if (!succeeded)
                throw new InvalidOperationException("Cannot enter NoGCRegion");
        }

        public NoGCRegion(int totalSize) : this(totalSize, defaultErrorF) { }
        public NoGCRegion() : this(safeEphemeralSegment, defaultErrorF) { }

        public void Dispose() => GC2.EndNoGCRegion();
    }
}
~~~
