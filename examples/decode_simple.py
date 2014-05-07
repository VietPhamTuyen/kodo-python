#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

"""
 @example decode_simple.cpp

 It may be that we want to implement a new decoding algorithm in Kodo or
 simply just test an existing decoding implementation. In that case, it may
 be preferred to reuse functionalities in already existing layers while
 stripping functionalities that are not required to keep it simple.

 This example illustrates how the operations of a RLNC decoder can be
 tested in a binary field without introducing unnecessary complexity.
 To keep it simple, we want to enter the data to be decoded ourself instead
 of relying on an encoder to generate the data.
 The functionalities in layers above the "Codec API" is therefore not
 required and has been stripped from the stack. However, the layers below
 the "Codec API" has been kept as they provide functionalities that are
 required.
"""

import kodo


def main():

    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the number of elements in a symbol
    symbols = 3

    # 1 byte can store 8 finite field elements per symbol
    symbol_size = 1

    # Get the size, in bytes, of a coefficient vector
    coefficients_size = 1

    # In the following we will make an decoder factory.
    # The factory is used to build actual decoders
    decoder_factory = kodo.full_rlnc_decoder_factory_binary(
        symbols, symbol_size)

    decoder = decoder_factory.build()

    # To illustrate decoding, random data has been filled into the
    # matrices below. It is crucial that the equation below is correct
    # if the purpose is to test if the decoder decodes correctly as this
    # example evaluates in the end of the example.
    #
    # For additional information, please see the article
    #
    #   Christina Fragouli, Jean-Yves Le Boudec, and Jörg Widmer.
    #   Network Coding: An Instant Primer.
    #   SIGCOMM Comput. Commun. Rev., 36(1):63-68, January 2006.
    #
    # from which the notation in the example is based on.
    #
    #
    #
    # original_symbols (M):    Symbols we expect to obtain from decoding
    #                          encoded_symbols using the symbol_coefficients.
    # symbol_coefficients (G): Coefficients used to encode/decode between
    #                          original_symbols and encoded_symbols.
    # encoded_symbols (X):     Symbols that has been encoded from
    #                          original_symbols using the symbol_coefficients.
    #
    #
    #                          X = G M
    #
    #                        X^j = sum_{i=1}^{n} g_i^j M^i
    #
    #                |   X^1   |   | g^1_1 g^1_2 g^1_3 | |   M^1   |
    #                |   X^2   | = | g^2_1 g^2_2 g^2_3 | |   M^2   |
    #                |   X^3   |   | g^3_1 g^3_2 g^3_3 | |   M^3   |
    #
    #       | encoded symbol 1 |   | encoding vect 1 | | original symbol 1 |
    #       | encoded symbol 2 | = | encoding vect 2 | | original symbol 2 |
    #       | encoded symbol 3 |   | encoding vect 3 | | original symbol 3 |
    #
    #        | 0 1 0 1 1 1 0 0 |   | 0 1 0 | | 1 1 1 0 1 1 0 1 |
    #        | 1 0 1 1 0 0 0 1 | = | 1 1 0 | | 0 1 0 1 1 1 0 0 |
    #        | 0 1 1 0 1 0 1 1 |   | 1 0 1 | | 1 0 0 0 0 1 1 0 |
    #
    # From the above matrix, the first encoded symbol is just the second
    # original symbol M_2. The second encoded symbol is M_1 bitwise xor M_2,
    # and the third encoded symbol is M_1 bitwise xor M_3.
    # The computer reads the bits in the opposite direction of how the
    # elements are written matematically in the matrices above.
    # Therefore, it may be easier to find the hex values, which we input into
    # the variables below, if the matrices above are rewritten with the bits
    # in the direction which they are stored in memory. This is shown in the
    # matrices below:
    #
    #        | 0 0 1 1 1 0 1 0 |   | 0 1 0 | | 1 0 1 1 0 1 1 1 |
    #        | 1 0 0 0 1 1 0 1 | = | 0 1 1 | | 0 0 1 1 1 0 1 0 |
    #        | 1 1 0 1 0 1 1 0 |   | 1 0 1 | | 0 1 1 0 0 0 0 1 |

    original_symbols = [chr(i) for i in [0xb7, 0x3a, 0x61]]
    symbol_coefficients = [chr(i) for i in [0x02, 0x03, 0x05]]
    encoded_symbols = [chr(i) for i in [0x3a, 0x8d, 0xd6]]

    print("Start decoding...\n")

    # Decode each symbol and print the decoding progress
    for i in range(symbols):
        # Pass the i'th symbol and coefficients to decoder
        decoder.decode_symbol(
            encoded_symbols[i],
            symbol_coefficients[i])

        print("Coded symbol data:")
        #decoder.print_cached_symbol_data()

        print("Coded symbol coefficients:")
        #decoder.print_cached_symbol_coefficients()

        print("\nDecoding matrix:")
        #decoder.print_decoder_state()

        print("Symbol matrix:")
        #decoder.print_storage_value()
        print('')

    # Ensure that decoding was completed successfully.
    if decoder.is_complete():
        print("Decoding completed")
    else:
        print("Decoding incomplete - not all encoding vectors are independent")

    # Copy decoded data into a vector
    decoded_symbols = decoder.copy_symbols()
    # Check that the original data is the same as the decoded data
    if decoded_symbols == original_symbols:
        print("Data decoded correctly")
    else:
        print("Error: Decoded data differs from original data")
        print decoded_symbols
        print original_symbols

if __name__ == "__main__":
    main()
