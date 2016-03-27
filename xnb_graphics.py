import xnb
from xnb import read_bool, read_u8, read_i32, read_u32, read_float

class Texture2D(object):
    def __init__(self, stream):
        self.surface_format = read_i32(stream)

        self.width  = read_u32(stream)
        self.height = read_u32(stream)

        n_mips = read_u32(stream)
        mips = []
        for i in range(n_mips):
            data_size = read_u32(stream)
            mips.append(stream.read(data_size))

xnb.register_reader('Microsoft.Xna.Framework.Content.Texture2DReader', Texture2D)
