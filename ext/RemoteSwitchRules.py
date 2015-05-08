"""
sudo mn --topo single,3 --mac --switch ovsk --controller remote
./pox.py log.level --DEBUG RemoteSwitchRules
sudo mn --custom ~/mininet/custom/topo-3sw-3host.py --topo mytopo --mac --switch ovsk --controller remote

"""


from pox.core import core
import pox
log = core.getLogger()

from pox.lib.packet.ethernet import ethernet, ETHER_ANY, ETHER_BROADCAST
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import str_to_bool, dpid_to_str, str_to_dpid
from pox.lib.recoco import Timer
import pox.lib.packet as pkt
import pox.openflow.spanning_tree
import pox.openflow.discovery
from pox.lib.packet.icmp import icmp

import pox.openflow.libopenflow_01 as of

from pox.lib.revent import *

import time

class MultiSwitch (EventMixin):
  def __init__ (self):

    # (dpid,IP) -> expire_time
    # We use this to keep from spamming ARPs
    self.outstanding_arps = {}

    # (dpid,IP) -> [(expire_time,buffer_id,in_port), ...]
    # These are buffers we've gotten at this datapath for this IP which
    # we can't deliver because we don't know where they go.
    self.lost_buffers = {}

    # For each switch, we map IP addresses to Entries
    self.arpTable = {}

    self.listenTo(core)
    
    #Same as above line
    #core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

    self.connections = set()

    #Timer(5,self.send_ping, recurring=True)

  def _handle_GoingUpEvent (self, event):
    core.openflow.miss_send_len = 512
    self.listenTo(core.openflow)
    log.debug("Controller Up...")

  def _handle_PacketIn (self, event):
    #print "Packet In from Switch %s" % event.dpid
    dpid = event.connection.dpid
    inport = event.port
    packet = event.parsed
    print event.ofp.reason
    print event.ofp.show

    if not packet.parsed:
      log.warning("%i %i ignoring unparsed packet", dpid, inport)
      return    
 
    if packet.type == ethernet.LLDP_TYPE or packet.type == ethernet.IPV6_TYPE:
      return     
    if isinstance(packet.next, icmp):
      print "ICMP"
    if isinstance(packet.next, ipv4):
      if packet.next.protocol == 1:
        print "ICMP Reply"
    #print inport

  def _handle_ConnectionUp (self, event):
    print "Switch %s has come up." % event.dpid
    log.debug("Controlling %s" % (event.connection,))

    msg = of.ofp_flow_mod()
    msg.priority = 10
    msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
    event.connection.send(msg)
    log.info("Disabling Flooding %s", dpid_to_str(event.dpid))

    self.connections.add(event.connection) 
    if len(self.connections) == 3:
      #for s in self.connections:
      #  print event.ofp
      #print event.ofp
      time.sleep(2)
      self.install_flow()

  def install_flow (self):
    #con = core.openflow.getConnection(3)
    # print con.ports.get(1) #s1-eth1
    #for no, port in con.ports.iteritems():
     # print no
      #print port
    #print con.ports
    #for con in core.openflow.connections:
    con = core.openflow.getConnection(1)
    msg = of.ofp_flow_mod()
    msg.match.dl_dst = EthAddr(core.openflow.getConnection(2).eth_addr)
    msg.actions.append(of.ofp_action_output(port=2))          
    msg.priority = 42
    msg.command = of.OFPFC_ADD
    msg.buffer_id = None
    msg.idle_timeout = of.OFP_FLOW_PERMANENT
    msg.hard_timeout = of.OFP_FLOW_PERMANENT
    msg.match.dl_type = 0x0800
    msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
    msg.out_port = of.OFPP_NONE
    con.send(msg)
  
    time.sleep(2)
  
    self.send_ping(eth_dst=EthAddr(core.openflow.getConnection(2).eth_addr))


  def send_ping (self, dpid=1, eth_dst = ETHER_ANY):
    con = core.openflow.getConnection(dpid)
    
    icmp = pkt.icmp()
    icmp.type = pkt.TYPE_ECHO_REQUEST
    echo=pkt.ICMP.echo(payload="SENDING PING")
    icmp.payload = echo

    #Make the IP packet around it
    ipp = pkt.ipv4()
    ipp.protocol = ipp.ICMP_PROTOCOL
    
    #Ethernet around that...
    e = pkt.ethernet()
    e.dst = eth_dst
    e.type = e.IP_TYPE

    
    #Hook them up...
    ipp.payload = icmp
    e.payload = ipp   
    
    '''
    msg = of.ofp_flow_mod()
    msg.match.dl_dst = EthAddr(core.openflow.getConnection(2).eth_addr)
    msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))          
    msg.priority = 125
    msg.command = of.OFPFC_ADD
    msg.buffer_id = None
    msg.idle_timeout = of.OFP_FLOW_PERMANENT
    msg.hard_timeout = of.OFP_FLOW_PERMANENT
    msg.match.dl_type = 0x0800
    msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
    msg.out_port = of.OFPP_NONE
    msg.data = e.pack()
    '''

    msg = of.ofp_packet_out()    
    msg.actions.append(of.ofp_action_output(port = of.OFPP_TABLE))
    msg.data = e.pack()
    con.send(msg)    
 
    #msg.actions.append(of.ofp_action_output(port = of.OFPP_TABLE))    
   

def launch ():    
  import pox.log.color
  pox.log.color.launch()
  pox.log.launch(format="[@@@bold@@@level%(name)-22s@@@reset] " + "@@@bold%(message)s@@@normal")
  core.registerNew(MultiSwitch)

