#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import sys
import argparse
import json

import udp_unicast


def main():
    """
    UDP Server/Client for sending and receiving random data.
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument(
        '--port-server',
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
        '--ip-server',
        type=str,
        help='ip of the server.',
        default='127.0.0.1')

    client_parser.add_argument(
        '--port_tx',
        type=int,
        help='port used for data transmission.',
        default=41011)

    client_parser.add_argument(
        '--port_rx',
        type=int,
        help='port used for data reception.',
        default=41012)

    client_parser.add_argument(
        '--direction',
        help='direction of data transmission',
        choices=[
            'client_to_server',
            'server_to_client'],
        default='client_to_server')

    client_parser.add_argument(
        '--symbols',
        type=int,
        help='number of symbols in each generation/block.',
        default=16)

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
    settings = vars(args)

    results = None
    if args.role == 'client':
        addr = (settings['ip_server'], settings['port_server'])
        client = udp_unicast.Client(report_results=print_results)
        d = client.run_test(settings)
        d.addCallback(lambda x: udp_unicast.stop())

    else:
        server = udp_unicast.Server(report_results=print_results)
        udp_unicast.reactor.listenUDP(settings['port_server'], server)

    udp_unicast.run()

def print_results(results):
    print("Summary for {} udp unicast: ".format(results['role']))
    for key, value in results.items():
        print("\t{0}: {1}".format(key, value))

if __name__ == "__main__":
    main()


