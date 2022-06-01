"""
a passive domsync component is something that you can add in the document tree and will render itself
but is still one-way in the sense that it only renders info server->client and there is no input from client->server
basically they don't have javascript event handlers such as onclick, onchange, ...
"""

from domsync.core import Component

class TableComponent(Component):
    def __init__(self, doc, parent_id, columns, id=None):
        if type(columns) is list:
            columns = {el:el for el in columns}
        super(TableComponent, self).__init__(doc, parent_id, id=id)
        self['columns'] = columns
        el_table = doc.createElement('table', id=self.getRootId())
        doc.getElementById(parent_id).appendChild(el_table)
        el_tr = doc.createElement('tr', id=self.getRootId()+'.tr.header')
        el_table.appendChild(el_tr)
        for col_id, col_name in columns.items():
            el_th = doc.createElement('th', id=self.getRootId()+'.td.header.'+col_id, text=col_name)
            el_tr.appendChild(el_th)
    
    def _row_id(self, row_id):
        return self.getRootId()+'.tr.'+row_id

    def _cell_id(self, row_id, col_id):
        return self.getRootId()+'.td.'+row_id+'.'+col_id

    def addRow(self, row_id, values=None):
        "adds a row by keeping rows sorted by row_id"
        _row_id = self._row_id(row_id)
        el_tr = self['doc'].createElement('tr', id=_row_id)
        table_el = self.getElement()
        found = False
        for row_el in table_el.children:
            if row_el.id == self['id']+'.tr.header': continue
            if _row_id < row_el.id:
                found = True
                break
        if found:
            table_el.insertBefore(el_tr, row_el)
        else:
            table_el.appendChild(el_tr)
        i = 0
        for col_id in self['columns']:
            value = "" if values is None else values[i] if type(values) is list else values[col_id] if type(values) is dict else throw(type(values))
            cell_id = self._cell_id(row_id, col_id)
            el_tr.appendChild(self['doc'].createElement('td', id=cell_id, text=value))
            i += 1

    def updateRow(self, row_id, values):
        i = 0
        for col_id in self['columns']:
            value = values[i] if type(values) is list else values[col_id] if type(values) is dict else throw(type(values))
            self.updateCell(row_id, col_id, value)
            i+=1

    def addOrUpdateRow(self, row_id, values):
        if self.hasRow(row_id):
            self.updateRow(row_id, values)
        else:
            self.addRow(row_id, values)

    def hasRow(self, row_id):
        return self._row_id(row_id) in self['doc']['elements_by_id']

    def removeRow(self, row_id):
        self['doc'].getElementById(self._row_id(row_id)).remove()

    def getRowIds(self):
        table_el = self['doc'].getElementById(self['id'])
        row_ids = []
        id_prefix = self['id']+'.tr.'
        for row_el in table_el.children:
            if row_el.id != self['id']+'.tr.header':
                row_id = row_el.id
                assert row_id.startswith(id_prefix)
                row_id = row_id[len(id_prefix):]
                row_ids.append(row_id)
        return row_ids

    def updateCell(self, row_id, col_id, value):
        self.getCellElement(row_id, col_id).text = value

    def getTableElement(self):
        return self.getElement()

    def getRowElement(self, row_id):
        row_id = self._row_id(row_id)
        return self['doc'].getElementById(row_id)

    def getCellElement(self, row_id, col_id):
        cell_id = self._cell_id(row_id, col_id)
        return self['doc'].getElementById(cell_id)
