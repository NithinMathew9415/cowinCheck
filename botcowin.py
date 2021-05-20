import requests
import json
import time
import datetime
import smtplib
import firebase_admin
from firebase_admin import firestore
import datetime
from datetime import timedelta

#Define Constants
PINCODE = "560077" #Example 600040
DISTRICT_ID = "294"
MY_EMAIL = "Sender email" #From this mail id, the alerts will be sent
MY_PASSWORD = "Enter password" #Enter the email id's password

#Derive the date and url
#url source is Cowin API - https://apisetu.gov.in/public/api/cowin
today = time.strftime("%d/%m/%Y")
url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={DISTRICT_ID}&date={today}"

cred_obj = firebase_admin.credentials.Certificate('./cowin-68efc-firebase-adminsdk-u2syt-447f15affe.json')
projectId = 'cowin-68efc'
default_app = firebase_admin.initialize_app(cred_obj, {
    'projectId':projectId
    })

db = firestore.client()

#Write a loop which checks for every 1000 seconds
while True:
    #Start a session
    with requests.session() as session:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        response = session.get(url, headers=headers)

        #Receive the response
        response = response.json()
        #print(response)
        print("API Call")

        alerts_ref = db.collection("Alerts")
        query = alerts_ref.order_by(u'DateAdded', direction=firestore.Query.DESCENDING).limit(1)
        latest = query.get()
        date = u'{}'.format(latest[0].to_dict()['DateAdded'])
        date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        if now-timedelta(hours=6) <= date_time_obj <= now:
            print("Sleep Time")
        else:
            for center in response['centers']:
                for session in center['sessions']:

                    #For Age not equal to 45 and capacity is above zero
                    if (session['min_age_limit'] != 45) & (session['available_capacity_dose1'] > 0) & (session['vaccine'] == "COVISHIELD"):
                        message_string=f"Subject: {today} Vaccine Alert'!! \n\n Available - {session['available_capacity']} in {center['name']} on {session['date']} for the age {session['min_age_limit']}"
                        
                        doc_ref = db.collection(u'Alerts').document()
                        doc_ref.set({
                            u'Email_Id': MY_EMAIL,
                            u'Message': message_string,
                            u'DateAdded': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

                        print(message_string)
                        
                        mail = smtplib.SMTP('smtp.gmail.com',587)
                        mail.ehlo()
                        mail.starttls()
                        mail.login(MY_EMAIL,MY_PASSWORD)
                        mail.sendmail('nithinmathew94155@gmail.com','nithin9415@gmail.com',message_string) 
                        mail.close()
                        

        time.sleep(30)