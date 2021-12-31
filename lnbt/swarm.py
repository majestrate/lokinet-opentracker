
from sqlalchemy import text, create_engine
from .config import config

engine = create_engine(config.db_url)

def query(sql, **kwargs):
    with engine.connect() as conn:
        return conn.execute(text(sql), **kwargs)

def remove_peer(infohash, peer_id):
    query("DELETE FROM bt_swarm_peers WHERE infohash = :infohash AND peer_id = :peer_id", infohash=infohash, peer_id=peer_id)

def add_peer(infohash, ip, port, peer_id, seed=False):
    query("INSERT OR REPLACE INTO bt_swarm_peers(infohash, ip, port, peer_id, seed) VALUES(:infohash, :ip, :port, :peer_id, :seed)", infohash=infohash, ip=ip, port=port, peer_id=peer_id, seed=seed)

def promote_peer(infohash, ip, port, peer_id):
    add_peer(infohash, ip, port, peer_id, True)

def get_peers(infohash, for_peer, numwant=50):
    peers = list()
    for row in query("SELECT peer_id, addr, port FROM bt_swarm_peers WHERE infohash = ? AND seed = 1 AND peer_id != :peer_id LIMIT :numwant", infohash=infohash, peer_id=for_peer, numwant=numwant):
        peers.append({"peer_id": row["peer_id"], "ip": row["addr"], "port": row["port"]})
    if len(peers) < numwant:
        for row in query("SELECT peer_id, addr, port FROM bt_swarm_peers WHERE infohash = :infohash AND seed = 0 AND peer_id != :peer_id LIMIT :numwant", infohash=infohash, peer_id=peer_id, numwant=numwant - len(peers)):
            peers.append({"peer_id": row["peer_id"], "ip": row["addr"], "port": row["port"]})
    return peers

query("CREATE TABLE IF NOT EXISTS bt_swarm_peers (infohash VARCHAR(20) NOT NULL, seed BOOL DEFAULT FALSE, peer_id VARCHAR(32) NOT NULL, addr VARCHAR(64) NOT NULL, port INTEGER NOT NULL, PRIMARY KEY(infohash, peer_id))")
