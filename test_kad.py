from kad import DHT


def test_kad():
    host1, port1 = 'localhost', 3000
    host2, port2 = 'localhost', 3001

    localDHT = DHT(host1, port1)
    # localDHT = DHT(host1, port1, storage=open_shelve)  # così esplode

    remoteDHT = DHT(host2, port2, seeds=[(host1, port1)])

    localDHT["my_key"] = [u"My", u"json-serializable", u"Object"]

    assert remoteDHT["my_key"] == ['My', 'json-serializable', 'Object']
