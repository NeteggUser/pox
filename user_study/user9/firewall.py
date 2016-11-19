from pox.core import core
import pox.openflow.libopenflow_01 as of

host_to_port = {}
def _handle_PacketIn (event):
    # put your code here
    # drop all UDP traffic
    inport = event.port # incoming port can either be 1 or 2
    if(inport == 1): # outgoing traffic, allow all
        if(not(isinstance(event.parsed.payload.payload,basestring)) and event.parsed.payload.protocol==event.parsed.payload.TCP_PROTOCOL):
            host_to_port[(event.parsed.payload.srcip,event.parsed.payload.payload.srcport)] = (event.parsed.payload.dstip,event.parsed.payload.payload.dstport)
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=2))
        event.connection.send(msg)
    else: # inport will be 2
        l2_packet = event.parsed
        l3_packet = l2_packet.payload
        print type(l3_packet)
        if(l3_packet.find('ipv4') is None):
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=1))
            event.connection.send(msg)
        else:
            l4_packet = l3_packet.payload
            print type(l4_packet)
            if(l3_packet.protocol==l3_packet.TCP_PROTOCOL):
                print type(l4_packet)
                if (l4_packet.dstport == 22):
                    return
                if (host_to_port[(l3_packet.dstip,l4_packet.dstport)]) == (l3_packet.srcip,l4_packet.srcport):
                     msg = of.ofp_packet_out()
                     msg.data = event.ofp
                     msg.actions.append(of.ofp_action_output(port=1))
                     event.connection.send(msg)
                else:
                    return
	    if not(l4_packet.find('tcp')):
                return

    # TCP allow if A,P --> B,Q before
    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
