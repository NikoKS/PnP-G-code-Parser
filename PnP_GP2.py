import os
import numpy as np
from sys import platform
from PyQt5.QtWidgets import (QApplication, QTextEdit, QLabel,
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
G4 P3000                 ;Delay\n\
M107 T[PnP_head]        ;Turn off vacuum\n\
G4 P500                 ;Delay\n\
M721 I1 T[PnP_head]     ;unprime current head\n\
G4 P2000                 ;delay 1s\n"

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
        label2 = QLabel('First X Tray Point')
        label3 = QLabel('Head X Offset')
        label4 = QLabel('X Tray Offset')
        label5 = QLabel('Y Tray Offset')
        label6 = QLabel('Head Y Offset')
        label7 = QLabel('First Y Tray Point')
        label8 = QLabel('Tray Item Height')
        label9 = QLabel('Tray X Dim')
        label10= QLabel('Tray Y Dim')
        label11= QLabel('G-Code Viewer')
        label11.setFont(subTFont)
        label12= QLabel('Main Head pos')
        label13= QLabel('PnP Head pos')

        self.Line1 = QLineEdit()    #first X point
        self.Line2 = QLineEdit()    #X Tray offset
        self.Line3 = QLineEdit()    #Y Tray offset
        self.Line4 = QLineEdit()    #Head X Offset
        self.Line5 = QLineEdit()    #Head Y Offset
        self.Line6 = QLineEdit()    #First Y Point
        self.Line7 = QLineEdit()    #Tray X Dimension
        self.Line8 = QLineEdit()    #Tray Y Dimension
        self.Line9 = QLineEdit()    #Tray Item Height
        self.FindString = QLineEdit()
        self.Line10= QLineEdit()    #Main Head
        self.Line11= QLineEdit()    #PnP Head

        self.But1 = QPushButton('Save')
        self.But1.clicked.connect(self.push1)
        self.But2 = QPushButton('Load')
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

        self.Text1 = QTextEdit()
        self.Cpos = 0

        #Window Layout
        fbox1 = QFormLayout()
        fbox1.addRow(label2,self.Line1)
        fbox1.addRow(label4,self.Line2)
        fbox1.addRow(label5,self.Line3)
        fbox1.addRow(label12,self.Line10)
        fbox1.addRow(label9,self.Line7)
        fbox1.addRow(label10,self.Line8)

        fbox2 = QFormLayout()
        fbox2.addRow(label7,self.Line6)
        fbox2.addRow(label3,self.Line4)
        fbox2.addRow(label6,self.Line5)
        fbox2.addRow(label13,self.Line11)
        fbox2.addRow(label8,self.Line9)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.But1)
        hbox1.addWidget(self.But2)

        vbox1 = QVBoxLayout()
        vbox1.addLayout(fbox2)
        vbox1.addLayout(hbox1)
        vbox1.addStretch()

        hbox2 = QHBoxLayout()
        hbox2.addLayout(fbox1)
        hbox2.addLayout(vbox1)
        hbox2.addStretch()

        vbox2 = QVBoxLayout()
        vbox2.addWidget(label1)
        vbox2.addLayout(hbox2)

        vbox8 = QVBoxLayout()
        vbox8.addLayout(vbox2)
        vbox8.addStretch()
        vbox8.addWidget(self.But12)
        vbox8.addStretch()

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

        vbox9 = QVBoxLayout()
        vbox9.addLayout(hbox5)
        vbox9.addWidget(self.Text1)
        vbox9.addLayout(hbox4)

        FinalBox = QHBoxLayout()
        FinalBox.addLayout(vbox8)
        FinalBox.addLayout(vbox9)

        #vbox 7 = add point, vbox 2 = setting
        self.setLayout(FinalBox)
        #Window Functions
        self.setGeometry(300,300,1500,600)
        self.setWindowTitle('Pick and Place Gcode Parser')
        self.show()

    def isfloat(self,s):
        try:
            float(s)
            return True
        except:
            return False

    def insert_GCode(self,cursor,placePos):
        TC = Tool_Change_Gcode.replace('[current_head]', self.Line10.text())
        TC = TC.replace('[height]', str(float(self.height)+10))
        cursor.insertText(TC)
        for item in placePos:
            item[0] = round(np.mean(item[0]), 3) + float(self.Line4.text())
            item[1] = round(np.mean(item[1]), 3) + float(self.Line5.text())
            xdim = float(self.Line7.text())
            ydim = float(self.Line8.text())
            PG = Pick_Gcode.replace('[pick_X]', str(self.dispenser[0]))
            PG = PG.replace('[pick_Y]', str(self.dispenser[1]))
            PG = PG.replace('[place_X]', str(item[0]))
            PG = PG.replace('[place_Y]', str(item[1]))
            PG = PG.replace('[height]', str(float(self.height)+10))
            PG = PG.replace('[tray_Z]', self.Line9.text())
            PG = PG.replace('[place_Z]', self.height)
            PG = PG.replace('[PnP_head]', self.Line11.text())
            cursor.insertText(PG)
            if self.change != xdim:
                self.dispenser[0] += float(self.Line2.text())
                self.change += 1
            else:
                self.dispenser[0] = float(self.Line1.text()) - self.Xorigin
                self.dispenser[1] += float(self.Line3.text())
                self.change = 1
        TC2 = Tool_Change_Gcode2.replace('[current_head]', self.Line10.text())
        cursor.insertText(TC2)

    def push1(self):  #Save Settings
        filename = QFileDialog.getSaveFileName(self, 'Save Settings')
        if not filename[0]:
            QMessageBox.warning(self,"Warning","Filename Empty!")
        else:
            with open(filename[0],'w') as f:
                Lines = [self.Line1.text(),self.Line2.text(),self.Line3.text(),self.Line4.text(),
                        self.Line5.text(),self.Line6.text(),self.Line7.text(),self.Line8.text(),
                        self.Line9.text(),self.Line10.text(),self.Line11.text()]
                if not all([self.isfloat(i) for i in Lines]):
                    QMessageBox.information(self,"Warning","Not a Number Detected")
                else:
                    file_text = ','.join(Lines)
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
                for i in range(len(item)):
                    Lines[i].setText(item[i])

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
                QMessageBox.information(self,"Info","Keyword Not Found /End of Line",QMessageBox.Ok)
            else:
                cursor1.movePosition(QTextCursor.WordRight,QTextCursor.KeepAnchor)
                self.Cpos = cursor1.position()
                self.Text1.setTextCursor(cursor1)

    def push10(self):  #Reset Find
        self.Cpos = 0
        self.FindString.clear()

    def push11(self): #Parse
        document = self.Text1.document()
        cursor1 = QTextCursor(document)
        cursor1 = document.find(keyword, cursor1)   #Finding do pnp
        cursor5 = QTextCursor(document)
        cursor5 = document.find('G0 X', cursor5)    #Finding the origin offset
        cursor5.clearSelection()
        cursor5.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
        self.Xorigin = float(cursor5.selectedText())
        cursor5.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor)
        cursor5.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor)
        cursor5.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
        self.Yorigin = float(cursor5.selectedText())
        cursor5.movePosition(QTextCursor.Start)
        cursor5 = document.find('T0 ; change extruder', cursor5)    #Remove change extruder commands
        cursor5.movePosition(QTextCursor.StartOfLine)
        cursor5.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        cursor5.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor5.removeSelectedText()
        Lines = [self.Line1.text(),self.Line2.text(),self.Line3.text(),self.Line4.text(),
                self.Line5.text(),self.Line6.text(),self.Line7.text(),self.Line8.text(),
                self.Line9.text(),self.Line10.text(),self.Line11.text()]
        if cursor1.position() == -1:    #Check if there's a result for the keyword find
            QMessageBox.information(self,"Info","No Pick and Place operation found on the GCode",QMessageBox.Ok)
        elif not all([self.isfloat(i) for i in Lines]):     #Check if all the input propper numbers
            QMessageBox.information(self,"Warning","Not a Number Detected")
        else:
            self.dispenser = [float(self.Line1.text())-self.Xorigin,    #dispenser location start
                              float(self.Line6.text())-self.Yorigin]
            self.change = 1
            ended = False
            while not ended:
                placePos = []
                pos = 0
                cursor2 = document.find('; perimeter (bridge)',cursor1) #cursor for traversing through all perimeter
                cursor2.select(QTextCursor.WordUnderCursor)
                comment = cursor2.selectedText()
                cursor3 = document.find(keyword, cursor1) #cursor to keep position of the end of PnP operation
                cursor4 = QTextCursor(document)
                cursor4.setPosition(cursor3.position())
                cursor4.movePosition(QTextCursor.StartOfLine)
                if cursor3.anchor() != cursor4.position():
                    ended = True
                    cursor3 = document.find('M107', cursor1)
                cursor5 = document.find('; move to next layer', cursor1, QTextDocument.FindBackward)
                cursor5.movePosition(QTextCursor.StartOfLine)
                cursor5.movePosition(QTextCursor.Right,QTextCursor.MoveAnchor,4)
                cursor5.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                cursor5.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, 2)
                cursor5.movePosition(QTextCursor.WordRight, QTextCursor.KeepAnchor)
                self.height = cursor5.selectedText()
                print(self.height)
                while cursor2 < cursor3:
                    placePos.append([[],[]])
                    while comment in {'(bridge)','fan'}:   #Scan through all perimeter
                        if comment == '(bridge)':
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
                        cursor2.select(QTextCursor.WordUnderCursor)
                        comment = cursor2.selectedText()
                    pos += 1
                    cursor2 = document.find('; perimeter (bridge)', cursor2)
                    cursor2.select(QTextCursor.WordUnderCursor)
                    comment = cursor2.selectedText()

                if not ended:
                    cursor3.movePosition(QTextCursor.Up)
                    cursor3.movePosition(QTextCursor.StartOfLine)
                    cursor4.movePosition(QTextCursor.Down)
                    cursor4.movePosition(QTextCursor.EndOfLine)
                    cursor3.setPosition(cursor4.position(),QTextCursor.KeepAnchor)
                    cursor3.removeSelectedText()

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
                    cursor1.movePosition(QTextCursor.Up)
                    cursor1.movePosition(QTextCursor.StartOfLine)
                    cursor1.setPosition(cursor3.position(),QTextCursor.KeepAnchor)
                    cursor1.removeSelectedText()

                    self.insert_GCode(cursor1, placePos)

                print(placePos)
                self.Text1.setTextCursor(cursor1)
                cursor1 = document.find(keyword,cursor1)
                cursor2.setPosition(cursor1.position())
                cursor2.movePosition(QTextCursor.StartOfLine)
                if cursor1.anchor() != cursor2.position():
                    ended = True

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
window1=window()
app.exec_()


