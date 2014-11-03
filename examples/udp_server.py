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
    """Example of a sender which encodes and sends a file."""
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument(
        '--settings-port',
        type=int,
        help='The port to use.',
        default=41001)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use.')

    args = parser.parse_args()

    if args.dry_run:
        return

    s = Server(args)
    s.start()


class Server:

    def __init__(self,args):

        self.args = args

        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
                print("Message not understood.")
                continue

            settings['client_ip'] = address[0]

            if settings['direction'] == 'server->client':
                self.send_data(settings)
            elif settings['direction'] == 'client->server':
                self.receive_data(settings)

    def receive_data(self, settings):

        decoder_factory = kodo.full_rlnc_decoder_factory_binary(
            max_symbols=settings['symbols'],
            max_symbol_size=settings['symbol_size'])

        decoder = decoder_factory.build()

        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.settimeout(settings['timeout'])
        data_socket.bind(('', settings['data_port']))

        self.send_socket.sendto(
            "settings OK, receiving",
            (settings['client_ip'], settings['client_control_port']))

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
        print("Receiving finished, decoded after " + str(received) + " packets")

    def send_data(self, settings):

        encoder_factory = kodo.full_rlnc_encoder_factory_binary(
            settings['symbols'], settings['symbol_size'])

        encoder = encoder_factory.build()
        data_in = os.urandom(encoder.block_size())
        encoder.set_symbols(data_in)

        control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        control_socket.settimeout(0.00000000000000000001)
        control_socket.bind(('', settings['server_control_port']))

        self.send_socket.sendto(
            "settings OK, sending",
            (settings['client_ip'], settings['client_control_port']))

        for i in range(1,settings['symbols'] + settings['redundant_symbols']+1):
            packet = encoder.encode()
            self.send_socket.sendto(packet,
                (settings['client_ip'], settings['data_port']))

            try:
                ack = control_socket.recv(1024)
                print ("Stopping after " + str(i) + " sent packets" )
                break
            except socket.timeout:
                continue

        control_socket.close()
        print("Sent " + str(i) + " packets")

if __name__ == "__main__":
    main()
