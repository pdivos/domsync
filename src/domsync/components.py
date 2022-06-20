from domsync.core import Document, _Element

def throw(x):
    raise Exception(x)

class Component(dict):
    """
    a Component is a reusable group of Elements along with some private data
    each Component has exactly one root Element which may have child Elements
    upon __init__ the Component writes it's Elements in the Document, under an existing parent Element
    """
    def __init__(self, parent_el):
        """
        :param doc: Document to add the components' elements into
        :param parent_el_or_id: an Element or an id of an Element in the Document under which the Component's root element shall be added
        :type parent_el_or_id: :class:`domsync.core._Element` or str
        """
        assert type(parent_el) is _Element, [type(parent_el), parent_el]
        super(Component, self).__init__({
            'parent_el': parent_el,
        })
        self._has_been_removed = False

    def getParentElement(self):
        """
        :returns: the parent element of the Component that was passed in __init__, under which it created it's own elements
        """
        return self['parent_el']

    def getDocument(self):
        """
        :returns: the document of the parent element
        """
        return self.getParentElement().getDocument()

    def has_been_removed(self):
        return self._has_been_removed

    def remove(self):
        assert not self._has_been_removed, "already removed"
        self._remove()
        self._has_been_removed = True

    def _remove(self):
        """
        shoudl be implement by the derived class
        should remove all elements that were added by the Component.
        """
        raise NotImplementedError

class TableComponent(Component):
    def __init__(self, parent_el, columns):
        """
        :param doc: Document to add the components' elements into
        :param parent_id: id of an Element in the Document under which the COmponent's Elements shall be added
        :param columns: dict of column id -> column name. insert order in dict determines the order of columns.
                        or list of column names which are also the column ids.
        :param id: id of the root Element inserted by the Component
        """
        if type(columns) is list:
            columns = {el:el for el in columns}
        self['columns'] = columns
        doc = parent_el.getDocument()
        self.table_el = doc.createElement('table')
        super(TableComponent, self).__init__(parent_el)
        parent_el.appendChild(self.table_el)
        el_tr = doc.createElement('tr', id=self.table_el.id+'.tr.header')
        self.table_el.appendChild(el_tr)
        for col_id, col_name in columns.items():
            el_th = doc.createElement('th', id=self.table_el.id+'.td.header.'+col_id, innerText=col_name)
            el_tr.appendChild(el_th)

    def _remove(self):
        self.table_el.remove()
    
    def _row_id(self, row_id):
        """
        :returns: the full id of a row
        """
        return self.table_el.id+'.tr.'+row_id

    def _cell_id(self, row_id, col_id):
        return self.table_el.id+'.td.'+row_id+'.'+col_id

    def addRow(self, row_id, values=None):
        "adds a row by keeping rows sorted by row_id"
        _row_id = self._row_id(row_id)
        el_tr = self.getDocument().createElement('tr', id=_row_id)
        table_el = self.table_el
        found = False
        for row_el in table_el.children:
            if row_el.id == self.table_el.id+'.tr.header': continue
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
            el_tr.appendChild(self.getDocument().createElement('td', id=cell_id, innerText=value))
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
        return self.getDocument().getElementById(self._row_id(row_id), strict=False) is not None

    def removeRow(self, row_id):
        self.getDocument().getElementById(self._row_id(row_id)).remove()

    def getRowIds(self):
        table_el = self.table_el
        row_ids = []
        id_prefix = self.table_el.id+'.tr.'
        for row_el in table_el.children:
            if row_el.id != self.table_el.id+'.tr.header':
                row_id = row_el.id
                assert row_id.startswith(id_prefix)
                row_id = row_id[len(id_prefix):]
                row_ids.append(row_id)
        return row_ids

    def updateCell(self, row_id, col_id, value):
        self.getCellElement(row_id, col_id).innerText = value

    def getTableElement(self):
        return self.table_el

    def getRowElement(self, row_id):
        row_id = self._row_id(row_id)
        return self.getDocument().getElementById(row_id)

    def getCellElement(self, row_id, col_id):
        cell_id = self._cell_id(row_id, col_id)
        return self.getDocument().getElementById(cell_id)

class SelectComponent(Component):
    """
    """
    def __init__(self, parent_el, options, callback, selected_value = None, id=None):
        """
        :param doc: Document to add the components' elements into
        :param parent_id: id of an Element in the Document under which the COmponent's Elements shall be added
        :param options: dict of option value -> option innerText, or list of option values in which case innerText will be the same as the value
        :param callback: called when an item is selected, needs to have one argument which is the event
        :param id: id of the root Element inserted by the Component
        """
        doc = parent_el.getDocument()
        super(SelectComponent, self).__init__(parent_el)
        self.select = doc.createElement('select',id=id)
        self.select.addEventListener('input', callback, js_value_getter = 'this.options[this.selectedIndex].value')
        if type(options) is list:
            options = {el:el for el in options}
        assert type(options) is dict
        for value, text in options.items():
            self.select.appendChild(doc.createElement('option', innerText=text, value=value))
        if selected_value is not None:
            assert selected_value in options, [selected_value, options]
            self.select.value = selected_value
        parent_el.appendChild(self.select)

    def _remove(self):
        self.select.remove()
