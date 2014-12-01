#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

from __future__ import print_function
from __future__ import division

import kodo

import math
import os
import random
import threading
import time

try:
    import pygame
    import pygame.locals
except:
    import sys
    print("Unable to import pygame module, please make sure it is installed.")
    sys.exit()

import numpy


class ImageViewer(object):
    """
    A class containing the logic for displaying an image during decoding
    """
    def __init__(self, width, height):
        """
        Construct ImageViewer object

        :param width: the width of the picture to be displayed
        :param height: the height of the picture to be displayed
        """
        super(ImageViewer, self).__init__()
        self.lock = threading.Lock()
        self.screen = None
        self.running = False
        self.size = (width, height)
        self.data_size = width * height * 3
        self.thread = threading.Thread(
            name='image_viewer', target=self.__start)

    def start(self):
        """Start a thread which runs the viewer logic"""
        self.thread.start()
        while not self.running:
            pass

    def __start(self):
        """Start pygame and create a game loop"""
        with self.lock:
            self.running = True
            pygame.init()
            pygame.display.set_caption('Kodo-python ImageViewer')
            self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
            self.screen.fill((250, 250, 250))

        while(self.running):
            with self.lock:
                pygame.display.flip()
        pygame.quit()

    def stop(self):
        """Stops the game loop and joins the thread"""
        self.running = False
        self.thread.join()

    def set_image(self, image_string):
        """
        Displays the provided string as an image.

        The string should be a string representation of a numpy 3d array,
        and it should be equal to or larger than width * height * 3.
        """
        image_array = numpy.fromstring(
            image_string[:self.data_size],
            dtype=numpy.uint8)
        image_array.shape = self.size + (3,)

        # Show picture from top to buttom
        image_array = numpy.rot90(image_array)

        with self.lock:
            pygame.surfarray.blit_array(self.screen, image_array)


class ForceSystematicEncoder(object):
    """Wrapper class to force an encoder to stay in systematic mode"""
    def __init__(self, encoder):
        self.encoder = encoder
        self.packets = []
        self.packet_count = 0

    def encode(self):
        self.packet_count += 1
        if self.packet_count != self.encoder.rank():
            self.packets.append(self.encoder.encode())

        return self.packets[(self.packet_count-1) % self.encoder.rank()-1]

    def set_symbols(self, symbols):
        return self.encoder.set_symbols(symbols)


def main():

    # Get directory of this file
    directory = os.path.dirname(os.path.realpath(__file__))

    # Load the image
    image = pygame.image.load(os.path.join(directory, 'lena.jpg'))

    # Create an image viewer (the width and height of the image is needed).
    image_viewer = ImageViewer(image.get_width(), image.get_height())

    # Convert the image into a string representation of a 3d (numpy) array
    # Rotate the array 270 degrees so that it's shown top down.
    data_in = numpy.rot90(pygame.surfarray.array3d(image), 3).tostring()

    # Pick a symbol size
    symbol_size = 64

    # Based on the size of the image and the symbol size, calculate the number
    # of symbols needed for containing this image in a single generation.
    symbols = int(math.ceil(float(len(data_in)) / symbol_size))

    # Create encoder
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    encoder = encoder_factory.build()

    # Create decoder
    decoder_factory = kodo.FullVectorDecoderFactoryBinary(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    decoder = decoder_factory.build()

    # Set the converted image data
    encoder.set_symbols(data_in)

    # Create an image viwer and run the following code in a try catch;
    # this prevents the program from locking up, as the finally clause will
    # close down the image viewer.
    image_viewer.start()
    try:
        packets = 0
        while not decoder.is_complete():
            packet = encoder.encode()
            packets += 1

            # Drop some packets
            if random.choice([True, False]):
                decoder.decode(packet)

            # limit the number of times we write to the screen (it's expensive)
            if packets % (symbols // 5) == 0 or decoder.is_complete():
                image_viewer.set_image(decoder.copy_symbols())

        # Let the user see the photo before closing the application
        time.sleep(1)
    finally:
        image_viewer.stop()


if __name__ == "__main__":
    main()
