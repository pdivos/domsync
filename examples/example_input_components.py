import asyncio
import json
from domsync.domsync_server import DomsyncServer
from domsync import Document
from domsync.components import Component, TableComponent

class ExampleInputsComponent(Component):
    def __init__(self, parent_el):
        super(ExampleInputsComponent, self).__init__(parent_el)
        doc = parent_el.getDocument()

        button = doc.createElement('button', id=parent_el.id+'.button', innerText='on')
        button.addEventListener('click', self.on_event)
        parent_el.appendChild(button)
        parent_el.appendChild(doc.createElement('br'))

        textinput = doc.createElement('input', id=parent_el.id+'.textinput', value='hi there!', attributes={'type':'text'})
        textinput.addEventListener('input', self.on_event, js_value_getter='this.value')
        parent_el.appendChild(textinput)
        parent_el.appendChild(doc.createElement('br'))

        textarea = doc.createElement('textarea', id=parent_el.id+'.textarea', value="Hello world\nhi there\nfoo bar", attributes={'rows':'20','cols':'40'})
        textarea.addEventListener('input', self.on_event, js_value_getter='this.value')
        parent_el.appendChild(textarea)
        parent_el.appendChild(doc.createElement('br'))

        select = doc.createElement('select', id=parent_el.id+'.select')
        select.appendChild(doc.createElement('option', innerText='Option 1'))
        select.appendChild(doc.createElement('option', innerText='Option 2'))
        select.addEventListener('input', self.on_event, js_value_getter = 'this.options[this.selectedIndex].value')
        parent_el.appendChild(select)
        parent_el.appendChild(doc.createElement('br'))

        table = TableComponent(parent_el, ['key','value'])
        table.addRow('textinput', ['textinput', textinput.value])
        table.addRow('textarea',  ['textarea',  textarea.value])
        table.addRow('select',    ['select',    'Option 1'])
        table.addRow('button',    ['button',    button.innerText])
        self['table'] = table

    def on_event(self, event):
        doc = event['doc']
        root_id = doc.getRootElement().id
        table = self['table']
        if event['id'] == root_id+'.button':
            button_text = doc.getElementById(event['id']).innerText
            button_text = 'on' if button_text == 'off' else 'off'
            doc.getElementById(event['id']).innerText = button_text
            table.updateCell('button','value',button_text)
        elif event['id'] == root_id+'.textinput':
            table.updateCell('textinput','value',event['value'])
        elif event['id'] == root_id+'.textarea':
            table.updateCell('textarea','value',event['value'])
        elif event['id'] == root_id+'.select':
            table.updateCell('select','value',event['value'])
        else:
            raise Exception(event)

async def main():
    async def connection_handler(server, client):
        doc = server.get_document(client)
        ExampleInputsComponent(doc.getRootElement())
        await server.flush(client)
    server = DomsyncServer(connection_handler, 'localhost', 8888)
    await server.serve()
    while True: await asyncio.sleep(999)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
