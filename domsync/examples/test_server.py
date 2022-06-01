from domsync import Document
from domsync.examples.test_inputs_component import TestInputsComponent

import asyncio
import json
import websockets

async def on_ws_client_connect(websocket, path):
    root_id = 'domsync_root_id'
    doc = Document(root_id)
    TestInputsComponent(doc, root_id)

    js = doc.render_js_updates()
    if len(js):
        await websocket.send(js)
    while True:
        msg = json.loads(await websocket.recv())
        assert msg.get('domsync')
        doc.handle_event(msg)
        js = doc.render_js_updates()
        if len(js) > 0:
            await websocket.send(js)

async def main():
    host = '0.0.0.0'
    port = 8152
    await websockets.serve(on_ws_client_connect, host, port)
    print(f'ws server started on ws://{host}:{port}')
    while True: await asyncio.sleep(999)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
