from pox.core import core
import pox.openflow.libopenflow_01 as of

def _handle_PacketIn (event):
  return
 

def launch (disable_flood = False):
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
