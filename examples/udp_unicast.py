#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import socket
import time

import argparse
import json

import kodo

def main():
    """
    UDP Client for sending and receiving files from/to a server.
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    # parser.add_argument(
    #     '--data-size',
    #     type=int,
    #     help='KB of data to be send or recieved.',
    #     default=100)

    parser.add_argument(
        '--role',
        choices=['server', 'client'],
        default='client')

    parser.add_argument(
        '--server-ip',
        type=str,
        help='The ip to use.',
        default='127.0.0.1')

    parser.add_argument(
        '--settings-port',
        type=int,
        help='The port to use.',
        default=41001)

    parser.add_argument(
        '--client-control-port',
        type=int,
        help='The port to use.',
        default=41003)

    parser.add_argument(
        '--server-control-port',
        type=int,
        help='The port to use.',
        default=41005)

    parser.add_argument(
        '--data-port',
        type=int,
        help='The port to use for data.',
        default=41011)

    parser.add_argument(
        '--symbols',
        type=int,
        help='The number of symbols.',
        default=64)

    parser.add_argument(
        '--symbol-size',
        type=int,
        help='The size of each symbol.',
        default=1400)

    parser.add_argument(
        '--max_redundancy',
        type=float,
        help='The maximum amount of redundancy to be sent in percent.',
        default=100)

    parser.add_argument(
        '--direction',
        choices=['client->server', 'server->client', 'client->server->client'],
        default='client->server->client')

    parser.add_argument(
        '--timeout',
        type=float,
        help='The timeout on the sockets.',
        default=.2)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use.')

    args = parser.parse_args()

    if args.dry_run:
        return

    if args.symbol_size > 65000:
        Print("Resulting packets too big, reduce symbol size")
        return

    if args.role == 'client':
        c = Client(args)
        c.start()

    if args.role == 'server':
        s = Server(args)
        s.start()


class Base:

    def __init__(self,args):

        self.args = args
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self):
        """
        Send data to the other node
        """

        # Setup kodo encoder_factory and encoder
        encoder_factory = kodo.full_rlnc_encoder_factory_binary(
            self.settings['symbols'], self.settings['symbol_size'])

        encoder = encoder_factory.build()
        data_in = os.urandom(encoder.block_size())
        encoder.set_symbols(data_in)

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_socket.settimeout(0.00000000000000000001)

        if self.args.role == 'client':
            self.send_settings()
            control_socket.bind(('', self.settings['client_control_port']))

        if self.args.role == 'server':
            self.send_socket.sendto("settings OK, sending",
                (self.settings['client_ip'], self.settings['client_control_port']))
            control_socket.bind(('', self.settings['server_control_port']))

        address = (self.settings['other_ip'], self.settings['data_port'])

        sent = 0
        start = end = time.time()


        while sent < self.settings['symbols']* self.settings['max_redundancy']:
            packet = encoder.encode()
            self.send_socket.sendto(packet, address)
            sent += 1

            try:
                ack = control_socket.recv(1024)
                if end == start:
                    end = time.time()
                #~ print ("Stopping after " + str(i) + " sent packets" )
                break
            except socket.timeout:
                continue

        # if no ack was received we sent all packets
        if end == start:
            end = time.time()

        control_socket.close()

        size = encoder.block_size() * (float(sent) / self.settings['symbols'])
        print("Sent " + str(sent) + " packets, " + str(size/1000) + " kB, in " +
              str(end-start) + " s, at " + str(size * 8 / 1000 / (end-start)) + " kb/s.")

    def receive_data(self):
        """Receive data from the other node"""

        # Setup kodo encoder_factory and decoder
        decoder_factory = kodo.full_rlnc_decoder_factory_binary(
            max_symbols=self.settings['symbols'],
            max_symbol_size=self.settings['symbol_size'])

        decoder = decoder_factory.build()

        # Set receiving sockets
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.settimeout(self.settings['timeout'])
        data_socket.bind(('', self.settings['data_port']))

        if self.args.role == 'client':
            self.send_settings()

        if self.args.role == 'server':
            self.send_socket.sendto("self.settings OK, receiving",
                (self.settings['client_ip'], self.settings['client_control_port']))

        # Decode coded packets
        received = 0
        start = end = time.time()

        while 1:
            try:
                packet = data_socket.recv(self.settings['symbol_size']+100)

                if not decoder.is_complete():
                    decoder.decode(packet)
                    received += 1

                if decoder.is_complete():
                    if end == start:
                        end = time.time() #stopping time once
                    self.send_socket.sendto("Stop sending",
                        (self.settings['other_ip'], self.settings['other_control_port']))

            except socket.timeout:
                #~print("Timeout - stopped receiving")
                break # no more data arriving

        # in case we did not complete
        if end == start:
            end = time.time()

        data_socket.close()

        size = decoder.block_size() * (float(received) / self.settings['symbols'])
        print("Decoded after " + str(received) + " packets, received " +
              str(size/1000 ) + " kB, in " + str(end-start) + " s, at " +
              str(decoder.block_size() * 8 / 1000 / (end-start)) + " kb/s.")


class Server(Base):

    def start(self):

        settings_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        settings_socket.bind(('', self.args.settings_port))

        # Wait for settings connections
        print("Server running, press ctrl+c to stop.")
        while True:
            data, address = settings_socket.recvfrom(1024)
            try:
                settings = json.loads(data)
            except Exception:
                print("Settings Message not understood.")
                continue

            settings['client_ip'] = address[0]
            settings['other_ip'] = address[0]
            settings['other_control_port'] = settings['client_control_port']
            self.settings = settings

            if settings['direction'] == 'server->client':
                self.send_data()
            elif settings['direction'] == 'client->server':
                self.receive_data()


class Client(Base):

    def start(self):

        settings = vars(self.args)
        settings['other_ip'] = settings['server_ip']
        settings['other_control_port'] = settings['server_control_port']
        self.settings = settings

        if self.settings['direction'] == 'server->client':
            self.receive_data()

        elif self.settings['direction'] == 'client->server':
            self.send_data()

        elif self.settings['direction'] == 'client->server->client':
            self.settings['direction'] = 'server->client'
            self.receive_data()
            self.settings['direction'] = 'client->server'
            self.send_data()

    def send_settings(self):
        """
        Send settings to server, block until confirmation received that settings
        was correctly received
        """

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_socket.settimeout(self.settings['timeout'])
        control_socket.bind(('', self.settings['client_control_port']))

        message = json.dumps(self.settings)
        data = None
        address = ''
        while data is None:
            # Send self.settings
            self.send_socket.sendto(
                message, (self.settings['server_ip'], self.settings['settings_port']))
            # Waiting for respons
            try:
                data, address = control_socket.recvfrom(1024) #Server acknowledged
            except socket.timeout:
                #~print("timeout.")
                pass

        control_socket.close()

if __name__ == "__main__":
    main()

