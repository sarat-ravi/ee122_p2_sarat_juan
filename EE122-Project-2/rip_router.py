from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
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
        Contains the nodes that send the DiscoveryPacket
            key = node
            value = port # 
        """
        self.discovered_nodes = {}

    def get_neighbors(self):
        n = self.discovered_nodes.keys()

    def get_cost_of_neighbor(self, neighbor):
        return 1

    def identify_packet(self, packet):
        # identify packet
        is_discovery_packet = isinstance(packet, DiscoveryPacket)
        is_routing_update = isinstance(packet, RoutingUpdate)

        return is_discovery_packet, is_routing_update


    def handle_discovery_packet(self, packet, port):
        """
        Add (or remove, if not is_link_up) packet info to discovered_nodes and update table accordingly 
        """
        link_up = packet.is_link_up
        if link_up:
            self.discovered_nodes[packet.src] = port
        else:
            self.discovered_nodes[packet.src] = None

    def handle_routing_update_packet(self, packet):
        """
        Get routing table information from someone else, and update table accordingly
        """

    def get_distance_vector_of(self, node):
        """
        returns dv of a certain node
        """
        dv = self.table[node]
        return dv

    def handle_rx (self, packet, port):

        is_discovery_packet, is_routing_update = identify_packet(packet=packet)

        if is_discovery_packet:
            self.handle_discovery_packet(packet=packet, port=port)
        elif is_routing_update:
            self.handle_routing_update_packet(packet=packet)
        else:
            # this is the normal case
            self.send(packet=packet, port=port, flood=False)





