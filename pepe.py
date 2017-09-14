import ipfs_pubsub
import ipfsapi
from time import time


def load_hash_set(path):
    """Loads a local copy of pepe hashes, useful for banning locally
    malicious files or protecting the dht"""
    hashes = set()
    try:
        with open(path, "r") as hash_list:
            for i in hash_list:
                hashes.append(i)
    except FileNotFoundError:
        open(path, "w").close()

    return hashes


def save_hash_set(path, hash_set):
    """Loads a local copy of pepe hashes, useful for banning locally
    malicious files or protecting the dht"""
    with open(path, "w") as hash_list:
        for i in hash_set:
            hash_list.write(i)

pepenet_channels = {"add": "pepenet_pepes_add",
                    "update": "pepenet_pepes_update"
                    }


class PepeMan:
    def __init__(self,
                 ipfs_conn,
                 banned_pepes_path="avoid_pepes.db",
                 local_pepes_path="known_pepes.db"):
        self.pubsub = ipfs_pubsub.PubSub()
        self.ipfs_conn = ipfs_conn
        # List of pepe hashes that you've banned LOCALLY, this helps in
        # avoiding unwanted content to show up in your browser
        self.banned_pepes = load_hash_set(banned_pepes_path)
        # Local list of pepes
        self.local_pepes = load_hash_set(local_pepes_path)
        self.update_pepe_list(self.local_pepes)

        self.dht_keys = ["rare_pepes"]

    def update_pepe_list(self, rare_pepes_set):
        """
            basically a client publishes his entire pepes hash list
            then other clients read that list and publish the missing hashes
            now all the clients should have an updated list
            PS: malicious clients could DOS the network by uploading a
            giant list
            max update time should be 10s
        """
        delta_t = 10
        init_t = time()

        hashes_set = set()
        for pepe in self.rare_pepes_set:
            self.pubsub.topic_pub(pepenet_channels["update"], pepe)

        while True:
            if time() - init_t > delta_t:
                break
            hashes_set.update(self.pubsub.
                              topic_data(pepenet_channels["update"]))

        rare_pepes_set.update(hashes_set - self.banned_pepes)

    def _on_update_request(self, pepe_hashes):
        """
            wait some time and then start printing your hashes
        """
        #sleep(5)
        received_hashes = set(pepe_hashes)
        # First we check if they've sent us some new hashes
        new_hash_delta = received_hashes - self.local_pepes

        if (received_hashes not in self.local_pepes):
            delta = self.local_pepes - received_hashes
            for i in delta:
                self.ipfs.topic_pub(pepenet_channels["update"])

        self.local_pepes.update(new_hash_delta)


    def get_pepe(self, pepe_hash):
        # Request pepe from pub sub
        self.ipfs_conn.get(pepe_hash)

    def register_pepe(self, pepe_hash):
        self.local_pepes.append(pepe_hash)

    def upload_pepe(self, path):
        res = self.ipfs_conn.add(path)
        self.pubsub.topic_pub(pepenet_channels["add"], res["Hash"])
        self.register_pepe(res["Hash"])

    def pin_pepe(self, pepe_hash):
        self.ipfs_conn.pin_add(pepe_hash)

    def unpin_pepe(self, pepe_hash):
        self.ipfs_conn.pin_rm(pepe_hash)

    def ls_pinned_pepes(self):
        return self.ipfs_conn.ping_ls()["Keys"]


class Pepe:
    def __init__(self, image_data):
        pass

    def calc_normieness(self, pepe_hash):
        pass


if __name__ == "__main__":
    print("Don't execute this module directly")
