---
id: 48
title: 'Write Yourself a Scheme in 48 Hours in F# – Part V'
date: 2011-07-29T07:26:00+00:00
author: lucabol
layout: post
guid: https://lucabolognese.wordpress.com/2011/07/30/write-yourself-a-scheme-in-48-hours-part-iv-2/
categories:
  - fsharp
tags:
  - fsharp
  - Lambda expressions
  - Parsing
---
We have one loose end to tie in the evaluator: the primitive operators. These are things that the interpreter knows intrinsically. There is a list of them below.

```fsharp
let rec primitives =
     [
        "+",    numericBinop (+)
        "-",    numericBinop (-)
        "*",    numericBinop (*)
        "/",    numericBinop (/)
        "mod",  numericBinop (%)
        "=",    numBoolBinop (=)
        "<",    numBoolBinop (<)
        ">",    numBoolBinop (>)
        "/=",   numBoolBinop (<>)
        ">=",   numBoolBinop (>=)
        "<=",   numBoolBinop (<=)
        "&&",   boolBoolBinop (&&)
        "||",   boolBoolBinop (||)
        "string=?",     strBoolBinop (=)
        "string>?",      strBoolBinop (>)
        "string<?",      strBoolBinop (<)
        "string<=?",    strBoolBinop (<=)
        "string>=?",    strBoolBinop (>=)
        "car",  car
        "cdr",  cdr
        "cons", cons
        "eq?", eqv
        "eqv?", eqv
        "equal?", equal
        // IO primitives
        "apply", applyProc
        "open-input-file", makePort FileAccess.Read
        "open-output-file", makePort FileAccess.Write
        "close-input-port", closePort
        "close-output-port", closePort
        "read", readProc
        "write", writeProc
        "read-contents", readContents
        "read-all", readAll
     ]
```

Having seen the above list, it now becomes clearer why the _primitiveBindings_ function was defined as such. It just binds these pairs into the environment.

```fsharp
let primitiveBindings () =
    (nullEnv ()) |> bindVars [ for v, f in primitives -> v, PrimitiveFunc f ]
```

_numericBinop_ unpacks the numbers, applies the provided operator and packs the result back in the Number.

```fsharp
let numericBinop op parms =
    if List.length parms < 2
        then throw <| NumArgs(2, parms)
        else parms |> List.map unpackNum |> foldl1 op |> Number
```

While we are at it, we can define _fold1 (_it tends to be&#160; useful)

```fsharp
let foldl1 op = function
    | h::t -> List.fold op h t
    | [] -> throw (Default("Expected a not empty list, got an empty list"))
```

The other XBinops work similarly …

```fsharp
let boolBinop unpacker op args =
    match args with
    | [ left; right ] -> Bool (op (unpacker left) (unpacker right))
    | _ -> throw (NumArgs(2,args))
let numBoolBinop = boolBinop unpackNum
let strBoolBinop = boolBinop unpackStr
let boolBoolBinop = boolBinop unpackBool
```

We now have to look at the family of unpackers. They all work rather similarly. Notice Scheme making an effort to get a number out of a string and to get anything out of a list. Strong type folks won't like that. Oh well, just remove these lines …

```fsharp
let rec unpackNum = function
    | Number n  -> n
    | String n  -> let success, result = System.Int32.TryParse n
                   if success
                       then result
                       else throw (TypeMismatch("number", String n))
    | List [n]  -> unpackNum n
    | notNumber -> throw (TypeMismatch("number", notNumber))
let rec unpackStr = function
    | String s -> s
    | Number n -> n.ToString()
    | Bool b   -> b.ToString()
    | List [s]  -> unpackStr s
    | noString -> throw (TypeMismatch("string", noString))
let rec unpackBool = function
    | Bool b -> b
    | List [b]  -> unpackBool b
    | noBool -> throw (TypeMismatch("boolean", noBool))
```

Now back to the list of primitive operators, there are the signature LISP operators _car_, _cdr_ and _cons_. Just understanding the first line for each function should be enough to get an idea of what they do.

```fsharp
let car = function
    | [List (x :: _)] -> x
    | [DottedList (x :: _, _)] -> x
    | [badArg] -> throw (TypeMismatch("pair", badArg))
    | badArgList -> throw (NumArgs(1, badArgList))
let cdr = function
    | [List (x :: xs)] -> List xs
    | [DottedList ([xs], x)] -> x
    | [DottedList ((_ :: xs), x)] -> DottedList (xs, x)
    | [badArg] -> throw (TypeMismatch("pair", badArg))
    | badArgList -> throw (NumArgs(1, badArgList))
let cons = function
    | [x; List xs] -> List (x :: xs)
    | [x; DottedList (xs, xlast)] -> DottedList (x :: xs, xlast)
    | [x1; x2] -> DottedList([x1], x2)
    | badArgList -> throw (NumArgs(2, badArgList))
```

We then need to work our way to implement _eqv_ (aka _eq?_ in Scheme). We first define a function that tests that two LispVal are the same. It should be pretty self explanatory (the list piece is kind of cute).

```fsharp
let rec eqvPrim e1 e2 =
        match e1, e2 with
        | (Bool b1, Bool b2) -> b1 = b2
        | (Number n1, Number n2) -> n1 = n2
        | (String s1, String s2) -> s1 = s2
        | (Atom a1, Atom a2) -> a1 = a2
        | (DottedList (xs, x), DottedList(ys, y)) -> eqvPrim (List (xs @ [x])) (List (ys @ [y]))
        | (List l1, List l2) -> l1.Length = l2.Length && List.forall2 eqvPrim l1 l2
        | _ -> false
```

Now we wrap the result in a _Bool_. Doing it this way avoid repeating the wrapping in each single line of _eqvPrim_ (thanks to Tobias for spotting this refactoring).

```fsharp
let eqv = function
          | [e1; e2] -> Bool (eqvPrim e1 e2)
          | badArgList -> throw (NumArgs (2, badArgList))
```

_Equal?_ checks if there is any unpacking scheme that can be used to test equality of the two elements of a two element list.

```fsharp
let equal = function
    | [arg1; arg2] ->
        let unpackEqual = numUnpackEq arg1 arg2 ||
                          strUnpackEq arg1 arg2 ||
                          boolUnpackEq arg1 arg2
        Bool (eqvPrim arg1 arg2 || unpackEqual)
    | argsList -> throw (NumArgs(2, argsList))
```

We need to define equality of packed primitive types. We do it nicely below.

```fsharp
let tryUnpacker (unpack : LispVal -> 'a) (op : 'a -> 'a -> bool) arg1 arg2 =
    try op (unpack arg1) (unpack arg2) with _ -> false
let numUnpackEq = tryUnpacker unpackNum (=)
let strUnpackEq = tryUnpacker unpackStr (=)
let boolUnpackEq = tryUnpacker unpackBool (=)
```

The _apply_ statement maps more or less directly to our _apply_ function.

```fsharp
applyProc = function
            | [func; List args] -> apply func args
            | func :: args -> apply func args
            | [] -> throw (Default("Expecting a function, got an empty list"))
```

And we are left with the I/O processing functions. We are simply wrapping a FileStream in a Port.

```fsharp
let makePort fileAccess = fileIOFunction (fun fileName ->
                                File.Open(fileName,FileMode.OpenOrCreate, fileAccess) |> Port)
    let closePort = function
                    | [Port(port)] -> port.Close() ; Bool true
                    | _ -> Bool false
```

We then can read and write from it. Notice how the lack of arguments makes us do it from the standard Console.

```fsharp
let rec readProc port =
    let parseReader (reader:TextReader) = reader.ReadLine() |> readExpr
    match port with
       | [] -> parseReader(System.Console.In)
       | [Port(port)] ->
            use reader = new StreamReader(port)
            parseReader (reader)
       | args -> throw (NumArgs(1, args))
let writeProc objPort =
    let write obj (writer: TextWriter) = writer.Write(showVal obj) ; Bool true
    match objPort with
    | [obj] -> write obj (System.Console.Out)
    | [obj ; Port(port)] ->
        use writer = new StreamWriter(port)
        write obj writer
    | args -> throw (NumArgs(1, args))
```

There you go. A full evaluator in two blog posts!! Next up, the parser.
