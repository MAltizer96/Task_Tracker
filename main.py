from PyQt5.QtWidgets import QApplication
import threading

from view import MainWindow
from model import ProductiveModel

class ProductivityApp:
    def __init__(self):
        self.model = ProductiveModel()
        self.view = MainWindow()

        # Connect signals and slots
        self.view.start_button.clicked.connect(self.start_tracking)
        self.view.stop_button.clicked.connect(self.stop_tracking)
        self.view.submit_to_db_button.clicked.connect(self.submit_to_db)
        self.view.visualize_button.clicked.connect(self.create_pie_chart)

    def start_tracking(self):
        if not self.model.is_tracking:
            self.tracking_thread = threading.Thread(target=self.model.start_tracking)
            self.tracking_thread.start()

    def stop_tracking(self):
        self.model.stop_tracking()

    def submit_to_db(self):
        self.model.write_daily_activity_to_db()
    
    def create_pie_chart(self):
        data = self.model.fetch_data()
        print(f'data: {data}')
        self.view.setup_pie_chart(data)

app = QApplication([])
productivity_app = ProductivityApp()
productivity_app.view.show()
app.exec_()