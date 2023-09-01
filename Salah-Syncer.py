import requests
import calendar
from datetime import datetime, timedelta
from Google import Create_Service
import os 

#The Google Calendar API requires the date to be in RFC3339 format which is why this function is used
def set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, start_or_end):
    date_time = (datetime.strptime((datetime.strptime(timings[start_or_end][:5], "%H:%M")).strftime(f'{str_year}-{str_month}-{str_day}T%H:%M:%S.%f%z'), '%Y-%m-%dT%H:%M:%S.%f') + timedelta(hours=hours_adjustment, minutes=minutes_adjustment)).isoformat()
    return date_time

def get_timings(url, salah_day):
    response = requests.get(url)
    data = response.json()
    timings = data['data'][salah_day]['timings']
    return timings

def create_calendar(calendar_name):
     #Making the request body for the calendar
            new_calendar_request_body = {
                'summary' : calendar_name,
                'timeZone' : 'Etc/UTC'
            } 
            #Creating the calendar
            created_calendar = service.calendars().insert(body=new_calendar_request_body).execute()
            calendar_id = created_calendar['id']    
            print("\nNew calendar successfully created.\n")
            
            #Enabling notifications for the calendar
            created_calendar_request_body = {
                'id' : calendar_id,
                'defaultReminders' : [
                    {
                        'method' : 'popup',
                        'minutes' : 0
                    }
                ]
            }
            service.calendarList().insert(body=created_calendar_request_body).execute()
            
            return calendar_id

def get_date(calendar_day, month, year):
    date = datetime(year, month, calendar_day)
    formatted_date = date.strftime(f"{calendar_day}{get_suffix(calendar_day)} %B %Y")
    return formatted_date

def get_suffix(calendar_day):
    if 10 <= calendar_day <= 20:
        return 'th'
    else:
        last_digit = calendar_day % 10
        if last_digit == 1:
            return 'st'
        elif last_digit == 2:
            return 'nd'
        elif last_digit == 3:
            return 'rd'
        else:
            return 'th'

#This block of code is all the input data the user needs to provide along with their validation:

print("Welcome to Salah Syncer!\nSalah Syncer is a program that syncs prayer timings with your google calendar.\n")
while True:
    choice = str(input("Is this your first time using Salah Syncer on the account you want to sync the prayer timings to? [y/n]\n")).upper()
    if choice == 'Y':
        print("Alright! Before proceeding, please visit the following liink and follow the steps under the 'Set up your Environment' heading to enable the program to communicate with your account:\nhttps://developers.google.com/calendar/api/quickstart/python\nPlease ignore the 'Configure the sample' and 'Run the sample' section\n When you have reached the step to 'Create Credentials', follow the instructions and download the credentials JSON file.\n\n")
        while True:
            choice = str(input("Please enter 'y' when you are ready to proceed.\n")).upper()
            if choice == 'Y':
                break
            else:
                print("Invalid choice.\n")
        print("Rename the downloaded file to 'credentials' and put it into the same folder as this program.\n")
        while True:
            choice = str(input("Please enter 'y' when you are ready to proceed.\n")).upper()
            if choice == 'Y':
                break
            else:
                print("Invalid choice.\n")
        break
    elif choice == 'N':
        break

#Setting the path for credentials.json
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json')
#Setting the rest of the parameters required for the Create_Service function
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']
service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES) 

while True:
    try:
        calendar_choice = int(input("Do you want to add prayer timings to:\n1 - A new calendar\n2 - A calendar that already exists\n"))
        if not 1 <= calendar_choice <= 2: 
            print("The value is out of range (min 1 max. 2).\n")
        elif calendar_choice == 1:
            calendar_name = str(input("Enter the name of the new calendar: "))
            break
        elif calendar_choice == 2:
            print("Heres a list of all of your calendars with their corresponding id's:\n")
            #Displaying all the calendar names with their corresponding keys
            list_response = service.calendarList().list().execute()
            items = list_response.get('items')

            for Calendar in items:
                print(f"{Calendar.get('summary')} : {Calendar.get('id')}")

            print("\n")
            calendar_id = str(input("Enter the id of the calendar you want to sync the prayer timings to (ctrl + shift + v to paste in terminal): "))
            break
            
    except ValueError:
                    print("Invalid input. Please enter an integer value.\n")

while True:
    try:
        calendar_day = int(input("Enter the day today (e.g 25) [max 31]: "))
        if not 1 <= calendar_day <= 31:
            print("The value is out of range [min 1, max 31].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")

salah_day = calendar_day - 1

while True:
    try:
        month = int(input("Enter the month (e.g 10) [min 1, max 12]: "))
        if not 1<= month <= 12:
            print("The value is out of range [min 1, max 12].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")

while True:
    try: 
        year = int(input("Enter the year (e.g 2023) [max 4 characters]: "))
        if len(str(year)) > 4:
            print("The value is out of range [max 4 characters].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")

month_days = calendar.monthrange(year, month)[1]

while True:
    try:
        num_of_days = int(input("Enter the number of days for which you want the prayer timings [min 1, max 30]:\nNumber of days:  "))
        if not 1 <= num_of_days <= 30:
            print("The value is out of range [min 1, max 30].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")

address = str(input("Enter your address (e.g San Francisco, California, United States): "))

while True:
    Timezone = str(input("Enter your timezone according to GMT in format GMT+/-HH:MM (e.g GMT+05:00): "))
    if len(Timezone) != 9 or Timezone[0:3] != 'GMT' or (Timezone[3:4] != '+' and Timezone[3:4] != '-') or Timezone[6:7] != ':' or not Timezone[4:6].isdigit() or not Timezone[7:].isdigit():
        print("Invalid input. Please enter a valid timezone.\n")
    else:
        break

hours_adjustment = int(Timezone[3:4] + Timezone[4:6]) * -1
minutes_adjustment = int(Timezone[3:4] + Timezone[7:9]) * -1

while True:
    try:
        method = int(input("\nEnter the method \n1 - University of Islamic Sciences, Karachi \n2 - Islamic Society of North America \n3 - Muslim World League \n4 - Umm Al-Qura University, Makkah \n5 - Egyptian General Authority of Survey \n7 - Institute of Geophysics, University of Tehran \n8 - Gulf Region \n9 - Kuwait \n10 - Qatar \n11 - Majlis Ugama Islam Singapura, Singapore \n12 - Union Organization islamic de France \n13 - Diyanet İşleri Başkanlığı, Turkey \n14 - Spiritual Administration of Muslims of Russia \n15 - Moonsighting Committee Worldwide (also requires shafaq parameter) \n16 - Dubai (unofficial)\n\nMethod: "))
        if not 1 <= method <= 16:
            print("The value is out of range [min 1, max 16].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")
print("\n")
while True:
    try:
        midnightMode = int(input("Choose your preferred midnight mode:\n0 - Standard (Mid Sunset to Sunrise)\n1 - Jafari (Mid Sunset to Fajr)\nMidnight mode: "))
        if not 0 <= midnightMode <= 1:
            print("The value is out of range [min 0, max 1].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")
print("\n")
while True:
    try:
        school = int(input("Choose your preferred school:\n0 - Shafi/Maliki/Hanbali (Standard)\n1 - Hanafi\nSchool: "))
        if not 0 <= school <= 1:
            print("The value is out of range [min 0, max 1].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")
print("\n")
while True:
    try:
        choice = int(input("Choose how you want the Dhuhr name to appear in the calendar:\n0 - Dhuhr (Standard)\n1 - Zuhr\nZuhr name: "))
        if not 0 <= choice <= 1:
            print("The value is out of range [min 0, max 1].\n")
        elif choice == 0:
            Zuhr_name = 'Dhuhr'
            break
        elif choice == 1:
            Zuhr_name = 'Zuhr'
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")
print("\n")
while True:
    try:
        Dharura_mode = int(input("Choose preferred asr end time mode:\n0 - Standard mode (Asr end time is Maghrib start time)\n1 - Dharura mode (Asr end time is start of Wakt Ad Dharura [hanafi asr start time]\nEnd time mode: "))
        if not 0 <= Dharura_mode <= 1:
            print("The value is out of range [min 0, max 1].\n")
        else:
            break
    except ValueError:
        print("Invalid input. Please enter an integer value.\n")

salah_info_index = -1

    
for day in range (num_of_days):
    date = get_date(calendar_day, month, year)
    print(f"\n{date}:")
    for event in range (5):
        salah_info_index += 1
        
        url = f'http://api.aladhan.com/v1/calendarByAddress/{year}/{month}?address={address}&method={method}&midnightMode={midnightMode}&school={school}'
        
        timings = get_timings(url, salah_day)
        
        #converting date values to strings for set_date_time function and adding leading zero's if needed (with .zfill)
        str_year = str(year)
        str_month = str(month).zfill(2)
        str_day = str(calendar_day).zfill(2)

        fajr_start_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Fajr')
        fajr_end_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Sunrise')
        
        zuhr_start_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Dhuhr')
        zuhr_end_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Asr')

        maghrib_start_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Maghrib')
        maghrib_end_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Isha')

        isha_start_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Isha')
        isha_end_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Midnight')

        #Asr end time needs to be set according to users choice of Dharura mode (setting asr at the end so other prayer timings dont get effected as we are creating a new url)
        asr_start_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Asr')
        if school == 1 or Dharura_mode == 0:    
            asr_end_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Maghrib')
        else:
            url = f'http://api.aladhan.com/v1/calendarByAddress/{year}/{month}?address={address}&method={method}&midnightMode={midnightMode}&school=1'
            timings = get_timings(url, salah_day)
            asr_end_time = set_date_time(str_year, str_month, str_day, timings, hours_adjustment, minutes_adjustment, 'Asr')
        
        salah_info = [
            {
                'Name' : 'Fajr',
                'Start time' : fajr_start_time,
                'End time' : fajr_end_time
            },  
            {   
                'Name' : Zuhr_name,
                'Start time' : zuhr_start_time,
                'End time' : zuhr_end_time
            },
            {   'Name' : 'Asr',
                'Start time' : asr_start_time,
                'End time' : asr_end_time
            },
            {   
                'Name' : 'Maghrib',
                'Start time' : maghrib_start_time,
                'End time' : maghrib_end_time
            },
            {   
                'Name' : 'Isha',
                'Start time' : isha_start_time,
                'End time' : isha_end_time
            }
        ]

        if calendar_choice == 1:
            calendar_id= create_calendar(calendar_name)
            calendar_choice = 0 #resetting the choice to 0 so the program doesnt create a new calendar in every itteration of the loop

        event_request_body = {
            'summary' : salah_info[salah_info_index]['Name'],
            'colorId' :'7',
            'start' : {
                'dateTime' : salah_info[salah_info_index]['Start time'],
                'timeZone' : 'Etc/UTC'
            },
            'end' : {
                'dateTime' : salah_info[salah_info_index]['End time'],
                'timeZone' : 'Etc/UTC'
            }
        }
        
        #Making a request to the api to creat the event
        event_response = service.events().insert(calendarId=calendar_id, body=event_request_body).execute()

        print(f"{salah_info[salah_info_index]['Name']} event successfully created")

    calendar_day += 1
    salah_day += 1
    salah_info_index = -1

    if calendar_day > month_days:
        calendar_day = 1
        salah_day = 0
        month += 1
        if month > 12:
            year += 1
            month = 1
        month_days = calendar.monthrange(year, month)[1]

print("\nAll events successfully created.")