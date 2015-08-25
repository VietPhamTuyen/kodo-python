#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import socket
import time
import sys
import json
import uuid

import kodo

"""
Functionality for communicating over udp using kodo to ensure reliability.

Both the server and the client can send and receive data

The client can send settings to the server, such that relevant test parameters
can be specified on the client side.

The sender side will send symols until it receives a stop signal on its control
port or it has sent all redundant symbols as specified.

All settings are contained in the 'settings' dictionary which should define the
following keys-values:

settings_port = (int) settings port on the server
server_ip = (string) ip of the server
client_control_port = (int) control port on the client side, used for signaling
server_control_port = (int) control port on the server side, used for signaling
data_port = (int) port used for data transmission
direction = (string) direction of data transmission
symbols = (int) number of symbols in each generation/block
symbol_size = (int) size of each symbol, in bytes
max_redundancy = (float percent) maximum amount of redundancy to be sent
timeout = (float seconds) timeout used for retransmitting various control messages

Both server and client return the 'settings' dictionary with added entries 
describing the process:

    test_id         = (int) 128bit unique test identifier
    client_ip       = (string) ip of the connected client (server only)
    status          = (string) describing if process succeeded or why it failed
    packets_total   = (int) total amount of packets transferred or received 
                      (depending on direction)
    packets_decode  = (int) amount of packets sent / received at decode time.
                      sender may have sent more packets before receiving the ack
    time_start      = (float) timestamp for when the first packet is sent 
    time_decode     = (float) timestamp for when the decode happens (or when 
                      ack is received for sender)
    time_stop       = (float) timestamp for when the last packet is sent or received

"""

from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.internet import reactor

class UnicastNode(DatagramProtocol):

    def startProtocol(self):
        """ Protocol startup phase: join multicast group, set TTL etc """
        pass

    def datagramReceived(self, data, (host, port)):
        print("Received {} bytes from {}:{}".format(len(data), host, port))
        # recv_datagram_callback(data, (host, port))

    def send(self, data, (host, port)):
        self.transport.write(data, (host, port))

class UnicastClient(Factory):

    def __init__(self, settings):
        self.settings = settings

    def buildProtocol(self, addr):
        print("Building UnicastNode with addr {}".format(addr))
        return UnicastNode()

if __name__ == '__main__':
    local_port = 44444
    settings = {}

    client = UnicastClient(settings)

    reactor.listenUDP(local_port, client)
    reactor.listenUDP(local_port+1, client)
    reactor.run()