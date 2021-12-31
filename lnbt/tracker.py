from flask import Flask, request
import socket
from oxenc import bt_serialize as bencode
from . import swarm
from urllib.parse import unquote_to_bytes

app = Flask(__name__)



def get_loki_addr():
    """ get the loki address of a requester """
    return socket.gethostbyaddr(request.remote_addr.split(':')[0])[0]

@app.route("/announce")
def announce():
    try:
        infohash = unquote_to_bytes(request.args.get("info_hash"))
        peerinfo = (get_loki_addr(), request.args.get("port", type=int), unquote_to_bytes(request.args.get("peer_id")))
        event = None
        if 'event' in request.args:
            event = request.args.get("event")
        started = event == 'started'
        completed = event == 'completed'
        stopped = event == 'stopped'
        if stopped:
            swarm.remove_peer(infohash, peerinfo[-1])
        if started:
            swarm.add_peer(infohash, *peerinfo)
        if completed:
            swarm.promote_peer(infohash, *peerinfo)

        peers = swarm.get_peers(infohash, for_peer=peerinfo[-1], numwant=request.args.get("numwant", default=50, type=int))
        return bencode({"interval": 600, "peers": peers})
    except Exception as ex:
        return bencode({"failure reason": f"{ex}"})
    
@app.route("/")
def index():
    return "opentracker"
