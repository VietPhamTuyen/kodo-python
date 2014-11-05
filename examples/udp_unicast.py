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
    UDP Server/Client for sending and receiving files.
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    # parser.add_argument(
    #     '--data-size',
    #     type=int,
    #     help='KB of data to be send or recieved.',
    #     default=100)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use, for testing purposes')

    parser.add_argument(
        '--settings-port',
        type=int,
        help='settings port on the server.',
        default=41001)

    parser.add_argument(
        '--role',
        help = 'intended role, a server is waiting for test settings \
            from a client.',
        choices=['server', 'client'],
        default='client')

    client_group = parser.add_argument_group('Client arguments',
        'Arguments set on the client defining test parameters.')

    client_group.add_argument(
        '--server-ip',
        type=str,
        help='ip of the server.',
        default='127.0.0.1')

    client_group.add_argument(
        '--client-control-port',
        type=int,
        help='control port on the client side, used for signaling.',
        default=41003)

    client_group.add_argument(
        '--server-control-port',
        type=int,
        help='control port on the server side, used for signaling.',
        default=41005)

    client_group.add_argument(
        '--data-port',
        type=int,
        help='port used for data transmission.',
        default=41011)

    client_group.add_argument(
        '--symbols',
        type=int,
        help='number of symbols in each generation/block.',
        default=64)

    client_group.add_argument(
        '--symbol-size',
        type=int,
        help='size of each symbol, in bytes.',
        default=1400)

    client_group.add_argument(
        '--max-redundancy',
        type=float,
        help='maximum amount of redundancy to be sent, in percent.',
        default=200)

    client_group.add_argument(
        '--direction',
        help='direction of data transmission',
        choices=['client->server', 'server->client', 'client->server->client'],
        default='client->server->client')

    client_group.add_argument(
        '--timeout',
        type=float,
        help='timeout used for various sockets, in seconds.',
        default=.2)

    args = parser.parse_args()

    if args.dry_run:
        return

    if args.symbol_size > 65000:
        Print("Resulting packets too big, reduce symbol size")
        return

    if args.role == 'client':
        client(args)
    else: #server
        server(args)

def send_data(settings):
    """
    Send data to the other node
    """

    # Setup kodo encoder_factory and encoder
    encoder_factory = kodo.full_rlnc_encoder_factory_binary(
        settings['symbols'], settings['symbol_size'])

    encoder = encoder_factory.build()
    data_in = os.urandom(encoder.block_size())
    encoder.set_symbols(data_in)

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_socket.settimeout(0.00000000000000000001)

    if settings['role'] == 'client':
        address = (settings['server_ip'], settings['data_port'])
        send_settings(settings)
        control_socket.bind(('', settings['client_control_port']))
    else: # server
        address = (settings['client_ip'], settings['data_port'])
        control_socket.bind(('', settings['server_control_port']))
        send_socket.sendto("settings OK, sending",
            (settings['client_ip'], settings['client_control_port']))

    sent = 0
    start = end = time.time()

    while sent < settings['symbols']* settings['max_redundancy']/100:
        packet = encoder.encode()
        send_socket.sendto(packet, address)
        sent += 1

        try:
            control_socket.recv(1024)
            if end == start:
                end = time.time()
            break
        except socket.timeout:
            continue

    # if no ack was received we sent all packets
    if end == start:
        end = time.time()

    control_socket.close()

    size = encoder.block_size() * (float(sent) / settings['symbols'])
    print("Sent " + str(sent) + " packets, " + str(size/1000) +
          " kB, in " + str(end-start) + " s, at " +
          str(size * 8 / 1000 / (end-start)) + " kb/s.")

def receive_data(settings):
    """Receive data from the other node"""

    # Setup kodo encoder_factory and decoder
    decoder_factory = kodo.full_rlnc_decoder_factory_binary(
        max_symbols=settings['symbols'],
        max_symbol_size=settings['symbol_size'])

    decoder = decoder_factory.build()

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set receiving sockets
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.settimeout(settings['timeout'])
    data_socket.bind(('', settings['data_port']))

    if settings['role'] == 'client':
        address = (settings['server_ip'], settings['server_control_port'])
        send_settings(settings)
    else: #server
        address = (settings['client_ip'], settings['client_control_port'])
        send_socket.sendto("settings OK, receiving", address)

    # Decode coded packets
    received = 0
    start = end = time.time()

    while 1:
        try:
            packet = data_socket.recv(settings['symbol_size']+100)

            if not decoder.is_complete():
                decoder.decode(packet)
                received += 1

            if decoder.is_complete():
                if end == start:
                    end = time.time() #stopping time once
                send_socket.sendto("Stop sending", address)

        except socket.timeout:
            #~ print("Timeout - stopped receiving")
            break # no more data arriving

    # in case we did not complete
    if end == start:
        end = time.time()

    data_socket.close()

    if not decoder.is_complete():
        print("Decoding failed")

    size = decoder.block_size() * (float(received) / settings['symbols'])
    print("Received " + str(received) + " packets, totalling " +
          str(size/1000 ) + " kB, in " + str(end-start) + " s, at " +
          str(decoder.block_size() * 8 / 1000 / (end-start)) + " kb/s.")

def send_settings(settings):
    """
    Send settings to server, block until confirmation received that settings
    was correctly received
    """

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_socket.settimeout(settings['timeout'])
    control_socket.bind(('', settings['client_control_port']))

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = json.dumps(settings)
    ack = None
    address = ''
    while ack is None:
        # Send settings
        send_socket.sendto(
            message, (settings['server_ip'], settings['settings_port']))
        # Waiting for respons
        try:
            ack, address = control_socket.recvfrom(1024) #Server ack
        except socket.timeout:
            print("Timeout - server not responding to settings.")

    control_socket.close()

def server(args):

    settings_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    settings_socket.bind(('', args.settings_port))

    # Wait for settings connections
    print("Server running, press ctrl+c to stop.")
    while True:
        data, address = settings_socket.recvfrom(1024)
        try:
            settings = json.loads(data)
        except Exception:
            print("Settings Message not understood.")
            continue

        settings['role'] = 'server'
        settings['client_ip'] = address[0]

        if settings['direction'] == 'server->client':
            send_data(settings)

        if settings['direction'] == 'client->server':
            receive_data(settings)

def client(args):

    settings = vars(args)
    direction = settings.pop('direction')

    if 'server->client' in direction:
        settings['direction'] = 'server->client'
        receive_data(settings)

    if 'client->server' in direction:
        settings['direction'] = 'client->server'
        send_data(settings)

if __name__ == "__main__":
    main()
