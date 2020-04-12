import sys
import os
import time

# There is likely a better way to do this but I couldn't find it

args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
pid = args[0]
os.system(f'kill {pid}')
os.system(f'git pull')
time.sleep(10)
