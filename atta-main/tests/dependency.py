from atta import *

Project.defaultTarget = 'install'

class prepare(Target):
  def Run(self):
    Echo('prepare (should be first and only one for any target from command line)')
    pass
  
class precompile(Target):
  DependsOn = [prepare]
  def Run(self):
    Echo('precompile')

class compile(Target):
  DependsOn = [prepare, precompile]
  def Run(self):
    Echo('compile')
    
class install(Target):
  DependsOn = [prepare, compile, precompile]
  def Run(self):
    Echo('install')
