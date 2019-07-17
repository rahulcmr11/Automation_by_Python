import boto3
import botocore
import paramiko
import json
import pandas as pd
from pandas.io.json import json_normalize
#from pandas.io.json import json_normalize

#pem file for login pem file available in my local
pem_file = 'C:/Users/212586594/Desktop/sage_maker/ge-dna-innovation-key.pem/ge-dna-innovation-key.pem'

# turn the .pem file to a ssh key
key = paramiko.RSAKey.from_private_key_file(pem_file)
print(key)

# Create client from SH keys
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect ssh to an EC2
#try:
#def jnb():
client.connect(hostname='10.232.159.236', username="ec2-user", pkey=key)
client.connect(hostname='10.232.158.27', username="ec2-user", pkey=key)

cmd = 'aws sagemaker list-notebook-instances'

stdin, stdout, stderr = client.exec_command(cmd) ## get list of all notebooks
x = stdout.read()
#print(type(x))
client.close()

#jnb()
#print(x)
#d = json.load(x)
my_json = x.decode('utf8')
d = json.loads(my_json)
f_normal = json_normalize(d['NotebookInstances'])
#f_normal.head(3)
#df = pd.read_json("C:/Users/212586594/Desktop/sage_maker/py_scripts/xyz.json")
inservice = f_normal[f_normal['NotebookInstanceStatus']=='InService']

######### taking the samll part of dataframe with only 'NotebookInstanceName','NotebookInstanceStatus'

inservice = inservice[['NotebookInstanceName','NotebookInstanceStatus']]


#inservice['NotebookInstanceStatus']
print("\n Below Jupyter NB instances will be killed as they found running after usual working hrs \n")
print("************************************\n")
for nb in inservice['NotebookInstanceName']:
    terminate_cmd = "aws sagemaker stop-notebook-instance --notebook-instance-name "+nb
    #stdin, stdout, stderr = client.exec_command(terminate_cmd) # executing kill command
    #print(stdout.read())
    print(terminate_cmd)
print("\n************************************\n")
client.close()
#terminate_cmd = "aws sagemaker stop-notebook-instance --notebook-instance-name "+
