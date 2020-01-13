import requests,math
from flask import Flask,render_template,request,url_for,redirect,session
from flask_sqlalchemy import SQLAlchemy 
from geopy.geocoders import Nominatim
from geopy import distance
import geocoder
from sqlalchemy import text
import pandas,numpy,csv
import diseaseprediction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mysite.db'
db = SQLAlchemy(app)

class User(db.Model):
    hno = db.Column(db.Integer, primary_key=True)
    hname = db.Column(db.String(1000), nullable=False)
    insurance = db.Column(db.String(1000), nullable=False)
    htype = db.Column(db.String(1000), nullable=False)
    hadd = db.Column(db.String(1000), nullable=False)
    telephone = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(100),nullable=False)
    specilties = db.Column(db.String(10000), nullable=False)
    ratings=db.Column(db.Numeric(),nullable=False)
    lat = db.Column(db.Numeric(), nullable=False)
    lng = db.Column(db.Numeric(), nullable=False)
    dist = db.Column(db.Numeric())

    def __repr__(self):
        return f"User('{self.hno}', '{self.hname}', '{self.insurance}', '{self.htype}', '{self.hadd}', '{self.telephone}', '{self.website}', '{self.specilties}', '{self.ratings}', '{self.lat}', '{self.lng}', '{self.dist}')"


with open('Testing.csv', newline='') as f:
        reader = csv.reader(f)
        symptoms = next(reader)
        symptoms = symptoms[:len(symptoms)-1]

@app.route('/',methods = ['GET','POST'])
def _home():
    if request.method == 'POST':
        radius=request.form['radius']
        session['radius']=radius
        #zip=request.form['zip']
        #session['zip']=zip
        return redirect(url_for('fly'))
        #return fly(radius)
        #return render_template('home.html',posts=posts)
    return render_template('index1.html',symptoms=symptoms)    
    return 'Oops! something went wrong'

@app.route('/search',methods=['GET','POST'])
def fly():
        selected_symptoms = []
        selected_users = request.form.getlist("users")
        disease = diseaseprediction.dosomething(selected_users)
        radius=session.get('radius')
        #a=session.get('zip')
        g=geocoder.ip('me')
        a=g.latlng
        geolocator = Nominatim(user_agent="specify_your_app_name_here")
        location = geolocator.geocode(a)
        sql1 = text('select lat from User')
        result1 = db.engine.execute(sql1)
        lats=[row[0] for row in result1]
        sql2 = text('select lng from User')
        result2 = db.engine.execute(sql2)
        lngs=[ro[0] for ro in result2]
        merged_list = [(lats[i], lngs[i]) for i in range(0, len(lats))]
        li=[]
        for j in merged_list:
            b=(distance.distance(a,j).km)
            li.append(b)
        res = dict(zip(lats, li)) 
        sorted_x = sorted(res.items(), key=lambda kv: kv[1])
        re = [lis[0] for lis in sorted_x]
        ra = [lis[1] for lis in sorted_x] 
        t=tuple(re)
        v=tuple(ra)
        for su in range(len(re)):
            query1 = "UPDATE User SET dist = '{}' WHERE lat = {}".format(v[su]+10,t[su])
        #query = "select * from User where lat IN {}".format(t)
            sql4=text(query1)
            result=db.engine.execute(sql4)
        sql5="select * from User order by ratings desc, dist asc"
        result5 = db.engine.execute(sql5)


        
        #app.logger.debug('A value for debugging')
        #users = User.query.all().filter_by(result1)
        #for i in re:
         #  query="select * from User where lat={};".format(i)
          # sql3=text(query)
           #result=db.engine.execute(sql3)
        #return f'{result.lat}'    
        #worms=[x for x in result]
        return render_template('home.html',result5=result5,sorted_x=sorted_x,selected_users=selected_users,disease=disease)

if __name__ == "__main__":
   app.run(debug=True)
