#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2011-2013.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import threading

try:
    import pygame
    import pygame.locals
    import pygame.gfxdraw
except:
    import sys
    print("Unable to import pygame module, please make sure it is installed.")
    sys.exit()

import numpy


class CanvasScreenEngine(object):
    """Canvas engine for displaying images to the screen"""
    def __init__(self, width, height):
        self.lock = threading.Lock()
        self.screen = None
        self.running = False
        # Add a little padding
        self.size = (width + 1, height + 1)
        self.thread = threading.Thread(name='canvas', target=self.__start)

    def start(self):
        """Start a thread which runs the viewer logic"""
        self.thread.start()
        # Busy wait for the engine to start.
        while not self.running:
            pass

    def __start(self):
        """Start pygame and create a game loop"""
        with self.lock:
            self.running = True
            pygame.init()
            pygame.display.set_caption('Example Canvas')
            self.screen = pygame.display.set_mode(self.size, pygame.NOFRAME)
            # Paint it black
            self.screen.fill((0, 0, 0))

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


class CanvasFileEngine(object):
    """Canvas engine for writing images to files"""
    def __init__(self, width, height, directory):
        # Add a little padding
        self.size = (width + 1, height + 1)
        self.files = 0
        self.directory = directory

    def start(self):
        pass

    def stop(self):
        pass

    def add_surface(self, surface, position):
        screen = pygame.Surface(self.size)
        screen.blit(surface, position)
        filename = "{:07d}.png".format(self.files)
        self.files += 1
        pygame.image.save(
            self.screen, os.path.join(self.directory, filename))


class DecodeStateViewer(object):
    """Class for displaying the decoding coefficients"""
    def __init__(self, size, canvas, canvas_position=(0, 0)):
        super(DecodeStateViewer, self).__init__()
        self.size = size
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

            # Add the decoding state
            decode_state.append([int(i) for i in line[2:]])

        self.show_decode_state(decode_state)

    def show_decode_state(self, decode_state):
        """
        Use the decoding state to print a graphical representation.

        :param decode_state: A list of lists containing the symbol coefficients
        """
        surface = pygame.Surface((self.size + 1, self.size + 1))
        surface.fill((0,)*3)
        diameter = self.size / len(decode_state)
        y = diameter / 2
        for symbol in decode_state:
            x = diameter / 2
            for data in symbol:
                x += diameter
                if data == 0:
                    continue
                color = (255,)*3
                if data != 1:
                    color = (data % 255,) * 3

                pygame.gfxdraw.circle(
                    surface,
                    int(x - diameter),
                    int(y),
                    int(diameter / 2),
                    color)
            y += diameter

        self.canvas.add_surface(
            surface,
            self.canvas_position)


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

        # We use PIL.Image to write the image and pygame to read it. To make
        # the two compliant, we must reshape, rotate, and flip the array/image.
        image_array.shape = (self.size[1], self.size[0], 3)
        image_array = numpy.flipud(numpy.rot90(image_array, 1))

        # Create a surface
        image_surface = pygame.Surface(self.size)

        # Blit the image data to the surface
        pygame.surfarray.blit_array(image_surface, image_array)

        # Add the surface to the canvas.
        self.canvas.add_surface(
            image_surface,
            self.canvas_position)
