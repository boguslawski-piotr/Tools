Atta
====

## Introduction
 
Atta is a FREE build tool, targets-tasks driven, developed in pure Python.

Similar in philosophy to the Ant, NAnt, etc. but without the use of XML syntax nightmare.

TODO: give a cool and sensible extended description 

http://boguslawski-piotr.github.com/atta/

## Philosophy example

build.py script:

```python
  from atta import *
  
  Project.defaultTarget = 'install'
  
  class prepare(Target):
    def Prepare(self):
      return True
      
    def Run(self):
      Echo('enter prepare')
    
  class precompile(Target):
    DependsOn = [prepare]
    def Run(self):
      Echo('enter precompile')
  
  class compile(Target):
    DependsOn = [prepare, precompile]
    def Run(self):
      Echo('enter compile')
      
  class install(Target):
    DependsOn = [prepare, compile, precompile]
    def Run(self):
      Echo('enter install', level = LogLevel.WARNING)
```
    
run Atta:

<pre>
  $> atta
</pre>

and output will be:

<pre>
  Buildfile: build.py
  
  prepare:
      Echo: enter prepare
  
  precompile:
      Echo: enter precompile
  
  compile:
      Echo: enter compile
  
  install:
      Echo: enter install
  
  Build: SUCCESSFUL
     At: 2012-06-17T00:28:29.099000
   Time: 0:00:00.055000
</pre>
   