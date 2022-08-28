from typing import Set
import bpy
import random
from bpy.props import StringProperty, IntProperty, FloatProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup, UIList

class SocketPropertyGroup(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="Socket Name",
    )
    hidden: BoolProperty()
    can_hide: BoolProperty()


class SocketUIList(UIList):
    """A list containing Node Sockets and checkboxes for visibility"""
    bl_label = "Sockets"
    bl_idname = "CUSTOM_UL_sockets"

    def draw_item(self, context, layout, data, item, iocon, active_data, active_propname, index) -> None:
        cxbox_layout = layout.column()
        cxbox_layout.enabled = item.can_hide
        cxbox_layout.prop(item, "hidden", text="", invert_checkbox=True)
        layout.label(text=str(item.name))


class ShowHideSockets(Operator):
    """An addon to allow selectively showing or hiding sockets on a node"""
    bl_idname = "blender_show_hide_sockets_addon.an_operator_with_uilist"
    bl_label = "Show/Hide Sockets"
    bl_options = {'REGISTER', 'UNDO'}

    sockets_in: CollectionProperty(type=SocketPropertyGroup)
    sockets_out: CollectionProperty(type=SocketPropertyGroup)

    active_socket_in: IntProperty()
    active_socket_out: IntProperty()

    @classmethod
    def poll(cls, context) -> bool:
        if len(context.selected_nodes) == 0:
            cls.poll_message_set("Select one (and only one) node")
            return False
        return True

    def draw(self, context) -> None:
        row = self.layout.row()
        row.template_list("CUSTOM_UL_sockets", "sockets_in", self, "sockets_in", self,
                                  "active_socket_in")
        row.template_list("CUSTOM_UL_sockets", "sockets_in", self, "sockets_out", self,
                                  "active_socket_out")

    def invoke(self, context, event) -> Set[str]:
        node = context.selected_nodes[0]

        self.sockets_in.clear()
        self.sockets_out.clear()

        for propcoll, attrname in [(self.sockets_in, "inputs"), (self.sockets_out, "outputs")]:
            for (name, socket) in getattr(node, attrname).items():
                ui_list_item = propcoll.add()
                ui_list_item.hidden = socket.hide
                ui_list_item.name = name
                ui_list_item.can_hide = not socket.is_linked

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context) -> Set[str]:
        node = context.selected_nodes[0]
        for propcoll, attrname in [(self.sockets_in, "inputs"), (self.sockets_out, "outputs")]:
            for item in [i for i in propcoll if i.can_hide]:
                socket = getattr(node, attrname)[item.name]
                socket.hide = item.hidden
        return {'FINISHED'}


REGISTER_CLASSES = [SocketPropertyGroup, SocketUIList, ShowHideSockets]
