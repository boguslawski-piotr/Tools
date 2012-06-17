## \package [task_name] 
#  \brief   [task_name] task 
#  \ingroup Tasks 
#
# \task{[task_name](...)}
#
# \param  ... ...
#             \type ... 
#             \def ...
#
# \tparam ... ...
#             \type ... 
#             \def ...
#  
# \uc [task_name].py
#
# \impl{pyant.[task_name].[task_name]}
#
# \todo 
#
# \author [author]
#
# \example [task_name].py
# [task_name] task use cases.

from pyant.BaseClasses import Task
from pyant.Log import LogLevel

# [task_name] task implementation
class [task_name](Task):
  def __init__(self, msg = '', **args):  
    pass
  