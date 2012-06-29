'''Target.system tests.'''

from atta import *

Project.defaultTarget = 'test'

class win(Target):
  system = 'windows'
  def Run(self):
    Echo('only on Windows')

class linux(Target):
  system = 'linux'
  def Run(self):
    Echo('only on linux')

class mac(Target):
  system = 'macos'
  def Run(self):
    Echo('only on mac')

class wlm(Target):
  system = 'win,linux,mac'
  def Run(self):
    Echo('on win,linux,mac')
    
class test(Target):
  dependsOn = [win,linux,mac,wlm]
  def Run(self):
    Echo('on all')
    
