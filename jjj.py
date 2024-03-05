import streamlit as st
import openapi
from bs4 import BeautifulSoup
import requests
from database import removeDbFile,setupTables, insertData, updateData, deleteData, queryByField, queryToDataframe, queryJoin


id = '1'
ps = '1'
no = 1
assistant_id = ''
thread_id = ''
if openapi.login(id, ps):
    apikey_id = openapi.load_api_key()
    client = openapi.client_connect(apikey_id)
    assistant_id,thread_id = openapi.isrelations(no,apikey_id,no)
    print(assistant_id,thread_id,apikey_id)



# for i in openapi.assistant_list(client):
#     print(i.id,i.description,i.model,i.instructions)
# openapi.assistants_delete(client)
