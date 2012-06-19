## \brief Environment properties test.

from atta import *

if attai is None or project is None:
  raise SystemError('The program was launched outside the Atta.')

project.defaultTarget = 'test'

# Property file.name is available only in 
# the interpretation of the file, 
# NOT when performing tasks.
Echo('File:')
Echo('  name: ' + file.name)

class test(Target):
  def Run(self):
    Echo('Atta:')
    Echo('     Version name: ' + attai.versionName)
    Echo('  Version numeric: ' + str(attai.version))
    Echo('   Home directory: ' + attai.dirName)

    Echo()
    Echo('Project:')
    Echo('   dirName: ' + project.dirName)
    Echo('  fileName: ' + project.fileName)
    
    Echo()
    Echo('Project.Env:')
    for var, v in project.env.vars.iteritems():
      Echo('  {0:<20}: {1}'.format(var, v))
    
    Echo()
    project.env['test_env'] = project.dirName
    Echo('  {0:<20}: {1}'.format('test_env', project.env['test_env']))
    