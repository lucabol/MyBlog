---
title: Meta-programming in C# with JIT dead code removal and inlining
date: 2019-01-29
author: lucabol
layout: post
tags:
  - csharp
---
# Abstract

Thanks to [Mike](https://github.com/mjrousos) for reviewing this.

This is a way to enable compile time customization of classes/functions in the style of C++ template meta-programming as in [Modern C++ Design](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design).
In particular, we are going to implement the [policy pattern](https://en.wikipedia.org/wiki/Modern_C%2B%2B_Design#Policy-based_design), which is compile time version of the [strategy pattern](https://en.wikipedia.org/wiki/Strategy_pattern).

What do we gain by constraining ourselves to compile time customization, instead of run time one? High performance. Blazingly high performance. You gain an abstraction, without paying for it.

Too good to be true? Read on!

BTW1: none of this is new. It has been floating around in various forms. But I have never seen explained fully and associated to the policy pattern.
BTW2: it is also related to the uber cool [Shape proposal for C#](https://github.com/dotnet/csharplang/issues/164), where it becomes an implementation detail.

# Implementation

First, the usual plethora of namespaces ... BenchmarkDotNet is really heavy into separating abstractions in different namespaces ...

~~~csharp
using System.Runtime.CompilerServices;
using System.Threading;

using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Diagnosers;
using BenchmarkDotNet.Diagnostics.Windows.Configs;
using BenchmarkDotNet.Mathematics;
using BenchmarkDotNet.Order;
using BenchmarkDotNet.Running;
~~~

Let's take a look at the strategy pattern, as more traditionally implemented. You got an interface `IIncrementer` and two implementations, either thread safe or not.
Let's also add a couple of struct implementations so that we can measure the performance difference of implementation by classes and by structs.

~~~csharp
public interface IIncrementer { void Increment(ref int location); }

public sealed class CStandardIncrementer        : IIncrementer {[MethodImpl(MethodImplOptions.AggressiveInlining)] public void Increment(ref int location) => location += 1; }
public sealed class CInterlockedIncrementer     : IIncrementer {[MethodImpl(MethodImplOptions.AggressiveInlining)] public void Increment(ref int location) => Interlocked.Increment(ref location); }

public readonly struct SStandardIncrementer     : IIncrementer {[MethodImpl(MethodImplOptions.AggressiveInlining)] public void Increment(ref int location) => location += 1; }
public readonly struct SInterlockedIncrementer  : IIncrementer {[MethodImpl(MethodImplOptions.AggressiveInlining)] public void Increment(ref int location) => Interlocked.Increment(ref location); }
~~~

We then need a class that can be customized by an Incrementer. Think of it as: the policy of incrementing something is independent from the class in question.

Let's take a Counter and call it Dynamic as we want to be able to customize it at runtime. We need to keep things simple so that looking at ASM is doable.
Also we inline everything to try to squeeze the most performance out of our program.

~~~csharp
public class DynamicCounter<T> where T: IIncrementer
{
    int _count;
    T _incrementer;

    public DynamicCounter(T incrementer) => _incrementer = incrementer;

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void Increment() => _incrementer.Increment(ref _count);
}
~~~

Then we look at how to implement the strategy pattern at compile time (transforming it magically into the policy pattern).

(no-one every talks about the negative aspects of giving names to things, one of these days I'll blog about it ...)

There are many ways to go about it. They all rely on the fact that the JIT Compiler instantiates a different type for each struct used to customize the type (aka each `T`).

For each one of these types, the JIT knows at compile type what `T` is, which brings about certain optimizations.

The optimization exploited by `StaticCounterInterface` is that the call to `Increment` becomes a non-virtual call that can be inlined.

~~~csharp
public class StaticCounterInterface<T> where T : struct, IIncrementer
{
    int _count;
    T _incrementer = new T();

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void Increment() => _incrementer.Increment(ref _count);
}
~~~

For `StaticCounterMatch` the situation is even more obvious.

The Jitter doesn't generate code for any of the `if` statements. It just puts the right code for the type `T` directly in the body of the `Increment` method.

It is as if the `if` statement were executed at compile time, as with `C++` templates. Also notice the `IncrementRaw` method used for perf comparison.

~~~csharp
public class StaticCounterMatch<T>
{
    int _count;

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void Increment() {
        if (typeof(T) == typeof(SStandardIncrementer))      _count += 1;
        if (typeof(T) == typeof(SInterlockedIncrementer))   Interlocked.Increment(ref _count);
    }

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    public void IncrementRaw() => _count += 1;
}
~~~

We are now ready for the performance testing. We create one class for each combination and benchmark their Increment method.

A few comments on the attributes:
1. `DryCoreJob` doesn't do the benchmark, but just runs the diagnosers, in this case produces assembly code.
2. `InProcessAttribute` makes everything go faster, but cannot be used to generate assembly.
3. `DisassemblyDiagnoser` creates files with the assembly code.
4. `RankColumn` generates a nicer table.

~~~csharp
//[DryCoreJob]
//[InProcessAttribute]
[DisassemblyDiagnoser(printAsm: true, printPrologAndEpilog: true, printIL: false, printSource: false, recursiveDepth: 3)]
[Orderer(SummaryOrderPolicy.FastestToSlowest)]
[RankColumn(NumeralSystem.Stars)]
public  class MainClass
{
    DynamicCounter<IIncrementer>         dynInterface           = new DynamicCounter<IIncrementer>(new CStandardIncrementer());
    DynamicCounter<CStandardIncrementer> dynConcrete            = new DynamicCounter<CStandardIncrementer>(new CStandardIncrementer());
    DynamicCounter<SStandardIncrementer> dynStruct              = new DynamicCounter<SStandardIncrementer>(new SStandardIncrementer());
    StaticCounterMatch<SStandardIncrementer> staticCounterM     = new StaticCounterMatch<SStandardIncrementer>();
    StaticCounterInterface<SStandardIncrementer> staticCounterI = new StaticCounterInterface<SStandardIncrementer>();

    [Benchmark] public void DynamicInterface()                      => dynInterface.Increment();
    [Benchmark] public void DynamicConcrete()                       => dynConcrete.Increment();
    [Benchmark] public void DynamicStruct()                         => dynStruct.Increment();
    [Benchmark] public void StaticCounterInterface()                => staticCounterI.Increment();
    [Benchmark] public void StaticCounterMatch()                    => staticCounterM.Increment();
    [Benchmark(Baseline = true)] public void IncrementRaw()         => staticCounterM.IncrementRaw();

    public static void Main() => BenchmarkRunner.Run<MainClass>();
}
~~~

# Results

Please note that the results are valid just for the tested configuration.

I have no reason to think that they would be different on other modern runtimes/OSs as the optimizations are quite well known.

``` ini

BenchmarkDotNet=v0.11.3, OS=Windows 10.0.17763.253 (1809/October2018Update/Redstone5)
Intel Core i7-6600U CPU 2.60GHz (Skylake), 1 CPU, 4 logical and 2 physical cores
.NET Core SDK=3.0.100-preview-009812
  [Host]     : .NET Core 2.0.9 (CoreCLR 4.6.26614.01, CoreFX 4.6.26614.01), 64bit RyuJIT
  DefaultJob : .NET Core 2.0.9 (CoreCLR 4.6.26614.01, CoreFX 4.6.26614.01), 64bit RyuJIT


```
|                 Method |      Mean |     Error |    StdDev |    Median |  Ratio | RatioSD |  Rank |
|----------------------- |----------:|----------:|----------:|----------:|-------:|--------:|------:|
| StaticCounterInterface | 0.0000 ns | 0.0000 ns | 0.0000 ns | 0.0000 ns |  0.000 |    0.00 |     * |
|           IncrementRaw | 0.1036 ns | 0.0515 ns | 0.0573 ns | 0.1071 ns |  1.000 |    0.00 |    ** |
|     StaticCounterMatch | 0.1122 ns | 0.0422 ns | 0.0943 ns | 0.1020 ns |  2.092 |    1.95 |    ** |
|          DynamicStruct | 0.2707 ns | 0.0910 ns | 0.2683 ns | 0.1407 ns |  4.135 |    6.28 |   *** |
|        DynamicConcrete | 1.9216 ns | 0.1506 ns | 0.4440 ns | 1.7883 ns | 23.417 |   21.44 |  **** |
|       DynamicInterface | 2.2441 ns | 0.1170 ns | 0.3449 ns | 2.1470 ns | 32.783 |   30.52 | ***** |

As expected, you gain an order of magnitude in performance by foregoing run time customization, except when using a `struct` as the optimizer manages to inline that one (as we'll see).

Notice that these numbers are really low. In fact the order of the first 4 lines might change when you run it. But they are always much faster than the rest.

But why? Let's look at the generated code.

# IL and ASM

First let's look at IL for a few of the methods
~~~assembly
MainClass.IncrementRaw()
       IL_0000: ldarg.0
       IL_0001: ldfld StaticCounterMatch`1<SStandardIncrementer> MainClass::staticCounterM
       IL_0006: callvirt System.Void StaticCounterMatch`1<SStandardIncrementer>::IncrementRaw()
       IL_000b: ret

; MainClass.StaticCounterInterface()
       IL_0000: ldarg.0
       IL_0001: ldfld StaticCounterInterface`1<SStandardIncrementer> MainClass::staticCounterI
       IL_0006: callvirt System.Void StaticCounterInterface`1<SStandardIncrementer>::Increment()
       IL_000b: ret

; MainClass.StaticCounterMatch()
       IL_0000: ldarg.0
       IL_0001: ldfld StaticCounterMatch`1<SStandardIncrementer> MainClass::staticCounterM
       IL_0006: callvirt System.Void StaticCounterMatch`1<SStandardIncrementer>::Increment()
       IL_000b: ret
~~~
Ok, nothing interesting there apart from the use of `callvirt` when you would think a standard `call` would do (i.e. `IncrementRaw`).

I vaguely remember from my C# compiler days that we do that as a way to short-circuit the test for null, as `callvirt` does it automatically.

The assembly code is more interesting. Let's start from the three fast-resolved-at-compile-time methods.

BTW: remember that looking at optimized ASM code is like peering into a muddy lake with foggy glasses. Let's do it.

~~~assembly
; MainClass.IncrementRaw()
       mov     rax,qword ptr [rcx+20h]
       inc     dword ptr [rax+8]
       ret

; MainClass.StaticCounterInterface()
       mov     rax,qword ptr [rcx+28h]
       (*)mov     edx,dword ptr [rax]
       add     rax,8
       inc     dword ptr [rax]
       ret

; MainClass.StaticCounterMatch()
       mov     rax,qword ptr [rcx+20h]
       (*)mov     edx,dword ptr [rax]
       inc     dword ptr [rax+8]
       ret

; MainClass.DynamicStruct()
       mov     rax,qword ptr [rcx+18h]
       (*) mov     edx,dword ptr [rax]
       add     rax,8
       inc     dword ptr [rax]
       ret
~~~

Yep, they are all the same (apart from the mysterious `*` instruction)! Get the memory location of the field, increment it.

The Jitter has completely inlined the code. It is as if you had written the incrementing code directly into the function, despite you composing the type using two independent abstractions.

I think that is pretty cool! You can abstract your code properly and not pay the price for it (well, apart from one assembly instruction).

For the sake of completeness, let's look at the assembly code for the dynamic dispatching cases.

~~~assemlby
; MainClass.DynamicConcrete()
       mov     rcx,qword ptr [rcx+10h]
       cmp     dword ptr [rcx],ecx
       lea     rdx,[rcx+10h]
       mov     rcx,qword ptr [rcx+8]
       mov     r11,7FF8C2B30470h
       mov     rax,qword ptr [r11]
       cmp     dword ptr [rcx],ecx
       jmp     rax

; MainClass.DynamicInterface()
       mov     rcx,qword ptr [rcx+8]
       cmp     dword ptr [rcx],ecx
       lea     rdx,[rcx+10h]
       mov     rcx,qword ptr [rcx+8]
       mov     r11,7FF8C2B10470h
       mov     rax,qword ptr [r11]
       cmp     dword ptr [rcx],ecx
       jmp     rax

~~~

The first thing to notice is that the code is identical, despite their seemingly different declarations. The Jitter doesn't care.

Notice the machinations the Jitter performs, very likely related to dynamic dispatching, to calculate the address to finally jump to. That's where our Increment method is located.

No wonder it is slower.

# Summary

If you can afford to use the policy pattern instead of the more generic strategy pattern (i.e. compile time vs run time dispatch) and/or you need bare to the metal performance, consider the code above.

As for me, I plan to use it in the near future for a few low level abstractions (i.e. memory allocators).
