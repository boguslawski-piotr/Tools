
class ICompiler:
  '''TODO: description'''
  def SourceExts(self, **tparams):
    '''TODO: description'''
    pass

  def OutputExt(self, **tparams):
    '''TODO: description'''
    pass

  def GetOutput(self):
    '''TODO: description'''
    pass

class IJavaCompiler(ICompiler):
  def Compile(self, srcFiles, destDir, **tparams):
    '''TODO: description'''
    pass
  
