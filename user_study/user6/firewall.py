from pox.core import core
import pox.lib.packet as pkt
import pox.openflow.libopenflow_01 as of

allowed = []

def _handle_PacketIn (event):
    # put your code here
    inport = event.port
    l2_packet = event.parsed
    # not IP, send straight through 
    if l2_packet.type != l2_packet.IP_TYPE:
	print 'not IP'
    	msg = of.ofp_packet_out()
	msg.data = event.ofp
	msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        event.connection.send(msg)
    # is IP packet
    else: # if l2_packet.type == pkt.IP_TYPE
	# from CS
	ip_packet = l2_packet.payload
	if inport == 1:
	    print 'from CS'
	    # if TCP, check if host is in list, if so check if port is associated with it. If no, add port to mapping
	    if ip_packet.protocol == ip_packet.TCP_PROTOCOL:
		tcp_packet = ip_packet.payload
		srchost = ip_packet.srcip
		dsthost = ip_packet.dstip
		srcport = tcp_packet.srcport
		dstport = tcp_packet.dstport
		allowed.append([srchost, srcport, dsthost, dstport])
		
	        msg = of.ofp_packet_out()
	        msg.data = event.ofp
	        msg.actions.append(of.ofp_action_output(port = 2))
	        event.connection.send(msg)
	    elif ip_packet.protocol == ip_packet.UDP_PROTOCOL:
		msg = of.ofp_packet_out()
		msg.data = event.ofp
		msg.actions.append(of.ofp_action_output(port = 2))
		event.connection.send(msg)
	    else:
		print 'Neither TCP nor UDP'
		return
	elif inport == 2:
	    print 'from Internet'
	    # if UDP from internet, don't fwd the packet
	    if ip_packet.protocol == ip_packet.UDP_PROTOCOL:
		print 'UDP from internet'
		return
		#do nothing
	    # TCP from internet
	    elif ip_packet.protocol == ip_packet.TCP_PROTOCOL:
		print 'TCP from internet'
		tcp_packet = ip_packet.payload
		# SSH packet (dstport == 22) are dropped
		if tcp_packet.dstport == 22:
		    return
		    # do nothing
		else:
		    srchost = ip_packet.srcip
		    dsthost = ip_packet.dstip
		    srcport = tcp_packet.srcport
		    dstport = tcp_packet.dstport
		    if [dsthost,dstport,srchost,srcport] in allowed:
			msg = of.ofp_packet_out()
			msg.data = event.ofp
			msg.actions.append(of.ofp_action_output(port = 1))
			event.connection.send(msg)
		    
	    # any other protocol from internet, do nothing
	    else:
		return
		#do nothing
	else:
	    print 'Error: port number neither 1 nor 2'
	    return

	
    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
