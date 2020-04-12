import sys
import os

args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
print(args[0])