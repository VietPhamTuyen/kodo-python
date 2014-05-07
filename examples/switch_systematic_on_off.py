#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

#include <kodo/rlnc/full_vector_codes.hpp>
#include <kodo/set_systematic_on.hpp>
#include <kodo/set_systematic_off.hpp>
#include <kodo/is_systematic_on.hpp>

/// @example switch_systematic_on_off.cpp
///
/// This example shows how to enable or disable systematic coding for
/// coding stacks that support it.
/// Systematic coding is used to reduce the amount of work done by an
/// encoder and a decoder. This is achieved by initially sending all
/// symbols which has not previously been sent uncoded. Kodo allows this
/// feature to be optionally turn of or off.

int main()
{
    // Set the number of symbols (i.e. the generation size in RLNC
    // terminology) and the size of a symbol in bytes
    uint32_t symbols = 16;
    uint32_t symbol_size = 160;

    // Typdefs for the encoder/decoder type we wish to use
    typedef kodo::full_rlnc_encoder<fifi::binary8> rlnc_encoder;
    typedef kodo::full_rlnc_decoder<fifi::binary8> rlnc_decoder;

    // In the following we will make an encoder/decoder factory.
    // The factories are used to build actual encoders/decoders
    rlnc_encoder::factory encoder_factory(symbols, symbol_size);
    auto encoder = encoder_factory.build();

    rlnc_decoder::factory decoder_factory(symbols, symbol_size);
    auto decoder = decoder_factory.build();

    // Allocate some storage for a "payload" the payload is what we would
    // eventually send over a network
    std::vector<uint8_t> payload(encoder->payload_size());

    // Allocate some data to encode. In this case we make a buffer
    // with the same size as the encoder's block size (the max.
    // amount a single encoder can encode)
    std::vector<uint8_t> data_in(encoder->block_size());

    // Just for fun - fill the data with random data
    for(auto &e: data_in)
        e = rand() % 256;

    // Assign the data buffer to the encoder so that we may start
    // to produce encoded symbols from it
    encoder->set_symbols(sak::storage(data_in));

    std::cout << "Starting encoding / decoding" << std::endl;

    while( !decoder->is_complete() )
    {
        // If the chosen codec stack supports systematic coding
        if(kodo::has_systematic_encoder<rlnc_encoder>::value)
        {
            // With 50% probability toggle systematic
            if((rand() % 2) == 0)
            {
                if(kodo::is_systematic_on(encoder))
                {
                    std::cout << "Turning systematic OFF" << std::endl;
                    kodo::set_systematic_off(encoder);
                }
                else
                {
                    std::cout << "Turning systematic ON" << std::endl;
                    kodo::set_systematic_on(encoder);
                }
            }
        }

        // Encode a packet into the payload buffer
        encoder->encode( &payload[0] );

        if((rand() % 2) == 0)
        {
            std::cout << "Drop packet" << std::endl;
            continue;
        }

        // Pass that packet to the decoder
        decoder->decode( &payload[0] );

        std::cout << "Rank of decoder " << decoder->rank() << std::endl;

        // Symbols that were received in the systematic phase correspond
        // to the original source symbols and are therefore marked as
        // decoded
        std::cout << "Symbols decoded "
                  << decoder->symbols_decoded() << std::endl;
    }

    // The decoder is complete, now copy the symbols from the decoder
    std::vector<uint8_t> data_out(decoder->block_size());
    decoder->copy_symbols(sak::storage(data_out));

    // Check we properly decoded the data
    if (std::equal(data_out.begin(), data_out.end(), data_in.begin()))
    {
        std::cout << "Data decoded correctly" << std::endl;
    }
    else
    {
        std::cout << "Unexpected failure to decode "
                  << "please file a bug report :)" << std::endl;
    }
}

