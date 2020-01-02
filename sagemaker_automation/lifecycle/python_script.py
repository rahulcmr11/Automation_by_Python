#!/usr/bin python
from __future__ import print_function
import re
import yaml
import fileinput
from shutil import copyfile
import time
import warnings
import os
import logging
import boto3
import botocore
import json
import pandas as pd
from pandas.io.json import json_normalize
import subprocess
import smtplib

warnings.filterwarnings(action='ignore',module='.*paramiko.*')
sts_default_provider_chain = boto3.client('sts')
print('Default Provider Identity: : ' + sts_default_provider_chain.get_caller_identity()['Arn'])
role_to_assume_arn='arn:aws:iam::753920291680:role/bu-ge-pwr-sagemaker-automation'
role_session_name='sagemaker-access'
response=sts_default_provider_chain.assume_role(RoleArn=role_to_assume_arn,RoleSessionName=role_session_name)
creds=response['Credentials']
a_role = boto3.client('sts',aws_access_key_id=creds['AccessKeyId'],aws_secret_access_key=creds['SecretAccessKey'],aws_session_token=creds['SessionToken'],)
accesskey_id = creds['AccessKeyId']
secret_access_key = creds['SecretAccessKey']
session_token = creds['SessionToken']
print('AssumedRole Identity: ' + a_role.get_caller_identity()['Arn'])

######### AUTHOR of Program :: RAHUL RANJAN 212586594 ################

with open('/tmp/first_json.json') as first:
        initial = json.load(first)
NotebookInstanceType = initial['instance_type']
cftstackname1 = initial['project_name']
cftstackname2 = re.sub('[^a-zA-Z0-9 \n\.]', '', cftstackname1)
cftstackname = cftstackname2.replace(" ","-").lower()+"-stk"
nbinstancename = "ml-"+cftstackname2.replace(" ","-").lower()+"-nbk"
NotebookInstanceName = initial['project_name']
#emailsender = '212586594@ge.com'
emailreceivers = initial['data_scientist_email']+","+initial['requestor_email']
mlrolename = "bu-ge-mlusr-"+nbinstancename.replace("-nbk","")

with open('/tmp/sm_nb_auto_instance_config.json', 'r') as file:
        json_initial = json.load(file)
for item in json_initial:
        if item['ParameterKey'] in ["NotebookInstanceType"]:
                item['ParameterValue'] = NotebookInstanceType

        if item['ParameterKey'] in ["cftstackname"]:
                item['ParameterValue'] = cftstackname

        if item['ParameterKey'] in ["NotebookInstanceName"]:
                item['ParameterValue'] = nbinstancename

        if item['ParameterKey'] in ["emailreceivers"]:
                item['ParameterValue'] = emailreceivers
                
        if item['ParameterKey'] in ["mlrolename"]:
                item['ParameterValue'] = mlrolename                

with open('/tmp/sm_nb_auto_instance_config.json', 'w') as file:
        json.dump(json_initial, file, indent=5)

with open('/tmp/sm_nb_auto_instance_config.json') as f:
        data = json.load(f)
        #print (data)
df1 = pd.DataFrame(data)
#print(df1.head())
df1['ParameterKey']=='NotebookInstanceName'#['ParameterValue']
#### notebook names which has to be assigned comes here####

client = boto3.client('sagemaker',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
response = client.list_notebook_instances()
#print("hello ok")
notebook = []
#print(response)
for k1 in response['NotebookInstances']:
        k2 = k1['NotebookInstanceName']
        notebook.append(k2)
print(notebook)
nb_name=df1.loc[df1['ParameterKey']=='NotebookInstanceName']['ParameterValue'].values[0]
#print("***************************************************",nb_name)

stack_name = df1.loc[df1['ParameterKey']=='cftstackname']['ParameterValue'].values[0]
bucket_name = "ml-"+cftstackname2.replace(" ","-").lower()+"-dev"

if nb_name in notebook:
        print("The notebook already exist, Please request for access in one IDM for:- ",nb_name)

                ############ SEND EMAIL TO GET IDM ACCESS ##############
        print("***********************"+bucket_name)
        SUBJECT = "The notebook already exist, Please request for access in one IDM for:-  "+nb_name
        TEXT1 = "Hi,\n\nThe notebook already exist, Please request for access in one IDM for:-  "+nb_name+"\n"
        TEXT2 = "\nPlease don't reply on top of this email\n"
        TEXT3 = "\nFor more info please reach out to Platform ops team.\n\n"
        TEXT4 = "\n Thanks,\n"
        TEXT = TEXT1 + TEXT2 + TEXT3 + TEXT4
                #message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        try:
                def send_email(to='', subject='', body=''):
                        if not subject:
                                raise NoSubjectError
                        if not to:
                                raise NoRecipientError
                                                #
                        if not body:
                                cmd = """mailx -s "{s}" < /dev/null "{to}" 2>/dev/null""".format(s=subject, to=to)
                        else:
                                cmd = """echo "{b}" | mailx -s "{s}" "{to}" 2>/dev/null""".format(b=body, s=subject, to=to)

                                os.system(cmd)

                send_email(to=emailreceivers,subject=SUBJECT,body=TEXT)
        except Exception:
                print ("Error: unable to send email")
else:
        print("The notebook dont exist, now creating:- "+nb_name)
        print("*************noteook_instance************\n"+nb_name)
        lc_name='lc-'+nb_name
        On_Create="[{'Content': 'IyEvYmluL2Jhc2g='},]"
        On_Start="[{'Content': 'IyEvYmluL2Jhc2g='},]"
        response = client.create_notebook_instance_lifecycle_config(NotebookInstanceLifecycleConfigName=lc_name,OnCreate=[{'Content': 'IyEvYmluL2Jhc2g='},],OnStart=[{ 'Content': 'IyEvYmluL2Jhc2g='},])
        #print(response)
        client = boto3.client('cloudformation',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
        stack_name = 'bu-ge-mlusr-'+cftstackname
        template_yaml = '/tmp/sagemaker-launch-notebook.yaml'
        #print(template_yaml)
        with open('/tmp/sm_nb_auto_instance_config.json') as f:
                Parameters_json = json.load(f)
        #print(Parameters_json)        
        with open('/tmp/sagemaker-launch-notebook.yaml') as cft:
                cft_file = cft.read()
        response = client.create_stack(StackName=stack_name,TemplateBody=cft_file,Parameters=Parameters_json,Capabilities=['CAPABILITY_NAMED_IAM'],DisableRollback=True)
        s3 = boto3.client('s3',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
        ### Create bucket
        s3.create_bucket(Bucket=bucket_name)
        response = s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
            )
        time.sleep(15)
    # Create the bucket policy
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                    "Sid": "ReadWriteAccess",
                    "Effect": "Allow",
                    "Action": ["s3:PutObject","s3:GetObject"],
                    "Resource": "arn:aws:s3:::%s/*" % bucket_name,
                    "Principal" : {
                            "AWS" :  "arn:aws:iam::820348651115:role/bu-ge-cldmlusr-per-fed"

                            }
            }]
                }

        bucket_policy = json.dumps(bucket_policy)
        s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

        ########### In the role created create and attach sagemaker and s3 policy ###################

        ############## first change template ###########################
        file1 = fileinput.FileInput(files=("/tmp/sagemaker_nb_policy_template.json"), inplace=True, backup='.bak')
        for line in file1:
                print(line.replace("<<nb_name>>", nb_name.replace("-nbk","")), end='')
        file1.close()
        file2 = fileinput.FileInput(files=("/tmp/s3_nb_policy_template.json"), inplace=True, backup='.bak')
        for line in file2:
                print(line.replace("<<bucket_name>>", bucket_name), end='')
        file2.close()
                ############ CREate Policy sage maker ###########################

        with open("/tmp/sagemaker_nb_policy_template.json") as smp:
                sm_policy = json.load(smp)
        iam = boto3.client('iam',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
        roles = iam.list_roles()
        #print(roles)
        for i in range(0,len(roles['Roles'][0]['Arn'])):
                if mlrolename in roles['Roles'][i]['Arn']:
                        Arn = roles['Roles'][i]['Arn']
                        RoleName = roles['Roles'][i]['RoleName']
                        print(RoleName)
                else :
                        print("No Role defined")

# Create a sagemaker policy
        sm_policy_name = 'GEPwrMLSageMakerCustomAccess-'+nb_name.replace("-nbk","")
        response = iam.create_policy(PolicyName=sm_policy_name,PolicyDocument=json.dumps(sm_policy))
        #print(response)

                ############ CREate Policy s3 ############################
        with open("/tmp/s3_nb_policy_template.json") as bucket:
                bucket_policy = json.load(bucket)

        s3_policy_name = 'GEPwrMLS3CustomAccess-'+bucket_name.replace("-s3","")
        response = iam.create_policy(PolicyName=s3_policy_name,PolicyDocument=json.dumps(bucket_policy))
        #print(response)

        #### get Policy name ########

        response_sm = iam.get_policy(PolicyArn='arn:aws:iam::753920291680:policy/'+sm_policy_name)
        sagemaker_policy = response_sm['Policy']['PolicyName']
        response_s3 = iam.get_policy(PolicyArn='arn:aws:iam::753920291680:policy/'+s3_policy_name)
        s3_policy = response_s3['Policy']['PolicyName']


        ### Add tags##
        s3 = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
        bucket_tagging = s3.BucketTagging(bucket_name)
        response = bucket_tagging.put(Tagging={'TagSet': [{'Key': 'ge-sagemaker-power-dev','Value': 'UAI3030911'},]})
        client = boto3.client('sagemaker',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)

        ## change file name and this will be loaded to git###
        copyfile('/tmp/sm_nb_auto_instance_config.json', '/tmp/sagemaker_used_filename/'+nb_name.replace("-nbk","")+'-sm_nb_auto_instance_config.json')

        
        #print("Programs end")

#### Attach policy
        #time.sleep(4)

        iam = boto3.client('iam',region_name='us-east-1',aws_access_key_id=accesskey_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
        iam.attach_role_policy(PolicyArn='arn:aws:iam::753920291680:policy/'+sagemaker_policy,RoleName=RoleName)
        iam.attach_role_policy(PolicyArn='arn:aws:iam::753920291680:policy/'+s3_policy,RoleName=RoleName)

        response = iam.tag_role(RoleName=RoleName,Tags=[{'Key': 'ge-sagemaker-power-dev','Value': 'UAI3030911'},])
        #### create and send email ####
        sender = df1.loc[df1['ParameterKey']=='emailsender']['ParameterValue'].values[0]
        receivers = df1.loc[df1['ParameterKey']=='emailreceivers']['ParameterValue'].values[0]
        SUBJECT = "The notebook don't exist, So a new Notebook is created:-  "+nb_name

        TEXT1 = "Hi,\n\nThe notebook don't exist, So a new Notebook is created:-  "+nb_name+"\n"
        TEXT2 = "\nPlease don't reply on top of this email\n"
        TEXT3 = "In case of issue please reach out to Platform ops team.\n\n"
        TEXT4 = "\n Thanks,\n"
        TEXT = TEXT1 + TEXT2 + TEXT3 + TEXT4
                #message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        try:
                def send_email(to='', subject='', body=''):
                        if not subject:
                                raise NoSubjectError
                        if not to:
                                raise NoRecipientError
                                        #
                        if not body:
                                cmd = """mailx -s "{s}" < /dev/null "{to}" 2>/dev/null""".format(s=subject, to=to)
                        else:
                                cmd = """echo "{b}" | mailx -s "{s}" "{to}" 2>/dev/null""".format(b=body, s=subject, to=to)

                                os.system(cmd)

                send_email(to=emailreceivers,subject=SUBJECT,body=TEXT)
        except Exception:
                print ("Error: unable to send email")
print("Programs end")
