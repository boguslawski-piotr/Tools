from atta import *
from atta.targets import Java

Project.groupId = 'pl.aqurat'
Project.version.Configure(fileName = 'version.number',
                          format = Version.Formats.MM)

#Project.dvcs = Git()

Java.Setup()

Project.dependsOn = ['com.beust:jcommander:1.26', 'commons-net:commons-net:3.1']

Project.packageAdditionalFiles += [Project.version.fileName]

class deploy(Java.deploy):
  def NextVersion(self):
    Project.version.NextMinor()
  def GetCommitMessage(self):
    return Project.name + ': next minor version number'
