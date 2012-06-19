import os
import glob
import shutil
import re

from atta import *
from atta.OS import *
from atta.Properties import Properties
from atta.Log import Log, LoggerBridge

if atta is None or project is None:
  raise SystemError('The program was launched outside the Atta.')

project.defaultTarget = 'help'

prop = Properties()
prop.Open('build.properties')

class help(Target):
  def Run(self):
    Echo(atta.name + ' v' + atta.versionName + \
'''
Usage: atta [target]

Available targes:
  makedocs
  clean
''')
    
class clean(Target):
  def Run(self):
    for fileName in glob.glob('*/*.py?'): os.remove(fileName)
    for fileName in glob.glob('*.py?'): os.remove(fileName)
    shutil.rmtree('docs', True)

import atta.StdLogger

class TestsLogger(atta.StdLogger.Logger):
  def __init__(self):
    open(os.path.join(project.dirName, 'tests.log'), 'wb').close()
    
  def _PhysicalLog(self, msg):
    if msg:
      print(msg)
      with open(os.path.join(project.dirName, 'tests.log'), 'a+b') as f:
        f.write(msg + os.linesep)
  
class tests(Target):
  def Run(self):
    olc = LoggerBridge.SetLoggerClass(TestsLogger)
    for fileName in glob.glob('tests/test*.py'):
      Log('\nRunning project: ' + fileName)
      project.RunProject(None, fileName, '')
    LoggerBridge.SetLoggerClass(olc)
##
#

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
  def Run(self):
    LineFilter('README.md', MD2DoxygenMD, 'README_.md')    
    Exec(prop.Get('doxygen.exe', 'doxygen'))
    os.remove('README_.md')
    #Exec('docs\index.html')

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