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
inputs = data.drop("Comment",axis = 1)

le = preprocessing.LabelEncoder()

Target = le.fit_transform(data['Comment'])

    

'''Spliting data into training set and testing set '''
xTrain, xTest, yTrain, yTest = train_test_split(inputs,Target, test_size = 0.3, random_state = 0)

'''Training our model '''
Model =  tree.DecisionTreeClassifier()
Model.fit(xTrain,yTrain)
Model.score(xTrain,yTrain)

data2b  = pd.read_csv("static/dataset/D2.csv")
# splitting data into inputs and outputs
input2 = data2b.drop("Remarks", axis=1)
lb2 = preprocessing.LabelEncoder()
Target2 = lb2.fit_transform(data2b['Remarks'])
#Split data into training set and testing set
x1Train, x1Test, y1Train, y1Test = train_test_split(input2,Target2, test_size = 0.3, random_state = 0)

Model2 = tree.DecisionTreeClassifier()
Model2.fit(x1Train,y1Train)

app = Flask(__name__)
client = pymongo.MongoClient('localhost', 27017)
db = client['Exam_record']

@app.route('/')
def home():
   Anomallies = []
   for course in db['Courses'].find():
      name = course['Course_code']+ " "+ course['Course_name']
      Total = db['Marks'].find({"Course": name}).count()
      A = db['Marks'].find({"$and":[{"Course": name},{"Grade":"1"}]}).count()
      B = db['Marks'].find({"$and":[{"Course": name},{"Grade":"2.1"}]}).count()
      C = db['Marks'].find({"$and":[{"Course": name},{"Grade":"2.2"}]}).count()
      D = db['Marks'].find({"$and":[{"Course": name},{"Grade":"P"}]}).count()
      F = db['Marks'].find({"$and":[{"Course": name},{"Grade":"F"}]}).count()

      A1 = (A/Total)*100
      B1 = (B/Total)*100
      C1 = (C/Total)*100
      D1 = (D/Total)*100
      F1 = (F/Total)*100

      Predict = Model2.predict([[A1,B1,C1,D1,F1]])
      Anomally = lb2.inverse_transform(Predict)

      data = {
         "Course_code": course['Course_code'],
         "Course_name": course['Course_name'],
         "a":A,
         "b":B,
         "c":C,
         "P":D,
         "F":F,
         "Total":Total,
         "Comment":Anomally
      }
      Anomallies.append(data)
      
   return render_template('Home.html',Anomallies = Anomallies)

@app.route('/Record',methods = ['POST','GET'])
def Record():
   if request.method == 'POST':
      course = request.form['course']
      Reg_number = request.form['RegNum']
      Full_name = request.form['fullname']
      Tcw = request.form['tcw']
      TEM = request.form['tem']

      Tcw = 0.4 * int((Tcw))
      TEM = 0.6 * int((TEM))
      total = Tcw + TEM

      if total < 45:
         grade = 'F'
      elif total > 44 and total < 55:
         grade = 'P'
      elif total >54 and total <65:
         grade = '2.2'
      elif total >64 and total < 75:
         grade = '2.1'
      else:
         grade = '1'

      Predict = Model.predict([[Tcw,TEM,total]])
      Anomally = le.inverse_transform(Predict)
      Anomally = Anomally[0]
      print(Anomally)

      New_record = {
         "Course": course,
         "Reg_number": Reg_number,
         "Full_name": Full_name,
         "Total_Course_Work": Tcw,
         "Total_Exam_mark": TEM,
         "Final_Mark": total,
         "Grade": grade,
         "Comment": Anomally
      }

      count = db.Marks.find({"$and":[{"Reg_number": Reg_number,"Course": course}]}).count()
      Students = []

      if count == 0:
         db['Marks'].insert_one(New_record)
         print("Record successfully added")
         message = "Record successfully added"

         for student in db['Marks'].find({"Course":course}):
            Students.append(student)
         Course = []
         for thecourse in db['Courses'].find():
            Course.append(thecourse)
         return render_template('students.html',Students = Students,message = message,course = course)
      else:
         db['Marks'].update( {"$and": [
            {"Reg_number": Reg_number,"Course": course}]},
            {"Total_Course_Work":Tcw,
            "Course": course,
            "Reg_number": Reg_number,
            "Full_name": Full_name,
            "Total_Exam_mark": TEM,
            "Final_Mark":total,
            "Grade": grade,
            "Comment": Anomally})
         print("Record successfully updated")
         message = "Record successfully updated"
         for student in db['Marks'].find({"Course": course}):
            Students.append(student)
         Course = []
         for thecourse in db['Courses'].find():
            Course.append(thecourse)
         return render_template('students.html',Students = Students,message = message,Course = Course,course = course)
   Course = []
   for course in db['Courses'].find():
      Course.append(course)
   return render_template('Record.html',Course = Course)

@app.route('/newcourse',methods = ['POST','GET'])
def newcourse():
   if request.method == 'POST':
      course_code = request.form['code']
      course_name = request.form['name']
      course_type = request.form['type']

      Course = {
         "Course_code": course_code,
         "Course_name": course_name,
         "Course_type": course_type
      }
      
      db['Courses'].insert(Course)
      print("Course successfully added")
      return render_template('Home.html')
   return render_template('newcourse.html')

@app.route('/delete')
def delete():
   db['Courses'].delete_many({})
   db['Marks'].delete_many({})
   return render_template('Home.html')

@app.route('/Marks')
def Marks():
   return render_template('Marks.html')

if __name__ == '__main__':
   app.secret_key = 'super secret key'
   app.config['SESSION_TYPE'] = 'filesystem'
   app.debug = True
   app.run()
   app.run(debug = True)
