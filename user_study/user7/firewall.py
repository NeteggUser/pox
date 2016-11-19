from pox.core import core
import pox.openflow.libopenflow_01 as of

savedAddresses = {}

def _handle_PacketIn (event):
    # put your code here
    l2_packet = event.parsed
    physicalReceivedPort = event.port
    payload = l2_packet.payload

    #print 'packet'
    #print dir(l2_packet)
    #print 'payload'
    #print dir(payload)
    
    isIp = True
    ipv4Check = l2_packet.find('ipv4')
    if ipv4Check is None:
	isIp = False

    #rule 0
    if not isIp:
	return
    
    srcip = l2_packet.srcip
    destip = l2_packet.dstip
    srcport = payload.srcport
    destport = payload.dstport
    isUDP = True
    isTCP = True
    
    udpCheck = l2_packet.find('udp')
    if udpCheck is None:
	isUDP = False
    
    tcpCheck = l2_packet.find('tcp')
    if tcpCheck is None:
	isTCP = False

    isARP = l2_packet.type == l2_packet.IP_TYPE

    protocolNumber = payload.protocol
    #rule 1
    if protocolNumber == 17 and physicalReceivedPort == 2:
	return

    #rule 2
    if protocolNumber == 17 and physicalReceivedPort == 1:
	msg = of.ofp_packet_out()
	msg.data = event.ofp
	msg.actions.append(of.ofp_action_output(port = destport))
	event.connection.send(msg)
	return

    #rule 3
    if protocolNumber == 6 and physicalReceivedPort == 1:     
    	#save address 
	key = srcip + srcport
	value = destip + destport
	found = False
	if savedAddresses[key] is None:
		savedAddresses[key] = [] 
	
	for add in savedAddresses[key]:
		if (add == value):
			found = True
	
	if found:
		msg = of.ofp_packet_out()
    		msg.data = event.ofp
    		msg.actions.append(of.ofp_action_output(port = destport))
    		event.connection.send(msg)
    	return

    #rule 4
    if protocolNumber == 6 and physicalReceivedPort == 2 and destport == 22:
	return

    #rule 5
    if protocolNumber == 6 and physicalReceivedPort == 2:
	key = destip + destport
	value = srcip + srcport
	found = False
	if savedAddresses[key] is None:
		return
	
	for add in savedAddresses[key]:
		if (add == value):
			found = True
	if found:
		msg = of.ofp_packet_out()
		msg.data = event.ofp
		msg.actions.append(of.ofp_action_output(port = destport))
		event.connection.send(msg)
	return

    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
