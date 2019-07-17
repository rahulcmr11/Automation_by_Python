import yaml
import psycopg2
import os
import pandas
import sys
import getpass
conn = None
password=getpass.getpass("Enter_connection password : ")
print("Author of program : Rahul Ranjan")
#print("This is the my first python program")
with open("conn_param.yml",'r') as conn_param:
    conn=yaml.load(conn_param)
config = conn['object']
#print(config)
query_dir_path = config['query_dir_path']
if os.path.exists("success_runs.txt"):
    os.remove("success_runs.txt")
elif os.path.exists("failures_run.txt"):
        os.remove("failures_run.txt")
else:
    print("The success_runs.txt and failures_run.txt file does not exist will create it ")
#print(query_dir_path)
#print(type(query_dir_path))
#print(os.listdir(query_dir_path))
#sqls=os.listdir(query_dir_path) #if os.path.isfile() ## take only files in directory
#print(os.walk(query_dir_path))
sqls = os.listdir(query_dir_path)
print(sqls)
host=config['hostname']
#print(host)
username=config['username']
port=config['port']
dbname=config['dbname']
#password=sys.argv[1]

steps_order_files = config['steps_order_files']
queries_to_run_in_order  = config['queries_to_run_in_order']
ex_query=' '

def run_query():
    global connect_db
    try:
        connect_db=psycopg2.connect("dbname = "+dbname+" user = "+username+" password = "+password+" host = "+host+" port="+port)
        #print("hellooooo")

    except:
            print ("Check the connection parameters in the conn_param.yml file , DB not connected")
            exit()
    if queries_to_run_in_order == "Y":

        df=pandas.read_csv(steps_order_files+"steps_of_script.csv")
        df_list_order=list(df["order"])
        sort_order_list = sorted(df_list_order)
        print(sort_order_list)
        df1=df.sort_values(["order"])
    #df1
        df_order = list(df1["script_name"])
        print(df_order)
        for sql in df_order:
            print(sql)

    #for sql in scn:
            print(type(sql))
            print(query_dir_path+sql)
            with open(query_dir_path+sql,"r") as run_sql:
            #print(query_dir_path+scn)


                sql_r=run_sql.read()
                print(sql_r)###printing dir
                cur=connect_db.cursor()

                try:
                    cur.execute(sql_r)
                    with open("success_runs.txt","a") as sql_res:
                #print("#########################bqjkwfbjqfbjf")
                        #sql_res.write("The queries which ran successfully are: \n" )
                            sql_res.write(sql+"\n")
                #sql_res.write("Hello \n")


                except psycopg2.ProgrammingError as e:
                    print(e)
                    with open("failures_run.txt","a") as sql_err: # append is used to open and keep appending lines, write will overwrite
                                            #sql_err.write("The queries which failed to run are: \n")
                                            sql_err.write(sql+"\n")
                                            connect_db.rollback()# Whenever the first query has failed then we need to do roll back and then
                                            #proceed to the next query else this will throw error
    elif queries_to_run_in_order == "N":
        print("Selected no orders required , so program will run queries randomly:\n")
        for sql in sqls:
                print(sql)
                #print(type(sqls))
                with open(query_dir_path+sql,"r") as run_sql:
                    print(query_dir_path+sql)


                    sql_r=run_sql.read()
                    print(sql_r)###printing dir
                    cur=connect_db.cursor()

                    try:
                        cur.execute(sql_r)
                        with open("success_runs.txt","a") as sql_res:
                    #print("#########################bqjkwfbjqfbjf")
                            #sql_res.write("The queries which ran successfully are: \n" )
                            sql_res.write(sql+"\n")
                    #sql_res.write("Hello \n")


                    except psycopg2.ProgrammingError as e:
                        print(e)
                        with open("failures_run.txt","a") as sql_err: # append is used to open and keep appending lines, write will overwrite
                                                #sql_err.write("The queries which failed to run are: \n")
                            sql_err.write(sql+"\n")
                            connect_db.rollback()# Whenever the first query has failed then we need to do roll back and then
                                                
        connect_db.commit()
        connect_db.close()
    else:
        print("Please select Y or N in  the run queries_to_run_in_order param in conn_param.yml")
run_query()
