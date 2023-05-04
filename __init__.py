bl_info = {
    "name": "Jack The Ripper",
    "author": "BlenderBoi",
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "description": "",
    "category": "Rigging Utilities",
}

import bpy
from . import Operators


modules = [
    Operators,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
