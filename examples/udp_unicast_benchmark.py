#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import sys

try:
    import argparse
    import json
    import itertools
    import time
    import datetime
    from twisted.internet.defer import inlineCallbacks

    import udp_unicast
    import udp_unicast_logging
except ImportError as err:
    print("Error: Could not import module '{0}'. Please install '{0}'.".format(
          err.name))
    sys.exit()


def get_settings(parameter_space, repeat=1):
    """
    Returns a iterator that yelds all possible combinations in a dictionary of
    parameter, where each parameter is given a list of possible values.

    the parameter space is repeated "repeat" times

    Example:
    {"p1": [1,2], "p2": [3,4], "p3": [5]}

    return and iterator the yelds the following:
    {"p1": [1], "p2": [3], "p3": [5]}
    {"p1": [1], "p2": [4], "p3": [5]}
    {"p1": [2], "p2": [3], "p3": [5]}
    {"p1": [2], "p2": [4], "p3": [5]}
    """

    l = list()

    for key, value in parameter_space.iteritems():
        l.append(list(itertools.product([key], value)))

    settings = iter("")

    for r in range(repeat):
        settings = itertools.chain(settings, itertools.product(*l))

    return settings


def log(results, logname, logtype):
    # add date and time to results
    results['date'] = str(datetime.datetime.now())
    if logtype == 'xml':
        udp_unicast_logging.save_as_xml(results, logname)
    elif logtype == 'csv':
        udp_unicast_logging.save_as_csv(results, logname)
    elif logtype == 'yaml':
        udp_unicast_logging.save_as_yaml(results, logname)
    elif logtype == 'json':
        udp_unicast_logging.save_as_json(results, logname)
    else:
        print("Unknown log format: " + logtype)


@inlineCallbacks
def queue_clients(parameters_list, logname, log_format):
    """
    Async function that ensures clients are run sequentially. Thread control
    is handed over after each yield, until client.on_finish as completed
    """
    logname = "client_benchmark_log"
    client = udp_unicast.Client(report_results=lambda x: log(x, logname,
                                                             log_format))
    for parameters in parameters_list:
        p = dict(parameters)
        yield client.run_test(p)
        # completed_test contains the ID of the completed test case

        # sleep for a bit to ensure that sockets have time to close
        time.sleep(1)

    # stop the event loop here
    udp_unicast.stop()


def main():
    """
    UDP Server/Client benchmarking of a defined parameter space
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use, for testing purposes')

    parser.add_argument('--log-format',
                        dest='log_format',
                        type=str,
                        help="one of the following: "
                        "'json', 'yaml', 'csv', 'xml'. ",
                        default='json')

    subparsers = parser.add_subparsers(
        dest='role', help='help for subcommand')

    server_parser = subparsers.add_parser(
        'server',
        description="UDP server for sending and receiving files.",
        help='Start a server')

    server_parser.add_argument(
        '--port_server',
        type=int,
        help='settings port on the server.',
        default=41001)

    client_parser = subparsers.add_parser(
        'client',
        description="UDP client for sending and receiving files.",
        help='Start a client')

    client_parser.add_argument(
        '--parameters-file',
        type=str,
        help='file containing test parameters',
        default='parameters.json')

    client_parser.add_argument(
        '--runs',
        type=int,
        help='number of times to run through the parameter space',
        default=1)

    client_parser.add_argument(
        '--print-parameters-used',
        type=bool,
        help='Print the parameters to be used instead of testing',
        default=False)

    # We have to use syg.argv for the dry-run parameter, otherwise a subcommand
    # is required.
    if '--dry-run' in sys.argv:
        return

    args = parser.parse_args()

    if args.role == 'client':

        parameter_space = json.load(open(args.parameters_file))

        # for run in range(args.runs):
        logname = "client_benchmark_log"
        settings = get_settings(parameter_space, args.runs)

        if args.print_parameters_used:
            for setting in settings:
                print(dict(setting))
        else:
            udp_unicast.reactor.callLater(0, queue_clients,
                                          settings, logname,
                                          args.log_format)
    else:  # server
        settings = vars(args)
        log_format = settings.pop('log_format')
        logname = 'server_benchmark_log'

        print("Starting server on port " + str(settings['port_server']) +
              ", press ctrl+c to stop.")

        server = udp_unicast.Server(
                    report_results=lambda x: log(x, logname, log_format))
        udp_unicast.reactor.listenUDP(settings['port_server'], server)

    udp_unicast.run()


if __name__ == "__main__":
    main()
