from atta import *
from atta.targets import Java

Project.groupId = 'org.atta'
# TODO: umozliwic (atta.properties?) globalne ustawianie parametrow projektow (jak groupId, type, itp. itd.)
Java.Setup(mainClass = 'main')

# This is "fake" dependency. Only for example.
Project.dependsOn += [
  dict(
    repository = 'atta.repositories.Maven',
    package = 'dom4j:dom4j.jar:1.6.1',
    #package = 'com.beust:jcommander:1.13',
    optional = True,
    # TODO: przemyslec to jeszcze, zmiana nazwy?
    getOptional = True
  )
]
