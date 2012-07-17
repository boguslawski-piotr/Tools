from atta import *
from atta.targets.Java import *

Project.defaultTarget = 'test'
Project.name = 'test_Java'

class test(Target):
  def Run(self):
    # Compile java source files.
    Javac('*.java')

    # Create basic manifest.
    manifest = {'Main-Class' : Project.name, }

    # Create jar file.
    Jar(Project.name, '*.class', manifest)

    # Run application.
    Exec('java', ['-jar', Project.name])

