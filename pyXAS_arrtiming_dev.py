import PyQt5.QtCore as QtCore
from silx.gui import qt
from silx.gui.plot import Plot1D, Plot2D
import numpy as np
import pandas as pd
import glob
import multiprocessing as mp
import sys, os, re, difflib, natsort, math, shutil, time, yaml
from ui_bottom import Ui_Form as UI_bottom
from ui_LeftWidget import Ui_Form as ui_Left
from ui_PopUp import Ui_Dialog as ui_popup

qapp = qt.QApplication([])

OStype = sys.platform

colours_XAS = ['#000000','#808080','#C0C0C0','#800000','#808000','#008080']
colours_diff = ['#FF0000','#0000FF','#FF00FF','#00FF00','#00FFFF','#FFA500']

class MainWindow(qt.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setMinimumWidth(1400)
        self.setWindowTitle('plot XAS: arrival timing')
        self.timer = qt.QBasicTimer()
        self.qtimer = qt.QTimer()

        self.waittime = 1000
        self.datasets = []
        self.Energy = []
        self.dct = {}

        self.CWidget = qt.QWidget(parent=self.centralWidget())
        self.CWidget.setMinimumWidth(800)

        self.CWidget.setLayout(qt.QGridLayout())
        
        MainWidget = qt.QWidget(parent=self.CWidget)
        #MainWidget.setMaximumHeight(750)
        #MainWidget.setMinimumWidth(800)

        LeftWidget = qt.QDockWidget(parent=self)
        LeftWidget.setMinimumWidth(270)

        HLayout = qt.QGridLayout()
        MainWidget.setLayout(HLayout)

        backend = "mpl"

        self.plotXAS = Plot1D(parent=MainWidget, backend=backend)
        self.plotXAS.setGraphTitle("XAS/diffXAS")
        MainWidget.layout().addWidget(self.plotXAS, 0, 0)

        self.plotAll = Plot2D(parent=MainWidget, backend=backend)
        self.plotAll.setGraphTitle("plot XAS all")
        MainWidget.layout().addWidget(self.plotAll, 0, 1)

        self.bwidget = qt.QWidget(parent=self.CWidget)
        self.bwidget.setMinimumHeight(180)

        self.leftform = ui_Left()
        self.leftform.setupUi(LeftWidget)

        self.bottomform = UI_bottom()
        self.bottomform.setupUi(self.bwidget)
        
        if os.path.isfile('init.yaml'):
            dct = yaml.load(open('init.yaml'))
            if 'DET' in dct.keys():
                self.bottomform.textEdit.clear()
                self.bottomform.textEdit.append(dct['DET'])
        
        MainWidget.layout().addWidget(self.bwidget, 1, 0)

        self.CWidget.layout().addWidget(MainWidget,0,0)
        self.CWidget.layout().addWidget(self.bwidget,1,0)

        self.setCentralWidget(self.CWidget)
        self.addDockWidget(qt.Qt.LeftDockWidgetArea, LeftWidget)

        def OpenDir():
            self.plotXAS.clear()
            self.plotAll.clear()
            fdir = self.bottomform.textBrowser.toPlainText()
            dat_dir=os.environ[("HOMEPATH")*(OStype =='win32')+("HOME")*(OStype =='darwin')]
            if fdir !="" and os.path.isdir(fdir):
                dat_dir = fdir
            FO_dialog = qt.QFileDialog()
            directory=FO_dialog.getExistingDirectory(None,caption="Select a directory", directory=dat_dir)
            if directory:
                self.bottomform.textBrowser_2.clear()
                self.bottomform.textBrowser_2.append(directory)

        def SetDir():
            self.plotXAS.clear()
            self.plotAll.clear()
            fdir = self.bottomform.textBrowser.toPlainText()
            dat_dir=os.environ[("HOMEPATH")*(OStype =='win32')+("HOME")*(OStype =='darwin')]
            if fdir !="" and os.path.isdir(fdir):
                dat_dir = fdir
            FO_dialog = qt.QFileDialog()
            directory=FO_dialog.getExistingDirectory(None,caption="Select a directory", directory=dat_dir)
            if directory:
                self.bottomform.textBrowser.clear()
                self.bottomform.textBrowser.append(directory)
            if os.path.isfile(self.bottomform.textBrowser.toPlainText()+'/'+'init.yaml'):
                if self.leftform.listWidget.count():
                    self.leftform.listWidget.clear()
                datdir = self.bottomform.textBrowser.toPlainText()
                dct = yaml.load(open(datdir+'/'+'init.yaml'))

                if dct['DET']:
                    self.bottomform.textEdit.clear()
                    self.bottomform.textEdit.append(dct['DET'])
                
                if dct['DataSets']:
                    for x in dct['DataSets']:
                        self.leftform.listWidget.addItem(qt.QListWidgetItem(x))
                    #print (dct['DataSets'])
                else:
                    msgBox = qt.QMessageBox()
                    msgBox.setText("Error: No data sets were specified")
                    msgBox.exec_()
            if os.path.isfile(directory+'/'+'measurements.yaml'):
                dct = yaml.load(open(directory+'/'+'measurements.yaml'))

                for f in dct[0]['files']:
                    self.leftform.listWidget.addItem(qt.QListWidgetItem(f))

        self.dialog = qt.QDialog()
        self.dialog.ui = ui_popup()
        self.dialog.ui.setupUi(self.dialog)
        def open_dialog():
            self.dialog.ui.lE_fname.clear()
            self.dialog.exec_()
            self.dialog.show()

        def close_wAccepted():
            self.dialog.done(1)

        def close_dialog():
            self.dialog.reject()

        def create_newItem():
            if self.dialog.ui.lE_fname.text():
                x = self.dialog.ui.lE_fname.text()
                self.leftform.listWidget.addItem(qt.QListWidgetItem(x))

        def addItem_inList():
            if not self.bottomform.textBrowser.toPlainText():
                msgBox = qt.QMessageBox()
                msgBox.setText("Error: set the data directory in \"Outdir\"")
                msgBox.exec_()
                return
            elif not self.bottomform.textBrowser_2.toPlainText() and not self.bottomform.checkBox_2.isChecked():
                msgBox = qt.QMessageBox()
                msgBox.setText("Error: set the original data  directory in \"Rawdata\"")
                msgBox.exec_()
                return
            else:
                open_dialog()
            # elif not os.path.isfile(self.bottomform.textBrowser.toPlainText()+'/'+'init.yaml'):
            #     msgBox = qt.QMessageBox()
            #     msgBox.setText("Error: create the data list file in \"Outdir\"")
            #     msgBox.exec_()
            #     return
            # elif os.path.isfile(self.bottomform.textBrowser.toPlainText()+'/'+'init.yaml'):
            #     if self.leftform.listWidget.count():
            #         self.leftform.listWidget.clear()
            #     datdir = self.bottomform.textBrowser.toPlainText()
            #     dct = yaml.load(open(datdir+'/'+'init.yaml'))
                
            #     if dct['DataSets']:
            #         for x in dct['DataSets']:
            #             self.leftform.listWidget.addItem(qt.QListWidgetItem(x))
            #         #print (dct['DataSets'])
            #     else:
            #         msgBox = qt.QMessageBox()
            #         msgBox.setText("Error: No data sets were specified")
            #         msgBox.exec_()
        self.rightMenu = qt.QMenu(self.leftform.listWidget)
        self.removeAction = qt.QAction('Delete Item')
        # triggered the activation events after the right-click menu is. Here slef.close call the system comes close event.
        self.rightMenu.addAction(self.removeAction)
        self.output = qt.QAction('Save this list')
        self.rightMenu.addAction(self.output)
        def rightMenuShow():
            #addAction = QtGui.QAction (u "Add", self, triggered = self.addItem) # define objects can be specified from the event
            #rightMenu.addAction(addAction)
            self.rightMenu.exec_(qt.QCursor.pos())

        self.leftform.listWidget.setContextMenuPolicy(qt.Qt.CustomContextMenu)
        self.leftform.listWidget.customContextMenuRequested[qt.QPoint].connect(rightMenuShow)

        def removeItem_from_List():
            ItemList = self.leftform.listWidget.selectedItems()
            if not ItemList: return        
            for item in ItemList:
                self.leftform.listWidget.takeItem(self.leftform.listWidget.row(item))
                self.leftform.listWidget.removeItemWidget(item)

        def remove_all_Items():
            # print (self.leftform.listWidget.count())
            arr = [x for x in range(self.leftform.listWidget.count())][::-1]
            for i in arr:
                item = self.leftform.listWidget.takeItem(i)
                self.leftform.listWidget.removeItemWidget(item)
            # self.leftform.listWidget.selectAll()

        def OutPut_List():
            # ItemList = self.leftform.listWidget.items()
            itemsTextList =  [str(self.leftform.listWidget.item(i).text()) for i in range(self.leftform.listWidget.count())]
            print ([x for x in itemsTextList])
            
            if not self.bottomform.textBrowser.toPlainText() or not os.path.isdir(self.bottomform.textBrowser.toPlainText()):
                return
            elif itemsTextList:
                outdir = self.bottomform.textBrowser.toPlainText()
                dict_file = [{'files' : itemsTextList}]
                with open(outdir+'/'+'measurements.yaml', 'w') as file:
                    documents = yaml.dump(dict_file, file)
                #print ([x for x in ItemList])
            # print ('Hello')
        
        self.removeAction.triggered.connect(removeItem_from_List)
        self.output.triggered.connect(OutPut_List)
            
        self.leftform.pB_add.clicked.connect(addItem_inList)
        self.leftform.pB_clear.clicked.connect(remove_all_Items)
        self.bottomform.pushButton.clicked.connect(OpenDir)
        self.bottomform.pushButton_3.clicked.connect(SetDir)
        self.bottomform.pushButton_2.clicked.connect(self.doAction)
        self.dialog.ui.pushButton.clicked.connect(close_wAccepted)
        self.dialog.ui.pushButton_2.clicked.connect(close_dialog)
        self.dialog.accepted.connect(create_newItem)
        self.show()

    def loadFiles(self):
        datdir = self.bottomform.textBrowser.toPlainText()
        rawdir = self.bottomform.textBrowser_2.toPlainText()
        #print (glob.glob(datdir+'/'+'*det0*.txt'))
        #print (self.det_roi)
        self.det_roi = self.bottomform.textEdit.toPlainText()

        if self.bottomform.checkBox_2.isChecked():
            lst = self.leftform.listWidget
            items = []
            for x in range(lst.count()):
                items.append(lst.item(x).text())

            #print (items)

            for x in items:
                if not os.path.isfile(datdir+'/'+x+'_'+self.det_roi+'.txt') and os.path.isfile(rawdir+'/'+x+'_'+self.det_roi+'.txt'):
                    files = glob.glob(rawdir+'/'+x+'*'+'.txt')
                    print (files)
                    for f in files:
                        shutil.copyfile(f,datdir+'/'+os.path.basename(f))
        
        
        #print (self.det_roi)
        tppdata=natsort.natsorted(glob.glob(datdir+'/'+'*'+self.det_roi+'.txt'))[:-1]*self.bottomform.checkBox.isChecked()+\
                natsort.natsorted(glob.glob(datdir+'/'+'*'+self.det_roi+'.txt'))*(not self.bottomform.checkBox.isChecked())
        #print (tppdata)
        ppdata = []

        if os.path.isfile(datdir+'/'+'init.yaml'):
            self.dct = yaml.load(open(datdir+'/'+'init.yaml'))
        else:
            self.dct = yaml.load(open('init.yaml'))

 
        if len(tppdata) and len(tppdata) != len(self.datasets):
            if self.datasets and not self.plotAll.getImage(legend='ppXAS'):
                ut = self.plotAll.getImage(legend='ppXAS').getData()
                for i in range(len(tppdata[:1])):
                    if not tppdata[i] in self.datasets:
                        self.datasets.append(tppdata)
            else:
                ut = []
                self.datasets = []
                self.Energy = []
                ppdata = tppdata

            for i in range(len(ppdata)):
                datf = ppdata[i]
                f = open(datf)
                #tut_off = []
                #tut_on =[]
                #tut_off_cam = []
                k = 0
                for l in f:
                    tarray = [x for x in l.rstrip().split(' ') if x!='']
                    if not self.datasets:
                        if i ==0:
                            ut.append(np.array([float(x) for x in tarray[1:-6]]))
                            self.Energy.append(float(tarray[0]))
                        else:
                            ut[k] += np.array([float(x) for x in tarray[1:-6]])
                            k+=1
                    else:
                        ut[k] += np.array([float(x) for x in tarray[1:-6]])
                        k+=1
                f.close()

                self.plotAll.addImage(np.transpose(ut),legend='ppXAS')

            if self.dct:
                ut_ng = []
                ut_ng_each = []
                ns_neg = self.dct['Areas']['preTime0'][0]
                ne_neg = self.dct['Areas']['preTime0'][1]
                for j in range(len(ut)):
                    ut_ng.append(np.average(ut[j][ns_neg:ne_neg]))
                    ut_ng_each.append(np.array(ut[j][ns_neg:ne_neg]))

                ut_err_ = np.std(np.transpose(ut_ng_each),axis=0)
                print (ut_err_)

                i = 0
                for x in self.dct['Areas'].keys():
                    if x != 'preTime0':
                        ut_ = []
                        ns = self.dct['Areas'][x][0]
                        ne = self.dct['Areas'][x][1]
                        for j in range(len(ut)):
                            ut_.append(np.average(ut[j][ns:ne]))
                        self.plotXAS.addCurve(self.Energy,ut_,legend=x,color=colours_XAS[i%6])
                    elif x == 'preTime0':
                        self.plotXAS.addCurve(self.Energy,ut_ng,legend=x,color=colours_XAS[i%6])
                    i += 1
                if self.dct['Plots']['difference'] == 'yes':
                    (ut_negx, ut_neg_y, ut_neg_errx, ut_neg_erry) = self.plotXAS.getCurve(legend=self.dct['Plots']['NEG']).getData()
                    j = 0
                    for x in self.dct['Areas'].keys():
                        if x == self.dct['Plots']['NEG']:
                            pass
                        else:
                            ns = self.dct['Areas'][x][0]
                            ne = self.dct['Areas'][x][1]
                            (ut_x, ut_y, ut_errx, ut_erry) = self.plotXAS.getCurve(legend=x).getData()
                            ut_err_diff = np.sqrt(ut_err_**2/abs(ne-ns) + ut_err_**2/abs(ne_neg-ns_neg))
                            self.plotXAS.addCurve(ut_x,ut_y-ut_neg_y,yaxis='right',legend='diff: '+x,
                                                  yerror=ut_err_diff,color=colours_diff[j%6])
                            j += 1
            
        else:
            print ('Waiting for updates.....')
            pass

    

    def doAction(self):
        if self.timer.isActive():
            self.timer.stop()
            self.bottomform.pushButton_2.setText('Run')
        else:
            if self.bottomform.textBrowser.toPlainText():
                self.plotXAS.clear()
                self.plotAll.clear()
                self.datasets = []
                self.timer.start(self.waittime,self)
                self.bottomform.pushButton_2.setText('Stop')
                #self.loadFiles()
            else:
                qt.QMessageBox.about(self, "Error", "Check the directory")
            
    def timerEvent(self, event):
        lst = self.leftform.listWidget
        if lst.count():
            # items = []
            # for x in range(lst.count()):
            #     items.append(lst.item(x).text())
            self.loadFiles()

if __name__ == '__main__':

    wid = MainWindow()

    qapp.exec_()
