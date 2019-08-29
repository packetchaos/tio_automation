#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!
#This script downloads all the all-2.0.tar file using the special URL provided in the offline updates document
#https://docs.tenable.com/sccv/5_8/Content/OfflineNessusPluginUpdate.htm
#https://docs.tenable.com/sccv/5_8/Content/OfflineSCFeedUpdate.htm
#This script changes the name of the all-2.0.tar to the supported names and imports them in to T.sc
from tenable.sc import TenableSC
import requests

sc = TenableSC('192.168.128.22')
sc.login('admin', "password")

url = 'special url'
plugins = requests.get(url)

open('sc-plugins-diff.tar.gz', 'wb').write(plugins.content)
with open('sc-plugins-diff.tar.gz', 'rb') as pubfile :
    print(sc.feeds.process('active', pubfile))

open('SecurityCenterFeed48.tar.gz', 'wb').write(plugins.content)
with open('SecurityCenterFeed48.tar.gz', 'rb') as feed:
    print(sc.feeds.process('sc', feed))

sc.logout()
