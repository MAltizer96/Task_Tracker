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

        self.uncategorized_activities_path = os.path.join(self.data_file_path, 'uncategorized_activities.csv')

        self.activity_types_file = os.path.join(self.config_path, 'activity_types.json')
        self.activity_log_file = os.path.join(self.data_file_path, 'activity_log.csv')
        self.activity_log_db_file = os.path.join(self.data_file_path, 'activity_log_db.csv')
        self.uncategorized_activities_file = os.path.join(self.data_file_path, 'uncategorized_activities.csv')

        work_activities, entertainment_activities = self.get_activity_types()

        for activity in work_activities:
            activity = activity.lower()

        for activity in entertainment_activities:
            activity = activity.lower()
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
        # gets the activity types from the json file
        with open(self.activity_types_file, 'r') as file:
            data = json.load(file)
        # convert the data to lowercase
        for key in data:
            data[key] = [item.lower() for item in data[key]]
        # create the work and entertainment activities lists and return them
        self.work_activites = data['work']
        self.entertainment_activities = data['entertainment']
        return self.work_activites, self.entertainment_activities
    
    def write_to_db(self):
        # create dicts to store the data      
        activity_log_db_string = self.fetch_data_csv(self.activity_log_db_file)
        activity_log_db  = {key: int(value) for key, value in activity_log_db_string.items()}

        activity_log = self.fetch_data_csv(self.activity_log_file)

        uncategorized_file_string = self.fetch_data_csv(self.uncategorized_activities_file)
        uncategorized_file  = {key: int(value) for key, value in uncategorized_file_string.items()}

        # loop through the activity log data values
        for row in activity_log.values():
            # get the type of activity
            current_type = self.check_type_of_activity(row)
            if current_type == 'uncategorized':
                # check if the activity is already in the uncategorized dict if it is loop through the dict
                if row in uncategorized_file:
                    for uncategorized_row in uncategorized_file:
                        if row == uncategorized_row:
                            # increment the value of the activity
                            uncategorized_file[uncategorized_row] = uncategorized_file[uncategorized_row] + 1
                            continue                
                else:
                    # if the activity is not in the uncategorized dict, add it to the dict
                    uncategorized_file[row] = 1
                    continue
                continue
            # not uncategorized, check if the activity is in the activity log db
            if activity_log_db:
                # if in the database dict, loop through the dict, increment the value of the activity
                if current_type in activity_log_db:
                    for db_row in activity_log_db:

                        if current_type == db_row:
                            activity_log_db[db_row] = activity_log_db[db_row] + 1
                            break
                else:
                # if not in the database dict, add the activity to the dict
                    activity_log_db[current_type] = 1
            else:
                # if the database dict is empty, add the activity to the dict
                activity_log_db[current_type] = 1
        # write the data to the csv files and remove the activity log file
        self.write_to_csv(activity_log_db, self.activity_log_db_file, mode='w')
        self.write_to_csv(uncategorized_file, self.uncategorized_activities_path, mode='w')
        os.remove(self.activity_log_file)
        return True

    def check_if_activity_is_already_uncategorized(self, activity):
        with open(self.uncategorized_activities_file, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row[1] == activity:
                    return True
        return False
    
    def recheck_uncategorized_activities(self):
        # get the data from current uncategorized activities
        uncategorized_activities = self.fetch_data_csv(self.uncategorized_activities_path)

        # create a dictionary to store the work and entertainment activities
        db = self.fetch_data_csv(self.activity_log_db_file)
        print("db: ", db)
        # loop through the uncategorized activities
        to_remove = []
        for activity in uncategorized_activities:
            current_type = self.check_type_of_activity(activity)
            # if not uncategorized, add it to the dictionary and remove it from the uncategorized activities
            if current_type != 'uncategorized':
                db[current_type] = int(db[current_type]) + int(uncategorized_activities[activity])
                to_remove.append(activity)

        for activity in to_remove:            
            if activity in uncategorized_activities:
                del uncategorized_activities[activity]
                continue
        
        self.write_to_csv(db, self.activity_log_db_file, mode='w')
        self.write_to_csv(uncategorized_activities, self.uncategorized_activities_path, mode='w')
        return True

    def check_type_of_activity(self, activity):
        # Convert the activity to lowercase
        activity_lower = activity.lower()             

        # check for the type of activity in the list of activities
        if any(word in activity_lower for word in self.work_activites):
            return 'work'        
        elif any(word in activity_lower for word in self.entertainment_activities):
            return 'entertainment'        
        else:
            return 'uncategorized'

    def write_to_csv(self, data, file_path, mode = 'w'):
        try:
            with open(file_path, mode = mode, newline='') as file:
                writer = csv.writer(file)
                for key, value in data.items():
                    writer.writerow([key, value])
        except FileNotFoundError:
            return "File not found"

    def read_from_csv(self, file):
        data = {}
        with open(file, mode='r') as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)
        return data
    
    def fetch_data_csv(self, file):
        # create a dictionary to store the data
        data = {}
        try:
            # open the db file to read, getting data from csv
            with open(file, mode='r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    data[row[0]] = row[1]
        except FileNotFoundError:
            pass
        return data
    
    def get_db_file(self):
        return self.activity_log_db_file