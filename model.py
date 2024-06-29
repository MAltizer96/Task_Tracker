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
            connection.commit()
            connection.close()
            

    def check_type_of_activity(self, activity):
        # arrays for activities        
        work_activities = ['Visual Studio Code','StB_Static']
        entertainment_activities = ['youtube', 'netflix', 'prime video', 'disney+', 'spotify']
        # loops through the arrays and checks if the activity is in the arrays
        for work in work_activities:
            if work.lower() in activity.lower():
                return 'work'
            
        for entertainment in entertainment_activities:
            if entertainment.lower() in activity.lower():
                return 'entertainment'
        
        return 'uncategorized'