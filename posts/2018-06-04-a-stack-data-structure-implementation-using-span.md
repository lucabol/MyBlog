---
id: 294
title: A Stack data structure implementation using Span
date: 2018-06-04T11:56:54+00:00
author: lucabol
excerpt: This Stack data structure can be used over memory that resides on the stack, heap or unmanaged heap. If you know about Span this should immediately make sense to you.
layout: post
guid: https://lucabolognese.wordpress.com/?p=294
timeline_notification:
  - "1528113420"
tags:
  - csharp
---
I am back in Microsoft and today we talk about the code below, which is on github here:
```csharp
public ref struct SpanStack<T>
{
    private Span memory;
    private int index;
    private int size;

    public SpanStack(Span mem) { memory = mem; index = 0; size = mem.Length; }

    public bool IsEmpty() => index < 0;
    public bool IsFull() => index > size - 1;

    public void Push(T item) => memory[index++] = item;
    public T Pop() => memory[--index];
}

public static class SpanExtensions
{
    public static SpanStack AsStack<T>(this Span span) => new SpanStack(span);
}
```
This Stack data structure can be used over memory that resides on the stack, heap or unmanaged heap. If you know about Span this should immediately make sense to you.

This has to be a ref struct because it contains a Span. It can't be used on the heap (i.e. in lambdas, async, class field, ...). You have to build it on top of Memory if you need that. Also, you can happily blow the stack with this guy ...

Let's micro-benchmark it with BenchmarkDotNet.  For example, a postfix calculator. Let's first do it naively using inheritance and the generic Stack class in the framework.

This is the naive object model:
```csharp
abstract class Token {}

sealed class Operand: Token
{
    public int Value { get; }
    public Operand(int v) { Value = v; }
}

abstract class Operator: Token {
    abstract public int Calc(int a, int b);
}

sealed class Add: Operator
{
    public override int Calc(int a, int b) => a + b;
}

sealed class Mult : Operator
{
    public override int Calc(int a, int b) => a * b;
}

sealed class Minus : Operator
{
    public override int Calc(int a, int b) => a - b;
}
Let's then do it trying to be a bit more performance aware using a stack friendly representation:

public enum TokenType { Operand, Sum, Mult, Minus}

readonly struct SToken
{
    public TokenType Type { get; }
    public int Value { get; }
    public SToken(TokenType t, int v) { Type = t; Value = v; }
    public SToken(TokenType t) { Type = t; Value = 0; }

    public int Calc(int a, int b) =>
               Type == TokenType.Sum   ? a + b :
               Type == TokenType.Minus ? a - b :
               Type == TokenType.Minus ? a * b :
               throw new Exception("I don't know that one");

}
```
Perhaps not overtly elegant, but not that terrible either. You got to love those expression bodied methods and throw-expression.

We then setup things (I know I could/should parse a string here):
```csharp
static Token[] tokens;
static SToken[] stokens;

[GlobalSetup]
public void Setup()
{
    tokens = new Token[] { new Operand(2), new Operand(3), new Operand(4), new Add(),
                           new Mult(), new Operand(5), new Minus() };
    stokens = new SToken[] { new SToken(TokenType.Operand, 2),
                             new SToken(TokenType.Operand, 3), new SToken(TokenType.Operand, 4),
                             new SToken(TokenType.Sum),  new SToken(TokenType.Mult),
                             new SToken(TokenType.Operand, 5), new SToken(TokenType.Minus)};
}
```
And first test the naive object model with the standard Stack from System.Collections.Generic.
```csharp
[Benchmark]
public int PostfixEvalStack()
{
    var stack = new Stack(100);

    foreach (var token in tokens)
    {
        switch (token)
        {
            case Operand t:
                stack.Push(t);
                break;
            case Operator o:
                var a = stack.Pop() as Operand;
                var b = stack.Pop() as Operand;
                var result = o.Calc(a.Value, b.Value);
                stack.Push(new Operand(result));
                break;
        }
    }
    return (stack.Pop() as Operand).Value;
}
```
Then let's just swap out our own lean-and-mean stack:
```csharp
[Benchmark]
public int PostfixEvalSpanStack()
{
    Span span = new Token[100];
    var stack = span.AsStack();

    foreach (var token in tokens)
    {
        switch (token)
        {
            case Operand t:
                stack.Push(t);
                break;
            case Operator o:
                var a = stack.Pop() as Operand;
                var b = stack.Pop() as Operand;
                var result = o.Calc(a.Value, b.Value);
                stack.Push(new Operand(result));
                break;
        }
    }
    return (stack.Pop() as Operand).Value;
}
```
And finally let's go the whole way, lean object model and lean data structure, everything on the stack:
```csharp
[Benchmark(Baseline = true)]
public int PostfixEvalSpanStackStructTypes()
{
    Span span = stackalloc SToken[100];
    var stack = span.AsStack();

    foreach (var token in stokens)
    {
        if (token.Type == TokenType.Operand)
        {
            stack.Push(token);
        } else {
            var a = stack.Pop();
            var b = stack.Pop();
            var result = token.Calc(a.Value, b.Value);
            stack.Push(new SToken(TokenType.Operand, result));
            break;
        }
    }
    return stack.Pop().Value;
}
```
We also want to check that we didn't code anything stupid and finally run the benchmark.
```csharp
static void Test()
{
    var p = new Program();
    p.Setup();
    Trace.Assert(p.PostfixEvalStack() == p.PostfixEvalSpanStack() &&
                 p.PostfixEvalSpanStack() == p.PostfixEvalSpanStackStructTypes());
}
static void Main(string[] args)
{
    Test();
    var summary = BenchmarkRunner.Run();
}
```
On my machine I get these results:

```
BenchmarkDotNet=v0.10.14, OS=Windows 10.0.16299.431 (1709/FallCreatorsUpdate/Redstone3)
Intel Core i7-6600U CPU 2.60GHz (Skylake), 1 CPU, 4 logical and 2 physical cores
Frequency=2742185 Hz, Resolution=364.6727 ns, Timer=TSC
.NET Core SDK=2.1.300-rc1-008673
  [Host]     : .NET Core 2.1.0-rc1 (CoreCLR 4.6.26426.02, CoreFX 4.6.26426.04), 64bit RyuJIT
  DefaultJob : .NET Core 2.1.0-rc1 (CoreCLR 4.6.26426.02, CoreFX 4.6.26426.04), 64bit RyuJIT
Method	Mean	Error	StdDev	Scaled	ScaledSD
PostfixEvalSpanStackStructTypes	76.24 ns	1.563 ns	2.857 ns	1.00	0.00
PostfixEvalSpanStack	168.65 ns	5.280 ns	15.319 ns	2.22	0.22
PostfixEvalStack	334.56 ns	7.387 ns	20.593 ns	4.39	0.31
```
Your mileage might vary. I want to emphasize that I am just playing with things. I haven't done any deep analysis of this benchmark. There can be flaws, etc... etc...

Still, I find the idea of data structures which are memory-location-independent rather fascinating.