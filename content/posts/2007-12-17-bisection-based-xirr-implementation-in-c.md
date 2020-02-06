---
id: 583
title: 'Bisection-based XIRR implementation in C#'
date: 2007-12-17T18:17:00+00:00
author: lucabol
layout: post
guid: https://blogs.msdn.microsoft.com/lucabol/2007/12/17/bisection-based-xirr-implementation-in-c/
permalink: /2007/12/17/bisection-based-xirr-implementation-in-c/
orig_url:
  - http://blogs.msdn.microsoft.com/b/lucabol/archive/2007/12/17/bisection-based-xirr-implementation-in-c.aspx
orig_site_id:
  - "3896"
orig_post_id:
  - "6793053"
orig_parent_id:
  - "6793053"
orig_thread_id:
  - "553534"
orig_application_key:
  - lucabol
orig_post_author_id:
  - "3896"
orig_post_author_username:
  - lucabol
orig_post_author_created:
  - 'Apr  2 2005 10:57:56:453AM'
orig_is_approved:
  - "1"
orig_attachment_count:
  - "0"
orig_url_title:
  - http://blogs.msdn.com/b/lucabol/archive/2007/12/17/bisection-based-xirr-implementation-in-c.aspx
opengraph_tags:
  - |
    <meta property="og:type" content="article" />
    <meta property="og:title" content="Bisection-based XIRR implementation in C#" />
    <meta property="og:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/17/bisection-based-xirr-implementation-in-c/" />
    <meta property="og:site_name" content="Luca Bolognese&#039;s WebLog" />
    <meta property="og:description" content="Here is a quick implementation of XIRR (using Excel nomenclature) written in C#. Disclaimer: this is a super simple Bisection-based implementation. People tend to prefer the Newton method, but this is simpler and works for the app I'm writing. I decided to post it because I couldn't find one on the net when I looked..." />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Bisection-based XIRR implementation in C#" />
    <meta name="twitter:url" content="https://blogs.msdn.microsoft.com/lucabol/2007/12/17/bisection-based-xirr-implementation-in-c/" />
    <meta name="twitter:description" content="Here is a quick implementation of XIRR (using Excel nomenclature) written in C#. Disclaimer: this is a super simple Bisection-based implementation. People tend to prefer the Newton method, but this is simpler and works for the app I'm writing. I decided to post it because I couldn't find one on the net when I looked..." />
    
restapi_import_id:
  - 5c011e0505e67
categories:
  - Uncategorized
tags:
  - csharp
  - Financial
---
Here is a quick implementation of XIRR (using Excel nomenclature) written in C#.

Disclaimer: this is a super simple Bisection-based implementation. People tend to prefer the Newton method, but this is simpler and works for the app I'm writing. I decided to post it because I couldn't find one on the net when I looked for it. I attached testcases to show the extent of my testing.

It is called CalculateXIRR and it is invoked by passing a list of cash flows, a tolerance and a max number of iterations.

~~~csharp
using System;

using System.Linq;

using Money = System.Decimal;

using Rate = System.Double;

using System.Collections.Generic;
public

 struct Pair<T, Z> {
public Pair(T first, Z second) { First = first; Second = second; }

public readonly T First;

public readonly Z Second;

}


public class CashFlow {

public CashFlow(Money amount, DateTime date) { Amount = amount; Date = date; }

public readonly Money Amount;
public readonly DateTime Date;
}

public struct AlgorithmResult<TKindOfResult, TValue> {

public AlgorithmResult(TKindOfResult kind, TValue value) {

Kind = kind;
Value = value;
}

public readonly TKindOfResult Kind;
public readonly TValue Value;
}

public enum ApproximateResultKind {
ApproximateSolution,
ExactSolution,
NoSolutionWithinTolerance
}

public static class Algorithms {

internal static Money CalculateXNPV(IEnumerable<CashFlow> cfs, Rate r) {

if (r <= -1)
r= -0.99999999; // Very funky ... Better check what an IRR <= -100% means

return (from cf in cfs
let startDate = cfs.OrderBy(cf1 => cf1.Date).First().Date
select cf.Amount / (decimal) Math.Pow(1 + r, (cf.Date - startDate).Days / 365.0)).Sum();
}

internal static Pair<Rate, Rate> FindBrackets(Func<IEnumerable<CashFlow>, Rate, Money> func, IEnumerable<CashFlow> cfs) {

// Abracadabra magic numbers ...
const int maxIter = 100;
const Rate bracketStep = 0.5;
const Rate guess = 0.1;

Rate leftBracket = guess - bracketStep;
Rate rightBracket = guess + bracketStep;
var iter = 0;

while (func(cfs, leftBracket) * func(cfs, rightBracket) > 0 && iter++ < maxIter) {

leftBracket -= bracketStep;
rightBracket += bracketStep;
}

if (iter >= maxIter)
return new Pair<double, double>(0, 0);

return new Pair<Rate, Rate>(leftBracket, rightBracket);
}

// From "Applied Numerical Analyis" by Gerald
internal static AlgorithmResult<ApproximateResultKind, Rate> Bisection(Func<Rate, Money> func, Pair<Rate, Rate> brackets, Rate tol, int maxIters) {

int iter = 1;

Money f3 = 0;
Rate x3 = 0;
Rate x1 = brackets.First;
Rate x2 = brackets.Second;

do {
var f1 = func(x1);
var f2 = func(x2);

if (f1 == 0 && f2 == 0)
return new AlgorithmResult<ApproximateResultKind, Rate>(ApproximateResultKind.NoSolutionWithinTolerance, x1);

if (f1 * f2 > 0)
throw new ArgumentException("x1 x2 values don't bracket a root");

x3 = (x1 + x2) / 2;
f3 = func(x3);

if (f3 * f1 < 0)
x2 = x3;
else
x1 = x3;

iter++;

} while (Math.Abs(x1 - x2)/2 > tol && f3 != 0 && iter < maxIters);

if (f3 == 0)
return new AlgorithmResult<ApproximateResultKind, Rate>(ApproximateResultKind.ExactSolution, x3);

if (Math.Abs(x1 - x2) / 2 < tol)
return new AlgorithmResult<ApproximateResultKind, Rate>(ApproximateResultKind.ApproximateSolution, x3);

if (iter > maxIters)
return new AlgorithmResult<ApproximateResultKind, Rate>(ApproximateResultKind.NoSolutionWithinTolerance, x3);

throw new Exception("It should never get here");
}

public static AlgorithmResult<ApproximateResultKind, Rate> CalculateXIRR(IEnumerable<CashFlow> cfs, Rate tolerance, int maxIters) {

var brackets = FindBrackets(CalculateXNPV, cfs);

if (brackets.First == brackets.Second)
return new AlgorithmResult<ApproximateResultKind, double>(ApproximateResultKind.NoSolutionWithinTolerance, brackets.First);

return Bisection(r => CalculateXNPV(cfs,r), brackets, tolerance, maxIters);
}
}

// TESTS
using Microsoft.VisualStudio.TestTools.UnitTesting;

using System.Collections.Generic;

using System;

using Rate = System.Double;
namespace TimeLineTest
{
[TestClass()]
public class AlgorithmsTest {

IEnumerable<CashFlow> cfs = new CashFlow[] {
new CashFlow(-10000, new DateTime(2008,1,1)),
new CashFlow(2750, new DateTime(2008,3,1)),
new CashFlow(4250, new DateTime(2008,10,30)),
new CashFlow(3250, new DateTime(2009,2,15)),
new CashFlow(2750, new DateTime(2009,4,1))
};

IEnumerable<CashFlow> bigcfs = new CashFlow[] {
new CashFlow(-10, new DateTime(2000,1,1)),
new CashFlow(10, new DateTime(2002,1,2)),
new CashFlow(20, new DateTime(2003,1,3))
};

IEnumerable<CashFlow> negcfs = new CashFlow[] {
new CashFlow(-10, new DateTime(2000,1,1)),
new CashFlow(-1, new DateTime(2002,1,2)),
new CashFlow(1, new DateTime(2003,1,3))
};

IEnumerable<CashFlow> samedaysamecfs = new CashFlow[] {
new CashFlow(-10, new DateTime(2000,1,1)),
new CashFlow(10, new DateTime(2000,1,1)),
};

IEnumerable<CashFlow> samedaydifferentcfs = new CashFlow[] {
new CashFlow(-10, new DateTime(2000,1,1)),
new CashFlow(100, new DateTime(2000,1,1)),
};

IEnumerable<CashFlow> bigratecfs = new CashFlow[] {
new CashFlow(-10, new DateTime(2000,1,1)),
new CashFlow(20, new DateTime(2000,5,30)),
};

IEnumerable<CashFlow> zeroRate = new CashFlow[] {
new CashFlow(-10, new DateTime(2000,1,1)),
new CashFlow(10, new DateTime(2003,1,1)),
};

IEnumerable<CashFlow> doubleNegative = new CashFlow[] {
new CashFlow(-10000, new DateTime(2008,1,1)),
new CashFlow(2750, new DateTime(2008,3,1)),
new CashFlow(-4250, new DateTime(2008,10,30)),
new CashFlow(3250, new DateTime(2009,2,15)),
new CashFlow(2750, new DateTime(2009,4,1))
};

IEnumerable<CashFlow> badDoubleNegative = new CashFlow[] {
new CashFlow(-10000, new DateTime(2008,1,1)),
new CashFlow(2750, new DateTime(2008,3,1)),
new CashFlow(-4250, new DateTime(2008,10,30)),
new CashFlow(3250, new DateTime(2009,2,15)),
new CashFlow(-2750, new DateTime(2009,4,1))
};

double r = 0.09;
double tolerance = 0.0001;
int maxIters = 100;

private TestContext testContextInstance;

public TestContext TestContext {
get {
return testContextInstance;
}
set {
testContextInstance = value;
}
}

[TestMethod()]
public void CalculateXNPV() {

Assert.AreEqual(2086.6476020315416570634272814M, Algorithms.CalculateXNPV(cfs, r));
Assert.AreEqual(-10.148147600710372651326920258M, Algorithms.CalculateXNPV(negcfs, 0.5));
Assert.AreEqual(4.9923725815954514810351876895M, Algorithms.CalculateXNPV(bigcfs, 0.3));
}

[TestMethod]
public void FindBrackets() {

var brackets = Algorithms.FindBrackets(Algorithms.CalculateXNPV, cfs);
Assert.IsTrue(brackets.First < 0.3733 && brackets.Second > 0.3733);

brackets = Algorithms.FindBrackets(Algorithms.CalculateXNPV, bigcfs);
Assert.IsTrue(brackets.First < 0.5196 && brackets.Second > 0.5196);

brackets = Algorithms.FindBrackets(Algorithms.CalculateXNPV, negcfs);
Assert.IsTrue(brackets.First < -0.6059 && brackets.Second > -0.6059);
}

[TestMethod]
public void XIRRTest() {

var irr = Algorithms.CalculateXIRR(cfs, tolerance, maxIters);
Assert.AreEqual(0.3733, irr.Value, 0.001);
Assert.AreEqual(ApproximateResultKind.ApproximateSolution, irr.Kind);

irr = Algorithms.CalculateXIRR(bigcfs, tolerance, maxIters);
Assert.AreEqual(0.5196, irr.Value, 0.001);
Assert.AreEqual(ApproximateResultKind.ApproximateSolution, irr.Kind);

irr = Algorithms.CalculateXIRR(negcfs, tolerance, maxIters);
Assert.AreEqual(-0.6059, irr.Value, 0.001);
Assert.AreEqual(ApproximateResultKind.ApproximateSolution, irr.Kind);

irr = Algorithms.CalculateXIRR(samedaysamecfs, tolerance, maxIters);
Assert.AreEqual(ApproximateResultKind.NoSolutionWithinTolerance, irr.Kind);

irr = Algorithms.CalculateXIRR(samedaydifferentcfs, tolerance, maxIters);
Assert.AreEqual(ApproximateResultKind.NoSolutionWithinTolerance, irr.Kind);

irr = Algorithms.CalculateXIRR(bigratecfs, tolerance, maxIters);
Assert.AreEqual(4.40140, irr.Value, 0.001);
Assert.AreEqual(ApproximateResultKind.ApproximateSolution, irr.Kind);

irr = Algorithms.CalculateXIRR(zeroRate, tolerance, maxIters);
Assert.AreEqual(0, irr.Value, 0.001);
Assert.AreEqual(ApproximateResultKind.ApproximateSolution, irr.Kind);

irr = Algorithms.CalculateXIRR(doubleNegative, tolerance, maxIters);
Assert.AreEqual(-0.537055, irr.Value, 0.001);
Assert.AreEqual(ApproximateResultKind.ApproximateSolution, irr.Kind);

irr = Algorithms.CalculateXIRR(badDoubleNegative, tolerance, maxIters);
Assert.AreEqual(ApproximateResultKind.NoSolutionWithinTolerance, irr.Kind);
}
}
}
~~~