'''Some tests.'''

from atta import *

Project.defaultTarget = 'test'

#test = [
#        {
#         'repository' : 'atta.repositories.Ftp',
#         'style'      : 'atta.repositories.Styles.Flat',
#         'host'       : p.Get('host'),
#         'rootDir'    : p.Get('rootDir'),
#         'user'       : p.Get('user'),
#         'password'   : p.Get('password'),
#         'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
#         'getOptional': True,
#        },
#        ] 

#test = [{
#       'repository' : 'atta.repositories.Maven',
#       'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
#       'getOptional': True,
#       }]

#test = [{
#       'repository' : 'atta.repositories.Local',
#       'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
#       'getOptional': True,
#       'putIn'     : 'atta.repositories.Project', # like repository
#       }]

#test = [{
#       'repository' : 'atta.repositories.Maven',
#       'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
#       'putIn' :
#          {
#           'repository' : 'atta.repositories.Ftp',
#           'style'      : 'atta.repositories.Styles.Flat',
#           'host'       : p.Get('host'),
#           'rootDir'    : p.Get('rootDir'),
#           'user'       : p.Get('user'),
#           'password'   : p.Get('password'),
#          },
#        }] 

#r = Project.ResolveDependencies(test)
#print r

def test():
  Echo(DirSet('.', '*'))
  return

  from atta.repositories.Maven import Repository
  from atta.repositories.Package import PackageId

  packageId = PackageId.FromStr('asm:asm-util.jar:2.2.3')
  #packageId = PackageId.FromStr('com.thoughtworks.xstream:xstream.jar:1.3.1')
  #packageId = PackageId.FromStr('ant.jar:1.6.2')
  #packageId = PackageId.FromStr('commons-jelly:commons-jelly-tags-xml.jar:1.1')
  r = Repository({'getOptional' : False})
  r.Get(packageId, 'compile')

