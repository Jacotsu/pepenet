#!/usr/bin/env python3
import pepe
import pepedb


def test_store_single():
    test_pepe = pepe.Pepe("test_hash_single")
    db = pepedb.PepeDB("test_pepe.db")
    db.insert_pepes(test_pepe)
    result = db.get_pepes()
    print(result)
    assert(True)

