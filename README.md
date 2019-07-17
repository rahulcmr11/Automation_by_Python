# 1 Automation_by_Python
# To use download from box python code 
Do below
1. In box_config.yml pass your Akana Client Id or secret key which is provided to your company.
2. In case there is use of Akana Client ID and secret key please remove them or commet the code(Download_Upload_Files_From Box.py) from line 14 to line 18
** and you are good to Go

###### 2 If you want to run the N no. of SQL functions or queries in your Database use (Automated_fun_sps.py and conn_param.yml)
1. In conn_param.yml just the change the patrameters . This code supports postgresql and Greenplum DB.
  a. Make sure psycopg2 "a python module is installed". to support Postgresql and GP DB 
2. For any other DB just install and import the required DB module and change from postgresql to another DB. 
** and this will run without manually running each queries.

## 3 if you want to make small dictionary of words 

1. use Small_data_Dictionary.py and dictionary used here is data.json
2. Search in any format any word if it has it well tell you answer.

** good in case you want to learn python


## 4. if you want to run the analysis on atable and figure out the actual error and false error ;

Use the pwr_audit_ds.ipynb in jupyter notebbok.

** Good for Data Visulaization examples

## 5. Do some Webscrapping using Python on magic brick.com.
use web_scrapping_python.ipynb in jupyter notebook

** Good for developers learning webscrapping

## 6. If you want to terminate AWS Sagemaker Running instances automatically at scheduled time use this as a lambda function.
boto3 is used to implement AWS from python
use sm_jupyter_terminate.py.
Make a zip file with all supporting lib of python and sm_jupyter_terminate.py and upload it in s3 bucket.
Point the lambda function to run from that bucket

## 7. To work and practice NLP use this NLP Project .ipynb
Run it in jupyter notebook
yelp.csv contains messages 
and this program predicts out the Spam message or a Ham message basedon NLP algo

