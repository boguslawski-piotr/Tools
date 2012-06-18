## \brief Targets dependency tests.

from atta import *

project.defaultTarget = 'install'

class init(Target):
  def Run(self):
    Echo('init (should be second)')
    pass

class prepare(Target):
  def Run(self):
    Echo('prepare (should be first)')
    pass
  
class precompile(Target):
  DependsOn = [init, prepare]
  def Run(self):
    Echo('precompile (should be third)')

class compile(Target):
  DependsOn = [prepare, precompile]
  def Run(self):
    Echo('compile (should be fourth)')
    
class install(Target):
  DependsOn = [prepare, compile, precompile]
  def Run(self):
    Echo('install (should be last)')
