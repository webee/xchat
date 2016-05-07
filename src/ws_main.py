
if __name__ == '__main__':
    import asyncio
    from autobahn.asyncio.websocket import WebSocketServerFactory
    from ws.server import XChatServerProtocol

    factory = WebSocketServerFactory()
    factory.protocol = XChatServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, 'localhost', 4880)
    server = loop.run_until_complete(coro)

    asyncio.coroutine()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
