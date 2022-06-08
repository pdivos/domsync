import asyncio
from datetime import datetime
from domsync.domsync_server import DomsyncServer

async def connection_handler(server, client):
    """
    connection_handler is called every time a client connects to the server
    :param server: is the DomsyncServer instance
    :param client: is a websocket client connection instance
    """

    # get the client's domsync Document
    document = server.get_document(client)

    # add a div to the root element
    root_element = document.getElementById(document.getRootId())
    div_element = document.createElement('div')
    root_element.appendChild(div_element)

    while True:
        # update the text of the div to the current time
        div_element.text = 'The current time is: ' + datetime.utcnow().isoformat()

        # wait a bit
        await asyncio.sleep(1)

        # send updates to the client
        await server.flush(client)

async def main():
    # start a domsync server on localhost port 8888
    await DomsyncServer(connection_handler, 'localhost', 8888).serve()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
