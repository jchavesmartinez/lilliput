import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import json
import pandas as pd
import re
import pydeck as pdk
import numpy as np
from streamlit_dynamic_filters import DynamicFilters
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
import numpy as np
import locale
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image
import time


#st.cache_data.clear()
st.set_page_config(
  page_title="Lilliput Inventory Management",
  page_icon="🔬",
  layout="wide",
)

#---------------------------- Variables generales --------------------------------


credentials = {
    "type": "service_account",
    "project_id": "devstackerp",
    "private_key_id": "3a7d1511ed3d81296b76f192794449c8145de068",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDp5iCeNNQl7WO3\nHwBSsnBazysuke/CjA9V5Pu+V9j0+PetgQgJbbHHkGzvC1W2vkXaZDD/veTn69Fq\n7VL2snWmna2OUg+j03j/zZtI2m8AHJNUoUvGKXAaYcUO1wrinGCPRrpcioNl8ZvO\nnJcfWuO/siPO0iT7L7xgYtAqd2RSHYGzY/9Q/2BdA2XtrPEu2VT79fVocJDwKZ9W\nnU9slh2aE7CDKDjn2ljiQXSrx6NkZyEdEdm/oaEd+2zvacx/zTpFpSzKCavj4h+y\n/iSgVZ0YKkc4QgUhWIQFUfq3/4Sk81K2CCjHSXSz0H4lh7qsO6yqoe1LU/IqwfJH\nabcVScFfAgMBAAECggEAVIqhb42YwLy1NhM2gq2MfsYyzXpiNud5A4rokzwdZy42\nF7hztzS29XL2bNCkApFzniRosYdpnYpW/1cYjaKjc726ZZ6zmHtvWMZwQjzxshCi\nEAzc3ptLsb11BJAllxL+s8rUwW4vYEGcF2nyFZs8hqVU3ASI6WGvrQcKRs8wq5zd\num2nnQuvVYVfCtGcp5qlcrDBgJV5EBy8H13mmAZSQo88UtK39KLc2qih2HFAmZnM\nJCjZj6EiJ57G4HuL1EF1pr6fIPzVgsYl6LFZ3MCr5qxrVYi8UxozdLVhka2jLLY1\nZSz+IOa4gm66nlYjdJoypmRFCXJrS4xVaTdah0DOQQKBgQD6sjAUFxNA1Fe0AdIc\nQdQnW9jcynLaXYSMqWZ/D7WsNnE7AVTnPuPuM/tY4jrxA4YNOUwVhJJxfRCgtWWt\nUwpBn0iFrh3oOWcLAi1fxoxj76b+mtzjuVEBSBmBvsIvnQJOpTWNfPp2OsnZwwz4\n3oGBeQ1bhCcTZK2rUE7tc7QAkwKBgQDu2PavXl8mhhzReeWlA/BftoaHWr0GfEaz\nyeVkqNHOlKPEl+Hmdb/YmEEhvcIHmC+a9UT4RdZdRRboPy1m2Z53OJn5VYuNuIil\nsStZO15xBEik1/gWeKUjTVX5HQqdoTccJpWINLpx95uNrZpLafsbMVUowdIgEipm\nYC9pEs7XhQKBgFtewmMwHdZNDkIPP9MIsxg9Q4cFSmMIHp1dyHua8C36Eb7dt2Io\n684PqBY3LiBVlnAPaAmXrgArAvpv4sUPNPfB5B7E3SWcdk/u1TbJGLX7zLOTIdrl\n2f5LlvBQ5FmSMhsT37bXzDl3J8Z0bq/t+OmFgzbNrahF035S4NFukDZ9AoGAQYNR\nZpjEEJUIooyE6NZDwH0YOVgyMO01l2rxeMK1iaxLn0jptYTmskpQ0yhxaBPeOuq7\nmD3PppWkyt9JXMSkKp9j3HgSZzUOhiQqd7dJGEbMhiqW6dL9uMklo8bLeqEVtKsA\nqPONkGUSTbIoeDcBoVvOt/cx44oYByyq1G9MPOECgYAPzv5Q93oiMAJlWVuzv1RV\nw9HpOD6pv5ryPMMd/q+qrWfJDz5wYoU4ccTRh0CzgERNKRPCy7zNMqCHRp0xTqBU\nyGMjJY6w1fvZYoqXVa2TVB3gXnb64v3guG2N8wHpK9qeAciN4G/IrCy5a9IQv45o\nSF/AbO/1i7rBpBtwfDuhZQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "itdevstack@devstackerp.iam.gserviceaccount.com",
    "client_id": "100362920078189694738",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/itdevstack%40devstackerp.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}


#---------------------------- Funciones generales --------------------------------

def read_file_googledrive(credentials,file_id):

    try:
        credentials_pdf = service_account.Credentials.from_service_account_info(credentials, scopes=['https://www.googleapis.com/auth/drive'])

        # Build the Drive service
        drive_service = build('drive', 'v3', credentials=credentials_pdf)

        # Request the file content
        file_content = drive_service.files().get_media(fileId=file_id).execute()

        # Convert bytes content to string
        text_content = file_content.decode('utf-8')  # Assuming UTF-8 encoding
        text_content = json.loads(file_content)
         
    except Exception as e:
        print(f"Error: {str(e)}")
        print("No fue posible leer el file")
        st.write(f"Error: {str(e)}")
        text_content=[]
    
    return text_content

def generate_barcode(number):
    # Ensure the number is a 12-digit string
    number = str(number).zfill(12)
    barcode = EAN13(number, writer=ImageWriter())
    barcode.save("barcode")
    return "barcode.png" , barcode

@st.experimental_dialog("New experiment")
def vote(barcode_image, barcode):

    with st.form("my_form"):
        st.image(image, caption='Generated Barcode')
        
        variables = read_file_googledrive(credentials,'1k-Gnh-xUFUXej14D6ABMhGeGe8dXGxyT')

        responses = {}

        # Iterate over variables and create a text input for each
        for i in variables:
            responses[i["variable_name"]] = st.text_input(i["variable_name"],0 , key=i["variable_name"])

    if st.button("Submit"):
        responses['Barcode']=barcode
        st.write(responses)
        st.success('This is a success message!', icon="✅")
        

#---------------------------- Codigo general --------------------------------

st.title("Lilliput Inventory Management")

description="""

### Overview
The Inventory Module streamlines tracking and managing experiments in our chemical lab. Each experiment is tagged with a unique barcode containing key information about its conditions and parameters.

### Key Features

1. **Barcode Generation:**
   - Automatically generate and assign unique barcodes to experiments.

2. **Experiment Tracking:**
   - Scan barcodes to access detailed experiment info and key parameters.

3. **Data Management:**
   - Securely store all experiment data in a centralized database.
   - Maintain a historical record for reference.

4. **User-Friendly Interface:**
   - Easy navigation with quick search and filter options.

5. **Lab Equipment Integration:**
   - Automatically record and tag experiments with barcodes.
   - Real-time data capture and updates.

6. **Reporting and Analysis:**
   - Generate reports and analyze experiment trends and patterns.

### Benefits

- **Accuracy:** Reduces manual errors and ensures precise data tracking.
- **Efficiency:** Streamlines documentation and retrieval processes.
- **Organization:** Centralized storage improves lab management.
- **Insights:** Supports data analysis for research advancements.

"""

st.markdown(description)


st.markdown("---")


#if "vote" not in st.session_state:
if st.button("Insert a new value", use_container_width=True):
    timestamp = int(time.time())
    timestamp_str = str(timestamp).zfill(12)  # Pad the timestamp to ensure it's 12 digits
    barcode_path, barcode = generate_barcode(timestamp_str)
    barcode = str(barcode).split("'")[0]
    image = Image.open(barcode_path)

    vote(image, barcode)

    



