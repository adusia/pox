"""
sudo mn --topo single,3 --mac --switch ovsk --controller remote
./pox.py log.level --DEBUG MultiSwitchWithDiagnosis
sudo mn --custom ~/mininet/custom/topo-3sw-3host.py --topo mytopo --mac --switch ovsk --controller remote

"""

"""
A stupid L3 switch

For each switch:
1) Keep a table that maps IP addresses to MAC addresses and switch ports.
   Stock this table using information from ARP and IP packets.
2) When you see an ARP query, try to answer it using information in the table
   from step 1.  If the info in the table is old, just flood the query.
3) Flood all other ARPs.
4) When you see an IP packet, if you know the destination port (because it's
   in the table from step 1), install a flow for it.
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

"""
class Entry (object):
  
  Not strictly an ARP entry.
  We use the port to determine which port to forward traffic out of.
  We use the MAC to answer ARP replies.
  We use the timeout so that if an entry is older than ARP_TIMEOUT, we
   flood the ARP request rather than try to answer it ourselves.
  
  def __init__ (self, port, mac):
    self.timeout = time.time() + ARP_TIMEOUT
    self.port = port
    self.mac = mac

  def __eq__ (self, other):
    if type(other) == tuple:
      return (self.port,self.mac)==other
    else:
      return (self.port,self.mac)==(other.port,other.mac)
  def __ne__ (self, other):
    return not self.__eq__(other)

  def isExpired (self):
    if self.port == of.OFPP_NONE: return False
    return time.time() > self.timeout


def dpid_to_mac (dpid):
  return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))
"""

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

    #self.previous_ping_returned = None

    self.ping_replies = {}

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
    print "Port %s on Switch %s has been %s. " % (event.port, event.dpid, action) 

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
        if dpid == 1:
          #log.info("ICMP Reply from switch 1")
          log.info("All links are up!!")
          #self.previous_ping_returned = True
          self.ping_replies[dpid] = True
        else: 
          #log.info("ICMP Reply from switch %s " % dpid)
          self.ping_replies[dpid] = True

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
      time.sleep(2)
      self.install_flow ()  

  def install_flow (self):    
    for con in core.openflow.connections:
      msg = of.ofp_flow_mod()

      if con.dpid == 1:
	#print "Ethernet Address %s " % con.eth_addr
        #msg.match.in_port = of.OFPP_CONTROLLER
        msg.actions.append(of.ofp_action_output(port=2))
      if con.dpid == 2:
        msg.match.in_port = 2
        msg.actions.append(of.ofp_action_output(port=3))
      if con.dpid == 3:
        msg.match.in_port = 2
        msg.actions.append(of.ofp_action_output(port=3))
          
      msg.priority = 42
      msg.command = of.OFPFC_ADD
      msg.buffer_id = None
      msg.idle_timeout = of.OFP_FLOW_PERMANENT
      msg.hard_timeout = of.OFP_FLOW_PERMANENT
      msg.match.dl_type = 0x0800
      msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
      msg.out_port = of.OFPP_NONE
      con.send(msg)
    
    con = core.openflow.getConnection(1)  
    msg = of.ofp_flow_mod()
    msg.buffer_id = None
    msg.priority = 100
    msg.command = of.OFPFC_ADD
    msg.idle_timeout = of.OFP_FLOW_PERMANENT
    msg.hard_timeout = of.OFP_FLOW_PERMANENT
    msg.match.dl_type = 0x0800
    msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
    msg.match.in_port = 3
    msg.out_port = of.OFPP_NONE
    msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))     
    con.send(msg)
    time.sleep(2)
    #self.send_ping ()
    #self.previous_ping_returned = True
    self.ping_replies[1] = True
    Timer(5,self.start_monitoring, recurring=True)

  def start_monitoring(self):
    if self.ping_replies[1] == True:
      self.ping_replies[1] = False
      self.send_ping()
    else:
      log.info("Link Failure: Starting Diagnosis")
      self.start_diagnosis()
      return False

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
  
  def start_diagnosis(self, rules='Install'):
    for con in core.openflow.connections:
      msg = of.ofp_flow_mod()

      if con.dpid == 1:
	#msg.match.dl_dst = EthAddr(con.eth_addr)
        #msg.actions.append(of.ofp_action_output(port=3))          
	continue
      if con.dpid == 2:
        msg.match.in_port = 2
	msg.match.dl_dst = EthAddr(con.eth_addr)
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))          
      if con.dpid == 3:
        msg.match.in_port = 2
	msg.match.dl_dst = EthAddr(con.eth_addr)
        msg.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER)) 

      msg.priority = 110
      msg.buffer_id = None
      msg.idle_timeout = of.OFP_FLOW_PERMANENT
      msg.hard_timeout = of.OFP_FLOW_PERMANENT
      msg.match.dl_type = 0x0800
      msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
      msg.out_port = of.OFPP_NONE      

      if rules == 'Install':
        log.info("installing rule in switch %s" % con.dpid)
        msg.command = of.OFPFC_ADD
      else:
        log.info("deleting rule in switch %s" % con.dpid)
        msg.command = of.OFPFC_DELETE
      
      con.send(msg)

    if rules == 'Install':
      self.ping_replies[1] = False
      self.ping_replies[2] = False
      self.ping_replies[3] = False
      self.send_ping()
      self.send_ping(eth_dst=EthAddr(core.openflow.getConnection(2).eth_addr))
      Timer(5, self.diagnosis_result, recurring=True)      

  def diagnosis_result(self):      
      self.send_ping()
      self.send_ping(eth_dst=EthAddr(core.openflow.getConnection(2).eth_addr))
      self.send_ping(eth_dst=EthAddr(core.openflow.getConnection(3).eth_addr))
      
      if(self.ping_replies[1] == True):    
        #self.previous_ping_returned = True  
	self.start_diagnosis(rules='Delete')
        Timer(5,self.start_monitoring, recurring=True)
        return False
      elif(self.ping_replies[2] and self.ping_replies[3]):
        log.info("Link between S1 and S3 has failed")
      elif(not (self.ping_replies[2]) and not (self.ping_replies[3])):
        log.info("Link between S1 and S2 has failed")
      elif(self.ping_replies[2] and not (self.ping_replies[3])):
        log.info("Link between S2 and S3 has failed")
      
      self.ping_replies[1] = False
      self.ping_replies[2] = False
      self.ping_replies[3] = False

def launch ():    
  import pox.log.color
  pox.log.color.launch()
  pox.log.launch(format="[@@@bold@@@level%(name)-22s@@@reset] " + "@@@bold%(message)s@@@normal")
  #pox.openflow.discovery.launch()
  #core.getLogger("openflow.spanning_tree").setLevel("INFO")
  core.registerNew(MultiSwitch)
  #pox.openflow.spanning_tree.launch()

