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

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import sys

# Server: Listens for incoming settings on settings_port - spawns appropriate test instance
# Client: Sends settings to Server and spawns appropriate test instance
# test_instance
# test_instance_data
# test_instance_data_send
# test_instance_data_recv
# test_instance_control


class Server(DatagramProtocol):
    """
    Listens for test settings on specified port and launches test instances
    based on received settings.
    Server may run indefinately, launching multiple test instances
    """

    def datagramReceived(self, data, (host, port)):

        try:
            settings = json.loads(data)
        except Exception:
            print("Received invalid settings message.")
            return

        if not settings.has_key('test_id'):
            print("Incomplete settings received, missing key 'test_id'")
            return

        settings_ack = settings['test_id']+"_ack"
        self.transport.write(settings_ack, (host, port))

        settings['client_ip'] = host
        settings['role'] = 'server'

        if settings['direction'] == 'server_to_client':
            instance = TestInstanceSend()
            ## start sending!!
        elif settings['direction'] == 'client_to_server':
            instance = TestInstanceRecv()
            pass
        else:
            print("Invalid direction specified in received settings: {}".format(
                  settings['direction']))
            return

        reactor.listenUDP(settings['port'], instance)

        # Wait for instance to finish
        # this should probably not be done here
        # ready for new test after this


class Client(DatagramProtocol):
    """
    Sends settings to specified server and launches appropriate test instance
    after the settings packet has been acknowledged.
    Client only launches on test instance, then closes.
    """

    def __init__(self, server_addr, settings):
        self.server_addr = server_addr
        self.settings = settings
        self.settings['test_id'] = uuid.uuid4().get_hex()

        # set more settings variables

        # Maybe this should be done once the protocol running (socket open)
        settings_string = json.dumps(self.settings)
        self.transport.write(settings_string, self.server_addr)

    def datagramReceived(self, data, addr):
        if not addr == self.server_addr:
            print("Client received datagram not from server ({})".format(addr))
            return
        if not data == settings['test_id']+"_ack":
            print("Client could not process ack: {}".format(data))
            return

        # ack received successfully
        if settings['direction'] == 'client_to_server':
            instance = TestInstanceSend()
            ## Start sending!
        elif settings['direction'] == 'server_to_client':
            instance = TestInstanceRecv()
        else:
            print("Could not interpret setting 'direction': {}".format(
                  settings['direction']))
            sys.exit()

        reactor.listenUDP(settings['port'], instance)

        # Wait for instance to finish
        # This should probably not be done here
        # We should be done here, close connection

class TestInstanceSend(DatagramProtocol):

    def __init__(self):
        # Setup variables related to test instance

        # begin sending
        pass

    def datagramReceived(self, data, (host, port)):
        # Check contents and sender of received datagram
        # if OK, stop sender

    def sendData(self, (host, port)):
        # Send data in loop if not finished, otherwise stop and clean up.
        pass

class TestInstanceRecv(DatagramProtocol):

    def __init__(self):
        # Setup variable related to test instance
        pass

    def datagramReceived(self, data, (host, port)):
        # Receive data and process (decode)
        # if complete, send nack packet
        pass

    def sendNack(self, (host, port)):
        # Construct and send nack packet
        pass


if __name__ == '__main__':
    server_port = 44444
    host = "127.0.0.1"
    addr = (host, server_port)
    settings = {}

    client = Client(addr, settings)
    reactor.listenUDP(0, client) # Any port

    server = Server()
    reactor.listenUDP(server_port, server)

    reactor.run()