from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt


host_to_port = {}
check = {}

def _handle_PacketIn (event):
    inport = event.port;
    l2_packet = event.parsed
    src = l2_packet.src
    dst = l2_packet.dst
       
    host_to_port[src] = inport
    
    if l2_packet.type != l2_packet.IP_TYPE:
	msg = of.ofp_packet_out(data = event.ofp)
	if dst in host_to_port:
        	msg.actions.append(of.ofp_action_output(port = host_to_port[dst]))
        	event.connection.send(msg)
		return
	else:
		msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                event.connection.send(msg)
		return
    
    if l2_packet.payload.protocol ==  l2_packet.payload.UDP_PROTOCOL:
	if inport == 2:
		return
	if inport == 1 :
		msg = of.ofp_packet_out(data = event.ofp)
        	if dst in host_to_port:
                	msg.actions.append(of.ofp_action_output(port = host_to_port[dst]))
                	event.connection.send(msg)
                	return
        	else:
                	msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                	event.connection.send(msg)
                	return

    if l2_packet.payload.protocol == l2_packet.payload.TCP_PROTOCOL:
        check[str(src)+str(l2_packet.payload.payload.srcport)] = str(dst)+str(l2_packet.payload.payload.dstport)
	if inport == 2 and l2_packet.payload.payload.dstport == 22 :
                return
        if inport == 1:
                msg = of.ofp_packet_out(data = event.ofp)
                if dst in host_to_port:
                        msg.actions.append(of.ofp_action_output(port = host_to_port[dst]))
                        event.connection.send(msg)
                        return
                else:
                        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                        event.connection.send(msg)
                        return
	if inport ==2 and check[str(dst)+ str(l2_packet.payload.payload.dstport)] == str(src)+str(l2_packet.payload.payload.srcport):
		msg = of.ofp_packet_out(data = event.ofp)
                if dst in host_to_port:
                        msg.actions.append(of.ofp_action_output(port = host_to_port[dst]))
                        event.connection.send(msg)
                        return
                else:
                        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                        event.connection.send(msg)
                        return

    

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
