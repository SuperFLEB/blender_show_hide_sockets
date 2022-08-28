from typing import Callable
import bpy
from . import operator

if "_LOADED" in locals():
    import importlib

    for mod in (operator,):  # list all imports here
        importlib.reload(mod)
_LOADED = True

package_name = __package__

bl_info = {
    "name": "Show/Hide Sockets",
    "description": "An addon to allow selectively showing or hiding sockets on a node",
    "author": "FLEB (a.k.a. SuperFLEB)",
    "version": (0, 1, 0),
    "blender": (3, 1, 0),
    "location": "View3D > Object",
    "warning": "", # used for warning icon and text in addons panel
    "doc_url": "https://github.com/SuperFLEB/blender_show_hide_sockets_addon",
    "tracker_url": "https://github.com/SuperFLEB/blender_show_hide_sockets_addon/issues",
    "support": "COMMUNITY",
    "category": "Node",
}


def menuitem(cls: bpy.types.Operator | bpy.types.Menu, operator_context: str = "EXEC_DEFAULT") -> Callable:
    if issubclass(cls, bpy.types.Operator):
        def operator_fn(self, context):
            self.layout.operator_context = operator_context
            self.layout.operator(cls.bl_idname)

        return operator_fn
    if issubclass(cls, bpy.types.Menu):
        def submenu_fn(self, context):
            self.layout.menu(cls.bl_idname)

        return submenu_fn
    raise Exception(f"Show/Hide Sockets: Unknown menu type for menu {cls}. The developer screwed up.")


# Registerable modules have a REGISTER_CLASSES list that lists all registerable classes in the module
registerable_modules = [
    operator,
]

classes = []

menus = [
    ["NODE_MT_context_menu", menuitem(operator.ShowHideSockets, "INVOKE_DEFAULT")],
]


def get_classes() -> list:
    # Uses a set to prevent doubles, and a list to preserve order
    all_classes = classes.copy()
    known_classes = set(classes)
    for module in [m for m in registerable_modules if hasattr(m, "REGISTER_CLASSES")]:
        for cls in [c for c in module.REGISTER_CLASSES if c not in known_classes]:
            all_classes.append(cls)
            known_classes.add(cls)
    return all_classes


def register() -> None:
    all_classes = get_classes()

    for c in all_classes:
        # Attempt to clean up if the addon broke during registration.
        try:
            bpy.utils.unregister_class(c)
        except RuntimeError:
            pass
        bpy.utils.register_class(c)
        print("Show/Hide Sockets registered class:", c)
    for m in menus:
        getattr(bpy.types, m[0]).append(m[1])


def unregister() -> None:
    all_classes = get_classes()
    for m in menus[::-1]:
        getattr(bpy.types, m[0]).remove(m[1])
    for c in all_classes[::-1]:
        try:
            bpy.utils.unregister_class(c)
        except RuntimeError:
            pass


if __name__ == "__main__":
    register()
