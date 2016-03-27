import parsley
import struct

def get(fmt, stream):
    return struct.unpack(fmt, stream.read(struct.calcsize(fmt)))

# some small helper functions
def read_7bei(stream):
    result = 0
    bitsRead = 0
    value = 0x80

    while value & 0x80:
        value = get("B", stream)[0]
        result |= (value & 0x7f) << bitsRead
        bitsRead += 7

    return result

def read_bool(stream):
    return get("B", stream)[0]>0

def read_u8(stream):
    return get("B", stream)[0]

def read_u32(stream):
    return get("<L", stream)[0]

def read_i32(stream):
    return get("<l", stream)[0]

def read_float(stream):
    return get("<f", stream)[0]

def read_string(stream):
    length = read_7bei(stream)
    return stream.read(length).decode('utf-8')

_type_readers            = {}
_registered_type_readers = []

def read_object(stream, t=None):
    if t and t.is_primitive:
        return t(stream)
    else:
        typeId = read_7bei(stream)
        if typeId == 0:
            return None
        else:
            typeId -= 1
            if typeId >= len(_type_readers):
                raise ValueError("Unknown type ID {:d}".format(typeId))

            return _registered_type_readers[typeId](stream)

def dictionary_reader(args):
    key_type, value_type = args
    def concrete(stream):
        n_items = read_u32(stream)
        result = {}
        for i in range(n_items):
            key         = read_object(stream, key_type)
            value       = read_object(stream, value_type)
            result[key] = value
        return result

    return concrete


def build_generic(base, n_args, args):
    assert len(args) == n_args
    return base(args)

def build_type(t, assembly_part=None):
    name = '.'.join(t)

    if name in _type_readers:
        return _type_readers[name]
    else:
        raise NotImplementedError("Unknown type '{:s}'".format(name))

class Attribute(object):
    def __init__(self, name, value):
        self.name  = name
        self.value = value

class Reader(object):
    def __init__(self, func, is_primitive):
        self.func = func
        self.is_primitive = is_primitive

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

def register_reader(name, reader, is_primitive=False):
    _type_readers[name] = Reader(reader, is_primitive)

class XNBFile(object):
    _typeNameGrammar = """
            type         = generic_type | simple_type
            generic_type = simple_type:base '`' number:n_args '[' ows type_list:args ows ']' -> build_generic(base, n_args, args)
            simple_type  = (namespaced_type_name:t (ows ',' ows assemblyPart:ap -> ap)?:ap -> build_type(t, ap))
            namespaced_type_name = (identifier:t '.' -> t)*:n identifier:i -> n + [i]
            assemblyPart = namespaced_type_name:assembly (ows ',' ows attribute:a -> a)*:attrs -> (assembly, attrs)
            type_list    = type_array:first (ows ',' ows type_array:a -> a)*:rest -> [first]+rest
            type_array   = '[' ows simple_type:t ows ']' -> t
            attribute    = identifier:name ows '=' ows value:value -> Attribute(name, value)
            value        = <(anything:c ?(not c in ',[]`'))*>
            identifier   = <ident_first ident_rest*>
            ident_first  = <anything:c ?(c == '_' or c.isalpha())>
            ident_rest   = <anything:c ?(c == '_' or c.isalnum())>
            number       = <digit+>:ds -> int(ds, 10)
            ows          = blank*
            blank        = anything:c ?(c.isspace())
        """

    _typeNameParser = parsley.makeGrammar(_typeNameGrammar, {'build_generic': build_generic, 'build_type': build_type, 'Attribute': Attribute})

    FLAG_PROFILE_HIDEF = 0x01
    FLAG_COMPRESSED    = 0x80

    def __init__(self, filename):
        stream = open(filename, 'rb')

        magic = stream.read(3)
        assert magic == b'XNB', "File does not start with 'XNB'."

        self.target_platform = stream.read(1)
        assert self.target_platform in b'wmx', "Invalid target platform '{:c}'".format(self.target_platform)

        self.version = read_u8(stream)
        assert self.version == 0x05, "Unsupported XNB version {:02x}".format(self.version)

        self.flags = read_u8(stream)
        assert not (self.flags & XNBFile.FLAG_COMPRESSED), "Compressed XNB files are currently unsupported"

        self.file_size = read_u32(stream)

        n_type_readers = read_7bei(stream)

        for i in range(n_type_readers):
            reader_name    = read_string(stream)
            reader_version = read_u32(stream)

            _registered_type_readers.append(self.resolveReader(reader_name, reader_version))

        sharedResCount = read_7bei(stream)

        self.primaryObject = read_object(stream)

        self.sharedObjects = []
        for i in range(sharedResCount):
            self.sharedObjects.append(read_object(stream))

    def resolveReader(self, name, version):
        return XNBFile._typeNameParser(name).type()


register_reader('System.Int32',                                     read_i32, True)
register_reader('System.String',                                    read_string)
register_reader('Microsoft.Xna.Framework.Content.StringReader',     read_string)
register_reader('Microsoft.Xna.Framework.Content.Int32Reader',      read_i32, True)
register_reader('Microsoft.Xna.Framework.Content.DictionaryReader', dictionary_reader)
