#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

"""
 @example sliding_window.cpp

 This example shows how to use sliding window encoder and decoder
 stacks. The sliding window is special in that it does not require
 that all symbols are available at the encoder before encoding can
 start. In addition it uses feedback beteen the decoder and encoder
 such that symbols that have already been received at the decoder
 are not included in the encoding again (saving computations).
"""

def main():
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 42
    symbol_size = 160

    # Typdefs for the encoder/decoder type we wish to use
    typedef kodo::sliding_window_encoder<fifi::binary8> rlnc_encoder
    typedef kodo::sliding_window_decoder<fifi::binary8> rlnc_decoder

    # In the following we will make an encoder/decoder factory.
    # The factories are used to build actual encoders/decoders
    rlnc_encoder::factory encoder_factory(symbols, symbol_size)
    auto encoder = encoder_factory.build()

    rlnc_decoder::factory decoder_factory(symbols, symbol_size)
    auto decoder = decoder_factory.build()

    # Allocate some storage for a "payload" the payload is what we would
    # eventually send over a network
    std::vector<uint8_t> payload(encoder.payload_size())

    # Allocate some data to encode. In this case we make a buffer
    # with the same size as the encoder's block size (the max.
    # amount a single encoder can encode)
    std::vector<uint8_t> data_in(encoder.block_size())

    # The sliding window codec stacks uses feedback to optimize the
    # coding. Using the following we can allocate a buffer for the
    # feedback buffer.
    std::vector<uint8_t> feedback(encoder.feedback_size())

    # Just for fun - fill the data with random data
    std::generate(data_in.begin(), data_in.end(), rand)

    # Lets split the data into symbols and feed the encoder one symbol
    # at a time
    auto symbol_storage =
        sak::split_storage(sak::storage(data_in), symbol_size)

    while( !decoder.is_complete() )

        # Encode a packet into the payload buffer
        encoder.encode( &payload[0] )

        # Send the data to the decoders, here we just for fun
        # simulate that we are loosing 50% of the packets
        if(rand() % 2)
           continue

        # Packet got through - pass that packet to the decoder
        decoder.decode( &payload[0] )

        # Randomly choose to insert a symbol
        if((rand() % 2) && (encoder.rank() < symbols))

            # For an encoder the rank specifies the number of symbols
            # it has available for encoding
            uint32_t rank = encoder.rank()

            encoder.set_symbol(rank, symbol_storage[rank])


        # Transmit the feedback
        decoder.write_feedback(&feedback[0])

        # Simulate loss of feedback
        if(rand() % 2)
            continue

        encoder.read_feedback(&feedback[0])


    # The decoder is complete, now copy the symbols from the decoder
    std::vector<uint8_t> data_out(decoder.block_size())
    decoder.copy_symbols(sak::storage(data_out))

    # Check we properly decoded the data
    if (std::equal(data_out.begin(), data_out.end(), data_in.begin()))

        print("Data decoded correctly")

    else

        print("Unexpected failure to decode "
                  << "please file a bug report :)")




