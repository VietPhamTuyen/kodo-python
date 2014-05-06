#! /usr/bin/env python
# encoding: utf-8

import os
import unittest

import kodo


class TestEncodeDecode(unittest.TestCase):

    def test_encode_decode_simple(self):

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
        data_in = bytes(data_in)

        # Assign the data buffer to the encoder so that we can
        # produce encoded symbols
        encoder.set_symbols(data_in)

        while not decoder.is_complete():
            # Generate an encoded packet
            packet = encoder.encode()
            # Decode the encoded packet
            decoder.decode(packet)

        # The decoder is complete, now copy the symbols from the decoder
        data_out = decoder.copy_symbols()

        # Check if we properly decoded the data
        self.assertEqual(data_out, data_in)


def main():
    unittest.main()

if __name__ == "__main__":
    main()
