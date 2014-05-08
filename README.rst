===========
kodo-python
===========

This repository contains high-level python bindings for the Kodo Network Coding
library. The bindings provide access to basic functionality provided by Kodo,
such as encoding and decoding of data. The examples folder provides sample
applications showing usage of the python API.

License
=======

If you wish to use this library, please obtain a valid Kodo license. To do so
**you must fill out the license request** form_.

Kodo is available under a research and educational friendly licensee, see the details in the LICENSE.rst file.

.. _form: http://steinwurf.com/license/

How to Get It
=============
To get the python bindings you can either build them from source or download
a prebuilt version from `here`_.

.. _here: http://bongo.steinwurf.dk/files/bin/kodo-python


Requirements
============

Depending on your platform, you'll need the following to build kodo-python.

Beside the requirements below, you'll need a recent c++ compiler.
The compilers used by Steinwurf is listed on the `buildbot page`_.

.. _buildbot page: http://buildbot.steinwurf.dk

Linux
-----
You'll need the the python development headers to build kodo-python. These can
most likely be acquired using your distro's package manager.

Mac
---

The default installation of python which exists on OSX doesn't include the
python development header, which is required for kodo-python.
Therefore you'll need to install python, e.g. using MacPorts.
When you have acquired python use that installation of python to execute the
waf commands.

Windows
-------

Beside a python installation, you'll need the following environment variable::

  VS90COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools\

How to Build It
===============

kodo-python is built like any other Steinwurf project::

  ./waf configure
  ./waf build
