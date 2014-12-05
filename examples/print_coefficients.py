#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

from __future__ import print_function
from __future__ import division

import kodo
import kodo_helpers

import os
import random
import sys
import time


def main():

    # Setup canvas and viewer
    size = 1024
    canvas = kodo_helpers.CanvasScreenEngine(size, size)
    viewer = kodo_helpers.DecodeStateViewer(
        size=size,
        canvas=canvas)

    canvas.start()
    try:
        # Set the number of symbols (i.e. the generation size in RLNC
        # terminology) and the size of a symbol in bytes
        symbols = 256
        symbol_size = 16

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

        # Set up tracing callback
        if 'trace' in dir(decoder):
            callback = lambda zone, msg: viewer.trace_callback(zone, msg)
            decoder.trace(callback)

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
        canvas.stop()

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
