# copied from https://way2tutorial.com/html/tag/index.php
_valid_tags = ["a","abbr","address","area","b","base","bdo","blockquote","body","br","button","caption","cite","code","col","colgroup","dd","del","dfn","div","dl","dt","em","fieldset","form","h1","h2","h3","h4","h5","h6","head","hr","html","i","iframe","img","input","ins","kbd","label","legend","li","link","map","menu","meta","noscript","object","ol","optgroup","option","p","param","pre","q","s","samp","script","select","small","span","strong","style","sub","sup","table","tbody","td","textarea","tfoot","th","thead","title","tr","u","ul","var"]

# https://www.w3schools.com/jsref/dom_obj_event.asp
_valid_events = ["abort","afterprint","animationend","animationiteration","animationstart","beforeprint","beforeunload","blur","canplay","canplaythrough","change","click","contextmenu","copy","cut","dblclick","drag","dragend","dragenter","dragleave","dragover","dragstart","drop","durationchange","ended","error","focus","focusin","focusout","fullscreenchange","fullscreenerror","hashchange","input","invalid","keydown","keypress","keyup","load","loadeddata","loadedmetadata","loadstart","message","mousedown","mouseenter","mouseleave","mousemove","mouseover","mouseout","mouseup","mousewheel","offline","online","open","pagehide","pageshow","paste","pause","play","playing","popstate","progress","ratechange","resize","reset","scroll","search","seeked","seeking","select","show","stalled","storage","submit","suspend","timeupdate","toggle","touchcancel","touchend","touchmove","touchstart","transitionend","unload","volumechange","waiting","wheel",]

class _Element(dict): # _Element is private because we are only meant to create an instance through Document.createElement
    """:class:`domsync.core._Element` is analogous to the Javascript Element which represents an individual HTML element.
    The name of the class starts with an underscore, expressing the fact that this class should not be instantiated by the user,
    instead all instances of this class are created by :meth:`domsync.Document.createElement`.

    :param document: document to create the element within
    :type document: :class:`domsync.Document`

    :param id: unique id of the element
    :type id: str

    :param tagName: tag name of the element
    :type tagName: str

    :class attributes:

    * **innerText** - sets and gets the element's innerText, analogous to Javascript element.innerText
    * **value** - sets and gets the element's value, analogous to Javascript element.value
    * **tagName** - gets the element's tagName, analogous to Javascript element.tagName
    * **children** - gets the element's list of child elements, analogous to Javascript element.children
    * **firstElementChild** - gets the element's first child element, analogous to Javascript element.firstElementChild
    * **lastElementChild** - gets the element's last child element, analogous to Javascript element.lastElementChild
    * **attributes** - gets the element's dictionary of attributes
    * **id** - gets the element's id

    """
    def __init__(self, document, id, tagName):
        assert tagName in _valid_tags
        super(_Element, self).__init__({
            'document': document,
            'id': id,
            'tag': tagName,
            'children': [],
            'parent': None,
            'attributes': {},
            'innerText': None,
            'value': None,
        })

    def _js_push(self, line):
        self['document']._js_push(line)

    def appendChild(self, el_child):
        """
        analogous to Javascript Element.appendChild

        :param el_child: child element to append
        :type el_child: :class:`domsync.core._Element`

        :returns: None
        """
        assert isinstance(el_child, _Element)
        assert not self.get('innerHTML_flag',False), "this element has some innerHTML, remove it first by self.innerHTML = "" before adding children"
        assert el_child is self['document'].getElementById(el_child['id'])
        assert el_child.parentElement is None, "child is already under a parent"
        el_child['parent'] = self
        self['children'].append(el_child)
        self._js_push(f"""__domsync__["{self['id']}"].appendChild(__domsync__["{el_child['id']}"]);\n""")

    def insertBefore(self, el_child_to_insert, el_child_before):
        """
        inserts an element as a child before an existing child element

        analogous to Javascript Element.insertBefore

        :returns: None
        """
        assert isinstance(el_child_to_insert, _Element)
        assert not self.get('innerHTML_flag',False), "this element has some innerHTML, remove it first by self.innerHTML = "" before adding children"
        assert el_child_to_insert.parentElement is None, "child is already under a parent"
        el_child_to_insert['parent'] = self
        found = False
        for i in range(len(self['children'])):
            if self['children'][i] is el_child_before:
                found = True
                break
        assert found
        self['children'].insert(i, el_child_to_insert)
        self._js_push(f"""__domsync__["{self['id']}"].insertBefore(__domsync__["{el_child_to_insert['id']}"], __domsync__["{el_child_before['id']}"]);\n""")

    def remove(self):
        """
        removes the element

        analogous to Javascript Element.remove

        :returns: None
        """
        _id = self['id']
        assert _id in self['document']['elements_by_id']
        parent = self.parentElement
        len_before = len(parent['children'])
        parent['children'] = [el for el in parent['children'] if el['id']!=_id]
        len_after = len(parent['children'])
        assert len_after == len_before - 1, len_before
        self._js_push(f"""__domsync__["{self['id']}"].remove();\n""")

        del self['document']['elements_by_id'][_id]
        if _id in self['document']['callbacks']:
            del self['document']['callbacks'][_id]
        to_remove = [el['id'] for el in self['children']]
        while len(to_remove):
            _id = to_remove.pop(0)
            element = self['document']['elements_by_id'][_id]
            del self['document']['elements_by_id'][_id]
            if _id in self['document']['callbacks']:
                del self['document']['callbacks'][_id]
            to_remove.extend([el['id'] for el in element['children']])

    def getAttribute(self, attrib, default = None):
        """
        gets an attribute of an element

        analogous to Javascript Element.getAttribute

        :param attrib: name of the attribute to return
        :type attrib: str

        :param default: Optional, value to return in case the attribute is not available

        :returns: str, the value of the attribute if the attribute exists, otherwise the value of the ``default`` argument
        """
        assert attrib != 'id' and type(attrib) is str
        return self['attributes'].get(attrib, default)

    def setAttribute(self, attrib, value):
        """
        sets the attribute of an element

        analogous to Javascript Element.setAttribute

        :param attrib: name of the attribute to set
        :type attrib: str

        :param value: value of the attribute to set
        :type value: str

        :returns: None
        """
        assert str_is_safe(attrib)
        assert attrib != 'id' and type(attrib) is str and type(value) is str
        if attrib.startswith('on'): assert attrib[2:] not in _valid_events, "please use addEventListener to add an event"
        if attrib.startswith('on'):
            # https://stackoverflow.com/questions/97578/how-do-i-escape-a-string-inside-javascript-code-inside-an-onclick-handler
            # need to escape quotes in code string
            value = str_escape_for_js(value)
        if self['attributes'].get(attrib) != value:
            self['attributes'][attrib] = value
            self._js_push(f"""__domsync__["{self['id']}"].setAttribute("{attrib}","{value}");\n""")

    def removeAttribute(self, attrib):
        """
        removes the given attribute

        analogous to Javascript Element.removeAttribute

        :param attrib: name of the attribute to remove
        :type attrib: str

        :returns: None
        """
        assert attrib != 'id' and type(attrib) is str
        del self['attributes'][attrib]
        self._js_push(f"""__domsync__["{self['id']}"].removeAttribute("{attrib}");\n""")

    def addEventListener(self, event, callback, js_value_getter = None):
        """
        adds an event listener to the element

        analogous to Javascript addEventListener

        :param event: name of the event to listen to, see https://www.w3schools.com/jsref/dom_obj_event.asp for a list of valid events
        :type event: str

        :param callback: | the callback function to be called when the event happens. the function must take one argument which is a dict containing the details of the message:
                         | 'event': name of the event, one of https://www.w3schools.com/jsref/dom_obj_event.asp
                         | 'id': id of the element that the event happened on
                         | 'doc': :class:`domsync.Document` instance
                         | 'value': value returned as a result of evaluating js_value_getter (see below)
        :type callback: Callable(dict)

        :param js_value_getter: | a javascript expression that is executed in the context of the event and the return value of which is retrned in the 'value' field of the event message.
                                | A good example is ``'this.value'`` in case of the 'input' event of an <input type='text'> element, this will retun the current changed value of the input.
                                | Another example would be ``'this.options[this.selectedIndex].value'`` in case of the 'input' event of a <select> element, this will retun the current changed value of the selection.
                                | In case of a 'click' event of a <button> there is no need to specify a js_value_getter because the click event doesn't carry any relevant value (apart form the fact that the event happened).
        :type js_value_getter: str

        :returns: None
        """
        assert event in _valid_events
        event_msg = {
            'domsync':True,
            'event':event,
            'id': self['id'],
            'value': js_value_getter,
        }
        import json
        event_msg = json.dumps(event_msg)
        if js_value_getter is not None:
            event_msg = event_msg.replace('"'+js_value_getter+'"',js_value_getter)
        callback_js = r"function(){ws_send("+event_msg+r")}"
        self['document']._register_callback(self['id'], event, callback)
        self._js_push(f"""__domsync__["{self['id']}"].addEventListener("{event}",{callback_js});\n""")

    def _setInnerHTML(self, innerHTML):
        """
        analogous to Javascript Element.innerHTML = innerHTML
        """
        assert type(innerHTML) is str
        # NOTE: in our representation we store innerHTML in self['innerText']
        #       also, we allow no innerHTML setting if the element has children
        assert len(self['children']) == 0, "cannot have children if setting innerHTML"
        if innerHTML != self['innerText']:
            self['innerText'] = innerHTML
            self['innerHTML_flag'] = True if len(innerHTML)>0 else False
            self._js_push(f"""__domsync__["{self['id']}"].innerHTML = "{innerHTML}";\n""")

    def _getInnerHTML(self):
        """
        analogous to Javascript Element.innerHTML
        """
        assert self['innerHTML_flag'] == True, "can only access innerHTML if it was set with innerHTML"
        return self['innerText']

    def _setText(self, text):
        """
        analogous to Javascript Element.innerText = text
        """
        assert type(text) is str, "we don't allow any other types than str to be stored in the DOM because we didn't want to make parsing/rendering/formatting part of the DOM, that should happen outside"
        if text != self['innerText']:
            self['innerText'] = text
            self._js_push(f"""__domsync__["{self['id']}"].innerText = `{text}`;\n""")

    def _setValue(self, value):
        """
        analogous to Javascript Element.value = value
        """
        assert type(value) is str, "we don't allow any other types than str to be stored in the DOM because we didn't want to make parsing/rendering/formatting part of the DOM, that should happen outside"
        if value != self['value']:
            self['value'] = value
            self._js_push(f"""__domsync__["{self['id']}"].value = `{value}`;\n""")

    def __setattr__(self, name, value):
        if name == 'innerHTML':
            self._setInnerHTML(value)
        elif name == 'innerText':
            self._setText(value)
        elif name == 'value':
            self._setValue(value)
        else:
            raise Exception('unsupported attribute: ' + str(name) + ' of type ' + str(type(name)))
    
    def __getattr__(self, name):
        if name == 'innerHTML':
            return self._getInnerHTML()
        elif name == 'innerText':
            return self['innerText']
        elif name == 'value':
            return self['value']
        elif name == 'tagName':
            return self['tag']
        elif name == 'children':
            return self['children']
        elif name == 'firstElementChild':
            return self['children'][0]
        elif name == 'lastElementChild':
            return self['children'][-1]
        elif name == 'attributes':
            return self['attributes']
        elif name == 'id': # NOTE: this is not in JS, only for us for convenience. in JS should be self.getAttribute('id')
            return self['id']
        elif name == 'parentElement':
            return self['parent']
        else:
            raise Exception('unsupported attribute: ' + str(name) + ' of type ' + str(type(name)))

class Document(dict):
    """:class:`domsync.Document` is analogous to the Javascriot DOM document which contains a tree of :class:`domsync.core._Element` objects.
    Every manipulation to the document generates Javascript code that when sent to the Browser client and evaluated results in the same DOM changes on the client side
    that happened in the :class:`domsync.Document`.

    :param root_id: id of the element in the client-side HTML where domsync should render
    :type root_id: str
    """
    def __init__(self, root_id):
        """Constructor method
        """
        root_tag = 'div' # doesn't matter what the tag of the root element actually is, we store it as div in our representatiopn just to have a valid tag
        root_el = _Element(self, root_id, root_tag)
        super(Document, self).__init__({
            'elements_by_id': { # returns the element of an id
                root_id: root_el,
            },
            'js_buffer': [],
            'id_autoinc': 0,
            'root_id': root_id,
            'callbacks': {},
        })
        self._js_push("var __domsync__ = [];\n")
        self._js_push(f"""__domsync__["{root_id}"] = document.getElementById("{root_id}");\n""")

    def _js_push(self, line):
        self['js_buffer'].append(line)

    def _get_autoinc_id(self):
        _id = '__domsync_el_'+str(self['id_autoinc'])
        self['id_autoinc'] += 1
        return _id

    def getRootId(self):
        """Returns the id of the root element that was passed on initialisation.

        :return: the id of the root element
        :rtype: str
        """
        return self['root_id']

    def getElementById(self, id, strict=True):
        """
        Returns the element of the given ID

        analogous to Javascript document.getElementById

        :param id: id of the element
        :type id: str

        :param strict: optional, if True (default), then an exception is thrown if the provided id doesn't exist. if False, then None is returned if the id doesn't exist
        :type strict: bool

        :return: the element of the provided id or None if the element doesn't exist and strict is False
        :rtype: :class:`domsync.core._Element`
        """
        if strict:
            assert id in self['elements_by_id'], "unknown id: " + str(id)
            return self['elements_by_id'][id]
        else:
            return self['elements_by_id'].get(id)

    def getElementsByClassName(self, className):
        """
        Returns a list of elements with the specified class name

        analogous to Javascript document.getElementsByClassName

        :param className: class name of the element
        :type className: str

        :return: the elements of the given class name
        :rtype: list of :class:`domsync.core._Element`
        """
        classNames = className.split(' ')
        return [el for el in self['elements_by_id'].values() if el.getAttribute('class') in classNames]

    def getElementsByTagName(self, tagName):
        """
        Returns a list of elements with the specified tag name

        analogous to Javascript document.getElementsByTagName

        :param tagName: tag name of the element
        :type tagName: str

        :return: the elements of the given tag
        :rtype: list of :class:`domsync.core._Element`
        """
        return [el for el in self['elements_by_id'].values() if (el.tagName == tagName or tagName == '')]

    def createElement(self, tagName, id=None, innerText=None, value=None, attributes=None):
        """
        Creates a new element in the :class:`domsync.Document` but doesn't add it as a child to any existing elements, that needs to be done separately using ``appendChild``.

        analogous to Javascript document.createElement

        This is the only way to create a new element because each element needs to be registered with the :class:`domsync.Document`.
        This is the reason why the name of :class:`domsync.core._Element` starts with an  underscore character signalling that it's a private class that is not meant
        to be instantiated by the user.

        :param tagName: tag name of the element to be created
        :type tagName: str

        :param id: Optional, unique id of the new element. if not provided, an automatically generated unique id will be used.
                   Note that this is a difference between domsync and Javascript: in domsync every element has a unique id while in Javascript not necessarily.
        :type id: str

        :param innerText: Optional, if provided this will be set as the innerText of the newly created element.
                          equivalent to later setting the .innerText attribute of the element.
        :type innerText: str

        :param value: Optional, if provided this will be set as the value attribute of the newly created element.
                      Typically only used in case of <input type='text'> elements.
                      equivalent to later setting the .value attribute of the element.
        :type value: str

        :param attributes: Optional, if provided these attributes will be set on the element.
                        equivalent to later using the setAttribute method on the element.
        :type attributes: dict

        :return: the newly created element
        :rtype: :class:`domsync.core._Element`
        """
        if id is None:
            id = self._get_autoinc_id()
        assert id not in self['elements_by_id']
        el = _Element(self, id, tagName)
        self['elements_by_id'][id] = el
        self._js_push(f"""__domsync__["{el['id']}"]=document.createElement("{el['tag']}");__domsync__["{el['id']}"].setAttribute("id","{el['id']}");\n""")
        if innerText is not None:
            assert type(innerText) is str
            el.innerText = innerText
        if value is not None:
            el.value = value
        if attributes is not None:
            assert type(attributes) is dict
            for attrib, value in attributes.items():
                el.setAttribute(attrib, value)
        return el

    def render_js_updates(self):
        """
        Returns the Javascript code changes that accummulated in the internal buffer of the :class:`domsync.Document` due to any manipulations since the last call to this function.
        This is the method for generating the Javascript code updates that can be sent to the client.
        :class:`domsync.domsync_server.DomsyncServer` uses this behind the scenes, so you only need to deal with this function if you want to use your own server.

        :return: the Javascript code generated since the last call to this function.
        :rtype: str
        """
        res = self['js_buffer']
        self['js_buffer'] = []
        return ''.join(res)

    def render_js_full(self):
        """
        Returns a full snapshot of Javascript code that represents the current state of the :class:`domsync.Document` from scratch, not just the updates since the last time.
        It is useful when you have one :class:`domsync.Document` instance in your memory and want to show the same instance to every users, like for example a read-only dashboard.
        In that case you can update your :class:`domsync.Document` and send updates to already connected clients using the ``render_js_updates`` method, but whenever a new client connects
        you can use this method to send an initial full snapshot of the current state of the doc. Again, this only needs to be used if you decide to keep one :class:`domsync.Document`
        instance for all users, as opposed to one :class:`domsync.Document` for each user.
        If you use :class:`domsync.domsync_server.DomsyncServer`, you don't need to deal with this method because the server maintains one :class:`domsync.Document`
        for each client and send updates behind the scenes automatically anyways.
        You only need to deal with this method if you decide to use your own server.

        :return: Javascript code containnig the full current state of the document.
        :rtype: str
        """
        assert self['js_buffer'] == [], 'can only call render_js_full right after render_js_updates'
        new_doc = Document(self.getRootId())
        ids_to_copy = [el.id for el in self.getElementById(self.getRootId()).children]
        while len(ids_to_copy):
            id = ids_to_copy.pop(0)
            old_el = self.getElementById(id)
            ids_to_copy.extend([el.id for el in old_el.children])
            parent_id = old_el.parentElement.id
            assert type(parent_id) is str
            new_doc.createElement(old_el.tagName, id=old_el.id, innerText=old_el.innerText, value=old_el.value, attributes=old_el.attributes)
            new_el = new_doc.getElementById(id)
            for event, callback in self['callbacks'].get(id,{}).items():
                new_el.addEventListener(event, callback)
            new_parent = new_doc.getElementById(parent_id)
            new_parent.appendChild(new_el)
        return new_doc.render_js_updates()

    def handle_event(self, msg):
        """
        The way event listeners work with domsync is that we set the event listener of an element using :meth:`domsync.core._Element.addEventListener` which
        on the client side causes the ``ws_send`` Javascript function to be executed which sends back a message to the server containing the
        details of the event. When that message arrives to the server, this method needs to be called with the message as an argument which
        eventually triggers the callback function to be executed that was added using the :meth:`domsync.core._Element.addEventListener` method.

        You only need to deal with this if you are using your own server. If you use :class:`domsync.domsync_server.DomsyncServer`,
        this is called automatically behind the scenes.

        :param msg: | is an event message generated on the client side containing:
                    | 'id' of the element that generated the event
                    | 'event' name of the HTML event that happened (see https://www.w3schools.com/jsref/dom_obj_event.asp for the list of events)
                    | 'value' associated with the event as defined when the event was added using the ``js_value_getter`` argument of :meth:`domsync.core._Element.addEventListener`
        :type msg: dict

        :returns: whatever the callback function returns that was added using :meth:`domsync.core._Element.addEventListener`
        """
        assert msg['domsync']
        if msg['event'] in self['callbacks'].get(msg['id'],{}):
            msg['doc'] = self
            callback = self['callbacks'][msg['id']][msg['event']]
            return callback(msg)

    def _register_callback(self, id, event, callback):
        """
        use this function to register an event handler callback
        """
        assert id in self['elements_by_id']
        self['callbacks'].setdefault(id,{})
        assert event not in self['callbacks'][id]
        self['callbacks'][id][event] = callback

def str_is_safe(s):
    return '"' not in s and "'" not in s and "`" not in s

def str_escape_for_js(s):
    return s.replace("'",r"\x27").replace('"',r"\x22")