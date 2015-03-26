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
    Perpetual example.

    This Example shows how to use the additional settings and parameters
    supported by the perpetual code.
    """
    # Set the number of symbols (i.e. the generation size in RLNC terminology)
    # and the size of a symbol in bytes
    symbols = 24
    symbol_size = 160

    # Create encoder/decoder factory used to build actual encoders/decoders
    encoder_factory = kodo.PerpetualEncoderFactoryBinary8(symbols, symbol_size)
    encoder = encoder_factory.build()

    decoder_factory = kodo.PerpetualDecoderFactoryBinary8(symbols, symbol_size)
    decoder = decoder_factory.build()

    # The perpetual encoder supports three operation modes;
    #
    # 1) Random pivot mode (default)
    # 2) Pseudo systematic
    # 3) Pre-charging
    #
    # See src/kodo/rlnc/perpetual_generator.hpp for a description of the
    # operation in the different modes. The operation mode is set in the
    # following. Note that if both pre-charging and pseudo-systematic is
    # enabled, pre-charging takes precedence.

    # Enable the pseudo-systematic operation mode - faster
    encoder.set_pseudo_systematic(True)

    # Enable the pre-charing operation mode - even faster
    # encoder.set_pre_charging(True);

    print("Pseudo-systematic is {}\nPre-charging is {}".format(
        encoder.pseudo_systematic(),
        encoder.pre_charging()))

    # The width of the perpetual code can be set either as a number of symbols
    # using set_width(), or as a ratio of the generation size using
    # set_width_ratio().
    #
    # The default width is set to 10% of the generation size.
    print("The width defaulted to: {}".format(encoder.width()))
    encoder.set_width(6)
    print("The width was set to: {}".format(encoder.width()))
    encoder.set_width_ratio(0.2)
    print("The width ratio was set to: {}".format(encoder.width_ratio()))

    # Create some data to encode. In this case we make a buffer
    # with the same size as the encoder's block size (the max.
    # amount a single encoder can encode)
    # Just for fun - fill the input data with random data
    data_in = os.urandom(encoder.block_size())

    # Assign the data buffer to the encoder so that we can
    # produce encoded symbols
    encoder.set_symbols(data_in)

    while not decoder.is_complete():
        # Encode a packet into the payload buffer
        payload = encoder.write_payload()

        # Pass that packet to the decoder
        decoder.read_payload(payload)

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
