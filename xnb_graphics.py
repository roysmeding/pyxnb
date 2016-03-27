import xnb
from xnb import read_bool, read_u8, read_i32, read_u32, read_float

class Texture2D(object):
    FORMAT_COLOR        = 0
    FORMAT_BGR565       = 1
    FORMAT_BGRA5551     = 2
    FORMAT_BGRA4444     = 3
    FORMAT_DXT1         = 4
    FORMAT_DXT3         = 5
    FORMAT_DXT5         = 6
    FORMAT_NB2          = 7
    FORMAT_NB4          = 8
    FORMAT_RGBA1010102  = 9
    FORMAT_RG32         = 10
    FORMAT_RGBA64       = 11
    FORMAT_ALPHA8       = 12
    FORMAT_SINGLE       = 13
    FORMAT_VECTOR2      = 14
    FORMAT_VECTOR4      = 15
    FORMAT_HALFSINGLE   = 16
    FORMAT_HALFVECTOR2  = 17
    FORMAT_HALFVECTOR4  = 18
    FORMAT_HDRBLENDABLE = 19

    def __init__(self, stream):
        self.surface_format = read_i32(stream)

        self.width  = read_u32(stream)
        self.height = read_u32(stream)

        n_mips = read_u32(stream)
        self.mips = []
        for i in range(n_mips):
            data_size = read_u32(stream)
            self.mips.append(stream.read(data_size))

xnb.register_reader('Microsoft.Xna.Framework.Content.Texture2DReader', Texture2D)
