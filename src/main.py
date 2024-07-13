from PyQt5.QtWidgets import QApplication, QMainWindow
import threading

from view import MainWindow
from model import ProductiveModel

class ProductivityApp():
    def __init__(self):
        self.model = ProductiveModel()
        self.view = MainWindow()
        # Connect the about_to_close signal to the on_app_exit slot        
        self.view.about_to_close.connect(self.on_app_exit)

        # Connect signals and slots
        self.view.start_button.clicked.connect(self.start_tracking)
        self.view.stop_button.clicked.connect(self.stop_tracking)
        self.view.submit_to_db_button.clicked.connect(self.submit_to_db)
        self.view.visualize_button.clicked.connect(self.create_pie_chart)
        self.view.recheck_uncategorized_button.clicked.connect(self.recheck_uncategorized)

    def start_tracking(self):
        if not self.model.is_tracking:
            self.tracking_thread = threading.Thread(target=self.model.start_tracking)
            self.tracking_thread.start()
            self.view.start_tracking()

    def stop_tracking(self):
        self.model.stop_tracking()
        self.view.stop_tracking()

    def submit_to_db(self):
        self.model.write_daily_activity_to_db_csv()
    
    def create_pie_chart(self):
        data = self.model.fetch_db_csv()
        self.view.setup_pie_chart(data)

    def recheck_uncategorized(self):
        self.model.recheck_uncategorized()

    def on_app_exit(self):
        print('stopping tracking')
        self.model.stop_tracking()
        if self.model.is_tracking:
            self.tracking_thread.join()


app = QApplication([])
productivity_app = ProductivityApp()
productivity_app.view.show()
app.exec_()