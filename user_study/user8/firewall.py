from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
host_to_port={}
def _handle_PacketIn (event):
    # put your code here
	
	inport = event.port
	l2_packet = event.parsed
	dst = l2_packet.dst
	src = l2_packet.src
	host_to_port[src] = inport
	if l2_packet.type != l2_packet.IP_TYPE:
		send(dst,event)
	else:
		if( inport == 2 and l2_packet.find(pkt.udp)):
			send(dst,event)
		if( inport == 1 and l2_packet.find(pkt.udp)):	
			send(dst,event)
		if (inport == 2 and l2_packet.find(pkt.tcp)):
			send(dst,event)
		if (inport == 2 and l2_packet.find(pkt.tcp) and l2_packet.dstport ==22):
			send(dst,event)
		if( inport == 1 and l2_packet.find(pkt.tcp)):
			if dst in host_to_port:
				send(dst,event)
		

	return

def send(dst,event):
			if(dst in host_to_port):
				outport = host_to_port[dst]
			else:
				outport = of.OFPP_FLOOD

			msg = of.ofp_packet_out()
			msg.data = event.ofp
			msg.actions.append(of.ofp_action_output(port = outport))
			event.connection.send(msg)



def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
