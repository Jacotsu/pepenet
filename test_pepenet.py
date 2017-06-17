from pepenet import get_saved_peers


def test_get_saved_peers():
    peers = get_saved_peers('test_peers.txt')
    assert peers == [("192.168.1.29", 3000),
                     ("168.192.2.30", 8000),
                     ("yourpeer.net", 9001)]
