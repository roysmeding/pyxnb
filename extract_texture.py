import sys
import xnb
import xnb_graphics
from PIL import Image

if len(sys.argv) != 3:
    print('Usage: {:s} <input_file> <output_file>'.format(sys.argv[0]))
    sys.exit(1)

xnb_file = xnb.XNBFile(sys.argv[1])

t = xnb_file.primaryObject

assert isinstance(t, xnb_graphics.Texture2D), "Expected xnb_graphics.Texture2D in XNB file"

if   t.surface_format != xnb_graphics.Texture2D.FORMAT_COLOR:
    raise NotImplementedError("Only the 'COLOR' texture format is supported right now")

im = Image.frombytes("RGBA", (t.width, t.height), t.mips[0])
im.save(sys.argv[2])
