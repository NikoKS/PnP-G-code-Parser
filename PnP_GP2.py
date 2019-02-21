#This software is used to implement a pick and place g-code from a regular
#gcode generated by Slic3R version 13.1
#created by Nikolas Setiawan

import os
import numpy as np
from sys import platform
from PyQt5.QtWidgets import (QApplication, QTextEdit, QLabel, QTabWidget, QComboBox,
                             QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton,
                             QFormLayout, QRadioButton, QTableWidget, QFrame,
                             QFileDialog, QMessageBox, QTableWidgetItem)
from PyQt5.QtGui import *

Tool_Change_Gcode = "\n\
G0 Z[height]            ;lower bed 1cm\n\
M721 I1 T[current_head] ;unprime current head\n\
G4 P1000                ;delay 1s\n\
M721 I1 T[current_head] ;unprime current head\n\
G4 P1000                ;delay 1s\n"

Tool_Change_Gcode2 = "\n\
M722 I1 T[current_head] ;prime current head\n\
G4 P1000                ;delay 1s\n\
M722 I1 T[current_head] ;prime current head\n\
G4 P1000                ;delay 1s\n"

Pick_Gcode = "\n\
G0 Z[height]            ;lower bed 1cm\n\
G1 X[pick_X] Y[pick_Y]  ;Go to picking tray location\n\
G1 Z[tray_Z]            ;bed up to pick up\n\
G4 P500                 ;Wait half second\n\
M106 S100 T[PnP_head]   ;Turn On vacuum \n\
G4 P1500                ;Wait another 1.5 s\n\
G1 Z[height]            ;lower bed\n\
G4 P500                 ;another delay\n\
G1 X[place_X] Y[place_Y];Go to place location\n\
G4 P500                 ;Delay half second\n\
G1 Z[place_Z]           ;Place item\n\
G4 P500                 ;Delay\n\
M722 I1 T[PnP_head]     ;Push Item\n\
G4 P3000                ;Delay\n\
M107 T[PnP_head]        ;Turn off vacuum\n\
G4 P500                 ;Delay\n\
M721 I1 T[PnP_head]     ;unprime current head\n\
G4 P2000                ;delay 1s\n"

Pick_Gcode_S = "\n\
G0 Z[height]            ;lower bed 1cm\n\
G1 X[pick_X] Y[pick_Y]  ;Go to picking tray location\n\
G1 Z[tray_Z]            ;bed up to pick up\n\
G4 P500                 ;Wait half second\n\
M106 S100 T[PnP_head]   ;Turn On vacuum \n\
G4 P1500                ;Wait another 1.5 s\n\
G1 Z[height]            ;lower bed\n\
G4 P500                 ;another delay\n\
G1 X[place_X] Y[place_Y];Go to place location\n\
G4 P500                 ;Delay half second\n\
G1 Z[place_Z]           ;Place item\n\
G4 P500                 ;Delay\n\
M107 T[PnP_head]        ;Turn off vacuum\n\
G4 P2000                ;delay 1s\n"

keyword = ';Do PnP Stuff'

class window(QWidget):
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        #Declaring Widgets
        subTFont = QFont("Arial",20,QFont.Bold)
        subTFont.setUnderline(True)

        label1 = QLabel('PnP Tray Setting')
        label1.setFont(subTFont)
        label11= QLabel('G-Code Viewer')
        label11.setFont(subTFont)

        self.Line0 = QLineEdit()    #Number of Trays
        self.Line1 = QLineEdit()    #first X point
        self.Line2 = QLineEdit()    #X Tray offset
        self.Line3 = QLineEdit()    #Y Tray offset
        self.Line4 = QLineEdit()    #Head X Offset
        self.Line5 = QLineEdit()    #Head Y Offset
        self.Line6 = QLineEdit()    #First Y Point
        self.Line7 = QLineEdit()    #Tray X Dimension
        self.Line8 = QLineEdit()    #Tray Y Dimension
        self.Line9 = QLineEdit()    #Tray Item Height
        self.FindString = QLineEdit()   #Search keyword
        self.Line10= QLineEdit()    #Main Head
        self.Line11= QLineEdit()    #PnP Head

        self.But1 = QPushButton('Save Settings')
        self.But1.clicked.connect(self.push1)
        self.But2 = QPushButton('Load Settings')
        self.But2.clicked.connect(self.push2)
        self.But7 = QPushButton('Load G-Code')
        self.But7.clicked.connect(self.push7)
        self.But8 = QPushButton('Save G-Code')
        self.But8.clicked.connect(self.push8)
        self.But9 = QPushButton('Find')
        self.But9.clicked.connect(self.push9)
        self.But10= QPushButton('Reset Search')
        self.But10.clicked.connect(self.push10)
        self.But11= QPushButton('Parse')
        self.But11.clicked.connect(self.push11)
        self.But12= QPushButton('Help')
        self.But12.clicked.connect(self.push12)
        self.ButTray = QPushButton('Add Extra Tray')
        self.ButTray.clicked.connect(self.AddTray)
        self.ButReset = QPushButton('Reset')
        self.ButReset.clicked.connect(self.Reset)

        self.Rad1 = QRadioButton('Standard')
        self.Rad1.setChecked(1)
        self.Rad2 = QRadioButton('Magnet')

        self.Text1 = QTextEdit()
        self.Cpos = 0

        self.tabs = QTabWidget()
        tab1 = QWidget()
        self.tabs.addTab(tab1, 'Tray 1')
        self.Line = []
        self.Etab = {}

        #Window Layout
        hbox0 = QHBoxLayout()
        hbox0.addWidget(QLabel('Number of Trays'))
        hbox0.addWidget(self.Line0)
        hbox0.addWidget(self.ButTray)
        hbox0.addWidget(self.ButReset)
        hbox0.addStretch()

        fbox1 = QFormLayout()
        fbox1.addRow('Initial X Tray', self.Line1)
        fbox1.addRow('X Tray Offset', self.Line2)
        fbox1.addRow('X Tray Dimension', self.Line7)

        fbox2 = QFormLayout()
        fbox2.addRow('Initial Y Tray', self.Line6)
        fbox2.addRow('Y Tray Offset', self.Line3)
        fbox2.addRow('Y Tray Dimension', self.Line8)

        hbox1 = QHBoxLayout()
        hbox1.addLayout(fbox1)
        hbox1.addLayout(fbox2)

        fbox3 = QFormLayout()
        fbox3.addRow('Head X Offset',self.Line4)
        fbox3.addRow('Main Head Pos',self.Line10)
        fbox3.addRow('Tray Item Height',self.Line9)

        fbox4 = QFormLayout()
        fbox4.addRow('Head Y Offset',self.Line5)
        fbox4.addRow('PNP Hed Pos',self.Line11)

        hbox6 = QHBoxLayout()
        hbox6.addWidget(self.Rad1)
        hbox6.addWidget(self.Rad2)

        vbox1 = QVBoxLayout()
        vbox1.addLayout(fbox4)
        vbox1.addLayout(hbox6)

        hbox2 = QHBoxLayout()
        hbox2.addLayout(fbox3)
        hbox2.addLayout(vbox1)

        tab1.setLayout(hbox1)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.But1)
        hbox3.addWidget(self.But2)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.But11)
        hbox4.addWidget(self.But7)
        hbox4.addWidget(self.But8)

        hbox5 = QHBoxLayout()
        hbox5.addWidget(label11)
        hbox5.addStretch()
        hbox5.addWidget(self.FindString)
        hbox5.addWidget(self.But9)
        hbox5.addWidget(self.But10)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(label1)
        vbox2.addLayout(hbox0)
        vbox2.addWidget(self.tabs)
        vbox2.addStretch()
        vbox2.addLayout(hbox2)
        vbox2.addLayout(hbox3)
        vbox2.addStretch()
        vbox2.addWidget(self.But12)
        vbox2.addStretch()

        vbox9 = QVBoxLayout()
        vbox9.addLayout(hbox5)
        vbox9.addWidget(self.Text1)
        vbox9.addLayout(hbox4)

        FinalBox = QHBoxLayout()
        FinalBox.addLayout(vbox2)
        FinalBox.addLayout(vbox9)

        #vbox 7 = add point, vbox 2 = setting
        self.setLayout(FinalBox)

        #Window Functions
        self.setGeometry(300,300,1600,600)
        self.setWindowTitle('Pick and Place Gcode Parser')
        self.show()

    def isfloat(self,s):
        try:
            float(s)
            return True
        except:
            return False

    def insert_GCode(self,cursor,placePos):
        #Insert PNP Tool Change G-code
        TC = Tool_Change_Gcode.replace('[current_head]', self.Line10.text())
        TC = TC.replace('[height]', str(float(self.height[-1])+10))
        cursor.insertText(TC)

        pos = 0 #counter to be increased for Height list

        #Insert PNP Operation G-Code
        for item in placePos:
            item[0] = round(np.mean(item[0]), 3) + float(self.Line4.text())
            item[1] = round(np.mean(item[1]), 3) + float(self.Line5.text())
            print(item)
            if not self.Line or item[2] > 6:
                disp = 0            #Tray/dispenser number
                xdim = float(self.Line7.text())
                ydim = float(self.Line8.text())
            else:
                disp = item[2] - 3
                xdim = float(self.Line[disp-1][2].text())
                ydim = float(self.Line[disp-1][5].text())

            if self.Rad1.isChecked():
                PG = Pick_Gcode_S.replace('[pick_X]', str(self.dispenser[disp][0]))
            else:
                PG = Pick_Gcode.replace('[pick_X]', str(self.dispenser[disp][0]))
            PG = PG.replace('[pick_Y]', str(self.dispenser[disp][1]))
            PG = PG.replace('[place_X]', str(item[0]))
            PG = PG.replace('[place_Y]', str(item[1]))
            PG = PG.replace('[height]', str(float(self.height[pos])+10))
            PG = PG.replace('[tray_Z]', self.Line9.text())
            PG = PG.replace('[place_Z]', self.height[pos])
            PG = PG.replace('[PnP_head]', self.Line11.text())
            cursor.insertText(PG)
            if self.change[disp] != xdim:
                if disp == 0:
                    self.dispenser[disp][0] += float(self.Line2.text())
                    self.change[disp] += 1
                else:
                    self.dispenser[disp][0] += float(self.Line[disp-1][1].text())
                    self.change[disp] += 1
            else:
                if disp == 0:
                    self.dispenser[disp][0] = float(self.Line1.text()) - self.Xorigin
                    self.dispenser[disp][1] += float(self.Line3.text())
                    self.change[disp] = 1
                else:
                    self.dispenser[disp][0] = float(self.Line[disp-1][2].text()) - self.Xorigin
                    self.dispenseri[disp][1] += float(self.Line[disp-1][4].text())
                    self.changei[disp] = 1
            pos += 1

        TC2 = Tool_Change_Gcode2.replace('[current_head]', self.Line10.text())
        cursor.insertText(TC2)
        print('finnished adding G-code')

    def Reset(self):
        Lines = [self.Line1,self.Line2,self.Line3,self.Line4,self.Line5,self.Line6,
                self.Line7,self.Line8,self.Line9,self.Line10,self.Line11]
        for item in Lines:
            item.setText('')
        self.Line0.setText('')
        self.updatesEnabled = False
        for item in self.Etab:
            self.tabs.removeTab(1)
        self.Line = []
        self.Etab = {}
        self.updatesEnabled = True

    def AddTray(self):           #Add extra tray for Pick and Place
        self.Trays = self.Line0.text()
        if not self.isfloat(self.Trays):
            QMessageBox.warning(self,"Warning","Not a Number!")
        elif int(self.Trays) == 1:
            pass
        elif int(self.Trays) > 6:
            QMessageBox.warning(self,"Warning","Too Many Trays!")
        else:
            self.Trays = int(self.Trays)
            self.updatesEnabled = False
            for i in range(len(self.Line)+2,self.Trays+1):
                self.Etab[i] = QWidget()
                self.tabs.addTab(self.Etab[i], 'Tray {}'.format(i))
                self.Line.append([])
                for j in range(6):
                    self.Line[i-2].append(QLineEdit())
                hbox = QHBoxLayout()
                fbox = [QFormLayout(), QFormLayout()]
                fbox[0].addRow('Initial X Tray',self.Line[i-2][0])
                fbox[0].addRow('X Tray Offset',self.Line[i-2][1])
                fbox[0].addRow('X Tray Dimension',self.Line[i-2][2])
                fbox[1].addRow('Initial Y Tray',self.Line[i-2][3])
                fbox[1].addRow('Y Tray Offset',self.Line[i-2][4])
                fbox[1].addRow('Y Tray Dimension',self.Line[i-2][5])
                hbox.addLayout(fbox[0])
                hbox.addLayout(fbox[1])
                self.Etab[i].setLayout(hbox)
            self.updatesEnabled = True

    def push1(self):  #Save Settings
        Lines = [self.Line1.text(),self.Line2.text(),self.Line3.text(),self.Line4.text(),
                self.Line5.text(),self.Line6.text(),self.Line7.text(),self.Line8.text(),
                self.Line9.text(),self.Line10.text(),self.Line11.text()]
        Line = []
        if not self.Line:
            check = 1
        else:
            Line = [[x.text() for x in y] for y in self.Line]
            check = all([all([self.isfloat(x) for x in y]) for y in Line])
        if not all([self.isfloat(i) for i in Lines]) or not check:
            QMessageBox.information(self,"Warning","Not a Number Detected in Settings")
        else:
            filename = QFileDialog.getSaveFileName(self, 'Save Settings')
            if not filename[0]:
                QMessageBox.warning(self,"Warning","Filename Empty!")
            else:
                with open(filename[0],'w') as f:
                    file_text = ','.join(Lines)
                    num = ''
                    for item in Line:
                        file_text = file_text + ',' +  ','.join(item)
                    try:
                        self.Trays
                    except:
                        num = '1,'
                    else:
                        num = str(self.Trays) + ','
                    file_text = num + file_text
                    print(file_text)
                    f.write(file_text)

    def push2(self):    #Load Settings
        filename = QFileDialog.getOpenFileName(self, 'Open Settings')
        if not filename[0]:
            QMessageBox.warning(self, "Warning","Filename Empty!")
        else:
            with open(filename[0],'r') as f:
                Lines = [self.Line1,self.Line2,self.Line3,self.Line4,self.Line5,self.Line6,
                        self.Line7,self.Line8,self.Line9,self.Line10,self.Line11]
                f_string = f.read()
                item = f_string.split(',')
                num = int(item[0])
                for i in range(1,12):
                    Lines[i-1].setText(item[i])
                if num > 1:
                    self.Line0.setText(item[0])
                    self.AddTray()
                    cnt = 0
                    for x in self.Line:
                        for y in x:
                            y.setText(item[12 + cnt])
                            cnt += 1

    def push8(self): #Save GCode
        filename = QFileDialog.getSaveFileName(
            self, 'Save File',os.getenv('HOME'))
        if not filename[0]:
            QMessageBox.warning(self,"Warning","Filename Empty!")
        else:
            if not filename[0].endswith('.gcode'):
                print('add .gcode')
            with open(filename[0],'w') as f:
                file_text = self.Text1.toPlainText()
                f.write(file_text)

    def push7(self): #Open GCode
        filename = QFileDialog.getOpenFileName(
            self, 'Open File')
        if not filename[0]:
            QMessageBox.warning(self,"Warning","Filename Empty!")
        else:
            with open(filename[0],'r') as f:
                file_text = f.read()
                self.Text1.setText(file_text)

    def push9(self):    #Find Word
        if not self.FindString.text():
            QMessageBox.information(self,"Info","Enter Keyword!",QMessageBox.Ok)
        else:
            document = self.Text1.document()
            cursor1 = QTextCursor(document)
            cursor1.setPosition(self.Cpos,QTextCursor.MoveAnchor)
            cursor1 = document.find(self.FindString.text(), cursor1)
            if cursor1.position() == -1:
                cursor1.setPosition(1)
                cursor1 = document.find(self.FindString.text(), cursor1)
                if cursor1.position() == -1:
                    QMessageBox.information(self,"Info","Keyword Not Found /End of Line",QMessageBox.Ok)
                else:
                    cursor1.select(QTextCursor.WordUnderCursor)
                    self.Cpos = cursor1.position()
                    self.Text1.setTextCursor(cursor1)
            else:
                cursor1.select(QTextCursor.WordUnderCursor)
                self.Cpos = cursor1.position()
                self.Text1.setTextCursor(cursor1)

    def push10(self):  #Reset Find
        self.Cpos = 0
        self.FindString.clear()

    def push11(self):     #Rebuilt Parse
        document = self.Text1.document()

        # Find the origin offset
        cursor1 = QTextCursor(document)
        cursor1 = document.find('G0 X', cursor1)
        cursor1.clearSelection()
        cursor1.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
        self.Xorigin = float(cursor1.selectedText())
        cursor1.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor)
        cursor1.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor)
        cursor1.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
        self.Yorigin = float(cursor1.selectedText())

        #User input Line edit
        Lines = [self.Line1.text(),self.Line2.text(),self.Line3.text(),self.Line4.text(),
                self.Line5.text(),self.Line6.text(),self.Line7.text(),self.Line8.text(),
                self.Line9.text(),self.Line10.text(),self.Line11.text()]
        if not self.Line: #check if user input are valid
            check = 1
        else:
            check = all([all([self.isfloat(y.text()) for y in x]) for x in self.Line])

        #cursor 1 find the next occurane of extruder change (T3 tool is set
        #as default for pick and place
        cursor1 = document.find('T3 ; change extruder', cursor1)
        if cursor1.position() == -1:    #Check if there's a result for the keyword find
            QMessageBox.information(self,"Info","No Pick and Place operation found on the GCode",QMessageBox.Ok)
        elif not all([self.isfloat(i) for i in Lines]) or not check:     #Check if all the input propper numbers
            QMessageBox.information(self,"Warning","Not a Number Detected in user input!")
        else:
            #Set up Tray location(s)
            self.dispenser = [[float(self.Line1.text())-self.Xorigin,    #dispenser location start
                              float(self.Line6.text())-self.Yorigin]]
            self.change = [1]     #For keeping track change change in tray row
            for item in self.Line:
                self.dispenser.append([float(item[0].text()) - self.Xorigin, float(item[3].text())-self.Yorigin])
                self.change.append(1)

            ended = 0 #flag for determining if the parser should keep searching for next pick and place operation block
            while not ended:
                #Determine pick and place block, set cursor2 position
                cursor2 = QTextCursor(document)
                cursor2.setPosition(cursor1.position())
                cursor3 = document.find(keyword, cursor2)
                cursor2 = document.find('; perimeter (bridge)', cursor2)
                cursor2.movePosition(QTextCursor.EndOfLine)
                cursor2.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                cursor2.select(QTextCursor.WordUnderCursor)
                comment = cursor2.selectedText()

                placePos = []
                pos = 0

                #cheking if the end of file is reached
                cursor4 = QTextCursor(document) #block helper cursor
                cursor4.setPosition(cursor3.position())
                cursor4.movePosition(QTextCursor.StartOfLine)
                if cursor3.anchor() != cursor4.position():
                    ended = True    #keyword is at end of file, reached last
                                    #operation block
                    cursor3 = document.find('M107', cursor1)

                #List of Layer height
                self.height = []

                #do operation as long cursor 2 have not exceed cursor3
                while cursor2<cursor3 and cursor2.position() != -1:
                    placePos.append([[],[],None])

                    #search for the next layer height
                    cursor4 = document.find('; move to next layer', cursor2, QTextDocument.FindBackward)
                    cursor4.movePosition(QTextCursor.StartOfLine)
                    cursor4.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,4)
                    cursor4.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                    cursor4.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
                    cursor4.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                    self.height.append(cursor4.selectedText())

                    #Scan through all perimeter and append X and Y coordinates
                    while comment == ')':
                        cursor2.movePosition(QTextCursor.StartOfLine)
                        cursor2.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, 4)
                        cursor2.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                        cursor2.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
                        cursor2.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                        placePos[pos][0].append(float(cursor2.selectedText()))
                        cursor2.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor)
                        cursor2.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor)
                        cursor2.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                        cursor2.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
                        cursor2.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                        placePos[pos][1].append(float(cursor2.selectedText()))
                        cursor2.movePosition(QTextCursor.Down)
                        cursor2.movePosition(QTextCursor.EndOfLine)
                        cursor2.movePosition(QTextCursor.Left)
                        cursor2.select(QTextCursor.WordUnderCursor)
                        comment = cursor2.selectedText()

                    #Search next pointer
                    placePos[pos][2] = len(placePos[pos][0])
                    pos += 1
                    cursor2 = document.find('; perimeter (bridge)', cursor2)
                    cursor2.movePosition(QTextCursor.EndOfLine)
                    cursor2.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                    cursor2.select(QTextCursor.WordUnderCursor)
                    comment = cursor2.selectedText()

                #Do G-Code clean up and insertion
                if not ended:
                    cursor3 = document.find(';announce', cursor1)
                    cursor3.movePosition(QTextCursor.Up)
                    cursor3.movePosition(QTextCursor.EndOfLine)
                    cursor1.movePosition(QTextCursor.Up)
                    cursor1.movePosition(QTextCursor.StartOfLine)
                    cursor1.setPosition(cursor3.position(),QTextCursor.KeepAnchor)
                    cursor1.removeSelectedText()

                    self.insert_GCode(cursor1,placePos)
                else:
                    cursor3.movePosition(QTextCursor.Up)
                    cursor3.movePosition(QTextCursor.EndOfLine)
                    cursor1.movePosition(QTextCursor.Up, QTextCursor.MoveAnchor,3)
                    cursor1.movePosition(QTextCursor.StartOfLine)
                    cursor1.setPosition(cursor3.position(),QTextCursor.KeepAnchor)
                    cursor1.removeSelectedText()

                    self.insert_GCode(cursor1, placePos)

                self.Text1.setTextCursor(cursor1)
                cursor1 = document.find('T3',cursor1)
                if cursor1.position() == -1:
                    ended = True    #Reached end of operation

    def push12(self):   #Open Help Page
        curdir = os.getcwd()
        if platform == 'linux' or platform == "linux2":
            curdir = curdir.replace(' ','\ ')
            os.system('/usr/bin/xdg-open '+curdir+'/Help.pdf')
        elif platform == 'win32':
            os.system('start "" "'+curdir+'\\Help.pdf"')

dfont = QFont("Arial",18)
app = QApplication([])
app.setFont(dfont)
window1 = window()
app.exec_()


