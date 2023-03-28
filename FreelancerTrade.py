# -*- coding: utf-8 -*-

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt5 import uic
from PyQt5.QtGui import QKeySequence
import sys


file = "Freelancer Traderoutes.xlsx"

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Setup important varibales
        self.systemFrom = "Bering"
        self.systemTo = "Bering"

        # Load data
        self.df = pd.read_excel(file)

        # Load the ui file
        uic.loadUi("FreelancerTrade.ui", self)

        # Show the app
        self.show()
        self.status.setText("" )

        # Define event handlers
        self.comboBox1a.currentTextChanged.connect(self.onSystemFromSelected)
        self.comboBox2a.currentTextChanged.connect(self.onSystemToSelected)
        self.comboBox1b.currentTextChanged.connect(self.onLocationFromSelected)
        self.comboBox2b.currentTextChanged.connect(self.onLocationToSelected)
        self.toolButton1.clicked.connect(self.onExchange)

        # Setup tables
        self.setupTable(self.table1)
        self.setupTable(self.table2,["Profit"])

        # Populate combo boxes
        systems = list(self.df.groupby(['System']).count().index)
        self.comboBox1a.addItems(systems)
        self.comboBox2a.addItems(systems)

    def onExchange(self):
        locationFrom = self.comboBox1b.currentText()
        locationTo = self.comboBox2b.currentText()
        self.systemFrom, self.systemTo = self.systemTo, self.systemFrom
        self.onSystemFromSelected()
        self.onSystemToSelected
        self.comboBox1b.setCurrentText(locationTo)
        self.comboBox2b.setCurrentText(locationFrom)

    def setupTable(self, t, extraColumns=[]):
        columns = ['Good','Location','Price']
        t.setColumnCount(3+len(extraColumns))
        t.setHorizontalHeaderLabels(columns+extraColumns)
        t.show()

    def loadTable(self, t: QTableWidget, system, location, action, computeProfit=False):
        def addItem(t,label,r,c, maxValue=0.0):
            newitem = QTableWidgetItem(label)
            if label == "%.0f $" % maxValue:
                newitem.setBackground(QtGui.QColor(255,255,153))
            t.setItem(r,c,newitem)

        if location == "All":
            df = self.df.query("System == '%s' and Art == '%s'" % (system,action) ).set_index("Ware")
        else:
            df = self.df.query("System == '%s' and Standort == '%s' and Art == '%s'" % (system,location,action) ).set_index("Ware")
        df["Preis je Stk"] = df["Preis je Stk"].apply(lambda x: x[:-2])
        df["Preis je Stk"] = df["Preis je Stk"].astype(float)

        if computeProfit:
            df = pd.merge(self.dfFrom, df, how="right", left_index=True, right_index=True )
            df["Profit"] = df["Preis je Stk_y"] - df["Preis je Stk_x"]
            df = df.drop(["System_x","Standort_x","Art_x","Preis je Stk_x"], axis=1).sort_values(by=["Profit"], ascending=False)
            maxValue = df["Profit"].max()

        t.clearContents()
        t.setRowCount(len(df.index))
        for i,r in enumerate(df.itertuples()):
            addItem(t,r[0],i,0)
            addItem(t,r[2],i,1)
            addItem(t,"%.0f $" % r[4],i,2)
            if computeProfit:
                if str(r[5]) == "nan":
                    addItem(t,"",i,3)
                else:
                    addItem(t,"%.0f $" % r[5],i,3,maxValue)
        t.resizeColumnsToContents()

        return df

    def loadLocationsComboBox(self, c, filter):
        l = list(self.df.query("System == '%s'" % filter).groupby(['Standort']).count().index)
        c.addItems(["All"]+l)
        return l

    def onSystemFromSelected(self):
        self.comboBox1b.clear()
        self.systemFrom = self.comboBox1a.currentText()
        locationsFrom = self.loadLocationsComboBox(self.comboBox1b,self.systemFrom)
        self.comboBox2a.setCurrentText(self.systemFrom)
        self.onLocationFromSelected()

    def onSystemToSelected(self):
        self.comboBox2b.clear()
        self.systemTo = self.comboBox2a.currentText()
        locationsto = self.loadLocationsComboBox(self.comboBox2b,self.systemTo)
        self.onLocationToSelected()

    def onLocationFromSelected(self):
        self.dfFrom = self.loadTable(self.table1,self.systemFrom,self.comboBox1b.currentText(),'verkauft')

    def onLocationToSelected(self):
        self.loadTable(self.table2,self.systemTo,self.comboBox2b.currentText(),'kauft',computeProfit=True)


app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()