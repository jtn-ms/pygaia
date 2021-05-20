# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 00:02:12 2018
@author: junying
"""

import sys

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout,QGridLayout,QPushButton,QSizePolicy,QSplitter#, QCheckBox
from PyQt5.QtWidgets import QComboBox,QDialog, QLabel,QLineEdit#, QTableWidget,QStackedWidget
from PyQt5.QtWidgets import QDateTimeEdit,QDialogButtonBox
from PyQt5.QtGui import QIcon,QFont,QKeySequence#,QVBoxLayout,QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread
from PyQt5.Qt import QDateTime
from PyQt5.QtWidgets import QWidget,QTabWidget
from PyQt5.QtGui import QImage,QPixmap

import os

class Tab(QTabWidget):
    keys = ["rest-server","chain-id","default-gas","default-fee","father-addr","child-key-path"]
    butts = ["载入","归集","分析","保存"]
    def __init__(self, parent = None):
        super(Tab, self).__init__(parent)
        self.isfinished = False
        self.initialize()

    def act_accumulate(self):
        pass
    
    def act_analyze(self):
        pass
    
    def act_fileopen(self):
        filepath,extensions = QFileDialog.getOpenFileName(self, r'File Open','',"configuration file (*.json)")

    def act_filesave(self):
        pass
         
    def closeEvent(self, event):
        
        if self.isfinished:
            self.deleteLater()
            return
        
        reply = QMessageBox.question(self, 'warning',
                                     "Are you sure to quit dialog?", QMessageBox.Yes | 
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.deleteLater()
            event.accept()
        else:
            event.ignore()
            
    def generateTab(self,filepath):
        tag = "sscq" if "sscq" in filepath else "usdp"
        from handy.jzon.handler import load
        config = load(filepath)
        ### tab.sscq
        labels,edits,buttons = {},{},{}
        for key in self.keys:
            label = QLabel(self) if not tag in self.labels.keys() else self.labels[tag][key];
            label.setText("%s: "%key);labels[key] = label
            edit = QLineEdit(self)if not tag in self.edits.keys() else self.edits[tag][key]
            edit.setText("%s"%config[key]) if config.keys() else edit.setText("");edits[key] = edit
        self.labels[tag]=labels
        self.edits[tag]=edits
        if tag not in self.buttons.keys():
            for but in self.butts:
                button = QPushButton(self);button.setText(but);buttons[but] = button
            buttons["载入"].released.connect(self.act_fileopen)
            buttons["归集"].released.connect(self.act_accumulate)
            buttons["分析"].released.connect(self.act_analyze)
            buttons["保存"].released.connect(self.act_analyze)
            self.buttons[tag]=buttons
        ### layout
        gridlayout = QGridLayout()
        for key in self.keys:
            gridlayout.addWidget(labels[key], self.keys.index(key), 0)
            gridlayout.addWidget(edits[key], self.keys.index(key), 1)
        for but in self.butts:
            gridlayout.addWidget(buttons[but], self.butts.index(but), 2)
        return gridlayout    
        
    def initialize(self):
        self.labels,self.edits,self.buttons,self.actions = {},{},{},{}
        ## tabs
        tab_sscq = QWidget()
        tab_usdp = QWidget()

        tab_sscq.setLayout(self.generateTab("config/sscq.json"))
        tab_usdp.setLayout(self.generateTab("config/usdp.json"))
        
        ### mainframe 
        self.resize(500,350)
        self.setMinimumSize(500,350)
        self.setMaximumSize(500,350)
        self.addTab(tab_sscq,"SSCQ")
        self.addTab(tab_usdp,"USDP")
        self.setWindowTitle('归集')
        self.show()

    def resizeEvent(self, event):
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.update()
        return super(Tab, self).resizeEvent(event)

if __name__ == "__main__":
    # Create an PyQT5 application object.
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    ex = Tab()
    sys.exit(app.exec_())