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

                                
    def handle_rx(self, packet, port):
        is_discovery_packet, is_routing_update = self.identify_packet(packet=packet)
        withdrawn = None
        tableChanged = False
        if is_discovery_packet:
            self.handle_discovery_packet(packet=packet, port=port)
            # TODO: not sure yet...
        elif is_routing_update:
            # self.handle_routing_update_packet(packet=packet)
            source = packet.src
            for destination in packet.all_dests():
                if destination == self:
                    pass
                else:
                    if packet.get_distance(destination) >= 100:
                        if not self.table[source].has_key(destination):
                            self.table[source][destination] = 100
                        elif self.table[source][destination] != 100:
                        # if our best past is about to be withdrawn, broadcast the withdrawal
                            lowestHop = self.lowest_hop(destination)
                            if lowestHop == source:
                                withdrawn = destination
                        # withdraw the path that goes through source to get to the withdrawn destination
                            self.table[source][destination] = 100
                            tableChanged = True
                    else:
                        distances = self.table[source][source]
                        if self.tables[source][destination]:
                            givenValue = self.table[source][destination]
                            if distances + packet.get_distance(destination) < givenValue:
                                self.table[source][destination] = distances + packet.get_distance(destination)
                                tableChanged = True
                        else:
                            self.table[source][destination] = distances + packet.get_distance(destination)
                            tableChanged = True
        else:
            # normal case
            lowestHop = self.lowest_hop(packet.dst)
            if lowestHop != None:
                newport = self.ports[lowestHop]
                if newport != port:
                    self.send(packet=packet, port=port, flood=False)
            else:
                # drop the packet
                 pass

        if tableChanged:
            self.send_routing_update(withdrawn)


    def send_routing_update(self, withdrawn=None):
        # iterate through table to find minimum distances to all destinations
        destinations = {}
        for (hop, distances) in self.table.items():
            for (destination, distance) in distances.items():
                if destinations.has_key(dest):
                    if distance < destinations[destination]:
                        destinations[destination] = distance
                else:
                    destinations[destination] = distance

        # withdrawn != None, then we'll be sure to broadcast
        # a cost of infinity to withdrawn
        if withdrawn != None:
            destination[withdrawn] = 100

        # send out the packets with poison reverse
        for hop in self.table.keys():
            if self.ports.has_key(hop):
                copiedDestinations = destinations.copy()
                # this port is still connected
                for destination in destinations.keys():
                    if self.lowest_hop(destination) == hop:
                        # don't poison distance to immediate neighbor
                        if destination != hop:
                            destinations[destination] = 100
                # fill up routingUpdate packet with information
                packet = RoutingUpdate()
                for (destination, distance) in destinations.items():
                    packet.add_destination(destination, distance)
                self.send(packet, self.ports[hop])
            

    def lowest_hop(self, dest):
        # look up the route with the lowest hop count
        minValue = 100
        minPort = None
        minEntity = None
        for hop in self.table.keys():
            if self.table[hop].has_key(dest):
                givenValue = self.table[hop][dest]
                if givenValue < minValue:
                    minValue = givenValue
                    minPort = self.ports[hop]
                    minEntity = hop
            elif givenValue < 100 and givenValue == minValue:
                givenPort = self.ports[hop]
                if port < minPort:
                    minPort = port
                    minEntity = hop
        return minEntity
