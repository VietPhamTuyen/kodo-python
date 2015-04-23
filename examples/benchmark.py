#! /usr/bin/env python
# encoding: utf-8

import time
import sys
import pykodo as kodo

def run_coding_test(algorithm, field, symbols, symbol_size):
    """Runs a timed encoding and decoding benchmark."""

    # First, we measure the combined setup time for the encoder and decoder
    start = time.clock()

    encoder_factory = kodo.encoder_factory(
        algorithm, field, symbols, symbol_size)

    decoder_factory = kodo.decoder_factory(
        algorithm, field, symbols, symbol_size)

    encoder = encoder_factory.build()
    decoder = decoder_factory.build()

    # Stop the setup timer
    stop = time.clock()

    setup_time = stop - start

    # We measure pure coding, so we always turn off the systematic mode
    if 'set_systematic_off' in dir(encoder):
        encoder.set_systematic_off()

    # Create random data to encode
    data_in = os.urandom(encoder.block_size())

    # The generated payloads will be stored in this list
    payloads = []

    # Generate an ample number of coded symbols (considering kodo_binary)
    payload_count = 2 * symbols

    # Start the encoding timer
    start = time.clock()

    # Copy the input data to the encoder
    encoder.set_symbols(data_in)

    # Generate coded symbols with the encoder
    for i in range(payload_count):
        payload = encoder.write_payload()
        payloads.append(payload)

    # Stop the encoding timer
    stop = time.clock()

    encoding_time = stop - start

    # Calculate the encoding rate in megabytes / seconds
    encoded_bytes = payload_count * symbol_size
    encoding_rate = encoded_bytes / encoding_time

    # Start the decoding timer
    start = time.clock()

    # Feed the coded symbols to the decoder
    for i in range(payload_count):
        if decoder.is_complete():
            break
        decoder.read_payload(payloads[i])

    # Copy the symbols from the decoder
    data_out = decoder.copy_symbols()

    # Stop the decoding timer
    stop = time.clock()

    decoding_time = stop - start

    # Calculate the decoding rate in megabytes / seconds
    decoded_bytes = symbols * symbol_size
    decoding_rate = decoded_bytes / decoding_time

    if data_out == data_in:
        success = True
    else:
        success = False

    print("Setup time: {} microsec".format(setup_time))
    print("Encoding time: {} microsec".format(encoding_time))
    print("Decoding time: {} microsec".format(decoding_time))

    return (success, encoding_rate, decoding_rate)


if __name__ == "__main__":

    argv = sys.argv

    if len(argv) != 5:
        print("Usage: {} <algorithm> <field> <symbols> <symbol_size>"
              .format(argv[0]))
        sys.exit(0)

    algorithm = argv[1]
    if hasattr(kodo, algorithm):
        algorithm = getattr(kodo, algorithm)
    else:
        sys.exit("Invalid algorithm: {0}".format(algorithm))

    field = argv[2]
    if hasattr(kodo, field):
        field = getattr(kodo, field)
    else:
        sys.exit("Invalid finite field: {0}".format(field))

    symbols = argv[3]
    symbol_size = argv[4]

    decoding_success, encoding_rate, decoding_rate = \
        run_coding_test(algorithm, field, symbols, symbol_size)

    print("Symbols: {} / Symbol_size: {}".format(symbols, symbol_size))
    print("Encoding rate: {} MB/s".format(encoding_rate))
    print("Decoding rate: {} MB/s".format(decoding_rate))

    if decoding_success:
        print("Data decoded correctly.")
    else:
        print("Decoding failed.")
