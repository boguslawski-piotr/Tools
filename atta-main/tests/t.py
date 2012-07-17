"""Some tests."""
import sys

from atta import *

#print dir(sys.modules['t'])

Project.defaultTarget = 'test'
p = Properties.Open('JavaMedium/deploy.properties')

#test = [
#        {
#         'repository' : 'atta.repositories.Ftp',
#         'style'      : 'atta.repositories.Styles.Flat',
#         'host'       : p.Get('host'),
#         'rootDirName': p.Get('rootDirName'),
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

test = [{
       'repository' : 'atta.repositories.Maven',
       'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
       'putIn' :
          {
           'repository' : 'atta.repositories.Ftp',
           'style'      : 'atta.repositories.Styles.Flat',
           'host'       : p.Get('host'),
           'rootDirName': p.Get('rootDirName'),
           'user'       : p.Get('user'),
           'password'   : p.Get('password'),
          },
        }]

#r = Project.ResolveDependencies(test)
#print r

class test(Target):
  def Run(self):
#    p = PackageId(artifactId='a')
#    p.exclusions += ['a']
#    print p.exclusions

    #------------------------------------------------------------------------------

    from atta.repositories.Maven import Repository

    #package = PackageId.FromStr('asm:asm-util.jar:2.2.3')
    package = PackageId.FromStr('com.thoughtworks.xstream:xstream.jar:1.3.1')
    #package = PackageId.FromStr('ant.jar:1.6.2')
    #package = PackageId.FromStr('commons-jelly:commons-jelly-tags-xml.jar:1.1')
    r = Repository({'getOptional' : True})
    r.Get(package, 'compile')

