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
    
    def write_to_db(self):
        # create a dictionary to store the activity log data        
        activity_log_db_string = self.fetch_data_csv(self.activity_log_db_file)
        activity_log_db  = {key: int(value) for key, value in activity_log_db_string.items()}

        activity_log = self.fetch_data_csv(self.activity_log_file)

        uncategorized_file_string = self.fetch_data_csv(self.uncategorized_activities_file)
        uncategorized_file  = {key: int(value) for key, value in uncategorized_file_string.items()}

        print("activity_log_db: ", activity_log_db)
        print("activity_log: ", activity_log)
        print("uncategorized_file: ", uncategorized_file)

        for row in activity_log.values():
            print(row)
            current_type = self.check_type_of_activity(row)
            if current_type == 'uncategorized':
                print("uncategorized")
                if uncategorized_file:
                    for uncategorized_row in uncategorized_file:
                        if row == uncategorized_row:
                            print("uncategorized_row: ", uncategorized_file[uncategorized_row])
                            uncategorized_file[uncategorized_row] = uncategorized_file[uncategorized_row] + 1
                            break
                else:
                    uncategorized_file[row] = 1
                    continue
            print(f"current_type: { current_type}, row: {row} ")                      

            if activity_log_db:
                for db_row in activity_log_db:
                    print("db_row: ", db_row)
                    if current_type == db_row:
                        activity_log_db[db_row] = activity_log_db[db_row] + 1
                        break
                    elif db_row == (activity_log_db):
                        activity_log_db[current_type] = 1
                        break
            else:
                activity_log_db[current_type] = 1

        # print("activity_log_db: ", activity_log_db)
        # print("activity_log: ", activity_log)
        # print("uncategorized_file: ", uncategorized_file)
 


        try:
            os.remove(self.activity_log_file)
        except FileNotFoundError:
            print("db File not found")
            pass

        self.write_to_csv(activity_log_db, self.activity_log_db_file, mode='w')
        self.write_to_csv(uncategorized_file, self.uncategorized_activities_path, mode='w')
        return True

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
            # open the db file to read
            with open(file, mode='r') as file:
                csv_reader = csv.reader(file)
                # read the db file and store the data in the dictionary
                for row in csv_reader:
                    # add the data to the dictionary with the type as the key and the count as the value
                    data[row[0]] = row[1]
        except FileNotFoundError:
            pass
        return data