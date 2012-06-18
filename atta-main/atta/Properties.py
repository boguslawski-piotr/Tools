import os, cStringIO, ConfigParser

## Supports the Java properties files.
#  \ingroup Utils 
class Properties:
  ## Reads a property list (key and element pairs) from the file.
  def Open(self, fileName):
    f = cStringIO.StringIO()
    f.write('[p]\n')
    f.write(open(fileName, 'r').read())
    f.seek(0, os.SEEK_SET)
    self.c = ConfigParser.RawConfigParser()
    self.c.readfp(f)
    f.close()
    return self

  ## Searches for the property with the specified key in this property list. 
  #  The method returns the default value argument if the property is not found. 
  def Get(self, name, default = None):
    try:
      return self.c.get('p', name)
    except:
      return default
    