import streamlit as st
import cv2
import pytesseract
from PIL import Image
from streamlit_option_menu import option_menu
import os 
import numpy as np
import easyocr
import re
import pandas as pd
import mysql.connector
def save_uploaded_image(uploaded_image):
    # Save the uploaded image temporarily
    image_path = os.path.join("uploaded_cards", uploaded_image.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_image.getbuffer())
    return image_path


def image_to_text(uploaded_image):
    # Save the uploaded image temporarily
    image_path = save_uploaded_image(uploaded_image)

    # Read the saved image using OpenCV
    image = cv2.imread(image_path)

    # Use EasyOCR to extract text from the image
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image, detail=0, paragraph=False)

    return text

def img_to_binary(file):
    # Convert image data to binary format
    with open(file, 'rb') as f:
        binaryData = f.read()
    return binaryData

saved_img = os.getcwd()+ "\\" + "uploaded_cards"
data = {
                "card_holder_name" : [],
                "designation" : [],
                "website" : [],
                "email" : [],
                "mobile_number" :[],
                "company_name" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : [],
                #"image" : img_to_binary(saved_img)
}
def get_data(text):
    for ind, i in enumerate(text):
        if ind==0:
            data['card_holder_name'].append(i)
        elif ind==1:
            data['designation'].append(i)
        elif "www " in i.lower() or "www." in i.lower():
            data["website"].append(i)
        elif "WWW" in i:
            data["website"] = text[4] +"." + text[5]
        elif  "@" in i:
            data["email"].append(i)
        elif "-" in i:
            data["mobile_number"].append(i)
            if len(data["mobile_number"]) ==2:
                data["mobile_number"] = " & ".join(data["mobile_number"])
        elif ind == len(text)-1:
            data["company_name"].append(i)

        elif re.findall('^[0-9].+, [a-zA-Z]+',i):
            data["area"].append(i.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+',i):
            data["area"].append(i)
        
        m1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        m2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        m3 = re.findall('^[E].*',i)
        if m1:
            data["city"].append(m1[0])
        elif m2:
            data["city"].append(m2[0])
        elif m3:
            data["city"].append(m3[0])

        state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
        if state_match:
            data["state"].append(i[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
            data["state"].append(i.split()[-1])
        if len(data["state"])== 2:
            data["state"].pop(0)

        if len(i)>=6 and i.isdigit():
            data["pin_code"].append(i)
        elif re.findall('[a-zA-Z]{9} +[0-9]',i):
            data["pin_code"].append(i[10:])


    return data
 # Establish a connection to your MySQL database
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database= "Biz_Card"
    )
mycursor = mydb.cursor()
def store_database(df):
    try:
        #Creating database
        query1='CREATE DATABASE IF NOT EXISTS Biz_Card'
        mycursor.execute(query1)
        mydb.commit()
        #Inserting using sqlalchemy
        import sqlalchemy
        from sqlalchemy import create_engine
        engine =sqlalchemy. create_engine('mysql+mysqlconnector://root:root@localhost/Biz_Card')
        #Transfer data
        #Inserting using sqlalchemy
        df.to_sql('customer_details', engine, if_exists ='replace', index=False,dtype={
                                                                    "card_holder_name":sqlalchemy.types.VARCHAR(length=50),
                                                                    "designation":sqlalchemy.types.VARCHAR(length=50),
                                                                    "website":sqlalchemy.types.VARCHAR(length=50),
                                                                    "email":sqlalchemy.types.VARCHAR(length=50),
                                                                    "mobile_number":sqlalchemy.types.VARCHAR(length=50),
                                                                    "company_name":sqlalchemy.types.VARCHAR(length=50),
                                                                    "area":sqlalchemy.types.VARCHAR(length=50),
                                                                    "city":sqlalchemy.types.VARCHAR(length=50),
                                                                    "state":sqlalchemy.types.VARCHAR(length=50),
                                                                    "pin_code":sqlalchemy.types.BIGINT})
        mydb.commit()
        return True
    except Exception as e:
        print("An error occurred while storing data in database:", e)
        return False

                                                                    
# Setting page configuration
st.set_page_config(layout="wide")

# Creating styled title using HTML
st.markdown("<h1 style='color: black;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# Creating option menu with purple colored options using Markdown with HTML
selected = option_menu(
    menu_title="",  # Leave it empty since we've already displayed the title above
    options=[
        "Home", 
        "Upload and Extract", 
        "Modify"
    ],
    orientation="horizontal"
)
# Home menu
if selected == "Home":
    col1,col2 = st.columns(2)
    with col1:
        st.image("C:\\Users\\RAMAN\\Desktop\\DS\\PROJECT\\BizCardX Extracting Business Card Data with OCR\\BizCard2dw5.jpg", width = 550)
    with col2:
        st.subheader("A business card is a small card typically used for networking and sharing contact information in a professional setting. It usually includes essential details such as the individual's name, job title, company name, contact information (phone number, email address), and possibly the company's logo and website URL. Business cards are exchanged during introductions or meetings as a convenient way to provide contact details and facilitate future communication and networking opportunities. They are an essential tool for professionals across various industries to establish connections and leave a lasting impression on potential clients, partners, or employers.")
# Upload and Extract
if selected == "Upload and Extract":
    # Creating file uploader to allow users to upload an image
    uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    col1, col2 = st.columns(2)
    with col1:
        if uploaded_image is not None:
            # Display the uploaded image
            st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)

            # Extract filename from the uploaded image
            image_filename = uploaded_image.name

            # Extract data from the uploaded image
            text = image_to_text(uploaded_image)
            # Display the extracted text
            st.write("Extracted Text:")
            st.write(text)
            data = get_data(text)
            st.write(data)
            #Convert to df
            def create_df(data):
                df = pd.DataFrame(data)
                return df
            df = create_df(data)
            st.write(df)
            #Convert to db
    with col2:
        SQL=st.button("Store it to database")
        if SQL:
            DB=store_database(df)
            st.success("Data loaded to Database")

#Modify
if selected == "Modify":
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT card_holder_name FROM customer_details")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card_holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute("select company_name,card_holder_name,designation,mobile_number,email,website,area,city,state,pin_code from customer_details WHERE card_holder_name=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # Displaying all the informations
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE customer_details SET company_name=%s,card_holder_name=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder_name=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")
    except Exception as e:
        print("An error occurred:", e)

                
    
        
       