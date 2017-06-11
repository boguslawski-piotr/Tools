import sys

print('External:')
print('  ' + ' '.join(sys.argv))
for p in sys.argv:
  print('  {0}'.format(p))
