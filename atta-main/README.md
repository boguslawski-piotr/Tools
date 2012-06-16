# pyant

The Ant in Python (the working name)

## Draft
 
Build system and build scripts in pure python.
TODO: give a cool and sensible brief description 

## Example

build.py script:

<code>
  from pyant import *
  
  Project.defaultTarget = 'install'
  
  class prepare(Target):
    def Prepare(self):
      return True
      
    def Run(self):
      Echo('enter prepare')
      pass
    
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
      Echo('''enter install, level=LogLevel.WARNING)
      Echo(Env.cwd)
</code>
    
run it:

<pre>
  $> pyant
</pre>

and output will be:

<pre>
  Buildfile: P:\pyant\a.py
  
  prepare:
  
  precompile:
      Echo: enter precompile
  
  compile:
      Echo: enter compile
  
  install:
      Echo: enter install
      Echo: P:\pyant
  
  Build: SUCCESSFUL
     At: 2012-06-17T00:28:29.099000
   Time: 0:00:00.055000
   
</pre>
   