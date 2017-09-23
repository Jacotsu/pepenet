#!/usr/bin/env python3


class DistrDataMan:
    def __init__(self):
        self.data = {}

    def insert_entry(self, key, entry_id, value):
        if not self.data[key]:
            self.data[key] = {}
        # Every entry must be unique, that's why we need an id
        self.data[key].update((entry_id, value))

    def get_value(self, key):
        values = {}
        max_val = None

        for entry, val in self.data[key]:
            if not max_val:
                max_val = val

            if not values[val]:
                values[val] = 1
            else:
                values[val] += 1
                if values[val] > values[max_val]:
                    max_val = val

        return max_val

    def get_number_of_entries(self, key):
        return len(self.data[key])
