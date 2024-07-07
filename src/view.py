from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QTabWidget, QLabel,QHBoxLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt, pyqtSignal

class MainWindow(QMainWindow):
    about_to_close = pyqtSignal()
    def __init__(self):
        super().__init__()
        # set the title of the main window
        self.setWindowTitle('Productivity App')
        # create a QTabWidget
        self.tab_widget = QTabWidget()
        # set the tab widget as the central widget
        self.setCentralWidget(self.tab_widget)
        # create a QWidget to hold the buttons
        self.buttons_widget = QWidget()
        self.pie_chart_widget = QWidget()

        self.create_buttons()
        self.setup_pie_chart()
        # add the buttons widget to the tab widget
        self.tab_widget.addTab(self.buttons_widget, 'Main')
        self.tab_widget.addTab(self.pie_chart_widget, 'Pie Chart')

        self.is_tracking = False
        self.update_status_indicator()

    def create_buttons(self):
        #create a QPushbutton widget
        self.start_button = QPushButton('Start Tracking')
        self.stop_button = QPushButton('Stop Tracking')
        self.submit_to_db_button = QPushButton('Submit to DB')
        self.visualize_button = QPushButton('Visualize Data')
        self.recheck_uncategorized_button = QPushButton('Recheck Uncategorized')

        # create a QLabel widget to display the status of tracking
        self.status_indicator = QLabel(self)
        self.status_indicator.setFixedSize(20,20)
        # create a QHBoxLayout to arrange widgets horizontally
        start_layout = QHBoxLayout()
        start_layout.addWidget(self.status_indicator)
        start_layout.addWidget(self.start_button)
        # Create a QVBoxLayout to arrange widgets vertically
        layout = QVBoxLayout()
        layout.addLayout(start_layout)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.submit_to_db_button)
        layout.addWidget(self.recheck_uncategorized_button)
        layout.addWidget(self.visualize_button)
        # create a QWidget and set it as the central widget of the main window
        widget = QWidget()
        widget.setLayout(layout)
        self.buttons_widget.setLayout(layout)


    def setup_pie_chart(self, data=None):
        # create a QPieSeries object
        series = QPieSeries()
        # checks if data exists
        if data is None:
            return
        # iterate over the data and add it to the series
        for category , value in data.items():
            series.append(category, value)
            # set the label of the last slice to display the category and value
            last_slice = series.slices()[-1]
            last_slice.setLabelVisible(True)
            last_slice.setLabel(f"{category}, {value} minutes")
        # create a QChart object and set the series
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle('Activity Distribution')
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        # create a QChartView object and set the chart
        chart_view = QChartView(chart)
        layout = QVBoxLayout()
        layout.addWidget(chart_view)
        self.pie_chart_widget.setLayout(layout)

    def update_status_indicator(self):
        if self.is_tracking:
            self.status_indicator.setStyleSheet('background-color: green; border-radius: 10px')
        else:
            self.status_indicator.setStyleSheet('background-color: red; border-radius: 10px')
    
    def start_tracking(self):
        self.is_tracking = True
        self.update_status_indicator()
    
    def stop_tracking(self):
        self.is_tracking = False
        self.update_status_indicator()

    def closeEvent(self, event):
        self.about_to_close.emit()
        super().closeEvent(event)


    
