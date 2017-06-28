# import requests library
import requests

#import json library
import json

controller='URL'

def getTicket():
    # put the ip address or dns of your apic-em controller in this url
    url = "https://" + controller + "/api/v1/ticket"

    #the username and password to access the APIC-EM Controller
    payload = {"username":"usernae","password":"password"}

    #Content type must be included in the header
    header = {"content-type": "application/json"}

    #Performs a POST on the specified url to get the service ticket
    response= requests.post(url,data=json.dumps(payload), headers=header, verify=False)

    #convert response to json format
    r_json=response.json()

    #parse the json to get the service ticket
    ticket = r_json["response"]["serviceTicket"]

    return ticket


def getNetworkDevices(ticket):
    # URL for network device REST API call to get list of existing devices on the network.
    url = "https://" + controller + "/api/v1/network-device"

    #Content type must be included in the header as well as the ticket
    header = {"content-type": "application/json", "X-Auth-Token":ticket}

    # this statement performs a GET on the specified network-device url
    response = requests.get(url, headers=header, verify=False)

    # json.dumps serializes the json into a string and allows us to
    # print the response in a 'pretty' format with indentation etc.
    print ("Network Devices = ")
    print (json.dumps(response.json(), indent=4, separators=(',', ': ')))

  #convert data to json format.
    r_json=response.json()

  #Iterate through network device data and print the id and series name of each device
    for i in r_json["response"]:
        print(i["id"] + "   " + i["series"])

#call the functions
theTicket=getTicket()
getNetworkDevices(theTicket)

