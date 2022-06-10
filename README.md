# domsync

domsync is a library for building responsive web UIs in Python. A DOM document containing the whole UI is built and updated on the Python server side,
changes to this DOM are synchronised efficiently to the Browser. Events that happen on the Browser-side trigger callbacks on the Python-side.
This allows you to keep what the user sees in your Python process, close to your existing Python logic, eliminating the need for
creating and maintaining a separate Javascript client application and building an API interface to communicate with the client.

The syntax of domsync closely follows the core Javascript syntax for manipulating a DOM document:
we got ```getElementById```, ```createElement```, ```appendChild```, ```setAttribute```, ```addEventListener```, and so on. Every change to the Python domsync document
generates Javascript code which is almost equivalent to the Python domsync call, this allows users to clearly understand and control what
is happening to the DOM document on the Browser-side.

## Installation

Install domsync with:

```console
pip install domsync
```

## Basic example

This Python domsync app shows the current time:

```Python
import asyncio
from datetime import datetime
from domsync.domsync_server import DomsyncServer

async def connection_handler(server, client):
    """
    connection_handler is called when a client connects to the server
    :param server: is the DomsyncServer instance
    :param client: is a websocket client connection instance
    """

    # get the client's domsync Document
    document = server.get_document(client)

    # add a div to the root element
    root_element = document.getElementById(document.getRootId())
    div_element = document.createElement('div')
    root_element.appendChild(div_element)

    while True:
        # update the text of the div to the current time
        div_element.innerText = 'The current time is: ' + datetime.utcnow().isoformat()

        # send updates to the client
        await server.flush(client)

        # wait a bit
        await asyncio.sleep(0.1)

async def main():
    # start a domsync server on localhost port 8888
    await DomsyncServer(connection_handler, 'localhost', 8888).serve()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
```

Let's take a look at what happens here.
1. ```await DomsyncServer(connection_handler, 'localhost', 8888).serve()``` starts a domsync server which is essentially a websocket server with a domsync ```Document``` instance for each connected client.
2. ```async def connection_handler(server, client)``` is the handler that runs when a new client connects to the server. The arguments of this function are the ```DomsyncServer``` instance and the websocket client connection instance.
3. ```doc = server.get_document(client)``` gets the domsync ```Document``` associated with the client which contains the DOM. Each client has it's separate ```Document``` that can be manipulated separately.
4. ```root_element = document.getElementById(document.getRootId())``` gets the root element of the ```Document``` which corresponds to the ```<div id='domsync_root_id'></div>``` element in the client-side HTML.  
```div_element = document.createElement('div')``` creates a new ```div``` element in the document.  
```root_element.appendChild(div_element)``` appends the ```div``` element under the root element as a child.  
```div_element.innerText = 'The current time is: ' + datetime.utcnow().isoformat()``` updates the text of the div element to the current time.  
These operations modify the domsync ```Document``` in memory but also generate Javascript code which is saved in an internal buffer of the ```Document```. At this point the content of the buffer is this generated Javascript code:
    ```javascript
    var __domsync__ = [];
    __domsync__["domsync_root_id"] = document.getElementById("domsync_root_id");
    __domsync__["__domsync_el_0"] = document.createElement("div");
    __domsync__["__domsync_el_0"].setAttribute("id","__domsync_el_0");
    __domsync__["domsync_root_id"].appendChild(__domsync__["__domsync_el_0"]);
    __domsync__["__domsync_el_0"].innerText = `The current time is: 2022-06-08T03:23:14.818841`;
    ```
5. ```await server.flush(client)``` sends the contents of the Javascript buffer to the client where it gets evaluated and as a result the current time appears on the screen.
6. As the ```while``` loop progresses, the ```Document``` is modified and the generated Javascript code is sent to the client continuously. However, domsync is efficient in the sense that it only sends changes for those elements that have actually changed, in this example this is the only line of generated Javascript that is sent by the next ```await server.flush(client)```:
    ```javascript
    __domsync__["__domsync_el_0"].innerText = `The current time is: 2022-06-08T03:23:14.925521`;
    ```

This is the generic Browser-side domsync client:
```html
<html>

  <!-- domsync will render into this element -->
  <body><div id='domsync_root_id'></div></body>

  <script type = "text/javascript">

    // server -> client: DOM changes are coming from websocket as javascript code and are eval'ed here
    socket = new WebSocket("ws://localhost:8888");
    socket.onmessage = function(event) { (function(){eval.apply(this, arguments);}(event.data)); };

    // client -> server: ws_send is called by event handlers to send event messages to the server
    function ws_send(msg) { socket.send(JSON.stringify(msg)); };

  </script>
</html>
```
The client connects to the domsync server running on localhost port 8888 over websocket.
The domsync server sends javascript code containing DOM operations that are evaluated in ```socket.onmessage```.
The ```ws_send``` function is used as an event callback to send events back to the server.

This example is in ```examples/example_clock.py``` with the client-side html in ```examples/client.html```.

Read the docs: [https://domsync.readthedocs.io/](https://domsync.readthedocs.io/)

<!--
<details>
  <summary>Click to see the Javascript code generated</summary>
  
```javascript
var __domsync__ = [];
__domsync__["domsync_root_id"] = document.getElementById("domsync_root_id");
el = document.createElement('h1');el.setAttribute('id', 'h1_0');__domsync__['h1_0'] = el;
__domsync__["h1_0"].innerText = "domsync demo";
__domsync__["domsync_root_id"].appendChild(__domsync__["h1_0"]);
el = document.createElement('ul');el.setAttribute('id', 'ul_0');__domsync__['ul_0'] = el;
__domsync__["domsync_root_id"].appendChild(__domsync__["ul_0"]);
el = document.createElement('li');el.setAttribute('id', 'li_0');__domsync__['li_0'] = el;
__domsync__["li_0"].innerText = "item 0";
__domsync__["ul_0"].appendChild(__domsync__["li_0"]);
el = document.createElement('li');el.setAttribute('id', 'li_1');__domsync__['li_1'] = el;
__domsync__["li_1"].innerText = "item 1";
__domsync__["ul_0"].appendChild(__domsync__["li_1"]);
el = document.createElement('li');el.setAttribute('id', 'li_2');__domsync__['li_2'] = el;
__domsync__["li_2"].innerText = "item 2";
__domsync__["ul_0"].appendChild(__domsync__["li_2"]);
```
</details>

On the Browser client side the generated javascript code is evaluated which causes the DOM within ```<div id='domsync_root_id'>``` to change to this:

```html
<div id='domsync_root_id'>
  <h1 id='h1_0'>domsync demo</h1>
  <ul id='ul_0'>
    <li id='li_0'>item 0</li>
    <li id='li_1'>item 1</li>
    <li id='li_2'>item 2</li>
  </ul>
</div>
```

Now on the Python server side we can do more manipulations to the DOM Document and send the updates to the client:
```Python
# change the first items text, remove the second item, change the third items attribute
doc.getElementById('li_0').innerText = doc.getElementById('li_0').innerText + ' is missing item 1'
doc.getElementById('li_1').remove()
doc.getElementById('li_2').setAttribute('style','color:red')

# generate the js updates
js = doc.render_js_updates()

# send the updates to the client
await ws_client.send(js)
```

<details>
  <summary>Click to see the Javascript code generated</summary>
  
```javascript
__domsync__["li_1"].remove();
__domsync__["li_0"].innerText = "item 0 is missing item 1";
__domsync__["li_2"].setAttribute("style","color:red");
```
</details>

On the Browser client side the generated javascript code is evaluated again that causes the DOM within ```<div id='domsync_root_id'>``` to change to this:

```html
<div id='domsync_root_id'>
  <h1 id='h1_0'>domsync demo</h1>
  <ul id='ul_0'>
    <li id='li_0'>item 0 is missing item 1</li>
    <li id='li_2' style='color:red'>item 2</li>
  </ul>
</div>
```

## Components

Components are subclasses of ```domsync.Component``` and allow you to create a reusable group of elements.
Each component takes a Document and an root_id as an input and adds it's elements on initialisation under the specified root element in the document.

### TableComponent

One use case for domsync is a table of data that we want to update efficiently cell-by-cell over websocket.

Using traditional methods, you would first need to design and implement a Python API to send out table update messages to your client,
possibly you would need to think about message format for your different UI components. Then you would need to build a client-side
Javascript application that receives the update messages, interprets them and renders/updates a table component. If you need to change anything on the Python side,
you will also have to change your Javascript client-side application, keeping these two in sync is a considerable amount of work.

Using domsync, you create an initial domsync document on the Python side. The first call to doc.render_js_updates() after creating the document
will contain all initialisation that is needed to create it on the Browser side, you send it over websocket, eval() it and your table is there.
Then you can change an individual cell of the table in the domsync document on the Python side. A subsequent call to doc.render_js_updates()
will generate minimal update message that contains the changes of the individual cell (not the whole document) that can be sent to the
browser over websocket where after eval() the changes will be reflected.

In this way you just saved yourself (1) having to implenent a separate UI logic in a separate language and (2) having to design and implement a Python API
updating your Browser components. You haven't saved (3) having to actually specify and update the DOM, you are now doing that on the Python side
instead of the Browser side, but you would have to do that anyways.

#### Example

```Python
from domsync import Document, TableComponent

# create a document under the id 'domsync_root_id'
doc = Document('domsync_root_id')

# add a Table
table = TableComponent(doc, 'domsync_root_id', ['Name', 'Age', 'Birthday', 'Hair'])
table.addRow('kyle',    ['Kyle Broflovski', '10', 'May 26',     'brown'])
table.addRow('eric',    ['Eric Cartman',    '10', 'July 1',     'brown'])
table.addRow('kenny',   ['Kenny McCormick', '10', 'March 22',   'blond'])
table.addRow('tolkien', ['Tolkien Black',   '10', 'June 20',    'black'])
table.addRow('stan',    ['Stan Marsh',      '10', 'October 19', 'black'])

# generate and send the updates to the client
js = doc.render_js_updates()
await ws_client.send(js)

# let's correct some mistakes in the table
table.updateCell('kyle','Hair','red')
table.updateCell('kenny','Age','9')

# generate and send the updates to the client
js = doc.render_js_updates()
await ws_client.send(js)
```

### Input Components and events callbacks

So far all the example showed a one-way synchronisation of changes on the Python side to the Browser side. However if an onclick or onchange event happens on the Browser side, we want to know about that and we want to be notified. domsync has implementations of input components that propagate the change event to the Python side by sending websocket messages from the Browser to Python and update the internal state of the Python DOM to reflect those changes. They also allow Python event handler functions to be added to the components. The input components at the time of writing are ```ButtonComponent```, ```TextInputComponent```, ```TextareaComponent```, ```SelectComponent```.

#### Example

This is what we have on the Python side:

```Python
from domsync import Document, ButtonComponent, TextInputComponent

def on_click(event):
    # print a message on each button push
    print('button got pressed')

def on_change(event):
    print('textinput value changed:' event['value'])
    # set the text of a div to the updated value of the text input
    doc = event['doc']
    doc.getElementById('id_div').innerText = doc.getElementById('id_textinput').value
    # NOTE: at this point domsync has updated the value of the textinput element,
    # therefore doc.getElementById('id_textinput').value is the same as event['value']

root_id = 'domsync_root_id'
doc = Document(root_id)

# add a <button> with a callback on_click
ButtonComponent(doc, root_id, text="press me", callback=on_click, id='id_button')

# add an <input type="text"> with a callback on_change
TextInputComponent(doc, root_id, value="hi there!", callback=on_change, id='id_textinput')

# add a <div> to show the value of the textinput
doc.getElementById(root_id).appendChild(doc.createElement('div', id='id_div'))

# we assume a websocket server is running on port 8888 and a client is connected to ws_client
while True:
    # get incoming event message
    msg = json.loads(await ws_client.recv())

    # give the incoming message to the doc, this will eventually trigger the callbacks of the components
    doc.handle_event(msg) 

    # send any updates to the client
    js = doc.render_js_updates()
    if len(js) > 0: await ws_client.send(js)
```

there is a full example of the input components in ```examples/example_input_components.py``` with the client-side html in ```examples/client.html```.
-->

