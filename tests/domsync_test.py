import unittest
from domsync import Document
from domsync.components import TableComponent

class Tests(unittest.TestCase):

    def test(self):
        doc = Document('domsync_root_id')
        doc.getElementById('domsync_root_id').appendChild(doc.createElement('div', id='el0'))
        doc.getElementById('domsync_root_id').insertBefore(doc.createElement('div', id='el1'), doc.getElementById('el0'))

        doc.getElementById('el1').appendChild(doc.createElement('div', id='el11'))
        doc.getElementById('el11').appendChild(doc.createElement('div', id='el111'))
        doc.getElementById('el11').appendChild(doc.createElement('div', id='el112'))
        doc.getElementById('el112').appendChild(doc.createElement('div', id='el1121'))

        doc.getElementById('el11').remove()
        doc.getElementById('el1').innerText = 'goodbye world'

        doc.render_js_updates()

    def test3(self):
        doc = Document('domsync_root_id')

        # add a <h1> header
        doc.getElementById('domsync_root_id').appendChild(doc.createElement('h1', innerText='domsync demo'))

        # add a <ul> list with three <li> items
        doc.getElementById('domsync_root_id').appendChild(doc.createElement('ul', id='id_ul'))
        doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_0', innerText='item 0'))
        doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_1', innerText='item 1'))
        doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_2', innerText='item 2'))    

        js = doc.render_js_updates()
        # print(js)

        # change the first items text, remove the second item, change the third items attribute
        doc.getElementById('id_li_0').innerText = doc.getElementById('id_li_0').innerText + ' is missing item 1'
        doc.getElementById('id_li_1').remove()
        doc.getElementById('id_li_2').setAttribute('style','color:red')

        js = doc.render_js_updates()
        # print(js)

    def test4(self):
        doc = Document('domsync_root_id')
        table = TableComponent(doc.getElementById('domsync_root_id'), ['cp','symbol','bid','ask'])
        table.addRow('row0', ['ftx','FTT-PERP','1','2'])
        table.addRow('row2', ['ftx','FTT-0624','5','6'])
        table.addRow('row1', ['ftx','FTT/USD', '3','4'])
        js = doc.render_js_updates()

        table.updateCell('row0','bid','11')
        js = doc.render_js_updates()
        assert js == """__domsync__["__domsync_el_0.td.row0.bid"].innerText = `11`;\n""", js
        js = doc.render_js_full()

if __name__ == '__main__':
    unittest.main(verbosity=2)