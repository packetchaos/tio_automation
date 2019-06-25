#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!
from tenable.sc import TenableSC
from tenable.io import TenableIO

sc = TenableSC("192.168.128.18")
sc.login("creid", "hacker")

tio = TenableIO(access_key='9a161e59ea21cbf3206b2109b38284a3f9d95bbd88b6fa48f6ca541a2fc88375', secret_key='6aa0f9fed1703cab588656fb6ebd191c1fe4219e99a910aef8029ceaae9d6537')


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
