#!/usr/bin/env python3

import sqlite3
from sqlite3 import IntegrityError
import logging
from pepe import Pepe

queries = {"init_pepe_hashes_tbl": "CREATE TABLE IF NOT EXISTS pepe_hashes ("
                                   "hash VARCHAR(128) NOT NULL,"
                                   "banned BIT DEFAULT 'TRUE',"
                                   "op VARCHAR(128),"
                                   "PRIMARY KEY (hash)"
                                   ");",
           "init_pepe_metadata_tbl": "CREATE TABLE IF NOT EXISTS pepe_metadata"
                                     "(id INT PRIMARY KEY,"
                                     "hash VARCHAR(128) NOT NULL,"
                                     "timestamp TIMESTAMP,"
                                     "tags MEDIUMTEXT,"
                                     "rareness FLOAT"
                                     ");",
           "insert_pepe": "INSERT INTO pepe_hashes(hash, banned, op)"
                          "VALUES (?, ?, ?)",
           "get_pepes": "SELECT * FROM pepe_hashes;",
           "get_pepe": "SELECT * FROM pepe_hashes WHERE hash=?;",
           "rm_pepe": "DELETE FROM pepe_hashes WHERE hash=?;",
           "exists_pepe": "SELECT 1 FROM pepe_hashes WHERE hash=?;"
           }


class PepeDB:

    def __init__(self, db_file="pepenet.db"):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()
        self.cur.execute(queries["init_pepe_hashes_tbl"])
        self.cur.execute(queries["init_pepe_metadata_tbl"])

    def insert_pepes(self, pepes):
        if pepes is not list:
            pepes = [pepes]
        try:
            for pepe in pepes:
                self.cur.execute(queries["insert_pepe"],
                                 (pepe.hash, False, None))
            self.conn.commit()
        except IntegrityError:
            logging.error("Pepe already in database")

    def remove_pepes(self, pepes):
        if pepes is not list:
            pepes = [pepes]
        try:
            for pepe in pepes:
                self.cur.execute(queries["rm_pepe"], (pepe.hash,))
            self.conn.commit()
        except IntegrityError:
            logging.error("Pepe not in database")

    def get_pepes(self, hashes=[]):
        pepes = []

        if len(hashes) == 0:
            for result in self.cur.execute(queries["get_pepes"]):
                try:
                    logging.debug(result)
                    pepes.append(Pepe(result[0]))
                except:
                    logging.error(result)

        if hashes is not list:
            hashes = [hashes]

        for pepe_hash in hashes:
            try:
                result = self.cur.execute(queries["get_pepe"], (pepe_hash,))
                logging.debug(result)
                pepes.append(Pepe(result[0]))
            except:
                logging.error(result)

        return pepes

    def is_pepes_stored(self, pepe_hash):
        result = self.cur.execute(queries["exists_pepe"], (pepe_hash,))
        if result:
            return True

        return False
