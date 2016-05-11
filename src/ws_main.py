if __name__ == '__main__':
    import asyncio
    from ws.server import XChatServerFactory

    factory = XChatServerFactory()

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, port=4880)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
