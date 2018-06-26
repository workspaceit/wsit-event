import sys
import time
from daemon import daemon
import os
import asyncio
import datetime
import random
import websockets
import json
import ssl
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wsitEvent.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from publicfront.views.nextup_evaluation import NextupEvaluation

total_conncetion = {}


@asyncio.coroutine
def time(websocket, path):
    path = path.replace(path[:1], '')
    if path in total_conncetion:
        total_conncetion[path].add(websocket)
    else:
        total_conncetion[path] = set()
        total_conncetion[path].add(websocket)

    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    exception_ws = None
    try:
        while len(total_conncetion):
            # print(path)
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            logger.debug(now)
            socket_data = {}
            socket_data["nextup_data"] = NextupEvaluation.socket_nextup(None, path,total_conncetion)
            socket_data["evaluation_data"] = NextupEvaluation.socket_evaluation(None, path)
            socket_data["message_data"] = NextupEvaluation.socket_message(None, path)
            for ws in total_conncetion[path]:
                exception_ws = ws
                # print(ws.ws_server)
                if socket_data["nextup_data"] or socket_data["evaluation_data"] or socket_data["message_data"]:
                    logger.debug(json.dumps(socket_data))
                    yield from ws.send(json.dumps(socket_data))

                else:
                    yield from ws.send(json.dumps({}))

            yield from asyncio.sleep(random.random() * 3)
    except:
        # Unregister.
        if exception_ws:
            print("Websocket disconnected")
            exception_ws.close()
            total_conncetion[path].remove(exception_ws)
            if not len(total_conncetion[path]):
                del total_conncetion[path]


class Socket(object):
    def run(self):
        socket_url = '0.0.0.0'
        if os.environ['ENVIRONMENT_TYPE'] == 'master':
            ctx=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ctx.load_cert_chain('/opt/python/current/app/ssl_master/cert.pem','/opt/python/current/app/ssl_master/privkey.pem')
            start_server = websockets.serve(time, socket_url, 5678,ssl=ctx)
        elif os.environ['ENVIRONMENT_TYPE'] == 'staging':
            # ctx=ssl.create_default_context(ssl.PROTOCOL_TLSv1)
            ctx=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ctx.load_cert_chain('/opt/python/current/app/sslkeys/cert.pem','/opt/python/current/app/sslkeys/privkey.pem')
            start_server = websockets.serve(time, socket_url, 5678,ssl=ctx)
        else:
            # ctx=ssl.create_default_context(ssl.PROTOCOL_TLSv1)
            # ctx.load_cert_chain('./sslkeys/cert.pem','./sslkeys/chain.pem')
            start_server = websockets.serve(time, socket_url, 5678)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()



class MyDaemon(daemon):
    def run(self):
        socket = Socket()
        socket.run()


if __name__ == "__main__":
    daemon = MyDaemon('/tmp/daemon-eventmanager.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
