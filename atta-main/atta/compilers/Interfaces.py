'''.. no-user-reference:'''

# TODO: dodac jakis mechanizm pozwalajacy na filtrowanie plikow zrodlowych w locie,
# przed przekazaniem ich do kompilacji
# przemyslec!
# musi byc uniwersalne

class ICompiler:
  '''TODO: description'''
  def SourceExts(self, **tparams):
    '''TODO: description'''
    assert False

  def OutputExt(self, **tparams):
    '''TODO: description'''
    assert False

  def GetOutput(self):
    '''TODO: description'''
    assert False

class IJavaCompiler(ICompiler):
  '''TODO: description'''
  def Compile(self, srcFiles, destDir, **tparams):
    '''TODO: description'''
    assert False

class IRequiresCompileStrategy:
  '''TODO: description'''
  def Start(self, destDir, **tparams):
    '''Invoked before scanning the source files. The return value is not checked in any way.'''
    assert False
    
  def RequiresCompile(self, srcFileName, destFileName, **tparams):
    '''Called for each source file. Should return `True` if `srcFileName` requires compilation.'''
    assert False
    
  def End(self, **tparams):
    '''Called after scanning all the source files.
       Should return list with the source files that require compilation and 
       could not be fully tested in the :py:meth:`.IRequiresCompileStrategy.RequiresCompile`.
    '''
    assert False
