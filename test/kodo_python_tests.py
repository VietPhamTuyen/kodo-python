#! /usr/bin/env python
# encoding: utf-8

import os
import unittest

import kodo

test_sets = [
    # Full RLNC
    (kodo.FullVectorEncoderFactoryBinary,
     kodo.FullVectorDecoderFactoryBinary),
    (kodo.FullVectorEncoderFactoryBinary4,
     kodo.FullVectorDecoderFactoryBinary4),
    (kodo.FullVectorEncoderFactoryBinary8,
     kodo.FullVectorDecoderFactoryBinary8),
    (kodo.FullVectorEncoderFactoryBinary16,
     kodo.FullVectorDecoderFactoryBinary16),
    # Full RLNC Trace
    (kodo.FullVectorEncoderFactoryBinaryTrace,
     kodo.FullVectorDecoderFactoryBinaryTrace),
    (kodo.FullVectorEncoderFactoryBinary4Trace,
     kodo.FullVectorDecoderFactoryBinary4Trace),
    (kodo.FullVectorEncoderFactoryBinary8Trace,
     kodo.FullVectorDecoderFactoryBinary8Trace),
    (kodo.FullVectorEncoderFactoryBinary16Trace,
     kodo.FullVectorDecoderFactoryBinary16Trace),

    # Sparse Full RLNC
    (kodo.SparseFullVectorEncoderFactoryBinary,
     kodo.FullVectorDecoderFactoryBinary),
    (kodo.SparseFullVectorEncoderFactoryBinary4,
     kodo.FullVectorDecoderFactoryBinary4),
    (kodo.SparseFullVectorEncoderFactoryBinary8,
     kodo.FullVectorDecoderFactoryBinary8),
    (kodo.SparseFullVectorEncoderFactoryBinary16,
     kodo.FullVectorDecoderFactoryBinary16),
    # Sparse Full RLNC Trace
    (kodo.SparseFullVectorEncoderFactoryBinaryTrace,
     kodo.FullVectorDecoderFactoryBinaryTrace),
    (kodo.SparseFullVectorEncoderFactoryBinary4Trace,
     kodo.FullVectorDecoderFactoryBinary4Trace),
    (kodo.SparseFullVectorEncoderFactoryBinary8Trace,
     kodo.FullVectorDecoderFactoryBinary8Trace),
    (kodo.SparseFullVectorEncoderFactoryBinary16Trace,
     kodo.FullVectorDecoderFactoryBinary16Trace),

    # On The Fly
    (kodo.OnTheFlyEncoderFactoryBinary,
     kodo.OnTheFlyDecoderFactoryBinary),
    (kodo.OnTheFlyEncoderFactoryBinary4,
     kodo.OnTheFlyDecoderFactoryBinary4),
    (kodo.OnTheFlyEncoderFactoryBinary8,
     kodo.OnTheFlyDecoderFactoryBinary8),
    (kodo.OnTheFlyEncoderFactoryBinary16,
     kodo.OnTheFlyDecoderFactoryBinary16),
    # On The Fly Trace
    (kodo.OnTheFlyEncoderFactoryBinaryTrace,
     kodo.OnTheFlyDecoderFactoryBinaryTrace),
    (kodo.OnTheFlyEncoderFactoryBinary4Trace,
     kodo.OnTheFlyDecoderFactoryBinary4Trace),
    (kodo.OnTheFlyEncoderFactoryBinary8Trace,
     kodo.OnTheFlyDecoderFactoryBinary8Trace),
    (kodo.OnTheFlyEncoderFactoryBinary16Trace,
     kodo.OnTheFlyDecoderFactoryBinary16Trace),

    # Sliding Window
    (kodo.SlidingWindowEncoderFactoryBinary,
     kodo.SlidingWindowDecoderFactoryBinary),
    (kodo.SlidingWindowEncoderFactoryBinary4,
     kodo.SlidingWindowDecoderFactoryBinary4),
    (kodo.SlidingWindowEncoderFactoryBinary8,
     kodo.SlidingWindowDecoderFactoryBinary8),
    (kodo.SlidingWindowEncoderFactoryBinary16,
     kodo.SlidingWindowDecoderFactoryBinary16),
    # Sliding Window Trace
    (kodo.SlidingWindowEncoderFactoryBinaryTrace,
     kodo.SlidingWindowDecoderFactoryBinaryTrace),
    (kodo.SlidingWindowEncoderFactoryBinary4Trace,
     kodo.SlidingWindowDecoderFactoryBinary4Trace),
    (kodo.SlidingWindowEncoderFactoryBinary8Trace,
     kodo.SlidingWindowDecoderFactoryBinary8Trace),
    (kodo.SlidingWindowEncoderFactoryBinary16Trace,
     kodo.SlidingWindowDecoderFactoryBinary16Trace),
]


class TestEncodeDecode(unittest.TestCase):

    def test_all(self):
        for test_set in test_sets:
            self.encode_decode_simple(*test_set)

    def encode_decode_simple(self, EncoderFactory, DecoderFactory):
        # Set the number of symbols (i.e. the generation size in RLNC
        # terminology) and the size of a symbol in bytes
        symbols = 8
        symbol_size = 160

        # In the following we will make an encoder/decoder factory.
        # The factories are used to build actual encoders/decoders
        encoder_factory = EncoderFactory(symbols, symbol_size)
        encoder = encoder_factory.build()

        decoder_factory = DecoderFactory(symbols, symbol_size)
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
