'''
Atta build module.

TODO: description
'''
import sys
import os
import glob
import shutil
import re

from atta.tools.Properties import Properties
from atta.tools.Misc import Logger
import atta.tools.OS as OS
from atta import *

if Project is not None:
  Project.defaultTarget = 'help'

#------------------------------------------------------------------------------ 

class help(Target):
  ''' Display help...
  '''
  def Run(self):
    Echo(Atta.name + ' v' + Atta.versionName + \
'''
Usage: atta [target]

Available targes:''')
    for m in dir(sys.modules['build']):
      d = sys.modules['build'].__dict__[m]
      if m != 'Target' and 'dependsOn' in dir(d):
        Echo('  ' + m)
    
#------------------------------------------------------------------------------ 

class cleandirs(Target):
  ''' Clean docs and dist
  '''
  def Run(self):
    Echo('Removing directories...')
    for dirName in DirSet(includes = ['**/*build', '**/dist', '**/bin', 'docs/html', 'docs/modules']):
      Echo('  %s' % dirName)
      shutil.rmtree(dirName, True)
      
class clean(Target):
  ''' Clean...
  '''
  dependsOn = [cleandirs]
  def Run(self):
    Echo('\nRemoving files:')
    for fileName in FileSet(includes = ['**/*.py?', '**/*.log', '**/*.class', '**/*.jar', 'tests/test_Java']):
      Echo('%s' % fileName)
      os.remove(fileName)

#------------------------------------------------------------------------------ 

import atta.loggers.Std as Std

class TestsLogger(Std.Logger):
  def __init__(self):
    open(os.path.join(Project.dirName, 'tests.log'), 'wb').close()
    
  def _PhysicalLog(self, msg):
    if msg:
      with open(os.path.join(Project.dirName, 'tests.log'), 'a+b') as f:
        f.write(msg + os.linesep)
  
class tests(Target):
  ''' Run Atta tasks and targets tests.
  '''
  def Run(self):
    listener = Atta.logger.RegisterListener(TestsLogger)
    for fileName in FileSet(includes = 'tests/test_*.py', excludes="**/test_exec_output.py"):
      self.Log('\nRunning project: ' + fileName)
      Project.RunProject(None, fileName, '')
    Atta.logger.UnRegisterListener(listener)

#------------------------------------------------------------------------------ 

class unittests(Target):
  ''' Run Atta unit tests.
  '''
  def Run(self):
    from datetime import datetime
    Echo('''

STARTED at: %s
======================================================================

''' % datetime.today(), 
      file = 'unittests.log', 
      append = True
    )
    
    t = PyExec('-m', ['unittest', 'discover', '-v', '-p', '*', '-s', 'tests\unittest'], failOnError = False, useShell = False)

    Echo(t.output, file = 'unittests.log', append = True)
    
    if t.returnCode != 0:
      raise AttaError(self, 'Unit tests are not performed correctly.')
    
    return
  
def MD2DoxygenMD(lineNo, line):
  if lineNo == 1: 
    line = line.replace('\n', '') + ' {#mainpage}\n'
  line = line.replace('```python', '~~~{.py}')
  line = line.replace('```', '~~~')
  return line

## TODO: make Task from this function
def LineFilter(inFile, filterFunc, outFile = None):
  # TODO: handle file-like objects, FileSet, etc.
  contens = ''
  with open(inFile, 'r') as f:
    lineNo = 1
    for line in f.readlines():
      contens = contens + filterFunc(lineNo, line)
      lineNo += 1
  if outFile is not None:
    with open(outFile, 'w') as f:
      f.write(contens)
  return contens

class makedocs(Target):
  ''' Make Atta documentation.
  '''
  dependsOn = [cleandirs]
  def Run(self):
    # doxygen
    #LineFilter('README.md', MD2DoxygenMD, 'README_.md')    
    #prop = Properties.Open('build.properties')
    #Exec(prop.Get('doxygen.exe', 'doxygen'))
    #os.remove('README_.md')
    
    # automodules
    OS.MakeDirs('docs/modules')
    Echo('Generating developer automodules...')
    m = FileSet('atta', includes = ['**/*.py'], excludes = ['**/__*', '**/*Test*', '**/templates/'], realPaths = False)
    for fileName in m:
      fileName = OS.Path.RemoveExt(fileName)
      Echo('  ' + fileName)
      moduleName = fileName.replace(os.path.sep, '.')
      dirName, _ = os.path.split(fileName)
      if dirName:
        OS.MakeDirs(os.path.join('docs/modules', dirName))
      
      Echo(''':mod:`${name}` Module
-------------------------------------------------------------------------------

.. automodule:: ${fullName}
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:
    :member-order: bysource
''',
      name = moduleName,
      fullName = 'atta.' + moduleName,
      file = os.path.join('docs/modules', fileName) + '.rst',
      )
      

    Echo()
    Echo('Generating user automodules...')
    m = {}
    for fileName in FileSet('atta', includes = ['targets/**/*.py', 'tasks/**/*.py', 'tools/**/*.py'], excludes = ['**/__*', '**/*Test*', '**/templates/'], realPaths = False):
      group = fileName.split(os.path.sep)[0]
      subgroup = 'TODO'
      desc = ''
      with open(os.path.join('atta', fileName), 'r') as f:
        line = f.readline()
        line = line.replace("'''", "").strip()
        if line == '.. :no-user-reference:':
          continue
        line = line.replace(".. ", "").strip()
        w = line.split(':')
        if len(w) > 1:
          subgroup = w[0]
          del w[0]
        desc = w[0]
      
      if group in m:
        if subgroup in m[group]:
          m[group][subgroup].append([desc, fileName])
        else:
          m[group][subgroup] = [[desc, fileName]]
      else:
        m[group] = { subgroup : [[desc, fileName]] }
    
    prevGroup = nextGroup = ''
    for i, group in enumerate(sorted(m.keys())):
      groupFileName = os.path.join('docs', group + '.rst')
      groupData = '''Atta ${groupName}
===============================================================================

'''
      Echo(groupFileName)
      for subgroup in m[group]:
        outputFile = os.path.join('docs/modules_user/', group, subgroup)
        OS.MakeDirs(outputFile)
        groupData = groupData + subgroup + '''
-------------------------------------------------------------------------------        

.. toctree::
  :glob:

  modules_user/${group}/''' + subgroup + '/*\n\n'
        for doc in m[group][subgroup]:
          #print doc
          fileName = OS.Path.RemoveExt(doc[1])
          desc = doc[0]
          moduleName = OS.Path.Ext(fileName.replace(os.path.sep, '.'), False)
          Echo('  ' + fileName + ' -> ' + moduleName)
          Echo('''${moduleName} - ${desc}
-------------------------------------------------------------------------------

.. automodule:: ${fullName}
    :members:
    :undoc-members:
    :member-order: bysource
    :noindex:
    ''',
          moduleName = moduleName,
          desc = desc,
          fullName = 'atta.' + fileName.replace(os.path.sep, '.'),
          file = os.path.join(outputFile, moduleName) + '.rst',
          )
          
      nextGroup = sorted(m.keys())[i + 1] if i < len(sorted(m.keys())) - 1 else ''
      
#      if len(prevGroup) > 0 or len(nextGroup) > 0:
      groupData = groupData + '''
      
-------------------------------------------------------------------------------


'''        
      groupData = groupData + '* '
      if len(prevGroup) > 0:
        groupData = groupData + '| :doc:`' + prevGroup + '` '
      if len(nextGroup) > 0:
        groupData = groupData + '| :doc:`' + nextGroup + '` '
      groupData = groupData + '''| :ref:`genindex` | :ref:`search`'''
      groupName = group[0].upper() + group[1:]
      Echo(groupData, 
            group = group, 
            groupName = groupName, 
            file = groupFileName)
      prevGroup = group
    #return 
    
    # Sphinx
    Project.env.chdir('docs')
    Exec('make', ['clean'], logOutput = False)
    Exec('make', ['html'])
    
    # Show documentation
    #Exec(os.path.join('html', 'index.html'))

class makedocs_old(Target):
  def Run(self):
    # TODO: task typu GlobEx - z wyrazeniemi regularnymi i chodzeniem po wszystkich katalogach, includes, excludes, itp. (walk?)
    pyFiles = glob.glob('atta/*.py')
    for file in pyFiles:
      if file.endswith('__init__.py'):
        file = 'atta'
      with PyExec('pydoc.py', ['-w', file], logOutput=False, failOnError=False) as proc:
        #Echo(proc.output)
        #Echo(proc.returnCode)
        pass
        
    # TODO: zestaw taskow do tego rodzaju operacji...
    try: shutil.rmtree('docs')
    except: pass
    OS.MakeDirs('docs')
    for fileName in os.listdir('.'):
      if re.search('.*.html', fileName) != None:
        shutil.move(fileName, 'docs')

    # TODO: zestaw taskow do roznego rodzaju filtrowanie (?)
    for fileName in os.listdir('docs'):
      output = ''
      with open(os.path.join('docs', fileName)) as f:
        for line in f.readlines():
          
          # replace links generated by pydoc
          while True:
            m = re.search('atta\.([a-zA-z]+\.html)', line)
            if m != None: line = str(line).replace(m.group(0), m.group(1))
            else: break

          m = re.search('\_((.+)\.html)', line)
          if m != None: 
#            print( '* ' + m.group(0))
#            print( m.group(1))
#            print( m.group(2))
            line = str(line).replace(m.group(0), '<a href="' + m.group(1) + '">Details</a>')

          m = re.search('\^(([a-zA-z\_\-]+)\.html)', line)
          if m != None: 
            line = str(line).replace(m.group(0), '<a href="' + m.group(1) + '">' + m.group(2) + '</a>')
          
          m = re.search('\_Tests_(([a-zA-z\_\-]+)\.py)', line)
          if m != None: 
            line = str(line).replace(m.group(0), '<a href="../Tests/' + m.group(1) + '">See the ' + m.group(2) + ' use case.</a>')

          m = re.search('\^type( |\&nbsp\;)', line)
          if m != None: 
            line = str(line).replace(m.group(0), '<i>Type:</i>')
          m = re.search('\^def( |\&nbsp\;)', line)
          if m != None: 
            line = str(line).replace(m.group(0), '<i>Default:</i>')
          
          output = output + line;
      
      with open(os.path.join('docs', fileName), 'w') as f:
        f.write(output)
    
    Echo('OK')
    
