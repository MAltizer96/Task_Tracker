from PyQt5.QtWidgets import QMainWindow, QComboBox, QVBoxLayout, QWidget, QPushButton
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Productivity App')
        self.create_buttons()

    def create_buttons(self):


        #create a QPushbutton widget
        self.start_button = QPushButton('Start Tracking')
        self.stop_button = QPushButton('Stop Tracking')
        self.submit_to_db_button = QPushButton('Submit to DB')

        # Create a QVBoxLayout to arrange widgets vertically
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.submit_to_db_button)

        # create a QWidget and set it as the central widget of the main window
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
