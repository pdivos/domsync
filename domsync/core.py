# copied from https://way2tutorial.com/html/tag/index.php
_valid_tags = ["a","abbr","address","area","b","base","bdo","blockquote","body","br","button","caption","cite","code","col","colgroup","dd","del","dfn","div","dl","dt","em","fieldset","form","h1","h2","h3","h4","h5","h6","head","hr","html","i","iframe","img","input","ins","kbd","label","legend","li","link","map","menu","meta","noscript","object","ol","optgroup","option","p","param","pre","q","s","samp","script","select","small","span","strong","style","sub","sup","table","tbody","td","textarea","tfoot","th","thead","title","tr","u","ul","var"]

# https://www.w3schools.com/jsref/dom_obj_event.asp
_events = ["abort","afterprint","animationend","animationiteration","animationstart","beforeprint","beforeunload","blur","canplay","canplaythrough","change","click","contextmenu","copy","cut","dblclick","drag","dragend","dragenter","dragleave","dragover","dragstart","drop","durationchange","ended","error","focus","focusin","focusout","fullscreenchange","fullscreenerror","hashchange","input","invalid","keydown","keypress","keyup","load","loadeddata","loadedmetadata","loadstart","message","mousedown","mouseenter","mouseleave","mousemove","mouseover","mouseout","mouseup","mousewheel","offline","online","open","pagehide","pageshow","paste","pause","play","playing","popstate","progress","ratechange","resize","reset","scroll","search","seeked","seeking","select","show","stalled","storage","submit","suspend","timeupdate","toggle","touchcancel","touchend","touchmove","touchstart","transitionend","unload","volumechange","waiting","wheel",]

_supported_input_types = ['text','password']

class _Element(dict): # _Element is private because we are only meant to create an instance through Document.createElement
    def __init__(self, document, _id, tag):
        assert tag in _valid_tags
        super(_Element, self).__init__({
            'document': document,
            'id': _id,
            'tag': tag,
            'children': [],
            'parent': None,
            'attributes': {},
            'text': None,
            'value': None,
        })

    def _js_push(self, line):
        self['document']._js_push(line)

    def appendChild(self, el_child):
        """
        javascript Element.appendChild
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
        javascript Element.insertBefore
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
        javascript Element.remove
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
        javascript Element.getAttribute
        """
        assert attrib != 'id' and type(attrib) is str
        return self['attributes'].get(attrib, default)

    def setAttribute(self, attrib, value):
        """
        javascript Element.setAttribute
        """
        assert str_is_safe(attrib)
        assert attrib != 'id' and type(attrib) is str and type(value) is str
        if attrib.startswith('on'): assert attrib[2:] not in _events, "please use addEventListener to add an event"
        if attrib.startswith('on'):
            # https://stackoverflow.com/questions/97578/how-do-i-escape-a-string-inside-javascript-code-inside-an-onclick-handler
            # need to escape quotes in code string
            value = str_escape_for_js(value)
        if self['attributes'].get(attrib) != value:
            self['attributes'][attrib] = value
            self._js_push(f"""__domsync__["{self['id']}"].setAttribute("{attrib}","{value}");\n""")

    def removeAttribute(self, attrib):
        """
        javascript Element.removeAttribute
        """
        assert attrib != 'id' and type(attrib) is str
        del self['attributes'][attrib]
        self._js_push(f"""__domsync__["{self['id']}"].removeAttribute("{attrib}");\n""")

    def addEventListener(self, event, callback, js_value_getter = None):
        assert event in _events
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
        self['document'].register_callback(self['id'], event, callback)
        self._js_push(f"""__domsync__["{self['id']}"].addEventListener("{event}",{callback_js});\n""")

    def _setInnerHTML(self, innerHTML):
        """
        javascript Element.innerHTML = innerHTML
        """
        assert type(innerHTML) is str
        # NOTE: in our representation we store innerHTML in self['text']
        #       also, we allow no innerHTML setting if the element has children
        assert len(self['children']) == 0, "cannot have children if setting innerHTML"
        if innerHTML != self['text']:
            self['text'] = innerHTML
            self['innerHTML_flag'] = True if len(innerHTML)>0 else False
            self._js_push(f"""__domsync__["{self['id']}"].innerHTML = "{innerHTML}";\n""")

    def _getInnerHTML(self):
        """
        javascript Element.innerHTML
        """
        assert self['innerHTML_flag'] == True, "can only access innerHTML if it was set with innerHTML"
        return self['text']

    def _setText(self, text):
        """
        javascript Element.text = text
        """
        assert type(text) is str, "we don't allow any other types than str to be stored in the DOM because we didn't want to make parsing/rendering/formatting part of the DOM, that should happen outside"
        if text != self['text']:
            self['text'] = text
            self._js_push(f"""__domsync__["{self['id']}"].innerText = `{text}`;\n""")

    def _setValue(self, value):
        """
        javascript Element.text = text
        """
        assert type(value) is str, "we don't allow any other types than str to be stored in the DOM because we didn't want to make parsing/rendering/formatting part of the DOM, that should happen outside"
        if value != self['value']:
            self['value'] = value
            self._js_push(f"""__domsync__["{self['id']}"].value = `{value}`;\n""")

    def __setattr__(self, name, value):
        if name == 'innerHTML':
            self._setInnerHTML(value)
        elif name == 'text':
            self._setText(value)
        elif name == 'value':
            self._setValue(value)
        else:
            raise Exception('unsupported attribute: ' + str(name) + ' of type ' + str(type(name)))
    
    def __getattr__(self, name):
        if name == 'innerHTML':
            return self._getInnerHTML()
        elif name == 'text':
            return self['text']
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
    def __init__(self, root_id):
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
        return self['root_id']

    def getElementById(self, _id):
        """
        javascript document.getElementById
        Returns the element that has the ID attribute with the specified value
        """
        assert _id in self['elements_by_id'], "unknown id: " + str(_id)
        return self['elements_by_id'][_id]

    def getElementsByClassName(self, className):
        """
        javascript document.getElementsByClassName
        Returns an HTMLCollection containing all elements with the specified class name
        """
        classNames = className.split(' ')
        return [el for el in self['elements_by_id'].values() if el.getAttribute('class') in classNames]

    def getElementsByName(self, name):
        """
        javascript document.getElementsByName
        Returns an live NodeList containing all elements with the specified name
        """
        return [el for el in self['elements_by_id'].values() if el.getAttribute('name') == name]

    def getElementsByTagName(self, tag):
        """
        javascript document.getElementsByTagName
        Returns an HTMLCollection containing all elements with the specified tag name
        """
        return [el for el in self['elements_by_id'].values() if (el.tagName == tag or tag == '')]

    def createElement(self, tagName, id=None, text=None, value=None, attributes=None):
        """
        javascript document.createElement
        Returns a new element
        NOTE: differences between javascript and our implementation:
         - if :param id: is provided it will be set as the id of the element.
           id can only be set in this way, later it's not allowed to use setAttribute('id','new_id')
         - if :param text: is provided, it will be set as the element's text
         - if :param attributes: is provided, it will be set as the element's attributes
        """
        if id is None:
            id = self._get_autoinc_id()
        assert id not in self['elements_by_id']
        if tagName == 'input':
            assert type(attributes) is dict and attributes.get('type') in _supported_input_types
        el = _Element(self, id, tagName)
        self['elements_by_id'][id] = el
        self._js_push(f"""__domsync__["{el['id']}"]=document.createElement("{el['tag']}");__domsync__["{el['id']}"].setAttribute("id","{el['id']}");\n""")
        if text is not None:
            assert type(text) is str
            el.text = text
        if value is not None:
            el.value = value
        if attributes is not None:
            assert type(attributes) is dict
            for attrib, value in attributes.items():
                el.setAttribute(attrib, value)
        return el

    def render_js_updates(self):
        """
        returns generated js code that contains the updates to the DOM that happened since the last call to this method.
        the return value can be sent to the client browser and eval()-ed there to apply the same changes that happened in the Document doc
        """
        res = self['js_buffer']
        self['js_buffer'] = []
        return ''.join(res)

    def render_js_full(self):
        """
        returns js that creates the full snapshot from scratch
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
            new_doc.createElement(old_el.tagName, id=old_el.id, text=old_el.text, value=old_el.value, attributes=old_el.attributes)
            new_el = new_doc.getElementById(id)
            for event, callback in self['callbacks'].get(id,{}).items():
                new_el.addEventListener(event, callback)
            new_parent = new_doc.getElementById(parent_id)
            new_parent.appendChild(new_el)
        return new_doc.render_js_updates()

    def handle_event(self, msg):
        """
        use this function to pass in incoming websocket messages that were triggered by events on the client
        :param msg: is an event message generated on the client side containing the 'id' and name of the 'event'
        :returns: the list of return values of the list of callbacks that are added to the given event
        """
        assert msg['domsync']
        id = msg['id']
        msg['doc'] = self
        if msg['event'] in self['callbacks'].get(id,{}):
            callback = self['callbacks'][id][msg['event']]
            return callback(msg)

    def register_callback(self, id, event, callback):
        """
        use this function to register an event handler callback
        """
        self['callbacks'].setdefault(id,{})
        assert event not in self['callbacks'][id]
        self['callbacks'][id][event] = callback

class Component(dict):
    """
    a Component is something that writes child elements under a parent_id of a document and may later manipulate these elements
    the Component object essentially contains two kinds of info:
    1. it kinda owns the child elements that inserted within the doc
    2. it has it's own data in the object itself
    it's up to the Component implementation to decide what to store where.
    if it's slim it's OK to store all data in the Document, if it's more complex it might make sense to store some of the data in the Component objec.
    """
    def __init__(self, doc, parent_id, id = None):
        assert type(doc) is Document and type(parent_id) is str and parent_id in doc['elements_by_id']
        if id is None:
            id = doc._get_autoinc_id()
        super(Component, self).__init__({
            'doc': doc,
            'parent_id': parent_id,
            'id': id,
        })

    def getElement(self):
        return self['doc'].getElementById(self['id'])

    def getRootId(self):
        return self['id']

def str_is_safe(s):
    return '"' not in s and "'" not in s and "`" not in s

def str_escape_for_js(s):
    return s.replace("'",r"\x27").replace('"',r"\x22")