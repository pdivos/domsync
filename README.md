# domsync

domsync is a DOM implementation in Python, such that any manipulations to the document will generate
Javascript code that can be executed on a client browser achieving the same manipulations of the browser DOM.
domsync follows the Javascript DOM syntax, we got ```getElementById```, ```appendChildren``` and so on.

As a result you can use domsync to maintain and manipulate the browser Javascript DOM on the Python server side
and synchronise any changes that happen on the Python side to the browser Javascript side.
Thereby you can keep all of your UI logic in Python, there is no need to write a separate Javascript UI app
and more importantly there is no need to write UI API endpoints in Python and interface between the Javascript UI and the Python server:
all happens on the server that is seemlessly and efficiently rendered out to the client.

Right now this is one-way implementation: only that synchronises changes that happen on the Python side to the Javascript side.
If there are any changes on the JS side, most importantly an onclick or onchange event, thise are not synchronised back to the Python
side by the framework, that needs to be done separately.

## Typical use case

The typical use case is a table of data that we want to update cell-by cell over websocket.

Using traditional methods, you would need to create a table on the Javascript side either in HTML or with a JS library.
Then you would need create a websocket client on the JS side that interprets the update messages sent by the Python server.
You need to initialise the table and then process any updates, dig into the DOM or maybe using Jquery/React/Angular/... framework
to do it for you, in any case you need to build logic on the JS side. Then on the Python side you need to.
efficiently generate the initial messages sending down the whole table and then create update messages if any table cell changes.

Using domsync, you create an initial domsync document on the Python side. The first call to doc.render_js_updates() after creating the document
will contain all initialisation that is needed to create it on the JS side, you send it to the browser over websocket, eval() it and your table is there.
Then, if there is a change, you change the cell of the table in the domsync documenton the Python side. A subsequent call to doc.render_js_updates()
will generate the minimal update messages that can again be sent to the browser over websocket where after eval() the changes will be reflected.
You just saved yourself (1) having to implenent a separate UI logic in a separate language and (2) having to write an API with specialised messages
updating your specialised component. You haven't saved (3) having to actually do the update in the DOM, you are now doing that on the Python side
instead of the JS side, but you would have to do that anyways. Using domsync your update is still efficient because update messages only 
contain those elements that have actually changed, not the whole document.

## Example

Initial DOM on the client browser side:
```html
<html><body>
<div id='domsync_root_id'></div>
</body></html>
```

Create a domsync document on the Python side and insert some elements:
```Python
from domsync import Document

# create a document under the id 'domsync_root_id'
doc = Document('domsync_root_id')

# add a <h1> header
doc.getElementById('domsync_root_id').appendChild(doc.createElement('h1', text='domsync demo'))

# add a <ul> list with three <li> items
doc.getElementById('domsync_root_id').appendChild(doc.createElement('ul', id='id_ul'))
doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_0', text='item 0'))
doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_1', text='item 1'))
doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_2', text='item 2'))    

js = doc.render_js_updates()
```

<details>
  <summary>Click to see the Javascript code generated</summary>
  
```javascript
var __domsync__ = [];
__domsync__["domsync_root_id"] = document.getElementById("domsync_root_id");
el = document.createElement('h1');el.setAttribute('id', 'id_h1');__domsync__['id_h1'] = el;
__domsync__["id_h1"].text = "domsync demo";
__domsync__["domsync_root_id"].appendChild(__domsync__["id_h1"]);
el = document.createElement('ul');el.setAttribute('id', 'id_ul');__domsync__['id_ul'] = el;
__domsync__["domsync_root_id"].appendChild(__domsync__["id_ul"]);
el = document.createElement('li');el.setAttribute('id', 'id_li_0');__domsync__['id_li_0'] = el;
__domsync__["id_li_0"].text = "item 0";
__domsync__["id_ul"].appendChild(__domsync__["id_li_0"]);
el = document.createElement('li');el.setAttribute('id', 'id_li_1');__domsync__['id_li_1'] = el;
__domsync__["id_li_1"].text = "item 1";
__domsync__["id_ul"].appendChild(__domsync__["id_li_1"]);
el = document.createElement('li');el.setAttribute('id', 'id_li_2');__domsync__['id_li_2'] = el;
__domsync__["id_li_2"].text = "item 2";
__domsync__["id_ul"].appendChild(__domsync__["id_li_2"]);
```
</details>

Once the generated javascript is sent to the client browser and evaluated, the DOM will change to this:

```html
<html><body>
<div id='domsync_root_id'>
    <h1 id='id_h1'>domsync demo</h1>
    <ul id='id_ul'>
        <li id='id_li_0'>item 0</li>
        <li id='id_li_1'>item 1</li>
        <li id='id_li_2'>item 2</li>
    </ul>
</div>
</body></html>
```

Now we can do more manipulations on the Python side:
```Python
# change the first items text, remove the second item, change the third items attribute
doc.getElementById('id_li_0').text = doc.getElementById('id_li_0').text + ' is missing item 1'
doc.getElementById('id_li_1').remove()
doc.getElementById('id_li_2').setAttribute('style','color:red')

# generate the js updates
js = doc.render_js_updates()
```

<details>
  <summary>Click to see the Javascript code generated</summary>
  
```javascript
__domsync__["id_li_1"].remove();
__domsync__["id_li_0"].text = "item 0 is missing item 1";
__domsync__["id_li_2"].setAttribute("style","color:red");
```
</details>

Once the generated javascript is sent to the client browser and evaluated, the DOM will change to this:

```html
<html><body>
<div id='domsync_root_id'>
    <h1 id='id_h1'>domsync demo</h1>
    <ul id='id_ul'>
        <li id='id_li_0'>item 0 is missing item 1</li>
        <li id='id_li_2' style='color:red'>item 2</li>
    </ul>
</div>
</body></html>
```
