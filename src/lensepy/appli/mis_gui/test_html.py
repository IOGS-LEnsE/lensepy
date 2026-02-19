import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView

import os
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-direct-composition"

app = QApplication(sys.argv)
view = QWebEngineView()
view.setUrl(QUrl("https://lense.institutoptique.fr/"))
view.show()
sys.exit(app.exec())
