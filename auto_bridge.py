#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!
#This script downloads all of the latest scan information for the IDs you specificy in a list format
#This script only imports into one repository

from tenable.sc import TenableSC
from tenable.io import TenableIO
import os

sc = TenableSC("1.1.1.1")
sc.login("uname", "password")

tio = TenableIO(access_key='', secret_key='')

def download_scans():

    #enter your scan id's below
    scan_id = (13,4001)

    #enter the repoistor to input the data into
    repo_id = 20
    try:
        for scan in scan_id:
            #export the scan
            with open('{}.nessus'.format(str(scan)), 'wb') as nessus:
                tio.scans.export(scan, fobj=nessus)

            #import the scan
            with open('{}.nessus'.format(str(scan))) as file:
                sc.scan_instances.import_scan(file,repo_id)

            #delete the scan
            os.remove('{}.nessus'.format(str(scan)))
    except:
        pass

if __name__ == '__main__':
    download_scans()

