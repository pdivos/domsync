from domsync import Document, TableComponent

def test():
    doc = Document('domsync_root_id')
    doc.getElementById('domsync_root_id').appendChild(doc.createElement('div', id='el0'))
    doc.getElementById('domsync_root_id').insertBefore(doc.createElement('div', id='el1'), doc.getElementById('el0'))

    doc.getElementById('el1').appendChild(doc.createElement('div', id='el11'))
    doc.getElementById('el11').appendChild(doc.createElement('div', id='el111'))
    doc.getElementById('el11').appendChild(doc.createElement('div', id='el112'))
    doc.getElementById('el112').appendChild(doc.createElement('div', id='el1121'))

    doc.getElementById('el11').remove()
    doc.getElementById('el1').text = 'goodbye world'

    print(doc.render_js_updates())

class MktdataV3Document(Document):
    def __init__(self, markets):
        super(MktdataV3Document, self).__init__('domsync_root_id')
        self.getElementById('domsync_root_id').appendChild(self.createElement('h1', text="mktdata_service_v3"))
        self.getElementById('domsync_root_id').appendChild(self.createElement('h3', text="Tickers"))
        columns = ['cp','symbol','bid','ask','bidVolume','askVolume']
        table = TableComponent(self, 'domsync_root_id', columns)
        self['table'] = table
        for cp, symbols in markets.items():
            for symbol in symbols:
                row_id = self._row_id(cp, symbol)
                table.addRow(row_id)
                for col_id in columns:
                    cell = table.getCellElement(row_id, col_id)
                    cell.setAttribute('onclick', "ws_send({'event':'click','id':'"+cell.id+"'})")

    def _row_id(self, cp, symbol):
        return 'row.'+cp+'.'+symbol

    def update_row(self, cp, symbol, ticker):
        values = ticker.copy()
        values['cp'] = cp
        values['symbol'] = symbol
        self['table'].updateRow(self._row_id(cp, symbol), values)

    def on_click(self, element_id):
        style = self.getElementById(element_id).getAttribute('style', 'color:white')
        if 'green' in style: style = style.replace('green','white')
        elif 'red' in style: style = style.replace('red','green')
        elif 'white' in style: style = style.replace('white','red')
        self.getElementById(element_id).setAttribute('style', style)

def test2():
    doc = MktdataV3Document({'ftx':['FTT-PERP','SOL-PERP']})
    # doc.on_click('table_markets.ftx.FTT-PERP.bid')
    doc.update_row('ftx','FTT-PERP',{'bid':'0','ask':'1','bidVolume':'3','askVolume':'4'})
    print(doc.render_js_updates())

def test3():
    doc = Document('domsync_root_id')


    # add a <h1> header
    doc.getElementById('domsync_root_id').appendChild(doc.createElement('h1', text='domsync demo'))

    # add a <ul> list with three <li> items
    doc.getElementById('domsync_root_id').appendChild(doc.createElement('ul', id='id_ul'))
    doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_0', text='item 0'))
    doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_1', text='item 1'))
    doc.getElementById('id_ul').appendChild(doc.createElement('li', id='id_li_2', text='item 2'))    

    js = doc.render_js_updates()
    # print(js)

    # change the first items text, remove the second item, change the third items attribute
    doc.getElementById('id_li_0').text = doc.getElementById('id_li_0').text + ' is missing item 1'
    doc.getElementById('id_li_1').remove()
    doc.getElementById('id_li_2').setAttribute('style','color:red')

    js = doc.render_js_updates()
    print(js)

def test4():
    doc = Document('domsync_root_id')
    table = TableComponent(doc, 'domsync_root_id', ['cp','symbol','bid','ask'])
    table.addRow('row0', ['ftx','FTT-PERP','1','2'])
    table.addRow('row2', ['ftx','FTT-0624','5','6'])
    table.addRow('row1', ['ftx','FTT/USD', '3','4'])
    js = doc.render_js_updates()

    table.updateCell('row0','bid','11')
    js = doc.render_js_updates()
    table.getCellElement('row0','cp').innerHTML = '<a></a>'
    js = doc.render_js_updates()
    print(js)

    js = doc.render_js_full()

if __name__ == '__main__':
    # test()
    # test2()
    # test3()
    test4()