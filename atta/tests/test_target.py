"""Targets dependency tests."""

from atta import *

Project.defaultTarget = 'install'

def init():
  Echo('init (should be second)')

def prepare():
  Echo('prepare (should be first)')

def precompile():
  Echo('precompile (should be third)')

precompile.dependsOn = [init, prepare]

class compile_(Target):
  dependsOn = [prepare, precompile]
  def Run(self):
    Echo('compile (should be fourth)')

class install(Target):
  dependsOn = [prepare, compile_, precompile]
  def Run(self):
    Echo('install (should be last)')
