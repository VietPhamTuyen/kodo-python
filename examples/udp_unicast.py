#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

from __future__ import print_function
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.base import DelayedCall
from twisted.internet import reactor

import sys
import kodo
import uuid
import time
import json
import os
import datetime
import random

random.seed()

"""
    General workflow and Hierarchi of the classes in this file 

    Server listens for test settings from Client on globally known port.
    On received settings, a client-specific port is opened.

    If the settings specify a test-scenario direction from:
    -   SERVER TO CLIENT: The server launches a SendInstance and transmits data 
        (from the new port) to the (host, port) pair used to send the settings.
        In case settings with the same test-id are received again,
        this is ignored and discarded while the SendInstance is active.
        The client is expected to send an ACK on the private port when finished
        receiving data. The ack should be re-sent for each additional
        packet the client receives.

    -   CLIENT TO SERVER: The server starts a ReceiveInstance on the new port,
        which begins its life begin transmitting an ACK to the client and 
        listens for incoming data. The server associates the RecvInstace with
        the specified test ID.
        In case the ACK was lost, the client will (after a timeout) re-send the 
        settings. An ACK for each received settings of this direction 
        must be sent. When the Server re-receives these settings, the test-id
        is recognised, and the RecvInstance is ordered to re-transmit the ACK.
        The cycle may run indefinately (but certainly should not), and is broken
        when the client receives the ACK before the timeout. The timeout should
        be big enough to allow this.
        When data is decoded fully, an ACK(data) is sent to the client.
        Additional ACKs are transmitted for each additional data packet received
        after all data is received.

    The Client thus only uses one port for each test scenario (and may re-use
    this for several runs), while the Server uses one for receiving settings,
    a "service" port, and then creates "private" ports for each
    connecting Client.
    This should also enable communication if only Server has a global address.
    """

class Server(DatagramProtocol):
    """
    Listens for settings from Clients on server port.
    On received settings:
    
    -   If settings direction is server to client, the server launches a 
        SendInstance on a new port.
        In case settings test-id is already known (an Instance is already 
        associated with the test-id), the settings are discarded
    -   If settings direction is client to server, the server launches a
        RecvInstance on a new port.
        In case settings test-id is already known (an Instance is already 
        associated with the test-id), the associated RecvInstance is ordered to
        retransmit the start-up ACK.
    
    Server may run indefinetely, launching multiple test instances
    """

    def __init__(self, report_results=print):
        print("Starting server..")
        self.report_results = report_results
        self.active_instances = {} # identified by "'test-id'"

    def detach_instance(results):
        self.report_results(results)
        instance = self.active_instances.pop(results['test_id'])
        return results
        # Any last operations for instance?

    def datagramReceived(self, data, (host, port)):
        try:
            settings = json.loads(data)
        except Exception:
            print("Discarding invalid settings message.")
            return

        print("Server received settings: {}".format(settings))

        # Verify that all needed entries are in settings, otherwise discard

        settings['ip_client'] = host
        settings['port_client'] = port
        settings['role'] = 'server'

        test_id = settings['test_id']

        if settings['direction'] == 'server_to_client':

            if not self.active_instances.has_key(test_id):
                instance = TestInstanceSend((host, port), settings, False)
                instance.results.addCallback(self.detach_instance)
                self.active_instances[test_id] = instance
                reactor.listenUDP(0, instance) # any port
            else:
                # just ignore
                return

        elif settings['direction'] == 'client_to_server':

            if not self.active_instances.has_key(test_id):
                instance = TestInstanceRecv((host, port), settings, False)
                instance.results.addCallback(self.detach_instance)
                self.active_instances[test_id] = instance
                reactor.listenUDP(0, instance) # any port
            else:
                assert(type(self.active_instances[test_id]) is TestInstanceRecv)
                self.active_instances[test_id].sendSettingsAck((host, port))
    
        else:

            print("Invalid direction specified in received settings: {}".format(
                  settings['direction']))
            return

        print("{}:{} Connected: Running '{}' with ID {}".format(
              host, port, settings['direction'], settings['test_id']))

class Client(object):
    """
    Depending on the test-direction specified in the settings, two procedures 
    will be launched by the Client:

    -   CLIENT_TO_SERVER: A SendInstance is launched in client mode, sending
        the test parameters to the server. When the server has ACK'd the
        settings, the instance will transmit data until the receiver has decoded
        the data.
    -   SERVER_TO_CLIENT: A RecvInstance is launched in client mode, sending
        the test parameters to the server. The server will then start sending
        data immidiately. The RecvInstance will re-transmit the settings if not
        data has been received before a timeout.
    """

    def __init__(self, report_results=print):
        self.report_results = report_results
    
    @inlineCallbacks
    def run_test(self, settings):
        server_ip = settings['ip_server']
        server_port = settings['port_server']
        settings['test_id'] = uuid.uuid4().get_hex()
        settings['role'] = 'client'
        settings['date'] = str(datetime.datetime.now())

        on_finish = Deferred()

        # Create the appropriate instance:
        instance = None
        if settings['direction'] is 'client_to_server':
            instance = TestInstanceSend((server_ip, server_port), 
                                        settings, True)
        elif settings['direction'] is 'server_to_client':
            instance = TestInstanceRecv((server_ip, server_port), 
                                        settings, True)
        else:
            print("Invalid direction specified in settings: {}".format(
                  settings['direction']))
            return

        reactor.listenUDP(0, instance) # any port
        instance.results.addCallback(self.report_results)
        instance.results.addCallback(on_finish.callback)

        print("Running '{}' with {} symbols of size {} ... ".format(
              settings['direction'], settings['symbols'], 
              settings['symbol_size']))

        results = yield on_finish
        # yield doesnt return until its callback has emitted. Meanwhile the
        # reactor event loop is free to process whatever task it may have.
        print("Finished")

class TestInstance(DatagramProtocol):
    """
    Base Class for TestInstanceSend and TestInstanceRecv.
    Contains shared functionality for the two, and doesnt do anything on its own
    """

    def __init__(self, remote_addr, settings, client_mode):
        self.remote_addr = remote_addr # for 'client_mode = True' this is server
        self.settings = settings
        self.client_mode = client_mode
        self.handshake_finished = not client_mode
        self.handshake_timeout = None

        self.settings['packets_total'] = 0

        self.settings['time_start'] = time.time()
        self.settings['time_first'] = None
        self.settings['time_last'] = None

        if not self.settings.has_key('erasures'):
            self.settings['erasures'] = 0

        self.results = Deferred()

    def doStop(self):
        print("Stopping TestInstance")
        self.results.callback(self.settings)

    @inlineCallbacks
    def doHandshake(self):
        print("Starting Handshake in TestInstance")
        assert(self.client_mode) # should only be called in client mode
        settings_string = json.dumps(self.settings)
        server_addr = (settings['ip_server'], settings['port_server'])
        while not self.handshake_finished:
            self.transport.write(settings_string, server_addr)
            timeout = Deferred()
            self.handshake_timeout = reactor.callLater(settings['timeout'], 
                                                       timeout.callback, None)
            print("Handshake: Waiting for handshake ack or timeout")
            yield timeout
            print("Handshake: trying again")

        # handhake finished at this point
        print("Finished Handshake in TestInstance")

    def finishHandshake(self, addr):
        print("Finish handshake with addr {}".format(addr))
        assert(self.client_mode) # Settings ACK only makes sense in client mode
        self.handshake_finished = True
        self.remote_addr = addr
        if self.handshake_timeout.active():
            self.handshake_timeout.reset(0);

class TestInstanceSend(TestInstance):
    """
    Sends coded data to a TestInstanceRecv until an ack is received or
    an upper limit of redundancy is reached. 
    If client mode is enabled, the process is started by sending the settings
    to the server address, and waiting for the subsequent ACK of these, until
    coded data is transmitted.
    """
    def __init__(self, remote_addr, settings, client_mode):
        TestInstance.__init__(self, remote_addr, settings, client_mode)

        self.settings['mode'] = 'TX'

        self.done = False

        # Build encoder
        self.encoder_factory = kodo.FullVectorEncoderFactoryBinary(
                                    max_symbols=self.settings['symbols'], 
                                    max_symbol_size=self.settings['symbol_size'])
        self.encoder = self.encoder_factory.build()
        data_in = os.urandom(self.encoder.block_size())
        self.encoder.set_symbols(data_in)

    @inlineCallbacks
    def doStart(self):
        if self.client_mode:
            # Wait for handshake to finish before continuing
            yield self.doHandshake()

        print("Connecting SendInstance to {}".format(self.remote_addr))
        self.transport.connect(*self.remote_addr)
        # start sending
        packet_interval = 0

        if self.settings.has_key('rate_limit_kBps'):
            rate_limit = self.settings['rate_limit_kBps']
            symbol_size = self.settings['symbol_size']
            packet_interval = symbol_size / float(1000 * rate_limit)

        reactor.callLater(0, self.asyncSendData, packet_interval)

    def datagramReceived(self, data, addr):
        """
        Checks if the correct ack was received from the remote
        """
        # Introduce erasures
        if random.random() < self.settings['erasures']:
            return

        if data == self.settings['test_id'] + "_ack_data":
            self.done = True
        elif data == self.settings['test_id'] + "_ack_settings":
            self.finishHandshake(addr)

    def asyncSendData(self, packet_interval=0):
        print("asyncSendData called!")
        """
        Asynchronous transmission of data. Queues itself on the reactor event
        loop if not done sending. Allows async operation with 1 thread
        """
        if self.settings['time_first'] is None:
            self.settings['time_first'] = time.time()
        self.settings['time_last'] = time.time()

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

class TestInstanceRecv(TestInstance):
    """
    Receives coded data from a TestInstanceSend. 
    If client_mode is enabled, the process is started by sending the settings to
    the server, and then waiting for data to arrive. If data does not arrive
    before a timeout is expired, the settings are re-transmitted, and 
    the timeout is reset.
    If client_mode is disabled, the process is started by sending an ack of the
    received settings.
    Sends an ack when data can be decoded, and for each packet received 
    after that event.
    """
    def __init__(self, remote_addr, settings, client_mode):
        TestInstance.__init__(self, remote_addr, settings, client_mode)

        self.settings['mode'] = 'RX'
        self.settings['packets_decode'] = 0
        self.settings['time_decode'] = None

        # Build decoder
        self.decoder_factory = kodo.FullVectorDecoderFactoryBinary(
                                    max_symbols=self.settings['symbols'], 
                                    max_symbol_size=self.settings['symbol_size'])
        self.decoder = self.decoder_factory.build()

    def doStart(self):
        if self.client_mode:
            self.doHandshake() # will modify remote_addr
        else:
            self.sendSettingsAck(self.remote_addr)

        self.transport.connect(*self.remote_addr)
        self.timeout = reactor.callLater(self.settings['timeout'], 
                                         self.transport.stopListening)

        # handhake finished at this point
        print("Finished Handshake in RecvInstance")

    def datagramReceived(self, data, addr):
        # Introduce erasures
        if random.random() < self.settings['erasures']:
            return

        if self.client_mode and not self.handshake_finished:
            finishHandshake(addr)

        self.timeout.reset(self.settings['timeout']) # postpone data timeout

        if self.settings['time_first'] is None:
            self.settings['time_first'] = time.time()
        self.settings['time_last'] = time.time()

        self.settings['packets_total'] += 1

        if not self.decoder.is_complete():
            self.decoder.read_payload(data)

        if self.decoder.is_complete():
            self.sendNack()
            if self.settings['time_decode'] is None:
                self.settings['time_decode'] = time.time()
                self.settings['packets_decode'] = self.settings['packets_total']

    def sendDataAck(self):
        ack = self.settings['test_id'] + "_ack_data"
        self.transport.write(ack)

    def sendSettingsAck(self, addr):
        ack = self.settings['test_id'] + "_ack_settings"
        self.transport.write(ack, addr)


def run():
    reactor.run()

def stop():
    reactor.stop()

if __name__ == '__main__':
    server_port = 44444
    host = "127.0.0.1"

    server_addr = (host, server_port)
    
    settings = dict(
    port_server = 10000,
    ip_server = "127.0.0.1",
    erasures = 0.1,
    rate_limit_kBps = 0.5,
    symbols   = 16,
    symbol_size = 1500,
    direction = 'client_to_server',
    max_redundancy = 200,
    timeout   = 0.5
    )

    # server = Server()
    # reactor.listenUDP(server_port, server)

    client = Client()
    # d = Deferred()
    # d.addCallback(client.run_test)
    # d.addCallback(reactor.stop())
    reactor.callLater(0, client.run_test, settings)

    run()