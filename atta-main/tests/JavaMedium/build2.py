from atta import *
from atta.targets.Java import Javac, clean as JavaClean
from atta.compilers.Strategies import SrcHashStrategy

Project.Import('build')
Javac.SetDefaultRequiresCompileImpl(SrcHashStrategy)

class clean(JavaClean):
  def Run(self):
    JavaClean.Run(self)
    Delete('.atta/srchash', force = True)

