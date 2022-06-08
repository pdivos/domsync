import asyncio
import json
from domsync import Document

class DomsyncServer():
    def __init__(self, connection_handler, host, port, verbose = True, root_id = 'domsync_root_id'):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.root_id = root_id
        self.clients = {} # client websocket instance -> domsync Document
        self.connection_handler = connection_handler

    async def serve(self):
        import websockets
        self.server = await websockets.serve(self._on_ws_client_connect, self.host, self.port)
        if self.verbose: print(f'domsync server started on ws://{self.host}:{self.port}')

    async def close(self):
        assert self.server.is_serving()
        self.server.close()
        await self.server.wait_closed()
        assert not self.server.is_serving()

    async def _on_ws_client_connect(self, client, _path):
        import websockets
        assert client not in self.clients
        doc = Document(self.root_id)
        self.clients[client] = doc

        asyncio.create_task(self.connection_handler(self, client))

        while True:
            try:
                msg = await client.recv()
            except websockets.exceptions.ConnectionClosedOK:
                break

            try:
                msg = json.loads(msg)
            except json.decoder.JSONDecodeError:
                continue

            if msg.get('domsync'):
                doc.handle_event(msg)
                await self.flush(client)

        del self.clients[client]
    
    def is_connected(self, client):
        return client in self.clients

    def get_clients(self):
        return list(self.clients.keys())

    def get_document(self, client):
        return self.clients[client]

    async def flush(self, client):
        doc = self.clients[client]
        js = doc.render_js_updates()
        if len(js) > 0:
            await client.send(js)

    async def flush_all(self):
        for client in self.clients:
            doc = self.clients[client]
            js = doc.render_js_updates()
            if len(js) > 0:
                await client.send(js)
