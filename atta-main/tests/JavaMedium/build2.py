from atta import *
from atta.targets import Java
from atta.tools.Strategies import SrcHashStrategy

import build

Javac.SetDefaultRequiresCompileImpl(SrcHashStrategy)

class clean(Java.clean):
  def Run(self):
    Java.clean.Run(self)
    Delete('.atta/srchash', force = True)

