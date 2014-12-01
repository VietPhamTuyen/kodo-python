#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

from __future__ import print_function
from __future__ import division

import kodo

import os
import random
import sys
import threading
import time

try:
    import pygame
    import pygame.locals
    import pygame.gfxdraw
except:
    print("Unable to import pygame module, please make sure it is installed.")
    sys.exit()


class DecodeStateViewer(object):
    """Class for displaying the decoding coefficients"""
    def __init__(self, symbols, screen_size):
        super(DecodeStateViewer, self).__init__()
        self.lock = threading.Lock()
        self.screen = None
        self.running = False
        self.size = (screen_size, screen_size)
        self.padding = 10.0
        self.diameter = (screen_size - self.padding * 2.0) / symbols
        self.thread = threading.Thread(
            name='decode_state_viewer', target=self.__start)

    def start(self):
        """Start a thread which runs the viewer logic"""
        self.thread.start()
        # wait for the game loop to start running
        while not self.running:
            pass

    def __start(self):
        """Start pygame and create a game loop"""
        with self.lock:
            self.running = True
            pygame.init()
            pygame.display.set_caption('Kodo-python DecodeStateViewer')
            self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
        while(self.running):
            with self.lock:
                pygame.display.flip()
        pygame.quit()

    def stop(self):
        """Stops the game loop and joins the thread"""
        self.running = False
        self.thread.join()

    def trace_callback(self, zone, message):
        """Callback to be used with the decoder trace API"""
        # We are only interested in the decoder state.
        if zone != "decoder_state":
            return

        decode_state = []
        for line in message.split('\n'):
            if not line:
                continue
            line = line.split()

            decode_state.append({
                'state': line[1][0],
                'data': [int(i) for i in line[2:]]
            })

        self.show_decode_state(decode_state)

    def show_decode_state(self, decode_state):
        """
        Use the decoding state to print a graphical representation.

        :param decode_state: A list of dictionaries containing the symbol
                             coefficients.
        """
        with self.lock:
            if not self.screen:
                print("viewer not running")
                return

            self.screen.fill((0,)*3)
            y = self.padding + self.diameter / 2
            for symbol in decode_state:
                x = self.padding + self.diameter / 2
                for data in symbol['data']:
                    x += self.diameter
                    if data == 0:
                        continue
                    color = (255,)*3
                    if data != 1:
                        color = (data % 255,) * 3
                    pygame.gfxdraw.circle(
                        self.screen,
                        int(x - self.diameter),
                        int(y),
                        int(self.diameter / 2),
                        color)
                y += self.diameter


def main():
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 64
    symbol_size = 16

    viewer = DecodeStateViewer(symbols, 512)
    viewer.start()

    try:
        # In the following we will make an encoder/decoder factory.
        # The factories are used to build actual encoders/decoders
        encoder_factory = kodo.FullVectorEncoderFactoryBinary8Trace(
            max_symbols=symbols,
            max_symbol_size=symbol_size)

        encoder = encoder_factory.build()

        decoder_factory = kodo.FullVectorDecoderFactoryBinary8Trace(
            max_symbols=symbols,
            max_symbol_size=symbol_size)

        decoder = decoder_factory.build()

        # Create some data to encode. In this case we make a buffer
        # with the same size as the encoder's block size (the max.
        # amount a single encoder can encode)
        # Just for fun - fill the input data with random data
        data_in = os.urandom(encoder.block_size())

        # Set up tracing
        if 'trace' in dir(decoder):
            cb = lambda zone, msg: viewer.trace_callback(zone, msg)
            decoder.trace(cb)

        # Assign the data buffer to the encoder so that we may start
        # to produce encoded symbols from it
        encoder.set_symbols(data_in)
        while not decoder.is_complete():
            # Encode a packet into the payload buffer
            packet = encoder.encode()

            # Here we "simulate" a packet loss of approximately 50%
            # by dropping half of the encoded packets.
            # When running this example you will notice that the initial
            # symbols are received systematically (i.e. uncoded). After
            # sending all symbols once uncoded, the encoder will switch
            # to full coding, in which case you will see the full encoding
            # vectors being sent and received.
            if random.choice([True, False]):
                continue

            # Pass that packet to the decoder
            decoder.decode(packet)

        time.sleep(1)
    finally:
        # What ever happens, make sure we stop the viewer.
        viewer.stop()

    # The decoder is complete, now copy the symbols from the decoder
    data_out = decoder.copy_symbols()
    # Check we properly decoded the data
    if data_out == data_in:
        print("Data decoded correctly")
    else:
        print("Unexpected failure to decode please file a bug report :)")
        sys.exit(1)

if __name__ == "__main__":
    main()
