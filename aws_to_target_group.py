import requests
from IPy import IP


def grab_headers():
    access_key = ''
    secret_key = ''
    return {'Content-type': 'application/json', 'user-agent': 'Navi:aws:tgroup', 'X-ApiKeys': 'accessKey=' + access_key + ';secretKey=' + secret_key}


def request_data(method, url_mod, **kwargs):

    # set the Base URL
    url = "https://cloud.tenable.com"

    # check for params and set to None if not found
    try:
        params = kwargs['params']
    except KeyError:
        params = None

    # check for a payload and set to None if not found
    try:
        payload = kwargs['payload']
    except KeyError:
        payload = None

    try:
        r = requests.request(method, url + url_mod, headers=grab_headers(), params=params, json=payload, verify=True)
        if r.status_code == 200:
            return r.json()

        if r.status_code == 202:
            # This response is for some successful posts.
            print("\nSuccess!\n")
        elif r.status_code == 404:
            print('\nCheck your query...I can\'t find what you\'re looking for', r)
        elif r.status_code == 429:
            print("\nToo many requests at a time...\n")
        elif r.status_code == 400:
            print("\nThe object you tried to create already exists\n")
            print("If you are Updating tags via groups it is not supported right now, "
                  "delete your group using the delete command\n")
        elif r.status_code == 403:
            print("\nYou are not authorized! You need to be an admin\n")
        elif r.status_code == 409:
            print("API Returned 409")
        else:
            print("Something went wrong...Don't be trying to hack me now", r)
    except ConnectionError:
        print("Check your connection...You got a connection error")


def find_target_group(tg_name):
    data = request_data("GET", '/target-groups')
    group_id = 0
    for group in data['target_groups']:
        try:
            if group['name'] == tg_name:
                group_id = group['id']
        except KeyError:
            pass
    return group_id


def create_target_group(tg_name, tg_list):

    # Check to see if the Target group exists
    group_id = find_target_group(tg_name)

    # Target group API takes a string of IPs. We will start the string here.
    trgstring = ""

    # turn the list into a string separated by a comma
    for ips in tg_list:
        trgstring = trgstring + str(ips) + ","

    print("These are the IPs that will be added to the target Group:")
    print(tg_list)

    if group_id != 0:
        # Update current Target Group
        payload = {"name": tg_name, "members": str(trgstring), "type": "system"}
        request_data("PUT", '/target-groups/' + str(group_id), payload=payload)
    else:
        # Create a New Target Group
        payload = {"name": tg_name, "members": str(trgstring), "type": "system", "acls": [{"type": "default", "permissions": 64}]}
        request_data("POST", '/target-groups', payload=payload)


def aws_to_tgroup():
    # use set-hasonly if you want to grab aws assets that have not been scanned
    aws_query = {"date_range": "30", "filter.0.filter": "sources", "filter.0.quality": "set-has", "filter.0.value": "AWS"}
    data = request_data('GET', '/workbenches/assets', params=aws_query)
    aws_ips = []

    for assets in data['assets']:
        for source in assets['sources']:
            if source['name'] == 'AWS':
                aws_ip = assets['ipv4']

                # IPy Checks for Public or Private
                for ip in aws_ip:
                    check_ip = IP(ip)

                    check = check_ip.iptype()
                    if check == 'PUBLIC':
                        aws_ips.append(ip)

    create_target_group("AWS Targets", aws_ips)


if __name__ == '__main__':
    aws_to_tgroup()
