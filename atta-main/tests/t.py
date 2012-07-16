"""Some tests."""

from atta import *

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

class Z(object):
  _p = None

  def GetP(self):
    print 'ZZZ', Z._p
    return Z._p

  def _SetP(self, project):
    Z._p = project
    print 'XXX', Z._p

  P = property(GetP, _SetP)

def test():

  print Project.env.get('ATTA_TESTS')

  class ZZ: pass

  z = Z()
  z.P = '1'
  print z.P

  #z.P.X = 10
#  print z.P.X
  print z._p

  #------------------------------------------------------------------------------

  z = 'c:\\ala:p:\\dupa\\aaaa/sd:f:\\asewe'
  print OS.Path.AsList(z)

  #------------------------------------------------------------------------------

  from atta.tools.Interfaces import Observable


  return

  #------------------------------------------------------------------------------

  from atta.repositories.Maven import Repository
  from atta.repositories.Package import PackageId

  package = PackageId.FromStr('asm:asm-util.jar:2.2.3')
  #package = PackageId.FromStr('com.thoughtworks.xstream:xstream.jar:1.3.1')
  #package = PackageId.FromStr('ant.jar:1.6.2')
  #package = PackageId.FromStr('commons-jelly:commons-jelly-tags-xml.jar:1.1')
  r = Repository({'getOptional' : False})
  r.Get(package, 'compile')

