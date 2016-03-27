import sys
import xnb
import xtile

if len(sys.argv) != 2:
    print('Usage: {:s} <input_file>'.format(sys.argv[0]))
    sys.exit(1)

xnb_file = xnb.XNBFile(sys.argv[1])

assert isinstance(xnb_file.primaryObject, xtile.Map), "File does not contain XTile map object"

print("Map:")
print("\tID: '{:s}'".format(xnb_file.primaryObject.map_id))
print("\tDescription:  '{:s}'".format(xnb_file.primaryObject.description))
print("\tProperties:")
for k,v in xnb_file.primaryObject.properties.items():
    print("\t\t{} = {}".format(k, v))

print("Tilesheets:")
for tilesheet in xnb_file.primaryObject.tilesheets:
    print("\tID: '{:s}'".format(tilesheet.ts_id))
    print("\t\tDescription:  '{:s}'".format(tilesheet.description))
    print("\t\tImage source: '{:s}'".format(tilesheet.image_source))
    print("\t\tSheet size: {}".format(tilesheet.sheet_size))
    print("\t\tTile size:  {}".format(tilesheet.tile_size))
    print("\t\tMargin:     {}".format(tilesheet.margin))
    print("\t\tSpacing:    {}".format(tilesheet.spacing))
    print("\t\tProperties:")

    for k,v in tilesheet.properties.items():
        print("\t\t\t{} = {}".format(k, v))


print("Layers:")
for layer in xnb_file.primaryObject.layers:
    print("\tID: '{:s}'".format(layer.layer_id))
    print("\t\tVisible: {}".format(layer.visible))
    print("\t\tDescription: '{:s}'".format(layer.description))
    print("\t\tLayer size: {}".format(layer.size))
    print("\t\tTile size:  {}".format(layer.tile_size))

    for k,v in layer.properties.items():
        print("\t\t\t{} = {}".format(k, v))
