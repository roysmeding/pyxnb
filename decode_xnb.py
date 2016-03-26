import sys
import xnb
import xtile

if len(sys.argv) != 2:
    print('Usage: {:s} <input_file>'.format(sys.argv[0]))
    sys.exit(1)

xnb_file = xnb.XNBFile(sys.argv[1])
print(xnb_file.primaryObject)
