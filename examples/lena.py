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
    import pygame.gfxdraw
except:
    import sys
    print("Unable to import pygame module, please make sure it is installed.")
    sys.exit()

import numpy


class CanvasEngine(object):
    def __init__(self, width, height):
        self.lock = threading.Lock()
        self.screen = None
        self.running = False
        self.size = (width, height)
        self.thread = threading.Thread(name='canvas', target=self.__start)

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
            pygame.display.set_caption('Example Canvas')
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

    def add_surface(self, surface, position):
        with self.lock:
            self.screen.blit(surface, position)


class ImageViewer(object):
    """
    A class containing the logic for displaying an image during decoding
    """
    def __init__(self, width, height, canvas, canvas_position=(0, 0)):
        """
        Construct ImageViewer object

        :param width: the width of the picture to be displayed
        :param height: the height of the picture to be displayed
        """
        super(ImageViewer, self).__init__()
        self.size = (width, height)
        self.data_size = width * height * 3
        self.canvas = canvas
        self.canvas_position = canvas_position

    def set_image(self, image_string):
        """
        Displays the provided string as an image.

        The string should be a string representation of a numpy 3d array,
        and it should be equal to or larger than width * height * 3.
        """
        image_array = numpy.fromstring(
            image_string[:self.data_size], dtype=numpy.uint8)

        image_array.shape = self.size + (3,)

        # Show picture from top to buttom
        image_array = numpy.rot90(image_array)
        image_surface = pygame.Surface(self.size)
        pygame.surfarray.blit_array(image_surface, image_array)
        self.canvas.add_surface(
            image_surface,
            self.canvas_position)


class DecodeStateViewer(object):
    """Class for displaying the decoding coefficients"""
    def __init__(self, symbols, size, canvas, canvas_position):
        super(DecodeStateViewer, self).__init__()
        self.surface = pygame.Surface((size, size))
        self.padding = 10.0
        self.diameter = (size - self.padding * 2.0) / symbols
        self.canvas = canvas
        self.canvas_position = canvas_position

    def trace_callback(self, zone, message):
        """Callback to be used with the decoder trace API"""
        # We are only interested in the decoder state.
        if zone != "decoder_state":
            return

        decode_state = []
        for line in message.split('\n'):
            if not line:
                continue
            line = line.split()

            decode_state.append({
                'state': line[1][0],
                'data': [int(i) for i in line[2:]]
            })

        self.show_decode_state(decode_state)

    def show_decode_state(self, decode_state):
        """
        Use the decoding state to print a graphical representation.

        :param decode_state: A list of dictionaries containing the symbol
                             coefficients.
        """

        self.surface.fill((0,)*3)
        y = self.padding + self.diameter / 2
        for symbol in decode_state:
            x = self.padding + self.diameter / 2
            for data in symbol['data']:
                x += self.diameter
                if data == 0:
                    continue
                color = (255,)*3
                if data != 1:
                    color = (data % 255,) * 3
                pygame.gfxdraw.circle(
                    self.surface,
                    int(x - self.diameter),
                    int(y),
                    int(self.diameter / 2),
                    color)
            y += self.diameter

        self.canvas.add_surface(
            self.surface,
            self.canvas_position)


def main():
    # Get directory of this file
    directory = os.path.dirname(os.path.realpath(__file__))

    # Load the image
    image = pygame.image.load(os.path.join(directory, 'lena.jpg'))

    # Create example canvas.
    canvas = CanvasEngine(image.get_width()*2, image.get_height())

    # Create an image viewer
    image_viewer = ImageViewer(image.get_width(), image.get_height(), canvas)

    # Convert the image into a string representation of a 3d (numpy) array
    # Rotate the array 270 degrees so that it's shown top down.
    data_in = numpy.rot90(pygame.surfarray.array3d(image), 3).tostring()

    # Pick a symbol size
    symbol_size = image.get_width()*3

    # Based on the size of the image and the symbol size, calculate the number
    # of symbols needed for containing this image in a single generation.
    symbols = int(math.ceil(float(len(data_in)) / symbol_size))

    # Create an coefficient viewer
    decode_state_viewer = DecodeStateViewer(
        symbols=symbols,
        size=max(image.get_width(), image.get_height()),
        canvas=canvas,
        canvas_position=(image.get_width(), 0))

    # Create encoder
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    encoder = encoder_factory.build()

    # Create decoder
    decoder_factory = kodo.FullVectorDecoderFactoryBinaryTrace(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    decoder = decoder_factory.build()

    # Set up tracing
    if 'trace' in dir(decoder):
        cb = lambda zone, msg: decode_state_viewer.trace_callback(zone, msg)
        decoder.trace(cb)

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


if __name__ == "__main__":
    main()
