import os
import yaml
import requests
import json
import ssl
#from docker import client
#import client
#import urllib2
with open("box_config.yml","r") as box_config:
    param=yaml.load(box_config)
#set http_proxy = config['proxy1']
#set https_proxy = config['proxy2']
config =   param['object']
akana_url_1 = config['akana_url_1']
client_id = config['client_id']
akana_url_2 = config['akana_url_2']
client_secret = config['client_secret']
akana_url_3 = config['akana_url_3']
box_token_url_1 =  config['box_token_url_1']
sso_email_id = config['sso_email_id']
proxy1 = config['proxy1']
proxy2 = config['proxy2']
box_url_1 = config['box_url_1']
box_url_2 = config['box_url_2']
folder_id = config['folder_id']
box_token_url = box_token_url_1 + sso_email_id
upload_url = config['upload_url']
print(box_token_url)
#os.environ['http_proxy'] = config['proxy1']
#os.environ['https_proxy'] = config['proxy2']
print(proxy1+"*****"+proxy2)
#set https_proxy = config['proxy2']

akana_url= akana_url_1+client_id+akana_url_2+client_secret+akana_url_3
print(akana_url)
response= requests.post(akana_url,verify = False)# doing a post request to API call
akana_url_content=response.content
#json_response = json.loads(response.decode('utf-8'))
#print(akana_url_content)
json_response = response.json()
akana_token = json_response['access_token']
print(akana_token)
print(box_token_url)
box_url = box_url_1+folder_id+box_url_2
print(box_url)
box_token_headers = {"Authorization":"Bearer "+akana_token}
try:

    box_token_response = requests.get(box_token_url,headers = box_token_headers,verify = False)# verify = False is used to ignore the
                                                                                        #SSL cert verification
except requests.exceptions.SSLError as SSL_ERROR:
    print("********************************************************************************************\n")
    print("SSL certificates required else add verify=False to Api calls \n")
    print("********************************************************************************************\n")
    exit()
box_token_json_response = box_token_response.json()
print("box_token_json_response************* ",box_token_json_response)
box_token = box_token_json_response['accessToken']
print("box_token  "+box_token)
box_url_headers = {"Authorization":"Bearer "+box_token}
box_response = requests.get(box_url,headers = box_url_headers,verify=False)
print(box_response.json())
#folder_id = '39832155676'
#upload_url = client.folder(folder_id).upload('C:/Users/212586594/Desktop/learn_python/box_config.zip')
#print("upload done")

#print(json_response)


#akana_data=akana_url_content.json()
#print("akana_data"+akana_data)
#for key, value in akana_url_content:
#print (key, values)
