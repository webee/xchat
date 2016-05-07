import logging
import json
import time
from autobahn.asyncio.websocket import WebSocketServerProtocol

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class XChatServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        logger.info("Client connecting: {}".format(request.peer))
        if request.path != '/ws':
            self.sendClose(1000, "bad path.")
        self.peer = request.peer

    def onOpen(self):
        logger.info("WebSocket connection open.")

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {}".format(reason))

    def onMessage(self, payload, isBinary):
        logger.info('[{}] {}.'.format(time.time(), self.peer))
        # try:
        #     obj = json.loads(payload.decode('utf8'))
        # except Exception as e:
        #     obj = {'error': str(e)}
        # payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
        self.sendMessage(payload, isBinary)
