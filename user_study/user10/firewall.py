from pox.core import core
import pox.openflow.libopenflow_01 as of

def _handle_PacketIn (event):
    # put your code here
    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
