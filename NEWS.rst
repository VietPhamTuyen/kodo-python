News for kodo-python
====================

This file lists the major changes between versions. For a more detailed list of
every change, see the Git log.

Latest
------
* Minor: Added ``symbols`` and ``symbol_size`` methods to factory.

4.0.0
-----
* Major: Upgrade to Fifi 14.
* Major: Upgrade to Kodo 19.
* Minor: Added ``sparse_full_rlnc_encoder``.
* Minor: Added guide on how to extend the bindings.
* Patch: Fix the docstrings to follow the pep257 style guide.
* Patch: Added keyword argument for the ``is_symbol_pivot`` method.
* Minor: Added UDP unicast example.
* Minor: Added graphical Lena example.

3.0.0
-----
* Minor: Added multicast examples.
* Major: Python objects now only provide the functions they support. E.g., a
  non-trace encoder no longer has the trace function. Also the ``has_``
  functions were removed. This includes: ``has_partial_decoding_tracker``,
  ``has_systematic_encoder``, and ``has_trace``.
* Patch: Simplified examples.
* Major: Updated Kodo 18.
* Major: Updated Fifi 13.
* Major: Updated Sak 12.

2.2.0
-----
* Minor: Added documentation for the python functions.
* Minor: Added keyword arguments for the python functions.
* Patch: Removed unused dependencies guage and tables.

2.1.0
-----
* Minor: Set ``kodo-python`` as the name for wscript target, so that it doesn't
  clash with the kodo dependency when both are used as dependencies.

2.0.0
-----
* Major: Updated to Kodo 17.
* Minor: Extended API.
* Minor: Added additional examples.

1.0.0
-----
* Initial release.
