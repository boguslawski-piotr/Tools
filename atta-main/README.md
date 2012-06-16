pyant
=====

The Ant in Python (the working name)

-- DRAFT --
 
Build system and build scripts in pure python.
TODO: give a cool and sensible brief description 

build.py script:

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
    
run it:

  $> pyant

output:

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
   