#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import socket

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
        default=4141)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use.')

    args = parser.parse_args()

    if args.dry_run:
        return

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.bind(('', args.settings_port))

    # Wait for settings connections
    print("Server running, press ctrl+c to stop.")
    while True:
        data, address = receive_socket.recvfrom(1024)
        try:
            settings = json.loads(data)
        except Exception:
            print("Message not understood.")
            continue
        settings['client_ip'] = address[0]

        if settings['direction'] == 'server->client':
            send_data(settings)
        elif settings['direction'] == 'client->server':
            receive_data(settings)

def respond_client(settings, message):
    '''
    Respond to the client when settings have been received and we are ready
    to send or receive
    '''

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_socket.sendto(
            message, (settings['client_ip'], settings['client_settings_port']))

def receive_data(settings):

    decoder_factory = kodo.full_rlnc_decoder_factory_binary(
        max_symbols=settings['symbols'],
        max_symbol_size=settings['symbol_size'])

    decoder = decoder_factory.build()

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.bind((settings['client_ip'], settings['server_port']))

    received = 0
    respond_client(settings, "settings OK, recieving")

    while not decoder.is_complete():
        packet = receive_socket.recv(settings['symbol_size']+100)
        decoder.decode(packet)
        received += 1

    print("Receiving finished, decoded after " + str(received) + " packets")


def send_data(settings):

    encoder_factory = kodo.full_rlnc_encoder_factory_binary(
        settings['symbols'], settings['symbol_size'])

    encoder = encoder_factory.build()
    data_in = os.urandom(encoder.block_size())
    encoder.set_symbols(data_in)

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (settings['client_ip'], settings['client_port'])

    respond_client(settings, "settings OK, sending")

    for i in range(1,settings['symbols'] + settings['redundant_symbols']+1):
        packet = encoder.encode()
        send_socket.sendto(packet, address)

    print("Sent " + str(i) + " packets")

if __name__ == "__main__":
    main()
