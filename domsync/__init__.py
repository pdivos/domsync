"""
domsync is a DOM implementation in Python, such that any manipulations to the document will generate
Javascript code that can be executed on a client browser achieving the same manipulations of the browser DOM.

As a result you can use domsync to maintain and manipulate the browser Javascript DOM on the Python server side
and synchronise any changes that happen on the Python side to the browser Javascript side.
Thereby you can keep all of your UI logic in Python, there is no need to write UI APIs and maintain a separate
React/Angular/Vue/... application for the UI.

Right now this is one-way implementation only that synchronises changes on the Python server to the Javascript client.
If you want event handlers like onclick, onchange and so on, you can add them as string attributes and issue websocket messages
on the client side that will be processed on the server side.
"""

from pprint import pprint

from domsync.core import Document, Component
from domsync.passive_components import TableComponent
from domsync.active_components import ButtonComponent, TextInputComponent, TextareaComponent, SelectComponent
