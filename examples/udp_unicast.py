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
import datetime

class Server(DatagramProtocol):
    """
    Listens for test settings on specified port and launches test instances
    based on received settings.
    Server may run indefinately, launching multiple test instances
    """

    def __init__(self, report_results=print):
        self.report_results = report_results

    def datagramReceived(self, data, (host, port)):
        try:
            settings = json.loads(data)
        except Exception:
            print("Received invalid settings message.")
            return

        settings_ack = settings['test_id']+"_ack"
        self.transport.write(settings_ack, (host, port))

        settings['ip_client'] = host
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

        print("Connection from {}: Running '{}'... ".format(
              host, settings['direction']))

        reactor.listenUDP(local_port, instance)
        instance.results.addCallback(self.report_results)

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
        self.settings['role'] = 'client'
        self.settings['ip_server'], self.settings['port_server'] = server_addr
        self.settings['date'] = str(datetime.datetime.now())

        self.report_results = report_results
        self.on_finish = Deferred()

        # set more settings variables

    def doStart(self):
        # Maybe this should be done once the protocol running (socket open)
        settings_string = json.dumps(self.settings)
        self.transport.connect(*self.server_addr)
        self.transport.write(settings_string, self.server_addr)

    def doStop(self):
        # Return test id to the on_finish callback
        reactor.callLater(0, self.on_finish.callback, self.settings['test_id'])

    def datagramReceived(self, data, (host, port)):
        if not data == self.settings['test_id']+"_ack":
            print("Client could not process ack: {}".format(data))
            return

        # ack received successfully
        local_port = 0
        if self.settings['direction'] == 'client_to_server':
            local_port = self.settings['port_tx']
            instance = TestInstanceSend((host, self.settings['port_rx']), self.settings)
            ## Start sending!
        elif self.settings['direction'] == 'server_to_client':
            local_port = self.settings['port_rx']
            instance = TestInstanceRecv((host, self.settings['port_tx']), self.settings)
        else:
            print("Could not interpret setting 'direction': {}".format(
                  self.settings['direction']))
            sys.exit()

        print("Running '{}' with {} symbols of size {}.".format(
              self.settings['direction'], self.settings['symbols'],
              self.settings['symbol_size']))

        reactor.listenUDP(local_port, instance)
        instance.results.addCallback(self.report_results)
        instance.results.addCallback(lambda x: self.transport.stopListening())

class TestInstanceSend(DatagramProtocol):
    """
    Sends coded data to a TestInstanceRecv until an ack is received or
    an upper limit of redundancy is reached.
    """
    def __init__(self, destination_addr, settings):
        # Setup variables related to test instance:
        self.destination_addr = destination_addr
        self.settings = settings

        self.settings['packets_total'] = 0
        self.settings['packets_decode'] = 0

        self.settings['time_start'] = None;
        self.settings['time_end'] = None;
        self.settings['time_decode'] = None;

        self.done = False

        self.results = Deferred()

        # Build encoder
        self.encoder_factory = kodo.FullVectorEncoderFactoryBinary(
                                    max_symbols=settings['symbols'], 
                                    max_symbol_size=settings['symbol_size'])
        self.encoder = self.encoder_factory.build()
        data_in = os.urandom(self.encoder.block_size())
        self.encoder.set_symbols(data_in)

    def doStart(self):
        self.transport.connect(*self.destination_addr)
        # Give the other side time to setup a receiver
        reactor.callLater(0, self.asyncSendData)

    def doStop(self):
        self.results.callback(self.settings)

    def datagramReceived(self, data, addr):
        """
        Checks if the correct nack was received from the correct sender
        """
        if not data == self.settings['test_id'] + "_ack_data":
            return

        # ack received
        self.done = True

        # keep track of how many packets were sent until 'done' detected
        self.settings['packets_decode'] = self.settings['packets_total']
        self.settings['time_decode'] = time.time()

    def asyncSendData(self, packet_interval=0):
        """
        Asynchronous transmission of data. Queues itself on the reactor event
        loop if not done sending. Allows async operation with 1 thread
        """

        if self.settings['time_start'] is None:
            self.settings['time_start'] = time.time()
        self.settings['time_end'] = time.time()

        if not self.done:

            packet = self.encoder.write_payload()
            self.transport.write(packet)
            self.settings['packets_total'] += 1

            if self.settings['packets_total'] >= (self.settings['symbols'] * 
                                        self.settings['max_redundancy']) / 100:
                self.done = True
            else:

                reactor.callLater(packet_interval, self.asyncSendData, 
                                  packet_interval)

        else:

            self.transport.stopListening() # stops the instance

class TestInstanceRecv(DatagramProtocol):
    """
    Receives coded data from a TestInstanceSend. Sends an ack when data can be
    decoded, an for each packet received after that.
    """
    def __init__(self, source_addr, settings):
        # Setup variable related to test instance
        self.source_addr = source_addr
        self.settings = settings
        
        self.settings['packets_decode'] = 0
        self.settings['packets_total'] = 0
        
        self.settings['time_start'] = None;
        self.settings['time_end'] = None;
        self.settings['time_decode'] = None;

        self.results = Deferred()

        # Build decoder
        self.decoder_factory = kodo.FullVectorDecoderFactoryBinary(
                                    max_symbols=settings['symbols'], 
                                    max_symbol_size=settings['symbol_size'])
        self.decoder = self.decoder_factory.build()

    def doStart(self):
        self.transport.connect(*self.source_addr)
        self.timeout = reactor.callLater(self.settings['timeout'], 
                                         self.transport.stopListening)

    def doStop(self):
        self.results.callback(self.settings)

    def datagramReceived(self, data, addr):
        self.timeout.reset(self.settings['timeout']) # postpone timeout

        if self.settings['time_start'] is None:
            self.settings['time_start'] = time.time()
        self.settings['time_end'] = time.time()

        self.settings['packets_total'] += 1

        if not self.decoder.is_complete():
            self.decoder.read_payload(data)

        if self.decoder.is_complete():
            self.sendNack()
            if self.settings['time_decode'] is None:
                self.settings['time_decode'] = time.time()
                self.settings['packets_decode'] = self.settings['packets_total']


    def sendNack(self):
        nack = self.settings['test_id'] + "_ack_data"
        self.transport.write(nack, self.source_addr)

def run():
    reactor.run()

def stop():
    reactor.stop()

if __name__ == '__main__':
    server_port = 44444
    host = "127.0.0.1"

    server_addr = (host, server_port)
    
    settings = dict(
    port_tx   = 10000,
    port_rx   = 10001,
    symbols   = 16,
    symbol_size = 1500,
    direction = 'client_to_server',
    max_redundancy = 200,
    timeout   = 0.2
    )

    server = Server()
    reactor.listenUDP(server_port, server)

    client = Client(server_addr, settings)
    reactor.listenUDP(0, client) # Any port

    run()