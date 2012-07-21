""".. no-user-reference:"""
from __future__ import print_function
import sys
from time import time
import math

class Bar:
  def __init__(self, title = 'Downloaded', max = 0):
    self.count = 0
    self.max = max
    self.title = title
    self.bpsArray = []
    self.startTime = time()
    self.Feed(0)

  def Feed(self, count):
    if sys.stdout.isatty():
      self.count += count

      bps = int(self.count / max(1, (time() - self.startTime)))
      self.bpsArray.append(bps)
      if len(self.bpsArray) > 100:
        del self.bpsArray[0]
      bps = sum(self.bpsArray, 0) / len(self.bpsArray) / 1024
      count = self.count / 1024 / 1024.0

      if self.max > 0:
        percet = min(100.0, math.ceil(float(self.count) / float(self.max) * 100.0))
        print("{4}: {2}% ({3}KB/s) ({0:.2f}MB / {1:.2f}MB)".format(count,
                                                                   self.max / 1024 / 1024.0,
                                                                   int(percet),
                                                                   bps,
                                                                   self.title),
              sep = '', end = '\r')
      else:
        print("{2}: {0:.2f}MB ({1}KB/s)".format(count, bps, self.title),
              sep = '', end = '\r')

  def End(self):
    self.totalTime = time() - self.startTime
    if sys.stdout.isatty():
      print(' ' * 80 + '\r', end = '')
