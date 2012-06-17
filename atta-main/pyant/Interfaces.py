## \brief Various interfaces.

## Logger interface  
#
#special arguments
#  
#  build
#    start
#    end
#    status
#    at
#    time
#    
#  target
#    prepare
#    start
#    end
#    finalize
#    
#  task
#  
class ILogger():
  def Log(self, msg, **args):
    pass