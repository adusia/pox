"""
This example will probe selected switches based on pre-planned probing algorithm
./pox.py log.level --DEBUG MultiSwitchPreplannedProbing
sudo mn --custom ~/mininet/custom/topo-6sw.py --topo mytopo --mac --switch ovsk --controller remote

"""

from pox.core import core
import pox
log = core.getLogger()

from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST, ETHER_ANY
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

from Preplanned_Probing import Preplanned_Probing 

class MultiSwitch (EventMixin):
  def __init__ (self):

    self.listenTo(core)
    
    #Same as above line
    #core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)

    self.connections = set()

    #Timer(5,self.send_ping, recurring=True)

    self.ping_replies = {}

    self.probing_nodes = set()
 
    #[node][adjacent node list] -> [4][1,3,5,6]
    self.probing_nodes_adj = {}

  def _handle_GoingUpEvent (self, event):
    core.openflow.miss_send_len = 512
    self.listenTo(core.openflow)
    log.debug("Controller Up...")

  def _handle_PortStatus (self, event):
    if event.added:
      action = "added"
    if event.deleted:
      action = "removed"
    else:
      action = "modified"
    #print "Port %s on Switch %s has been %s. " % (event.port, event.dpid, action) 

  def _handle_PacketIn (self, event):
    #print "Packet In from Switch %s" % event.dpid
    dpid = event.connection.dpid
    inport = event.port
    packet = event.parsed
    #print event.ofp.reason
    #print event.ofp.show

    if not packet.parsed:
      log.warning("%i %i ignoring unparsed packet", dpid, inport)
      return    
 
    if packet.type == ethernet.LLDP_TYPE or packet.type == ethernet.IPV6_TYPE:
      return     

    if isinstance(packet.next, ipv4):
      if packet.next.protocol == 1:
	probe_node = int(str(packet.dst).split(":")[5])
	if probe_node in self.ping_replies:
	  self.ping_replies[probe_node].remove(dpid)

  def _handle_ConnectionUp (self, event):
    #print "Switch %s has come up." % event.dpid
    log.debug("Controlling %s" % (event.connection,))
    
    msg = of.ofp_flow_mod()
    msg.priority = 10
    msg.actions.append(of.ofp_action_output(port = of.OFPP_NONE))
    event.connection.send(msg)
    log.info("Disabling Flooding %s", dpid_to_str(event.dpid))

    self.connections.add(event.connection) 
    if len(self.connections) == 6:      
      time.sleep(2)
      self.select_probing_nodes()
      self.install_flow ()

  def install_flow (self):    
    for con in core.openflow.connections:
      msg = of.ofp_flow_mod()

      if con.dpid == 1:
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
      if con.dpid == 2:	
	msg.match.dl_dst = con.eth_addr
        msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
      if con.dpid == 3:
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
      if con.dpid == 4:
	msg.match.dl_dst = con.eth_addr
        msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
      if con.dpid == 5:
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
      if con.dpid == 6:
	msg.match.dl_dst = con.eth_addr
        msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
          
      msg.priority = 100
      msg.command = of.OFPFC_ADD
      msg.buffer_id = None
      msg.idle_timeout = of.OFP_FLOW_PERMANENT
      msg.hard_timeout = of.OFP_FLOW_PERMANENT
      msg.match.dl_type = 0x0800
      msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
      msg.out_port = of.OFPP_NONE
      con.send(msg)

    for con in core.openflow.connections:
      msg = of.ofp_flow_mod()

      if con.dpid == 2:	
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
      if con.dpid == 4:
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
      if con.dpid == 6:
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
          
      msg.priority = 80
      msg.command = of.OFPFC_ADD
      msg.buffer_id = None
      msg.idle_timeout = of.OFP_FLOW_PERMANENT
      msg.hard_timeout = of.OFP_FLOW_PERMANENT
      msg.match.dl_type = 0x0800
      msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
      msg.out_port = of.OFPP_NONE
      con.send(msg)

    Timer(4,self.start_monitoring, recurring=True)
    #time.sleep(2)
    #self.send_ping(dpid=4, eth_dst=EthAddr(core.openflow.getConnection(4).eth_addr))
    

  def start_monitoring(self):
    #print self.ping_replies
    no_errors = True
    for probing_node, adj_nodes in self.ping_replies.iteritems():
      if adj_nodes:
	for node in adj_nodes:
          log.info("Link between switches %s and %s is down" % (probing_node, node))
        no_errors = False

    if no_errors:
      log.info("All links are up!")

    for probing_node in self.probing_nodes_adj.iterkeys():
      #print "probing_node %s" % probing_node
      self.ping_replies[probing_node] = self.probing_nodes_adj[probing_node][:]
  

    #self.ping_replies = self.probing_nodes_adj.copy()
    #print self.ping_replies
    for node in self.probing_nodes:   
      self.send_ping(dpid=node,eth_dst=EthAddr(core.openflow.getConnection(node).eth_addr))

  def send_ping (self, dpid=1, eth_dst = ETHER_ANY):
      con = core.openflow.getConnection(dpid)
      icmp = pkt.icmp()
      icmp.type = pkt.TYPE_ECHO_REQUEST
      echo=pkt.ICMP.echo(payload="SENDING PING")
      icmp.payload = echo

      #Make the IP packet around it
      ipp = pkt.ipv4()
      ipp.protocol = ipp.ICMP_PROTOCOL

      # Ethernet around that...
      e = pkt.ethernet()
      e.dst = eth_dst
      e.type = e.IP_TYPE

      # Hook them up...
      ipp.payload = icmp
      e.payload = ipp   
    
      msg = of.ofp_packet_out()    
      msg.actions.append(of.ofp_action_output(port = of.OFPP_TABLE))
      msg.data = e.pack()
      con.send(msg)
      #self.previous_ping_returned = False

      #log.info("Sending ping to switch %s" % dpid) 
  

  def select_probing_nodes (self):

    Topo = []

    for x in range(0,6):
      Topo.append([])

    Topo[0].extend([0,1,0,1,0,1])
    Topo[1].extend([1,0,1,0,0,0])
    Topo[2].extend([0,1,0,1,0,0])
    Topo[3].extend([1,0,1,0,1,1])
    Topo[4].extend([0,0,0,1,0,1])
    Topo[5].extend([1,0,0,1,1,0])

    pp = Preplanned_Probing(Topo)
    self.probing_nodes = pp.select_nodes()
    
    for node in self.probing_nodes:
      self.probing_nodes_adj[node] = []
      for index in range(0,len(Topo[int(node)-1])):
	if Topo[int(node)-1][index] == 1:
            self.probing_nodes_adj[node].append(index+1)
    #print self.probing_nodes_adj[2]
    #self.ping_replies = self.probing_nodes_adj.copy()  

def launch ():    
  import pox.log.color
  pox.log.color.launch()
  pox.log.launch(format="[@@@bold@@@level%(name)-22s@@@reset] " + "@@@bold%(message)s@@@normal")
  #pox.openflow.discovery.launch()
  #core.getLogger("openflow.spanning_tree").setLevel("INFO")
  core.registerNew(MultiSwitch)
  #pox.openflow.spanning_tree.launch()

