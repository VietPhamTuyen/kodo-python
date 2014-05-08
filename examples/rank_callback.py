#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing
"""
 @example rank_callback.cpp

 It may be that we want a function to be called on some event within the
 decoder. This can be done using callback functions. The following example
 illustrates how this can be done by adding the rank_callback_decoder layer to
 the decoder stack and how the rank changed event can be handled in three
 different ways. Other callback layers could also be used instead of the rank
 callback layer provided that they are added at the correct position in the
 stack.
"""

import kodo
import threading
import os


# Global function as callback handler
def rank_changed_event(rank):
    print("Rank changed to " << rank)

lock = threading.Lock()


# Global function as callback handler with pointer to the calling decoder
# as parameter
def rank_changed_event2(decoder, rank):
    # Lock decoder pointer so that it cannot be freed until we are done
    with lock:
        print("Rank changed to {}/{}".format(rank, decoder.symbols()))


# Some class
class callback_handler(object):
    def __init__(self):
        super(callback_handler, self).__init__()

    # Member function as callback handler
    def rank_changed_event3(rank):
        print("Rank changed to " << rank)


def main():
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 8
    symbol_size = 160

    # In the following we will make an encoder/decoder factory.
    # The factories are used to build actual encoders/decoders
    encoder_factory = kodo.full_rlnc_encoder_factory_binary(symbols,
                                                            symbol_size)
    encoder = encoder_factory.build()

    decoder_factory = kodo.full_rlnc_decoder_factory_binary(symbols,
                                                            symbol_size)
    decoder = decoder_factory.build()

    # The following three code blocks illustrates three common ways that
    # a callback function may be set and used.
    # You may comment in the code block that you want to test.

    # Callback option 1:
    # Set callback for decoder to be a global function

    # Set callback handler
    decoder.set_rank_changed_callback(rank_changed_event)

    # Callback option 2:
    # Set callback for decoder to be a global function that takes a
    # pointer to the calling decoder as an additional argument

    decoder.set_rank_changed_callback(
        lambda x: rank_changed_event2(decoder, x))

    # Callback option 3:
    # Set callback for decoder to be a member function of some class
    # This method is using lambda expressions which is not yet available in
    # all compilers.

    # Declare a class to handle callback
    handler = callback_handler()

    # Set callback handler
    decoder.set_rank_changed_callback(
        lambda x: handler.rank_changed_event3(x)
    )

    # Just for fun - fill the data with random data
    data_in = bytearray(os.urandom(encoder.block_size()))
    data_in = bytes(data_in)

    # Assign the data buffer to the encoder so that we may start
    # to produce encoded symbols from it
    encoder.set_symbols(data_in)

    while not decoder.is_complete():
        # Encode a packet into the payload buffer
        packet = encoder.encode()

        # Pass that packet to the decoder
        decoder.decode(packet)

    # The decoder is complete, now copy the symbols from the decoder
    data_out = decoder.copy_symbols()

    # Check we properly decoded the data
    if data_out == data_in:
        print("Data decoded correctly")
    else:
        print("Unexpected failure to decode please file a bug report :)")

if __name__ == "__main__":
    main()
