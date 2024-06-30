from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QDialog, QTabWidget
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

class MainWindow(QMainWindow):
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

    def create_buttons(self):


        #create a QPushbutton widget
        self.start_button = QPushButton('Start Tracking')
        self.stop_button = QPushButton('Stop Tracking')
        self.submit_to_db_button = QPushButton('Submit to DB')
        self.visualize_button = QPushButton('Visualize Data')

        # Create a QVBoxLayout to arrange widgets vertically
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.submit_to_db_button)
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




    
