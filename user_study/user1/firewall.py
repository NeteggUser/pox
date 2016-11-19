from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as p

def _handle_PacketIn (event):
    	pkt = event.parsed
	cs_src = {}
	cs_port = {}
	lst = []
	if pkt.type != pkt.IP_TYPE:
		msg = of.ofp_packet_out()
		msg.data = event.ofp
		msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
		event.connection.send(msg)
		return
	if pkt.payload.protocol == pkt.payload.UDP_PROTOCOL:
		if event.port == 1:
			msg = of.ofp_packet_out()
                	msg.data = event.ofp
                	msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                	event.connection.send(msg)
           
		if event.port == 2:
                        return
	if pkt.payload.protocol == pkt.payload.TCP_PROTOCOL:
                tcpp = pkt.payload.payload
		if event.port == 1:
			cs_src[pkt.src] = pkt.dst
			cs_port[tcpp.srcport] = tcpp.dstport
			lst.append([pkt.src,pkt.dst,tcpp.srcport,tcpp.dstport])
                        msg = of.ofp_packet_out()
                        msg.data = event.ofp
                        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                        event.connection.send(msg)
                       
                if tcpp.dstport == 22:
                        return
		if [pkt.dst,pkt.src,tcpp.dstport,tcpp.srcport] in lst:
			msg = of.ofp_packet_out()
                        msg.data = event.ofp
                        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
                        event.connection.send(msg)
			return

    	return


def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
