from pox.core import core
import pox.openflow.libopenflow_01 as of


host_to_inport = {} 

def _handle_packetIn(event):
    inport = event.port # get the inport of the packet

    l2_packet = event.parsed # get the packet from the PacketIn event

    src = l2_packet.src # get the source MAC address of the packet
    dst = l2_packet.dst # get the dest MAC address of the packet

    host_to_inport[src] = inport

    if dst in host_to_inport:
        msg = of.ofp_packet_out(data = event.ofp)
        msg.actions.append(of.ofp_action_output(port = host_to_inport[dst]))
        event.connection.send(msg)

    else:
        msg = of.ofp_packet_out(data = event.ofp)
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        event.connection.send(msg)


def launch():
    core.openflow.addListenerByName("PacketIn", _handle_packetIn)

