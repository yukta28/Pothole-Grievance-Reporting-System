# from dataclasses import replace
from flask import *
from werkzeug.utils import secure_filename
# from flask import Flask, render_template, request
import pickle
import pymysql
import pandas as pd
import socket
from datetime import datetime
# import tensorflow
# from tensorflow import keras
# from tensorflow.keras.models import load_model
import pickle


app = Flask(__name__)

def dbConnection():
    try:
        connection = pymysql.connect(host="localhost", user="root", password="root", database="dbroadpotholes",charset='utf8')
        return connection
    except:
        print("Something went wrong in database Connection")

def dbClose():
    try:
        dbConnection().close()
    except:
        print("Something went wrong in Close DB Connection")

con=dbConnection()
cursor=con.cursor()

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploaded_img/'
app.secret_key = 'random string'

##########################################################################################################
#                                           Register
##########################################################################################################
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        # print("hii register")
        email = request.form['Email']
        mobileno = request.form['mobileno']
        password = request.form['pass1']
        username = request.form['Name']

        print(email,password,username)

        try: 
            con = dbConnection()
            cursor = con.cursor()
            sql1 = "INSERT INTO tblregister (uname, email, password, mobile) VALUES (%s, %s, %s, %s)"
            val1 = (username, email, password, mobileno)
            cursor.execute(sql1, val1)
            print("query 1 submitted")
            con.commit()

            FinalMsg = "Congrats! Your account registerd successfully!"
        except:
            con.rollback()
            msg = "Database Error occured"
            print(msg)
            return render_template("login.html", error=msg)
        finally:
            dbClose()
        return render_template("login.html",FinalMsg=FinalMsg)
    return render_template("register.html")
##########################################################################################################
#                                               Login
##########################################################################################################
@app.route("/", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['password'] 

        print(email,password)

        con = dbConnection()
        cursor = con.cursor()
        result_count = cursor.execute('SELECT * FROM tblregister WHERE email = %s AND password = %s', (email, password))
        result = cursor.fetchone()
        print("result")
        print(result)
        if result_count>0:
            print("len of result")
            session['uname'] = result[1]
            session['userid'] = result[0]
            return redirect(url_for('root'))
        else:
            result_count = cursor.execute("Select * FROM tbladmin WHERE email=%s AND password=%s", (email, password))
            result = cursor.fetchone()
            if result_count == 1:
                session['uname'] = result[1]
                session['userid'] = result[0]
                return redirect(url_for("adminindex"))
            else:
                return render_template('login.html')
    return render_template('login.html')
##########################################################################################################
#                                       Product Description
##########################################################################################################
@app.route("/single", methods = ['POST', 'GET'])
def productDescription():
    
    return render_template('services.html')
##########################################################################################################
#                                               about
##########################################################################################################
@app.route("/about", methods = ['POST', 'GET'])
def about():
    username=session.get('uname')
    return render_template('about.html')

@app.route("/adminabout", methods = ['POST', 'GET'])
def adminabout():
    username=session.get('uname')
    return render_template('adminabout.html')
##########################################################################################################
#                                               contact
##########################################################################################################
@app.route("/contact", methods = ['POST', 'GET'])
def contact():
    username=session.get('uname')
    return render_template('contact.html',firstName=username)

@app.route("/admincontact", methods = ['POST', 'GET'])
def admincontact():
    username=session.get('uname')
    return render_template('admincontact.html',firstName=username)
##########################################################################################################
#                                               contact
##########################################################################################################
@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    session.pop('uname',None)
    session.pop('userid',None)
    return redirect(url_for('login'))
#########################################################################################################
#                                       Home page
##########################################################################################################
@app.route("/root")
def root():
    if 'uname' in session:

        return render_template('index.html')
    
@app.route("/adminindex")
def adminindex():
    if 'uname' in session:
        con = dbConnection()
        cursor =con.cursor()
        result1 = cursor.execute("SELECT imagepath, latitude, longitude, uname, address FROM tblroadimg where status='underprogress'")    
        res = cursor.fetchall()
        result = list(res)

        imagepath = [i[0] for i in result]
        latitude = [i[1] for i in result]
        longitude = [i[2] for i in result]
        uname = [i[3] for i in result]
        address = [i[4] for i in result]
    
        finallst = zip(imagepath,latitude,longitude, uname, address)
        #print(set(finallst))
        print("query submitted...")
        con.commit()

        return render_template('adminindex.html',finallst=finallst)
########################################### UPLOAD IMAGE  ###################################################################

import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import  torch
from PIL import Image
import imageio
from geopy.geocoders import Nominatim
import geocoder

def image_coordinates(filenamepath):
    #filenamepath ="D:\\Work\\road_potholes_detection\\grand_canyon.jpg"
    print('filenamepath1='+filenamepath)
    from exif import Image
    with open(filenamepath, 'rb') as src:
        img = Image(src)
    if img.has_exif:
        try:
            print('filenamepath2='+filenamepath)
            
            img.gps_longitude
            coords = (decimal_coords(img.gps_latitude,
                        img.gps_latitude_ref),
                        decimal_coords(img.gps_longitude,
                        img.gps_longitude_ref))
        except AttributeError:
            print('No Coordinates')
    else:
        print('The Image has no EXIF information')
    print(f"Image {src.name}, OS Version:{img.get('software', 'Not Known')} ------")
    print(f"Was taken: {img.datetime_original}, and has coordinates:{coords}")
    return coords
    
def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

@app.route("/upload_image", methods=['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        image = request.files['file']
        address = request.form['address']
        print(address)
        #print("image=  "+str(image))
        uname = session['uname']
                
        filename_secure = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename_secure))
        filenamepath = os.path.join(app.config['UPLOADED_PHOTOS_DEST'],filename_secure)
        ff = filename_secure
        print(filenamepath)
        
        # model = torch.hub.load('ultralytics/yolov5', 'custom', 'yolov5/runs/train/exp/weights/best.pt',force_reload=True)
        model = torch.hub.load('ultralytics/yolov5', 'custom', 'yolov5/runs/train/exp/weights/best.pt')
        results = model(str(filenamepath))
        # results = model(MEDIA_URL+"/"+str(file_url))
        results.print()
        b=results.pandas().xyxy[0]
        print(b)
        
        print(type(b))
        name = b['name'].tolist()
        list1=["Pothole","pothole"]
        detected=[]
        notdetected=[]
        geolocator = Nominatim(user_agent="geoapiExercises")

        for i in list1:
            print(i)
            if i in name:
                detected.append(i)
                final_cord = image_coordinates(filenamepath)
                print('final_cord=')
                print(final_cord)
                #######################################################################
                # latitude = "19.0745"
                # longitude = "72.9978" 
                latitude = final_cord[0]
                longitude = final_cord[1]
                print("latitude= " +str(latitude))
                print("longitude= " +str(longitude)) 

                # Latitude & Longitude input
                Latitude = latitude
                Longitude = longitude

                location = geolocator.reverse(str(Latitude)+","+str(Longitude))

                # Display
                print(location)

                latlong_address = location.raw['address']
                print(latlong_address)
                
                con = dbConnection()
                cursor = con.cursor()
                potholestatus = "underprogress"
                prediction = "Pothole detected"
                print("connection done...")
                query1 = "INSERT INTO tblroadimg(imagepath,address,latitude,longitude,uname,prediction,status) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                value = (filenamepath,location,latitude,longitude,uname,prediction,potholestatus)
                result = cursor.execute(query1,value)
                print(result)
                print("query 1 submitted successfully...")
                #print(image)
                con.commit() 
                msg = "Image Uploaded Successfully...."        
                return render_template('uploadimage.html', msg=msg)
            else:                
                # notdetected.append(i)
                msg = "You have uploaded wrong image!!!" 
                # con.commit()        
                return render_template('uploadimage.html', msg=msg)
    return render_template('uploadimage.html')

#############################################################  USER History   ###############################################################
@app.route("/history", methods=['POST', 'GET'])
def userhistory():
    con = dbConnection()
    cursor = con.cursor()
    uname = session['uname']
    lbl1 = "underprogress"    
    result_count1 = cursor.execute("SELECT imgid,imagepath,address,uname,prediction,status FROM tblroadimg where uname=%s ",(uname))
    result = cursor.fetchall() 
    print(result)
    con.commit()
    return render_template('userDetails.html',result=result)

#############################################################  CUSTOMER REQUEST PAGE   ###############################################################
@app.route("/customerRequest", methods=['POST', 'GET'])
def customerRequest():
    #imgid=id
    con = dbConnection()
    cursor = con.cursor()
    
    lbl1 = "underprogress"    
    result_count1 = cursor.execute("SELECT imgid,imagepath,uname,status FROM tblroadimg where status=%s ",(lbl1))
    result1 = cursor.fetchall() 
    print(result1)
    
    lbl2 = " Done "
    result_count2 = cursor.execute("SELECT imgid,imagepath,uname,status FROM tblroadimg where status=%s ",(lbl2))
    result2 = cursor.fetchall()
    print(result2)
    
    print("query 2 submitted")
    con.commit()
    return render_template('customerRequest.html',result1=result1,result2=result2)

#################################################################  UPDATE STATUS   ############################################################### 
@app.route("/updateStatus/<string:id>", methods=['POST', 'GET'])
def updateStatus(id):
    imgid = id
    lbl =" Done"
    con = dbConnection()
    cursor = con.cursor()
    upQuery = (" Update tblroadimg SET status = %s WHERE imgid=%s")
    val = (lbl,imgid)
    result = cursor.execute(upQuery,val)
    print("Query updated...")
    con.commit()
    return redirect(url_for("customerRequest"))

if __name__=='__main__':
    app.run(debug=True)
    # app.run('0.0.0.0')