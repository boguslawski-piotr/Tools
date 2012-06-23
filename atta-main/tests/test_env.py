'''Environment properties test.'''

from atta import *

if Project is None:
  raise SystemError('The program was launched outside the Atta.')

Project.defaultTarget = 'test'

Echo('File:')
Echo('  name: ' + File.name)

class test(Target):
  def Run(self):
    Echo('Atta:')
    Echo('  versionName: ' + Atta.versionName)
    Echo('      version: ' + str(Atta.version))
    Echo('      dirName: ' + Atta.dirName)

    Echo()
    Echo('Project:')
    Echo('   dirName: ' + Project.dirName)
    Echo('  fileName: ' + Project.fileName)
    
    Echo()
    Echo('Project.Env:')
    for var, v in Project.env.iteritems():
      Echo('  {0}: {1}'.format(var, v))
    
    Echo()
    Project.env['test_env'] = Project.dirName
    Echo('  {0}: {1}'.format('test_env', Project.env['test_env']))
    