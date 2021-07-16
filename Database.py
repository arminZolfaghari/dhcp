import pymongo
from time import gmtime, strftime

databases = pymongo.MongoClient("mongodb://localhost:27017/")
DHCP_database = databases["DHCP"]
clients_collection = DHCP_database["Clients"]


def add_client_information(client_mac_address, ip):
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    inserted_object = {"allocated_time": current_time, "client_mac_address": client_mac_address, "ip": str(ip)}
    clients_collection.insert_one(inserted_object)


def update_client_information(client_mac_address, ip):
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    clients_collection.update_one({"client_mac_address": client_mac_address},
                                  {"$set": {"allocated_time": current_time}})


def read_from_database():
    client_information = clients_collection.find({}, {"_id": 0, "client_mac_address": 1, "allocated_time": 1, "ip": 1})
    return client_information[-1]


