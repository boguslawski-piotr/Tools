'''Xml task tests.'''

from atta import *

Project.defaultTarget = 'test'

import re
import xml.etree.cElementTree

class Xml:
  '''Extension for xml.etree.ElementTree/xml.etree.cElementTree'''
  def __init__(self, src):
    if isinstance(src, basestring) and src.lstrip().startswith('<'):
      self._root = xml.etree.cElementTree.fromstring(src)
    else:
      self._root = xml.etree.cElementTree.parse(src).getroot()
    
#    for x in self.root.iter():
#      print x
    #print self.root.find('distributionManagement/site/url').text
    
  def root(self):
    '''Returns xml.etree.ElementTree.Element'''
    return self._root
  
  def rootNS(self):
    try:
      m = re.search('({.*})', self._root.tag)
      if m != None:
        return m.group(1)
    except: 
      pass
    return ''
  
  def values(self, match, caseSensitive = True):
    '''Returns values for tag or path as list with dicts inside
    TODO: more description
    '''
    values = []
    if len(match) <= 0:
      return values
    
    def _GetValues(e, d):
      c = list(e)
      if len(c) <= 0:
        tag = re.sub('{.*}', '', e.tag) # remove namespace, TODO: add support for namespaces
        d[tag] = e.text.strip()
      else:
        text = e.text.strip()
        if text:
          tag = re.sub('{.*}', '', e.tag) # remove namespace, TODO: add support for namespaces
          d[tag] = text 
        
        lastFlatLevel = len(list(c[0])) == 0
        if lastFlatLevel:
          tag = c[0].tag 
          for z in c[1:]:
            if z.tag != tag or len(list(z)) > 0: 
              lastFlatLevel = False
              break
            
        d = {}
        for e in c:
          _GetValues(e, d)
          if lastFlatLevel:
            values.append(d)
            d = {}
        if not lastFlatLevel:
          values.append(d)
    
    match = OS.Path.AsList(match, '/')
    root = self._root
    i = 0
    while True:
      for e in list(root):
        tag = re.sub('{.*}', '', e.tag) # remove namespace, TODO: add support for namespaces
        name = match[i]
        if not caseSensitive:
          tag = tag.lower()
          name = name.lower()
        if tag == name:
          if i < len(match) - 1:
            root = e
            break
          else:
            d = {}
            _GetValues(e, d)
            values.append(d)
      else:
        break
      i += 1
      if i >= len(match):
        break
      
    # Remove empty 'lines'.
    values = filter((lambda e: len(e)), values)
    return values
  
def printv(xml, name):
  values = xml.values(name, False)
  print 'In: %s found %d value(s):' % (name, len(values))  
  for v in values:
    print ' ', v
  
def test():
  Echo('Xml test')
  xml = Xml('test_xml.xml')
  printv( xml, 'properties' )
  printv( xml, 'distributionmanagement' )
  printv( xml, 'distributionmanagement/site/url' )
  printv( xml, 'distributionManagement/downloadUrl' )
#  d = xml.GetValues('modules/module')
#  d = xml.GetValues('modules')
#  d = xml.GetValues('parent')
  printv( xml, 'dependencies' )
#  d = xml.GetValues('dependencies/dependency')
#  d = xml.GetValues('dependencies/dependency/groupId')
#  d = xml.GetValues('dependencyManagement/dependencies/dependency')
#  d = xml.GetValues('dependencyManagement/dependencies')
  printv( xml, 'dependencyManagement' )
  
  with open('test_xml.xml', 'r') as f:
    xml = Xml(f.read())
    printv( xml, 'properties' )
    
  xmldata = '''
<xml>
  <node>
  n1
    <subnode>
    sn1
      <subsubnode>
      ssn1
      </subsubnode>
    </subnode>
  </node>  
</xml>  
'''
  xml = Xml(xmldata)
  printv( xml, 'node')  
  printv( xml, 'node/subnode')  
  printv( xml, 'node/subnode/subsubnode')
  
  return
