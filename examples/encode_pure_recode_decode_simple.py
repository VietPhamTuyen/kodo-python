#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2015.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import sys

import kodo


def main():
    """
    Encode pure recode decode example.

    This example is very similar to encode_recode_decode_simple.py.
    The only difference is that this example uses a pure recoder instead of
    a decoder acting as a recoder. By "pure", we mean that the recoder will not
    decode the incoming data, it will only re-encode it.
    This example shows how to use an encoder, recoder, and decoder to
    simulate a simple relay network as shown below. For simplicity,
    we have error free links, i.e. no data packets are lost when being
    sent from encoder to recoder to decoder:

            +-----------+      +-----------+      +------------+
            |  encoder  |+---->| recoder   |+---->|  decoder   |
            +-----------+      +-----------+      +------------+

    For a more elaborate description of recoding, please see the
    description of encode_recode_decode_simple.py.
    """
# Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 42
    symbol_size = 160

    # In the following we will make an encoder/decoder factory.
    # The factories are used to build actual encoders/decoders
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    encoder = encoder_factory.build()

    # recoder_factory = kodo.FullVectorRecoderFactoryBinary(
    #     max_symbols=symbols,
    #     max_symbol_size=symbol_size)

    # recoder = recoder_factory.build()

    decoder_factory = kodo.FullVectorDecoderFactoryBinary(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    decoder = decoder_factory.build()

    # Create some data to encode. In this case we make a buffer
    # with the same size as the encoder's block size (the max.
    # amount a single encoder can encode)
    # Just for fun - fill the input data with random data
    data_in = os.urandom(encoder.block_size())

    # Assign the data buffer to the encoder so that we may start
    # to produce encoded symbols from it
    encoder.set_const_symbols(data_in)

    while not decoder.is_complete():

        # Encode a packet into the payload buffer
        packet = encoder.write_payload()

        # Pass that packet to decoder1
        # recoder.read_payload(packet)

        # Now produce a new recoded packet from the current
        # decoding buffer, and place it into the payload buffer
        # packet = recoder.write_payload()

        # Pass the recoded packet to decoder2
        decoder.read_payload(packet)

    # The decoder should now be complete,
    # copy the symbols from the decoders
    data_out = decoder.copy_from_symbols()

    # Check we properly decoded the data
    if data_out == data_in:
        print("Data decoded correctly")
    else:
        print("Unexpected failure to decode please file a bug report :)")
        sys.exit(1)

if __name__ == "__main__":
    main()
