from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt

host_to_port = {}

def _handle_PacketIn (event):
    flag = 0
    inport = event.port
    l2 = event.parsed
    typ = l2.type
    if typ != pkt.ethernet.IP_TYPE:
        flag =1
    else:
        P = l2.payload
        src = P.payload.srcport
        dst = P.payload.dstport
        host_to_port[src] = dst
        ip = l2.find('tcp')
        if ip:#tcp
                if inport ==2:#from Internet
                    if P.payload.dstport == 22:#SSH
                        flag =0
                    else:#not SSH
                        if dst in host_to_port:
                            if src == host_to_port[dst] :
                                flag = 1
                            else:
                                flag = 0
                        else:
                            flag = 0
                else:# from CS
                    flag =1
        else:#udp
                if inport ==2:
                        flag =0
                if inport == 1:
                        flag =1

    if flag ==0:
        return
    msg = of.ofp_packet_out()
    msg.data = event.ofp
    if inport ==1:
        msg.actions.append(of.ofp_action_output(port = 2))
    else:
        msg.actions.append(of.ofp_action_output(port = 1))
    event.connection.send(msg)
    return

def launch():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)