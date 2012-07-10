'''.. no-user-reference:'''

# TODO: dodac jakis mechanizm pozwalajacy na filtrowanie plikow zrodlowych w locie,
# przed przekazaniem ich do kompilacji
# przemyslec!
# musi byc uniwersalne

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

