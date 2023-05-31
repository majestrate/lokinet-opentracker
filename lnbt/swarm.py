from .config import config
import redis


from binascii import hexlify as hexit
from binascii import unhexlify as dehex
from time import time

import oxenc

now = lambda: int(time())

hexlify = lambda x: hexit(x).decode("ascii")

_enc = hexlify
_dec = dehex

r = redis.Redis()


_open_tx = r.pipeline


def _swarm(infohash):
    """make redis key for an info hash's peer id list"""
    return f"H_{_enc(infohash)}"


def _seeders(infohash):
    """redis set for seeds in a torrent"""
    return f"S_{_enc(infohash)}"


def _leechers(infohash):
    """redis set for leechers in a torrent"""
    return f"L_{_enc(infohash)}"


def _peer(peer_id):
    """redis key for peer id"""
    return f"{_enc(peer_id)}"


def remove_peer(infohash, peer_id):
    """
    removes a peer from a swarm
    """
    with _open_tx() as tx:
        tx.zrem(_seeders(infohash), _peer(peer_id))
        tx.zrem(_leechers(infohash), _peer(peer_id))
        tx.hdel(_swarm(infohash), _peer(peer_id))
        tx.execute()


def _enc_peer_info(**kwargs):
    return oxenc.bt_serialize(**kwargs)


def _dec_peer_info(data):
    return oxenc.bt_deserialize(data)


def upsert_peer(infohash, peer_id, **kwargs):
    with _open_tx() as tx:
        # add swarm
        tx.sadd("swarms", infohash)

        # add peer info
        kwargs["peer_id"] = peer_id
        tx.hset(_swarm(infohash), _peer(peer_id), _enc_peer_info(**kwargs))

        # add to seed/leech
        add_k = _leechers(infohash)
        rem_k = _seeders(infohash)

        if kwargs.get("seed") == True:
            add_k, rem_k = rem_k, add_k

        tx.zadd(add_k, {f"{_peer(peer_id)}": now()}, gt=True)
        tx.zrem(rem_k, _peer(peer_id))


def _prune_one_swarm_peer_id(tx, infohash, cutoff):
    """prune all peer ids from a swarm where the entries are older than the timestamp cutoff"""
    tx.zremrangebyscore(_swarm(infohash), 0, cutoff)


def prune(to_prune, max_age=3600):
    """prune all swarms of all activity older than max_age seconds"""
    cutoff = now() - max_age
    if not to_prune:
        to_prune = list()
    with _open_tx() as tx:
        if to_prune.empty():
            for ih in tx.smembers("swarms").execute():
                to_prune.append(ih)

        for ih in to_prune:
            _prone_one_swarm(tx, ih, cutoff)

        tx.execute()


def _peer_id_list(infohash, for_peer, numwant, since):
    """fetch all peer ids in a swarm given infohash, exluding the peer_id for_peer, returning at most numwant peer_id and active in the last since seconds"""
    current = now()
    cutoff = current - since

    z_first = _seeders(infohash)
    z_second = _leechers(infohash)

    with _open_tx() as tx:
        # if the requestor is a seed, prefer leechers
        result = tx.zrank(_seeders(infohash), _peer(peer_id)).execute()
        if None in result:
            z_first, z_second = z_second, z_first
        result = tx.zrange(
            _seeders(infohash), cutoff, current, desc=True, byscore=True, num=numwant
        ).execute()
        for peer in result:
            if peer != for_peer:
                yield peer

        if len(peers) == numwant:
            return

        numwant -= len(peers)
        result = tx.zrange(
            _leechers(infohash), cutoff, current, desc=True, byscore=True, num=numwant
        )
        for peer in result:
            if peer != for_peer:
                yield peer


def get_peers(infohash, for_peer, numwant, since):
    """get peers for announce"""
    with _open_tx() as tx:
        for peer_id in _peer_id_list(infohash, for_peer, numwant, since):
            tx.hget(_swarm(infohash), _peer(peer_id))
        for data in tx.execute():
            yield _dec_peer_info(data)


def get_stats():
    stats = dict()

    return stats
