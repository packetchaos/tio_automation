#!/usr/bin/env python3
#This Script Requires the Export Script be run
import requests
import json

requests.packages.urllib3.disable_warnings()

def grab_headers():
    # Enter Your Access keys
    access_key = ''
    secret_key = ''

    # Set the Authentication Header
    headers = {'Content-type': 'application/json', 'X-ApiKeys': 'accessKey=' + access_key + ';secretKey=' + secret_key}
    return headers


def get_data(url_mod):
    # Base URL
    url = "https://cloud.tenable.com"

    # Retreive Headers
    headers = grab_headers()

    # API Call
    r = requests.request('GET', url + url_mod, headers=headers, verify=False)

    # convert response to json
    data = r.json()

    # return data in json format
    return data


def post_data(url_mod, payload):
    # Set the URL endpoint
    url = "https://cloud.tenable.com"

    # grab headers for auth
    headers = grab_headers()

    # send Post request to API endpoint
    r = requests.post(url + url_mod, json=payload, headers=headers, verify=False)

    # retreive data in json format
    data = r.json()

    return data


def create_target_group(tg_name, tg_list):
    #turn the list back into a string seperated by a comma
    trgstring = ','.join(tg_list)

    print("These are the IPs that will be added to the target Group", tg_list)

    #create payload to create a new Target Groups
    payload = dict({"name":tg_name, "members": str(trgstring),"type":"system","acls":[{"type":"default", "permissions":64}]})

    try:
        #Create a target group
        post_data('/target-groups', payload)

    except:
        print("An Error Occurred")


def targetgroup_by_plugin(name, plugin):
    #create a empty list to fill with our assets
    target_list = []

    try:
        #open our file we created with the export.py program
        with open('tio_vuln_data.json') as json_file:
            #put the data into a varable
            data = json.load(json_file)

            #loop through the data
            for x in data:

                #Search for our plugin
                if str(x['plugin']['id']) == plugin:

                    #grab the IP so we can enter it into our List
                    ip = x['asset']['ipv4']

                    #ensure there are no duplicates; check to see if the current IP is already in the list
                    if ip not in target_list:

                        #add unique IP to the list
                        target_list.append(ip)

                        #inform the user of the IPs that will be added to the list
                        print("\nIP : ", ip)
                else:
                    #skip on error.  This could be an asset without an IP like a WAS scan.
                    pass

        #send the list and name for creation
        create_target_group(name, target_list)

    except:
        print("Local Cache is corrupt; Use the Export script")


def targetgroup_by_plugin_name(name, pname):

    target_list = []

    try:
        with open('tio_vuln_data.json') as json_file:

            data = json.load(json_file)

            for x in data:

                plugin_name = x['plugin']['name']

                if pname in plugin_name:

                    ip = x['asset']['ipv4']

                    if ip not in target_list:

                        target_list.append(ip)

                        print("\nIP : ", ip)
                else:
                    pass

        print(target_list)

        # send the list and name for creation
        create_target_group(name, target_list)

    except:
        print("Local Cache is corrupt; Use the Export script")


def targetgroup_by_text_in_output(name, text, plugin):
        target_list = []

        try:

            with open('tio_vuln_data.json') as json_file:

                data = json.load(json_file)

                for x in data:

                    if str(x['plugin']['id']) == plugin:

                        if text in x['output']:

                            ip = x['asset']['ipv4']


                            if ip not in target_list:

                                target_list.append(ip)

                                print("\nIP : ", ip)
                    else:
                        pass

            print(target_list)

            #send the list and name for creation
            create_target_group(name,target_list)
        except:
            print("Local Cache is corrupt; Use the Export script")


def main():
    targetgroup_by_plugin("Docker", str(93561))
    targetgroup_by_plugin_name("Microsoft Assets", "Microsoft")
    targetgroup_by_text_in_output("Wireshark Assets", "Wireshark", str(20811))


if __name__ == '__main__':
    main()