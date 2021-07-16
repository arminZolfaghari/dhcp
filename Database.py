import pymongo
from time import gmtime, strftime

databases = pymongo.MongoClient("mongodb://localhost:27017/")
DHCP_database = databases["DHCP"]
clients_collection = DHCP_database["Clients"]


def add_client_information(client_mac_address, ip):
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    inserted_object = {"allocated_time": current_time, "client_mac_address": client_mac_address, "ip": ip}
    clients_collection.insert_one(inserted_object)

def update_client_information():
    pass



