#!/usr/bin/env python
import os
import sys
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
existing_sesion_id = []
from django.core.files import File


@asyncio.coroutine
def time(websocket, path):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print(now)
    print(path)
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
        print("total_conncetion")
        print(total_conncetion)
        while len(total_conncetion):
            now = datetime.datetime.utcnow().isoformat() + 'Z'
            print(path)
            print(now)
            print(len(total_conncetion))
            socket_data = {}
            socket_data["nextup_data"] = NextupEvaluation.socket_nextup(None, path, total_conncetion)
            socket_data["evaluation_data"] = NextupEvaluation.socket_evaluation(None, path)
            socket_data["message_data"] = NextupEvaluation.socket_message(None, path)
            # print(socket_data)
            for ws in total_conncetion[path]:
                exception_ws = ws
                # print(ws.ws_server)
                if socket_data["nextup_data"] or socket_data["evaluation_data"] or socket_data["message_data"]:
                    logger.debug(json.dumps(socket_data))
                    yield from ws.send(json.dumps(socket_data))

                else:
                    yield from ws.send(json.dumps({}))

            # yield from websocket.send(json.dumps(socket_data))
            yield from asyncio.sleep(random.random() * 3)
    except:
        # Unregister.
        # logger.debug('Websocket disconnected')
        if exception_ws:
            print("Websocket disconnected")
            exception_ws.close()
            total_conncetion[path].remove(exception_ws)
            if not len(total_conncetion[path]):
                del total_conncetion[path]
                # del total_conncetion[path]


@asyncio.coroutine
def hello(websocket, path):
    while True:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        yield from websocket.send(now)
        yield from asyncio.sleep(random.random() * 3)


# ctx=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
# ctx=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ctx.load_cert_chain('/home/chizz/cert/apache.crt','/home/chizz/cert/apache.key')
# ctx.load_cert_chain('./sslkeys/cert.pem','./sslkeys/privkey.pem')
# start_server = websockets.serve(hello, '127.0.0.1', 5678,ssl=ctx)
start_server = websockets.serve(time, '127.0.0.1', 5678)
print(start_server)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
