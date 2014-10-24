#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import argparse
import socket
import json
import kodo
import os


def main():
    return
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

    receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_socket.bind(('', args.settings_port))

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Wait for connections
    print("running server, press ctrl+c to stop.")
    while True:
        data, address = receive_socket.recvfrom(1024)
        try:
            settings = json.loads(data)
        except Exception:
            print("Message not understood.")
            continue
        send_socket.sendto("OK", (address[0], args.settings_port+1))
        print settings
        if settings['request'] == 'download':
            run_download_simulation(ip=address[0], **settings)
        elif settings['request'] == 'upload':
            run_upload_simulation(ip=address[0], **settings)


def run_upload_simulation(ip, symbols, request, symbol_size, port):
    pass


def run_download_simulation(ip, symbols, request, symbol_size, port):
    # In the following we will make an encoder factory.
    # The factories are used to build actual encoder
    encoder_factory = kodo.full_rlnc_encoder_factory_binary(symbols,
                                                            symbol_size)
    encoder = encoder_factory.build()
    data_in = os.urandom(encoder.block_size())
    encoder.set_symbols(data_in)

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (ip, port)

    while encoder.rank() == encoder.symbols():
        packet = encoder.encode()
        print("Packet encoded!")

        # Send the packet.
        send_socket.sendto(packet, address)

    print("Processing finished")
if __name__ == "__main__":
    main()
