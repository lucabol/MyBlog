---
title: Status of C# 8.0 functional features with a comparison to Haskell
date: 2019-12-06
author: lucabol
layout: post
tags:
  - csharp
  - functional-programming
---
# Abstract
Writing C# functional code has become easier with each new release of the language (i.e. nullable ref types, tuples, switch expr, ...).
This document presents a review of the current status of *basic* functional features for C# 8.0.
It focuses mostly on syntax and aims to achieve its goal using code examples.
It doesn't touches on more advanced topics as Monad, Functors, etc ...

Haskell has been chosen as the 'comparison' language (using few examples from [here](http://learnyouahaskell.com/) and elsewhere).
This is not intended as a statement of value of one language vs the other.
The languages are profoundly  different in underlying philosophies.
They both do much more than what is presented here (i.e. C# supports OO and imperative style, while Haskell goes much deeper in type system power etc...).

I also present samples of usage of [language-ext](https://github.com/louthy/language-ext) to show what can be achieved in C# using a functional library.


# Using a library of functions
In C# you can use static functions as if they were 'floating' by importing the static class they are defined to with the syntax `using static CLASSNAME`. Below an example of both importing `Console.WriteLine` and using it.

```csharp
using System;
using System.IO;

using LanguageExt;
using LanguageExt.TypeClasses;
using LanguageExt.ClassInstances;
using System.Collections.Generic;

using static System.Console;
using static System.Linq.Enumerable;
using static System.Math;
using static LanguageExt.Prelude;

public static class Core {

    static void UseFunc() => WriteLine("System.WriteLine as a floating function");
```

# Writing simple functions
In Haskell, a simple function might be written as:
```haskell
   square :: Num a => a -> a
   square x = x * x
```

Which in C# looks like the below.

```csharp
    static int Square(int x) => x * x; 
```

As an aside, note that we lose the generality of the function (i.e. we need a different one for doubles).This is due to the lack of ad-hoc polymorphism in C#.
By using language-ext, you can fake it so that it looks like this:

```csharp
    static A Square<NumA, A>(A x) where NumA : struct, Num<A> => default(NumA).Product(x, x);

    static void SquarePoly() {
        WriteLine(Square<TInt, int>(2));
        WriteLine(Square<TDouble, double>(2.5));
    }
```

In Haskell, it is conventional to write the type of a function before the function itself. In C# you can use `Func` and `Action` to
achieve a similar goal (aka seeing the types separately from the function implementation), despite with more verbose syntax, as below:

```csharp
    static Func<int, int> SquareF = x => x * x;
```

# Pattern matching
Here is an example in Haskell:

```haskell
    lucky :: (Integral a) => a -> String  
    lucky 7 = "LUCKY NUMBER SEVEN!"  
    lucky x = show x
```

In C#, you can write it in a few ways. Either as a function static property ...

```csharp
    static Func<int, string> Lucky = x => x switch {
            7 => "LUCKY NUMBER SEVEN!",
            _ => x.ToString()
        };
```

Or with a normal function:

```csharp
    static string Lucky1(int x) => x switch {
            7 => "LUCKY NUMBER SEVEN!",
            _ => x.ToString()
    };
```

Or even using the ternary operator (a perennial favorite of mine).

```csharp
    static string Lucky2(int x) => x == 7 ? "LUCKY NUMBER SEVEN!"
                                          : x.ToString();
```

Pattern matching on tuples works with similar syntax:

```csharp
    static bool And(bool x, bool y) =>
        (x, y) switch
        {
            (true, true) => true,
            _            => false
        };

    
```

        
In Haskell you can match on lists as follows:

```haskell
    sum :: Num a => [a] -> a
    sum [] = 0
    sum (x:xs) = x + sum xs
```
Writing this in standard C# looks like this:

```csharp
    static int Sum(IEnumerable<int> l) => l.Count() == 0
                                            ? 0
                                            : l.First() + Sum(l.Skip(1));

    static int Sum1(IEnumerable<int> l) => l.Count() switch {
        0 => 0,
        _ => l.First() + Sum(l.Skip(1))
    };
```

Language-ext gives you a simpler syntax, with more flexibility on what you can match against:

```csharp
    static int Sum2(Seq<int> l) =>
        match(l,
               () => 0,
               (x, xs) => x + Sum1(xs));
```

Obviously you always have to be careful with recursion in C# ([here](https://github.com/dotnet/csharplang/issues/2544)).
Better use the various methods on `Enumerable`.

# Guards (and case expressions)
Let's explore guards. Case expressions have an identical translation in C#.
            
In Haskell guards are used as below:

```haskell
    bmiTell :: (RealFloat a) => a -> a -> String  
    bmiTell weight height  
            | weight / height ^ 2 <= 18.5 = "Under"  
            | weight / height ^ 2 <= 25.0 = "Normal"  
            | weight / height ^ 2 <= 30.0 = "Over"  
            | otherwise                   = "Way over"
```
Which can be coded in C# as:

```csharp
    static string BmiTell(double weight, double height) =>
        (weight, height) switch
        {
            _ when Pow(weight / height, 2) <= 18.5 => "Under",
            _ when Pow(weight / height, 2) <= 25.0 => "Normal",
            _ when Pow(weight / height, 2) <= 30.0 => "Over",
            _                                      => "Way over"
        };
```

Obviously this is quite bad. You would like something more like:

```haskell
    bmiTell :: (RealFloat a) => a -> a -> String  
    bmiTell weight height  
            | bmi <= skinny = "Under"  
            | bmi <= normal = "Normal"  
            | bmi <= fat    = "Over"  
            | otherwise     = "Way Over"  
            where bmi = weight / height ^ 2  
                  skinny = 18.5  
                  normal = 25.0  
                  fat = 30.0 
```
But it is not trivial in C# to declare variables in expression bodied members.
You can either move it to a normal method or abuse the LINQ query syntax. Both shown below.
Notice that this is more similar to `let` expressions in Haskell, as they come before the expression, not after.

```csharp
    static string BmiTell1(double weight, double height) {
        double bmi = Pow(weight / height, 2),
               skinny = 18.5,
               normal = 25.0,
               fat = 30;

        return bmi switch
        {
            _ when bmi <= skinny => "Under",
            _ when bmi <= normal => "Normal",
            _ when bmi <= fat    => "Over",
            _                    => "Way over"
        };
    }

    static string BmiTell2(double weight, double height) =>
        (   from _ in "x"
            let bmi     = Pow(weight / height, 2)
            let skinny  = 18.5
            let normal  = 25.0
            let fat     = 30
            select   bmi <= skinny ? "Under"
                   : bmi <= normal ? "Normal"
                   : bmi <= fat    ? "Over"
                   :                 "Way over").First();
```

# Product types (aka Records)
In Haskell you define a product type as below:

```haskell
    data Person = Person { firstName :: String  
                             , lastName :: String  
                             , age :: Int
                             } deriving (Show)
```

In C#, it is currently complicated to define an immutable product type with structural equality, structural ordering and efficient hashing.

In essence, you have to implement a bunch of interfaces and operators, somehow similar to below (and I am not implementing ordering, and it is probably not too efficient either).

```csharp
    public readonly struct PersonData: IEquatable<PersonData> {
        public readonly string FirstName;
        public readonly string LastName;
        public readonly int Age;

        public PersonData(string first, string last, int age) => (LastName, FirstName, Age) = (last, first, age);

        public override int GetHashCode() => (FirstName, LastName, Age).GetHashCode();
        public override bool Equals(object other) => other is PersonData l && Equals(l);
        public bool Equals(PersonData oth) => LastName == oth.LastName && FirstName == oth.FirstName && Age == oth.Age;
        public static bool operator ==(PersonData lhs, PersonData rhs) => lhs.Equals(rhs);
        public static bool operator !=(PersonData lhs, PersonData rhs) => !(lhs == rhs);
    }
```

If you use a `struct`, you are still open to someone simply newing it using the default constructor, that you can't make `private`.

Using a class (as below) avoids that, but loses the pass by value semantic.

```csharp
    public class PersonData1 : IEquatable<PersonData1> {
        public readonly string FirstName;
        public readonly string LastName;
        public readonly int Age;

        public PersonData1(string first, string last, int age) => (LastName, FirstName, Age) = (last, first, age);

        public override int GetHashCode() => (FirstName, LastName, Age).GetHashCode();
        public override bool Equals(object oth) => oth is PersonData l && Equals(l);
        public bool Equals(PersonData1 other) => LastName == other.LastName && FirstName == other.FirstName && Age == other.Age;
        public static bool operator ==(PersonData1 lhs, PersonData1 rhs) => lhs.Equals(rhs);
        public static bool operator !=(PersonData1 lhs, PersonData1 rhs) => !(lhs == rhs);
    }
```

So, there is no easy fix. Using Language-ext you can do it much more simply, by inheritance.
But obviously it uses IL generation that is slow the first time around. Try running the code and notice the delay when IL generating.

```csharp
    public class PersonData2 : Record<PersonData2> {
        public readonly string FirstName;
        public readonly string LastName;
        public readonly int Age;

        public PersonData2(string first, string last, int age) => (LastName, FirstName, Age) = (last, first, age);

    }
```

# Sum types (aka Discriminated Union)
In Haskell you write:

```haskell
    data Shape =
                Circle Float Float Float
            | Rectangle Float Float Float Float
            | NoShape
            deriving (Show)  
```

There is no obvious equivalent in C#, and different libraries has sprung up to propose possible solutions (but not language-ext)
(i.e. [here](https://github.com/Galad/CSharpDiscriminatedUnion) or [here](https://github.com/mcintyre321/OneOf)).

One possible 'pure language' implementation, not considering structural equality/ordering/hash, follows:

```csharp
    abstract class Shape {

        public sealed class NoShape : Shape { }
        public sealed class Circle : Shape {
            internal Circle(double r) => Radius = r;
            public readonly double Radius;
        }
        public sealed class Rectangle : Shape {
            internal Rectangle(double height, double width) => (Height, Width) = (height, width);
            public readonly double Height;
            public readonly double Width;
        }
    }

    static Shape.Circle Circle(double x)                 => new Shape.Circle(x);
    static Shape.Rectangle Rectangle(double x, double y) => new Shape.Rectangle(x,y);
    static Shape.NoShape NoShape()                       => new Shape.NoShape();
```

You can then pattern match on it in various obvious ways:

```csharp
    static double Area(Shape s) => s switch
    {
        Shape.NoShape _                  => 0,
        Shape.Circle {Radius: var r }    => Pow(r, 2) * PI,
        Shape.Rectangle r                => r.Height * r.Width,
        _                                => throw new Exception("No known shape")
    };

    static void CalcAreas() {
        var c = Circle(10);
        var r = Rectangle(10, 3);
        var n = NoShape();

        WriteLine(Area(c));
        WriteLine(Area(r));
        WriteLine(Area(n));
    }
```

# Maybe (Or Option) type
In Haskell you write:

```Haskell
     f::Int -> Maybe Int
     f 0 = Nothing
     f x = Just x

     g::Maybe Int -> Int
     g Nothing  = 0
     g (Just x) = x

```

In C#, this easily translates to `Nullable` value and reference types. Assume you have `Nullable = enabled` in your project

```csharp
    static int? F(int i) => i switch {
        0 => new Nullable<int>(),
        _ => i
    };

    static int G(int? i) => i ?? 0;
```

# Main Method
Let's wrap all the samples with a `Main` function and then write a full program.

```csharp
    static void Main() {
        UseFunc();
        SquarePoly();
        WriteLine(Square(2) == SquareF(2));
        WriteLine(Sum(new[] { 1, 2, 3, 4 })  == Sum1(new[] { 1, 2, 3, 4 }));
        WriteLine(Sum1(new[] { 1, 2, 3, 4 }) == Sum2(new[] { 1, 2, 3, 4 }.ToSeq()));
        WriteLine(BmiTell(80, 100) == BmiTell1(80, 100));
        WriteLine(BmiTell(80, 100) == BmiTell2(80, 100));

        WriteLine(new PersonData("Bob", "Blake", 40) == new PersonData("Bob", "Blake", 40));
        WriteLine(new PersonData1("Bob", "Blake", 40) == new PersonData1("Bob", "Blake", 40));
        WriteLine("Before IL gen");
        WriteLine(new PersonData2("Bob", "Blake", 40) == new PersonData2("Bob", "Blake", 40));
        WriteLine(new PersonData2("Alphie", "Blake", 40) <= new PersonData2("Bob", "Blake", 40));
        WriteLine("Already genned");
        WriteLine(new PersonData2("Bob", "Blake", 40) == new PersonData2("Bob", "Blake", 40));
        WriteLine(new PersonData2("Alphie", "Blake", 40) <= new PersonData2("Bob", "Blake", 40));

        CalcAreas();

        Hangman.Core.MainHangman();

    }
}
```

# Full program

Let's finish with a semi-working version of Hangman,
from an exercise in [Haskell programming from first principles](http://haskellbook.com/),
just to get an overall impression of how the two languages look for bigger things.

The exercise was a fill-in-the-blanks kind of thing with the function names and types given,
so I don't think I butcher it too badly, but maybe not.

The Haskell code is:

```haskell
module Main where

import Control.Monad (forever) -- [1]
import Data.Char (toLower) -- [2]
import Data.Maybe (isJust) -- [3]
import Data.List (intersperse) -- [4]
import System.Exit (exitSuccess) -- [5]
import System.Random (randomRIO) -- [6]

type WordList = [String]

allWords :: IO WordList
allWords = do
      dict <- readFile "data/dict.txt"
      return (lines dict)

minWordLength :: Int
minWordLength = 5

maxWordLength :: Int
maxWordLength = 9

gameWords :: IO WordList
gameWords = do
      aw <- allWords
      return (filter gameLength aw)
      where gameLength w =
              let l = length (w :: String)
              in l > minWordLength && l < maxWordLength

randomWord :: WordList -> IO String
randomWord wl = do
      randomIndex <- randomRIO ( 0, length wl - 1)
      return $ wl !! randomIndex

randomWord' :: IO String
randomWord' = gameWords >>= randomWord

data Puzzle = Puzzle String [Maybe Char] [Char]

instance Show Puzzle where
      show (Puzzle _ discovered guessed) =
        (intersperse ' ' $ fmap renderPuzzleChar discovered)
        ++ " Guessed so far: " ++ guessed

freshPuzzle :: String -> Puzzle
freshPuzzle s = Puzzle s (map (const Nothing) s) []

charInWord :: Puzzle -> Char -> Bool
charInWord (Puzzle s _ _) c = c `elem` s

alreadyGuessed :: Puzzle -> Char -> Bool
alreadyGuessed (Puzzle _ _ s) c = c `elem` s

renderPuzzleChar :: Maybe Char -> Char
renderPuzzleChar Nothing  = '_'
renderPuzzleChar (Just c) = c

fillInCharacter :: Puzzle -> Char -> Puzzle
fillInCharacter (Puzzle word filledInSoFar s) c =
      Puzzle word newFilledInSoFar (c : s)
      where zipper guessed wordChar guessChar =
              if wordChar == guessed
                then Just wordChar
                else guessChar
            newFilledInSoFar =
              zipWith (zipper c) word filledInSoFar

handleGuess :: Puzzle -> Char -> IO Puzzle
handleGuess puzzle guess = do
      putStrLn $ "Your guess was: " ++ [guess]
      case (charInWord puzzle guess, alreadyGuessed puzzle guess) of
        (_, True) -> do
          putStrLn "You already guessed that character, pick something else!"
          return puzzle
        (True, _) -> do
          putStrLn "This character was in the word,filling in the word accordingly"
          return (fillInCharacter puzzle guess)
        (False, _) -> do
          putStrLn "This character wasn't in the word, try again."
          return (fillInCharacter puzzle guess)

gameOver :: Puzzle -> IO ()
gameOver (Puzzle wordToGuess _ guessed) =
      if (length guessed) > 7 then do
          putStrLn "You lose!"
          putStrLn $ "The word was: " ++ wordToGuess
          exitSuccess
      else return ()

gameWin :: Puzzle -> IO ()
gameWin (Puzzle _ filledInSoFar _) =
      if all isJust filledInSoFar then do
        putStrLn "You win!"
        exitSuccess
      else return ()

runGame :: Puzzle -> IO ()
runGame puzzle = forever $ do
      gameOver puzzle
      gameWin puzzle
      putStrLn $ "Current puzzle is: " ++ show puzzle
      putStr "Guess a letter: "
      guess <- getLine
      case guess of
        [c] -> handleGuess puzzle c >>= runGame
        _ -> putStrLn "Your guess must be a single character"


main :: IO ()
main = do
      word <- randomWord'
      let puzzle = freshPuzzle (fmap toLower word)
      runGame puzzle
```
Which loosely translate to the code below (pure C#, no language-ext) . A few comments:

1. I tried to keep the translation as 1:1 as possible.
2. I used expression bodied members for everything except IO returning function. That's a pleasing convention to me.
3. Things translate rather straightforwardly except for:
    1. Cheated using a simple `struct` instead of a `Record`, but often it is ok to do so.
    2. Needed to use LINQ query syntax to translate more complex expressions, but cannot have lambadas in it.
    3. Needed to do manual currying (`language-ext` would have beautified that).
4. The line count for this example is roughly similar. I think that's random. Also the C# code 'extends to the right' more.
5. Notably absent from the code are sum types, which would have been verbose to implement in C#.

```csharp
namespace Hangman {
    using WordList = IEnumerable<String>;
    using static System.Linq.Enumerable;

    static class Core {

        const int MinWordLength = 5;
        const int MaxWordLength = 9;

        static WordList AllWords => File.ReadAllLines("data/dict.txt");

        static WordList GameWords =>
            AllWords.Where(w => w.Length > MinWordLength && w.Length < MaxWordLength);

        static Random r = new Random();

        static string RandomWord(WordList wl) => GameWords.ElementAt(r.Next(0, wl.Length()));

        static string RandomWord1 => RandomWord(GameWords);

        static char RenderPuzzleChar(char? c) => c ?? '_';

        struct Puzzle { // Not implemented Eq and Ord because not needed in this program
            public string Word;
            public IEnumerable<char?> Discovered;
            public string Guessed;

            public override string ToString() =>
                $"{string.Join(" ", Discovered.Select(RenderPuzzleChar))}"
                    + " Guessed so far: " + Guessed;
        }

        static Puzzle FreshPuzzle(string s) => new Puzzle {
            Word       = s,
            Discovered = s.Select(_ => new Nullable<char>()),
            Guessed    = ""
        };

        static bool CharInWord(Puzzle p, char c)     => p.Word.Contains(c);
        static bool AlreadyGuessed(Puzzle p, char c) => p.Guessed.Contains(c);

        // Can't assign lambda expression to range variable with let, hence separate function
        static char? Zipper(char guessed, char wordChar, char? guessChar) =>
            wordChar == guessed ? wordChar : guessChar;

        // Manual curry. Could use language-ext to make it more beautiful.
        static Func<char, char?, char?> Zipper1(char c) => (c1, c2) => Zipper(c, c1, c2);

        static Puzzle FillInCharacter(Puzzle p, char c) =>
            (from _ in "x"
             let newFilledInSoFar = System.Linq.Enumerable.Zip<char, char?, char?>(p.Word, p.Discovered, Zipper1(c))
             select new Puzzle {
                Word = p.Word,
                Discovered = newFilledInSoFar,
                Guessed = c + p.Guessed
            }).First();

        static Puzzle HandleGuess(Puzzle puzzle, char guess) {// Braces means IO ...
            WriteLine($"Your guess was {guess}");
            switch (CharInWord(puzzle, guess), AlreadyGuessed(puzzle, guess)) {
                case (_, true):
                    WriteLine("You already guessed that character, pick something else!");
                    return puzzle;
                case (true, _):
                    WriteLine("This character was in the word,filling in the word accordingly");
                    return FillInCharacter(puzzle, guess);
                case (false, _):
                    WriteLine("This character wasn't in the word, try again.");
                    return FillInCharacter(puzzle, guess);
            }
        }

        static void GameOver(Puzzle p) {
            if(p.Guessed.Length > 7) {
                WriteLine("You lose!");
                WriteLine($"The word was {p.Word}");
                Environment.Exit(0);
            }
        }

        static void GameWin(Puzzle p) {
            if(p.Discovered.All(c => c.HasValue)) {
                WriteLine("You win!");
                Environment.Exit(0);
            }
        }

        static void RunGame(Puzzle puzzle) {
            while(true) {
                GameOver(puzzle);
                GameWin(puzzle);
                WriteLine($"Current puzzle is: {puzzle}");
                WriteLine("Guess a letter: ");
                var guess = ReadLine();
                if(guess.Length == 1) RunGame(HandleGuess(puzzle, guess[0]));
                else WriteLine("Your guess must be a single char");
            }
        }

        public static void MainHangman() {
            var puzzle = FreshPuzzle(RandomWord1);
            RunGame(puzzle);
        }

    }
}
```