
import importlib
import os
import sys
import math
import copy
import urllib
import zipfile
import requests
import shutil
import re
from collections import OrderedDict
import warnings

from azureml.core import Run
from azureml.core import Workspace, Datastore
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.datastore import Datastore
from azureml.data.data_reference import DataReference

pip_packages=[
              "azureml-sdk==1.0.17", "scikit-learn==0.21.3",
              "download==0.3.4", "pandas==0.25.1",
              "spacy==2.1.4", "numpy==1.17.2"
              ]

for item in pip_packages:
  try:
    importlib.import_module(item.split("=")[0])
  except:
    _command="pip install --upgrade "+item
    os.system(_command)

from sklearn.utils.class_weight import compute_class_weight
import spacy
from download import download
import numpy as np
import pandas as pd


cwd = str(os.getcwd())
sys.path.append(cwd)
sys.path.insert(0, cwd)

def download_files(files,download_folder):
    for file in files:
        [[_,location]]=file.items()
        file_name=os.path.basename(location)
        exists,_=check_file(file_name,download_folder)
        if(exists):
            pass
        else:
            print('*** Downloading : ',file_name)
            try:
                r = requests.get(location, auth=('usrname', 'password'), verify=False,stream=True)
                r.raw.decode_content = True   
                with open(os.path.join(download_folder,file_name), 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
            except:
                raise Exception('Failed')
                
def check_file(filename,location=cwd):    
    
    return os.path.exists(os.path.join(location,filename)),os.path.join(location,filename)

def check_folder(foldername,location=cwd):    
    
    return os.path.exists(os.path.join(location,foldername))


def create_folders(folders):
    for folder in folders:
        if(check_folder(folder)):
            pass
        else:
            os.mkdir(folder)
            
def get_args():

  parser = argparse.ArgumentParser()
  parser.add_argument("--processed_data_ref",  type=str, dest="processed_data_ref")
  parser.add_argument("--input_data_ref",  type=str, dest="input_data_ref")
  parser.add_argument("--tenant_id",  type=str, dest="tenant_id")
  parser.add_argument("--application_id",  type=str, dest="application_id")
  parser.add_argument("--app_secret",  type=str, dest="app_secret")
  parser.add_argument("--subscription_id",  type=str, dest="subscription_id")
  parser.add_argument("--resource_group",  type=str, dest="resource_group")
  parser.add_argument("--workspace_name",  type=str, dest="workspace_name")
  parser.add_argument("--workspace_region",  type=str, dest="workspace_region")
  parser.add_argument("--object_id",  type=str, dest="object_id") 
  args = parser.parse_args()

  return(args)

def get_ws(args):
  
  tenant_id = args.tenant_id
  application_id = args.application_id
  app_secret = args.app_secret
  subscription_id = args.subscription_id
  resource_group = args.resource_group
  workspace_name = args.workspace_name
  workspace_region = args.workspace_region
  object_id = args.object_id
  
  service_principal = ServicePrincipalAuthentication(
          tenant_id=tenant_id,
          service_principal_id=application_id,
          service_principal_password=app_secret)

  ws = Workspace.get(
              name=workspace_name,
              subscription_id=subscription_id,
              resource_group=resource_group,
              auth=service_principal)
  return(ws)
    

if __name__ == '__main__':
    global run
    run = Run.get_context()
    _params=get_args()
    ws=get_ws(_params)
    
    processed_data_ref=_params.processed_data_ref
    input_data_ref=_params.input_data_ref
    
    def_blob_store = Datastore(ws, 'workspaceblobstore')
    blob_container_name=def_blob_store.container_name
    
    
    word_vectors={"en_vectors_web_lg":"https://github.com/explosion/spacy-models/releases/download/en_vectors_web_lg-2.1.0/en_vectors_web_lg-2.1.0.tar.gz"}
    toDownload=[word_vectors]
    download_files(toDownload,cwd)
    
    try:
        nlp = spacy.load("en_vectors_web_lg")
    except:
        os.system("pip install "+"{}\en_vectors_web_lg.tar.gz".format(os.getcwd()))
        nlp = spacy.load("en_vectors_web_lg")    
    


#     df=pd.read_csv('{}/original/train.csv'.format(input_data_ref))
#     print(df.head(10))
