#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!
from tenable.sc import TenableSC
from tenable.io import TenableIO

sc = TenableSC("")
sc.login("", "")

tio = TenableIO(access_key='', secret_key='')


#Get Agent IPs from Tenable.io
def get_ips():
    #great an empty list
    list = []
    for agent in tio.agents.list():
        ip = agent['ip']
        list.append(ip)
    return list


def get_or_create():

    #load all of the current asset lists for parsing
    asset_lists = sc.asset_lists.list()

    #grab the latest agent IPs from Tenable.io
    list = get_ips()

    #set asset_id to zero to toggle creating a new list
    asset_id = 0

    #cycle through all of the assets in SC and search for our list
    for assets in asset_lists['manageable']:

        if assets['name'] == "Exclude Agents":
            #if we found our list, grab the ID
            asset_id = assets['id']

    #verify we found the list
    if asset_id == 0:
        #looks like we didn't find it; lets create it
        sc.asset_lists.create("Exclude Agents", "static", ips=list)
    else:
        #We found our list, let's update it
        sc.asset_lists.edit(asset_id, ips=list)

    sc.logout()

if __name__ == '__main__':
    get_or_create()
