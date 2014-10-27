#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import argparse
import socket
import json
import kodo
import os

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
        if settings['direction'] == 'download':
            run_download(settings)
        elif settings['direction'] == 'upload':
            run_upload(settings)

def run_upload(settings):
    pass

def run_download(settings):
    # In the following we will make an encoder factory.
    # The factories are used to build actual encoder
    encoder_factory = kodo.full_rlnc_encoder_factory_binary(settings['symbols'],
                                                            settings['symbol_size'])
    encoder = encoder_factory.build()
    data_in = os.urandom(encoder.block_size())
    encoder.set_symbols(data_in)

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (settings['ip'], settings['port'])

    for i in range(settings['symbols'] + settings['redundant_symbols']):
        packet = encoder.encode()
        send_socket.sendto(packet, address)

    print("Sent " + str(i) + " packets")
if __name__ == "__main__":
    main()
