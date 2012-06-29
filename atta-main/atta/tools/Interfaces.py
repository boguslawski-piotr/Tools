import os
import OS

class IVariablesExpander:
  '''
  IVariablesExpander interface
  
  TODO: description
  '''
  def Expand(self, txt, **tparams): 
    pass  
  
#------------------------------------------------------------------------------ 

class ICompareStrategy:
  def ActionNeeded(self, src, dest):
    '''Should return True if "action" is nedded.'''
    pass
  
#------------------------------------------------------------------------------ 

class IArchiveFile:
  def __init__(self, fileName, mode, password = None, **tparams): 
    pass
  def close(self):
    pass
  def CanWrite(self):
    pass
  def write(self, file_, arcName):
    pass
  def writestr(self, data, arcName):
    pass
  def CanRead(self):
    pass
  def read(self, fileName, password = None):
    pass
  def FileTime(self, fileName):
    pass
  def HasCRCs(self):
    pass
  def FileCRCn(self, fileName):
    pass
  def FileCRC(self, fileName):
    pass

    