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
        '--dry-run',
        action='store_true',
        help='Run without network use.')

    parser.add_argument(
        '--settings-port',
        type=int,
        help='The port to use.',
        default=41001)

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
        default=200)

    parser.add_argument(
        '--direction',
        choices=['client->server', 'server->client', 'client->server->client'],
        default='client->server->client')

    parser.add_argument(
        '--timeout',
        type=float,
        help='The timeout on the sockets.',
        default=.2)

    args = parser.parse_args()

    if args.dry_run:
        return

    if args.symbol_size > 65000:
        Print("Resulting packets too big, reduce symbol size")
        return

    if args.role == 'client':
        client(args)

    if args.role == 'server':
        server(args)

def send_data(args, settings):
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

    if args.role == 'client':
        send_settings(settings)
        control_socket.bind(('', settings['client_control_port']))

    if args.role == 'server':
        send_socket.sendto("settings OK, sending",
            (settings['client_ip'], settings['client_control_port']))
        control_socket.bind(('', settings['server_control_port']))

    address = (settings['other_ip'], settings['data_port'])

    sent = 0
    start = end = time.time()

    while sent < settings['symbols']* settings['max_redundancy']:
        packet = encoder.encode()
        send_socket.sendto(packet, address)
        sent += 1

        try:
            ack = control_socket.recv(1024)
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
    print("Sent " + str(sent) + " packets, " + str(size/1000) + " kB, in " +
          str(end-start) + " s, at " + str(size * 8 / 1000 / (end-start)) + " kb/s.")

def receive_data(args, settings):
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

    address = (settings['other_ip'], settings['other_control_port'])

    if args.role == 'client':
        send_settings(settings)

    if args.role == 'server':
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

    size = decoder.block_size() * (float(received) / settings['symbols'])
    print("Decoded after " + str(received) + " packets, received " +
          str(size/1000 ) + " kB, in " + str(end-start) + " s, at " +
          str(decoder.block_size() * 8 / 1000 / (end-start)) + " kb/s.")

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

        settings['client_ip'] = address[0]
        settings['other_ip'] = address[0]
        settings['other_control_port'] = settings['client_control_port']
        settings = settings

        if settings['direction'] == 'server->client':
            send_data(args, settings)
        elif settings['direction'] == 'client->server':
            receive_data(args, settings)

def client(args):

    settings = vars(args)
    settings['other_ip'] = settings['server_ip']
    settings['other_control_port'] = settings['server_control_port']

    if settings['direction'] == 'server->client':
        receive_data(args, settings)

    elif settings['direction'] == 'client->server':
        send_data(args, settings)

    elif settings['direction'] == 'client->server->client':
        settings['direction'] = 'server->client'
        receive_data(args, settings)
        settings['direction'] = 'client->server'
        send_data(args, settings)

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
    data = None
    address = ''
    while data is None:
        # Send settings
        send_socket.sendto(
            message, (settings['server_ip'], settings['settings_port']))
        # Waiting for respons
        try:
            data, address = control_socket.recvfrom(1024) #Server acknowledged
        except socket.timeout:
            print("Timeout - server not responding to settings.")
            pass

    control_socket.close()

if __name__ == "__main__":
    main()

