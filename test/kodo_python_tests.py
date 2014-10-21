#! /usr/bin/env python
# encoding: utf-8

import os
import unittest

import kodo

test_sets = [
    # Full RLNC
    (kodo.full_rlnc_encoder_factory_binary,
     kodo.full_rlnc_decoder_factory_binary),
    (kodo.full_rlnc_encoder_factory_binary4,
     kodo.full_rlnc_decoder_factory_binary4),
    (kodo.full_rlnc_encoder_factory_binary8,
     kodo.full_rlnc_decoder_factory_binary8),
    (kodo.full_rlnc_encoder_factory_binary16,
     kodo.full_rlnc_decoder_factory_binary16),
    # Full RLNC Trace
    (kodo.full_rlnc_encoder_factory_binary_trace,
     kodo.full_rlnc_decoder_factory_binary_trace),
    (kodo.full_rlnc_encoder_factory_binary4_trace,
     kodo.full_rlnc_decoder_factory_binary4_trace),
    (kodo.full_rlnc_encoder_factory_binary8_trace,
     kodo.full_rlnc_decoder_factory_binary8_trace),
    (kodo.full_rlnc_encoder_factory_binary16_trace,
     kodo.full_rlnc_decoder_factory_binary16_trace),

    # Sparse Full RLNC
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary,
     kodo.full_rlnc_decoder_factory_binary),
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary4,
     kodo.full_rlnc_decoder_factory_binary4),
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary8,
     kodo.full_rlnc_decoder_factory_binary8),
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary16,
     kodo.full_rlnc_decoder_factory_binary16),
    # Sparse Full RLNC Trace
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary_trace,
     kodo.full_rlnc_decoder_factory_binary_trace),
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary4_trace,
     kodo.full_rlnc_decoder_factory_binary4_trace),
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary8_trace,
     kodo.full_rlnc_decoder_factory_binary8_trace),
    (kodo.shallow_sparse_full_rlnc_encoder_factory_binary16_trace,
     kodo.full_rlnc_decoder_factory_binary16_trace),

    # On The Fly
    (kodo.on_the_fly_encoder_factory_binary,
     kodo.on_the_fly_decoder_factory_binary),
    (kodo.on_the_fly_encoder_factory_binary4,
     kodo.on_the_fly_decoder_factory_binary4),
    (kodo.on_the_fly_encoder_factory_binary8,
     kodo.on_the_fly_decoder_factory_binary8),
    (kodo.on_the_fly_encoder_factory_binary16,
     kodo.on_the_fly_decoder_factory_binary16),
    # On The Fly Trace
    (kodo.on_the_fly_encoder_factory_binary_trace,
     kodo.on_the_fly_decoder_factory_binary_trace),
    (kodo.on_the_fly_encoder_factory_binary4_trace,
     kodo.on_the_fly_decoder_factory_binary4_trace),
    (kodo.on_the_fly_encoder_factory_binary8_trace,
     kodo.on_the_fly_decoder_factory_binary8_trace),
    (kodo.on_the_fly_encoder_factory_binary16_trace,
     kodo.on_the_fly_decoder_factory_binary16_trace),

    # Sliding Window
    (kodo.sliding_window_encoder_factory_binary,
     kodo.sliding_window_decoder_factory_binary),
    (kodo.sliding_window_encoder_factory_binary4,
     kodo.sliding_window_decoder_factory_binary4),
    (kodo.sliding_window_encoder_factory_binary8,
     kodo.sliding_window_decoder_factory_binary8),
    (kodo.sliding_window_encoder_factory_binary16,
     kodo.sliding_window_decoder_factory_binary16),
    # Sliding Window Trace
    (kodo.sliding_window_encoder_factory_binary_trace,
     kodo.sliding_window_decoder_factory_binary_trace),
    (kodo.sliding_window_encoder_factory_binary4_trace,
     kodo.sliding_window_decoder_factory_binary4_trace),
    (kodo.sliding_window_encoder_factory_binary8_trace,
     kodo.sliding_window_decoder_factory_binary8_trace),
    (kodo.sliding_window_encoder_factory_binary16_trace,
     kodo.sliding_window_decoder_factory_binary16_trace),
]


class TestEncodeDecode(unittest.TestCase):

    def test_all(self):
        for test_set in test_sets:
            self.encode_decode_simple(*test_set)

    def encode_decode_simple(self, encoder_factory, decoder_factory):
        # Set the number of symbols (i.e. the generation size in RLNC
        # terminology) and the size of a symbol in bytes
        symbols = 8
        symbol_size = 160

        # In the following we will make an encoder/decoder factory.
        # The factories are used to build actual encoders/decoders
        encoder_factory = encoder_factory(symbols, symbol_size)
        encoder = encoder_factory.build()

        decoder_factory = decoder_factory(symbols, symbol_size)
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
