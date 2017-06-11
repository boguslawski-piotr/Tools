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
    optional = False,
    exclusions = 'xml-apis, stax:stax-api:1.0',
    #exclusions = ['xml-apis', 'stax:stax-api:1.0'],
    #exclusions = [dict(artifactId = 'xml-apis'), 'stax:stax-api:1.0'],
    # TODO: przemyslec to jeszcze, zmiana nazwy?
    getOptional = False
  )
]
