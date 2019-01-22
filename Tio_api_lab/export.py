#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!

#This script downloads Vulnerability and Asset Data from Tenable.io and saves it locally
#Two files are saved - tio_asset_data.json and tio_vuln_data.json
import requests
import time
import json
import pprint

#avoid insecure warning
requests.packages.urllib3.disable_warnings()

def grab_headers():
    #Enter Your Access keys
    access_key = ''
    secret_key = ''

    #Set the Authentication Header
    headers = {'Content-type':'application/json','X-ApiKeys':'accessKey='+access_key+';secretKey='+secret_key}
    return headers


def get_data(url_mod):
    #Base URL
    url = "https://cloud.tenable.com"

    #Retreive Headers
    headers = grab_headers()

    #API Call
    r = requests.request('GET', url + url_mod, headers=headers, verify=False)

    #convert response to json
    data = r.json()

    #return data in json format
    return data


def post_data(url_mod,payload):
    #Set the URL endpoint
    url = "https://cloud.tenable.com"

    #grab headers for auth
    headers = grab_headers()

    #send Post request to API endpoint
    r = requests.post(url + url_mod, json=payload, headers=headers, verify=False)

    #retreive data in json format
    data = r.json()

    return data


def vuln_export():
    # Limit the data to 30 days
    thirty_days = time.time() - 2592000

    # Set the payload to the maximum number of assets to be pulled at once
    pay_load = {"num_assets": 5000, "filters": {"last_found": int(thirty_days)}}

    # request an export of the data
    export = post_data("/vulns/export", pay_load)

    # grab the export UUID
    ex_uuid = export['export_uuid']

    # Let the user know the Export ID
    print('Requesting Export with ID : ' + ex_uuid)

    # now check the status
    status = get_data('/vulns/export/' + ex_uuid + '/status')

    print(status)

    #set a variable to True for our While loop
    not_ready = True

    #loop to check status until finished
    while not_ready is True:
        #Pull the status, then pause 5 seconds and ask again.
        if status['status'] == 'PROCESSING':
            time.sleep(5)
            status = get_data('/vulns/export/' + ex_uuid + '/status')
            print(status)

        #Exit Loop once confirmed finished
        elif status['status'] == 'FINISHED':
            not_ready = False

        #Tell the user an error occured
        else:
            print("Error occurred")

    #create an empty list to put all of our data into.
    data = []

    #loop through all of the chunks that are available
    for x in status['chunks_available']:
        # Add 1 to the value of X because it will start at 0, and there isn't going to be  a zero chunk.
        chunk_data = get_data('/vulns/export/' + ex_uuid + '/chunks/' + str(x))

        # Add data to our list
        data.append(chunk_data)

        #open a new file
        with open('tio_vuln_data.json', 'w') as json_outfile:

            #write the data we have to the file
            json.dump(chunk_data, json_outfile)

            #close the file
            json_outfile.close()


def asset_export():
    #Limit the data to the last 30 days
    thirty_days = time.time() - 2592000

    # Set the payload to the maximum number to be pulled at once
    pay_load = {"chunk_size": 5000, "filters": {"last_assessed": int(thirty_days)}}

    # request an export of the data
    export = post_data("/assets/export", pay_load)

    # grab the export UUID
    ex_uuid = export['export_uuid']

    #let the use know the export ID
    print('Requesting Export with ID : ' + ex_uuid)

    # now check the status
    status = get_data('/assets/export/' + ex_uuid + '/status')

    print(status)

    # set a variable to True for our While loop
    not_ready = True

    # loop to check status until finished
    while not_ready is True:
        # Pull the status, then pause 5 seconds and ask again.
        if status['status'] == 'PROCESSING':

            #pause the program for 5 seconds and check the status again
            time.sleep(5)

            #pull new status
            status = get_data('/assets/export/' + ex_uuid + '/status')

            #notify the user of the current status
            print(status)

        # Exit Loop once confirmed finished
        elif status['status'] == 'FINISHED':

            #set not_ready to false to exit while-loop
            not_ready = False

        #Inform the user or use pass to ignore any errors
        else:
            print("Something Went wrong")

    # create an empty list to put all of our data into.
    data = []

    # loop through all of the chunks
    for x in status['chunks_available']:
        #Download the chunk data
        chunk_data = get_data('/assets/export/' + ex_uuid + '/chunks/' + str(x))

        #append the data to the temp list
        data.append(chunk_data)

        #open a new file to save to
        with open('tio_asset_data.json', 'w') as json_outfile:
            #write the data to the file
            json.dump(chunk_data, json_outfile)

            #close the file
            json_outfile.close()


def main():
    asset_export()
    vuln_export()


if __name__ == '__main__':
    main()