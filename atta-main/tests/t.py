'''Some tests.'''

from atta import *

Project.defaultTarget = 'test'

def test():
  from atta.repositories.Maven import Repository
  from atta.repositories.Package import PackageId
  
  #packageId = PackageId.FromStr('asm:asm-util.jar:2.2.3')
  packageId = PackageId.FromStr('com.thoughtworks.xstream:xstream.jar:1.3.1')
  #packageId = PackageId.FromStr('ant.jar:1.6.2')
  r = Repository({'getOptional' : False})
  r.Get(packageId, 'compile')
  
