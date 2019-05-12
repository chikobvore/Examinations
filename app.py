from flask import Flask, render_template, request,url_for,redirect,session
import pymongo
import pandas as pd
import numpy as np
import sys
from sklearn import preprocessing
from sklearn import tree
from sklearn.metrics import accuracy_score,precision_score,f1_score, confusion_matrix,recall_score
from sklearn.model_selection import train_test_split

# loading datasets here

data = pd.read_csv('static/dataset/newdata.csv')
print(data.head())
inputs = data.drop('Grade',axis='columns')

le = preprocessing.LabelEncoder()

Target = le.fit_transform(inputs['Comment'])

app = Flask(__name__)
client = pymongo.MongoClient('localhost', 27017)
db = client['Exams']

@app.route('/')
def home():
   return render_template('Home.html')

@app.route('/Record')
def Record():
   return render_template('Record.html')

@app.route('/newcourse')
def newcourse():
   return render_template('newcourse.html')


if __name__ == '__main__':
   app.secret_key = 'super secret key'
   app.config['SESSION_TYPE'] = 'filesystem'
   app.debug = True
   app.run()
   app.run(debug = True)
