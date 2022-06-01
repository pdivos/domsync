# domsync

domsync makes it easy to create responsive web UIs in a Python server. You build and update your DOM document on the Python server side and the changes
to the DOM are synchronised efficiently to the Browser. This allows you to keep what the user sees in your Python process, close to your
existing Python logic, eliminating the need for creating and maintaining a separate Javascript client application and exposing an API
interface to communicate with the client. This technique is also known as Server Side Rendering (SSR).

The syntax of domsync closely follows the core Javascript syntax fo manipulating a DOM document: we got ```getElementById```, ```appendChildren```, ```setAttribute``` and so on.
Every change to the DOM document on the Python side generates Javascript code which is sent to the Browser and gets evaluated, resulting in the DOM on the Browser side
to be synchronised with the DOM on the Python side.

## Quickstart

On the Browser client side all we need is this minimal HTML:
```html
<html>
  <body><div id='domsync_root_id'></div></body> <!-- domsync will be rendered into this element -->
  <script type = "text/javascript">
    // changes are coming from websocket as javascript code and are eval'ed here to be applied
    socket = new WebSocket("ws://localhost:8888");
    socket.onmessage = function(event) { (function(){eval.apply(this, arguments);}(event.data)); };
  </script>
</html>
```

On the Python server side we create a domsync DOM Document, insert some elements and send the updates to the client:
```Python
from domsync import Document

# create a document under the id 'domsync_root_id'
doc = Document('domsync_root_id')

# add a <h1> header
doc.getElementById('domsync_root_id').appendChild(doc.createElement('h1', text='domsync demo'))

# add a <ul> list with three <li> items
doc.getElementById('domsync_root_id').appendChild(doc.createElement('ul', id='ul_0'))
doc.getElementById('ul_0').appendChild(doc.createElement('li', id='li_0', text='item 0'))
doc.getElementById('ul_0').appendChild(doc.createElement('li', id='li_1', text='item 1'))
doc.getElementById('ul_0').appendChild(doc.createElement('li', id='li_2', text='item 2'))    

js = doc.render_js_updates()

# websocket server is assumed to be running on port 8888 with one client connected

# send the updates to the client
await ws_client.send(js)
```

<details>
  <summary>Click to see the Javascript code generated</summary>
  
```javascript
var __domsync__ = [];
__domsync__["domsync_root_id"] = document.getElementById("domsync_root_id");
el = document.createElement('h1');el.setAttribute('id', 'h1_0');__domsync__['h1_0'] = el;
__domsync__["h1_0"].text = "domsync demo";
__domsync__["domsync_root_id"].appendChild(__domsync__["h1_0"]);
el = document.createElement('ul');el.setAttribute('id', 'ul_0');__domsync__['ul_0'] = el;
__domsync__["domsync_root_id"].appendChild(__domsync__["ul_0"]);
el = document.createElement('li');el.setAttribute('id', 'li_0');__domsync__['li_0'] = el;
__domsync__["li_0"].text = "item 0";
__domsync__["ul_0"].appendChild(__domsync__["li_0"]);
el = document.createElement('li');el.setAttribute('id', 'li_1');__domsync__['li_1'] = el;
__domsync__["li_1"].text = "item 1";
__domsync__["ul_0"].appendChild(__domsync__["li_1"]);
el = document.createElement('li');el.setAttribute('id', 'li_2');__domsync__['li_2'] = el;
__domsync__["li_2"].text = "item 2";
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
doc.getElementById('li_0').text = doc.getElementById('li_0').text + ' is missing item 1'
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
__domsync__["li_0"].text = "item 0 is missing item 1";
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
will contain all initialisation that is needed to create it on the JS side, you send it to the browser over websocket, eval() it and your table is there.
Then you can change an individual cell of the table in the domsync document on the Python side. A subsequent call to doc.render_js_updates()
will generate the minimal update messages that can again be sent to the browser over websocket where after eval() the changes will be reflected.

In this way you just saved yourself (1) having to implenent a separate UI logic in a separate language and (2) having to design and implement a Python API
updating your JS component. You haven't saved (3) having to actually specify and update the DOM, you are now doing that on the Python side
instead of the JS side, but you would have to do that anyways. Using domsync your updates are efficient because update messages only 
contain those elements that have actually changed, not the whole document.

Example:

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

So far all the example showed a one-way synchronisation of changes on the Python side to the Browser side. However if an onclick or onchange event happens on the Browser side, we want to know about that and we want to be notified. domsync has implementations of input components that propagate the change event to the Python side by sending websocket messages from the Browser to Python and update the internal state of the Python DOM to reflect those changes. They also allow Python event handler functions to be added to the components. The input components at the time of writing are ```TextInputComponent```, ```ButtonComponent```, ```TextareComponent```, ```SelectComponent```.

Example:

The client-side initial HTML needs to contain a ```ws_send``` function that allows the components to send change events to the server:

```html
<html>
  <body><div id='domsync_root_id'></div></body> <!-- domsync will be rendered into this element -->
  <script type = "text/javascript">
    // changes are coming from websocket as javascript code and are eval'ed here to be applied
    socket = new WebSocket("ws://localhost:8888");
    socket.onmessage = function(event) { (function(){eval.apply(this, arguments);}(event.data)); };
    // ws_send is called by the components to send event messages to the server
    function ws_send(msg) { socket.send(JSON.stringify(msg)); };
  </script>
</html>
```

This is what we have on the Python side:

```Python
from domsync import Document, Component, TableComponent, TextInputComponent, TextareaComponent, ButtonComponent, SelectComponent

# event callback on the Python side
def on_event(event):
    if event['id'] == 'id_button':
        # print a message on each button push
        print('button got pressed')
    elif event['id'] == 'id_textinput':
        print('textinput value changed:' event['value'])
        # set the text of a div to the updated value of the text input
        event['doc'].getElementById('id_div').text = event['value']

root_id = 'domsync_root_id'
doc = Document(root_id)

# add a <button> with a callback on_event
ButtonComponent(doc, root_id, text="press me", callback=on_event, id='id_button')

# add an <input type="text"> with a callback on_event
TextInputComponent(doc, root_id, value="hi there!", callback=on_event, id='id_textinput')

# add a <div> to show the value of the textinput
doc.getElementById(root_id).appendChild(doc.createElement('div', id='id_div'))

# we assume a websocket server is running and a client is connected
while True:
    # get incoming message
    msg = json.loads(await ws_client.recv())

    # give the incoming message to the doc, this will eventually trigger the callbacks of the components
    doc.handle_event(msg) 

    # send any updates to the client
    js = doc.render_js_updates()
    if len(js) > 0: await ws_client.send(js)
```

there is a full example of the input components in ```examples/example_input_components.py```

## Installation

To install the most recent version from github as a package on your system:

```console
pip install git+https://github.com/pdivos/domsync.git
```

To run the examples in Docker, without installing the package on your system:

```console
git clone https://github.com/pdivos/domsync.git
cd domsync
docker build -t domsync -f Dockerfile .
docker run -i --network host domsync python -u examples/example_input_components.py
```
