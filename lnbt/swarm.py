from sqlalchemy import text, create_engine
from .config import config
from binascii import hexlify as hexit
from binascii import unhexlify as dehex
from time import time

now = lambda: int(time())

hexlify = lambda x: hexit(x).decode("ascii")

engine = create_engine(config.db_url)


def query(sql, **kwargs):
    with engine.connect() as conn:
        return conn.execute(text(sql), **kwargs)


def remove_peer(infohash, peer_id):
    query(
        "DELETE FROM bt_swarm_peers WHERE infohash = :infohash AND peer_id = :peer_id",
        infohash=hexlify(infohash),
        peer_id=hexlify(peer_id),
    )


def add_peer(infohash, ip, port, peer_id, seed=False):
    query(
        "INSERT INTO bt_swarm_peers(infohash, addr, port, peer_id, seed, last_active_at) VALUES(:infohash, :ip, :port, :peer_id, :seed, :now) ON CONFLICT(peer_id, infohash) DO UPDATE SET last_active_at = EXCLUDED.last_active_at",
        infohash=hexlify(infohash),
        ip=ip,
        port=port,
        peer_id=hexlify(peer_id),
        seed=seed,
        now=now(),
    )


def promote_peer(infohash, ip, port, peer_id):
    add_peer(infohash, ip, port, peer_id, True)
    query(
        "UPDATE bt_swarm_peers SET seed = TRUE WHERE infohash = :infohash AND peer_id = :peer_id",
        infohash=hexlify(infohash),
        peer_id=hexlify(peer_id),
    )


def peer_active(infohash, peer_id):
    query(
        "UPDATE bt_swarm_peers SET last_active_at = :now WHERE infohash = :infohash AND peer_id = :peer_id",
        now=now(),
        infohash=hexlify(infohash),
        peer_id=hexlify(peer_id),
    )


def prune(infohash=None, threshold=3600):
    if infohash:
        query(
            "DELETE FROM bt_swarm_peers WHERE infohash = :infohash AND last_active_at < :time",
            infohash=hexlify(infohash),
            time=now() - threshold,
        )
    else:
        query(
            "DELETE FROM bt_swarm_peers WHERE last_active_at < :time",
            time=now() - threshold,
        )


def get_peers(infohash, for_peer, numwant=50, since=300):
    peers = list()
    last = now() - since
    for row in query(
        "SELECT peer_id, addr, port FROM bt_swarm_peers WHERE infohash = :infohash AND seed = TRUE AND peer_id != :peer_id AND last_active_at > :time LIMIT :numwant",
        infohash=hexlify(infohash),
        peer_id=hexlify(for_peer),
        numwant=numwant,
        time=last,
    ):
        peers.append(
            {"peer_id": dehex(row["peer_id"]), "ip": row["addr"], "port": row["port"]}
        )
    if len(peers) < numwant:
        for row in query(
            "SELECT peer_id, addr, port FROM bt_swarm_peers WHERE infohash = :infohash AND seed = FALSE AND peer_id != :peer_id AND last_active_at > :time LIMIT :numwant",
            infohash=hexlify(infohash),
            peer_id=hexlify(for_peer),
            numwant=numwant - len(peers),
            time=last,
        ):
            peers.append(
                {
                    "peer_id": dehex(row["peer_id"]),
                    "ip": row["addr"],
                    "port": row["port"],
                }
            )
    return peers


def get_stats():
    stats = dict()
    for row in query(
        "SELECT COUNT(DISTINCT(infohash)) AS swarms, COUNT(DISTINCT(peer_id)) AS peers FROM bt_swarm_peers"
    ):
        stats["swarms"] = row["swarms"]
        stats["peers"] = row["peers"]
    return stats


query(
    "CREATE TABLE IF NOT EXISTS bt_swarm_peers (infohash VARCHAR(40) NOT NULL, seed BOOL DEFAULT FALSE, peer_id VARCHAR(64) NOT NULL, addr VARCHAR(64) NOT NULL, port INTEGER NOT NULL, last_active_at BIGINT NOT NULL, PRIMARY KEY(infohash, peer_id))"
)
