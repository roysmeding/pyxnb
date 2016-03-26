import io
import xnb

PROPERTY_BOOL   = 0
PROPERTY_INT    = 1
PROPERTY_FLOAT  = 2
PROPERTY_STRING = 3

from xnb import read_bool, read_u8, read_i32, read_float

def read_xtile_string(stream):
    length = read_i32(stream)
    return stream.read(length).decode('utf-8')

class Size(object):
    def __init__(self, w, h):
        self.width  = w
        self.height = h

    def __str__(self):
        return "{:d}x{:d}".format(self.width, self.height)


def read_size(stream):
    width  = read_i32(stream)
    height = read_i32(stream)
    return Size(width, height)

def read_properties(stream):
    properties = {}
    n_properties = read_i32(stream)
    for i in range(n_properties):
        key = read_xtile_string(stream)
        value_type = read_u8(stream)

        if   value_type == PROPERTY_BOOL:
            properties[key] = read_bool(stream)

        elif value_type == PROPERTY_INT:
            properties[key] = read_i32(stream)

        elif value_type == PROPERTY_FLOAT:
            properties[key] = read_float(stream)

        elif value_type == PROPERTY_STRING:
            properties[key] = read_xtile_string(stream)

    return properties

class StaticTile(object):
    def __init__(self, stream, layer, tilesheet):
        self.tile_index = read_i32(stream)
        self.blend_mode = read_u8(stream)
        self.layer      = layer
        self.tilesheet  = tilesheet

        self.properties = read_properties(stream)

class AnimatedTile(object):
    def __init__(self, stream, layer):
        self.frame_interval = read_i32(stream)

        frame_count    = read_i32(stream)
        tile_frames = []

        tilesheet = None
        while frame_count > 0:
            ch = stream.read(1)

            if   ch == b'T':
                ts_id = read_xtile_string(stream)
                tilesheet = layer.parent.get_tilesheet(ts_id)

            elif ch == b'S':
                tile_frames.append(StaticTile(stream, layer, tilesheet))
                frame_count -= 1

            else:
                raise ValueError("Unexpected control character '{}' in animated tile definition".format(ch))

        self.layer      = layer
        self.tilesheet  = tilesheet

        self.properties  = read_properties(stream)

class Layer(object):
    def __init__(self, stream, parent):
        self.parent      = parent

        self.layer_id    = read_xtile_string(stream)
        self.visible     = read_bool(stream)
        self.description = read_xtile_string(stream)
        self.size        = read_size(stream)
        self.tile_size   = read_size(stream)

        self.tiles = [[None]*self.size.width for y in range(self.size.height)]

        self.properties  = read_properties(stream)

        y = 0
        tilesheet = None
        while y < self.size.height:
            x = 0
            while x < self.size.width:
                ch = stream.read(1)

                if   ch == b'T':
                    ts_id = read_xtile_string(stream)
                    tilesheet = parent.get_tilesheet(ts_id)

                elif ch == b'N':
                    null_count = read_i32(stream)
                    x += null_count

                elif ch == b'S':
                    self.tiles[y][x] = StaticTile(stream, self, tilesheet)
                    x += 1

                elif ch == b'A':
                    self.tiles[y][x] = AnimatedTile(stream, self)
                    x += 1

                else:
                    raise ValueError("Unexpected control character '{}' in layer definition".format(ch))

            y += 1

class Tilesheet(object):
    def __init__(self, stream, parent):
        self.ts_id        = read_xtile_string(stream)
        self.description  = read_xtile_string(stream)
        self.image_source = read_xtile_string(stream)

        self.sheet_size   = read_size(stream)
        self.tile_size    = read_size(stream)
        self.margin       = read_size(stream)
        self.spacing      = read_size(stream)

        self.properties   = read_properties(stream)

class Map(object):
    @staticmethod
    def read(stream):
        data_length = read_i32(stream)
        data = stream.read(data_length)
        substream = io.BytesIO(data)

        return Map(substream)

    def __init__(self, stream):
        magic = stream.read(6)
        assert magic == b'tBIN10', "xTile block does not start with 'tBIN10' header"

        # read general metadata
        self.map_id      = read_xtile_string(stream)
        self.description = read_xtile_string(stream)
        self.properties  = read_properties(stream)

        # read tilesheets
        n_tilesheets = read_i32(stream)
        self.tilesheets = {}
        for i in range(n_tilesheets):
            ts = Tilesheet(stream, self)
            self.tilesheets[ts.ts_id] = ts 

        # read layers
        n_layers = read_i32(stream)
        self.layers = []
        for i in range(n_layers):
            self.layers.append(Layer(stream, self))

    def get_tilesheet(self, ts_id):
        return self.tilesheets[ts_id]


xnb.register_reader('xTile.Pipeline.TideReader', Map.read)
