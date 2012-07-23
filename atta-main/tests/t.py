"""Some tests."""
import sys
import urllib2
from atta import *

#v = Version.FromStr('1.3.4a0', fileName = None)
#print v, v._AsInt()
#v = Version.FromStr('0.6c11', fileName = None)
#print v, v._AsInt()
#v = Version.FromStr('0.6_11', fileName = None)
#print v, v._AsInt()
#v = Version.FromStr('0.6A11', fileName = None)
#print v, v._AsInt()
#v = Version.FromStr('0.6Z11', fileName = None)
#print v, v._AsInt()
#sys.exit()

#z = urllib2.urlopen('http://www.automapa.pl/zzz')
#print '1'
#z.read()
#print '2'

#def AbstractClass(_class):
#  """TODO: description"""
#  #raise Exception('cos')
#  print 'cos'
#  return _class
#
#@AbstractClass
#class abc:
#  def __init__(self):
#    print '!'
#
#class sabc(abc):
#  def __new__(cls, *args, **kwargs):
#    print '!!'
#
#z = sabc()
#sys.exit(0)

Project.defaultTarget = 'test'
p = Properties.Open('JavaMedium/deploy.properties')
test = []

#MyPackage = PackageId.FromStr('slinky.jar:2.1')
#test = [{
#  'repository' : '.repositories.Http',
#  #'style' : '.repositories.Styles.OnlyFileName',
#  'url' : 'http://slinky2.googlecode.com/svn/artifacts/2.1',
#  'package' : MyPackage,
#  'fileNames' : ['slinky.jar'],
#  'putIn' :
#      {
#      'repository' : 'atta.repositories.Ftp',
#      'style'      : 'atta.repositories.Styles.Flat',
#      'host'       : p.Get('host'),
#      'rootDirName': p.Get('rootDirName'),
#      'user'       : p.Get('user'),
#      'password'   : p.Get('password'),
#      },
#}]

#r, rr = Project.ResolveDependencies(test)
#print rr, rr[0].fileNames
#print MyPackage, MyPackage.fileNames
#sys.exit()

# Atta depends...
#pkg = PackageId.FromStr('bitprophet:ssh.tar.gz:master')
#test = [{
#  'repository' : '.repositories.GitHub',
#  'package' : 'bitprophet:ssh.tar.gz:1.7.13',
#  }]

CryptPkg = PackageId.FromStr('pycrypto.tar.gz:2.6')
#CryptPkg.importName = 'Crypto'
#CryptPkg.siParams = '--user'
test += [{
  'repository': '.repositories.PyPI',
  'package'   : 'bitprophet:ssh.tar.gz:1.7.14',
  'dependsOn' : CryptPkg
  }]

test += [{
  'repository': '.repositories.Http',
  'url'       : 'http://pysftp.googlecode.com/files',
  'package'   : 'pysftp.tar.gz:0.2.2',
  'fileNames' : 'pysftp-0.2.2.tar.gz'
}]

test += ['Jinja2.tar.gz:2.6', 'Pygments.tar.gz:1.5', 'pep8.tar.gz:1.3.3', 'logilab-astng.tar.gz:0.23.1']

#cx_FreezePkg = PackageId.FromStr('cx_Freeze:4.3')
#cx_FreezePkg.siParams = '--user'
#test += [
#    {
#    'repository': '.repositories.Http',
#    'url'       : 'http://prdownloads.sourceforge.net/cx-freeze',
#    'package'   : cx_FreezePkg,
#    'fileNames' : 'cx_Freeze-4.3.tar.gz'
#  }
#]

files, packages = Project.ResolveDependencies(test, defaultRepository = '.repositories.PyPI')
py = PyInstall(packages, sgParams = '--quiet', failOnError = False, logOutput = False, downgrade = True, force = False)
#if py.badPackages:
#  for package, importName, returnCode, errorMsg, output in py.badPackages:
#    print output

sys.exit()


#test = [
#        {
#         'repository' : 'atta.repositories.Ftp',
#         'style'      : 'atta.repositories.Styles.Flat',
#         'host'       : p.Get('host'),
#         'rootDirName': p.Get('rootDirName'),
#         'user'       : p.Get('user'),
#         'password'   : p.Get('password'),
#         #'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
#         'package'    : 'commons-net.jar:3.0.1',
#         'getOptional': True,
#        },
#        ]

test = [{
       'repository' : 'atta.repositories.Maven',
       #'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
       #'package'    : 'org.sat4j:org.sat4j.pb.jar:2.3.1',
       'package' : 'org.apache.mina:mina-core:2.0.2',
       #'getOptional': True,
       #'optional' : True,
       #'failOnError' : False,
       }]

r, rr = Project.ResolveDependencies(test)
for o in rr:
  print o, o.fileNames
#sys.exit()

#test = [{
#       'repository' : 'atta.repositories.Local',
#       'style'      : 'atta.repositories.Styles.Flat',
#       #'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
#       'package'    : 'commons-net.jar:3.0.1',
#       'getOptional': True,
#       'putIn'     : {'repository' : 'atta.repositories.Project', 'lifeTime' : 2},
#       #'putIn'     : 'atta.repositories.Local',
#       }]

#r = Project.ResolveDependencies(test)

test = [{
       'repository' : 'atta.repositories.Maven',
       #'package'    : 'org.jvnet.libzfs:libzfs.jar:0.5',
       'package'    : 'commons-net.jar:3.0.1',
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
#sys.exit()

# Get any files from FTP...

PP = PackageId.FromStr('MyFiles.set:1')
#PP.fileNames = ['include1.py', 'Inc2/includes2.py', 'Polska_1206_6.263.r37.7z']
PP.fileNames = ['include1.py', 'Inc2/includes2.py']
#PP.optional = True

from atta.repositories import Styles
OnlyFN = Styles.OnlyFileName()

test = [
    {
    'repository' : 'atta.repositories.Ftp',
    #'style'      : OnlyFN,
    #'failOnError': False,
    'host'       : p.Get('host'),
    'rootDirName': p.Get('rootDirName') + '/Inc',
    'user'       : p.Get('user'),
    'password'   : p.Get('password'),
    'package'    : PP,
    'putIn'     : {'repository' : 'atta.repositories.Local',
                   'rootDirName': Project.dirName + '/repository',
                   'lifeTime' : 15, # in seconds
                   'style' : 'atta.repositories.Styles.Flat',
                  },
    },
]

#PP.fileNames.append('zzz')
##PP.optional = True
#
#test = [
#    {
#     'repository' : 'atta.repositories.Local',
#     'rootDirName': Project.dirName + '/repository/PP',
#     'package' : PP,
#     'style' : 'atta.repositories.Styles.OnlyFileName',
#    },
#]

r = Project.ResolveDependencies(test)
#print r

class test(Target):
  def Run(self):
#    i1 = []
#    i2 = [1]
#    i3 = [4,1]
#    if i1: print 'i1'
#    if not i1: print 'not i1'
#    if i2: print 'i2'
#    if not i2: print 'not i2'
#    return
#
#    import datetime
#
#    d1 = datetime.datetime(2012,10,1,10,00,00)
#    d2 = datetime.datetime(2012,10,1,9,00,00)
#    print repr(d1 - d2)
#    print d1 - d2 > datetime.timedelta(minutes=59)
#    print repr(d2 - d1)
#    print abs(d2 - d1) > datetime.timedelta(minutes=59)
#    return
#
#    p = PackageId(artifactId='a')
#    p.exclusions += ['a']
#    print p.exclusions
#    print hash(p)
#    return

    #------------------------------------------------------------------------------

    from atta.repositories.Maven import Repository

    package = PackageId.FromStr('asm:asm-util.jar:2.2.3')
    #package = PackageId.FromStr('com.thoughtworks.xstream:xstream.jar:1.3.1')
    #package = PackageId.FromStr('ant.jar:1.6.2')
    #package = PackageId.FromStr('commons-jelly:commons-jelly-tags-xml.jar:1.1')
    #r = Repository(getOptional = True)
    #r.Get(package, 'compile')

