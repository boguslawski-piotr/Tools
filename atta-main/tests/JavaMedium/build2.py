import shutil

from atta import *
from atta.targets import Java
from atta.Strategies import SrcHashStrategy

Project.Import('build')

Javac.RequiresCompileImpl = SrcHashStrategy()

class clean(Java.clean):
  def Run(self):
    Java.clean.Run(self)
    dirName = '.atta/markers'
    Echo('Deleting directory: ' + dirName)
    shutil.rmtree(dirName, True)
    