from .. import AttaError

class ArtifactNotFoundError(AttaError): 
  def __init__(self, caller, msg):
    AttaError.__init__(self, caller, msg)
    
