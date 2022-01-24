from pymongo import MongoClient
import yaml


class MongoDatabase:
    client: MongoClient

    def __init__(self) -> None:
        with open('config/db.yaml') as f:
            conf_yml = yaml.safe_load(f)

        self.client = MongoClient(conf_yml['connection_string'])
        self.db = self.client.db
