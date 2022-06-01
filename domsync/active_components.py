"""
active domsync components are two-way components that render info both from server->client and also take input from client->server
on the client side they add onclick, onchange, ... event handlers that will cause a websocket message sent from the client
the client-side html hosting domsync must be capable of executing a function called 'ws_send'
handling of the websocket messages is not done by the domsync library, needs to be done by the python server separately
"""
import json
from domsync.core import Component, str_is_safe
from functools import partial

class ButtonComponent(Component):
    """
    puts an <div> in the dom.
    the onclick event of that element will generate events on the client side that are sent to us and triggers the callback to be called
    """
    def __init__(self, doc, parent_id, text, callback, id=None, event_additional_props = {}):
        assert callable(callback)
        super(ButtonComponent, self).__init__(doc, parent_id, id=id)
        doc.register_callback(self.getRootId(), callback, component = self)
        button = doc.createElement('button',id=self.getRootId(),text=text)
        doc.getElementById(parent_id).appendChild(button)
        event_msg = {
            'domsync':True,
            'event':'onclick',
            'id': self.getRootId(),
        }
        assert set(event_msg.keys()).intersection(set(event_additional_props.keys())) == set()
        event_msg.update(event_additional_props)
        event_msg = json.dumps(event_msg)
        button.setAttribute('onclick', "ws_send("+event_msg+")")

    def getValue(self):
        return self.getElement().text

class TextInputComponent(Component):
    """
    puts an <input type="text"> in the dom.
    the oninput event of that element will generate events on the client side that are sent to us and triggers the callback to be called
    the component object stores the updated value of the input in self.value which is read-only because it's update dby the client only
    """
    def __init__(self, doc, parent_id, value, callback, id=None, event_additional_props = {}):
        super(TextInputComponent, self).__init__(doc, parent_id, id=id)
        def my_callback(_self, _callback, event):
            event['component'].getElement()['value'] = event['value']
            return _callback(event) if _callback is not None else None
        doc.register_callback(self.getRootId(), partial(my_callback, self, callback), component = self)
        input_text = doc.createElement('input', id=self.getRootId(), attributes={'type':'text'}, value=value)
        doc.getElementById(parent_id).appendChild(input_text)
        event_msg = {
            'domsync':True,
            'event':'oninput',
            'value': 'this.value',
            'id': self.getRootId(),
        }
        assert set(event_msg.keys()).intersection(set(event_additional_props.keys())) == set()
        event_msg.update(event_additional_props)
        event_msg = json.dumps(event_msg).replace('"this.value"','this.value')
        input_text.setAttribute('oninput', "ws_send("+event_msg+")")
    
    def getValue(self):
        return self.getElement().value

class TextareaComponent(Component):
    """
    puts a <textarea> in the dom.
    the oninput event of that element will generate events on the client side that are sent to us and triggers the callback to be called
    the component object stores the updated value of the input in self.value which is read-only because it's update dby the client only
    """
    def __init__(self, doc, parent_id, value, callback, rows=None, cols=None, id=None, event_additional_props = {}):
        super(TextareaComponent, self).__init__(doc, parent_id, id=id)
        def my_callback(_self, _callback, event):
            event['component'].getElement()['value'] = event['value']
            return _callback(event) if _callback is not None else None
        doc.register_callback(self.getRootId(), partial(my_callback, self, callback), component = self)
        textarea = doc.createElement('textarea', id=self.getRootId(), value=value)
        if rows is not None:
            assert type(rows) is int and rows > 0
            textarea.setAttribute('rows',str(rows))
        if cols is not None:
            assert type(cols) is int and cols > 0
            textarea.setAttribute('cols',str(cols))
        doc.getElementById(parent_id).appendChild(textarea)
        event_msg = {
            'domsync':True,
            'event':'oninput',
            'value': 'this.value',
            'id': self.getRootId(),
        }
        assert set(event_msg.keys()).intersection(set(event_additional_props.keys())) == set()
        event_msg.update(event_additional_props)
        event_msg = json.dumps(event_msg).replace('"this.value"','this.value')
        textarea.setAttribute('oninput', "ws_send("+event_msg+")")
    
    def getValue(self):
        return self.getElement().value

class SelectComponent(Component):
    """
    <select>
        <option value="ws://localhost:8150">algotrader_v3 prod</option>
        <option value="ws://localhost:8151">algotrader_v3 qa</option>
        <option value="ws://localhost:8888">mktdata_service_v3</option>
    </select>
    puts an <input type="text"> in the dom.
    the oninput event of that element will generate events on the client side that are sent to us and triggers the callback to be called
    the component object stores the updated value of the input in self.value which is read-only because it's update dby the client only
    """
    def __init__(self, doc, parent_id, options, callback, id=None, event_additional_props = {}):
        assert type(options) is list
        super(SelectComponent, self).__init__(doc, parent_id, id=id)
        select = doc.createElement('select', id=self.getRootId())
        doc.getElementById(parent_id).appendChild(select)
        for value in options:
            if 'value' not in self:
                self['value'] = value
            assert str_is_safe(value)
            option = doc.createElement('option', text=value)
            select.appendChild(option)
        def my_callback(_self, _callback, event):
            _self['value'] = event['value']
            return _callback(event) if _callback is not None else None
        doc.register_callback(self.getRootId(), partial(my_callback, self, callback), component = self)
        event_msg = {
            'domsync':True,
            'event':'onchange',
            'value': 'this.options[this.selectedIndex].value',
            'id': self.getRootId(),
        }
        assert set(event_msg.keys()).intersection(set(event_additional_props.keys())) == set()
        event_msg.update(event_additional_props)
        event_msg = json.dumps(event_msg).replace('"this.options[this.selectedIndex].value"', 'this.options[this.selectedIndex].value')
        select.setAttribute('onchange', "ws_send("+event_msg+")")

    def getValue(self):
        return self['value']
