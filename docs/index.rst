domsync
=======

``domsync`` is a library for building responsive web UIs in Python. A DOM document containing the whole UI is built and updated on the Python server side,
changes to this DOM are synchronised efficiently to the Browser. Events that happen on the Browser-side trigger callbacks on the Python-side.
This allows you to keep what the user sees in your Python process, close to your existing Python logic, eliminating the need for
creating and maintaining a separate Javascript client application and building an API interface to communicate with the client.

The syntax of domsync closely follows the core Javascript syntax for manipulating a DOM document:
we got ``getElementById``, ``createElement``, ``appendChild``, ``setAttribute``, ``addEventListener``, and so on. Every change to the Python domsync document
generates Javascript code which is almost equivalent to the Python domsync call, this allows users to clearly understand and control what
is happening to the DOM document on the Browser-side.

Here is a ``domsync`` server-side app that shows the current server time in a Browser:

.. literalinclude:: ../src/examples/example_clock.py

Let's take a look at what happens here.

#. ``await DomsyncServer(connection_handler, 'localhost', 8888).serve()`` starts a domsync server which is essentially a websocket server with a domsync ``Document`` instance for each connected client.

#. ``async def connection_handler(server, client)`` is the handler that runs when a new client connects to the server. The arguments of this function are the ``DomsyncServer`` instance and the websocket client connection instance.

#. ``doc = server.get_document(client)`` gets the domsync ``Document`` associated with the client which contains the DOM. Each client has it's separate ``Document`` that can be manipulated separately.

#. | ``root_element = document.getElementById(document.getRootId())`` gets the root element of the ``Document`` which corresponds to the ``<div id='domsync_root_id'></div>`` element in the client-side HTML.
   | ``div_element = document.createElement('div')`` creates a new ``div`` element in the document.
   | ``root_element.appendChild(div_element)`` appends the ``div`` element under the root element as a child.
   | ``div_element.innerText = 'The current time is: ' + datetime.utcnow().isoformat()`` updates the text of the div element to the current time.
   | These operations modify the domsync ``Document`` in memory but also generate Javascript code which is saved in an internal buffer of the ``Document``. At this point the content of the buffer is this generated Javascript code:

   .. code-block:: javascript

      var __domsync__ = [];
      __domsync__["domsync_root_id"] = document.getElementById("domsync_root_id");
      __domsync__["__domsync_el_0"] = document.createElement("div");
      __domsync__["__domsync_el_0"].setAttribute("id","__domsync_el_0");
      __domsync__["domsync_root_id"].appendChild(__domsync__["__domsync_el_0"]);
      __domsync__["__domsync_el_0"].innerText = `The current time is: 2022-06-08T03:23:14.818841`;

#. ``await server.flush(client)`` sends the contents of the Javascript buffer to the client where it gets evaluated and as a result the current time appears on the screen.

#. As the ``while`` loop progresses, the ``Document`` is modified and the generated Javascript code is sent to the client continuously. However, domsync is efficient in the sense that it only sends changes for those elements that have actually changed, in this example this is the only line of generated Javascript that is sent by the next ``await server.flush(client)``:

   .. code-block:: javascript

      __domsync__["__domsync_el_0"].innerText = `The current time is: 2022-06-08T03:23:14.925521`;


Here is the generic Browser-side client:

.. literalinclude:: ../src/examples/client.html
   :language: html

#. The client connects to the domsync server running on localhost port 8888 over websocket.

#. The domsync server sends javascript code containing DOM operations that are evaluated in ``socket.onmessage``.

#. The ``ws_send`` function is used as an event callback to send events back to the server.

This example is in ``examples/example_clock.py`` with the client-side html in ``examples/client.html``.

Do you like it? Let's dive in!

.. toctree::
   :hidden:

   reference/index

.. intro/index
.. howto/index
.. project/index



.. websockets
.. ==========

.. .. |licence| |version| |pyversions| |wheel| |tests| |docs|

.. .. |licence| image:: https://img.shields.io/pypi/l/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |version| image:: https://img.shields.io/pypi/v/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |pyversions| image:: https://img.shields.io/pypi/pyversions/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |wheel| image:: https://img.shields.io/pypi/wheel/websockets.svg
..     :target: https://pypi.python.org/pypi/websockets

.. .. |tests| image:: https://img.shields.io/github/checks-status/aaugustin/websockets/main
..    :target: https://github.com/aaugustin/websockets/actions/workflows/tests.yml

.. .. |docs| image:: https://img.shields.io/readthedocs/websockets.svg
..    :target: https://websockets.readthedocs.io/

.. websockets is a library for building WebSocket_ servers and
.. clients in Python with a focus on correctness, simplicity, robustness, and
.. performance.

.. .. _WebSocket: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

.. Built on top of :mod:`asyncio`, Python's standard asynchronous I/O framework,
.. it provides an elegant coroutine-based API.

.. Here's how a client sends and receives messages:

.. .. literalinclude:: ../example/hello.py

.. And here's an echo server:

.. .. literalinclude:: ../example/echo.py

.. Don't worry about the opening and closing handshakes, pings and pongs, or any
.. other behavior described in the specification. websockets takes care of this
.. under the hood so you can focus on your application!

.. Also, websockets provides an interactive client:

.. .. code-block:: console

..     $ python -m websockets ws://localhost:8765/
..     Connected to ws://localhost:8765/.
..     > Hello world!
..     < Hello world!
..     Connection closed: 1000 (OK).

.. 
