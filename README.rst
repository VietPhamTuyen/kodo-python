kodo-python
===========

This repository contains high-level python bindings for the Kodo Network Coding
library. The bindings provide access to basic functionality provided by Kodo,
such as encoding and decoding of data. The examples folder provides sample
applications showing usage of the python API.

License
-------

To obtain a valid Kodo license **you must fill out the license request** form_.

Kodo is available under a research and educational friendly licensee, see the details in the LICENSE.rst file.

.. _form: http://steinwurf.com/license/

Get
---
To get the python bindings you can either build them from source or download
a prebuilt version from `here`_.

.. _here: http://bongo.steinwurf.dk/files/bin/kodo-python

Build
-----

Kodo-python requires python headers to be available, but besides that it's build
like any other Steinwurf project::

  ./waf configure
  ./waf build

One additional requirement is present on windows, here you need the following
system environment variable::

  VS90COMNTOOLS=C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools\

