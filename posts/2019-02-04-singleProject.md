---
title: A single .NET Core project to rule them all
date: 2019-02-04
author: lucabol
layout: post
description: "One project to rule them all, one build to find them, one configuration to bring them all, and in the darkness bind them! Watch as we bend MSBuild to our will, turning the multi-project .NET convention on its head. Warning: may contain traces of build system hackery and mild rebellion against the 'golden path'"
tags:
  - csharp
---
## Abstract
The code is [here](https://github.com/lucabol/SingleSourceProject).

Thanks to [Mike](https://github.com/mjrousos) for reviewing this.

I have always been mildly irritated by how many .net projects I need to create in my standard workflow.

Usually I start with an idea for a library; I then want to test it with a simple executable; write some XUnit tests for it and finally benchmark some key scenarios. So I end up with at least four projects to manage.

Sure, I can find ways to automatically generate those projects, but I have always been weary of codegen to solve complexity issues. It always ends up coming back to bite you. For those of you as old as I am, think [MFC](https://en.wikipedia.org/wiki/Microsoft_Foundation_Class_Library) ...

So what is my ideal world then? Well, let's try this:

1. One single project for the library and related artifacts (i.e. test, benchmarks, etc...).
2. Distinguish the library code from the test code from the benchmark code by some convention (i.e. name scheme).
3. Generate each artifact (i.e. library, tests, benchmarks, executable) by passing different options to `dotnet build` and `dotnet run`.
4. Create a new project by using the standard `dotnet new` syntax.
5. Have intellisense working normally in each file for my chosen editor (VSCode).
6. Work with `dotnet watch` so that one can automatically run tests when anything changes.

## Disclaimer
What follows, despite working fine, is not the standard way .net tools are used. It is not in the 'golden path'. That is problematic for production usage as:

1. It might not work in your particular configuration.
2. It might not work with other tools that rely on the presence of multiple projects (i.e. code coverage? ...).
3. It might work now in all scenarios, but get broken in the future as you update to a new framework, sdk, editor.
4. It might expose bugs in the tools, now or later, which aren't going to be fixed, as you are not using the tools as intended.
5. It might upset your coworkers that are used to a more standard setup.

I need to write a blog post about the concept of the 'golden path' and the perils, mostly hidden, of getting away from it. The summary, it is a bad idea.

Having said all of that, for the daring souls, here is one way to achieve most of the above. It also works out as a tutorial on how the different components of the .NET Core build system interacts.

## How to use it
Here are the steps:

1. Type `dotnet new -i Lucabol.SingleSourceProject`.
2. Create a directory for your project and cd to it.
3. Type `dotnet new lsingleproject` and optionally `--standardVersion <netstandardXX> --appVersion <netcoreappXX>`.
4. Either modify the `Library.cs`, `Main.cs`, `Test.cs`, `Bench.cs` files or create your own with this convention:
    * Code for the executable goes in potentially multiple files named `XXXMain.cs` (i.e. `MyLibrary.Main.cs`).
    * Code for the tests goes into files named `XXXTest.cs` (i.e. `MyLibrary.Test.cs`).
    * Code for the benchmarks goes into files named `XXXBench.cs` (i.e. `MyLibrary.Bench.cs`).
    * Any `.cs` file not following the above conventions is compiled into the dll.
5. Type:
    * `dotnet build` or `dotnet build -c release` to build `debug` or `release` version of your dll. This doesn't include any of the main, test or bench code.
    * `dotnet build -c main` or `dotnet build -c main_release` and the corresponding `dotnet run -c ..` build and run the exe.
    * `dotnet build -c test`, `dotnet build -c test_release` and `dotnet test -c test` build and run the tests.
    * `dotnet build -c bench`, `dotnet run -c bench` build and run the benchmark.

## How it all works
The various steps above are implemented as follows:

`dotnet new -i ...` install a [custom template](https://docs.microsoft.com/en-us/dotnet/core/tools/custom-templates) that I have created and pushed on NuGet.

The custom template is composed of the following files:
### Code files
There is one file for each kind of artifact that the project can generate: library, program, tests and benchmark. The files follow the name terminating conventions, as described above.
### Project file
The project file is identical to any other project file generated by `dotnet new` except that there is one additional line appended at the end:

~~~cs
<Import Project="Base.targets" />
~~~

This instruct `msbuild` to include the `Base.targets` file. That file has most of the magick. I have separated it out so that you can use it unchanged in your own projects.

### Base.targets
We start by removing all the file from compilation except the ones that are used to build the library.

~~~cs
  <ItemGroup>
    <Compile Remove="**/*Bench.cs;**/*Test.cs;**/*Main.cs" />
  </ItemGroup>
~~~

We then conditionally include the correct ones depending on which configuration is chosen. Please notice the last line, which instruct `dotnet watch` to watch all the `.cs` files. By default it just watches the ones in the `debug` configuration.

~~~cs
  <ItemGroup>
    <Compile Include="**/*Test.cs"  Condition="'$(Configuration)'=='Test'"/>
    <Compile Include="**/*Test.cs"  Condition="'$(Configuration)'=='Test_Release'"/>
    <Compile Include="**/*Bench.cs" Condition="'$(Configuration)'=='Bench'"/>
    <Compile Include="**/*Main.cs"  Condition="'$(Configuration)'=='Main'"/>
    <Compile Include="**/*Main.cs"  Condition="'$(Configuration)'=='Main_Release'"/>
    <Watch Include="**\*.cs" />
  </ItemGroup>
~~~

Then we need to define the references. Depending on what you are building you need to include references to the correct NuGet packages (i.e. if you are building `test` you need the `xunit` packages). This is done below:

~~~cs
  <ItemGroup  Condition="'$(Configuration)'=='Bench' OR '$(Configuration)'=='Debug'">
    <PackageReference Include="BenchmarkDotNet" Version="0.11.3" />
  </ItemGroup>

  <ItemGroup Condition="'$(Configuration)'=='Test' OR '$(Configuration)'=='Test_Release' OR '$(Configuration)'=='Debug'">
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="15.9.0" />
    <PackageReference Include="xunit" Version="2.4.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.0" />
  </ItemGroup>
~~~

One thing to notice is that most references are also included in the `debug` configuration. This is not a good thing, but it is the only way to get VSCode Intellisense to work for all the files in the solution. Apparently, IntelliSense uses whatever reference are defined for the `debug` build in `VsCode`. So `debug` is special, if you wish ...

But that's not enough. When you create your own `MsBuild` configurations, you also have to replicate the properties and constants that are set in the `debug` and `release` configurations. You would like a way to inherit them, but I don't think it is possible.

It is particularly important to set the `TargetFramework` property, as it needs to be set to `netcoreappXXX` for the main, test and benchmark configurations. I give an example of the `Test` and `Test_release` configurations below. The rest is similar:

~~~cs
  <PropertyGroup Condition="'$(Configuration)'=='Test'">
    <TargetFramework>netcoreapp2.1</TargetFramework>
    <DefineConstants>$(DefineConstants);DEBUG;TRACE;TEST</DefineConstants>
    <DebugSymbols>true</DebugSymbols>
    <DebugType>portable</DebugType>
    <Optimize>false</Optimize>
  </PropertyGroup>

  <PropertyGroup Condition="'$(Configuration)'=='Test_Release'">
    <TargetFramework>netcoreapp2.1</TargetFramework>
    <DefineConstants>$(DefineConstants);RELEASE;TRACE;TEST</DefineConstants>
    <DebugSymbols>false</DebugSymbols>
    <DebugType>portable</DebugType>
    <Optimize>true</Optimize>
  </PropertyGroup>
~~~

### The .template.config/template.json file
This is necessary to create a `dotnet new` custom template. The only thing to notice is the two parameters `standardVersion` and `appVersion` that gives the user a way to indicate which version of the .NET Standard to use for the library and which version of the application framework to use for Main, Test and Bench.

~~~cs
{
  "$schema": "http://json.schemastore.org/template",
  "author": "Luca Bolognese",
  "classifications": [ "Classlib", "Console", "XUnit" ],
  "identity": "Lucabol.SingleSourceProject",
  "name": "One single Project",
  "description": "One single Project for DLL, XUnit, Benchmark & Main, using configurations to decide what to compile",
  "shortName": "oneproject",
  "tags": {
    "language": "C#",
    "type": "project"
  },
  "preferNameDirectory": true,
  "sourceName": "SingleSourceProject",
  "symbols":{
    "standardVersion": {
      "type": "parameter",
      "defaultValue": "netstandard2.0",
      "replaces":"netstandard2.0"
    },
    "appVersion": {
      "type": "parameter",
      "defaultValue": "netcoreapp2.1",
      "replaces":"netcoreapp2.1"
    }
  }
}
~~~

## Conclusion
Now that you know how it all works, you can make an informed decision if to use it or not. As for me ...
