import csv
import os
import json
import sys
import time
import pygetwindow as gw

class Database:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.project_root = os.path.dirname(os.path.dirname(sys.executable))
        elif __file__:
            self.project_root = os.path.dirname(os.path.dirname(__file__))

        self.config_path = os.path.join(self.project_root,'config')
        self.data_file_path = os.path.join(self.project_root, 'data')

        self.activity_types_csv_path = os.path.join(self.data_file_path, 'activity_types.csv')
        self.activity_types_db_path = os.path.join(self.data_file_path, 'activity_log_db.csv')
        self.uncategorized_activities_path = os.path.join(self.data_file_path, 'uncategorized_activities.csv')

        self.activity_types_file = os.path.join(self.config_path, 'activity_types.json')
        self.activity_log_file = os.path.join(self.data_file_path, 'activity_log.csv')
        self.activity_log_db_file = os.path.join(self.data_file_path, 'activity_log_db.csv')
        self.uncategorized_activities_file = os.path.join(self.data_file_path, 'uncategorized_activities.csv')

        work_activities, entertainment_activities = self.get_activity_types()
        self.work_activites = work_activities
        self.entertainment_activities = entertainment_activities   

    def write_daily_activity_to_csv(self):
        # get the active window
        active_window = gw.getActiveWindow().title
        # get the current time
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # open csv file to append
        with open(self.activity_log_file, mode='a', newline='') as file:
            # create a csv writer and write the timestamp and active window
            writer = csv.writer(file)                    
            writer.writerow([timestamp, active_window])
        return True

    def get_activity_types(self):
        with open(self.activity_types_file, 'r') as file:
            data = json.load(file)
            self.work_activites = data['work']
            self.entertainment_activities = data['entertainment']

        return self.work_activites, self.entertainment_activities
    
    def write_daily_activity_to_db_csv(self):
        # create a dictionary to store the activity log data
        activity_log_db = {}
        try:
            # open the db file to read
            with open(self.activity_types_db_path, mode='r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                # read the db file and store the data in the dictionary
                for row in csv_reader:
                    # add the data to the dictionary with the type as the key and the count as the value
                    activity_log_db [row[0]] = int(row[1])
        except FileNotFoundError:
            pass

        with open (self.activity_log_file, mode='r') as file:
            csv_reader = csv.reader(file)  
            # read the csv file and check the type of activity          
            for column in csv_reader:
                # check the type of activity
                activity_type = self.check_type_of_activity(column[1])
                if activity_type == 'uncategorized':
                    with open(self.uncategorized_activities_path, mode='a', newline='') as uncategorized_file:
                        uncategorized_writer = csv.writer(uncategorized_file)
                        uncategorized_writer.writerow([column[0], column[1]])                      
                    continue
                # check if the activity is in the dictionary
                if activity_type in activity_log_db:
                    activity_log_db[activity_type] += 1
                # if the activity is not in the dictionary, add it
                else:
                    activity_log_db[activity_type] = 1
        
        with open (self.activity_types_db_path, mode='w', newline='') as file:
            db_writer = csv.writer(file)
            # write the header
            db_writer.writerow(['type', 'count'])

            for activity_type, count in activity_log_db.items():
                db_writer.writerow([activity_type, count])
        # delete the csv file
        os.remove(self.activity_log_file)

    def fetch_data_csv(self):
        # create a dictionary to store the data
        data = {}
        try:
            # open the db file to read
            with open(self.activity_log_db_file, mode='r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                # read the db file and store the data in the dictionary
                for row in csv_reader:
                    # add the data to the dictionary with the type as the key and the count as the value
                    data[row[0]] = int(row[1])
        except FileNotFoundError:
            pass
        return data
    
    def check_if_activity_is_already_uncategorized(self, activity):
        with open(self.uncategorized_activities_file, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[1] == activity:
                    return True
        return False
    
    def recheck_uncategorized_activities(self):
        work_activities_count  = 0
        entertainment_activities_count = 0
        uncategorized_activities = {}
        rows_to_delete = []
        with open(self.uncategorized_activities_path, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                found = False
                for work_activites in self.work_activites:
                    if work_activites.lower() in row[1].lower():
                        work_activities_count+=1
                        found = True
                        break
                for entertainment_activities in self.entertainment_activities:
                    if entertainment_activities.lower() in row[1].lower():
                        entertainment_activities_count+=1
                        found = True
                        break
                if not found:
                    uncategorized_activities[row[0]] = row[1]
        os.remove(self.uncategorized_activities_path)
        with open(self.uncategorized_activities_path, mode='w', newline='') as uncategorized_file:
            uncategorized_writer = csv.writer(uncategorized_file)
            for key, value in uncategorized_activities.items():
                uncategorized_writer.writerow([key, value])
        
        return {'work':work_activities_count , 'entertainment':entertainment_activities_count}

    def check_type_of_activity(self, activity):
        # loops through the arrays and checks if the activity is in the arrays
        for work in self.work_activites:
            if work.lower() in activity.lower():
                return 'work'
            
        for entertainment in self.entertainment_activities:
            if entertainment.lower() in activity.lower():
                return 'entertainment'
        
        return 'uncategorized'   