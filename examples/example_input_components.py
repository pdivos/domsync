import asyncio
from datetime import datetime
from domsync.domsync_server import DomsyncServer

async def main():
    async def connection_handler(server, client, doc):
        doc.getElementById(doc.getRootId()).appendChild(doc.createElement("div", id='div_clock', text=''))
        while True:
            doc.getElementById('div_clock').text = 'The current time is: ' + datetime.utcnow().isoformat()
            await asyncio.sleep(0.1)
            await server.flush(client)
    server = DomsyncServer(connection_handler, 'localhost', 8888)
    await server.serve()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
