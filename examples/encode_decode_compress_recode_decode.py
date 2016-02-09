#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2016.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import sys

import kodo


def main():
    """
    Encode decode compress recode decode example.

    This example is similar to the encode recode decode example. But with the
    difference that the data on the recoding node is "compressed" before
    recoding is performed. In order for decoder2 to decode it must also obtain
    information directly from the encoder (as is the case in this example), or
    from another node that hold a recoder for the particlar piece of data.

            +-----------+     +-----------+     +-----------+
            |  encoder  |+--->| decoder1  |+--->|  decoder2 |
            +-----------+     | (recoder) |     +-----------+
                     +        +-----------+        ^
                     |                             |
                     -------------------------------

    This could e.g. be in a P2P type network where an intermidiate node do not
    have enough storage to store all decoded content after it is decoded and
    consumed locally. Rather then choosing which files (decoders) should be
    deleted to free storage, the node could opt to compress one or more of the
    decoders freeing up memory.
    """

    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 42
    symbol_size = 160

    # In the following we will make an encoder/recoder/decoder factory.
    # The factories are used to build actual encoders/recoders/decoders
    encoder_factory = kodo.FullVectorEncoderFactoryBinary8(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    encoder = encoder_factory.build()

    recoder_factory = kodo.FullVectorRecoderFactoryBinary8(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    recoder = recoder_factory.build()

    decoder_factory = kodo.FullVectorDecoderFactoryBinary8(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    decoder1 = decoder_factory.build()
    decoder2 = decoder_factory.build()

    # Create some data to encode. In this case we make a buffer with the same
    # size as the encoder's block size (the max. amount a single encoder can
    # encode) Just for fun - fill the input data with random data
    data_in = os.urandom(encoder.block_size())

    # Assign the data buffer to the encoder
    encoder.set_const_symbols(data_in)

    while not decoder1.is_complete():

        # Encode a packet into the payload buffer
        packet = encoder.write_payload()
        decoder1.read_payload(packet)

    # the capasity that our recoder have in packets
    cache_capasity = 20 # should be less than symbols

    # compress the content at the middle node by feeding the recoder symbols,
    # subsequently the decoder can be deleted
    for i in range(cache_capasity):
        packet = decoder1.write_payload()
        recoder.read_payload(packet)

    # first the recoder sends symbols to decoder2
    for i in range(cache_capasity):
        recoded_packet = recoder.write_payload()
        decoder2.read_payload(recoded_packet)

    # then the remainig packets are received from the encoder
    packets = 0
    while not decoder2.is_complete():
        packet = encoder.write_payload()
        decoder2.read_payload(packet)
        packets += 1

    # The decoder should now be complete, copy the symbols from the decoder
    data_out = decoder2.copy_from_symbols()

    # Check we properly decoded the data
    if data_out == data_in:
        print("Data decoded correctly, received " + str(cache_capasity) + \
              " packets from the recoder and " + str(packets) + \
              " packets from the encoder, for a total of " + \
              str(cache_capasity + packets)) + " packets."
    else:
        print("Unexpected failure to decode please file a bug report :)")
        sys.exit(1)

if __name__ == "__main__":
    main()
