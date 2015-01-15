kodo-python
===========

kodo-python contains a set of high-level python bindings for the Kodo Network
Coding C++ library. The bindings provide access to basic functionality provided
by Kodo, such as encoding and decoding of data. The examples folder provides
sample applications showing usage of the python API.

.. image:: http://buildbot.steinwurf.dk/svgstatus?project=kodo-python
    :target: http://buildbot.steinwurf.dk/stats?projects=kodo-python
    :alt: Buildbot status
.. image:: https://badge.fury.io/py/kodo.svg
    :target: http://badge.fury.io/py/kodo
.. image:: https://pypip.in/download/kodo/badge.svg
    :target: https://pypi.python.org/pypi/kodo
    :alt: Downloads
.. image:: https://pypip.in/py_versions/kodo/badge.svg
    :target: https://pypi.python.org/pypi/kodo
    :alt: Supported Python versions
.. image:: https://pypip.in/format/kodo/badge.svg
    :target: https://pypi.python.org/pypi/kodo
    :alt: Download format
.. image:: https://pypip.in/license/kodo/badge.svg
    :target: https://pypi.python.org/pypi/kodo
    :alt: License

License
=======

A valid license is required if you wish to use and install this library. Please
request a license by filling out the license request** form_.

Note, this project is available under a research- and educational-friendly
license, see the details in the `LICENSE.rst file
<https://github.com/steinwurf/kodo-python/blob/master/LICENSE.rst>`_.

.. _form: http://steinwurf.com/license/


Installation
============
We provide a pip package for easy installation of the kodo-python library.

To install this you'll need python and pip installed:
 - To get python `go here <https://www.python.org/downloads/>`_.
 - To install pip `follow this guide
   <https://pip.pypa.io/en/latest/installing.html>`_.

Depending on your platform, you will need a set of tools and libraries to build
the library.

Common for all platforms is that you will need a recent C++11 compiler.
The compilers used by Steinwurf are listed on the
`buildbot page <http://buildbot.steinwurf.com>`_.

Linux
-----
These steps may not work with your specific Linux distribution, but they may
guide you in the right direction.

First, acquire the required packages from your package management system::

  sudo apt-get update
  sudo apt-get install python git build-essential libpython-dev

If you are using Python 3, you'll need to install ``libpython3-dev`` instead.

When you are ready to install the package, you can simply type::

  sudo pip install kodo

MacOS
-----

Follow `this guide
<https://help.github.com/articles/set-up-git#setting-up-git>`_ to install git.

Install Xcode and Command-line Tools from the Mac Store.

When you are ready to install the package, you can simply type::

  sudo pip install kodo

Windows
-------
Install Python 2.7 32-bit and Visual Studio 2013 (Express).
Now set the following environment variable ``VS90COMNTOOLS`` to::

  C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools\

so that Python distutils can detect your new compiler.

To enable the use of pip from the command line, ensure that the ``Scripts``
subdirectory of your Python installation is available on the system ``PATH``.
(This is not done automatically.)

When you are ready to install the package, you can simply type::

  pip install kodo

Building From Source
====================
If you prefer not to use pip, you can also build the bindings yourself.

Before doing anything, make sure you've installed the requirements specified in
the previous section.

When you have installed all dependencies, you can clone the project::

    git clone https://github.com/steinwurf/kodo-python.git

configure and build the project::

  cd kodo-python
  python waf configure
  python waf build

Now the project is built and you should be able to find the resulting
kodo.so file here (the actual path and extension is dependent on
your OS and python version.)::

  build/linux/src/kodo_python/kodo.so

You can add this path to your PYTHONPATH and import the module in your Python
script::

  >>> import kodo
