from domsync import Component, TableComponent, TextInputComponent, TextareaComponent, ButtonComponent, SelectComponent

class TestInputsComponent(Component):
    def __init__(self, doc, parent_id, id=None):
        super(TestInputsComponent, self).__init__(doc, parent_id, id=id)
        button = ButtonComponent(doc, parent_id, "on", self.on_event, id=parent_id+'.button')
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        textinput = TextInputComponent(doc, parent_id, "hi there!", self.on_event, id=parent_id+'.textinput', event_additional_props = {'t':'TextInputComponent'})
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        textarea = TextareaComponent(doc, parent_id, "Hello world\nhi there\nfoo bar", self.on_event, rows = 20, cols = 40, id=parent_id+'.textarea', event_additional_props = {'t':'TextareaComponent'})
        doc.getElementById(parent_id).appendChild(doc.createElement('br'))

        select = SelectComponent(doc, parent_id, ['Option 1','Option 2'], self.on_event, id=parent_id+'.select', event_additional_props = {'t':'SelectComponent'})
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