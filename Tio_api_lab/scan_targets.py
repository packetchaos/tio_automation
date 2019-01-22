#!/usr/bin/env python3
#Disclaimer: This is NOT supported By Tenable!

#This script scans specified targets
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

    return dat


def nessus_scanners():
    try:
        data = get_data('/scanners')

        for x in data["scanners"]:
            print(str(x["name"]) + " : " + str(x["id"]))
    except:
        print("You may not have access...Check permissions.")


def scan(targets):

    print("\nChoose your Scan Template")
    print("1.  Basic")
    print("2   Discovery Scan")
    option = input("Please enter option #.... ")
    if option == '1':
        template = "731a8e52-3ea6-a291-ec0a-d2ff0619c19d7bd788d6be818b65"
    elif option == '2':
        template = "bbd4f805-3966-d464-b2d1-0079eb89d69708c3a05ec2812bcf"
    elif len(option) == 52:
        template = str(option)
    else:
        print("Using Basic scan since you can't follow directions")
        template = "731a8e52-3ea6-a291-ec0a-d2ff0619c19d7bd788d6be818b65"

    print("Here are the available scanners")
    print("Remember, don't pick a Cloud scanner for an internal IP address")
    nessus_scanners()
    scanner_id = input("What scanner do you want to scan with ?.... ")

    print("creating your scan of : " + targets + "  Now...")

    payload = dict(uuid=template, settings={"name": "Script Created Scan of " + targets,
                                            "enabled": "true",
                                            "scanner_id": scanner_id,
                                            "text_targets": targets})

    scan_data = post_data('/scans', payload)

    # pull scan ID after Creation
    scan = scan_data["scan"]["id"]

    print(scan)

    # launch Scan
    launch = requests.post('https://cloud.tenable.com/scans/'+ str(scan) + '/launch', headers=grab_headers(), verify=False)

    response = launch.json()

    # print Scan UUID
    print("A scan started with UUID: " + str(response['scan_uuid']))
    print("The scan ID is " + str(scan))


def main():
   scan("192.168.128.200")


if __name__ == '__main__':
    main()