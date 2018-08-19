import csv

import os
from collections import namedtuple


class CSVWriter:

    def __init__(self, directory="data"):
        self.directory = directory
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def write(self, filename, data, columns=None):
        if columns is None:
            columns = ["game_id", "name", "url"]
        file_path = os.path.join(self.directory, filename)
        mode = "w"
        if os.path.exists(file_path):
            mode = "a"

        with open(file_path, mode, newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            if mode == "w":
                writer.writerow(columns)
            for row in data:
                writer.writerow(row)


Entry = namedtuple("Entry", ["id", "name", "url"])


class CSVReader:

    def read(self, file_path, has_columns=True):
        entries = []
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            for index, row in enumerate(reader):
                if has_columns and index == 0:
                    continue
                game_id = int(row[0])
                name = row[1]
                url = row[2]
                entries.append(Entry(id=game_id, name=name, url=url))
        return entries


