import os
import csv
import time 
import pygetwindow as gw
import sqlite3

class ProductiveModel:
    def __init__(self):
        self.is_tracking = False


    def start_tracking(self):
        self.is_tracking = True                            
        while self.is_tracking:
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

    def write_daily_activity_to_db(self):
        # open csv to read
        with open('activity_log.csv', mode='r') as file:
            csv_reader = csv.reader(file)

            # create a connection to the database
            connection = sqlite3.connect('activity_log.db')
            cursor = connection.cursor()
            # create db is needed
            cursor.execute('CREATE TABLE IF NOT EXISTS activity_log (type TEXT, count INTEGER)')
            # reads the csv file and checks the type of activity
            for column in csv_reader:   
                # check the type of activity             
                activity_type = self.check_type_of_activity(column[1])     
                if activity_type == 'uncategorized':                     
                    with open('uncategorized_activities.csv', mode='a', newline='') as uncategorized_file:
                        uncategorized_writer = csv.writer(uncategorized_file)
                        uncategorized_writer.writerow([column[0], column[1]])                      
                    continue
                # check if the activity is in the db       
                cursor.execute('SELECT * FROM activity_log WHERE type = ?', (activity_type,))
                result = cursor.fetchone()
                if result:
                    # if the activity is in the db, update the count
                    cursor.execute('UPDATE activity_log SET count = count + 1 WHERE type = ?', (activity_type,))
                else:
                    # if the activity is not in the db, insert the activity
                    cursor.execute('INSERT INTO activity_log VALUES (?, ?)', (activity_type, 1))
            # commit and close the connection
            print('done')
            connection.commit()
            connection.close()
            # delete the csv file
        os.remove('activity_log.csv')

    def check_type_of_activity(self, activity):
        # arrays for activities        
        work_activities = ['Visual Studio Code']
        entertainment_activities = ['youtube', 'netflix', 'prime video', 'disney+', 'spotify', 'World of Warcraft', 'battle.net', 'steam', 'stb_static']
        # loops through the arrays and checks if the activity is in the arrays
        for work in work_activities:
            if work.lower() in activity.lower():
                return 'work'
            
        for entertainment in entertainment_activities:
            if entertainment.lower() in activity.lower():
                return 'entertainment'
        
        return 'uncategorized'
    
    def fetch_data(self):
        # open connection to the db
        connection = sqlite3.connect('activity_log.db')
        cursor = connection.cursor()
        # get the count of work and entertainment activities
        work_activities_count = cursor.execute('SELECT count FROM activity_log WHERE type = "work"').fetchone()
        entertainment_activities_count = cursor.execute('SELECT count FROM activity_log WHERE type = "entertainment"').fetchone()
        # calculate the time spent on work and entertainment activities in minutes
        work_activity_time = self.calculate_activities_time_in_minutes(work_activities_count[0])       
        entertainment_activity_time = self.calculate_activities_time_in_minutes(entertainment_activities_count[0])
        return {'work': work_activity_time, 'entertainment': entertainment_activity_time}
   
    def calculate_activities_time_in_minutes(self, activity_count):
        return activity_count * 5 / 60 
    