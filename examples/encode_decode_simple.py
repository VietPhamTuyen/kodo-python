#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import random

import kodo

def main():
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 8
    symbol_size = 160

    # In the following we will make an encoder/decoder factory.
    # The factories are used to build actual encoders/decoders
    encoder_factory = kodo.full_rlnc_encoder_factory_binary(
        symbols, symbol_size)
    encoder = encoder_factory.build()

    decoder_factory = kodo.full_rlnc_decoder_factory_binary(
        symbols, symbol_size)
    decoder = decoder_factory.build()

    # Create some data to encode. In this case we make a buffer
    # with the same size as the encoder's block size (the max.
    # amount a single encoder can encode)
    # Just for fun - fill the input data with random data
    data_in = bytearray(os.urandom(encoder.block_size()))
    data_in = str(data_in)

    # Assign the data buffer to the encoder so that we can
    # produce encoded symbols
    encoder.set_symbols(data_in)

    print("Processing")
    package_number = 0
    while not decoder.is_complete():
        # Generate an encoded packet
        sys.stdout.write("\tEncoding packet {} ...".format(package_number))
        packet = encoder.encode()
        sys.stdout.write(" done!\n")

        # Pass that packet to the decoder
        sys.stdout.write("\tDecoding packet {} ...".format(package_number))
        decoder.decode(packet)
        sys.stdout.write(" done!\n")
        package_number += 1
        print("rank: {}/{}".format(decoder.rank(), decoder.symbols()))

    print("Processing finished")

    # The decoder is complete, now copy the symbols from the decoder
    data_out = decoder.copy_symbols()

    # Check if we properly decoded the data
    print("Checking results")
    if data_out == data_in:
        print("Data decoded correctly")
    else:
        print("Unable to decode please file a bug report :)")

if __name__ == "__main__":
    main()
