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

    #~parser.add_argument(
        #~'--role',
        #~choices=['server', 'client'],
        #~default='client')

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
        '--redundant-symbols',
        type=int,
        help='The number of redundant symbols.',
        default=10)

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

    settings = vars(args)

    c = Client(args)

    if settings['direction'] == 'server->client':
        c.receive_data(settings)
    elif settings['direction'] == 'client->server':
        c.send_data(settings)
    elif settings['direction'] == 'client->server->client':
        settings['direction'] = 'server->client'
        c.receive_data(settings)
        settings['direction'] = 'client->server'
        c.send_data(settings)

class Client:

    def __init__(self,args):

        self.args = args

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, settings):
        """Upload data."""

        self.send_settings(settings)

        # Setup kodo encoder_factory and encoder
        encoder_factory = kodo.full_rlnc_encoder_factory_binary(
            settings['symbols'],
            settings['symbol_size'])

        encoder = encoder_factory.build()
        data_in = os.urandom(encoder.block_size())
        encoder.set_symbols(data_in)

        start = time.clock()
        for i in range(1,settings['symbols'] + settings['redundant_symbols']+1):
            packet = encoder.encode()
            self.send_socket.sendto(packet, (settings['server_ip'], settings['data_port']))

        end = time.clock()
        size = encoder.block_size() * (1. + float(settings['redundant_symbols']) /
               settings['symbols'])

        print("Sent " + str(settings['symbols']+settings['redundant_symbols']) +
              " packets, " + str(size/1000) + " kB, in " + str(end-start) +
              " s, at " + str(size * 8 / 1000 / (end-start)) + " kb/s.")

    def receive_data(self, settings):
        """Receive data from the server."""

        # Setup kodo encoder_factory and decoder
        decoder_factory = kodo.full_rlnc_decoder_factory_binary(
            max_symbols=settings['symbols'],
            max_symbol_size=settings['symbol_size'])

        decoder = decoder_factory.build()

        # Set receiving sockets
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.settimeout(settings['timeout'])
        data_socket.bind(('', settings['data_port']))

        self.send_settings(settings)

        # Decode coded packets
        received = 0
        start = time.time()
        end = start

        while 1:
            try:
                packet = data_socket.recv(settings['symbol_size']+100)

                if not decoder.is_complete():
                    decoder.decode(packet)
                    received += 1

                if decoder.is_complete():
                    if end == start:
                        end = time.time() #stopping time once
                    self.send_socket.sendto("Stop sending",
                        (settings['server_ip'], settings['server_control_port']))

            except socket.timeout:
                #~print("Timeout - stopped receiving")
                break # no more data arriving

        data_socket.close()

        print("Decoded after " + str(received) + " packets, received " +
              str(float(decoder.block_size()) / 1000 ) + " kB, in " + str(end-start) +
              " s, at " + str(decoder.block_size() * 8 / 1000 / (end-start))
              + " kb/s.")

    def send_settings(self, settings):
        """
        Send settings to server, block until confirmation received that settings
        was correctly understood and everything is set up
        """

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_socket.settimeout(settings['timeout'])
        control_socket.bind(('', settings['client_control_port']))

        message = json.dumps(settings)
        data = None
        address = ''
        while data is None:
            # Send settings
            self.send_socket.sendto(
                message, (settings['server_ip'], settings['settings_port']))
            # Waiting for respons
            try:
                data, address = control_socket.recvfrom(1024) #Server acknowledged
            except socket.timeout:
                #~print("timeout.")
                pass

        control_socket.close()

if __name__ == "__main__":
    main()
