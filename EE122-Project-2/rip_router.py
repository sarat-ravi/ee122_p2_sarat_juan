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
        self.saratdebug = False

        # init self as a node with distance vector {}
        self.table[self] = {}

        """
        Contains the neighboring nodes that send the DiscoveryPacket
            key = node
            value = port # 
        """
        self.discovered_nodes = {}

        """
        Maps the destination to the best neighbor to pass the packet to 
            key = destination node
            value = neighbor node # 
        """
        self.routing_table = {}

        """
        maps a deleted node to its believed distance vector
            key = deleted node
            value = distance vector of that node
        """
        self.deleted_nodes = {}

    def mylog(self, message, caller="(rip_router)"):
        if self.saratdebug:
            print "%s: %s" %(str(caller), str(message))

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
        self.mylog("get_min_cost called with destination %s" %(str(dest)))
        min_cost = 100 
        my_dv = self.table[self]
        for neighbor, port in self.discovered_nodes.items():
            if neighbor == dest:
                self.mylog("\tThe neighbor is the dest")
                #return self.table[self][neighbor]
                return 1 

            neighbor_dv = self.table[neighbor]
            if not dest in neighbor_dv:
                # neighbor doesn't know how to get to dest, so theres no point
                self.mylog("Neighbor %s doesn't know how to get to dest %s" %(str(neighbor), str(dest)))
                continue

            cost_to_neighbor = 1 
            cost_to_dest_from_neighbor = self.table[neighbor][dest]
            cost_to_dest = cost_to_neighbor + cost_to_dest_from_neighbor

            if cost_to_dest < min_cost:
                min_cost = cost_to_dest
                self.mylog("Added %s : (%s, %s) to routing table" %(str(dest), str(neighbor), str(port)))
                self.routing_table[dest] = (neighbor, port)

        return min_cost


    def update_belief(self):
        table_changed = False

        self.mylog("update belief called")
        my_dv = self.table[self]
        for node, distance in my_dv.items():
            if node == self:
                continue

            old_dist = distance 
            new_min_dist = self.get_min_cost_if_sent_to_neighbor_closest_to_dest(dest=node)
            self.mylog("Old dist is %s and new_min_dist = %s" %(str(old_dist), str(new_min_dist)))
            if not old_dist == new_min_dist:
                self.mylog("\tDist changed from %s to %s for neighbor %s" %(str(old_dist), str(new_min_dist), str(node)))
                table_changed = True

            self.table[self][node] = new_min_dist 

        return table_changed

    def handle_new_destinations_and_withdrawals(self, source, new_dv):
        # handle new destinations
        for possible_destination, distance in new_dv.items():
            # add this new reachable destination to my dv
            if not possible_destination in self.table[self]:
                self.table[self][possible_destination] = distance

        # handle withdrawal
        for old_neighbors_believed_destination, distance in self.table[source].items():
            if not old_neighbors_believed_destination in new_dv:
                # this means this destination has been withdrawn by source node
                # so we must make it unreachable by making its cost 100
                # or by popping. Dont know yet
                self.table[source][old_neighbors_believed_destination] = 100
                #self.table[self][old_neighbors_believed_destination] = 100
                #self.table[source].pop(old_neighbors_believed_destination)

    def add_dv_to_table(self, source, dv):
        """
        Handles dv insertion into table, returns True if table changed or false ow
        """
        if source in self.table and self.table[source] == dv:
            self.mylog("the old dv %s and new dv %s are the same for %s" %(str(self.table[source]), str(dv), str(source)))
            return False
        
        self.mylog("adding dv '%s' to source '%s'" %(str(dv), str(source)))
        # table changed for sure, at this point
        self.table[source] = dv
        self.handle_new_destinations_and_withdrawals(source=source, new_dv=dv)
        table_changed = self.update_belief()
        return table_changed

    def get_poisoned_dv_for_neighbor(self, neighbor):
        my_dv = self.table[self]
        #poisoned_dv = self.table[self].copy()
        poisoned_dv = {}
        neighbor_dv = self.table[neighbor]

        # if neighbor already has a better idea to get to a certain destination, poison!
        for destination, distance in my_dv.items():
            if destination == neighbor:
                # Must not EVER advertize my own believed distance to my neighbor
                continue
            else:
                poisoned_dv[destination] = distance

            if not destination in neighbor_dv:
                # Can't poison, because neighbor doesn't even know how to get to this destination.
                # I must tell my neighbor
                poisoned_dv[destination] = distance
                continue

            cost_for_neighbor_to_destination = neighbor_dv[destination]
            cost_for_me_to_destination = my_dv[destination]

            if cost_for_neighbor_to_destination < cost_for_me_to_destination:
                # dont even bother telling. Pretend I can't get to destination
                self.mylog("Poisoned neighbor '%s' for destination '%s'" %(str(neighbor), str(destination)))
                poisoned_dv[destination] = 100

        return poisoned_dv

    def advertize_my_dv_to_neighbors(self):
        self.mylog("called advertize")

        for neighbor, port in self.discovered_nodes.items():
            if neighbor == self:
                continue
            if port == None:
                # the link to this neighbor is down
                self.mylog("Port for neighbor %s is %s" %(str(neighbor), str(port)))
                continue
            
            poisoned_dv = self.get_poisoned_dv_for_neighbor(neighbor=neighbor)

            update_packet = RoutingUpdate()
            update_packet.paths = poisoned_dv

            self.mylog("Advertizing to neighbor: %s" %(str(neighbor)))
            self.mylog("Before Poisoned: Advertizement: " + str(self.table[self]))
            self.mylog("Advertizement: " + str(update_packet.paths))
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
                if neighbor in self.deleted_nodes:
                    self.mylog("Old neighbor '%s' is back online" %(str(neighbor)))
                    self.table[neighbor] = self.deleted_nodes[neighbor]
                    self.deleted_nodes.pop(neighbor)
                else:
                    self.mylog("New neighbor '%s' discovered" %(str(neighbor)))
                    self.table[neighbor] = {}
            self.table[self][neighbor] = 1

            self.discovered_nodes[neighbor] = port
        else:
            #self.discovered_nodes[neighbor] = None
            #self.table[self][neighbor] = 100 

            # remove neighbor from existance:
            if not neighbor in self.discovered_nodes:
                # haha we don't have to do anything
                return
            #self.deleted_nodes[neighbor] = self.table[neighbor].copy()

            self.discovered_nodes.pop(neighbor)
            self.table[self].pop(neighbor)
            self.table.pop(neighbor)
            self.mylog("Link to Neighbor '%s' is down" %(str(neighbor)))

        table_changed = False
        table_changed = self.update_belief() 
        if table_changed:
            # call a function to advertize
            self.advertize_my_dv_to_neighbors()

    def handle_routing_update_packet(self, packet, port):
        """
        Get routing table information from someone else, and update table accordingly
        """
        # the distance vector given by the update packet
        self.mylog("received update packet: %s" %(str(packet)))
        dv = packet.paths
    
        source = packet.src
        if source in self.deleted_nodes:
            # if this link is down, ignore
            self.mylog("Dropping update packet from '%s'" %(str(source)))
            return

        table_changed = self.add_dv_to_table(source=packet.src, dv=dv)

        if table_changed:
            # call a function to advertize
            self.advertize_my_dv_to_neighbors()

    def lookup_exit_port_for(self, dest):
        """
        Studies our belief form the distance vectors of all our neighbors,
        and picks the best neighbor to pass packet to and returns the port of this neighbor
        """
        #min_dist = float("inf")
        #best_neighbor = None

        ##if dest in self.discovered_nodes:
            ### if the neighbor is the destination itself
            ### and the link to this dest is up,
            ### return the port that goes to dest
            ##best_neighbor = dest
            ##exit_port = self.discovered_nodes[dest]
            ##if exit_port:
                ##return exit_port

        #for node, dv in self.table.items():
            #if node == self:
                #continue
            #if not dest in dv:
                ## this node has no freakin clue how to get to dest
                #continue

            #dist = dv[dest]
            #if dist < min_dist:
                #min_dist = dist
                #best_neighbor = node

        #if not best_neighbor:
            ## if best_neighbor not found, we are screwd.
            ## this means that this is a dead end
            ## luckily, this will be rare
            #return None

        #exit_port = self.discovered_nodes[best_neighbor]
        #return exit_port

        if not dest in self.routing_table:
            return None, None
        best_neighbor, exit_port = self.routing_table[dest]
        return best_neighbor, exit_port

    def handle_rx (self, packet, port):

        self.mylog("----------------------------------------------------------------")
        self.mylog("I am %s" %(str(self)))

        is_discovery_packet, is_routing_update = self.identify_packet(packet=packet)
        dest, ttl = packet.dst, packet.ttl
        self.mylog("Packet Arrived: %s, trying to go to %s" %(str(packet), str(dest)))

        if is_discovery_packet:
            self.handle_discovery_packet(packet=packet, port=port)
        elif is_routing_update:
            self.handle_routing_update_packet(packet=packet, port=port)
        else:
            # this is the normal case
            #self.send(packet=packet, port=port, flood=False)


            if dest == self or dest == None:
                # hand the packet over to the upper layer
                self.mylog("Packet sent for processing")
                self.send(packet=packet)

            if ttl == 0:
                # packet dropped lol
                self.mylog("Packet dropped because ttl is 0")
                return

            best_neighbor, exit_port = self.lookup_exit_port_for(dest=dest)
            if not exit_port:
                # packet dropped lol
                return

            self.mylog("Sending packet to %s" %(str(dest)))
            self.send(packet=packet, port=exit_port, flood=False)



















