from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

dictionary = {}

def _handle_PacketIn (event):
    # put your code here
    inport = event.port
    outport = 1 if(event.port == 2) else 2
    packet = event.parsed
    msg = of.ofp_packet_out()
    if packet.type != pkt.ethernet.IP_TYPE:
        print("1")
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=outport))
        event.connection.send(msg)
    else:
        print("2")
        ip_packet = packet.payload
        if inport == 1:
            # Condition 1, 2 and 3
            # Allow to go
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=outport))
            event.connection.send(msg)
            if ip_packet.protocol == pkt.ipv4.TCP_PROTOCOL:
                # Store if TCP for reverse direction check
                inhost = ip_packet.srcip
                outhost = ip_packet.dstip
                if inhost not in dictionary:
                    dictionary[inhost] = {}
                if outhost not in dictionary:
                    dictionary[inhost][outhost] = []
                dictionary[inhost][outhost].append((ip_packet.payload.srcport, ip_packet.payload.dstport))
        elif ip_packet.protocol == pkt.ipv4.TCP_PROTOCOL and inport == 2 and ip_packet.payload.dstport != 22:
            # Allow if dst(CS) has already sent a packet to src(internet) using the same port combination 
            if (ip_packet.payload.dstport, ip_packet.payload.srcport) in dictionary[ip_packet.dstip][ip_packet.srcip]:
                msg.data = event.ofp
                msg.actions.append(of.ofp_action_output(port=outport))
                event.connection.send(msg)
    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
