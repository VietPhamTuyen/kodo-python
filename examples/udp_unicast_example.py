#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import sys
import argparse
import json

import kodo

import udp_unicast


def main():
    """
    UDP Server/Client for sending and receiving random data.
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument(
        '--settings-port',
        type=int,
        help='settings port on the server.',
        default=41001)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use, for testing purposes')

    subparsers = parser.add_subparsers(
        dest='role', help='help for subcommand')

    subparsers.add_parser(
        'server',
        description="UDP server for sending and receiving files.",
        help='Start a server')

    client_parser = subparsers.add_parser(
        'client',
        description="UDP client for sending and receiving files.",
        help='Start a client')

    client_parser.add_argument(
        '--server-ip',
        type=str,
        help='ip of the server.',
        default='127.0.0.1')

    client_parser.add_argument(
        '--client-control-port',
        type=int,
        help='control port on the client side, used for signaling.',
        default=41003)

    client_parser.add_argument(
        '--server-control-port',
        type=int,
        help='control port on the server side, used for signaling.',
        default=41005)

    client_parser.add_argument(
        '--data-port',
        type=int,
        help='port used for data transmission.',
        default=41011)

    client_parser.add_argument(
        '--direction',
        help='direction of data transmission',
        choices=[
            'client_to_server',
            'server_to_client',
            'client_to_server_to_client'],
        default='client_to_server_to_client')

    client_parser.add_argument(
        '--symbols',
        type=int,
        help='number of symbols in each generation/block.',
        default=64)

    client_parser.add_argument(
        '--symbol-size',
        type=int,
        help='size of each symbol, in bytes.',
        default=1400)

    client_parser.add_argument(
        '--max-redundancy',
        type=float,
        help='maximum amount of redundancy to be sent, in percent.',
        default=200)

    client_parser.add_argument(
        '--timeout',
        type=float,
        help='timeout used for various sockets, in seconds.',
        default=1.)

    # We have to use syg.argv for the dry-run parameter, otherwise a subcommand
    # is required.
    if '--dry-run' in sys.argv:
        return

    args = parser.parse_args()

    while True: # Loop until cancelled, e.g. by "ctrl+c"
        results = None
        if args.role == 'client':
            results = udp_unicast.client(args)
        else:
            results = udp_unicast.server(args)

        if(results['status'] != "success"):
            print("{0} failed: {1}".format(args.role, results['status']))
        else:
            print("Summary for {} udp unicast:".format(args.role))
            for key, value in results:
                print("\t{0}: {1}".format(key, value))

        if args.role == 'client':
            break # only run once for client

if __name__ == "__main__":
    main()
