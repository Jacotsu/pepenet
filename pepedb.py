#!/usr/bin/env python3

import sqlite3

queries = {"mk_pepe_hashes": "IF NOT EXISTS (SELECT * FROM \
                                        INFORMATION_SCHEMA.TABLES \
                                        WHERE TABLE_NAME = 'pepe_hashes' \
                              CREATE TABLE pepe_hashes ( \
                                  hash VARCHAR(128) NOT NULL, \
                                  banned BIT DEFAULT 'TRUE', \
                                  op VARCHAR(128), \
                                  PRIMARY KEY (hash) \
                              );",
           "mk_pepe_metadata": "IF NOT EXISTS (SELECT * FROM \
                                        INFORMATION_SCHEMA.TABLES \
                                        WHERE TABLE_NAME = 'pepe_metadata' \
                                CREATE TABLE pepe_metadata (\
                                    id INT NOT NULL AUTO_INCREMENT, \
                                    hash VARCHAR(128) NOT NULL, \
                                    timestamp TIMESTAMP, \
                                    tags MEDIUMTEXT, \
                                    rareness FLOAT \
                                );",
           "insert_pepe": "INSERT INTO pepe_hashes(hash=?, banned=?, op=?)"
           }


class PepeDB:

    def __init__(self):
        self.conn = sqlite3.connect("pepenet.db")
        self.cur = self.conn.cursor()
        self.cur.execute(queries["mk_pepe_hashes"])
        self.cur.execute(queries["mk_pepe_metadata"])

    def insert_pepe(self, pepe): 

