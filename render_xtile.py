import sys
import xnb
import xnb_graphics
import xtile
from PIL import Image
import os

if len(sys.argv) != 4:
    print('Usage: {:s} <input_file> <asset_dir> <output_file>'.format(sys.argv[0]))
    sys.exit(1)

xnb_file = xnb.XNBFile(sys.argv[1])

assert isinstance(xnb_file.primaryObject, xtile.Map), "File does not contain XTile map object"

def loadImage(source):
    source = os.path.join(*source.split('\\'))
    filename = os.path.join(sys.argv[2], source) + '.png'
    return Image.open(filename)

m = xnb_file.primaryObject

print("Loading tilesheets")
for tilesheet in m.tilesheets:
    print("\t{} ({})".format(tilesheet.ts_id, tilesheet.image_source))
    tilesheet.image = loadImage(tilesheet.image_source)


map_w = map_h = 0
tile_w = tile_h = None

for layer in m.layers:
    map_w = max(map_w, layer.size.width)
    map_h = max(map_h, layer.size.height)

    if tile_w is None:
        tile_w = layer.tile_size.width
    else:
        assert tile_w == layer.tile_size.width

    if tile_h is None:
        tile_h = layer.tile_size.height
    else:
        assert tile_h == layer.tile_size.height

w = map_w * tile_w
h = map_h * tile_h

output = Image.new("RGBA", (w,h), (0,0,0,0))

print("Rendering layers")
for layer_idx, layer in enumerate(m.layers):
    print("\t{}".format(layer.layer_id))

    layer_img = Image.new("RGBA", (w,h), (0,0,0,0))
    for row,line in enumerate(layer.tiles):
        for col,tile in enumerate(line):
            if tile is None:
                continue

            if isinstance(tile, xtile.AnimatedTile):
                tile = tile.frames[0]

            tilesheet = tile.tilesheet
            tile = tilesheet.image.crop(tilesheet.getTileBounds(tile.index))

            left  = layer.tile_size.width  * col
            upper = layer.tile_size.height * row

            right = left  + layer.tile_size.width
            lower = upper + layer.tile_size.height

            layer_img.paste(tile, (left, upper, right, lower))

    output = Image.alpha_composite(output, layer_img)

output.save(sys.argv[3])
