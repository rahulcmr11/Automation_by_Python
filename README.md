# Automation_by_Python
##### To use download from box python code 
Do below
1. In box_config.yml pass your Akana Client Id or secret key which is provided to your company.
2. In case there is use of Akana Client ID and secret key please remove them or commet the code(Download_Upload_Files_From Box.py) from line 14 to line 18
## and you are good to Go

###### If you want to run the N no. of SQL functions or queries in your Database use (Automated_fun_sps.py and conn_param.yml)
1. In conn_param.yml just the change the patrameters . This code supports postgresql and Greenplum DB.
  a. Make sure psycopg2 "a python module is installed". to support Postgresql and GP DB 
2. For any other DB just install and import the required DB module and change from postgresql to another DB. 
## and this will run without manually running each queries.
