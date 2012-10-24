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



    def get_min_cost_if_sent_to_neighbor_closest_to_dest(self, dest):
        min_cost = float("inf") 
        my_dv = self.table[self]
        for neighbor, port in self.discovered_nodes.items():
            neighbor_dv = self.table[neighbor]
            if not dest in neighbor_dv:
                # neighbor doesn't know how to get to dest, so theres no point
                continue

            cost_to_neighbor = my_dv[neighbor]
            cost_to_dest_from_neighbor = self.table[neighbor][dest]
            cost_to_dest = cost_to_neighbor + cost_to_dest_from_neighbor

            if cost_to_dest < min_cost:
                min_cost = cost_to_dest

        return min_cost


    def update_belief(self):
        table_changed = False

        my_dv = self.table[self]
        for node, distance in my_dv:
            if node == self:
                continue

            old_dist = self.table[self][node]
            new_min_dist = self.get_min_cost_if_sent_to_neighbor_closest_to_dest(dest=node)
            if not old_dist == new_min_dist:
                table_changed = True

            self.table[self][node] = self.get_min_cost_if_sent_to_neighbor_closest_to_dest(dest=node)

        return table_changed

    def add_dv_to_table(self, source, dv):
        """
        Handles dv insertion into table, returns True if table changed or false ow
        """
        if source in self.table and self.table[source] == dv:
            return False

        # table changed for sure, at this point
        self.table[source] = dv
        table_changed = self.update_belief()
        return table_changed

    def advertize_my_dv_to_neighbors(self):
        update_packet = RoutingUpdate()

        my_dv = self.table[self]
        for dest, distance in my_dv:
            update_packet.add_destination(dest=dest, distance=distance)

        for neighbor, port in self.discovered_nodes.items():
            if not port:
                # the link to this neighbor is down
                continue

            self.send(packet=update_packet, port=port, flood=False)

    def handle_discovery_packet(self, packet, port):
        """
        Add (or remove, if not is_link_up) packet.src to discovered_nodes and update table accordingly 
        """
        link_up = packet.is_link_up
        neighbor = packet.src
        if link_up:
            if not neighbor in self.discovered_nodes:
                # if neighbor is not already there
                # initialize a dv for our dear neighbor
                self.table[neighbor] = {}
            self.table[self][neighbor] = 1

            self.discovered_nodes[neighbor] = port
        else:
            self.discovered_nodes[neighbor] = None
            self.table[self][neighbor] = float("inf")

        table_changed = self.update_belief() 
        if table_changed:
            # call a function to advertize
            self.advertize_my_dv_to_neighbors()

    def handle_routing_update_packet(self, packet, port):
        """
        Get routing table information from someone else, and update table accordingly
        """
        # the distance vector given by the update packet
        dv = packet.paths
        table_changed = self.add_dv_to_table(source=packet.src, dv=dv)

        if table_changed:
            # call a function to advertize
            self.advertize_my_dv_to_neighbors()

    def lookup_exit_port_for(dest):
        """
        Studies our belief form the distance vectors of all our neighbors,
        and picks the best neighbor to pass packet to and returns the port of this neighbor
        """
        min_dist = float("inf")
        best_neighbor = None

        #if dest in self.discovered_nodes:
            ## if the neighbor is the destination itself
            ## and the link to this dest is up,
            ## return the port that goes to dest
            #best_neighbor = dest
            #exit_port = self.discovered_nodes[dest]
            #if exit_port:
                #return exit_port

        for node, dv in self.table.items():
            if node == self:
                continue
            if not dest in dv:
                # this node has no freakin clue how to get to dest
                continue

            dist = dv[dest]
            if dist < min_dist:
                min_dist = dist
                best_neighbor = node

        if not best_neighbor:
            # if best_neighbor not found, we are screwd.
            # this means that this is a dead end
            # luckily, this will be rare
            return None

        exit_port = self.discovered_nodes[best_neighbor]
        return exit_port


    def handle_rx (self, packet, port):

        is_discovery_packet, is_routing_update = identify_packet(packet=packet)

        if is_discovery_packet:
            self.handle_discovery_packet(packet=packet, port=port)
        elif is_routing_update:
            self.handle_routing_update_packet(packet=packet, port=port)
        else:
            # this is the normal case
            #self.send(packet=packet, port=port, flood=False)

            dest, ttl = packet.dst, packet.ttl

            if dest == self:
                # hand the packet over to the upper layer
                pass

            if ttl == 0:
                # packet dropped lol
                return

            exit_port = self.lookup_exit_port_for(dest=dest)
            self.send(packet=packet, port=exit_port, flood=False)



















