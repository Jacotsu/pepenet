from ipfs_pubsub import PubSub
import time


def test_ls():
    api = PubSub()
    # We need to publish something otherwise ls doesn't work
    api.topic_pub("pepenet_dev_test", "Testing")
    topics = api.topic_ls()
    assert isinstance(topics, list)
    with open("test_pubsub_ls", "w") as out:
        out.write("\n".join(topics))


def test_peers():
    api = PubSub()
    api.topic_pub("pepenet_dev_test", "Testing")
    peers = api.topic_peers()
    assert isinstance(peers, list)
    with open("test_pubsub_peers", "w") as out:
        out.write("\n".join(peers))


def test_pubSub():
    api = PubSub(update_interval=0)
    # We use a timestamp so every test is unique and is not influenced by
    # previous tests
    timestamp = time.time()
    api.topic_sub("pepenet_dev_test", True)
    assert api.update_thread.isAlive()
    api.topic_pub("pepenet_dev_test", "{}".format(timestamp))
    with open("test_pubsub_pubSub", "w") as out:
        out.write("\n".join(api.subscriptions))
