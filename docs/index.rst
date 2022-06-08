domsync
=======

.. .. |pypi-v| |pypi-pyversions| |pypi-l| |pypi-wheel| |circleci| |codecov|

.. .. |pypi-v| image:: https://img.shields.io/pypi/v/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |pypi-pyversions| image:: https://img.shields.io/pypi/pyversions/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |pypi-l| image:: https://img.shields.io/pypi/l/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |pypi-wheel| image:: https://img.shields.io/pypi/wheel/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |circleci| image:: https://img.shields.io/circleci/project/github/aaugustin/websockets.svg
..    :target: https://circleci.com/gh/aaugustin/websockets

.. .. |codecov| image:: https://codecov.io/gh/aaugustin/websockets/branch/master/graph/badge.svg
..     :target: https://codecov.io/gh/aaugustin/websockets

``domsync`` is a library for building responsive web UIs in Python. A DOM document containing the whole UI is built and updated on the Python server side,
changes to this DOM are synchronised efficiently to the Browser. Events that happen on the Browser-side trigger callbacks on the Python-side.
This allows you to keep what the user sees in your Python process, close to your existing Python logic, eliminating the need for
creating and maintaining a separate Javascript client application and building an API interface to communicate with the client.

The syntax of domsync closely follows the core Javascript syntax for manipulating a DOM document:
we got ``getElementById``, ``createElement``, ``appendChild``, ``setAttribute``, ``addEventListener``, and so on. Every change to the Python domsync document
generates Javascript code which is almost equivalent to the Python domsync call, this allows users to clearly understand and control what
is happening to the DOM document on the Browser-side.

This is the generic Browser-side domsync client:

.. literalinclude:: ../examples/client.html
   :language: html

This Python domsync app shows the current time:

.. literalinclude:: ../examples/example_clock.py

Do you like it? Let's dive in!

Tutorials
---------

If you're new to ``domsync``, this is the place to start.

.. toctree::
   :maxdepth: 2

   intro

How-to guides
-------------

These guides will help you build and deploy a ``domsync`` application.

.. toctree::
   :maxdepth: 2

   cheatsheet
   deployment

Reference
---------

Find all the details you could ask for, and then some.

.. toctree::
   :maxdepth: 2

   api

Discussions
-----------

Get a deeper understanding of how ``domsync`` is built and why.

.. toctree::
   :maxdepth: 2

   design
   limitations
   security

Project
-------

This is about domsync-the-project rather than domsync-the-software.

.. toctree::
   :maxdepth: 2

   contributing
   changelog
   license

.. Welcome to Lumache's documentation!
.. ===================================

.. **Lumache** (/lu'make/) is a Python library for cooks and food lovers
.. that creates recipes mixing random ingredients.
.. It pulls data from the `Open Food Facts database <https://world.openfoodfacts.org/>`_
.. and offers a *simple* and *intuitive* API.

.. Check out the :doc:`usage` section for further information, including
.. how to :ref:`installation` the project.

.. .. note::

..    This project is under active development.

.. Contents
.. --------

.. .. toctree::

..    usage
..    api
