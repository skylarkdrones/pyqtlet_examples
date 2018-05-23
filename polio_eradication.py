'''
This is a simple app that shows how we can control the leaflet map
from PyQt widgets. In this app we will explore how effective the
polio vaccine is, and how humanity can come together and trump all
other national, regional and cultural biases to truly achieve 
something great
'''

import json
import math
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from pyqtlet import L, MapWidget

DATA_PATH = 'data/polio_data.json'
MAX_SIZE = 200

class PolioEradiactor(QWidget):
    def __init__(self, data_path=DATA_PATH):
        super().__init__()
        self.data_path = data_path
        self.data = {}
        self._init_ui()
        self._init_map()
        self._load_data()
        self.show()

    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.mapWidget = MapWidget()
        self.yearLayout = QHBoxLayout()
        self.yearLabel = QLabel()
        self.yearSlider = QSlider(Qt.Horizontal)
        self.yearLayout.addWidget(self.yearLabel)
        self.yearLayout.addWidget(self.yearSlider)
        self.layout.addWidget(self.mapWidget)
        self.layout.addItem(self.yearLayout)
        self.setLayout(self.layout)
        self.yearSlider.valueChanged.connect(self._linkSlider)

    def _init_map(self):
        self.map = L.map(self.mapWidget)
        self.map.setView([0, 0], 1)
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {'noWrap': 'true'}).addTo(self.map)
        self.layerGroup = L.layerGroup()
        self.map.addLayer(self.layerGroup)
        self.yearLayers = {} 
        
    def _load_data(self):
        with open(self.data_path) as data_in:
            self.data = json.load(data_in)
        years = [int(year) for year in next(iter(self.data.values()))['occurences']]
        occurences = [self.data[country]['occurences'][str(year)] for country in self.data for year in years]
        high = max(occurences)
        firstYear, lastYear = min(years), max(years)
        for key in self.data:
            country = self.data[key]
            for year in country['occurences']:
                if not country['occurences'][year]:
                    continue
                num = country['occurences'][year]
                if year not in self.yearLayers:
                    self.yearLayers[year] = []
                coords = [country['coordinates'][1], country['coordinates'][0]]
                yearMarker = L.circleMarker(coords, {'radius': self._getMarkerRadius(num, high)})
                yearMarker.bindPopup('In {year}, {country} has {num} incidents of polio reported'.format(year=year, country=key, num=num))
                self.yearLayers[year].append(yearMarker)
        self.yearSlider.setMinimum(firstYear)
        self.yearSlider.setMaximum(lastYear)
        self.yearLabel.setText(str(firstYear))

    def _getMarkerRadius(self, value, max_occurences):
        # Exponentially show the size of the marker
        power = (1/2)
        return MAX_SIZE * (value**power) / (max_occurences**power) 

    def _linkSlider(self, year):
        self.yearLabel.setText(str(year))
        self.map.runJavaScript('{lg}.clearLayers()'.format(lg=self.layerGroup.jsName))
        for marker in self.yearLayers[str(year)]:
            self.layerGroup.addLayer(marker)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = PolioEradiactor()
    sys.exit(app.exec_())
