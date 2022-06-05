import asyncio
import json
from domsync.domsync_server import DomsyncServer
from domsync import Document, Component, TableComponent, TextInputComponent, TextareaComponent, ButtonComponent, SelectComponent

class ExampleInputsComponent(Component):
    def __init__(self, doc, parent_id, id=None):
        super(ExampleInputsComponent, self).__init__(doc, parent_id, id=id)
        button = ButtonComponent(doc, parent_id, text="on", callback=self.on_event, id=parent_id+'.button')
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        textinput = TextInputComponent(doc, parent_id, value="hi there!", callback=self.on_event, id=parent_id+'.textinput')
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        textarea = TextareaComponent(doc, parent_id, value="Hello world\nhi there\nfoo bar", callback=self.on_event, rows = 20, cols = 40, id=parent_id+'.textarea')
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        select = SelectComponent(doc, parent_id, ['Option 1','Option 2'], callback=self.on_event, id=parent_id+'.select')
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        table = TableComponent(doc, parent_id, ['key','value'], id=parent_id+'.table')
        table.addRow('textinput', ['textinput', textinput.getValue()])
        table.addRow('textarea',  ['textarea',  textarea.getValue()])
        table.addRow('select',    ['select',    select.getValue()])
        table.addRow('button',    ['button',    button.getValue()])
        self['table'] = table

    def on_event(self, event):
        doc = event['doc']
        root_id = doc.getRootId()
        table = self['table']
        if event['id'] == root_id+'.button':
            button_text = doc.getElementById(event['id']).text
            button_text = 'on' if button_text == 'off' else 'off'
            doc.getElementById(event['id']).text = button_text
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
    async def connection_handler(server, client, doc):
        ExampleInputsComponent(doc, doc.getRootId())
        await server.flush(client)
    server = DomsyncServer(connection_handler, 'localhost', 8888)
    await server.serve()
    while True: await asyncio.sleep(999)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
