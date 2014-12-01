#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import random
import sys

import kodo


def main():
    """An example of how to use the trace functionality."""
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 8
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

    # Setup tracing
    if 'trace' in dir(encoder):
        encoder.trace()

    if 'trace' in dir(decoder):
        def callback_function(zone, message):
            if zone in ["decoder_state", "input_symbol_coefficients"]:
                print("{}:".format(zone))
                print(message)

        decoder.trace(callback_function)

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
