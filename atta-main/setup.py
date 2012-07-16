# A very simple setup script to create a single Atta executable.
# Needs cx_Freeze utility: http://cx-freeze.sourceforge.net/
#
# Run the build process by running the command 'python setup.py build'.
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the script without Python.

import cx_Freeze
import sys

from atta import Atta

buildExeOptions = {
  "packages" : ["atta"],
  "copy_dependent_files" : True,
  "include_files" : ["atta.properties", 'docs/html'],
}

targetExt = ''
if sys.platform == 'win32':
  targetExt = '.exe'

cx_Freeze.setup(
  name = Atta.name,
  version = Atta.version,
  description = Atta.description,
  options = dict(build_exe = buildExeOptions),
  executables = [cx_Freeze.Executable('main.py', targetName = 'atta' + targetExt, base = 'Console')]
)

