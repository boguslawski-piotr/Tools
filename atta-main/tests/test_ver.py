'''PyExec task tests.'''

from atta import *

Project.defaultTarget = 'test'

def test():
  # Valid, existing file.
  v = Version(fileName = 'test_ver.txt')
  Echo('  Initial:' + str(v))
  v.NextBuild(True)
  Echo('NextBuild:' + str(v))
  v.NextPatch(True)
  Echo('NextPatch:' + str(v))  
  v.NextMinor(True)
  Echo('NextMinor:' + str(v))  
  v.NextMajor(True)
  Echo('NextMajor:' + str(v))
  
  # New file.
  Echo()
  v = Version(fileName = 'test_ver.log')
  Echo(v)
  v.NextBuild(True)

  # Not valid. Version info will be add at the end.
  Echo('''import something

Line 1
  Line 2
    Line 3
      Line 4      ''', 
    file = 'test_ver.info', force = True)
  Echo()

  def VObserver(v, event):
    Echo('%s sent event: %d' % (v.fileName, event))
  
  v = Version(fileName = 'test_ver.info', observers = [VObserver])
  Echo(v)
  v.NextMajor(True)
  