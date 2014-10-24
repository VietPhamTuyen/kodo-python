#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import argparse
import kodo
import socket
import json


def main():
    return
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
        '--ip',
        type=str,
        help='The ip to use.',
        default='127.0.0.1')

    parser.add_argument(
        '--settings-port',
        type=int,
        help='The port to use.',
        default=4141)

    parser.add_argument(
        '--port',
        type=int,
        help='The port to use.',
        default=4242)

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
        '--direction',
        choices=['upload', 'download'],
        default='download')

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use.')

    args = parser.parse_args()

    if args.direction == 'download':
        download(args)
    elif args.direction == 'upload':
        upload(args)


def upload(args):
    """Upload data."""
    send_settings(args)
    assert 0, 'Wrong direction!'


def download(args):
    """Download data."""
    # In the following we will make an decoder factory.
    # The factories are used to build actual decoder
    decoder_factory = kodo.full_rlnc_decoder_factory_binary(
        max_symbols=args.symbols,
        max_symbol_size=args.symbol_size)

    decoder = decoder_factory.build()

    # Count number of lost packets.
    # Time time it took / print throughput

    send_settings(
        settings_port=args.settings_port,
        ip=args.ip,
        request=args.direction,
        symbol_size=args.symbol_size,
        symbols=args.symbols,
        port=args.port)

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.bind((args.ip, args.port))

    print("Processing")
    while not decoder.is_complete() and not args.dry_run:
        packet = receive_socket.recv(4096)

        decoder.decode(packet)
        print("Packet decoded!")
        print("rank: {}/{}".format(decoder.rank(), decoder.symbols()))

        # Write data to file (it may not be valid until the very end though).
        f = open(args.output_file, 'wb')
        f.write(decoder.copy_symbols())
        f.close()

    print("Processing finished")


def send_settings(ip, settings_port, request, symbol_size, symbols, port):
    """ Send settings to server and wait for it to start."""
    settings = {
        'request': request,
        'symbol_size': symbol_size,
        'symbols': symbols,
        'port': port
    }
    message = json.dumps(settings)

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.settimeout(2)
    receive_socket.bind((ip, settings_port+1))

    data = None
    address = ''
    while data is None and address != ip:
        print("Sending configuration.")
        send_socket.sendto(message, (ip, settings_port))
        print("Waiting for confirmation.")
        try:
            data, address = receive_socket.recvfrom(1024)
        except socket.timeout:
            print("timeout.")
            pass
    print("Server acknowledged.")
    print settings


if __name__ == "__main__":
    main()
