import os
import csv
import time 
import pygetwindow as gw
import json
import ctypes
import time
import sys
from ctypes import Structure, c_uint, sizeof, windll
from pathlib import Path
from db import Database as db

class ProductiveModel:
    def __init__(self):
        self.db = db()


        work_activities, entertainment_activities = self.db.get_activity_types()
        self.work_activites = work_activities
        self.entertainment_activities = entertainment_activities      
        
        print(f'work_activities {self.work_activites}')
        print(f'entertainment_activities {self.entertainment_activities}')
        self.is_tracking = False

    def start_tracking(self):
        self.is_tracking = True                            
        while self.is_tracking:
            if self.is_user_afk():
                print('User is AFK')
                continue
            try:
                self.db.write_daily_activity_to_csv()
            except Exception:
                pass
            # sleep for 5 seconds
            time.sleep(5)

    def stop_tracking(self):
        self.is_tracking = False
    
    def recheck_uncategorized(self):
        fetched_data = self.fetch_data_csv()
        check_data = self.db.recheck_uncategorized_activities()
        print(f'check_data : {check_data}')
        for key, value in check_data.items():
            if key in fetched_data:
                fetched_data[key] += value
        return fetched_data
   
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

    def write_daily_activity_to_db_csv(self):
        self.db.write_to_db()

    def fetch_data_csv(self):
        return self.db.fetch_data_csv()

class LASTINPUTINFO(Structure):
    _fields_ = [("cbSize", c_uint), ("dwTime", c_uint)]

    def get_last_input():
        lii = LASTINPUTINFO()
        lii.cbSize = sizeof(LASTINPUTINFO)
        windll.user32.GetLastInputInfo(ctypes.byref(lii))
        return lii.dwTime