'''
  Atta build module.
  
  *TODO*
  
'''
import sys
import os
import glob
import shutil
import re

from atta.tools.OS import *
from atta.tools.Properties import Properties
from atta import Log
from atta import *

if project is not None:
  project.defaultTarget = 'help'

class help2(Target):
  def Run(self):
    pass
  
class help(Target):
  ''' Display help...
  '''
  DependsOn = [help2]
  
  def Run(self):
    Echo(attai.name + ' v' + attai.versionName + \
'''
Usage: atta [target]

Available targes:''')
    for m in dir(sys.modules['build']):
      d = sys.modules['build'].__dict__[m]
      if m != 'Target' and 'DependsOn' in dir(d):
        Echo('  ' + m)
    
class clean(Target):
  ''' Clean...
  '''
  def Run(self):
    Echo('Removing directories...')
    for dirName in DirSet(includes = ['**/*build', '**/dist', 'docs/html', 'docs/modules']):
      Echo('  %s' % dirName)
      shutil.rmtree(dirName, True)

    Echo('\nRemoving *.py? and *.log files...')
    for fileName in FileSet(includes = ['**/*.py?', '**/*.log']):
      Echo('  %s' % fileName)
      os.remove(fileName)
    return

import atta.loggers.StdLogger as StdLogger

class TestsLogger(StdLogger.Logger):
  def __init__(self):
    open(os.path.join(project.dirName, 'tests.log'), 'wb').close()
    
  def _PhysicalLog(self, msg):
    if msg:
      print(msg)
      with open(os.path.join(project.dirName, 'tests.log'), 'a+b') as f:
        f.write(msg + os.linesep)
  
class tests(Target):
  ''' Run Atta tasks and targets tests.
  '''
  def Run(self):
    olc = Log.SetLogger(TestsLogger)
    for fileName in FileSet(includes = 'tests/test_*.py'):
      Log.Log('\nRunning project: ' + fileName)
      project.RunProject(None, fileName, '')
    Log.SetLogger(olc)

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
      raise Exception('Unit tests are not performed correctly.')
    
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
  def Run(self):
    # doxygen
    #LineFilter('README.md', MD2DoxygenMD, 'README_.md')    
    #prop = Properties()
    #prop.Open('build.properties')
    #Exec(prop.Get('doxygen.exe', 'doxygen'))
    #os.remove('README_.md')
    
    # automodules
    MakeDirs('docs/modules')
    Echo('''Atta modules
============
''',
      file = os.path.join('docs', 'modules.rst'),
    )
    for fileName in FileSet('atta', includes = '**/*.py', excludes = ['**/__*', '**/*Test*', '**/templates/'], realPaths = False):
      #print os.path.splitext(fileName)
      fileName = RemoveExt(fileName)
      moduleName = fileName.replace(os.path.sep, '.')
      dirName, _ = os.path.split(fileName)
      if dirName:
        MakeDirs(os.path.join('docs/modules', dirName))
      Echo(''':mod:`${name}` Module
-------------------------------------------------------------------------------

.. automodule:: atta.${name}
    :members:
    :undoc-members:
    :show-inheritance:
''',
      name = moduleName,
      file = os.path.join('docs/modules', fileName) + '.rst',
      )
      
      Echo('''
${mname} module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. snippetref:: ${mname}

Details: :doc:`modules/${fname}`
''',
      mname = moduleName,
      fname = fileName.replace(os.path.sep, '/'),
      file = os.path.join('docs', 'modules.rst'),
      append = True
      )
    #return
  
    # Sphinx
    project.env.chdir('docs')
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
    MakeDirs('docs')
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
    
