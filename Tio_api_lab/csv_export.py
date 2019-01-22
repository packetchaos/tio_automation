import json
import csv
import requests

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


def csv_export():
    with open('tio_asset_data.json') as json_file:
        data = json.load(json_file)

        #Create our headers - We will Add these two our list in order
        header_list = ["IP Address", "Hostname", "FQDN", "UUID", "First Found", "Last Found", "Operating System",
                       "Mac Address", "Tags", "Info", "Low", "Medium", "High", "Critical"]

        #Crete a csv file object
        with open('csv_data.csv', mode='w') as csv_file:
            agent_writer = csv.writer(csv_file, delimiter=',', quotechar='"')

            #write our Header information first
            agent_writer.writerow(header_list)

            #Loop through each asset
            for assets in data:
                #create a blank list to append asset details
                csv_list = []
                #Try block to ignore assets without IPs
                try:
                    #Capture the first IP
                    ip = assets['ipv4s'][0]
                    csv_list.append(ip)

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

                    id = assets['id']
                    csv_list.append(id)
                    csv_list.append(assets['first_seen'])
                    csv_list.append(assets['last_seen'])
                    try:
                        csv_list.append(assets['operating_systems'][0])
                    except:
                        csv_list.append(" ")

                    try:
                        csv_list.append(assets['mac_addresses'][0])
                    except:
                        csv_list.append(" ")

                    try:
                        csv_list.append(assets['tags'][0]['value'])
                    except:
                        csv_list.append(" ")

                    info = get_data('/workbenches/assets/' + id + '/info')

                    for counts in info['info']['counts']['vulnerabilities']['severities']:
                        count = counts['count']
                        csv_list.append(count)

                    agent_writer.writerow(csv_list)

                except IndexError:
                    pass


def main():
    csv_export()

if __name__ == '__main__':
    main()