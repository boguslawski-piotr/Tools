from ..tools.Archivers import ZipFile
from Archive import Archive

class Zip(Archive):  
  def __init__(self, fileName, srcs, **tparams):
    Archive.__init__(self, ZipFile, fileName, srcs, **tparams)
    
