#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

from __future__ import print_function
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet import reactor

import sys
import kodo
import uuid
import time
import json
import os

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

    def __init__(self, report_results=print):
        self.report_results = report_results
        print("Built Server!")


    def datagramReceived(self, data, (host, port)):

        print("Server receiving {} from {}!".format(data, (host, port)))

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

        local_port = 0
        if settings['direction'] == 'server_to_client':
            local_port = settings['port_tx']
            instance = TestInstanceSend((host, settings['port_rx']), settings)
            ## start sending!!
        elif settings['direction'] == 'client_to_server':
            local_port = settings['port_rx']
            instance = TestInstanceRecv((host, settings['port_tx']), settings)
        else:
            print("Invalid direction specified in received settings: {}".format(
                  settings['direction']))
            return

        reactor.listenUDP(local_port, instance)
        instance.results.addCallback(self.report_results)

        # Wait for instance to finish
        # this should probably not be done here
        # ready for new test after this


class Client(DatagramProtocol):
    """
    Sends settings to specified server and launches appropriate test instance
    after the settings packet has been acknowledged.
    Client only launches on test instance, then closes.
    """

    def __init__(self, server_addr, settings, report_results=print):
        self.server_addr = server_addr
        self.settings = settings
        self.settings['test_id'] = uuid.uuid4().get_hex()
        self.report_results = report_results
        print("Built Client!")

        # set more settings variables

    def startProtocol(self):
        # Maybe this should be done once the protocol running (socket open)
        settings_string = json.dumps(self.settings)
        self.transport.connect(*self.server_addr)
        self.transport.write(settings_string, self.server_addr)
        print("Client started protocol!")

    def datagramReceived(self, data, addr):
        print("Client received {} from {}".format(data, addr))

        if not data == settings['test_id']+"_ack":
            print("Client could not process ack: {}".format(data))
            return

        # ack received successfully
        local_port = 0
        if settings['direction'] == 'client_to_server':
            local_port = settings['port_tx']
            instance = TestInstanceSend((host, settings['port_rx']), settings)
            ## Start sending!
        elif settings['direction'] == 'server_to_client':
            local_port = settings['port_rx']
            instance = TestInstanceRecv((host, settings['port_tx']), settings)
        else:
            print("Could not interpret setting 'direction': {}".format(
                  settings['direction']))
            sys.exit()

        reactor.listenUDP(local_port, instance)
        instance.results.addCallback(lambda x: self.report_results())
        instance.results.addCallback(lambda x: self.transport.stopListening())


        # Wait for instance to finish
        # This should probably not be done here
        # We should be done here, close connection

class TestInstanceSend(DatagramProtocol):
    """
    Sends coded data to a TestInstanceRecv until an ack is received or
    an upper limit of redundancy is reached.
    """
    def __init__(self, destination_addr, settings):
        # Setup variables related to test instance:
        self.destination_addr = destination_addr
        self.settings = settings
        self.packets_sent = 0
        self.done = False

        self.results = Deferred()

        # Build encoder
        self.encoder_factory = kodo.FullVectorEncoderFactoryBinary(
                                    max_symbols=settings['symbols'], 
                                    max_symbol_size=settings['symbol_size'])
        self.encoder = self.encoder_factory.build()
        data_in = os.urandom(self.encoder.block_size())
        self.encoder.set_symbols(data_in)
        print("TestInstanceSend built!")

    def startProtocol(self):
        self.transport.connect(*self.destination_addr)
        print("TestInstanceSend connected")
        reactor.callLater(0.5, self.asyncSendData)



    def datagramReceived(self, data, addr):
        """
        Checks if the correct nack was received from the correct sender
        """
        print("TestInstanceSend received {} from {}".format(data, addr))
        if not data == self.settings['test_id'] + "_ack_data":
            return
        # ack received

        self.done = True

    @inlineCallbacks
    def asyncSendData(self, packet_interval=0.5):
        """
        Asynchronous transmission of data
        """

        # there should be a start delay of some sort
        while not self.done:
            packet = self.encoder.write_payload()
            yield reactor.callLater(packet_interval, self.transport.write,
                                    packet)
            self.packets_sent += 1
            print("TestInstanceSend sent packet {}".format(self.packets_sent))
            if self.packets_sent >= (self.settings['symbols'] * 
                                     self.settings['max_redundancy']) / 100:
                self.done = True

        print("TestInstanceSend done")

        ## populate settings

        self.results.callback(self.settings)
        # yield self.transport.stopListening()

class TestInstanceRecv(DatagramProtocol):
    """
    Receives coded data from a TestInstanceSend. Sends an ack when data can be
    decoded, an for each packet received after that.
    """
    def __init__(self, source_addr, settings):
        # Setup variable related to test instance
        self.source_addr = source_addr
        self.settings = settings
        
        self.packets_received = 0
        self.packets_decode = 0
        
        self.time_start = None;
        self.time_stop = None;
        self.time_decode = None;

        self.results = Deferred()

        # Build decoder
        self.decoder_factory = kodo.FullVectorDecoderFactoryBinary(
                                    max_symbols=settings['symbols'], 
                                    max_symbol_size=settings['symbol_size'])
        self.decoder = self.decoder_factory.build()
        print("TestInstanceRecv built!")

    def startProtocol(self):
        self.transport.connect(*self.source_addr)
        print("TestInstanceRecv connected")

    def datagramReceived(self, data, addr):
        print("TestInstanceRecv received {} bytes from {}".format(len(data), addr))

        if self.time_start is None:
            self.time_start = time.time()

        self.packets_received += 1

        if not self.decoder.is_complete():
            self.decoder.read_payload(data)

        if self.decoder.is_complete():
            self.sendNack()
            if self.time_decode is None:
                self.time_decode = time.time()
                self.packets_decode = self.packets_received
            

                results = {'empty':'results'}
                # populate results dict
                # close test instance
                self.results.callback(results)
                # self.transport.stopListening()    

    def sendNack(self):
        nack = self.settings['test_id'] + "_ack_data"
        self.transport.write(nack, self.source_addr)

if __name__ == '__main__':
    server_port = 44444
    host = "127.0.0.1"

    server_addr = (host, server_port)
    
# test_id, source_addr, symbols, symbol_size

    settings = {
    'port_tx'   : 10000,
    'port_rx'   : 10001,
    'symbols'   : 16,
    'symbol_size' : 1500,
    'direction' : 'client_to_server',
    'max_redundancy' : 200,
    }

    server = Server()
    reactor.listenUDP(server_port, server)

    client = Client(server_addr, settings)
    reactor.listenUDP(0, client) # Any port

    # send = TestInstanceSend("test", addr, 16, 1500, 200)
    # reactor.listenUDP(server_port + 1, send)

    # recv = TestInstanceRecv("test", (host, port+1), 16, 1500)
    # reactor.listenUDP(server_port, recv)


    reactor.run()