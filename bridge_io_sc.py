#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!
#This script reaches out to Tenable IO and exports the latest scan information by Scan ID of your choice
#Then it imports the nessus data into a repository of your choice
#zero Error correction
from tenable.sc import TenableSC
from tenable.io import TenableIO

sc = TenableSC("1.1.1.1")
sc.login("user", "password")

tio = TenableIO(access_key='', secret_key='')

def download_scans():

    print("I'm grabbing All of your Scans and their IDs\b")
    scans = tio.scans.list()
    print("\bScan Name - Scan ID")
    print("-------------------\b")
    for scan in scans:
        print(scan['name'], scan['id'])

    print()
    scan_id = input("What is the Scan ID you want to do Download and Import?")

    with open('newscan.nessus', 'wb') as nessus:
        tio.scans.export(scan_id, fobj=nessus)

    print("I'm grabbing all of the repositories to Choose from\b")
    print("Repo Name - Repo ID")
    print("-------------------\b")
    for repo in sc.repositories.list():
        print(repo['name'], repo['id'])

    repo_id = input("What is your Repository ID?")

    #import the scan
    with open('newscan.nessus') as file:
        sc.scan_instances.import_scan(file,repo_id)

if __name__ == '__main__':
    download_scans()
