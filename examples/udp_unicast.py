#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import socket
import time
import sys
import json
import uuid

import kodo

"""
Functionality for communicating over udp using kodo to ensure reliability.

Both the server and the client can send and receive data

The client can send settings to the server, such that relevant test parameters
can be specified on the client side.

The sender side will send symols until it receives a stop signal on its control
port or it has sent all redundant symbols as specified.

All settings are contained in the 'settings' dictionary which should define the
following keys-values:

settings_port = (int) settings port on the server
server_ip = (string) ip of the server
client_control_port = (int) control port on the client side, used for signaling
server_control_port = (int) control port on the server side, used for signaling
data_port = (int) port used for data transmission
direction = (string) direction of data transmission
symbols = (int) number of symbols in each generation/block
symbol_size = (int) size of each symbol, in bytes
max_redundancy = (float percent) maximum amount of redundancy to be sent
timeout = (float seconds) timeout used for retransmitting various control messages

Both server and client return the 'settings' dictionary with added entries 
describing the process:

    test_id         = (int) 128bit unique test identifier
    client_ip       = (string) ip of the connected client (server only)
    status          = (string) describing if process succeeded or why it failed
    packets_total   = (int) total amount of packets transferred or received 
                      (depending on direction)
    packets_decode  = (int) amount of packets sent / received at decode time.
                      sender may have sent more packets before receiving the ack
    time_start      = (float) timestamp for when the first packet is sent 
    time_decode     = (float) timestamp for when the decode happens (or when 
                      ack is received for sender)
    time_stop       = (float) timestamp for when the last packet is sent or received

"""


def server(args):
    settings = {}

    settings_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    settings_socket.bind(('', args['settings_port']))

    # Wait for settings connections
    print("Server running, listening for connection settings on port " +
          str(args['settings_port']) + ", press ctrl+c to stop.")
    
    data, address = receive(settings_socket, 1024)
    
    try:
        settings = json.loads(data) # may throw exception

        settings['client_ip'] = address[0]
        settings['role'] = 'server'
        if settings['direction'] == 'server_to_client':
            send_data(settings, 'server')
        elif settings['direction'] == 'client_to_server':
            receive_data(settings, 'server')
        else:
            print("Invalid direction.")
            settings['status'] = "Invalid direction "
    except Exception:
        print("Settings message invalid.")
        settings['status'] = 'Settings message invalid'
    finally:
        return settings

def client(settings):
    if settings['symbol_size'] > 65000:
        print("Resulting packets too big, reduce symbol size")
        return

    direction = settings.pop('direction')

    settings['test_id'] = uuid.uuid4().int

    # Note: "server>client>server" matches both cases.
    if 'server_to_client' in direction:
        settings['direction'] = 'server_to_client'
        receive_data(settings, 'client')

    if 'client_to_server' in direction:
        settings['direction'] = 'client_to_server'
        send_data(settings, 'client')
    return settings


def send_data(settings, role):
    """
    Send data to the other node
    """

    # Setup kodo encoder_factory and encoder
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(
        max_symbols=settings['symbols'],
        max_symbol_size=settings['symbol_size'])

    encoder = encoder_factory.build()
    data_in = os.urandom(encoder.block_size())
    encoder.set_symbols(data_in)

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_socket.settimeout(0.00000000000000000001)

    if role == 'client':
        address = (settings['server_ip'], settings['data_port'])
        send_settings(settings)
        control_socket.bind(('', settings['client_control_port']))
    else:  # server
        address = (settings['client_ip'], settings['data_port'])
        server_address = (
            settings['server_ip'],
            settings['client_control_port'])
        control_socket.bind(('', settings['server_control_port']))
        send(send_socket, "settings OK, sending", server_address)

    sent = 0
    start = time.time()
    ack = None
    end = None
    sent_decode = 0
    while sent < settings['symbols'] * settings['max_redundancy'] / 100:
        packet = encoder.write_payload()
        send(send_socket, packet, address)
        sent += 1

        try:
            control_socket.recv(1024)
            if ack is None:
                ack = time.time()
                sent_decode = sent
            break
        except socket.timeout:
            continue

    # if no ack was received we sent all packets
    if end is None:
        end = time.time()
    if ack is None:
        ack = end;

    control_socket.close()

    size = encoder.block_size() * (float(sent) / settings['symbols'])
    seconds = end - start
    
    # save results in settings
    settings['packets_total'] = sent # packets
    settings['packets_decode'] = sent_decode
    settings['status'] = "success"
    settings['time_start'] = start
    settings['time_decode'] = ack
    settings['time_stop'] = end


def receive_data(settings, role):
    """Receive data from the other node"""

    # Setup kodo encoder_factory and decoder
    decoder_factory = kodo.FullVectorDecoderFactoryBinary(
        max_symbols=settings['symbols'],
        max_symbol_size=settings['symbol_size'])

    decoder = decoder_factory.build()

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set receiving sockets
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.settimeout(settings['timeout'])
    data_socket.bind(('', settings['data_port']))

    if role == 'client':
        address = (settings['server_ip'], settings['server_control_port'])
        send_settings(settings)
    else:  # server
        address = (settings['client_ip'], settings['client_control_port'])
        send(send_socket, "settings OK, receiving", address)

    # Decode coded packets
    received = 0
    received_decode = 0
    start = time.time()
    dec = None
    end = None
    while 1:
        try:
            packet = data_socket.recv(settings['symbol_size'] + 100)

            if not decoder.is_complete():
                decoder.read_payload(packet)
                received += 1

            if decoder.is_complete():
                if dec is None:
                    dec = time.time()  # stopping time once
                    received_decode = received
                send(send_socket, "Stop sending", address)

        except socket.timeout:
            break  # no more data arriving

    # in case we did not complete
    if end is None:
        end = time.time()
    if dec is None:
        dec = end

    data_socket.close()

    if not decoder.is_complete():
        settings['status'] = "Decoding failed"
    else:
        settings['status'] = "success"

    size = decoder.block_size() * (float(received) / settings['symbols'])
    seconds = end-start

    settings['packets_total'] = received; # packets
    settings['packets_decode'] = received_decode
    settings['time_start'] = start
    settings['time_decode'] = dec
    settings['time_stop'] = end


def send_settings(settings):
    """
    Send settings to server, block until confirmation received that settings
    was correctly received
    """

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_socket.settimeout(settings['timeout'])
    control_socket.bind(('', settings['client_control_port']))

    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_address = (settings['server_ip'], settings['settings_port'])

    message = json.dumps(settings)
    ack = None
    address = ''
    while ack is None:
        # Send settings
        send(send_socket, message, send_address)
        # Waiting for respons
        try:
            ack, address = receive(control_socket, 1024)  # Server ack
        except socket.timeout:
            print("Timeout - server not responding to settings.")

    control_socket.close()


def send(socket, message, address):
    """
    Send message to address using the provide socket.

    Works for both python2 and python3

    :param socket: The socket to use.
    :param message: The message to send.
    :param address: The address to send to.
    """
    if sys.version_info[0] == 2:
        message = message
    else:
        if isinstance(message, str):
            message = bytes(message, 'utf-8')
    socket.sendto(message, address)


def receive(socket, number_of_bytes):
    """
    Receive an amount of bytes.

    Works for both python2 and python3

    :param socket: The socket to use.
    :param number_of_bytes: The number of bytes to receive.
    """
    data, address = socket.recvfrom(number_of_bytes)
    if sys.version_info[0] == 2:
        return data, address
    else:
        if isinstance(data, bytes):
            return str(data, 'utf-8'), address
