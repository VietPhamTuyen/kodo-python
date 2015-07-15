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
    max_symbols = 4
    max_symbol_size = 32

    encoder_factory = kodo.FullVectorEncoderFactoryBinary(
        max_symbols=max_symbols,
        max_symbol_size=max_symbol_size)


    encoder = encoder_factory.build()

    data_in = (
        "The size of this data is exactly 128 bytes "
        "which means it will fit perfectly in a single generation. "
        "That is very lucky, indeed!"
    )

    encoder.set_symbols(data_in)
    decoder_factory = kodo.FullVectorDecoderFactoryBinary(
        max_symbols, max_symbol_size)
    decoder = decoder_factory.build()
    def callback_function(zone, message):
        if zone in ["decoder_state", "input_symbol_coefficients"]:
            print("{}:".format(zone))
            print(message)

    decoder.trace(callback_function)

    packet = encoder.write_payload()
    encoder.write_payload()
    encoder.write_payload()
    encoder.write_payload()
    packet2 = encoder.write_payload()
    decoder.read_payload(packet)
    print(decoder.copy_symbols().replace('\x00', '_'))
    print(
        "rank: {}\n"
        "symbols_uncoded: {}".format(
            decoder.rank(),
            decoder.symbols_uncoded()
        )
    )
    decoder.read_payload(packet2)
    print("")
    print(decoder.copy_symbols().replace('\x00', '_'))
    print(
        "rank: {}\n"
        "symbols_uncoded: {}".format(
            decoder.rank(),
            decoder.symbols_uncoded()
        )
    )

if __name__ == "__main__":
    main()
