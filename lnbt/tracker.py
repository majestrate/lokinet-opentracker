from flask import Flask, request, render_template
import socket
from oxenc import bt_serialize as bencode
from . import swarm
from .config import config
from urllib.parse import unquote_to_bytes, parse_qsl
from binascii import hexlify
import struct

app = Flask(__name__)


def get_loki_addr():
    """ get the loki address of a requester """
    ip = str(request.remote_addr)
    return socket.gethostbyaddr(ip.split(":")[0])[0]


@app.route("/announce")
def announce():
    try:
        infohash = b""
        peer_id = b""
        for part in request.query_string.split(b"&"):
            if part.startswith(b"info_hash="):
                infohash = unquote_to_bytes(part[10:])
            if part.startswith(b"peer_id="):
                peer_id = unquote_to_bytes(part[8:])
        if len(infohash) == 0:
            raise Exception("no infohash provided")
        if len(infohash) != 20:
            raise Exception("invalid infohash")
        if len(peer_id) == 0:
            raise Exception("no peer_id provided")
        if len(peer_id) != 20:
            raise Exception("invalid peer_id")

        peerinfo = (get_loki_addr(), request.args.get("port", type=int), peer_id)
        event = None
        if "event" in request.args:
            event = request.args.get("event")
        started = event == "started"
        completed = (
            event == "completed" or request.args.get("left", type=int, default=-1) == 0
        )
        stopped = event == "stopped"
        if stopped:
            swarm.remove_peer(infohash, peerinfo[-1])
        if started:
            swarm.add_peer(infohash, *peerinfo)
        if completed:
            swarm.promote_peer(infohash, *peerinfo)

        swarm.peer_active(infohash, peerinfo[-1])
        swarm.prune(infohash, threshold=config.interval * 4)
        peers = swarm.get_peers(
            infohash,
            for_peer=peerinfo[-1],
            numwant=request.args.get("numwant", default=50, type=int),
        )
        return bencode({"interval": config.interval, "peers": peers})
    except Exception as ex:
        app.logger.warn(f"{ex}")
        return bencode({"failure reason": f"{ex}"})


@app.route("/")
def index():
    return render_template("index.html", host=request.host)
