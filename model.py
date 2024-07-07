import os
import csv
import time 
import pygetwindow as gw
import json
import ctypes
import time
from ctypes import Structure, c_uint, sizeof, windll

class ProductiveModel:
    def __init__(self):
        self.work_activities = []
        self.entertainment_activities = []
        self.get_actvity_types()
        self.is_tracking = False

    def get_actvity_types(self):
        with open('activity_types.json', 'r') as file:
            data = json.load(file)
            self.work_activites = data['work']
            self.entertainment_activities = data['entertainment']
        
    def start_tracking(self):
        self.is_tracking = True                            
        while self.is_tracking:
            if self.is_user_afk():
                print('User is AFK')
                continue
            try:
                # get the active window
                active_window = gw.getActiveWindow().title
                # get the current time
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                # open csv file to append
                with open('activity_log.csv', mode='a', newline='') as file:
                    # create a csv writer and write the timestamp and active window
                    writer = csv.writer(file)                    
                    writer.writerow([timestamp, active_window])
            except Exception:
                pass
            # sleep for 5 seconds
            time.sleep(5)

    def stop_tracking(self):
        self.is_tracking = False

    def write_daily_activity_to_db_csv(self):
        # create a dictionary to store the activity log data
        activity_log_db = {}
        try:
            # open the db file to read
            with open('activity_log_db.csv', mode='r') as file:
                csv_reader = csv.reader(file)
                # read the db file and store the data in the dictionary
                for row in csv_reader:
                    # add the data to the dictionary with the type as the key and the count as the value
                    activity_log_db [row['type']] = int(row['count'])
        except FileNotFoundError:
            pass

        with open ('activity_log.csv', mode='r') as file:
            csv_reader = csv.reader(file)  
            # read the csv file and check the type of activity          
            for column in csv_reader:
                # check the type of activity
                activity_type = self.check_type_of_activity(column[1])
                if activity_type == 'uncategorized':
                    with open('uncategorized_activities.csv', mode='a', newline='') as uncategorized_file:
                        uncategorized_writer = csv.writer(uncategorized_file)
                        uncategorized_writer.writerow([column[0], column[1]])                      
                    continue
                # check if the activity is in the dictionary
                if activity_type in activity_log_db:
                    activity_log_db[activity_type] += 1
                # if the activity is not in the dictionary, add it
                else:
                    activity_log_db[activity_type] = 1
        
        with open ('activity_log_db.csv', mode='w', newline='') as file:
            db_writer = csv.writer(file)
            # write the header
            db_writer.writerow(['type', 'count'])

            for activity_type, count in activity_log_db.items():
                db_writer.writerow([activity_type, count])
        # delete the csv file
        os.remove('activity_log.csv')

    def fetch_data_csv(self):
        # create a dictionary to store the data
        data = {}
        try:
            # open the db file to read
            with open('activity_log_db.csv', mode='r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                # read the db file and store the data in the dictionary
                for row in csv_reader:
                    # add the data to the dictionary with the type as the key and the count as the value
                    data[row[0]] = int(row[1])
        except FileNotFoundError:
            pass
        return data
    
    def check_type_of_activity(self, activity):
        # arrays for activities        
        # work_activities = ['Visual Studio Code']
        # entertainment_activities = ['youtube', 'netflix', 'prime video', 'disney+', 'spotify', 'World of Warcraft', 'battle.net', 'steam', 'stb_static']
        # loops through the arrays and checks if the activity is in the arrays
        for work in self.work_activities:
            if work.lower() in activity.lower():
                return 'work'
            
        for entertainment in self.entertainment_activities:
            if entertainment.lower() in activity.lower():
                return 'entertainment'
        
        return 'uncategorized'   
    
    def check_if_activity_is_already_uncategorized(self, activity):
        with open('uncategorized_activities.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[1] == activity:
                    return True
        return False
    def recheck_uncategorized(self):
        fetched_data = self.fetch_data_csv()
        check_data = self.recheck_uncategorized_activities()

        for key, value in check_data.items():
            if key == fetched_data[0]:
                fetched_data[0] += value
            elif key == fetched_data[1]:
                fetched_data[1] += value
        return fetched_data

    def recheck_uncategorized_activities(self):
        work_activites_count = 0
        entertainment_activities_count = 0
        uncategorized_activities = {}
        rows_to_delete = []

        with open('uncategorized_activities.csv', mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                
                for work_activites in self.work_activities:
                    if work_activites.lower() in row[1].lower():
                        work_activites_count+=1
                        continue
                for entertainment_activities in self.entertainment_activities:
                    if entertainment_activities.lower() in row[1].lower():
                        entertainment_activities_count+=1
                        continue
                uncategorized_activities[row[0]] = row[1]
        print(f'work_activities_count: {work_activites_count}')
        os.remove('uncategorized_activities.csv')
        with open('uncategorized_activities.csv', mode='w', newline='') as uncategorized_file:
            uncategorized_writer = csv.writer(uncategorized_file)
            for key, value in uncategorized_activities.items():
                uncategorized_writer.writerow([key, value])
        return work_activites_count, entertainment_activities_count
   
    def calculate_activities_time_in_minutes(self, activity_count):
        return activity_count * 5 / 60 
    
    def is_user_afk(self, threshold=10):
        # Get the tick count when the last input event was recorded
        last_input_tick = LASTINPUTINFO.get_last_input()
        # Get the current tick count
        current_tick = windll.kernel32.GetTickCount()
        # Calculate the difference in milliseconds
        elapsed = (current_tick - last_input_tick) / 1000.0
        # Check if the user has been AFK longer than the threshold
        return elapsed > threshold
    
class LASTINPUTINFO(Structure):
    _fields_ = [("cbSize", c_uint), ("dwTime", c_uint)]

    def get_last_input():
        lii = LASTINPUTINFO()
        lii.cbSize = sizeof(LASTINPUTINFO)
        windll.user32.GetLastInputInfo(ctypes.byref(lii))
        return lii.dwTime