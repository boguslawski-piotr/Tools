'''Some tests.'''

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

r = Project.ResolveDependencies(test)
#print r

def test():
  
  z = 'c:\\ala:p:\\dupa\\aaaa/sd:f:\\asewe'
  print OS.Path.AsList(z)
      
  #------------------------------------------------------------------------------
   
  from atta.tools.Interfaces import Observable
  
  class X(Observable):
    def action(self):
      self.notifyObservers(1)
      
  class o0():
    def __call__(self, c, event):
      print 'o0', event

  class o1(object):
    def __call__(self, c, event):
      print 'o1', event
  
  def o2(c, event):
    print 'o2', event
    
  x = X()
  x.addObserver(o0)
  x.addObserver(o1)
  x.addObserver(o2)
  x.action()
  x.removeObserver(o2)
  x.action()
  x.removeObserver(o0)
  x.action()
  
  return

  #------------------------------------------------------------------------------ 

  from atta.repositories.Maven import Repository
  from atta.repositories.Package import PackageId

  packageId = PackageId.FromStr('asm:asm-util.jar:2.2.3')
  #packageId = PackageId.FromStr('com.thoughtworks.xstream:xstream.jar:1.3.1')
  #packageId = PackageId.FromStr('ant.jar:1.6.2')
  #packageId = PackageId.FromStr('commons-jelly:commons-jelly-tags-xml.jar:1.1')
  r = Repository({'getOptional' : False})
  r.Get(packageId, 'compile')

