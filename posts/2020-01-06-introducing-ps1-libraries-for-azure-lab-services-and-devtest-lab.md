---
title: Introducing PS1 Libraries for Azure Lab Services and DevTest Labs
date: 2020-01-06
author: lucabol
layout: post
tags:
  - lab services
  - devtest labs
---
I am not sure why I have not blogged about this. We have released some very nice PS1 libraries to automate the usage of Azure Lab Services and Azure DevTest Labs.

The nicest thing about them is how they make use of the [PS1 Pipeline](https://docs.microsoft.com/en-us/powershell/scripting/learn/understanding-the-powershell-pipeline?view=powershell-7) to give a nice user experience.

```powershell
Get-AzLabAccount | Get-AzLab | Get-AzLabVm -Status Running | Stop-AzLabVm
```

I intend to shoot some brief videos to describe how to use them. In the meantime, you can read tutorials [here](https://github.com/Azure/azure-devtestlab/blob/master/samples/ClassroomLabs/Modules/Library/HowTo.md) and [here](https://github.com/Azure/azure-devtestlab/blob/master/samples/DevTestLabs/Modules/Library/HowTo.md)