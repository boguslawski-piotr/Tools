# A very simple setup script to create a single Atta executable.
# Needs cx_Freeze utility: http://cx-freeze.sourceforge.net/
#
# Run the build process by running the command 'python setup.py build'.
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python.

from cx_Freeze import setup, Executable
from atta.version import attaVersionName
import sys

buildExeOptions = {
  "packages" : ["atta"], 
  "copy_dependent_files" : True,  
  "include_files" : ["atta.properties", 'docs/html'],
}  

targetExt = ''
if sys.platform == 'win32':
  targetExt = '.exe'

setup(
  name = 'Atta',
  version = attaVersionName,
  description = 'Atta',
  options = dict(build_exe = buildExeOptions),
  executables = [Executable('main.py', targetName = 'atta' + targetExt, base = 'Console')]
)

