
class Foo:
    """
      Docstring for class Foo.

      .. note::
      
        ala ma kota
        
      .. snippet:: FooParams
      
        :param int value: exception value
        :param dict cos: cos
        :param limit: maximum number of stack frames to show
        :type limit: string or None
        
        :rtype: list of strings
        :return: a list of strings
                 
      .. todo::
        
        - nr 1
        - nr 2
          
      **Data from Foocp.rst**
            
      .. literalinclude:: ../docs/Foocp.rst 
    
      .. snippet:: ExecUsesCases
        
        Use cases:
        
        .. literalinclude:: ../tests/test_env.py
       
      .. seealso::
      
        Module :py:class:`atta.Project.Project`
          Cos...
           
        Module :py:mod:`zipfile`
          Documentation of the :py:mod:`zipfile` standard module.
      
        `GNU tar manual, Basic Tar Format <http://link>`_
          Documentation for tar archive files, including GNU tar extensions.
            
    """

    #: it lslslsls dldlldsd sdlmsds slmds sldms
    #: is
    #: a __init__
    def __init__(self):
        #: Doc comment for instance attribute qux.
        self.qux = 3

        self.spam = 4
        """Docstring for instance attribute spam."""

    #: Doc comment for class attribute Foo.bar.
    #: It can have multiple lines.
    bar = 1

    flox = 1.5   #: Doc comment for Foo.flox. One line only.

    baz = 2
    """Docstring for class attribute Foo.baz."""

