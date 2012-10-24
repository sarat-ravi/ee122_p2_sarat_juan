from sim.api import *
from sim.basics import *

'''
Create your learning switch in this file.
'''
class LearningSwitch(Entity):
    def __init__(self):
        # dict of key = destination and value = port
        self.table = {}
        pass

    def _get_packet_info(self, packet):
        source  = packet.src
        destination = packet.dst
        ttl = packet.ttl
        trace = packet.trace
        return source, destination, ttl, trace

    def destination_is_known(self, destination):
        known = destination in self.table
        return known

    def get_destination_port_for(self, destination):
        return self.table[destination]

    def update_table(self, source, port):
        # Returns true if table has been updated 
        if source in self.table and self.table[source] == port:
            return False

        self.table[source] = port
        return True
    
    def flood_table(self, except_port):
        # code here to broadcast the change in table
        #discovery_packet = Packet()
        #self.send(packet=discovery_packet,
                #port=except_port,
                #flood=True)
        pass

    def send_packet(self, packet, destination):
        dest_port = self.get_destination_port_for(destination=destination) 
        self.send(packet=packet, port=dest_port, flood=False)

    def flood_packet(self, packet, except_port):
        self.send(packet=packet, port=except_port, flood=True)

    def handle_rx (self, packet, port):
        # Get required packet information
        source, destination, ttl, trace = self._get_packet_info(packet=packet)

        # learns everything possible from the arriving packet
        table_updated = self.update_table(source=source, port=port)

        if table_updated:
            # code here to broadcast the change in table
            self.flood_table(except_port=port)

        if self.destination_is_known(destination=destination):
            self.send_packet(packet=packet, destination=destination)
        else:
            self.flood_packet(packet=packet, except_port=port)

"""
class Entity(__builtin__.object)
    handle_rx(self, packet, port)
        Called by the framework when the Entity self receives a packet. packet - a Packet (or subclass).
        port - port number it arrived on.
        You definitely want to override this function.

    send(self, packet, port=None, flood=False)
        Sends the packet out of a specific port or ports. If the packet's src is None, it will be set automatically to the Entity self. packet - a Packet (or subclass).
        port - a numeric port number, or a list of port numbers.
        flood - If True, the meaning of port is reversed - packets will be sent from all ports EXCEPT those listed.
        Do not override this function.

    get_port_count(self)
        Returns the number of ports this Entity has.
        Do not override this function.

    set_debug(self, *args)
        Turns all arguments into a debug message for this Entity. args - Arguments for the debug message.
        Do not override this function.

class Packet(object)
    self.src
    The origin of the packet.

    self.dst
    The destination of the packet.

    self.ttl
    The time to live value of the packet.
    Automatically decremented for each Entity it goes.

    self.trace
    A list of every Entity that has handled the packet previously. This is
    here to help you debug.

"""











