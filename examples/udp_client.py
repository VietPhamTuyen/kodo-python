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
        '--server_ip',
        type=str,
        help='The ip to use.',
        default='127.0.0.1')

    parser.add_argument(
        '--settings-port',
        type=int,
        help='The port to use.',
        default=4141)

    parser.add_argument(
        '--client_port',
        type=int,
        help='The port to use.',
        default=4242)

    parser.add_argument(
        '--server_port',
        type=int,
        help='The port to use.',
        default=4343)

    parser.add_argument(
        '--symbols',
        type=int,
        help='The number of symbols.',
        default=64)

    parser.add_argument(
        '--symbol_size',
        type=int,
        help='The size of each symbol.',
        default=1400)

    parser.add_argument(
        '--redundant_symbols',
        type=int,
        help='The number of redundant symbols.',
        default=10)

    parser.add_argument(
        '--direction',
        choices=['client->server', 'server->client', 'client->server->client'],
        default='client->server->client')

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use.')

    args = parser.parse_args()

    if args.dry_run:
        return

    settings = vars(args)

    if settings['direction'] == 'server->client':
        receive_data(settings)
    elif settings['direction'] == 'client->server':
        send_data(settings)
    elif settings['direction'] == 'client->server->client':
        settings['direction'] = 'client->server'
        send_data(settings)
        settings['direction'] = 'server->client'
        receive_data(settings)


def send_data(settings):
    """Upload data."""

    send_settings(settings)

    # Setup kodo encoder_factory and encoder
    encoder_factory = kodo.full_rlnc_encoder_factory_binary(
        settings['symbols'],
        settings['symbol_size'])

    encoder = encoder_factory.build()
    data_in = os.urandom(encoder.block_size())
    encoder.set_symbols(data_in)

    # Set sending sockets
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (settings['server_ip'], settings['server_port'])

    # Sent coded packets
    for i in range(1,settings['symbols'] + settings['redundant_symbols']+1):
        packet = encoder.encode()
        send_socket.sendto(packet, address)

    print("Sent " + str(i) + " packets." )


def receive_data(settings):
    """Receive data from the server."""

    # Setup kodo encoder_factory and decoder
    decoder_factory = kodo.full_rlnc_decoder_factory_binary(
        max_symbols=settings['symbols'],
        max_symbol_size=settings['symbol_size'])

    decoder = decoder_factory.build()

    # Set receiving sockets
    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.bind((settings['server_ip'], settings['client_port']))

    send_settings(settings)

    # Decode coded packets
    #~ print("Receiving data")
    received = 0
    while not decoder.is_complete():
        packet = receive_socket.recv(4096)

        decoder.decode(packet)
        received += 1

    print("Receiving finished, decoded after " + str(received) + " packets")


def send_settings(settings):
    """ Send settings to server."""

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.settimeout(2)
    receive_socket.bind((settings['server_ip'], settings['settings_port']+1))

    message = json.dumps(settings)
    data = None
    address = ''
    while data is None and address != settings['server_ip']:
        #~ print("Sending configuration.")
        send_socket.sendto(
            message, (settings['server_ip'], settings['settings_port']))
        #~ print("Waiting for confirmation.")
        try:
            data, address = receive_socket.recvfrom(1024)
        except socket.timeout:
            print("timeout.")
            pass
    #~ print("Server acknowledged.")

if __name__ == "__main__":
    main()
