kodo-python
===========

kodo-python contains a set of high-level Python bindings for the Kodo Network
Coding C++ library. The bindings provide access to basic functionality provided
by Kodo, such as encoding and decoding data. The examples folder contains
sample applications showing the usage of the Python API.

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
request a license by **filling out the license request** form_.

This project is available under a research- and education-friendly license,
see the details in the `LICENSE.rst file
<https://github.com/steinwurf/kodo-python/blob/master/LICENSE.rst>`_.

.. _form: http://steinwurf.com/license/


Installation
============
We provide a pip package for the easy installation of the kodo-python library.

To install this you'll need python and pip installed:

- To get python `go here <https://www.python.org/downloads/>`_.
- To install pip `follow this guide <https://pip.pypa.io/en/latest/installing.html>`_.

You will need a set of tools and packages to build the library.

On all platforms, you will need a recent C++11 compiler.
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

MacOSX
------
Follow `this guide
<https://help.github.com/articles/set-up-git#setting-up-git>`_ to install git.

Install the latest XCode and Command-line Tools from the Mac Store.

When you are ready to install the package, you can simply type::

  sudo pip install kodo

Windows
-------
Install Python 2.7 (32-bit) and Visual Studio Express 2013 for Windows Desktop.
Then set the ``VS90COMNTOOLS`` environment variable to::

  C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\Tools\

so that Python distutils can detect your new compiler.

To enable the use of pip from the command line, ensure that the ``Scripts``
subdirectory of your Python installation is available on the system ``PATH``.
(This is not done automatically.)

When you are ready to install the package, you can simply type::

  pip install kodo

Building From Source
====================
You can also build the bindings from source, if you don't want to use pip.

Before doing anything, please install the requirements specified in
the previous section (you can ignore the parts about pip).

After that you can clone the project::

  git clone git@github.com:steinwurf/kodo-python.git

Configure and build the project::

  cd kodo-python
  python waf configure
  python waf build

Now the project is built and you should be able to find the resulting
``kodo.so`` or ``kodo.pyd`` file here (the actual path and extension is
dependent on your OS and Python version)::

  build/linux/src/kodo_python/kodo.so
  build/darwin/src/kodo_python/kodo.dylib
  build/win32/src/kodo_python/kodo.pyd

You can add this path to your PYTHONPATH and import the module in your Python
script::

  >>> import kodo
