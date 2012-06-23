# -*- coding: utf-8 -*-
"""
  snippet
  ~~~~~~~

  Allow define snippets...
"""

from docutils import nodes

from sphinx.util.nodes import set_source_info
from sphinx.util.compat import Directive
from sphinx.locale import l_, _

"""
  Code from `sphinx.util.docfields` with minimal modifications.
"""

def _is_single_paragraph(node):
    """True if the node only contains one paragraph (and system messages)."""
    if len(node) == 0:
        return False
    elif len(node) > 1:
        for subnode in node[1:]:
            if not isinstance(subnode, nodes.system_message):
                return False
    if isinstance(node[0], nodes.paragraph):
        return True
    return False

class Field(object):
    """
    A doc field that is never grouped.  It can have an argument or not, the
    argument can be linked using a specified *rolename*.  Field should be used
    for doc fields that usually don't occur more than once.

    Example::

       :returns: description of the return value
       :rtype: description of the return type
    """
    is_grouped = False
    is_typed = False

    def __init__(self, name, names = (), label = None, has_arg = True):
        self.name = name
        self.names = names
        self.label = label
        self.has_arg = has_arg

    def make_entry(self, fieldarg, content):
        return (fieldarg, content)

    def make_field(self, types, item):
        fieldarg, content = item
        fieldname = nodes.field_name('', self.label)
        if fieldarg:
            fieldname += nodes.Text(' ')
            fieldname += nodes.Text(fieldarg)
        fieldbody = nodes.field_body('', nodes.paragraph('', '', *content))
        return nodes.field('', fieldname, fieldbody)

class GroupedField(Field):
    """
    A doc field that is grouped; i.e., all fields of that type will be
    transformed into one field with its body being a bulleted list.  It always
    has an argument.
    GroupedField should be used for doc fields that can occur more than once.
    If *can_collapse* is true, this field will revert to a Field if only used
    once.

    Example::

       :raises ErrorClass: description when it is raised
    """
    is_grouped = True
    list_type = nodes.bullet_list

    def __init__(self, name, names = (), label = None,
                 can_collapse = False):
        Field.__init__(self, name, names, label, True)
        self.can_collapse = can_collapse

    def make_field(self, types, items):
        fieldname = nodes.field_name('', self.label)
        listnode = self.list_type()
        if len(items) == 1 and self.can_collapse:
            return Field.make_field(self, items[0])
        for fieldarg, content in items:
            par = nodes.paragraph()
            par += fieldarg
            par += nodes.Text(' -- ')
            par += content
            listnode += nodes.list_item('', par)
        fieldbody = nodes.field_body('', listnode)
        return nodes.field('', fieldname, fieldbody)


class TypedField(GroupedField):
    """
    A doc field that is grouped and has type information for the arguments.  It
    always has an argument.

    Two uses are possible: either parameter and type description are given
    separately, using a field from *names* and one from *typenames*,
    respectively, or both are given using a field from *names*, see the example.

    Example::

       :param foo: description of parameter foo
       :type foo:  SomeClass

       -- or --

       :param SomeClass foo: description of parameter foo
    """
    is_typed = True

    def __init__(self, name, names = (), typenames = (), label = None, can_collapse = False):
        GroupedField.__init__(self, name, names, label, can_collapse)
        self.typenames = typenames

    def make_field(self, types, items):
        def handle_item(fieldarg, content):
            par = nodes.paragraph()
            par += nodes.Text(fieldarg)
            if fieldarg in types:
                par += nodes.Text(' (')
                # NOTE: using .pop() here to prevent a single type node to be
                # inserted twice into the doctree, which leads to
                # inconsistencies later when references are resolved
                fieldtype = types.pop(fieldarg)
                if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                    typename = u''.join(n.astext() for n in fieldtype)
                    par += nodes.Text(typename)
                else:
                    par += fieldtype
                par += nodes.Text(')')
            par += nodes.Text(' -- ')
            par += content
            return par

        fieldname = nodes.field_name('', self.label)
        if len(items) == 1 and self.can_collapse:
            fieldarg, content = items[0]
            bodynode = handle_item(fieldarg, content)
        else:
            bodynode = self.list_type()
            for fieldarg, content in items:
                bodynode += nodes.list_item('', handle_item(fieldarg, content))
        fieldbody = nodes.field_body('', bodynode)
        return nodes.field('', fieldname, fieldbody)

class snippet(nodes.Element):
    doc_field_types = [
        TypedField('parameter', label = l_('Parameters'),
                   names = ('param', 'parameter', 'arg', 'argument',
                          'keyword', 'kwarg', 'kwparam'),
                   typenames = ('paramtype', 'type'),
                   can_collapse = True),
        TypedField('variable', label = l_('Variables'),
                   names = ('var', 'ivar', 'cvar'),
                   typenames = ('vartype',),
                   can_collapse = True),
        GroupedField('exceptions', label = l_('Raises'),
                     names = ('raises', 'raise', 'exception', 'except'),
                     can_collapse = True),
        Field('returnvalue', label = l_('Returns'), has_arg = False,
              names = ('returns', 'return')),
        Field('returntype', label = l_('Return type'), has_arg = False,
              names = ('rtype',)),
    ]

    def preprocess_fieldtypes(self, types):
        typemap = {}
        for fieldtype in types:
            for name in fieldtype.names:
                typemap[name] = fieldtype, False
            if fieldtype.is_typed:
                for name in fieldtype.typenames:
                    typemap[name] = fieldtype, True
        return typemap

    def transform_all(self, node):
        """Transform all field list children of a node."""
        # don't traverse, only handle field lists that are immediate children
        self.typemap = self.preprocess_fieldtypes(snippet.doc_field_types)
        for child in node:
            if isinstance(child, nodes.field_list):
                #print child
                self.transform(child)

    def transform(self, node):
        """Transform a single field list *node*."""
        typemap = self.typemap

        entries = []
        groupindices = {}
        types = {}

        # step 1: traverse all fields and collect field types and content
        for field in node:
            fieldname, fieldbody = field
            try:
                # split into field type and argument
                fieldtype, fieldarg = fieldname.astext().split(None, 1)
            except ValueError:
                # maybe an argument-less field type?
                fieldtype, fieldarg = fieldname.astext(), ''
            typedesc, is_typefield = typemap.get(fieldtype, (None, None))

            # sort out unknown fields
            if typedesc is None or typedesc.has_arg != bool(fieldarg):
                # either the field name is unknown, or the argument doesn't
                # match the spec; capitalize field name and be done with it
                new_fieldname = fieldtype.capitalize() + ' ' + fieldarg
                fieldname[0] = nodes.Text(new_fieldname)
                entries.append(field)
                continue

            typename = typedesc.name

            # collect the content, trying not to keep unnecessary paragraphs
            if _is_single_paragraph(fieldbody):
                content = fieldbody.children[0].children
            else:
                content = fieldbody.children

            # if the field specifies a type, put it in the types collection
            if is_typefield:
                # filter out only inline nodes; others will result in invalid
                # markup being written out
                content = filter(
                    lambda n: isinstance(n, nodes.Inline) or
                              isinstance(n, nodes.Text),
                    content)
                if content:
                    types.setdefault(typename, {})[fieldarg] = content
                continue

            # also support syntax like ``:param type name:``
            if typedesc.is_typed:
                try:
                    argtype, argname = fieldarg.split(None, 1)
                except ValueError:
                    pass
                else:
                    types.setdefault(typename, {})[argname] = \
                                               [nodes.Text(argtype)]
                    fieldarg = argname

            # grouped entries need to be collected in one entry, while others
            # get one entry per field
            if typedesc.is_grouped:
                if typename in groupindices:
                    group = entries[groupindices[typename]]
                else:
                    groupindices[typename] = len(entries)
                    group = [typedesc, []]
                    entries.append(group)
                group[1].append(typedesc.make_entry(fieldarg, content))
            else:
                entries.append([typedesc,
                                typedesc.make_entry(fieldarg, content)])

        # step 2: all entries are collected, construct the new field list
        new_list = nodes.field_list()
        for entry in entries:
            if isinstance(entry, nodes.field):
                # pass-through old field
                new_list += entry
            else:
                fieldtype, content = entry
                fieldtypes = types.get(fieldtype.name, {})
                new_list += fieldtype.make_field(fieldtypes,
                                                 content)

        node.replace_self(new_list)

"""
  Snippets implementation.
"""

class Snippet(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        node = snippet()
        node.document = self.state.document
        set_source_info(self, node)

        node['name'] = self.arguments[0]
        self.state.nested_parse(self.content, self.content_offset,
                                node, match_titles = 1)

        node.transform_all(node)
        return [node]

class snippetref(nodes.Element): pass

class SnippetRef(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        node = snippetref()
        node.document = self.state.document
        set_source_info(self, node)

        node['name'] = self.arguments[0]
        return [node]

def read_snippets(app, doctree):
    env = app.builder.env
    if not hasattr(env, 'snippets'):
        env.snippets = {}
    for node in doctree.traverse(snippet):
        env.snippets[node['name']] = {'node': node.deepcopy(), 'docname' : env.docname}

def resolve_snippets(app, doctree, fromdocname):
    for node in doctree.traverse(snippet):
        node.replace_self(node.children)

    env = app.builder.env
    for node in doctree.traverse(snippetref):
        content = []
        if env.snippets.has_key(node['name']):
            #print "psn 3"
            content = env.snippets[node['name']]['node'].children
        node.replace_self(content)

def setup(app):
    app.add_node(snippet)
    app.add_node(snippetref)

    app.add_directive('snippet', Snippet)
    app.add_directive('snippetref', SnippetRef)

    app.connect('doctree-read', read_snippets)
    app.connect('doctree-resolved', resolve_snippets)

