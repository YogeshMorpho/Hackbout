from flask import Flask, redirect, url_for, request, render_template
import sqlite3
import pickle
import cv2,keras
from keras import models
import os
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
import numpy as np
import tensorflow as tf


app=Flask(__name__, static_folder='static')


diseases={0:'Apple___Apple_scab',
 1:'Apple___Black_rot',
  2:'Apple___Cedar_apple_rust',
   3:'Apple___healthy', 
   4:'Blueberry___healthy',
    5:'Cherry_(including_sour)___Powdery_mildew',
     6:'Cherry_(including_sour)___healthy',
      7:'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
       8:'Corn_(maize)___Common_rust_',
        9:'Corn_(maize)___Northern_Leaf_Blight',
         10:'Corn_(maize)___healthy',
          11:'Grape___Black_rot',
           12:'Grape___Esca_(Black_Measles)',
            13:'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
             14:'Grape___healthy',
              15:'Orange___Haunglongbing_(Citrus_greening)',
               16:'Peach___Bacterial_spot',
                17:'Peach___healthy',
                 18:'Pepper,_bell___Bacterial_spot',
                  19:'Pepper,_bell___healthy',
                   20:'Potato___Early_blight',
                    21:'Potato___Late_blight',
                     22:'Potato___healthy',
                      23:'Raspberry___healthy',
                       24:'Soybean___healthy',
                        25:'Squash___Powdery_mildew', 
                        26:'Strawberry___Leaf_scorch',
                         27:'Strawberry___healthy',
                          28:'Tomato___Bacterial_spot',
                           29:'Tomato___Early_blight',
                            30:'Tomato___Late_blight',
                             31:'Tomato___Leaf_Mold',
                              32:'Tomato___Septoria_leaf_spot',
                               33:'Tomato___Spider_mites Two-spotted_spider_mite',
                                34:'Tomato___Target_Spot',
                                 35:'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                                  36:'Tomato___Tomato_mosaic_virus',
                                   37:'Tomato___healthy',
                                    38:'background'}

model=pickle.load(open('model.pkl','rb'))
model._make_predict_function() 
print('Model Loaded')

def model_predict(img_path,model):
    img3=cv2.imread(img_path)
    img3=cv2.resize(img3,(224,224))
    img3=np.reshape(img3,[1,224,224,3])

    prediction=model.predict_classes(img3)
    
    #prediction=np.array_str(prediction)
    b=prediction[0]
    print(b)

    return diseases[b]

@app.route('/')
def home():
	return render_template('home.html')

	
@app.route('/index',methods=['GET'])
def index():
    return render_template('index.html')
    
'''
@app.route('/qna')
def faq():
    return render_template('l.html')

'''
@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/predict',methods=['GET','POST'])
def upload():
    if request.method=='POST':
        f=request.files['file']

        basepath=os.path.dirname(__file__)
        file_path=os.path.join(
            basepath,'uploads',secure_filename(f.filename)
        )
        f.save(file_path)

        preds=model_predict(file_path,model)
        return preds
    return 'RANDOM'

import json,requests
api_token = 'Your mapmyindia api token here'
#api_url_base ='https://atlas.mapmyindia.com/api/places/nearby/json?keywords=fertiliser&refLocation=12.8434519,77.37721959999999'
api_url_base ='https://atlas.mapmyindia.com/api/places/search/json?query=fertiliser'



headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(api_token)}


def get_account_info():

    response = requests.get(api_url_base, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None 

account_info = get_account_info()
print(account_info)

@app.route('/shops')
def shops():
    c=0
    d=[]
    for i in account_info["suggestedLocations"]:
        lat=i["latitude"]
        long=i["longitude"]
        crd=[lat,long]
        #return render_template('shops.html',crd=crd)
        d.append(crd)
        c=c+1
    length=len(account_info["suggestedLocations"])   
    return render_template('shops.html',d=d,data=account_info["suggestedLocations"],length=length)    

@app.route('/enternew')
def new_ques():
   return render_template('Ask.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   if request.method == 'POST':
      
         que = request.form['ques']
         cat = request.form['opt']
         desc= request.form['desc']
         
         with sqlite3.connect("ques.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO questionaaa (ques,description,category) VALUES (?,?,?)",(que,desc,cat) )
            
            con.commit()
         return render_template('Ask.html')
@app.route('/list1')
def list1():
   con = sqlite3.connect("answer.db")
   con.row_factory = sqlite3.Row
   
   cur = con.cursor()
   cur.execute("select * from ans")
   
   rows = cur.fetchall(); 
   return render_template("disp.html",rows = rows)

@app.route('/qna')
def list():
   con = sqlite3.connect("quest.db")
   con.row_factory = sqlite3.Row
   
   cur = con.cursor()
   cur.execute("select * from questionaaa")
   
   rows = cur.fetchall(); 
   return render_template("toanswer.html",rows = rows)




@app.route('/addrec1',methods = ['POST', 'GET']) 
def addrec1():
    if request.method == 'POST':
      
         ques = request.form['ques']
         ans = request.form['ans']
         
         with sqlite3.connect("answer.db") as con:
            cur = con.cursor()
            
            cur.execute("INSERT INTO ans (ques,answer) VALUES (?,?)",(ques,ans) )
            
            con.commit()
            con.close()
            render_template("toanswer.html")            

if __name__ == '__main__':
    app.run(debug=True)



