from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
NOTE: a "node" in the router topology is defined by the source (packet.src)         <-------------------
'''
class RIPRouter (Entity):
    def __init__(self):
        """
         Dict
           key = node
           value = Distance vector of that node
         NOTE: Distance Vector D is also a dict (key, val) = (node, cost)
        """
        self.table = {}

        # init self as a node with distance vector {}
        self.table[self] = {}

        """
        Contains the neighboring nodes that send the DiscoveryPacket
            key = node
            value = port # 
        """
        self.discovered_nodes = {}

    def get_distance_vector_of(self, node):
        """
        returns dv of a certain node
        """
        dv = self.table[node]
        return dv

    def get_neighbors(self):
        """
        Highly doubt anything is going to call this
        """
        n = self.discovered_nodes.keys()

    def get_cost_of_neighbor(self, neighbor):
        """
        This is bullshit, but exists so that we can generalize just in case
        """
        return 1

    def identify_packet(self, packet):
        """
        tells us what is the type of packet, so they could be handled independently
        """
        # identify packet
        is_discovery_packet = isinstance(packet, DiscoveryPacket)
        is_routing_update = isinstance(packet, RoutingUpdate)

        return is_discovery_packet, is_routing_update


    def handle_discovery_packet(self, packet, port):
        """
        Add (or remove, if not is_link_up) packet.src to discovered_nodes and update table accordingly 
        """
        link_up = packet.is_link_up
        if link_up:
            self.discovered_nodes[packet.src] = port
        else:
            self.discovered_nodes[packet.src] = None

        # TODO: Update table intelligently here

    def handle_routing_update_packet(self, packet):
        """
        Get routing table information from someone else, and update table accordingly
        """
        # the distance vector given by the update packet
        dv = packet.paths

        # TODO: Update table intelligently here

    def handle_rx (self, packet, port):

        is_discovery_packet, is_routing_update = identify_packet(packet=packet)

        if is_discovery_packet:
            self.handle_discovery_packet(packet=packet, port=port)
        elif is_routing_update:
            self.handle_routing_update_packet(packet=packet)
        else:
            # this is the normal case
            self.send(packet=packet, port=port, flood=False)





