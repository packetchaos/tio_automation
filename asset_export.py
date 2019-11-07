#!/usr/bin/env python3
import requests
import csv
import time
requests.packages.urllib3.disable_warnings()

def grab_headers():
    access_key = ''
    secret_key = ''

    #set the header
    headers = {'Content-type':'application/json','X-ApiKeys':'accessKey='+access_key+';secretKey='+secret_key}
    return headers


def get_data(url_mod):
    url = "https://cloud.tenable.com"
    headers = grab_headers()
    try:
        r = requests.request('GET', url + url_mod, headers=headers, verify=False)

        if r.status_code == 200:
            data = r.json()
            #print(r.headers)
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
    #Trying to catch API errors


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


def asset_export():
    # Set the payload to the maximum number of assets to be pulled at once
    thirty_days = time.time() - 7776000#2660000
    pay_load = {"chunk_size": 100}#, "filters": {"last_assessed": int(thirty_days)}}
    try:
        # request an export of the data
        export = post_data("/assets/export", pay_load)

        # grab the export UUID
        ex_uuid = export['export_uuid']
        print('Requesting Asset Export with ID : ' + ex_uuid)

        # now check the status
        status = get_data('/assets/export/' + ex_uuid + '/status')

        # status = get_data('/vulns/export/89ac18d9-d6bc-4cef-9615-2d138f1ff6d2/status')
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


        # create an empty list to put all of our data into.
        data = []

        #Create our headers - We will Add these two our list in order
        header_list = ["IP Address", "Hostname", "FQDN", "UUID", "First Found", "Last Found", "Operating System",
                       "Mac Address", "Agent UUID", "Last Licensed Scan Data"]

        #Crete a csv file object
        with open('asset_data.csv', mode='w', newline='') as csv_file:
            agent_writer = csv.writer(csv_file, delimiter=',', quotechar='"')

            #write our Header information first
            agent_writer.writerow(header_list)

            # loop through all of the chunks
            for x in range(len(status['chunks_available'])):
                chunk_data = get_data('/assets/export/' + ex_uuid + '/chunks/' + str(x+1))

                print("Parsing Chunk {} ...Finished".format(x+1))
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

                        agent_writer.writerow(csv_list)

                    except IndexError:
                        pass

    except KeyError:
        print("Well this is a bummer; you don't have permissions to download Asset data :( ")


if __name__ == '__main__':
    #vuln_export()
    asset_export()
    print("\nStarting your CSV Export now")
    #csv_export()
    #print("\nYour export is finished")
    #print("\nStarting your agent CSV Export")
    #agent_export()
    #print("\nAgent Export Finished")
