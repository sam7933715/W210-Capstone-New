from flask import Flask,jsonify,request
import json
import pandas as pd
import numpy as np
import os

# from sklearn.cluster import KMeans
pd.set_option('display.float_format', lambda x: '{:.3f}'.format(x)) #limit floats output to 3
pd.set_option('display.max_columns', None) #display all columns in data frame
pd.set_option('display.max_rows', None)
import seaborn as sns
sns.set_context('talk')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
# %matplotlib inline
# import googlemaps
from datetime import datetime
import math
from k_means_constrained import KMeansConstrained
import pyodbc 

app = Flask(__name__)

#### Connect to database ####
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
# server = 'localhost' 
# database = 'RoutePlanning' 
# username = 'sa' 
# password = 'sfm123' 
# cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
# cursor = cnxn.cursor()

# @app.route('/getStores')
# def getStores():
#     stores = []
#     cursor.execute("SELECT top 100 * FROM [RoutePlanning].[dbo].[StoreMaster]") 
#     row = cursor.fetchone() 
#     while row: 
#         store = dict()
#         store['Storename'] = row[1]
#         stores.append(store)
#         print(row)
#         row = cursor.fetchone()
#     return jsonify(stores)

# @app.route('/insertStores', methods=['POST'])
# def insertStores():
#     storeid_exp = request.values.get('storeid_exp')
#     storename_exp = request.values.get('storename_exp')
#     store_format_exp = request.values.get('store_format_exp')
#     insert_date_exp = request.values.get('insert_date_exp')
#     status_exp = request.values.get('status_exp')

#     cursor.execute("""
#     INSERT INTO [RoutePlanning].[dbo].[StoreMaster] (Storecode, Storename, Store_Format,Createtime,Isdelete) 
#     VALUES ('{storeid_exp}','{storename_exp}','{store_format_exp}','{insert_date_exp}','{status_exp}')""".format(storeid_exp = storeid_exp,storename_exp=storename_exp,store_format_exp=store_format_exp,insert_date_exp=insert_date_exp,status_exp=status_exp)) 
#     cnxn.commit()
#     return "success!"
#### End of Connect to database ####


# Router of a test API
@app.route('/api')
def hello_world():
    data = """ {
       "name":"123",
        "age":20
    } """
    return json.loads(data)

# Router of a test API
@app.route('/test')  # api route
def test():
    print("test")
    return "test"

# Router of a test API

# Router for the main function - store clsutering
# @app.route('/clusters', methods=['POST'])  # api route
@app.route('/clusters', methods=['POST'])  # api route
def clusters():
    # Get the file from front-end submission
    file = request.files['file']
    path = os.path.join(r'C:\IIIfinalproject\final project\file_uploaded', file.filename)
    file.save(path)
    print('Successful upload:',file.filename)
    # rawdatatable = pd.read_excel(path,sheet_name=1)

    # Read the table from local storage
    # path_local = r'.\excel\Store Master.xlsx'
    # rawdatatable = pd.read_excel(path_local,sheet_name=1)
    # rawdatatable.head()
    # rawdatatable = pd.read_csv(r'C:\IIIfinalproject\final project\python\Berkeley_1000.csv',header=None)
    rawdatatable = pd.read_csv(path,header=None)
    rawdatatable.columns = ['Longitude','Latitude','NUMBER','STREET','UNIT','CITY','DISTRICT','REGION','POSTCODE','ID','HASH']


    rawdatatable["ADDRESS"] = rawdatatable["STREET"] + rawdatatable["UNIT"]

    # Number of clusters (Number of working days)
    Target_Num_Cluster = 22
    avg_sites = round(rawdatatable.shape[0]/22,0)
    print('Expected number of clusters:',Target_Num_Cluster)
    X_features = rawdatatable[['Longitude','Latitude']]

    # Size constraint K-means
    clf = KMeansConstrained(
    n_clusters=Target_Num_Cluster,
    size_min=avg_sites-3,
    size_max=avg_sites+3,
    random_state=0
    )
    clf.fit_predict(X_features)


    # Get the labels of each store
    Label_frame = pd.DataFrame(clf.labels_)
    # Get the number of store which allocate to certain clusters
    for i in range(Target_Num_Cluster):
        print('Cluster',i,":",clf.labels_[clf.labels_==i].shape[0],'stores')

    Storeinfo = rawdatatable[['NUMBER','POSTCODE','ADDRESS']]
    clustering_X_features = pd.concat([Storeinfo,X_features,Label_frame], axis=1)
    clustering_X_features = clustering_X_features.rename(columns={0 : 'Clusters'})
    clustering_X_features.head()

    dataset=[]
    for i in range(Target_Num_Cluster):
        dataset.append({
        'Clusters':i,
        'datas':[]
        })
        clusters = clustering_X_features[clustering_X_features['Clusters']==i]
        cluster_len = len(clusters)

        for j in range(cluster_len):
            LatLngObj = {'lat':clusters.iloc[j,:][4],'lng':clusters.iloc[j,:][3]}
            dataset[i]['datas'].append({
                'NUMBER':str(clusters.iloc[j,:][0]),
                'POSTCODE':str(clusters.iloc[j,:][1]),
                'ADDRESS':str(clusters.iloc[j,:][2]),
                'Longitude':str(clusters.iloc[j,:][3]),
                'Latitude':str(clusters.iloc[j,:][4]),
                'LatLng':str(LatLngObj)
            })

    print('Clustering Success')
    return jsonify(dataset)


if __name__ == '__main__':
    app.run()