from tracemalloc import start
import requests
import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
import time

if os.getenv('TIME_REQUIREMENT') is not None:
    time_requirement = os.environ['TIME_REQUIREMENT']
else: 
    time_requirement = True

if os.getenv('CHECK_ONLY') is not None:
    check_only = os.environ['CHECK_ONLY']
else: 
    check_only = False
   
appointment_created = False


def create_appointment(date, startTime, endTime, key):
    
    
    json_result = {}
    
    bookable_slot = {"key": key, "date": date, "startTime":startTime, "endTime": endTime, "parts":2, "booked": False}
    appointment = {"productKey": "DOC", "date": date, "startTime":startTime, "endTime": endTime, "email": "test@gmail.com", "phone": "06000000", "language":"nl" }
    customers = [{"vNumber": 123444, "firstName": "firstname", "lastName": "lastnam"},{"vNumber": 123456, "firstName": "firtName", "lastName": "last"}]
    
    response = requests.post('https://oap.ind.nl/oap/api/desks/AM/slots/' + key, json=bookable_slot)
    print(bookable_slot)
    json_result['bookableSlot'] = bookable_slot
    appointment['customers'] = customers
    json_result['appointment'] = appointment

    response = requests.post('https://oap.ind.nl/oap/api/desks/AM/appointments/', json=json_result)
    
    print(response)

    if (response.status_code == 200):
        response = response.text.replace(")]}',", "")
        response_for_email = json.loads(response)
        print("An appointment has been created. \n\nDate: " + date_option['date'] + '. \nTime: ' + date_option['startTime'] + '. \nCancellation URL: https://oap.ind.nl/oap/nl/#/cancel/' + response_for_email['data']['key'] +'. \nAppointment Code: ' + response_for_email['data']['code'])
        print("Successfully created an appointment")

while appointment_created is False:
    
    r = requests.get(
        'https://oap.ind.nl/oap/api/desks/AM/slots/?productKey=DOC&persons=2') #look for 2 slots
    response = r.text.replace(")]}',", "")
    result = json.loads(response)

    #Loop through the retrieved dates
    for date_option in result['data']:
    
        expected_start_date = datetime.strptime('2022-09-20 09:30', '%Y-%m-%d %H:%M')
        expected_end_date = datetime.strptime('2022-10-20 18:30', '%Y-%m-%d %H:%M')


        # get all the data coming back from the server
        first_date_option_str = date_option['date'] + \
            " " + date_option['startTime']
        first_date_option_obj = datetime.strptime(
            first_date_option_str, '%Y-%m-%d %H:%M')
        first_date_option_obj_month = first_date_option_obj.month
        first_date_option_obj_day = first_date_option_obj.day
        
        # check for any requirements, if nothing, just continue
        if (time_requirement):
            # do the check here, this below should be dynamic TODO
            #if((first_date_option_obj_month == 9 or first_date_option_obj_month == 10) and ()):
             if((first_date_option_obj >= expected_start_date and first_date_option_obj <= expected_end_date)):
                # then send email
                if(check_only): 
                    send_email('There is a slot: ' + first_date_option_str)
                else:
                    print("There is slot available " + first_date_option_str)
                    create_appointment(date_option['date'], date_option['startTime'], date_option['endTime'], date_option['key'])
                    appointment_created = True
                break
        else:
            #create the appointment directly once we get the first date available
            print("No slot available")
            appointment_created = False 
    time.sleep(60)

print("Appointment has been created, the job is done.")

    
