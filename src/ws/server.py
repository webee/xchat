import logging
import json
import time
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class XChatServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        logger.info("Client connecting: {}, {}".format(request.peer, self.factory.clients))

    def onOpen(self):
        logger.info("self: {}".format(self))
        self.factory.clients += 1
        logger.info("WebSocket connection open: {}, {}".format(self.peer, self.factory.clients))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}, {}".format(self.peer, reason))

    def onMessage(self, payload, isBinary):
        logger.info('[{}] {}.'.format(time.time(), self.peer))
        # try:
        #     obj = json.loads(payload.decode('utf8'))
        # except Exception as e:
        #     obj = {'error': str(e)}
        # payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
        self.sendMessage(payload, isBinary)


class XChatServerFactory(WebSocketServerFactory):

    protocol = XChatServerProtocol

    def __init__(self, *args, **kwargs):
        WebSocketServerFactory.__init__(self, *args, **kwargs)
        self.clients = 0
