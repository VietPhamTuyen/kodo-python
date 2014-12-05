#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import kodo
import kodo_helpers

import Image
import math
import os
import random
import time
import sys


def main():

    # Get directory of this file
    directory = os.path.dirname(os.path.realpath(__file__))

    # The name of the file to use for the test
    filename = 'lena.jpg'

    # Open the image convert it to RGB and get the height and width
    image = Image.open(os.path.join(directory, filename)).convert("RGB")
    image_width = image.size[0]
    image_height = image.size[1]

    # The canvas should be able to contain both the image and the decoding
    # state. Note the decoding state is the same width as the image height.
    canvas_width = image_width + image_height

    # Create the canvas
    canvas = kodo_helpers.CanvasScreenEngine(
        width=canvas_width,
        height=image_height)

    # Create the image viewer
    image_viewer = kodo_helpers.ImageViewer(
        width=image_width,
        height=image_height,
        canvas=canvas)

    # Create the decoding coefficient viewer
    state_viewer = kodo_helpers.DecodeStateViewer(
        size=image_height,
        canvas=canvas,
        canvas_position=(image_width, 0))

    # Pick a symbol size (image_width * 3 will create a packet for each
    # horizontal line of the image)
    symbol_size = image_width * 3

    # Based on the size of the image and the symbol size, calculate the number
    # of symbols needed for containing the image in a single generation.
    symbols = int(math.ceil(image_width * image_height * 3.0 / symbol_size))

    # Create encoder factory and encoder
    encoder_factory = kodo.FullVectorEncoderFactoryBinary8(
        max_symbols=symbols,
        max_symbol_size=symbol_size)
    encoder = encoder_factory.build()

    # Create decoder factory and decoder
    decoder_factory = kodo.FullVectorDecoderFactoryBinary8Trace(
        max_symbols=symbols,
        max_symbol_size=symbol_size)
    decoder = decoder_factory.build()

    # Connect the tracing callback to the decode state viewer
    callback = lambda zone, msg: state_viewer.trace_callback(zone, msg)
    decoder.trace(callback)

    # Create a byte array from the image to use in the encoding
    data_in = image.tobytes()

    # Set the converted image data
    encoder.set_symbols(data_in)

    # Create an image viwer and run the following code in a try catch;
    # this prevents the program from locking up, as the finally clause will
    # close down the image viewer.
    canvas.start()
    try:
        packets = 0
        while not decoder.is_complete():
            packet = encoder.encode()
            packets += 1

            # Drop some packets
            if random.choice([True, False]):
                decoder.decode(packet)

            # limit the number of times we write to the screen (it's expensive)
            if packets % (symbols // 20) == 0 or decoder.is_complete():
                image_viewer.set_image(decoder.copy_symbols())

        # Let the user see the photo before closing the application
        time.sleep(1)
    finally:
        canvas.stop()

    # The decoder is complete, now copy the symbols from the decoder
    data_out = decoder.copy_symbols()

    # Check we properly decoded the data
    if data_out[:len(data_in)] == data_in:
        print("Data decoded correctly")
    else:
        print("Unexpected failure to decode please file a bug report :)")
        sys.exit(1)


if __name__ == "__main__":
    main()
