import ipfs_pubsub
import distr_data_man
from base64 import b64decode
import os
import time
import logging

pepenet_channels = {"upload": "dev_pepenet_pepes_upload",
                    "update_control": "dev_pepenet_pepes_update_control",
                    "update": "dev_pepenet_pepes_update",
                    "metadata": "dev_pepenet_pepes_metadata",
                    }
control_codes = {"updating_finished": "0"

                 }


def load_hash_set(path):
    """Loads a local copy of pepe hashes, useful for banning locally
    malicious files or protecting the dht"""
    try:
        with open(path, "r") as hash_list:
            hashes = {pepe_hash.rstrip() for pepe_hash in hash_list}
            logging.debug("Loaded {} as {}".format(path, hashes))
        return hashes

    except FileNotFoundError:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()
        logging.debug("Found an empty hash file")
        return set()

    return hashes


def save_hash_set(path, hash_set):
    """Loads a local copy of pepe hashes, useful for banning locally
    malicious files or protecting the dht"""
    with open(path, "w") as hash_list:
        for pepe_hash in hash_set:
            if pepe_hash != "":
                hash_list.write(pepe_hash + "\n")
    logging.debug("saved {} as {}".format(path, hash_set))



class PepeMan:
    def __init__(self,
                 ipfs_conn,
                 host='localhost',
                 database="rare_pepes",
                 banned_pepes_path="rare_pepes/avoid_pepes.db",
                 local_pepes_path="rare_pepes/known_pepes.db"):
        self.pubsub = ipfs_pubsub.PubSub(host)
        self.ipfs_conn = ipfs_conn
        self.database = database

        # List of pepe hashes that you've banned LOCALLY, this helps in
        # avoiding unwanted content to show up in your browser
        self.banned_pepes = load_hash_set(banned_pepes_path)
        self.banned_pepes_path = banned_pepes_path

        # Local list of pepes
        self.local_pepes = load_hash_set(local_pepes_path) - self.banned_pepes
        self.local_pepes_path = local_pepes_path
        for key in pepenet_channels:
            self.pubsub.topic_sub(pepenet_channels[key])

        logging.debug("Topics subscribed: {}".format(self.pubsub.topic_ls()))

        self.pubsub.topic_set_callback(pepenet_channels["update_control"],
                                       self._on_update_control)

        self.pubsub.topic_set_callback(pepenet_channels["upload"],
                                       self._on_upload)

        self.update_pepe_list(self.local_pepes)

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
                              control_codes["updating_finished"])

    def _on_update_control(self, data):
        """Callback when pubsub updates
        data has the following keys: ["content", "sender", "timestamp"]"""
        logging.debug("Received. {}".format(data))
        code = b64decode(data["content"]).decode('utf8')
        if code == control_codes["updating_finished"]:
            self._on_update_request(data["sender"])

    def _on_update_request(self, sender_id):
        """
            After the updater has sent his uploading_finished CC
            we upload our hashes
        """
        encoded_pepe_hashes = self.pubsub.\
            topic_pop_messages_from_sender(pepenet_channels["update"],
                                           sender_id)

        pepe_hashes = {b64decode(pepe_hash).decode("utf-8")
                       for pepe_hash in encoded_pepe_hashes}

        logging.debug("updating hashes: {}".format(pepe_hashes))
        # We remove the pepes that we don't want
        received_hashes = pepe_hashes - self.banned_pepes
        # Then we check if they've sent us some new hashes
        new_hash_delta = received_hashes - self.local_pepes

        delta = self.local_pepes - received_hashes
        logging.debug("Sending hashes: {}".format(delta))

        for pepe_hash in delta:
            self.pubsub.topic_pub(pepenet_channels["update"], pepe_hash)
        if delta:
            self.pubsub.topic_pub(pepenet_channels["update_control"],
                                  control_codes["updating_finished"])

        self.local_pepes.update(new_hash_delta)

    def _on_upload(self, data):
        """Callback called when someone on the network uploads a pepe
        self.local_pepes is set, so if the pepe is a duplicate i will not
        be added twice"""

        self._register_pepe(b64decode(data["content"]).decode('utf8'))
        logging.info("Received pepe: {}".format(b64decode(data["content"])
                                                .decode('utf8')))

    def get_timestamp(self, pepe):
        """
        The client sends a dict containing the pepe hash and it's possible
        timestamp, and then waits until a percentage of the network responds.
        Other clients respond only if their timestamp is different.
        If the number of responses > the number of non responses we consider
        the most popoular one as valid
        """
        # We want atleast 60% of the network to agree
        minimun_response_ratio = .6

        compact_pepe = {"pepe_hash": pepe.hash,
                        "timestamp": pepe.timestamp
                        }
        self.pubsub.pub(pepenet_channels["metadata"], compact_pepe)

        pass

    def _on_timestamp_update(self, data):
        "Timestamp channel callback"
        pass

    def get_peer_number(self):
        "Returns the number of connected peers to the network"
        return self.pubsub.topic_peer_number(pepenet_channels["update"])

    def get_pepe(self, pepe_hash):
        "Downloads pepe from ipfs and saves it in database folder"
        self.ipfs_conn.get(pepe_hash)
        target_path = os.path.join(self.database, pepe_hash)
        os.rename(pepe_hash, target_path)
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
        returns its hash
        """
        logging.info("Uploading pepe: {}".format(path))
        res = self.ipfs_conn.add(path)
        self.pubsub.topic_pub(pepenet_channels["upload"], res["Hash"])
        self._register_pepe(res["Hash"])
        logging.info("Uploaded from {} as {}".format(path, res["Hash"]))
        return res["Hash"]

    def calc_normieness(self, pepe_hash):
        """
            This function calculates the normieness of a pepe based on the
            function definition
        """
        day = 24
        week = 168
        month = 730
        year = 87600


        pepe_types = {"Absolute cancer": {"perc_bounds": (.8, 1),
                                          "time_threshold": (2*week, 100*year),
                                          "val": 0
                                          },
                      "Pop": {"perc_bounds": (.8, 1),
                              "time_threshold": (day, 2*week),
                              "val": 1
                              },
                      "Spammed": {"perc_bounds": (.05, 1),
                                  "time_threshold": (0, day),
                                  "val": 2
                                  },
                      "Normified": {"perc_bounds": (.05, .2),
                                    "time_threshold": (day, 100*year),
                                    "val": 3
                                    },
                      "Outdated": {"perc_bounds": (0, .05),
                                   "time_threshold": (2*week, 100*year),
                                   "val": 4
                                   },
                      "Novel": {"perc_bounds": (0, .05),
                                "time_threshold": (0, day),
                                "val": 5
                                },
                      "Artifact": {"perc_bounds": (.05, .2),
                                   "time_threshold": (1*month, 100*year),
                                   "val": 6
                                   },
                      "Rare": {"perc_bounds": (.05, .2),
                               "time_threshold": (day, 100*year),
                               "val": 7
                               }
                      }

        copies_number = 0
        for entry in self.ipfs_conn.dht_findprovs(pepe_hash):
            if entry["Type"] == 4:
                copies_number += 1

        # This avoid the 0 division and doesn't skew the results
        peer_number = self.get_peer_number() + 1

        # We should put the time difference from the posting time and the
        # actual time here
        delta_time = 0

        perc_val = copies_number / peer_number

        logging.debug("{}/{} Peers have {}".format(copies_number,
                                                   peer_number,
                                                   pepe_hash))

        for name, info in pepe_types.items():
            if perc_val <= info["perc_bounds"][1] and \
               perc_val >= info["perc_bounds"][0]:
                logging.debug("Calculated normieness for: {} Result: {} ({})".
                              format(pepe_hash, name, info))
                return (name, info["val"])

        return ("Novel", 5)

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
    def __init__(self, pepe_hash, timestamp=time.time(), tags=[]):
        self.hash = pepe_hash
        self.timestamp = timestamp
        self.tags = tags

    def __repr__(self):
        dict_repr = {"pepe_hash": self.hash,
                     "timestamp": self.timestamp,
                     "tags": self.tags
                     }
        return str(dict_repr)

    def __eq__(self, other):
        """
        This method is used when you're comparing 2 pepes in a logical
        construct
        """
        if isinstance(other, Pepe):
            return ((self.hash == other.hash) and
                    (self.timestamp == other.timestamp) and
                    (self.tags == other.tags))
        else:
            return False

    def __ne__(self, other):
        """
        This method is used when you're comparing 2 pepes in a logical
        construct
        """
        return (not self.__eq__(other))

    def __hash__(self):
        """
        This method is used when you're searching in a hash table or set
        """
        return self.hash


if __name__ == "__main__":
    print("Don't execute this module directly")
