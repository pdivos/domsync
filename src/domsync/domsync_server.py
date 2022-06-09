import asyncio
import json
from domsync import Document

class DomsyncServer():
    """
    :class:`domsync.domsync_server.DomsyncServer` is a websocket server that maintains a :class:`domsync.Document` instance for each connected client,
    sends updates of the document to the client and applies event messages received from the client on the document

    :param connection_handler: is a callback function that is called each time a client connects to the server.
       It has two arguments: the first contains the DomsyncServer instance, the second contains the client websocket connection instance.
    :type connection_handler: Callable(:class:`domsync.domsync_server.DomsyncServer`, ``WebSocketServerProtocol``)

    :param host: host name to listen on
    :type host: str

    :param port: port number to listen on
    :type port: int

    :param verbose: optional, should we print status messages to stdout? default = True.
    :type verbose: bool

    :param root_id: optional, id of the element in the client-side HTML where domsync should be rendered. default = 'domsync_root_id'.
    :type root_id: str
    """
    def __init__(self, connection_handler, host, port, verbose = True, root_id = 'domsync_root_id'):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.root_id = root_id
        self.clients = {} # client websocket instance -> domsync Document
        self.connection_handler = connection_handler

    async def serve(self):
        """
        starts the server
        """
        import websockets
        self.server = await websockets.serve(self._on_ws_client_connect, self.host, self.port)
        if self.verbose: print(f'domsync server started on ws://{self.host}:{self.port}')

    async def close(self):
        """
        stops the server
        """
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
        """
        returns whether the given client is still connected

        :param client: a websocket client connection instance
        :type: client: ``WebSocketServerProtocol``

        :returns: True if the client is still connected, False otherwise
        :rtype: bool
        """
        return client in self.clients

    def get_clients(self):
        """
        returns the list of connected clients

        :returns: list of connected clients
        :rtype: list of ``WebSocketServerProtocol``
        """
        return list(self.clients.keys())

    def get_document(self, client):
        """
        returns the document of the given connected client

        :param client: a websocket client connection instance
        :type: client: ``WebSocketServerProtocol``

        :returns: the document associated with the client connection
        :rtype: :class:`domsync.Document`
        """
        return self.clients[client]

    async def flush(self, client):
        """
        sends the generated Javascript code updates to the client that happened due to manipulations to the clien'ts document since the last time this function was called

        :param client: the client to send the updates for
        :type: client: ``WebSocketServerProtocol``

        :returns: None
        """
        doc = self.clients[client]
        js = doc.render_js_updates()
        if len(js) > 0:
            await client.send(js)

    async def flush_all(self):
        """
        similar to :meth:`domsync.domsync_server.DomsyncServer.flush`, but sends updates to all connected clients

        :returns: None
        """
        for client in self.clients:
            doc = self.clients[client]
            js = doc.render_js_updates()
            if len(js) > 0:
                await client.send(js)
