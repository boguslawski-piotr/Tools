'''.. no-user-reference:'''

class ICompareStrategy:
  '''TODO: description'''
  def ActionNeeded(self, src, dest):
    '''Should return True if "action" is nedded.'''
    pass

#------------------------------------------------------------------------------ 

class IVariablesExpander:
  '''
  IVariablesExpander interface
  
  TODO: description
  '''
  def Expand(self, txt, **tparams):
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

#------------------------------------------------------------------------------ 

class IVersionStrategy:
  '''TODO: description'''
  def NextMajor(self, v):
    '''TODO: description'''
    pass
  def NextMinor(self, v):
    '''TODO: description'''
    pass
  def NextPath(self, v):
    '''TODO: description'''
    pass
  def NextBuild(self, v):
    '''TODO: description'''
    pass

class IVersionListener:
  '''TODO: description'''
  def AfterConfigure(self, v):
    '''TODO: description'''
    pass
  def NextMajor(self, v):
    '''TODO: description'''
    pass
  def NextMinor(self, v):
    '''TODO: description'''
    pass
  def NextPatch(self, v):
    '''TODO: description'''
    pass
  def NextBuild(self, v):
    '''TODO: description'''
    pass
  def SetPrefix(self, v):
    '''TODO: description'''
    pass
  def SetPostfix(self, v):
    '''TODO: description'''
    pass
  def AfterRead(self, v):
    '''TODO: description'''
    pass
  def BeforeUpdate(self, v):
    '''TODO: description'''
    pass
  def AfterUpdate(self, v):
    '''TODO: description'''
    pass
