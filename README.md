# pyxnb -- Python library for the XNA Content Pipeline's XNB file format

This repository contains some Python code to deal with the XNB file format, which is used by XNA in its Content Pipeline system. In addition, there is code to parse the tIDE binary map file format that can occur within these files.

XNB files can contain arbitrary objects, provided the software reading them has a 'type reader' object that can read those objects from the file. Files can be compressed (currently not supported in this code base, but hopefully coming soon)
