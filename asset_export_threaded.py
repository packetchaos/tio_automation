#!/usr/bin/env python3

import requests
import csv
import time
import threading
from queue import Queue

lock = threading.Lock()

q = Queue()

def grab_headers():
    access_key = ''
    secret_key = ''

    # set the header
    headers = {'Content-type': 'application/json', 'X-ApiKeys': 'accessKey='+access_key+';secretKey='+secret_key}
    return headers


def get_data(url_mod):
    url = "https://cloud.tenable.com"
    headers = grab_headers()
    try:
        r = requests.request('GET', url + url_mod, headers=headers, verify=True)

        if r.status_code == 200:
            data = r.json()
            # print(r.headers)
            return data
        elif r.status_code == 404:
            print('Check your query...')
            print(r)
        elif r.status_code == 429:
            print("Too many requests at a time... Threading is unbound right now.")
        elif r.status_code == 400:
            pass
        else:
            print("Something went wrong...Don't be trying to hack me now")
            print(r)
    except ConnectionError:
        print("Check your connection...You got a connection error")


def post_data(url_mod, payload):
    # Set the URL endpoint
    url = "https://cloud.tenable.com"

    # grab headers for auth
    headers = grab_headers()

    # send Post request to API endpoint
    r = requests.post(url + url_mod, json=payload, headers=headers, verify=True)

    # retrieve data in json format
    data = r.json()

    return data


def worker():
    # The worker thread pulls an item from the queue and processes it
    while True:
        item = q.get()
        parse_data(get_data(item))
        q.task_done()


def parse_data(chunk_data):

    # Open up current CSV and append data
    with open('threaded_asset_list.csv', mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')

        # cycle through each chunk and grab the data we want
        for assets in chunk_data:
            #create a blank list to append asset details
            csv_list = []
            #Try block to ignore assets without IPs
            try:
                #Capture the first IP
                try:
                    ip = assets['ipv4s'][0]
                    csv_list.append(ip)
                except:
                    csv_list.append(" ")
                #try block to skip if there isn't a hostname
                try:
                    csv_list.append(assets['hostnames'][0])

                except:
                    # If there is no hostname add a space so columns still line up
                    csv_list.append(" ")

                try:
                    csv_list.append(assets['fqdns'][0])
                except:
                    csv_list.append(" ")

                try:
                    id = assets['id']
                    csv_list.append(id)
                except:
                    csv_list.append(" ")
                try:

                    csv_list.append(assets['first_seen'])
                except:
                    csv_list.append(" ")
                try:

                    csv_list.append(assets['last_seen'])
                except:
                    csv_list.append(" ")
                try:
                    csv_list.append(assets['operating_systems'][0])
                except:
                    csv_list.append(" ")

                try:
                    csv_list.append(assets['mac_addresses'][0])
                except:
                    csv_list.append(" ")

                try:
                    csv_list.append(assets['agent_uuid'])
                except:
                    csv_list.append(" ")

                try:
                    csv_list.append(assets["last_licensed_scan_date"])
                except:
                    csv_list.append(" ")

                # print(csv_list)
                csv_writer.writerow(csv_list)
            except:
                print("bummer")


def request_export():
    urls = []
    # Set the payload to the maximum number of assets to be pulled at once
    thirty_days = time.time() - 2660000
    pay_load = {"chunk_size": 10000}#, "filters": {"last_found": int(thirty_days)}}
    try:
        # request an export of the data
        export = post_data("/assets/export", pay_load)

        # grab the export UUID
        ex_uuid = export['export_uuid']
        print('Requesting Asset Export with ID : ' + ex_uuid)

        # now check the status
        status = get_data('/assets/export/' + ex_uuid + '/status')

        # status = get_data('/vulns/export/export_id/status')
        print("Status : " + str(status["status"]))

        # set a variable to True for our While loop
        not_ready = True

        # loop to check status until finished
        while not_ready is True:
            # Pull the status, then pause 5 seconds and ask again.
            if status['status'] == 'PROCESSING' or 'QUEUED':
                time.sleep(5)
                status = get_data('/assets/export/' + ex_uuid + '/status')
                print("Status : " + str(status["status"]))

            # Exit Loop once confirmed finished
            if status['status'] == 'FINISHED':
                not_ready = False

            # Tell the user an error occured
            if status['status'] == 'ERROR':
                print("Error occurred")

        #create a new csv to save our data
        with open('threaded_asset_list.csv', mode='w', newline='') as csv_file:
            new_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
            header_list = ["IP Address", "Hostname", "FQDN", "UUID", "First Found", "Last Found", "Operating System",
                           "Mac Address", "Agent UUID", "Last Licensed Scan Data"]
            new_writer.writerow(header_list)

        # grab all of the chunks and craft the URLS for threading
        for y in range(len(status['chunks_available'])):
            urls.append('/assets/export/' + ex_uuid + '/chunks/' + str(y+1))

        start = time.time()
        # Create the queue and thread pool.

        for i in range(4):
            t = threading.Thread(target=worker)
            t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
            t.start()

        # stuff work items on the queue (in this case, just a number).
        #start = time.perf_counter()
        for item in range(len(urls)):
            q.put(urls[item])

        q.join()
        end = time.time()
        print(end - start)

    except KeyError:
        print("Well this is not cool")

if __name__ == '__main__':
    request_export()
