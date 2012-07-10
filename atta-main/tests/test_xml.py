'''Xml tool tests.'''

from atta import *

Project.defaultTarget = 'test'

def printv(xml, name):
  values = xml.values(name, False)
  i = 0
  for v in values:
    i += len(v.keys())
  Echo('In: %s found %d value(s):' % (name, i))  
  for v in values:
    Echo('  ' + str(v))

def printxml(xml, ident = 0):  
  for e in list(xml):
    Echo('.' * ident + e.tag + str(e.attrib) + '\n', file = 'test_xml.log', append = True)
    printxml(e, ident + 2)

def test():
  Echo('Big xml data test (result in test_xml.log):')
  Echo()
  xml = Xml('test_xml.vcproj')
  Echo(xml.tag + str(xml.attrib) + '\n', file = 'test_xml.log')
  #printxml(xml, 2)
    
  Echo('POM data test:')
  Echo()
  xml = Xml('test_xml.xml')
  printv( xml, 'properties' )
  printv( xml, 'distributionmanagement' )
  printv( xml, 'distributionmanagement/site/url' )
  printv( xml, 'distributionManagement/downloadUrl' )

  printv( xml, 'modules/module' )
  printv( xml, 'modules' )
  
  printv( xml, 'dependencies' )
  printv( xml, 'dependency' )
  printv( xml, 'dependencies/dependency' )
  printv( xml, 'dependencies/dependency/groupId')

  printv( xml, 'dependencyManagement/dependencies/dependency')
  printv( xml, 'dependencyManagement/dependencies')
  printv( xml, 'dependencyManagement' )
  
  Echo()
  Echo('Simple data test:')
  Echo()
  xmldata = '''
<xml xmlns:ns2="ns2_name">
  <node>
  n1
    <subnode>
    sn1
      <ns2:subsubnode>
      ssn1
      </ns2:subsubnode>
    </subnode>
  </node>  
</xml>  
'''
  xml = Xml(xmldata)
  printv(xml, 'node')  
  printv(xml, 'node/subnode')  
  printv(xml, 'node/subnode/subsubnode')
  Echo(xml.findtext('node/subnode/subsubnode'))
  
  elem = XmlElement('new_node', {'attr' : 'value'}, ns='ns_new_node')
  elem.text = 'some text'
  elem2 = XmlElement('new_node2', {'attr' : 'value 2'})
  elem2.text = 'some text 2'
  xml.extend([elem, elem2])
  printv( xml, 'new_node')  
  printv(xml, '')  
  e = xml.find('node/subnode/subsubnode')
  Echo(e)
  
  Echo()
  
  Echo( 'makeelement:')
  Echo( xml.makeelement('cos', {}) )
  
  Echo()
  Echo('nodes count: %d' % len(xml) )
  Echo( xml[0] )
  Echo( xml[1] )
  xml[1] = XmlElement('new_node3', {'attr' : 'value 3'}, ns='ns_new_node_3')
  Echo( xml[1] )
  del xml[1]
  Echo( xml[1] )
  xml.remove(elem2)
  Echo( 'nodes count: %d' % len(xml) )
  
  from atta.repositories.Maven import Repository
  from atta.repositories.Package import PackageId
  
  Echo()  
  Echo('POM data test 2:')
  with open('test_xml.pom', 'r') as f:
    pom = f.read()
  package = PackageId()
  Echo(Repository.GetDependenciesFromPOM(package, pom, ['compile'], True, Atta.Log))
