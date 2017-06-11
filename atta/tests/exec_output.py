import sys

x = 0
max = int(sys.argv[1])
while x < max:
  print('line {0}'.format(x + 1))
  y = 100000
  while y > 0:
    y -= 1
  x += 1

sys.exit(0)
