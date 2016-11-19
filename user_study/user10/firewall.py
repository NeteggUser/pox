from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from collections import namedtuple

INTERNET_PORT = 2
CS_PORT = 1
SSH_PORT = 22

TcpRouteStruct = namedtuple("TcpRouteStruct", "src_ip src_port dst_ip dst_port")

outgoing_tcp_route = []
port_map = {}
port_map[CS_PORT] = INTERNET_PORT
port_map[INTERNET_PORT] = CS_PORT

def _handle_PacketIn (event):
    # put your code here
    inport = event.port
    eth_packet = event.parsed
    # only look at IP traffic since all non-IP traffic
    # will not be dropped
    if eth_packet.type == eth_packet.IP_TYPE:
        ip_packet = eth_packet.payload
        # drop UDP traffic from the internet, keep UDP traffic from CS
        if ip_packet.protocol == pkt.UDP and inport == INTERNET_PORT:
            return
        # handle TCP traffic
        if ip_packet.protocol == 6: #TCP
            tcp_packet = ip_packet.payload
            # log outgoing TCP traffic from CS to Internet
            if inport == CS_PORT:
                #cs_host = ip_packet.srcip
                #cs_port = tcp_packet.srcport
                #internet_host = ip_packet.dstip
                #internet_port = tcp_packet.dstport
                route = TcpRouteStruct(ip_packet.srcip, tcp_packet.srcport,
                                       ip_packet.dstip, tcp_packet.dstport)
                # append to list of routes if not already in
                if route not in outgoing_tcp_route:
                    outgoing_tcp_route.append(route)
            # drop SSH packets from the internet
            elif tcp_packet.dstport == SSH_PORT:
                return
            else:
                route = TcpRouteStruct(ip_packet.dstip, tcp_packet.dstport,
                                       ip_packet.srcip, tcp_packet.srcport)
                # drop if the reverse route (from CS to Internet) has not been taken
                if route not in outgoing_tcp_route:
                    return

    # forward messages that have not been dropped (fn hasn't returned)
    msg = of.ofp_packet_out(data = event.ofp)
    msg.actions.append(of.ofp_action_output(port = port_map[inport]))
    event.connection.send(msg)
    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
