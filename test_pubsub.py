from ipfs_pubsub import PubSub
import time


def test_ls():
    api = PubSub()
    topics = api.topic_ls()
    assert list == type(topics)
    with open("test_pubsub_ls", "w") as out:
        out.write(topics)


def test_peers():
    api = PubSub()
    peers = api.topic_peers()
    assert list == type(peers)
    with open("test_pubsub_peers", "w") as out:
        out.write(peers)


# def test_pubSub():
#    api = PubSub()
#    # We use a timestamp so every test is unique and is not influenced by
#    # previous tests
#    timestamp = time.time()
#    response = api.topic_pub("pepenet_dev_test", "{}".format(timestamp))
#    assert response == "{}".format(timestamp)
#    data = api.topic_sub("pepenet_dev_test", True)
