""".. Data manipulation: Support for Xml data and files: xml"""
import sys
import re
import xml.etree.ElementTree as ET

from . import OS
from . import Misc

class XmlElement(ET.Element):
  """TODO: description
  You can use any attribute and method from :py:class:`.ElementTree.Element`.
  """

  ns = None
  '''element namespace TODO: description'''

  parent = None
  '''TODO: description'''

  def __init__(self, tag, attrib = {}, ns = '', **extra):
    self.ns = ns
    self._parent = None
    ET.Element.__init__(self, tag, attrib, **extra)

  def append(self, element):
    element._setparent(self)
    ET.Element.append(self, element)

  def insert(self, index, element):
    element._setparent(self)
    ET.Element.insert(self, index, element)

  def extend(self, elements):
    for e in elements:
      e._setparent(self)
    ET.Element.extend(self, elements)

  def values(self, match, caseSensitive = True, stripfn = lambda str: str):
    """Returns values for tag or path as list with dicts inside...
    It's more flexible and powerful version of Element.findtext.
    TODO: more and better description

    Example:

    .. code-block:: xml

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

    .. code-block:: python

      >>> xml = Xml(xmldata)
      >>> print xml.values('node')
      [{'subsubnode': 'ssn1'}, {'subnode': 'sn1'}, {'node': 'n1'}]
      >>> print xml.values('node/subnode')
      [{'subsubnode': 'ssn1'}, {'subnode': 'sn1'}]
      >>> print xml.values('node/subnode/subsubnode')
      [{'subsubnode': 'ssn1'}]

    """
    values = []

    def _GetValues(e, d):
      c = list(e)
      if len(c) <= 0:
        if e.text:
          d[e.tag] = stripfn(e.text)
      else:
        if e.text:
          text = stripfn(e.text)
          if text:
            d[e.tag] = text

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

    if len(match) <= 0:
      # Return all values in whole document (it is not very useful, but who knows?)
      d = {}
      _GetValues(self, d)
      values.append(d)
    else:
      match = OS.Path.AsList(match, '/')
      root = self
      i = 0
      while True:
        for e in list(root):
          tag = e.tag
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

  @staticmethod
  def _splittag(tag):
    """Split `tag` on the `namespace` and `name` (supported format: ``{namespace}name)``."""
    try:
      m = re.search('({(.*)})', tag)
      if m != None:
        return (m.group(2), tag.replace(m.group(1), ''))
    except:
      pass
    return ('', tag)

  def _setparent(self, parent):
    self._parent = parent

  def _setns(self):
    if len(self.ns) <= 0:
      self.ns, self.tag = XmlElement._splittag(self.tag)
    return self.ns

  @staticmethod
  def __repr(parent, ident):
    if parent == None:
      return 'None'
    return "<XmlElement: ns: %s tag: %s text: %s attrib: %s\n" % \
       (repr(parent.ns), repr(parent.tag), repr(parent.text), str(parent.attrib)) \
       + ' ' * ident + \
       "%s>" % (XmlElement.__repr(parent._parent, ident + 2))

  def __repr__(self):
    return XmlElement.__repr(self, 2)

class _TreeBuilderEx(ET.TreeBuilder):
  def end(self, tag):
    _last = ET.TreeBuilder.end(self, tag)
    if _last != None:
      if len(self._elem):
        _last._setparent(self._elem[-1])

class Xml:
  """Extension for xml.etree.ElementTree.ElementTree. As nodes uses XmlElement.
  desc for:
  __getitem__
  __delitem__
  remove
  and others from Element
  """
  def __init__(self, src):
    self.namespaces = None
    self.read(src)

  def read(self, src):
    """src can be: xml data (as string), filename or filelike object"""
    parser = ET.XMLParser(target = _TreeBuilderEx(XmlElement))
    if isinstance(src, basestring) and src.lstrip().startswith('<'):
      self._root = ET.XML(src, parser)
    else:
      self._root = ET.parse(src, parser).getroot()
    for e in self._root.iter():
      e._setns()

  def write(self, f, **tparams):
    """TODO: description"""
    # TODO: handle namespaces...
    self._buildnamespaces()
    return ET.ElementTree(self._root).write(f, **tparams)

  def append(self, element):
    """TODO: description"""
    element._setns()
    self._root.append(element)

  def insert(self, index, element):
    """TODO: description"""
    element._setns()
    self._root.insert(index, element)

  def extend(self, elements):
    """TODO: description"""
    for e in elements:
      e._setns()
    self._root.extend(elements)

  def __setitem__(self, index, element):
    element._setparent(self._root)
    element._setns()
    self._root[index] = element

  def __getattr__(self, name):
    attr = getattr(self._root, name, None)
    if not attr:
      raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, name))
    return attr

  def _buildnamespaces(self):
    self.namespaces = {}
    i = 0
    for e in self._root.iter():
      prefix = str(i)
      if e.ns in ET._namespace_map:
        prefix = ET._namespace_map[e.ns]
      if e.ns in self.namespaces:
        self.namespaces[e.ns][1] += 1
      else:
        self.namespaces[e.ns] = [prefix, 1]
        i += 1

  def _setroot(self, element):
    self._root = element
    self._buildnamespaces()
