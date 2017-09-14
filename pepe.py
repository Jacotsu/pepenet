import ipfs_pubsub
from time import time
import logging

pepenet_channels = {"upload": "dev_pepenet_pepes_upload",
                    "update_control": "dev_pepenet_pepes_update_control",
                    "update": "dev_pepenet_pepes_update"
                    }
control_codes = {"uploading_finished": 0

                 }


def load_hash_set(path):
    """Loads a local copy of pepe hashes, useful for banning locally
    malicious files or protecting the dht"""
    hashes = set()
    try:
        with open(path, "r") as hash_list:
            for i in hash_list:
                hashes.update((i,))
    except FileNotFoundError:
        open(path, "w").close()

    return hashes


def save_hash_set(path, hash_set):
    """Loads a local copy of pepe hashes, useful for banning locally
    malicious files or protecting the dht"""
    with open(path, "w") as hash_list:
        for i in hash_set:
            hash_list.write(i)


class PepeMan:
    def __init__(self,
                 ipfs_conn,
                 database="rare_pepes",
                 banned_pepes_path="rare_pepes/avoid_pepes.db",
                 local_pepes_path="rare_pepes/known_pepes.db"):
        self.pubsub = ipfs_pubsub.PubSub()
        self.ipfs_conn = ipfs_conn
        self.database = database

        # List of pepe hashes that you've banned LOCALLY, this helps in
        # avoiding unwanted content to show up in your browser
        self.banned_pepes = load_hash_set(banned_pepes_path)
        self.banned_pepes_path = banned_pepes_path

        # Local list of pepes
        self.local_pepes = load_hash_set(local_pepes_path)
        self.local_pepes_path = local_pepes_path
        for key in pepenet_channels:
            self.pubsub.topic_sub(pepenet_channels[key])

        logging.debug("Topics subscribed: {}".format(self.pubsub.topic_ls()))

        self.pubsub.topic_set_callback(pepenet_channels["update_control"],
                                       self._on_update_control)

        #self.update_pepe_list(self.local_pepes)

    def update_pepe_list(self, rare_pepes_set):
        """
            basically a client publishes his entire pepes hash list
            then other clients read that list and publish the missing hashes
            now all the clients should have an updated list
            PS: malicious clients could DOS the network by uploading a
            giant list
            The pepe list should be updated by the _on_update_control callback
        """
        for pepe in rare_pepes_set:
            self.pubsub.topic_pub(pepenet_channels["update"], pepe)

        self.pubsub.topic_pub(pepenet_channels["update_control"],
                              control_codes["uploading_finished"])


    def _on_update_control(self, data):
        if data["msg"] == control_codes["uploading_finished"]:
            self._on_update_request(data["sender"])

    def _on_update_request(self, sender_id):
        """
            After the updater has sent his uploading_finished CC
            we upload our hashes
        """
        pepe_hash = self.pubsub.\
            topic_pop_messages_from_sender(pepenet_channels["upload"],
                                           sender_id)

        logging.debug("updating hashes: {}".format(pepe_hash))
        # We remove the pepes that we don't want
        received_hashes = set(pepe_hash) - self.banned_pepes
        # Then we check if they've sent us some new hashes
        new_hash_delta = received_hashes - self.local_pepes

        if (received_hashes not in self.local_pepes):
            delta = self.local_pepes - received_hashes
            for i in delta:
                self.ipfs.topic_pub(pepenet_channels["update"])

        self.local_pepes.update((new_hash_delta,))

    def _on_upload(self, data):
        """Callback called when someone on the network uploads a pepe
        self.local_pepes is set, so if the pepe is a duplicate i will not
        be added twice"""

        self.local_pepes.update((data["content"],))
        logging.info("Received pepe: {}".format(data["content"]))

    def get_peer_number(self):
        "Returns the number of connected peers to the network"
        return self.pubsub.topic_peer_number(pepenet_channels["update"])

    def get_pepe(self, pepe_hash):
        "Downloads pepe from ipfs and saves it in database folder"
        self.ipfs_conn.get(pepe_hash)
        os.rename("{}".format(pepe_hash), "{}/{}".format(self.database,
                                                         pepe_hash))
        logging.info("Downloaded: {}".format(pepe_hash))

    def get_all_pepes(self):
        logging.debug("Getting all pepes: {}".format(self.local_pepes))
        return self.local_pepes

    def _register_pepe(self, pepe_hash):
        "Locally registers a new pepe known it's hash"
        logging.info("Registering: {}".format(pepe_hash))
        self.local_pepes.update((pepe_hash,))
        logging.info("Registered: {}".format(pepe_hash))

    def upload_pepe(self, path):
        """
        Given the local path relative to the working directory
        it uploads the pepe image to the network
        """
        logging.info("Uploading pepe: {}".format(path))
        res = self.ipfs_conn.add(path)
        self.pubsub.topic_pub(pepenet_channels["upload"], res["Hash"])
        self._register_pepe(res["Hash"])
        logging.info("Uploaded from {} as {}".format(path, res["Hash"]))

    def pin_pepe(self, pepe_hash):
        "Pins a pepe to your ipfs repository"
        self.ipfs_conn.pin_add(pepe_hash)
        logging.info("Pepe {} pinned".format(pepe_hash))

    def unpin_pepe(self, pepe_hash):
        "Unpins a pepe from your local repository"
        self.ipfs_conn.pin_rm(pepe_hash)
        logging.info("Pepe {} unpinned".format(pepe_hash))

    def ls_pinned_pepes(self):
        "Returns a list of hashes of the pinned pepes"
        logging.debug("Listing pinned pepes")
        return self.ipfs_conn.pin_ls()["Keys"]

    def save_pepes_lists(self):
        logging.info("Saving banned pepes list in: "
                     "{}".format(self.banned_pepes_path))
        save_hash_set(self.banned_pepes_path, self.banned_pepes)

        logging.info("Saving local pepes list in: "
                     "{}".format(self.local_pepes_path))
        save_hash_set(self.local_pepes_path, self.local_pepes)


class Pepe:
    def __init__(self, image_data):
        pass

    def calc_normieness(self, pepe_hash):
        pass


if __name__ == "__main__":
    print("Don't execute this module directly")
