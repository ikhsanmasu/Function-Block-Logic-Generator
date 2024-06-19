import pandas as pd
import numpy as np
import csv
import math
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QInputDialog, QApplication, QFileDialog, QDialog, QMessageBox
from PyQt5.QtCore import Qt

# convert ui to py
# python -m PyQt5.uic.pyuic -x "UI REV 00.ui" -o "UI REV 00.py"

# it_address = "C:\File Ikhsan\Development\GELO\Interlocking Table Kiaracondong rev.00 GELO.xlsx"
# it_address = "C:\File Ikhsan\Development\GELO\Interlocking Table Cimahi rev.00 - GELO.xlsx"
# it_address = "C:\File Ikhsan\Development\GELO\Interlocking Table THB REV02 - GELO.xlsx"
referensi_csv = os.getcwd() + "\REFERENSI CSV"

simp = lambda a: a.replace('J', '').replace('JL', '').replace('L', '')
def simp_number(input_string):
    num = ""
    first_number = 0
    for c in input_string:
        if c.isdigit():
            num = num + c
            first_number = 1
        if not c.isdigit() and first_number:
            break
    return str(num)
def arah_rute(input_IT):
    if input_IT[2].endswith("B") or input_IT[15].endswith("B") or \
            simp_number(input_IT[2])[-1] < simp_number(input_IT[15])[-1]:
        arah_rute = "EAST"
    else:
        arah_rute = "WEST"
    return arah_rute
def arah_rute_it2(input_IT):
    if input_IT[2].endswith("B") or input_IT[6].endswith("B") or \
            simp_number(input_IT[2])[-1] < simp_number(input_IT[6])[-1]:
        arah_rute = "EAST"
    else:
        arah_rute = "WEST"
    return arah_rute
def normalize_track(track):
    output = track
    if track.endswith("T"):
        output = track[:-1]
    if track.endswith(".0"):
        output = track.replace(".0", "")
    return output

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(691, 192)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 671, 151))
        self.groupBox.setStyleSheet("background-color: rgb(227, 229, 240);")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(11, 20, 651, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.horizontalLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.search_IT_Directory = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.search_IT_Directory.setMaximumSize(QtCore.QSize(25, 16777215))
        self.search_IT_Directory.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.search_IT_Directory.setIconSize(QtCore.QSize(16, 16))
        self.search_IT_Directory.setObjectName("search_IT_Directory")
        self.gridLayout.addWidget(self.search_IT_Directory, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.IT_Directory = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.IT_Directory.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.IT_Directory.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.IT_Directory.setObjectName("IT_Directory")
        self.gridLayout.addWidget(self.IT_Directory, 0, 1, 1, 1)
        self.Generate_L = QtWidgets.QPushButton(self.groupBox)
        self.Generate_L.setGeometry(QtCore.QRect(230, 90, 241, 23))
        self.Generate_L.setStyleSheet("background-color: rgb(85, 194, 218);")
        self.Generate_L.setObjectName("Generate_L")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 691, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.search_IT_Directory.clicked.connect(self.searchITdir)
        self.Generate_L.clicked.connect(self.generateLogic)
        # self.generateLogic()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SILOGOR (SIL02NG LOGIC GENERATOR)"))
        self.search_IT_Directory.setText(_translate("MainWindow", "..."))
        self.label.setText(_translate("MainWindow", "Interlocking Table Directorry :"))
        self.Generate_L.setText(_translate("MainWindow", "GENERATE LOGIC"))

    def searchITdir(self):
        # Memilih dan mengambil data path Interlocking Table ke dalam input box
        file, check = QFileDialog.getOpenFileName(None, "Pilih Interlocking Table",
                                                  "", "All Files (*);;Python Files (*.py);;Text Files (*.txt)")
        if check:
            self.IT_Directory.setText(file)

    def generateLogic(self):
        # pilih folder untuk menyimpan hasil generate
        directory_simpan = ""
        # Delete this
        # directory_simpan = "C:/File Ikhsan/Development/GELO/Hasil Generate"
        # Uncomment this
        directorySimpan = str(QFileDialog.getExistingDirectory(None, "Pilih Folder Penyimpanan Hasil"))

        QApplication.setOverrideCursor(Qt.WaitCursor)
        it_address = self.IT_Directory.text()

        # Baca Excel File ke data frame
        it1_df = pd.read_excel(it_address, sheet_name='IT 1')
        it2_df = pd.read_excel(it_address, sheet_name='IT 2')
        pm_df = pd.read_excel(it_address, sheet_name='POINT MACHINE')
        jpl_df = pd.read_excel(it_address, sheet_name='JPL')

        # Convert data frame ke excel and ubah nan value
        it1_raw = [[(str(str(x).strip().upper()) if str(x) != 'nan' else '') for x in d] for d in it1_df.values.tolist()]
        it2_raw = [[(str(str(x).strip().upper()) if str(x) != 'nan' else '') for x in d] for d in it2_df.values.tolist()]
        pm_raw = [[(str(str(x).strip().upper()) if str(x) != 'nan' else '') for x in d] for d in pm_df.values.tolist()]
        jpl_raw = [[(str(str(x).strip().upper()) if str(x) != 'nan' else '') for x in d] for d in jpl_df.values.tolist()]

        # tambah arah rute di ujung data
        it1_raw = [data + [arah_rute(data)] for data in it1_raw]
        it2_raw = [data + [arah_rute_it2(data)] for data in it2_raw]

        # normalkan nomor rute dan hapus spasi di nama rute
        it1_raw = [[normalize_track(data[0])] + [data[1].replace(" ", "")] + data[2:] for data in it1_raw]
        it2_raw = [[normalize_track(data[0])] + [data[1].replace(" ", "")] + data[2:] for data in it2_raw]

        pm_raw = [[w[0], normalize_track(w[1]), normalize_track(w[2])] for w in pm_raw]
        jpl_raw = [[j[0].replace("JPL", ""), normalize_track(j[1]), j[2].replace("W", "")] for j in jpl_raw]

        # normalisasi data speed
        it1_raw = [data[0:8] + ["V" if data[8] == "3.0" or data[8] == "4.0" or data[8] == "3" or data[8] == "4" else ""] + data[9:] for data in it1_raw]

        # IT1
        # | 0: NO RUTE | 1: RUTE | 2: START SIGNAL | 3:R | 4:Y | 5:G | 6:E | 7:Shunt | 8:Speed | 9:CF | 10:Dir-L |
        # | 11:Dir-R | 12:Distant Signal | 13: DIST Y | 14: DIST G | 15: DESTINATION SIGNAL | 16: STATION NAME |
        # | 17: ASPEK PROVING | 18: POINT LOCKED | 19: KEY DETECT | 20: TRACK CIRCUIT CLEAR | 21: SHUNT SIGNAL |
        # | 22: OPPOSING SIGNAL LOCKED | 23: APROACH TRACK | 24: APPROACH REQUAIRED | 25: REMARK |

        # Non Vital
        print("Generation Started...")
        self.nv_fc1_glob_var_and_pb_ctrl(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc2_il_route(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc3_il_point_parameter(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc4_te_route_req(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc5_shunt_int_shunt_req(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc6_route_parameter(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc7_ind_signal(it1_raw, it2_raw, referensi_csv, directory_simpan) # KURANG SINYAL IB
        self.nv_fc8_ind_point(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc9_ind_track(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw) # KURANG TRACK IB UJUNG NORMAL
        self.nv_fc10_ind_block_and_ind_alarm(it1_raw, it2_raw, referensi_csv, directory_simpan)
        self.nv_fc11_ind_pb_and_ind_fail(it1_raw, it2_raw, referensi_csv, directory_simpan)
        self.nv_fc12_ind_sig_fail(it1_raw, it2_raw, referensi_csv, directory_simpan) # KURANG SINYAL IB
        self.nv_fc13_ind_point_fail(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc14_counter(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc15_com_func_and_lamptest(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.nv_fc16_level_crossing(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw, jpl_raw)
        
        # Vital
        self.v_fc1_global_variable(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc3_route_conflict_lock(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc4_track_timer(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw) # kurang track yang tidak ada di IT
        self.v_fc5_point_control(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc6_lock_from_this_station(it1_raw, it2_raw, referensi_csv, directory_simpan) # belum sempurna
        self.v_fc8_route_check(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc9_signal_lighting(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw, jpl_raw) # kurang sinyal IB dan -H/D/G kurang -ACCNV
        self.v_fc10_route_lock(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc11_overlap_aproach_lock(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc12_aproach_lock(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc13_point_lock(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        self.v_fc14_emerg_rp_release(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw) # -AS kurang syarat wesel
        self.v_fc18_level_crossing(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw, jpl_raw)
        self.v_fc19_Key_Lock_Point(it1_raw, it2_raw, referensi_csv, directory_simpan, pm_raw)
        print("Generation Finished...")
        QApplication.restoreOverrideCursor()

    # -------------------------------------------------------- NON VITAL -----------------------------------------------#
    ################################# nV FC1 GLOB VAR & PB CTRL ############################
    def nv_fc1_glob_var_and_pb_ctrl(self, it1, it2, referensi_csv, directory_simpan, pm):
        # Generate nV FC1 GLOB VAR & PB CTRL - vSFC2_DI_to_EKR2
        def generatenVFC1vSFC2EKR2():
            allSignalS = list(set([s[2] for s in it1 if s[7]]))
            allSignal = list(set([s[2] for s in it1 if s[3] or s[4] or s[5]])) + list(set([s[12] for s in it1 if s[12] and (s[13] or s[14])]))
            allSignal = sorted(allSignal)

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allSignal), 10):
                dfLogic = pd.read_csv(referensi_csv + "\\vSFC2 DI to EKR2.csv")
                for y in range(10):

                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allSignal) % 10 != 0 and x == (math.floor(len(allSignal) / 10) * 10) and y == len(
                            allSignal) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-EKR-DI_' + str(y + 1): allSignal[y + x] + '-EKR-DI'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-EKR_' + str(y + 1): allSignal[y + x] + '-EKR'})
                    # jika sinyal beraspek warna ada sinyal langsirnya masukin GR-DO
                    if allSignal[y + x] in allSignalS:
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-GR-DO_' + str(y + 1): allSignal[y + x] + '-GR-DO'})
                    else:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-GR-DO_' + str(y + 1): 'FALSE'})

                dfLogic.to_csv(
                    directory_simpan + "\\vSFC2 DI to EKR2 " + str(x) + "-" + str(x + 10) + ".csv",
                    index=False)

        # Generate nV FC1 GLOB VAR & PB CTRL - vSFC2_DI_to_EKR6
        def generatenVFC1vSFC2EKR6():
            allSignal = list(set([s[2] for s in it1 if s[10] or s[11]]))
            allSignal = sorted(allSignal)
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allSignal), 10):
                dfLogic = pd.read_csv(referensi_csv + "\\vSFC2 DI to EKR6.csv")
                for y in range(10):

                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allSignal) % 10 != 0 and x == (math.floor(len(allSignal) / 10) * 10) and y == len(
                            allSignal) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-CFEK/DKR-DI_' + str(y + 1): allSignal[y + x] + '-DKR-DI'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-CFEK/DKR_' + str(y + 1): allSignal[y + x] + '-DKR'})

                dfLogic.to_csv(
                    directory_simpan + "vSFC2 DI to EKR6 DKR " + str(x) + "-" + str(x + 10) + ".csv",
                    index=False)

            allSignal = list(set([s[2] for s in it1 if s[9]]))
            allSignal = sorted(allSignal)

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allSignal), 10):
                dfLogic = pd.read_csv(referensi_csv + "\\vSFC2 DI to EKR6.csv")
                for y in range(10):

                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allSignal) % 10 != 0 and x == (math.floor(len(allSignal) / 10) * 10) and y == len(
                            allSignal) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-CFEK/DKR-DI_' + str(y + 1): allSignal[y + x] + '-CFEK-DI'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-CFEK/DKR_' + str(y + 1): allSignal[y + x] + '-CFEK'})

                dfLogic.to_csv(
                    directory_simpan + "\\vSFC2 DI to EKR6_" + str(x) + "-" + str(x + 10) + ".csv",
                    index=False)

        # Generate nV FC1 GLOB VAR & PB CTRL - nSFC2_TPBP
        def generatenVFC1vSFC2TPBP():

            allOsTrack = list(set([t[20].split(" ")[0].replace('T', '') for t in it1]))
            allOsTrack = sorted(allOsTrack)

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allOsTrack), 10):
                dfLogic = pd.read_csv(referensi_csv + "\\nSFC2 TPBP.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allOsTrack) % 10 != 0 and x == (math.floor(len(allOsTrack) / 10) * 10) and y == len(
                            allOsTrack) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TP_' + str(y + 1): allOsTrack[y + x] + '-TP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TPBP_' + str(y + 1): allOsTrack[y + x] + '-TPBP'})

                dfLogic.to_csv(directory_simpan + "\\nSFC2 TPBP " + str(x) + "-" + str(x + 10) + ".csv",
                               index=False)

        # Generate nV FC1 GLOB VAR & PB CTRL - nFC54 PB CTRL 1
        def nfc1_fc54_pbctrl1():
            ############################### Generate PB CTRL kombinasi tombol rute #####################################
            # list semua signal asal
            sig_asal = sorted(list(set([s[2] for s in it1])))
            # list signal asal jika rutenya lebih dari 10 sehingga FBDnya lebih dari 1
            signal_asal_2fbdmore = [s for s in sig_asal if
                                    len([it[15] for it in it1 if s == it[2] and "(T)" not in it[1]]) > 10]
            # list signal asal yang butuh 1 FBD saja
            signal_asal_1fbd = [s for s in sig_asal if s not in signal_asal_2fbdmore]

            # Generate per 10 signal asal
            # variable yang akan di generate
            var_enumerated = signal_asal_1fbd
            # jumlah FBD yang akan di generate
            jumlah_gen_fbd = 10
            # nama referensi csv FBD yang akan di generate
            fbd_tujuan = "nFC54 PB CTRL 1"
            # generate berdasarkan jumalah data per jumlah FBD yang akan di generate
            for index_csv in range(0, len(var_enumerated), jumlah_gen_fbd):
                # baca data referensi csv menjadi data frame logic
                df_logic = pd.read_csv(referensi_csv + f"\\{fbd_tujuan}.csv")
                # fungsi menyingkat perubahan variable data frame
                def replace_var(var_awal, var_baru):
                    df_logic['New Name'] = df_logic['New Name'].replace({var_awal: var_baru})
                # generate berdasarkan jumlah FBD yang akan di generate
                for ind_fbd in range(jumlah_gen_fbd):
                    # ubah bagian dibawah ini
                    try:
                        data_var = var_enumerated[ind_fbd + index_csv]
                        ind_fbd += 1

                        sig_asal = data_var

                        replace_var(f'xx-PB-DI_{ind_fbd}', f'{sig_asal}-PB-DI')

                        ind_sig_tujuan = 1
                        for data_it in it1:
                            if sig_asal == data_it[2] and "(T)" not in data_it[1]:
                                cf = ""
                                if "(CF)" in data_it[1]:
                                    cf = "-CF"
                                replace_var(f'xx-PB-DI_{ind_fbd}-{ind_sig_tujuan}', f'{data_it[15]}-PB-DI')
                                replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_tujuan}', f'{sig_asal}-{simp(data_it[15])}{cf}-CTRL')
                                ind_sig_tujuan += 1

                        # normalisasi data
                        for index in range(1, 11):
                            replace_var(f'xx-PB-DI_{ind_fbd}-{index}', f'FALSE')
                            replace_var(f'xx-CTRL_{ind_fbd}-{index}', f'HAPUS VARIABLE INI')

                    except Exception as e:
                        print(f"{fbd_tujuan} -> {e}" if str(e) != "list index out of range" else f"{fbd_tujuan} -> Done..")
                        break
                    finally:
                        pass

                df_logic.to_csv(directory_simpan + f"\\{fbd_tujuan} - Kombinasi Tombol Rute {index_csv}-{index_csv + jumlah_gen_fbd}.csv",
                                index=False)

            # Generate per 1 signal asal
            # variable yang akan di generate
            var_enumerated = signal_asal_2fbdmore
            for index_csv, s_a in enumerate(var_enumerated):
                # baca data referensi csv menjadi data frame logic
                df_logic = pd.read_csv(referensi_csv + f"\\{fbd_tujuan}.csv")

                # fungsi menyingkat perubahan variable data frame
                def replace_var(var_awal, var_baru):
                    df_logic['New Name'] = df_logic['New Name'].replace({var_awal: var_baru})

                replace_var(f'xx-PB-DI_{index_csv+1}', f'{s_a}-PB-DI')

                ind_fbd = 1
                ind_sig_tujuan = 1
                for it_data in it1:
                    if it_data[2] == s_a and "(T)" not in it_data[1]:
                        cf = ""
                        if "(CF)" in s_a[1]:
                            cf = "-CF"
                        replace_var(f'xx-PB-DI_{ind_fbd}-{ind_sig_tujuan}', f'{it_data[15]}-PB-DI')
                        replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_tujuan}', f'{sig_asal}-{simp(it_data[15])}{cf}-CTRL')
                        ind_sig_tujuan += 1
                        if ind_sig_tujuan == 11:
                            ind_fbd += 1
                            ind_sig_tujuan = 1

                for index in range(1, 11):
                    replace_var(f'xx-PB-DI_{ind_fbd}-{index}', f'FALSE')
                    replace_var(f'xx-CTRL_{ind_fbd}-{index}', f'HAPUS VARIABLE INI')
                df_logic.to_csv(
                    directory_simpan +
                    f"\\{fbd_tujuan} - Kombinasi Tombol Rute {s_a} {index_csv}-{index_csv + jumlah_gen_fbd}.csv",
                    index=False)

            ############################### Generate PB CTRL kombinasi tombol TSD #####################################
            # list semua signal asal emergency
            signal_asal = sorted(list(set([s[2] for s in it1 if "(E)" in s[1] or "(CF)" in s[1]])))
            ind_fbd = 1
            ind_sig_asal = 1
            df_logic = pd.read_csv(referensi_csv + f"\\{fbd_tujuan}.csv")
            # fungsi menyingkat perubahan variable data frame
            def replace_var(var_awal, var_baru):
                df_logic['New Name'] = df_logic['New Name'].replace({var_awal: var_baru})
            for s_a in signal_asal:
                replace_var(f'xx-PB-DI_{ind_fbd}', f'TSD-PB-DI')
                replace_var(f'xx-PB-DI_{ind_fbd}-{ind_sig_asal}', f'{s_a}-PB-DI')
                replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_asal}', f'{s_a}-E-CTRL')
                ind_sig_asal += 1
                if ind_sig_asal == 11:
                    ind_fbd += 1
                    ind_sig_asal = 1
            for ind_x in range(1, 11):
                for ind_y in range(1, 11):
                    replace_var(f'xx-PB-DI_{ind_x}', f'HAPUS FBD INI')
                    replace_var(f'xx-PB-DI_{ind_x}-{ind_y}', f'FALSE')
                    replace_var(f'xx-CTRL_{ind_x}-{ind_y}', f'HAPUS VARIABLE INI')

            df_logic.to_csv(
                directory_simpan + f"\\{fbd_tujuan} - Kombinasi Tombol TSD + Sinyal Asal.csv",
                index=False)

            ########################## Generate PB CTRL kombinasi tombol TPR sinyal Asal ##############################
            # list semua signal asal emergency
            signal_asal = sorted(list(set([s[2] for s in it1])))
            ind_fbd = 1
            ind_sig_asal = 1
            df_logic = pd.read_csv(referensi_csv + f"\\{fbd_tujuan}.csv")

            # fungsi menyingkat perubahan variable data frame
            def replace_var(var_awal, var_baru):
                df_logic['New Name'] = df_logic['New Name'].replace({var_awal: var_baru})

            for s_a in signal_asal:
                replace_var(f'xx-PB-DI_{ind_fbd}', f'TPR-PB-DI')
                replace_var(f'xx-PB-DI_{ind_fbd}-{ind_sig_asal}', f'{s_a}-PB-DI')
                replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_asal}', f'{s_a}-RST-CTRL')
                ind_sig_asal += 1
                if ind_sig_asal == 11:
                    ind_fbd += 1
                    ind_sig_asal = 1
            for ind_x in range(1, 11):
                for ind_y in range(1, 11):
                    replace_var(f'xx-PB-DI_{ind_x}', f'HAPUS FBD INI')
                    replace_var(f'xx-PB-DI_{ind_x}-{ind_y}', f'FALSE')
                    replace_var(f'xx-CTRL_{ind_x}-{ind_y}', f'HAPUS VARIABLE INI')

            df_logic.to_csv(directory_simpan + f"\\{fbd_tujuan} - Kombinasi Tombol TPR + Sinyal Asal.csv", index=False)

            ############################### Generate PB CTRL kombinasi tombol TBMS #####################################
            # list semua signal asal emergency
            signal_tujuan = sorted(list(set([s[15] for s in it1 if s[15].startswith("A")])))
            signal_tujuan_cf = sorted(list(set([s[15] for s in it1 if s[15].startswith("A") and "(CF)" in s[1]])))

            ind_fbd = 1
            ind_sig_asal = 1
            df_logic = pd.read_csv(referensi_csv + f"\\{fbd_tujuan}.csv")

            # fungsi menyingkat perubahan variable data frame
            def replace_var(var_awal, var_baru):
                df_logic['New Name'] = df_logic['New Name'].replace({var_awal: var_baru})

            for s_a in signal_tujuan:
                replace_var(f'xx-PB-DI_{ind_fbd}', f'TBMS-PB-DI')
                replace_var(f'xx-PB-DI_{ind_fbd}-{ind_sig_asal}', f'{s_a}-PB-DI')
                if s_a in signal_tujuan_cf:
                    replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_asal}', f'{s_a}-CF-TBMS-CTRL')
                else:
                    replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_asal}', f'{s_a}-TBMS-CTRL')
                ind_sig_asal += 1
                if ind_sig_asal == 11:
                    ind_fbd += 1
                    ind_sig_asal = 1
            for ind_x in range(1, 11):
                for ind_y in range(1, 11):
                    replace_var(f'xx-PB-DI_{ind_x}', f'HAPUS FBD INI')
                    replace_var(f'xx-PB-DI_{ind_x}-{ind_y}', f'FALSE')
                    replace_var(f'xx-CTRL_{ind_x}-{ind_y}', f'HAPUS VARIABLE INI')

            df_logic.to_csv(
                directory_simpan + f"\\{fbd_tujuan} - Kombinasi Tombol TBMS + Sinyal Tujuan.csv",
                index=False)


            ########################## Generate PB CTRL kombinasi tombol TUR sinyal Asal ##############################
            # list semua signal asal emergency
            signal_asal = sorted(list(set([s[2] for s in it1 if "-R" not in s[18]])))
            ind_fbd = 1
            ind_sig_asal = 1
            df_logic = pd.read_csv(referensi_csv + f"\\{fbd_tujuan}.csv")

            # fungsi menyingkat perubahan variable data frame
            def replace_var(var_awal, var_baru):
                df_logic['New Name'] = df_logic['New Name'].replace({var_awal: var_baru})

            for s_a in signal_asal:
                replace_var(f'xx-PB-DI_{ind_fbd}', f'TUR-PB-DI')
                replace_var(f'xx-PB-DI_{ind_fbd}-{ind_sig_asal}', f'{s_a}-PB-DI')
                replace_var(f'xx-CTRL_{ind_fbd}-{ind_sig_asal}', f'{s_a}-F-CTRL')
                ind_sig_asal += 1
                if ind_sig_asal == 11:
                    ind_fbd += 1
                    ind_sig_asal = 1
            for ind_x in range(1, 11):
                for ind_y in range(1, 11):
                    replace_var(f'xx-PB-DI_{ind_x}', f'HAPUS FBD INI')
                    replace_var(f'xx-PB-DI_{ind_x}-{ind_y}', f'FALSE')
                    replace_var(f'xx-CTRL_{ind_x}-{ind_y}', f'HAPUS VARIABLE INI')

            df_logic.to_csv(directory_simpan + f"\\{fbd_tujuan} - Kombinasi Tombol TUR + Sinyal Asal.csv", index=False)

        # Generate nV FC1 GLOB VAR & PB CTRL - nFC51 SW CTRL
        def generatenVFC1nFC51SWCTRL():
            allWesel = [w for w in pm if w[0].startswith("W")]
            allDeraileur = [w for w in pm if w[0].startswith("D")]
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allWesel), 10):
                dfLogic = pd.read_csv(referensi_csv + "\\nFC51 SW CTRL.csv")
                for y in range(10):

                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allWesel) % 10 != 0 and x == (math.floor(len(allWesel) / 10) * 10) and y == len(
                            allWesel) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-PB-DI_' + str(y + 1): allWesel[y + x][0] + '-PB-DI'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-SWRLSPB-CTRL_' + str(y + 1): allWesel[y + x][0] + '-SWRLSPB-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-B-CTRL_' + str(y + 1): allWesel[y + x][0] + '-B-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RST-CTRL_' + str(y + 1): allWesel[y + x][0] + '-RST-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-TRAIL-CTRL_' + str(y + 1): allWesel[y + x][0] + '-TRAIL-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-CAL-CTRL_' + str(y + 1): allWesel[y + x][0] + '-CAL-CTRL'})
                    track1 = allWesel[y + x][1]
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'xx-TP_' + str(y + 1) + '-' + str(1): track1 + '-TP'})
                    if allWesel[y + x][2]:
                        track2 = allWesel[y + x][2]
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'xx-TP_' + str(y + 1) + '-' + str(2):track2 + '-TP'})
                    else:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'xx-TP_' + str(y + 1) + '-' + str(2): 'TRUE'})

                dfLogic.to_csv(
                    directory_simpan + "\\nFC51 SW CTRL WESEL " + str(x) + "-" + str(x + 10) + ".csv",
                    index=False)

            for x in range(0, len(allDeraileur), 10):
                dfLogic = pd.read_csv(referensi_csv + "\\nFC51 SW CTRL (DERAILEUR).csv")
                for y in range(10):

                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allDeraileur) % 10 != 0 and x == (math.floor(len(allDeraileur) / 10) * 10) and y == len(
                            allDeraileur) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-PB-DI_' + str(y + 1): allDeraileur[y + x][0] + '-PB-DI'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-B-CTRL_' + str(y + 1): allDeraileur[y + x][0] + '-B-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RST-CTRL_' + str(y + 1): allDeraileur[y + x][0] + '-RST-CTRL'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace({'xx-TP_' + str(y + 1) + '-' + str(1): 'TRUE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'xx-TP_' + str(y + 1) + '-' + str(2): 'TRUE'})

                dfLogic.to_csv(directory_simpan + "\\nFC51 SW CTRL (DERAILEUR)" + str(x) + "-" + str(
                    x + 10) + ".csv", index=False)

        # Generate nV FC1 GLOB VAR & PB CTRL - nFC53 RRLS PB CTRL
        def generatenVFC1nFC53RRLSPBCTRL():

            signalHR = list(set([signal[2] for signal in it1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in it1 if signal[5]]))
            signalER = list(set([signal[2] for signal in it1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in it1 if signal[7]]))

            # sinyal berangkat
            varEnumerated = sorted(list(set([it[15] for it in it1 if not it[15].startswith("A")])))
            jumlahGenFBD = 10
            FBDtujuan = "nFC53 RRLS PB CTRL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-RRLSPB-CTRL_{indexFBD}', f'{data_var}-RRLSPB-CTRL')
                        replace_var(f'J/JL/Lxx-PB-DI_{indexFBD}', f'{data_var}-PB-DI')
                        if data_var in signalHR: replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{data_var}-HR-DO')
                        if data_var in signalDR: replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{data_var}-DR-DO')
                        if data_var in signalER: replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{data_var}-ER-DO')
                        if data_var in signalGR: replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{data_var}-GR-DO')

                        index_TES = 1
                        arah = ""
                        track = ""
                        for it in it1:
                            if data_var in it[15]:
                                if "EAST" in it[-1]:
                                    arah = "E"
                                else:
                                    arah = "W"
                                if it[27]:
                                    track = it[20].split(" ")[-2]
                                else:
                                    track = it[20].split(" ")[-1]
                                if track.endswith("T"):
                                    track = track[:-1]
                                break
                        for it in it1:
                            if "(T)" in it[1] and data_var in it[15]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_TES}', f'{track}-T-{arah}S')
                                index_TES += 1
                                break
                        for it in it1:
                            if "(E)" in it[1] or "(CF)" in it[1]in it[1] and data_var in it[15]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_TES}', f'{track}-E-{arah}S')
                                index_TES += 1
                                break
                        for it in it1:
                            if "(S)" in it[1] and data_var in it[15]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_TES}', f'{track}-S-{arah}S')
                                index_TES += 1
                                break

                        index_rs = 1
                        for it in it1:
                            if it[15] == data_var and "(T)" not in it[1]:
                                cf = ""
                                if "(CF)" in it[1]:
                                    cf = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}', f'{it[2]}-{simp(data_var)}{cf}-RS')
                                index_rs += 1

                        replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')

                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-3', f'TRUE')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} Sinyal Berangkat {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            # sinyal Axx
            varEnumerated = sorted(list(set([it[15] for it in it1 if it[15].startswith("A")])))
            jumlahGenFBD = 10
            FBDtujuan = "nFC53 RRLS PB CTRL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-RRLSPB-CTRL_{indexFBD}', f'{data_var}-RRLSPB-CTRL')
                        replace_var(f'J/JL/Lxx-PB-DI_{indexFBD}', f'{data_var}-PB-DI')
                        if data_var in signalHR: replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{data_var}-HR-DO')
                        if data_var in signalDR: replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{data_var}-DR-DO')
                        if data_var in signalER: replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{data_var}-ER-DO')
                        if data_var in signalGR: replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{data_var}-GR-DO')

                        index_TES = 1
                        arah = ""
                        track = ""
                        for it in it1:
                            if data_var in it[15]:
                                if "EAST" in it[-1]:
                                    arah = "E"
                                else:
                                    arah = "W"
                                if it[27]:
                                    track = it[20].split(" ")[-2]
                                else:
                                    track = it[20].split(" ")[-1]
                                if track.endswith("T"):
                                    track = track[:-1]
                                break
                        for it in it1:
                            if "(T)" in it[1] and data_var in it[15]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_TES}', f'{track}-T-{arah}S')
                                index_TES += 1
                                break
                        for it in it1:
                            if "(E)" in it[1] or "(CF)" in it[1] in it[1] and data_var in it[15]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_TES}', f'{track}-E-{arah}S')
                                index_TES += 1
                                break

                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_TES}', f'{data_var}-{arah}FLR-DO')

                        index_rs = 1
                        for it in it1:
                            if it[15] == data_var and "(T)" not in it[1]:
                                cf = ""
                                if "(CF)" in it[1]:
                                    cf = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}', f'{it[2]}-{simp(data_var)}{cf}-RS')
                                index_rs += 1

                        replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')

                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-3', f'TRUE')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directory_simpan + f"\\{FBDtujuan} Sinyal Axx {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)

            # sinyal masuk
            varEnumerated = sorted(list(set([it[2] for it in it1 if "(T)" not in it[1] and "(S)" not in it[1] and not it[15].startswith("A")])))
            jumlahGenFBD = 10
            FBDtujuan = "nFC53 RRLS PB CTRL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-RRLSPB-CTRL_{indexFBD}', f'{data_var}-RRLSPB-CTRL')
                        replace_var(f'J/JL/Lxx-PB-DI_{indexFBD}', f'{data_var}-PB-DI')
                        if data_var in signalHR: replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{data_var}-HR-DO')
                        if data_var in signalDR: replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{data_var}-DR-DO')
                        if data_var in signalER: replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{data_var}-ER-DO')
                        if data_var in signalGR: replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{data_var}-GR-DO')

                        arah = ""
                        for it in it1:
                            if data_var in it[2]:
                                if "EAST" in it[-1]:
                                    arah = "E"
                                else:
                                    arah = "W"
                                break

                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-1', f'{data_var.replace("J", "A")}-{arah}S')

                        replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')

                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-3', f'TRUE')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directory_simpan + f"\\{FBDtujuan} Sinyal Masuk {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)


        # directori penyimpanan hasil generate
        directory_simpan = directory_simpan + "\\Non Vital\\nV FC1 GLOB VAR & PB CTRL\\"
        # buat directori penyimpanan hasil generate jika belum ada
        if not os.path.exists(directory_simpan):
            os.makedirs(directory_simpan)
        # directori referensi csv
        referensi_csv = referensi_csv + "\\Non Vital\\nV FC1 GLOB VAR & PB CTRL\\"

        generatenVFC1vSFC2EKR2()
        generatenVFC1vSFC2EKR6()
        generatenVFC1vSFC2TPBP()
        nfc1_fc54_pbctrl1()
        generatenVFC1nFC51SWCTRL()
        generatenVFC1nFC53RRLSPBCTRL()

    ################################### nV FC2 I/L ROUTE ###################################
    def nv_fc2_il_route(self, it1, it2, referensi_csv, directory_simpan, pm):
        # nV FC2 IL ROUTE - J/JL/L-S-AS
        def nv_fc2_tesas():
            listSAS = list(
                set([jl[2] + '-' + jl[1][jl[1].find('(') + 1:jl[1].find('(') + 2] + '-AS' for jl in it1 if
                     '(CF)' not in jl[1]]))

            dfLogic = pd.read_csv(referensi_csv + "\\TES-AS.csv")
            for i, sas in enumerate(listSAS):
                dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/L-T/E/S-AS_' + str(i + 1): sas})
            for i in range(len(listSAS), 100):
                dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/L-T/E/S-AS_' + str(i + 1): 'TRUE'})

            dfLogic.to_csv(directory_simpan + "\\TES-AS.csv", index=False)

        # nV FC2 IL ROUTE - nFC96 SW FUNCTION
        def nv_fc2_nfc96():
            # list variable semua wesel
            allWesel = list(set((' '.join([w[18].replace("-N", "").replace("-R", "") for w in it1])).split() +
                                (' '.join([w[7].replace("-N", "").replace("-R", "") for w in it2])).split()))
            # total output tergenerate (sum generated output)
            sGO = 10
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allWesel), sGO):
                dfLogic = pd.read_csv(referensi_csv + "\\nFC96 SW FUNCTION.csv")

                for y in range(sGO):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allWesel) % sGO != 0 and x == (math.floor(len(allWesel) / sGO) * sGO) and y == len(
                            allWesel) % sGO:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-L_' + str(y + 1): 'W' + allWesel[y + x] + '-L'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-NWZ_' + str(y + 1): 'W' + allWesel[y + x] + '-NWZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RWZ_' + str(y + 1): 'W' + allWesel[y + x] + '-RWZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-R_' + str(y + 1): 'W' + allWesel[y + x] + '-R'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-N_' + str(y + 1): 'W' + allWesel[y + x] + '-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-OOC_' + str(y + 1): 'W' + allWesel[y + x] + '-OOC'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-SWINIT_' + str(y + 1): 'W' + allWesel[y + x] + '-SWINIT'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-TPZ_' + str(y + 1): 'W' + allWesel[y + x] + '-TPZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-SWRLS_' + str(y + 1): 'W' + allWesel[y + x] + '-SWRLS'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-B-N_' + str(y + 1): 'W' + allWesel[y + x] + '-B-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-B-R_' + str(y + 1): 'W' + allWesel[y + x] + '-B-R'})

                dfLogic.to_csv(
                    directory_simpan + "\\nFC96 SW FUNCTION " + str(x) + "-" + str(
                        x + sGO) + ".csv",
                    index=False)

        # nV FC2 IL ROUTE - nFC98 I/L R
        def nv_fc2_nfc98():
            all_empl_langsir = sorted(list(set([it[20].replace("T", "").split(" ")[-1] for it in it1 if "(S)" in it[1] and it[27]])))
            varEnumerated = [it for it in it1 if ("(E)" in it[1] or "(CF)" in it[1])]
            jumlahGenFBD = 5
            FBDtujuan = "nFC98 IL R"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        os_track = data_var[20].replace("T", "").split(" ")[0]
                        emplacement_track = data_var[20].replace("T", "").split(" ")[-1]
                        arah_rute = data_var[-1]
                        track_rute = data_var[20].replace("T", "").split(" ")[:-1]
                        track_rute_all = data_var[20].replace("T", "").split(" ")
                        wesel_rute = data_var[18].split(" ")
                        deraileur_rute = []
                        if data_var[19]:
                            deraileur_rute = data_var[19].split(" ")
                        rute_langsungan = [it[0] for it in it1 if "-R" not in it[18] and (sinyal_asal == it[15] or sinyal_tujuan == it[2])]


                        cf = ""
                        if "(CF)" in data_var[1]:
                            cf = "-CF"

                        replace_var(f'J/JL/Lxx-xx-B_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}{cf}-B')
                        replace_var(f'J/JL/Lxx-RRLS_{indexFBD}', f'{data_var[15]}-RRLS')

                        ################################### conflict subroute rute #####################################
                        index = 1
                        index_es = 1
                        index_ws = 1

                        t_stop = False
                        e_stop = False
                        s_stop = False
                        for it in it1:
                            if it[27]: track_cek = it[20].replace("T", "").split(" ")[:-1]
                            else: track_cek = it[20].replace("T", "").split(" ")

                            if os_track in track_cek and arah_rute != it[-1]:
                                arah_conflict = ""
                                if arah_rute == "EAST":
                                    arah_conflict = "W"
                                    index = index_ws
                                else:
                                    arah_conflict = "E"
                                    index = index_es

                                if "(T)" in it[1] and not t_stop:
                                    replace_var(f'xx-E/T/S-{arah_conflict}S_{indexFBD}-{index}', f'{os_track}-T-{arah_conflict}S')
                                    t_stop = True
                                    index += 1
                                if ("(E)" in it[1] or "(CF)" in it[1]) and not e_stop:
                                    replace_var(f'xx-E/T/S-{arah_conflict}S_{indexFBD}-{index}', f'{os_track}-E-{arah_conflict}S')
                                    e_stop = True
                                    index += 1
                                if "(S)" in it[1] and not s_stop:
                                    replace_var(f'xx-E/T/S-{arah_conflict}S_{indexFBD}-{index}', f'{os_track}-S-{arah_conflict}S')
                                    s_stop = True
                                    index += 1
                                if arah_rute == "EAST":
                                    index_ws = index
                                else:
                                    index_es = index

                        if sinyal_tujuan.startswith("A") and arah_rute == "EAST":
                            replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_ws}', f'{sinyal_tujuan}-WS')
                            index_ws += 1
                        if sinyal_tujuan.startswith("A") and arah_rute == "WEST":
                            replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_es}', f'{sinyal_tujuan}-ES')
                            index_es += 1

                        trackbemplist = []
                        for track in track_rute_all:
                            if track in all_empl_langsir:
                                for it in it1:
                                    if track == it[20].replace("T", "").split(" ")[-1] and "(S)" in it[1] and it[20].replace("T", "").split(" ")[-2] in track_rute_all:
                                        track_before_empl = it[20].replace("T", "").split(" ")[-2]

                                        if it[-1] == "EAST": arah_conflict = "E"
                                        else: arah_conflict = "W"

                                        if f'{track_before_empl}-S-{arah_conflict}S' not in trackbemplist:

                                            if it[-1] == "EAST": index = index_es
                                            else: index = index_ws
                                            replace_var(f'xx-E/T/S-{arah_conflict}S_{indexFBD}-{index}', f'{track_before_empl}-S-{arah_conflict}S')
                                            trackbemplist.append(f'{track_before_empl}-S-{arah_conflict}S')
                                            index += 1
                                            if it[-1] == "EAST": index_es = index
                                            else: index_ws = index

                        #################################### conflict ELAS WLAS ########################################
                        if arah_rute == "EAST" and not sinyal_tujuan.startswith("A"):
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data[20].replace("T", "").split(" ")[-1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-T-ELAS/WLAS_{indexFBD}', f'{emplacement_track}-T-WLAS')
                                    break
                        if arah_rute == "WEST" and not sinyal_tujuan.startswith("A"):
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data[20].replace("T", "").split(" ")[-1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-T-ELAS/WLAS_{indexFBD}', f'{emplacement_track}-T-ELAS')
                                    break

                        ######################################### conflict RS ##########################################

                        index_rs = 1
                        for it_data in it1:
                            if sinyal_asal == it_data[15] and "(T)" not in it_data[1] and normalize_track(it_data[0]) not in rute_langsungan:
                                cf_conflict = ""
                                if "(CF)" in it_data[1]:  cf_conflict = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}', f'{it_data[2]}-{simp(it_data[15])}{cf_conflict}-RS')
                                index_rs += 1
                            if sinyal_tujuan == it_data[2] and "(T)" not in it_data[1] and normalize_track(it_data[0]) not in rute_langsungan:
                                cf_conflict = ""
                                if "(CF)" in it_data[1]:  cf_conflict = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}', f'{it_data[2]}-{simp(it_data[15])}{cf_conflict}-RS')
                                index_rs += 1

                        ######################################## syarat wesel ##########################################
                        index_wesel = 1
                        for w in wesel_rute:
                            replace_var(f'Wxx-B-R/N_{indexFBD}-{index_wesel}', f'W{w[:w.find("-")]}-B-{w[-1]}')
                            index_wesel += 1

                        #################################### conflict emplacement ######################################
                        track_conflict_empl = ""
                        if not sinyal_tujuan.startswith("A"):
                            for it_data in it1:
                                if (arah_rute == "EAST" and it_data[-1] == "WEST") or (arah_rute == "WEST" and it_data[-1] == "EAST"):
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        track_conflict_empl = it_data[20].replace("T", "").split(" ")[-2]
                                        break
                            index_esws = 1
                            for it_data in it1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{track_conflict_empl}-T-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{track_conflict_empl}-T-ES')
                                            index_esws += 1
                                            break
                            for it_data in it1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{track_conflict_empl}-E-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',f'{track_conflict_empl}-E-ES')
                                            index_esws += 1
                                            break
                            for it_data in it1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',f'{track_conflict_empl}-S-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',f'{track_conflict_empl}-S-ES')
                                            index_esws += 1
                                            break

                        # Generate WP back
                        # 1.cari wesel yang berada dalam 1 track
                        wesel_on_track = [w[0].replace("W", "") for w in pm if (track_conflict_empl == w[1] or track_conflict_empl == w[2]) and track_conflict_empl]
                        # cari posisi wesel tersebut di interlocking table jika berada sama2 dengan indikasi wesel yang di generate
                        all_wesel_pos = []
                        for wt in wesel_on_track:
                            for it in it1:
                                if wt in it[18] and emplacement_track == it[20].replace("T", "").split(" ")[-1]:
                                    for w_tes in it[18].split(" "):
                                        if wt == w_tes.replace("-R", "").replace("-N", ""):
                                            all_wesel_pos.append(w_tes)
                        all_wesel_pos = sorted(list(set(all_wesel_pos)))
                        # masukan posisi wesel jika saat bersamaan dengan wesel indikasi, wesel tersebut hanya mengarah ke 1 arah saja
                        index_wp_back = 1
                        for w in wesel_on_track:
                            if not (w + "-R" in all_wesel_pos and w + "-N" in all_wesel_pos):
                                if w + "-R" in all_wesel_pos:
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wp_back}', f'W{w}-NWZ')
                                    index_wp_back += 1
                                if w + "-N" in all_wesel_pos:
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wp_back}', f'W{w}-RWZ')
                                    index_wp_back += 1

                        ######################################## conflict deraileur ###########################################
                        if deraileur_rute != []:
                            index_deraileur = 1
                            for d in deraileur_rute:
                                replace_var(f'Dxx-B-N/R_{indexFBD}-{index_deraileur}',f'{d[:-2]}-B-{d[-1]}')
                                index_deraileur += 1


                        ######################################## normalisasi ###########################################
                        for index in range(1, 11):
                            replace_var(f'xx-E/T/S-WS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-E/T/S-ES_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Dxx-B-N/R_{indexFBD}-{index}', f'TRUE')
                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Wxx-B-R/N_{indexFBD}-{index}', f'TRUE')
                        replace_var(f'xx-T-ELAS/WLAS_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-3', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nV FC2 IL ROUTE - nFC98 I/L R SHUNT
        def nv_fc2_nfc99():
            varEnumerated = [it for it in it1 if "(S)" in it[1]]
            jumlahGenFBD = 5
            FBDtujuan = "nFC99 IL R SHUNT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        os_track = data_var[20].replace("T", "").split(" ")[0]
                        emplacement_track = data_var[20].replace("T", "").split(" ")[-1]
                        arah_rute = data_var[-1]
                        track_rute = data_var[20].replace("T", "").split(" ")[:-1]
                        track_rute_all = data_var[20].replace("T", "").split(" ")
                        wesel_rute = data_var[18].split(" ")
                        deraileur_rute = []
                        if data_var[19]:
                            deraileur_rute = data_var[19].split(" ")

                        if len(track_rute_all) == 1:
                            trackujung = track_rute_all
                        elif data_var[27]:
                            trackujung = track_rute_all[-2]
                        else:
                            trackujung = track_rute_all[-1]
                        cf = ""
                        # if "(CF)" in data_var[1]:
                        #     cf = "-CF"

                        replace_var(f'J/JL/Lxx-xx-B_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}{cf}-B')

                        # conflict WS
                        index_WS = 1
                        if arah_rute == "EAST":
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_WS}', f'{os_track}-T-WS')
                                        index_WS += 1
                                        break
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data != data_var and ("(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_WS}', f'{os_track}-E-WS')
                                        index_WS += 1
                                        break
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data != data_var and "(S)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_WS}', f'{os_track}-S-WS')
                                        index_WS += 1
                                        break
                        if arah_rute == "WEST":
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_WS}', f'{trackujung}-T-WS')
                                        index_WS += 1
                                        break
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data != data_var and ("(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_WS}', f'{trackujung}-E-WS')
                                        index_WS += 1
                                        break

                        # conflict ES
                        index_ES = 1
                        if arah_rute == "WEST":
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_ES}', f'{os_track}-T-ES')
                                        index_ES += 1
                                        break
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data != data_var and (
                                        "(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_ES}', f'{os_track}-E-ES')
                                        index_ES += 1
                                        break
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data != data_var and "(S)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_ES}', f'{os_track}-S-ES')
                                        index_ES += 1
                                        break
                        if arah_rute == "EAST":
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_ES}', f'{trackujung}-T-ES')
                                        index_ES += 1
                                        break
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data != data_var and (
                                        "(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_ES}', f'{trackujung}-E-ES')
                                        index_ES += 1
                                        break

                        # conflict ELAS WLAS
                        if arah_rute == "EAST":
                            for it_data in it1:
                                if it_data[-1] == "WEST" and it_data[20].replace("T", "").split(" ")[
                                    -1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-E/T/S-WS_{indexFBD}-{index_WS}', f'{emplacement_track}-T-WLAS')
                                    index_WS += 1
                                    break
                        if arah_rute == "WEST":
                            for it_data in it1:
                                if it_data[-1] == "EAST" and it_data[20].replace("T", "").split(" ")[
                                    -1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-E/T/S-ES_{indexFBD}-{index_ES}', f'{emplacement_track}-T-ELAS')
                                    index_ES += 1
                                    break

                        index_rs = 1
                        for it_data in it1:
                            if sinyal_tujuan == it_data[2] and "(T)" not in it_data[1] and "(S)" not in it_data[1]:
                                CF = ""
                                if "(CF)" in it_data[1]:  CF = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}',
                                            f'{it_data[2]}-{simp(it_data[15])}{CF}-RS')
                                index_rs += 1

                            if sinyal_asal == it_data[15] and "(T)" not in it_data[1] and "(S)" not in it_data[1]:
                                CF = ""
                                if "(CF)" in it_data[1]:  CF = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}',
                                            f'{it_data[2]}-{simp(it_data[15])}{CF}-RS')
                                index_rs += 1

                        replace_var(f'J/JL/Lxx-RRLS_{indexFBD}', f'{data_var[15]}-RRLS')

                        index_wesel = 1
                        for w in wesel_rute:
                            replace_var(f'Wxx-B-R/N_{indexFBD}-{index_wesel}', f'W{w[:w.find("-")]}-B-{w[-1]}')
                            index_wesel += 1

                        track_conflict_empl = ""
                        if not sinyal_tujuan.startswith("A"):
                            for it_data in it1:
                                if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                                        arah_rute == "WEST" and it_data[-1] == "EAST"):
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        track_conflict_empl = it_data[20].replace("T", "").split(" ")[-2]
                                        break
                            index_esws = 1
                            for it_data in it1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-T-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-T-ES')
                                            index_esws += 1
                                            break
                            for it_data in it1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-E-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-E-ES')
                                            index_esws += 1
                                            break
                            for it_data in it1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-S-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-S-ES')
                                            index_esws += 1
                                            break

                        # Generate WP back
                        # 1.cari wesel yang berada dalam 1 track
                        wesel_on_track = [w[0].replace("W", "") for w in pm if (
                                    track_conflict_empl == w[1] or track_conflict_empl == w[
                                2]) and track_conflict_empl]
                        # cari posisi wesel tersebut di interlocking table jika berada sama2 dengan indikasi wesel yang di generate
                        all_wesel_pos = []
                        for wt in wesel_on_track:
                            for it in it1:
                                if wt in it[18] and emplacement_track == \
                                        it[20].replace("T", "").split(" ")[-1]:
                                    for w_tes in it[18].split(" "):
                                        if wt == w_tes.replace("-R", "").replace("-N", ""):
                                            all_wesel_pos.append(w_tes)
                        all_wesel_pos = sorted(list(set(all_wesel_pos)))
                        # masukan posisi wesel jika saat bersamaan dengan wesel indikasi, wesel tersebut hanya mengarah ke 1 arah saja
                        index_wp_back = 1
                        for w in wesel_on_track:
                            if not (w + "-R" in all_wesel_pos and w + "-N" in all_wesel_pos):
                                if w + "-R" in all_wesel_pos:
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wp_back}',
                                                f'W{w}-NWZ')
                                    index_wp_back += 1
                                if w + "-N" in all_wesel_pos:
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wp_back}',
                                                f'W{w}-RWZ')
                                    index_wp_back += 1

                        if deraileur_rute != []:
                            index_deraileur = 1
                            for d in deraileur_rute:
                                replace_var(f'Dxx-B-N/R_{indexFBD}-{index_deraileur}', f'{d[:-2]}-B-{d[-1]}')
                                index_deraileur += 1

                        replace_var(f'xx-TP_{indexFBD}', f'{os_track}-TP')

                        for index in range(1, 11):
                            replace_var(f'xx-E/T/S-WS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-E/T/S-ES_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Dxx-B-N/R_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')
                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Wxx-B-R/N_{indexFBD}-{index}', f'TRUE')

                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-3', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nV FC2 IL ROUTE - nFC56 SIG BLOCK
        def nv_fc2_nfc56():
            signalHR = list(set([signal[2] for signal in it1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in it1 if signal[5]]))
            signalER = list(set([signal[2] for signal in it1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in it1 if signal[7]]))

            # SIGNAL 3 ASPEK -B
            varEnumerated = sorted(signalHR)
            jumlahGenFBD = 10
            FBDtujuan = "nFC56 SIG BLOCK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-B_{indexFBD}', f'{data_var}-B')
                        TUR = False

                        index_rs = 1
                        for it_data in it1:
                            if it_data[2] == data_var and it_data[4]:
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}', f'{data_var}-{simp(it_data[15])}-RS')
                                index_rs += 1
                                if "-R" not in it_data[18]:
                                    TUR = True

                        for it_data in it1:
                            if it_data[2] == data_var and it_data[4]:
                                os_track = it_data[20].split(" ")[0]
                                if os_track.endswith("T"):
                                    os_track = os_track[:-1]
                                replace_var(f'xx-TP_{indexFBD}', f'{os_track}-TP')
                                break

                        replace_var(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{data_var}-HR-DO')
                        replace_var(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'{data_var}-HR-RD')

                        if TUR:
                            replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'{data_var}-F-RS')
                            replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'{data_var}-ECR')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                        replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} -B 3 aspek {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            # SIGNAL 2 ASPEK -B
            varEnumerated = sorted([s for s in signalDR if s not in signalHR])
            jumlahGenFBD = 10
            FBDtujuan = "nFC56 SIG BLOCK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-B_{indexFBD}', f'{data_var}-B')
                        TUR = False

                        index_rs = 1
                        for it_data in it1:
                            if it_data[2] == data_var and it_data[5]:
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}',
                                            f'{data_var}-{simp(it_data[15])}-RS')
                                index_rs += 1
                                if "-R" not in it_data[18]:
                                    TUR = True

                        for it_data in it1:
                            if it_data[2] == data_var and it_data[5]:
                                os_track = it_data[20].split(" ")[0]
                                if os_track.endswith("T"):
                                    os_track = os_track[:-1]
                                replace_var(f'xx-TP_{indexFBD}', f'{os_track}-TP')
                                break

                        replace_var(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{data_var}-DR-DO')
                        replace_var(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'{data_var}-DR-RD')

                        if TUR:
                            replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'{data_var}-F-RS')
                            replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'{data_var}-ECR')
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{data_var}-EC-G-RD')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                        replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} -B 2 aspek {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            # SIGNAL HIJAU 3 ASPEK -D-B
            varEnumerated = sorted([s for s in signalDR if s in signalHR])
            jumlahGenFBD = 10
            FBDtujuan = "nFC56 SIG BLOCK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-B_{indexFBD}', f'{data_var}-D-B')
                        TUR = False

                        index_rs = 1
                        for it_data in it1:
                            if it_data[2] == data_var and it_data[5]:
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}',
                                            f'{data_var}-{simp(it_data[15])}-RS')
                                index_rs += 1
                                if "-R" not in it_data[18]:
                                    TUR = True

                        for it_data in it1:
                            if it_data[2] == data_var and it_data[5]:
                                os_track = it_data[20].split(" ")[0]
                                if os_track.endswith("T"):
                                    os_track = os_track[:-1]
                                replace_var(f'xx-TP_{indexFBD}', f'{os_track}-TP')
                                break

                        replace_var(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{data_var}-DR-DO')
                        replace_var(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'{data_var}-DR-RD')

                        if TUR:
                            replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'{data_var}-F-RS')
                            replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'{data_var}-ECR')
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{data_var}-EC-G-RD')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                        replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} -D-B {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            # SIGNAL LANGSIR -S-B
            varEnumerated = sorted(signalGR)
            jumlahGenFBD = 10
            FBDtujuan = "nFC56 SIG BLOCK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-B_{indexFBD}', f'{data_var}-S-B')
                        TUR = False

                        index_rs = 1
                        for it_data in it1:
                            if it_data[2] == data_var and it_data[7]:
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}',
                                            f'{data_var}-{simp(it_data[15])}-RS')
                                index_rs += 1
                                if "-R" not in it_data[18]:
                                    TUR = True
                        for it_data in it1:
                            if data_var in it_data[21].split(" "):
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}',
                                            f'{data_var}-{simp(it_data[15])}-2-RS')
                                index_rs += 1

                        for it_data in it1:
                            if it_data[2] == data_var and it_data[7]:
                                os_track = it_data[20].split(" ")[0]
                                if os_track.endswith("T"):
                                    os_track = os_track[:-1]
                                replace_var(f'xx-TP_{indexFBD}', f'{os_track}-TP')
                                break

                        replace_var(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{data_var}-GR-DO')
                        replace_var(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'{data_var}-GR-RD')

                        if TUR:
                            replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'{data_var}-F-RS')
                            replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'{data_var}-ECR')
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{data_var}-EC-G-RD')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                        replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} -S-B {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            # SINYAL EMERGENCY -E-B
            varEnumerated = sorted(signalER)
            jumlahGenFBD = 10
            FBDtujuan = "nFC56 SIG BLOCK EMERGENCY"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensi_csv + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-E-B_{indexFBD}', f'{data_var}-E-B')

                        index_rs = 1
                        for it_data in it1:
                            if it_data[2] == data_var and it_data[6]:
                                cf = ""
                                if "(CF)" in it_data[1]:
                                    cf = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index_rs}', f'{data_var}-{simp(it_data[15])}{cf}-RS')
                                index_rs += 1

                        replace_var(f'J/JL/Lxx-E-CTRL_{indexFBD}', f'{data_var}-E-CTRL')
                        replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{data_var}-ER-DO')
                        replace_var(f'J/JL/Lxx-ER-RD_{indexFBD}', f'{data_var}-ER-RD')

                        for index in range(1, 21):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directory_simpan + f"\\{FBDtujuan} -E-B {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directory_simpan = directory_simpan + "\\Non Vital\\nV FC2 IL ROUTE"
        if not os.path.exists(directory_simpan):
            os.makedirs(directory_simpan)

        referensi_csv = referensi_csv + "\\Non Vital\\nV FC2 IL ROUTE"

        nv_fc2_tesas()
        nv_fc2_nfc96()
        nv_fc2_nfc98()
        nv_fc2_nfc99()
        nv_fc2_nfc56()

    ############################## nV FC3 I/L POINT & PARAMETER ############################
    def nv_fc3_il_point_parameter(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # nFC57 SW ILOCK
        def nfc57_sw_ilock():
            # list variable semua wesel
            allWesel = sorted(
                list(set((' '.join([w[18].replace("-N", "").replace("-R", "") for w in IT1])).split() +
                         (' '.join([w[7].replace("-N", "").replace("-R", "") for w in IT2])).split())))
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allWesel), 5):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC57 SW ILOCK.csv")

                for y in range(5):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allWesel) % 5 != 0 and x == (math.floor(len(allWesel) / 5) * 5) and y == len(
                            allWesel) % 5:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-CAL-CTRL_' + str(y + 1): 'W' + allWesel[y + x] + '-CAL-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-B-CTRL_' + str(y + 1): 'W' + allWesel[y + x] + '-B-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RST-CTRL_' + str(y + 1): 'W' + allWesel[y + x] + '-RST-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-TRAIL-CTRL_' + str(y + 1): 'W' + allWesel[y + x] + '-TRAIL-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-NWZ_' + str(y + 1): 'W' + allWesel[y + x] + '-NWZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RWZ_' + str(y + 1): 'W' + allWesel[y + x] + '-RWZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-NWP_' + str(y + 1): 'W' + allWesel[y + x] + '-NWP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RWP_' + str(y + 1): 'W' + allWesel[y + x] + '-RWP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-NWC_' + str(y + 1): 'W' + allWesel[y + x] + '-NWC'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RWC_' + str(y + 1): 'W' + allWesel[y + x] + '-RWC'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-L_' + str(y + 1): 'W' + allWesel[y + x] + '-L'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-NW-TE_' + str(y + 1): 'W' + allWesel[y + x] + '-NW-TE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RW-TE_' + str(y + 1): 'W' + allWesel[y + x] + '-RW-TE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-OOC_' + str(y + 1): 'W' + allWesel[y + x] + '-OOC'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-OOC-RD_' + str(y + 1): 'W' + allWesel[y + x] + '-OOC-RD'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RS-N_' + str(y + 1): 'W' + allWesel[y + x] + '-RS-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RS-R_' + str(y + 1): 'W' + allWesel[y + x] + '-RS-R'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-OL-N_' + str(y + 1): 'W' + allWesel[y + x] + '-OL-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-OL-R_' + str(y + 1): 'W' + allWesel[y + x] + '-OL-R'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-N-REQ_' + str(y + 1): 'W' + allWesel[y + x] + '-N-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-R-REQ_' + str(y + 1): 'W' + allWesel[y + x] + '-R-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-BACK-TO-N_' + str(y + 1): 'W' + allWesel[y + x] + '-BACK-TO-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-BACK-TO-R_' + str(y + 1): 'W' + allWesel[y + x] + '-BACK-TO-R'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-N_' + str(y + 1): 'W' + allWesel[y + x] + '-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-R_' + str(y + 1): 'W' + allWesel[y + x] + '-R'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-N-BLOCK_' + str(y + 1): 'W' + allWesel[y + x] + '-N-BLOCK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-R-BLOCK_' + str(y + 1): 'W' + allWesel[y + x] + '-R-BLOCK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-BLOCK_' + str(y + 1): 'W' + allWesel[y + x] + '-BLOCK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-START_' + str(y + 1): 'W' + allWesel[y + x] + '-START'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-SWINIT_' + str(y + 1): 'W' + allWesel[y + x] + '-SWINIT'})

                    # generate start wesel
                    for i, w in enumerate(allWesel):
                        if w == allWesel[y + x]:
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'Wxx-START_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})
                        else:
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'Wxx-START_' + str(y + 1) + '-' + str(i + 1): 'W' + w + '-START'})
                    for i in range(len(allWesel), 50):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'Wxx-START_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})

                    wesel = allWesel[y + x]
                    # generate rute yang memanggil wesel
                    listRSN = [r[2] + '-' + simp(r[15]) + '-RS' for r in IT1 if
                               wesel + "-N" in r[18] and '(CF)' not in r[1]] + \
                              [r[2] + '-' + simp(r[15]) + '-CF-RS' for r in IT1 if
                               wesel + "-N" in r[18] and '(CF)' in r[1]]
                    listRSN = sorted(list(set(listRSN)))
                    for i, rs in enumerate(listRSN):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RSN_' + str(y + 1) + '-' + str(i + 1): rs})
                    for i in range(len(listRSN), 50):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RSN_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})

                    listRSR = [r[2] + '-' + simp(r[15]) + '-RS' for r in IT1 if
                               wesel + "-R" in r[18] and '(CF)' not in r[1]] + \
                              [r[2] + '-' + simp(r[15]) + '-CF-RS' for r in IT1 if
                               wesel + "-R" in r[18] and '(CF)' in r[1]]
                    listRSR = sorted(list(set(listRSR)))
                    for i, rs in enumerate(listRSR):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RSR_' + str(y + 1) + '-' + str(i + 1): rs})
                    for i in range(len(listRSR), 50):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RSR_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})

                    # generate luncuran yang memanggil wesel
                    listOLN = [r[2] + '-' + simp(r[6]) + '-T-REQ' for r in IT2 if wesel + "-N" in r[7]]
                    listOLN = sorted(list(set(listOLN)))
                    for i, treq in enumerate(listOLN):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-T-REQN_' + str(y + 1) + '-' + str(i + 1): treq})
                    for i in range(len(listOLN), 10):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-T-REQN_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})

                    listOLR = [r[2] + '-' + simp(r[6]) + '-T-REQ' for r in IT2 if wesel + "-R" in r[7]]
                    listOLR = sorted(list(set(listOLR)))
                    for i, treq in enumerate(listOLR):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-T-REQR_' + str(y + 1) + '-' + str(i + 1): treq})
                    for i in range(len(listOLR), 10):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-T-REQR_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})

                dfLogic.to_csv(directorySimpan + "\\nFC57 SW ILOCK " + str(x) + "-" + str(
                    x + 5) + ".csv", index=False)

        # nFC89 DERAILEUR ILOCK
        def nfc89_deraileur_ilock():
            # list variable semua wesel
            allDeraileur = list(
                set((' '.join([d[19].replace("-N", "").replace("-R", "").strip() for d in IT1])).split() +
                    (' '.join([d[8].replace("-N", "").replace("-R", "").strip() for d in IT2])).split()))

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allDeraileur), 5):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC89 DERAILEUR ILOCK.csv")

                for y in range(5):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allDeraileur) % 5 != 0 and x == (math.floor(len(allDeraileur) / 5) * 5) and y == len(
                            allDeraileur) % 5:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-RST-CTRL_' + str(y + 1): allDeraileur[y + x] + '-RST-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-B-CTRL_' + str(y + 1): allDeraileur[y + x] + '-B-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-REL-REQ_' + str(y + 1): allDeraileur[y + x] + '-REL-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-R-OK_' + str(y + 1): allDeraileur[y + x] + '-R-OK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-R-N_' + str(y + 1): allDeraileur[y + x] + '-R-N'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-NP_' + str(y + 1): allDeraileur[y + x] + '-NP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-RP_' + str(y + 1): allDeraileur[y + x] + '-RP'})

                    deraileur = allDeraileur[x + y]
                    listRSN = [r[2] + '-' + simp(r[15]) + '-RS' for r in IT1 if
                               deraileur + "-N" in r[19] and '(CF)' not in r[1]] + \
                              [r[2] + '-' + simp(r[15]) + '-CF-RS' for r in IT1 if
                               deraileur + "-N" in r[19] and '(CF)' in r[1]] + \
                              [r[2] + '-' + simp(r[6]) + '-T-REQ' for r in IT2 if deraileur + "-N" in r[8]]

                    listRSN = sorted(list(set(listRSN)))

                    for i, rs in enumerate(listRSN):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RSN_' + str(y + 1) + '-' + str(i + 1): rs})
                    for i in range(len(listRSN), 50):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RSN_' + str(y + 1) + '-' + str(i + 1): 'FALSE'})

                dfLogic.to_csv(
                    directorySimpan + "\\nFC89 DERAILEUR ILOCK " + str(x) + "-" + str(
                        x + 5) + ".csv", index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC3 IL POINT & PARAMETER"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC3 IL POINT & PARAMETER"

        nfc57_sw_ilock()
        nfc89_deraileur_ilock()

    ############################## nV FC4 TE ROUTE REQ ############################
    def nv_fc4_te_route_req(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # Generate nV FC4 T/E ROUTE REQ FBD nFC57 SW ILOCK - nFC84 T E ROUTE REQ
        def generatenVFC4nFC84():
            allRute = [r[1] for r in IT1]
            ruteList = [r for r in IT1 if
                        ('(E)' not in r[1] or ('(E)' in r[1] and r[1] not in allRute)) and '(S)' not in r[1]]
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(ruteList), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC84 TE ROUTE REQ.csv")
                for y in range(10):

                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(ruteList) % 10 != 0 and x == (math.floor(len(ruteList) / 10) * 10) and y == len(
                            ruteList) % 10:
                        break

                    CF = ''
                    # jik rute Contra Flow maka tambahkan -CF di variable
                    if '(CF)' in ruteList[y + x][1]:
                        CF = '-CF'

                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-CTRL_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + CF + '-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-RST-CTRL_' + str(y + 1): ruteList[y + x][2] + '-RST-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-E-CTRL_' + str(y + 1): ruteList[y + x][2] + '-E-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-B_' + str(y + 1): ruteList[y + x][
                                                                                                          2] + '-' + simp(
                        ruteList[y + x][15]) + CF + '-B'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TPF_' + str(y + 1): ruteList[y + x][23].replace('T', '') + '-TP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TPB_' + str(y + 1): ruteList[y + x][20].replace('T', '').split(" ")[0] + '-TP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TPBP_' + str(y + 1): ruteList[y + x][20].replace('T', '').split(" ")[0] + '-TPBP'})

                    # jika rute Contra Flow maka HR/DR, B, P dan F-RS di isi False
                    if '(CF)' in ruteList[y + x][1]:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-HR/DR-DO_' + str(y + 1): 'FALSE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-B_' + str(y + 1): 'FALSE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-P_' + str(y + 1): 'FALSE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-F-RS_' + str(y + 1): 'FALSE'})
                    else:
                        # jika terdapat sinyal kuning maka generate HR, jika hijau generate DR
                        if 'V' in ruteList[y + x][4]:
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-HR/DR-DO_' + str(y + 1): ruteList[y + x][2] + '-HR-DO'})
                        elif 'V' in ruteList[y + x][5]:
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-HR/DR-DO_' + str(y + 1): ruteList[y + x][2] + '-DR-DO'})

                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-B_' + str(y + 1): ruteList[y + x][2] + '-B'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-P_' + str(y + 1): ruteList[y + x][2] + '-' + simp(ruteList[y + x][15]) + '-P'})

                    # jika rute TUR isi F-RS
                    if "-R" not in ruteList[y + x][18]:
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-F-RS_' + str(y + 1): ruteList[y + x][2] + '-F-RS'})
                    else:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-F-RS_' + str(y + 1): 'FALSE'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-RS_' + str(y + 1): ruteList[y + x][
                                                                                                           2] + '-' + simp(ruteList[y + x][15]) + CF + '-RS'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-E-REQ_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + CF + '-E-REQ'})

                    # Generate T-REQ di rute normal saja
                    if '(T)' in ruteList[y + x][1]:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-T-REQ_' + str(y + 1):
                                                                               ruteList[y + x][2] + '-' + simp(
                                                                                   ruteList[y + x][15]) + '-T-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-E-COUNT_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + CF + '-E-COUNT'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-E-RST-TE_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + CF + '-E-RST-TE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-E-B_' + str(y + 1): ruteList[y + x][2] + '-E-B'})
                dfLogic.to_csv(directorySimpan + "\\nFC84 TE ROUTE REQ " + str(x) + "-" + str(x + 10) + ".csv", index=False)

        # Generate nV FC4 T/E ROUTE REQ FBD nFC57 SW ILOCK - nFC103 F_RS
        def generatenVFC4nFC103():
            ruteList = [r for r in IT1 if "-R" not in  r[18]]
            # pecah hasil generator menjadi per 4 output
            for x in range(0, len(ruteList), 4):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC103 F_RS.csv")
                for y in range(4):
                    # jika jumlah rute tidak kelipatan 4 dan iterasi terakhir selesaikan looping
                    if len(ruteList) % 4 != 0 and x == (math.floor(len(ruteList) / 4) * 4) and y == len(ruteList) % 4:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-F-CTRL_' + str(y + 1): ruteList[y + x][2] + '-F-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-RST-CTRL_' + str(y + 1): ruteList[y + x][2] + '-RST-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-T-REQ_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + '-T-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-B_' + str(y + 1): ruteList[y + x][2] + '-B'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-F-RS_' + str(y + 1): ruteList[y + x][2] + '-F-RS'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-TUR-DO_' + str(y + 1): ruteList[y + x][2] + '-TUR-DO'})

                dfLogic.to_csv(
                    directorySimpan + "\\nFC103 F_RS " + str(x) + "-" + str(x + 4) + ".csv",
                    index=False)

        # Generate nV FC4 T/E ROUTE REQ FBD nFC57 SW ILOCK - D-REQ
        def generatenVFC4DREQ():
            ruteList = [r for r in IT1 if r[4] and r[5]]
            for x in range(0, len(ruteList), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\D-REQ.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(ruteList) % 10 != 0 and x == (math.floor(len(ruteList) / 10) * 10) and y == len(
                            ruteList) % 10:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-D-REQ_' + str(y + 1): ruteList[y + x][2] + '-' + simp(ruteList[y + x][15]) + '-D-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-T-REQ_' + str(y + 1): ruteList[y + x][2] + '-' + simp(ruteList[y + x][15]) + '-T-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace( {'J/JL/Lxx-D-B_' + str(y + 1): ruteList[y + x][2] + '-D-B'})
                    if ruteList[y + x][15].startswith("A") and '' != ruteList[y + x][16]:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-HR-DI_' + str(y + 1): ruteList[y + x][15] + '-HR-DI'})
                    elif ruteList[y + x][15].startswith("A") and '' == ruteList[y + x][16]:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-HR-DI_' + str(y + 1): ruteList[y + x][16] + '-HR-DI'})
                    else:
                        pasanganRute = ""
                        for it in IT1:
                            if "-R" not in it[18] and (ruteList[y + x][15] == it[2] or ruteList[y + x][2] == it[15]):
                                pasanganRute = f"{it[2]}-{simp(it[15])}"
                                break
                        if pasanganRute:
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-HR-DI_' + str(y + 1): pasanganRute + '-T-REQ'})
                dfLogic.to_csv(directorySimpan + "\\D-REQ " + str(x) + "-" + str(x + 10) + ".csv", index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC4 TE ROUTE REQ"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC4 TE ROUTE REQ"

        generatenVFC4nFC84()
        generatenVFC4nFC103()
        generatenVFC4DREQ()

    ############################## nV FC5 SHUNT & INT SHUNT REQ ############################
    def nv_fc5_shunt_int_shunt_req(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # Generate nV FC5 SHUNT & INT SHUNT REQ - nFC86 S ROUTE REQ
        def generatenVFC5nFC86():
            ruteList = [r for r in IT1 if '(S)' in r[1]]
            for x in range(0, len(ruteList), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC86 S ROUTE REQ.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(ruteList) % 10 != 0 and x == (math.floor(len(ruteList) / 10) * 10) and y == len(
                            ruteList) % 10:
                        break

                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-CTRL_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + '-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-RST-CTRL_' + str(y + 1): ruteList[y + x][2] + '-RST-CTRL'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-S-B_' + str(y + 1): ruteList[y + x][2] + '-S-B'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-xx-B_' + str(y + 1): ruteList[y + x][2] + '-' + simp(ruteList[y + x][15]) + '-B'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TP_' + str(y + 1): ruteList[y + x][20].replace('T', '').split(" ")[0] + '-TP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TPBP_' + str(y + 1): ruteList[y + x][20].replace('T', '').split(" ")[0] + '-TPBP'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-xx-RS_' + str(y + 1): ruteList[y + x][2] + '-' + simp(ruteList[y + x][15]) + '-RS'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-S-REQ_' + str(y + 1):
                                                                           ruteList[y + x][2] + '-' + simp(
                                                                               ruteList[y + x][15]) + '-S-REQ'})

                dfLogic.to_csv(
                    directorySimpan + "\\nFC86 S ROUTE REQ " + str(x) + "-" + str(
                        x + 10) + ".csv", index=False)

        # Generate nV FC5 SHUNT & INT SHUNT REQ - nFC85 S 2 ROUTE REQ
        def generatenVFC5nFC85():
            # mencari langsir antara dengan 1 sinyal tujuan sama sinyal asal berbeda (JENIS 2)
            listLangsirAntara = list(set((' '.join([r[21] for r in IT1 if '' != r[21]])).split(" ")))

            listSinyalTujuan = []
            for l in listLangsirAntara:
                for r in IT1:
                    if l in r[21]:
                        listSinyalTujuan.append([l, r[15]])

            satuTujuan = list(set([x[0] for x in listSinyalTujuan if listSinyalTujuan.count(x) > 1]))

            # list langsir antara bukan 1 sinyal tujuan sama atau sinyal asalanya sama (JENIS 1)
            satuAsal = [x for x in listLangsirAntara if x not in satuTujuan]

            # JENIS 1
            for sA in satuAsal:
                ruteList = [r for r in IT1 if sA in r[21]]
                for x in range(0, len(ruteList), 10):
                    dfLogic = pd.read_csv(
                        referensiCSV + "\\nFC85 S 2 ROUTE REQ JENIS 1.csv")
                    for y in range(10):
                        # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                        if len(ruteList) % 10 != 0 and x == (math.floor(len(ruteList) / 10) * 10) and y == len(
                                ruteList) % 10:
                            break
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-RS_' + str(y + 1):
                                                                               ruteList[y + x][2] + '-' + simp(
                                                                                   ruteList[y + x][15]) + '-RS'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-RST-CTRL_' + str(y + 1): ruteList[y + x][2] + '-RST-CTRL'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-E-RST-TE_' + str(y + 1):
                                                                               ruteList[y + x][2] + '-' + simp(
                                                                                   ruteList[y + x][15]) + '-E-RST-TE'})

                        osTrack = ""
                        approachTrack = ""
                        arah = "ES/WS"

                        for z in IT1:
                            if sA == z[2]:
                                osTrack = z[20].replace('T', '').split(" ")[0]
                                approachTrack = z[23].replace('T', '').split(" ")[0]
                                if 'WEST' in z[-1]:
                                    arah = "WS"
                                if 'EAST' in z[-1]:
                                    arah = "ES"

                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'xx-TP_' + str(y + 1): osTrack.split(" ")[0] + '-TP'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'xx-TPBP_' + str(y + 1): osTrack.split(" ")[0] + '-TPBP'})

                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'xx-T-WS_' + str(y + 1): approachTrack.split(" ")[0] + '-T-' + arah})

                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-B_' + str(y + 1): ruteList[y + x][2] + '-B'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-S-B_' + str(y + 1): sA + '-S-B'})

                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-2-RS_' + str(y + 1): sA + '-' + simp(ruteList[y + x][15]) + '-2-RS'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-S-2-REQ_' + str(y + 1): sA + '-' + simp(ruteList[y + x][15]) + '-S-2-REQ'})

                    dfLogic.to_csv(
                        directorySimpan + "\\nFC85 S 2 ROUTE REQ JENIS 1 " + sA + ' ' + str(
                            x) + '-' + str(x + 10) + '.csv', index=False)
            # JENIS 2
            for x in range(0, len(satuTujuan), 5):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC85 S 2 ROUTE REQ JENIS 2.csv")

                for y in range(5):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(satuTujuan) % 5 != 0 and x == (math.floor(len(satuTujuan) / 5) * 5) and y == len(
                            satuTujuan) % 5:
                        break
                    ruteList = [r for r in IT1 if satuTujuan[y + x] in r[21]]
                    # *******************
                    for z, data in enumerate(ruteList):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RS_' + str(y + 1) + '-' + str(z + 1): data[2] + '-' + simp(data[15]) + '-RS'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-RST-CTRL_' + str(y + 1) + '-' + str(z + 1): data[2] + '-RST-CTRL'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-E-RST-TE_' + str(
                            y + 1) + '-' + str(z + 1): data[2] + '-' + simp(data[15]) + '-E-RST-TE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-B_' + str(y + 1) + '-' + str(z + 1): data[2] + '-B'})
                    for z in range(len(ruteList), 10):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-RS_' + str(y + 1) + '-' + str(z + 1): 'FALSE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-RST-CTRL_' + str(y + 1) + '-' + str(z + 1): 'FALSE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-xx-E-RST-TE_' + str(y + 1) + '-' + str(z + 1): 'FALSE'})
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'J/JL/Lxx-B_' + str(y + 1) + '-' + str(z + 1): 'FALSE'})
                    # *******************

                    osTrack = ""
                    approachTrack = ""
                    arah = "ES/WS"

                    for z in IT1:
                        if satuTujuan[y + x] == z[2]:
                            osTrack = z[20].replace('T', '').split(" ")[0]
                            approachTrack = z[23].replace('T', '').split(" ")[0]
                            if 'WEST' in z[-1]:
                                arah = "WS"
                            if 'EAST' in z[-1]:
                                arah = "ES"

                    sinyalTujuan = ""
                    for z in ruteList:
                        sinyalTujuan = z[15]

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TP_' + str(y + 1): osTrack.split(" ")[0] + '-TP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-TPBP_' + str(y + 1): osTrack.split(" ")[0] + '-TPBP'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'xx-T-ES/WS_' + str(y + 1): approachTrack.split(" ")[0] + '-T-' + arah})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-S-B_' + str(y + 1): satuTujuan[y + x] + '-S-B'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-xx-2-RS_' + str(y + 1): satuTujuan[y + x] + '-' + simp(sinyalTujuan) + '-2-RS'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-xx-S-2-REQ_' + str(y + 1): satuTujuan[
                                                                                                                y + x] + '-' + simp(
                        sinyalTujuan) + '-S-2-REQ'})

                dfLogic.to_csv(
                    directorySimpan + "\\nFC85 S 2 ROUTE REQ JENIS 2" + ' ' + str(
                        x) + '-' + str(x + 5) + '.csv', index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC5 SHUNT & INT SHUNT REQ"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC5 SHUNT & INT SHUNT REQ"

        generatenVFC5nFC86()
        generatenVFC5nFC85()

    ############################## nV FC6 ROUTE PARAMETER ############################
    def nv_fc6_route_parameter(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # Generate nV FC6 ROUTE PARAMETER - nFC96 SW FUNCTION
        def generatenVFC6nFC96():
            # list variable semua wesel
            allWesel = list(set((' '.join([w[18].replace("-N", "").replace("-R", "") for w in IT1])).split() +
                                (' '.join([w[7].replace("-N", "").replace("-R", "") for w in IT2])).split()))
            # total output tergenerate (sum generated output)
            sGO = 10
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allWesel), sGO):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC96 SW FUNCTION.csv")

                for y in range(sGO):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allWesel) % sGO != 0 and x == (math.floor(len(allWesel) / sGO) * sGO) and y == len(
                            allWesel) % sGO:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-L_' + str(y + 1): 'W' + allWesel[y + x] + '-L'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-NWZ_' + str(y + 1): 'W' + allWesel[y + x] + '-NWZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-RWZ_' + str(y + 1): 'W' + allWesel[y + x] + '-RWZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-R_' + str(y + 1): 'W' + allWesel[y + x] + '-R'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-N_' + str(y + 1): 'W' + allWesel[y + x] + '-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-OOC_' + str(y + 1): 'W' + allWesel[y + x] + '-OOC'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-SWINIT_' + str(y + 1): 'W' + allWesel[y + x] + '-SWINIT'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-TPZ_' + str(y + 1): 'W' + allWesel[y + x] + '-TPZ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-SWRLS_' + str(y + 1): 'W' + allWesel[y + x] + '-SWRLS'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-P-N_' + str(y + 1): 'W' + allWesel[y + x] + '-P-N'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Wxx-P-R_' + str(y + 1): 'W' + allWesel[y + x] + '-P-R'})

                dfLogic.to_csv(directorySimpan + "\\nFC96 SW FUNCTION " + str(x) + "-" + str(
                    x + sGO) + ".csv", index=False)

        # Generate nV FC6 ROUTE PARAMETER - nFC97 ROUTE PAR
        def generatenVFC6nFC97():
            # list variable semua rute normal
            ruteList = IT2

            # total output tergenerate (sum generated output)
            sGO = 10
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(ruteList), sGO):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC97 ROUTE PAR.csv")

                for y in range(sGO):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(ruteList) % sGO != 0 and x == (math.floor(len(ruteList) / sGO) * sGO) and y == len(
                            ruteList) % sGO:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-xx-P_' + str(y + 1): ruteList[y + x][2] + '-' + simp(ruteList[y + x][6]) + '-P'})

                    # list wesel luncuran
                    listWesel = [w.strip() for w in ruteList[y + x][7].split(" ") if '' != ruteList[y + x][7]]
                    listWesel = list(filter(None, listWesel))

                    for i, wesel in enumerate(listWesel):
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'Wxx-P-N/R_' + str(y + 1) + '-' + str(
                            i + 1): 'W' + wesel.replace('-N', '-P-N').replace('-R', '-P-R')})
                    for i in range(len(listWesel), 10):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'Wxx-P-N/R_' + str(y + 1) + '-' + str(i + 1): 'TRUE'})

                    # list track luncuran
                    tujuan_not_ib = True
                    listTrack = []
                    for rute in IT1:
                        if ruteList[y + x][1] == rute[1]:
                            listTrack = rute[20].replace('T', '').split(" ")
                            if "IB" in rute[16]:
                                tujuan_not_ib = False

                    listTrack += (ruteList[y + x][9].replace('T', '').split(" "))
                    listTrack += (ruteList[y + x][5].replace('T', '').split(" "))
                    if ruteList[y + x][6].startswith("A") and tujuan_not_ib:
                        arah = "W"
                        if 'EAST' in ruteList[y + x][-1]:
                            arah = "E"
                        listTrack.append(f"{ruteList[y + x][6]}-{arah}TP")
                    listTrack = list(filter(None, listTrack))
                    for i, track in enumerate(listTrack):
                        if track.startswith("A"):
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'xx-TP_' + str(y + 1) + '-' + str(i + 1): track})
                        else:
                            dfLogic['New Name'] = dfLogic['New Name'].replace( {'xx-TP_' + str(y + 1) + '-' + str(i + 1): track + '-TP'})
                    for i in range(len(listTrack), 20):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'xx-TP_' + str(y + 1) + '-' + str(i + 1): 'TRUE'})

                    # generate I3 FF TE jika rute belok dan terdapat sinyal arah
                    ruteBelok = False
                    for rute in IT1:
                        if ruteList[y + x][1] == rute[1] and rute[8] != '':
                            ruteBelok = True

                    if ruteBelok:
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'Jxx-I3-FF-TE_' + str(y + 1): ruteList[y + x][2] + "-I3-FF-TE"})
                    else:
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'Jxx-I3-FF-TE_' + str(y + 1): "FALSE"})

                    # list deraileur luncuran
                    listDeraileur = [d.strip() for d in ruteList[y + x][8].split(" ") if '' != ruteList[y + x][8]]
                    listDeraileur = list(filter(None, listDeraileur))

                    for i, deraileur in enumerate(listDeraileur):
                        dfLogic['New Name'] = dfLogic['New Name'].replace({'Dxx-B-N_' + str(y + 1) + '-' + str(
                            i + 1): deraileur.replace('-N', '-B-N').replace('-R', '-B-R')})
                    for i in range(len(listDeraileur), 10):
                        dfLogic['New Name'] = dfLogic['New Name'].replace(
                            {'Dxx-B-N_' + str(y + 1) + '-' + str(i + 1): 'TRUE'})
                dfLogic.to_csv(directorySimpan + "\\nFC97 ROUTE PAR " + str(x) + "-" + str(
                    x + sGO) + ".csv", index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC6 ROUTE PARAMETER"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC6 ROUTE PARAMETER"

        generatenVFC6nFC96()
        generatenVFC6nFC97()

    ######################### nV FC7 IND SIGNAL ################################
    def nv_fc7_ind_signal(self, IT1, IT2, referensiCSV, directorySimpan):
        # Generate nV FC7 IND SIGNAL - nFC58 S IND MASUK
        def generatenVFC7nFC58(IT1, IT2, referensiCSV, directorySimpan):
            allSignal = list(set([s[2] for s in IT1 if '(S)' not in s[1] and 'A' != s[15][0]]))

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allSignal), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC58 S IND MASUK.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allSignal) % 10 != 0 and x == (math.floor(len(allSignal) / 10) * 10) and y == len(
                            allSignal) % 10:
                        break
                    for r in IT1:
                        if allSignal[y + x] == r[2]:
                            if 'V' == r[13] or 'V' == r[14]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'MJ/JL/Lxx-EKR_' + str(y + 1): r[12] + '-EKR'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'MJ/JL/Lxx-ECR_' + str(y + 1): r[12] + '-ECR'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'MJ/JL/Lxx-CGE-F_' + str(y + 1): r[12] + '-CGE-F'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'MJ/JL/Lxx-CGE_' + str(y + 1): r[12] + '-CGE'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'MJ/JL/Lxx-CGE-DO_' + str(y + 1): r[12] + '-CGE-DO'})
                            if 'V' == r[3] or 'V' == r[4] or 'V' == r[5]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-EKR_' + str(y + 1): allSignal[y + x] + '-EKR'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-ECR_' + str(y + 1): allSignal[y + x] + '-ECR'})
                            if 'V' == r[4]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-HR-DO_' + str(y + 1): allSignal[y + x] + '-HR-DO'})
                            if 'V' == r[6]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-ER-DO_' + str(y + 1): allSignal[y + x] + '-ER-DO'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-EGE-DO_' + str(y + 1): allSignal[y + x] + '-EGE-DO'})
                            if 'V' == r[3]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-RGE-F_' + str(y + 1): allSignal[y + x] + '-RGE-F'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-RGE_' + str(y + 1): allSignal[y + x] + '-RGE'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-RGE-DO_' + str(y + 1): allSignal[y + x] + '-RGE-DO'})
                            if 'V' == r[4] or 'V' == r[5]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CGE-F_' + str(y + 1): allSignal[y + x] + '-CGE-F'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CGE_' + str(y + 1): allSignal[y + x] + '-CGE'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CGE-DO_' + str(y + 1): allSignal[y + x] + '-CGE-DO'})
                    for r in IT1:
                        if allSignal[y + x] == r[2]:
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'MJ/JL/Lxx-EKR_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'MJ/JL/Lxx-ECR_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'MJ/JL/Lxx-CGE-F_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'MJ/JL/Lxx-CGE_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'MJ/JL/Lxx-CGE-DO_' + str(y + 1): 'FALSE'})

                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-EKR_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-ECR_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-HR-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-ER-DO_' + str(y + 1): 'FALSE'})

                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-RGE-F_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-RGE_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-RGE-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-CGE-F_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-CGE_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-CGE-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-EGE-DO_' + str(y + 1): 'FALSE'})

                dfLogic.to_csv(directorySimpan + "\\nFC58 S IND MASUK " + str(x) + "-" + str(x + 10) + ".csv",
                               index=False)

        # Generate nV FC7 IND SIGNAL - nFC59 S IND BERANGKAT
        def generatenVFC7nFC59(IT1, IT2, referensiCSV, directorySimpan):
            allSignal = list(
                set([s[2] for s in IT1 if 'L' != s[2][0] and ('A' == s[15][0] or 'X' == s[15][0] or 'L' == s[15][0])]))

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allSignal), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC59 S IND BERANGKAT.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allSignal) % 10 != 0 and x == (math.floor(len(allSignal) / 10) * 10) and y == len(
                            allSignal) % 10:
                        break
                    for r in IT1:
                        if allSignal[y + x] == r[2]:
                            if 'V' == r[3] or 'V' == r[4] or 'V' == r[5]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-EKR_' + str(y + 1): allSignal[y + x] + '-EKR'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-ECR_' + str(y + 1): allSignal[y + x] + '-ECR'})
                            if 'V' == r[4]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-HR-DO_' + str(y + 1): allSignal[y + x] + '-HR-DO'})
                            if 'V' == r[6]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-ER-DO_' + str(y + 1): allSignal[y + x] + '-ER-DO'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-EGE-DO_' + str(y + 1): allSignal[y + x] + '-EGE-DO'})
                            if 'V' == r[3]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-RGE-F_' + str(y + 1): allSignal[y + x] + '-RGE-F'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-RGE_' + str(y + 1): allSignal[y + x] + '-RGE'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-RGE-DO_' + str(y + 1): allSignal[y + x] + '-RGE-DO'})
                            if 'V' == r[4] or 'V' == r[5]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CGE-F_' + str(y + 1): allSignal[y + x] + '-CGE-F'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CGE_' + str(y + 1): allSignal[y + x] + '-CGE'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CGE-DO_' + str(y + 1): allSignal[y + x] + '-CGE-DO'})
                            if 'V' == r[7]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-GR-DO_' + str(y + 1): allSignal[y + x] + '-GR-DO'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-WGE-DO_' + str(y + 1): allSignal[y + x] + '-WGE-DO'})
                            if 'V' == r[9]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CFEK_' + str(y + 1): allSignal[y + x] + '-CFEK'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CFR-DO_' + str(y + 1): allSignal[y + x] + '-CFR-DO'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CFGE-F_' + str(y + 1): allSignal[y + x] + '-CFGE-F'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CFGE_' + str(y + 1): allSignal[y + x] + '-CFGE'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-CFGE-DO_' + str(y + 1): allSignal[y + x] + '-CFGE-DO'})
                    for r in IT1:
                        if allSignal[y + x] == r[2]:
                            if 'V' == r[5]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'J/JL/Lxx-HR-DO_' + str(y + 1): allSignal[y + x] + '-DR-DO'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-EKR_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-ECR_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-CFEK_' + str(y + 1): 'TRUE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-HR-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-ER-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-GR-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-CFR-DO_' + str(y + 1): 'FALSE'})

                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-RGE-F_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-RGE_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-RGE-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-CGE-F_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-CGE_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-CGE-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-WGE-DO_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-CFGE-F_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace({'J/JL/Lxx-CFGE_' + str(y + 1): 'FALSE'})
                            dfLogic['New Name'] = dfLogic['New Name'].replace(
                                {'J/JL/Lxx-CFGE-DO_' + str(y + 1): 'FALSE'})

                dfLogic.to_csv(directorySimpan + "\\nFC59 S IND BERANGKAT " + str(x) + "-" + str(x + 10) + ".csv",
                               index=False)

        # Generate nV FC7 IND SIGNAL - nFC60 S IND SHUNT
        def generatenVFC7nFC60(IT1, IT2, referensiCSV, directorySimpan):
            allSignal = list(set([s[2] for s in IT1 if 'L' in s[2][0]]))

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allSignal), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC60 S IND SHUNT.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allSignal) % 10 != 0 and x == (math.floor(len(allSignal) / 10) * 10) and y == len(
                            allSignal) % 10:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-GR-DO_' + str(y + 1): allSignal[y + x] + '-GR-DO'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-RGE-DO_' + str(y + 1): allSignal[y + x] + '-RGE-DO'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'J/JL/Lxx-WGE-DO_' + str(y + 1): allSignal[y + x] + '-WGE-DO'})

                dfLogic.to_csv(directorySimpan + "\\nFC60 S IND SHUNT " + str(x) + "-" + str(x + 10) + ".csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC7 IND SIGNAL"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC7 IND SIGNAL"

        generatenVFC7nFC58(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC7nFC59(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC7nFC60(IT1, IT2, referensiCSV, directorySimpan)

    ########################## nV FC8 IND POINT ################################
    def nv_fc8_ind_point(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # nFC61 POINT IND_VDU
        def nfc61_point_ind_vdu(IT1, IT2, referensiCSV, directorySimpan, PM):
            wesel = []
            for w in PM:
                if "/" in w[0] and w[0].startswith("W"):
                    wesel.append([w[0].replace("W", "").split("/")[0], w[1]])
                    wesel.append([w[0].replace("W", "").split("/")[1], w[2]])
                elif w[0].startswith("W"):
                    wesel.append([w[0].replace("W", ""), w[1]])

            varEnumerated = sorted(wesel)

            jumlahGenFBD = 5
            FBDtujuan = "nFC61 POINT IND_VDU"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        wesel = data_var[0]
                        track_wesel = data_var[1].replace("T", "")
                        wesel_full = ""
                        for w in PM:
                            if (f"W{wesel}" in w[0] or f"/{wesel}" in w[0]) and \
                                    (track_wesel == w[1].replace("T", "") or track_wesel == w[2].replace("T", "")):
                                wesel_full = w[0].replace("W", "")

                        replace_var(f'xx-TP_{indexFBD}', f'{track_wesel}-TP')
                        replace_var(f'Wxx-L_{indexFBD}', f'W{wesel_full}-L')
                        replace_var(f'Wxx-SWINIT_{indexFBD}', f'W{wesel_full}-SWINIT')
                        replace_var(f'Wxx-BLOCK_{indexFBD}', f'W{wesel_full}-BLOCK')

                        replace_var(f'Wxx-NWP_{indexFBD}', f'W{wesel_full}-NWP')
                        replace_var(f'Wxx-NWZ_{indexFBD}', f'W{wesel_full}-NWZ')
                        replace_var(f'Wxx-NWC_{indexFBD}', f'W{wesel_full}-NWC')

                        replace_var(f'Wxx-RWP_{indexFBD}', f'W{wesel_full}-RWP')
                        replace_var(f'Wxx-RWZ_{indexFBD}', f'W{wesel_full}-RWZ')
                        replace_var(f'Wxx-RWC_{indexFBD}', f'W{wesel_full}-RWC')

                        replace_var(f'Wxx-SWRLS_{indexFBD}', f'W{wesel_full}-SWRLS')
                        replace_var(f'Wxx-LS_{indexFBD}', f'W{wesel_full}-LS')
                        replace_var(f'Wxx-OOC_{indexFBD}', f'W{wesel_full}-OOC')

                        replace_var(f'Wxx-LE-F_{indexFBD}', f'W{wesel}-LE-F')
                        replace_var(f'Wxx-LE_{indexFBD}', f'W{wesel}-LE')
                        replace_var(f'Wxx-LE-DO_{indexFBD}', f'W{wesel}-LE-DO')
                        replace_var(f'Wxx-BE-F_{indexFBD}', f'W{wesel}-BE-F')
                        replace_var(f'Wxx-BE_{indexFBD}', f'W{wesel}-BE')
                        replace_var(f'Wxx-BE-DO_{indexFBD}', f'W{wesel}-BE-DO')

                        replace_var(f'Wxx-NWE-F_{indexFBD}', f'W{wesel}-NWE-F')
                        replace_var(f'Wxx-NWE_{indexFBD}', f'W{wesel}-NWE')
                        replace_var(f'Wxx-NWE-DO_{indexFBD}', f'W{wesel}-NWE-DO')
                        replace_var(f'Wxx-NWTE-F_{indexFBD}', f'W{wesel}-NWTE-F')
                        replace_var(f'Wxx-NWTE_{indexFBD}', f'W{wesel}-NWTE')
                        replace_var(f'Wxx-NWTE-DO_{indexFBD}', f'W{wesel}-NWTE-DO')
                        replace_var(f'Wxx-NTE-DO_{indexFBD}', f'W{wesel}-NTE-DO')
                        replace_var(f'Wxx-NRE-DO_{indexFBD}', f'W{wesel}-NRE-DO')

                        replace_var(f'Wxx-RWE-F_{indexFBD}', f'W{wesel}-RWE-F')
                        replace_var(f'Wxx-RWE_{indexFBD}', f'W{wesel}-RWE')
                        replace_var(f'Wxx-RWE-DO_{indexFBD}', f'W{wesel}-RWE-DO')
                        replace_var(f'Wxx-RWTE-F_{indexFBD}', f'W{wesel}-RWTE-F')
                        replace_var(f'Wxx-RWTE_{indexFBD}', f'W{wesel}-RWTE')
                        replace_var(f'Wxx-RWTE-DO_{indexFBD}', f'W{wesel}-RWTE-DO')
                        replace_var(f'Wxx-RTE-DO_{indexFBD}', f'W{wesel}-RTE-DO')
                        replace_var(f'Wxx-RRE-DO_{indexFBD}', f'W{wesel}-RRE-DO')

                        index_subroute = 1
                        for it_data in IT1:
                            if track_wesel in it_data[20].replace("T", "").split(" ") and "(T)" in it_data[1] and "WEST" in it_data[-1]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{track_wesel}-T-WS')
                                index_subroute += 1
                                break
                        for it_data in IT1:
                            if track_wesel in it_data[20].replace("T", "").split(" ") and ("(E)" in it_data[1] or "(CF)" in it_data[1]) and "WEST" in it_data[-1]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{track_wesel}-E-WS')
                                index_subroute += 1
                                break
                        for it_data in IT1:
                            if track_wesel in it_data[20].replace("T", "").split(" ") and "(S)" in it_data[1] and "WEST" in it_data[-1]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{track_wesel}-S-WS')
                                index_subroute += 1
                                break
                        for it_data in IT1:
                            if track_wesel in it_data[20].replace("T", "").split(" ") and "(T)" in it_data[1] and "EAST" in it_data[-1]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{track_wesel}-T-ES')
                                index_subroute += 1
                                break
                        for it_data in IT1:
                            if track_wesel in it_data[20].replace("T", "").split(" ") and ("(E)" in it_data[1] or "(CF)" in it_data[1]) and "EAST" in it_data[-1]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{track_wesel}-E-ES')
                                index_subroute += 1
                                break
                        for it_data in IT1:
                            if track_wesel in it_data[20].replace("T", "").split(" ") and "(S)" in it_data[1] and "EAST" in it_data[-1]:
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{track_wesel}-S-ES')
                                index_subroute += 1
                                break
                        for it_data in IT2:
                            if track_wesel in it_data[9].replace("T", "").split(" ") and "WEST" in it_data[-1] and (f'{wesel}/' in it_data[7] or f'{wesel}-' in it_data[7]):
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{simp_number(it_data[6])}-T-WLAS')
                                index_subroute += 1
                            if track_wesel in it_data[9].replace("T", "").split(" ") and "EAST" in it_data[-1] and (f'{wesel}/' in it_data[7] or f'{wesel}-' in it_data[7]):
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{simp_number(it_data[6])}-T-ELAS')
                                index_subroute += 1

                        # Generate WP back
                        # 1.cari wesel yang berada dalam 1 track
                        wesel_on_track = [w[0].replace("W", "") for w in PM if (track_wesel == w[1] or track_wesel == w[2]) and wesel not in w[0].replace("W", "").split("/")]
                        # cari posisi wesel tersebut di interlocking table jika berada sama2 dengan indikasi wesel yang di generate
                        all_wesel_pos = []
                        for wt in wesel_on_track:
                            for it in IT1:
                                if wt in it[18] and wesel in it[18]:
                                    for w_tes in it[18].split(" "):
                                        if wt == w_tes.replace("-R","").replace("-N",""):
                                            all_wesel_pos.append(w_tes)
                        all_wesel_pos = sorted(list(set(all_wesel_pos)))
                        # masukan posisi wesel jika saat bersamaan dengan wesel indikasi, wesel tersebut hanya mengarah ke 1 arah saja
                        index_wp_back = 1
                        for w in wesel_on_track:
                            if not (w + "-R" in all_wesel_pos and w + "-N" in all_wesel_pos):
                                if w + "-R" in all_wesel_pos:
                                    replace_var(f'Wxx-N/RWP-BACK_{indexFBD}-{index_wp_back}', f'W{w}-RWP')
                                    index_wp_back += 1
                                if w + "-N" in all_wesel_pos:
                                    replace_var(f'Wxx-N/RWP-BACK_{indexFBD}-{index_wp_back}', f'W{w}-NWP')
                                    index_wp_back += 1

                        for index in range(1, 16):
                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Wxx-N/RWP-BACK_{indexFBD}-{index}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC8 IND POINT - nFC90 DERAILEUR IND
        def generatenVFC8nFC90(IT1, IT2, referensiCSV, directorySimpan, PM):
            allDeraileur = [d[0] for d in PM if 'D' in d[0][0]]
            allEloc = [r[0] for r in PM if 'R' in r[0][0]]

            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allDeraileur), 10):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC90 DERAILEUR IND.csv")
                for y in range(10):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allDeraileur) % 10 != 0 and x == (math.floor(len(allDeraileur) / 10) * 10) and y == len(
                            allDeraileur) % 10:
                        break

                    # belum beres di bagian eloc
                    for it in IT1:
                        for el in allEloc:
                            if allDeraileur[y + x] + '-R' in it[19] and el in it[19]:
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'Rxx-REL-REQ_' + str(y + 1): el + '-REL-REQ'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'Rxx-N/RWP_' + str(y + 1): el + '-' + 'NWP'})
                                dfLogic['New Name'] = dfLogic['New Name'].replace(
                                    {'Rxx-R-OK_' + str(y + 1): el + '-R-OK'})
                                break

                    dfLogic['New Name'] = dfLogic['New Name'].replace({'Rxx-REL-REQ_' + str(y + 1): 'TRUE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'Rxx-N/RWP_' + str(y + 1): 'FALSE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace({'Rxx-R-OK_' + str(y + 1): 'TRUE'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-REL-REQ_' + str(y + 1): allDeraileur[y + x] + '-REL-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-R-OK_' + str(y + 1): allDeraileur[y + x] + '-R-OK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-NP_' + str(y + 1): allDeraileur[y + x] + '-NP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-RP_' + str(y + 1): allDeraileur[y + x] + '-RP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-BE-F_' + str(y + 1): allDeraileur[y + x] + '-BE-F'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-BE_' + str(y + 1): allDeraileur[y + x] + '-BE'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-BE-DO_' + str(y + 1): allDeraileur[y + x] + '-BE-DO'})

                dfLogic.to_csv(directorySimpan + "\\nFC90 DERAILEUR IND " + str(x) + "-" + str(x + 10) + ".csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC8 IND POINT"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC8 IND POINT"

        nfc61_point_ind_vdu(IT1, IT2, referensiCSV, directorySimpan, PM)
        generatenVFC8nFC90(IT1, IT2, referensiCSV, directorySimpan, PM)

    ############################# nV FC9 IND TRACK #############################
    def nv_fc9_ind_track(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # Generate nV FC9 IND TRACK - nFC80 TIND EMPL and nFC81 T IND
        def generatenVFC9nFC8081(IT1, IT2, referensiCSV, directorySimpan, PM):
            # list variable semua wesel kecual APP track dan hapus 'T' jika berakhir 'T'
            allTrack = [[track[:-1] if track.endswith('T') else track for track in trackT[20].split(" ") if
                         'APP' not in track and track] for trackT in IT1]
            allTrack = sum(list(map(list, allTrack)), [])  # falten list
            allTrack = list(set((allTrack)))  # filter unique value
            allTrack = sorted(allTrack)  # sort the list

            # semua track emplacement
            trackEmplA = [
                track[20].split(" ")[-1][:-1] if track[20].split(" ")[-1].endswith('T') else track[20].split(" ")[-1]
                for track in IT1
                if not track[15].startswith("A") and track[27]]
            trackEmplA = sorted(list(set((trackEmplA))))

            ########################### nFC80 TIND EMPL #########################
            # track emplacement, untuk track empl langsir dikecualikan jika dilewati rute non langsir
            trackEmpl = []
            for tE in trackEmplA:
                forINDEmpl = True
                for it in IT1:
                    trackList = [track[:-1] if track.endswith('T') else track.split(" ") for track in
                                 it[20].split(" ")[:-1] if it[27]]
                    if tE in trackList:
                        forINDEmpl = False
                        break
                if forINDEmpl:
                    trackEmpl.append(tE)
            trackEmpl = sorted(list(set((trackEmpl))))
            # INDIKASI EMPLACEMENT -> pecah hasil generate csv menjadi per {jumlahGenFBD} output
            jumlahGenFBD = 10
            for indexCSV in range(0, len(trackEmpl), jumlahGenFBD):

                dfLogic = pd.read_csv(referensiCSV + "\\nFC80 TIND EMPL.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    try:
                        weselSEast = []
                        weselSWest = []
                        replaceVar(f'xx-TP_{indexFBD + 1}', f'{trackEmpl[indexFBD + indexCSV]}-TP')
                        replaceVar(f'xx-TE-DO_{indexFBD + 1}', f'{trackEmpl[indexFBD + indexCSV]}-TE-DO')
                        replaceVar(f'xx-RE-DO_{indexFBD + 1}', f'{trackEmpl[indexFBD + indexCSV]}-RE-DO')
                        # cek subroute : jika track dilewati rute, ambil arah rute dan jenis rutenya
                        for itList in IT1:
                            trackList = [track[:-1] if track.endswith('T') else track for track in
                                         itList[20].split(" ")]
                            weselList = [wL for wL in itList[18].split(" ")]
                            if trackEmpl[indexFBD + indexCSV] == trackList[-1]:
                                if 'EAST' in itList[-1]:
                                    if '(T)' in itList[1]:
                                        replaceVar(f'xx-T-ES_{indexFBD + 1}', f'{trackList[-2]}-T-ES')
                                    if '(E)' in itList[1] or '(CF)' in itList[1]:
                                        replaceVar(f'xx-E-ES_{indexFBD + 1}', f'{trackList[-2]}-E-ES')
                                    if '(S)' in itList[1]:
                                        replaceVar(f'xx-S-ES_{indexFBD + 1}', f'{trackList[-2]}-S-ES')

                                    if not weselSEast:
                                        for wsE in PM:
                                            if trackList[-2] == wsE[1].replace("T", "") or trackList[-2] == wsE[
                                                2].replace(
                                                    "T", ""):
                                                weselSEast.append([wsE[0].replace("W", ""), 0, 0])
                                    for i, w in enumerate(weselSEast):
                                        if f"{w[0]}-N" in weselList:
                                            weselSEast[i][1] = 1
                                        if f"{w[0]}-R" in weselList:
                                            weselSEast[i][2] = 1

                                if 'WEST' in itList[-1]:
                                    if '(T)' in itList[1]:
                                        replaceVar(f'xx-T-WS_{indexFBD + 1}', f'{trackList[-2]}-T-WS')
                                    if '(E)' in itList[1] or '(CF)' in itList[1]:
                                        replaceVar(f'xx-E-WS_{indexFBD + 1}', f'{trackList[-2]}-E-WS')
                                    if '(S)' in itList[1]:
                                        replaceVar(f'xx-S-WS_{indexFBD + 1}', f'{trackList[-2]}-S-WS')

                                    if not weselSWest:
                                        for wsW in PM:
                                            if trackList[-2] == wsW[1].replace("T", "") or trackList[-2] == wsW[
                                                2].replace(
                                                    "T", ""):
                                                weselSWest.append([wsW[0].replace("W", ""), 0, 0])
                                    for i, w in enumerate(weselSWest):
                                        if f"{w[0]}-N" in weselList:
                                            weselSWest[i][1] = 1
                                        if f"{w[0]}-R" in weselList:
                                            weselSWest[i][2] = 1
                        weselSEast = [w for w in weselSEast if not (w[1] and w[2])]
                        weselSWest = [w for w in weselSWest if not (w[1] and w[2])]
                        for indexWZ, wesel in enumerate(weselSEast):
                            if wesel[1]:
                                replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-RWZ')
                            elif wesel[2]:
                                replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-NWZ')

                        for indexWZ, wesel in enumerate(weselSWest):
                            if wesel[1]:
                                replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-RWZ')
                            elif wesel[2]:
                                replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-NWZ')

                        # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                        replaceVar(f'xx-T-ES_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-E-ES_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-S-ES_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-T-WS_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-E-WS_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-S-WS_{indexFBD + 1}', 'TRUE')
                        for i in range(1, 11):
                            replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD + 1}-{i}', 'FALSE')
                            replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD + 1}-{i}', 'FALSE')

                    except Exception as e:
                        print(f"nFC80 TIND EMPL -> {e}" if str(e) != "list index out of range" else f'nFC80 TIND EMPL -> Done..')
                        break

                dfLogic.to_csv(directorySimpan + f"\\nFC80 TIND EMPL {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

            ########################## nFC81 T IND ###############################
            # selain track emplacement
            trackNotEmpl = [track for track in allTrack if track not in trackEmpl]
            trackEmplS = [track for track in trackEmplA if track not in trackEmpl]
            # INDIKASI TRACK -> pecah hasil generate csv menjadi per {jumlahGenFBD} output
            jumlahGenFBD = 10
            for indexCSV in range(0, len(trackNotEmpl), jumlahGenFBD):

                dfLogic = pd.read_csv(referensiCSV + "\\nFC81 T IND.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    try:
                        weselSEast = []
                        weselSWest = []

                        replaceVar(f'xx-TP_{indexFBD + 1}', f'{trackNotEmpl[indexFBD + indexCSV]}-TP')
                        replaceVar(f'xx-TE-DO_{indexFBD + 1}', f'{trackNotEmpl[indexFBD + indexCSV]}-TE-DO')
                        replaceVar(f'xx-RE-DO_{indexFBD + 1}', f'{trackNotEmpl[indexFBD + indexCSV]}-RE-DO')
                        # cek subroute : jika track dilewati rute, ambil arah rute dan jenis rutenya
                        for itList in IT1:
                            trackList = [track[:-1] if track.endswith('T') else track for track in
                                         itList[20].split(" ")]
                            weselList = [wL for wL in itList[18].split(" ")]
                            # print(trackList)
                            if trackNotEmpl[indexFBD + indexCSV] in trackList:
                                if 'EAST' in itList[-1]:
                                    if '(T)' in itList[1]:
                                        replaceVar(f'xx-T-ES_{indexFBD + 1}',
                                                   f'{trackNotEmpl[indexFBD + indexCSV]}-T-ES')
                                    if '(E)' in itList[1] or '(CF)' in itList[1]:
                                        replaceVar(f'xx-E-ES_{indexFBD + 1}',
                                                   f'{trackNotEmpl[indexFBD + indexCSV]}-E-ES')
                                    if '(S)' in itList[1] and trackNotEmpl[indexFBD + indexCSV] not in trackEmplS:
                                        replaceVar(f'xx-S-ES_{indexFBD + 1}',
                                                   f'{trackNotEmpl[indexFBD + indexCSV]}-S-ES')
                                    if '(S)' in itList[1] and trackNotEmpl[indexFBD + indexCSV] in trackEmplS and \
                                            trackNotEmpl[indexFBD + indexCSV] == trackList[-1]:
                                        replaceVar(f'xx-S-ES_{indexFBD + 1}', f'{trackList[-2]}-S-ES')
                                        if not weselSEast:
                                            for wsE in PM:
                                                if trackList[-2] == wsE[1].replace("T", "") or trackList[-2] == wsE[
                                                    2].replace("T", ""):
                                                    weselSEast.append([wsE[0].replace("W", ""), 0, 0])
                                        for i, w in enumerate(weselSEast):
                                            if f"{w[0]}-N" in weselList:
                                                weselSEast[i][1] = 1
                                            if f"{w[0]}-R" in weselList:
                                                weselSEast[i][2] = 1

                                if 'WEST' in itList[-1]:
                                    if '(T)' in itList[1]:
                                        replaceVar(f'xx-T-WS_{indexFBD + 1}',
                                                   f'{trackNotEmpl[indexFBD + indexCSV]}-T-WS')
                                    if '(E)' in itList[1] or '(CF)' in itList[1]:
                                        replaceVar(f'xx-E-WS_{indexFBD + 1}',
                                                   f'{trackNotEmpl[indexFBD + indexCSV]}-E-WS')
                                    if '(S)' in itList[1] and trackNotEmpl[indexFBD + indexCSV] not in trackEmplS:
                                        replaceVar(f'xx-S-WS_{indexFBD + 1}',
                                                   f'{trackNotEmpl[indexFBD + indexCSV]}-S-WS')
                                    if '(S)' in itList[1] and trackNotEmpl[indexFBD + indexCSV] in trackEmplS and \
                                            trackNotEmpl[indexFBD + indexCSV] == trackList[-1]:
                                        replaceVar(f'xx-S-WS_{indexFBD + 1}', f'{trackList[-2]}-S-WS')
                                        if not weselSWest:
                                            for wsW in PM:
                                                if trackList[-2] == wsW[1].replace("T", "") or trackList[-2] == wsW[
                                                    2].replace("T", ""):
                                                    weselSWest.append([wsW[0].replace("W", ""), 0, 0])
                                        for i, w in enumerate(weselSWest):
                                            if f"{w[0]}-N" in weselList:
                                                weselSWest[i][1] = 1
                                            if f"{w[0]}-R" in weselList:
                                                weselSWest[i][2] = 1

                        weselSEast = [w for w in weselSEast if not (w[1] and w[2])]
                        weselSWest = [w for w in weselSWest if not (w[1] and w[2])]
                        for indexWZ, wesel in enumerate(weselSEast):
                            if wesel[1]:
                                replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-RWZ')
                            elif wesel[2]:
                                replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-NWZ')

                        for indexWZ, wesel in enumerate(weselSWest):
                            if wesel[1]:
                                replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-RWZ')
                            elif wesel[2]:
                                replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD + 1}-{indexWZ + 1}', f'W{wesel[0]}-NWZ')

                        indexE = 0
                        indexW = 0
                        for itList in IT2:
                            trackList = [track[:-1] if track.endswith('T') else track for track in itList[9].split(" ")]
                            if trackNotEmpl[indexFBD + indexCSV] in trackList:
                                if 'EAST' in itList[-1]:
                                    replaceVar(f'xx-T-ELAS_{indexFBD + 1}-{indexE + 1}', simp_number(itList[6]) + '-T-ELAS')
                                    indexE += 1
                                if 'WEST' in itList[-1]:
                                    replaceVar(f'xx-T-WLAS_{indexFBD + 1}-{indexW + 1}', simp_number(itList[6]) + '-T-WLAS')
                                    indexW += 1

                        # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                        replaceVar(f'xx-T-ES_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-E-ES_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-S-ES_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-T-WS_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-E-WS_{indexFBD + 1}', 'TRUE')
                        replaceVar(f'xx-S-WS_{indexFBD + 1}', 'TRUE')
                        for i in range(1, 11):
                            replaceVar(f'xx-T-ELAS_{indexFBD + 1}-{i}', 'TRUE')
                            replaceVar(f'xx-T-WLAS_{indexFBD + 1}-{i}', 'TRUE')
                            replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD + 1}-{i}', 'FALSE')
                            replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD + 1}-{i}', 'FALSE')

                    except Exception as e:
                        print(f"nFC81 T IND -> {e}" if str(e) != "list index out of range" else f'nFC81 T IND -> Done..')
                        break

                dfLogic.to_csv(directorySimpan + f"\\nFC81 T IND {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

            ########################## nFC81 T IND BLOK ###############################
            # selain track emplacement
            track_blok = sorted(list(set([it[15] for it in IT1 if it[15].startswith("A")])))
            # INDIKASI TRACK -> pecah hasil generate csv menjadi per {jumlahGenFBD} output
            jumlahGenFBD = 10
            for indexCSV in range(0, len(track_blok), jumlahGenFBD):

                dfLogic = pd.read_csv(referensiCSV + "\\nFC81 T IND.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    try:
                        data_var = track_blok[indexFBD + indexCSV]
                        indexFBD += 1
                        arah = "W"
                        for it in IT1:
                            if it[15] == data_var and "EAST" in it[-1]:
                                arah = "E"
                                break

                        track_ujung = ""
                        for it in IT1:
                            if it[15] == data_var:
                                if it[20].split(" ")[-1].endswith("T"):
                                    track_ujung = it[20].split(" ")[-1][:-1]
                                else:
                                    track_ujung = it[20].split(" ")[-1]
                                break

                        replaceVar(f'xx-TP_{indexFBD}', f'{data_var}-{arah}TP')
                        replaceVar(f'xx-TE-DO_{indexFBD}', f'{data_var}-{arah}TE-DO')
                        replaceVar(f'xx-RE-DO_{indexFBD}', f'{data_var}-{arah}RE-DO')
                        # cek subroute : jika track dilewati rute, ambil arah rute dan jenis rutenya
                        for itList in IT1:
                            trackList = [track[:-1] if track.endswith('T') else track for track in itList[20].split(" ")]
                            if track_ujung in trackList:
                                if 'EAST' in itList[-1]:
                                    if '(T)' in itList[1]:
                                        replaceVar(f'xx-T-ES_{indexFBD}', f'{track_ujung}-T-ES')
                                    if '(E)' in itList[1] or '(CF)' in itList[1]:
                                        replaceVar(f'xx-E-ES_{indexFBD}', f'{track_ujung}-E-ES')
                                    if '(S)' in itList[1]:
                                        replaceVar(f'xx-S-ES_{indexFBD}', f'{track_ujung}-S-ES')

                                if 'WEST' in itList[-1]:
                                    if '(T)' in itList[1]:
                                        replaceVar(f'xx-T-WS_{indexFBD}', f'{track_ujung}-T-WS')
                                    if '(E)' in itList[1] or '(CF)' in itList[1]:
                                        replaceVar(f'xx-E-WS_{indexFBD}', f'{track_ujung}-E-WS')
                                    if '(S)' in itList[1]:
                                        replaceVar(f'xx-S-WS_{indexFBD}', f'{track_ujung}-S-WS')

                        # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                        replaceVar(f'xx-T-ES_{indexFBD}', 'TRUE')
                        replaceVar(f'xx-E-ES_{indexFBD}', 'TRUE')
                        replaceVar(f'xx-S-ES_{indexFBD}', 'TRUE')
                        replaceVar(f'xx-T-WS_{indexFBD}', 'TRUE')
                        replaceVar(f'xx-E-WS_{indexFBD}', 'TRUE')
                        replaceVar(f'xx-S-WS_{indexFBD}', 'TRUE')
                        for i in range(1, 11):
                            replaceVar(f'xx-T-ELAS_{indexFBD}-{i}', 'TRUE')
                            replaceVar(f'xx-T-WLAS_{indexFBD}-{i}', 'TRUE')
                            replaceVar(f'Wxx-NWZ/RWZ-ES_{indexFBD}-{i}', 'FALSE')
                            replaceVar(f'Wxx-NWZ/RWZ-WS_{indexFBD}-{i}', 'FALSE')

                    except Exception as e:
                        print(f"nFC81 T IND (BLOK) -> {e}" if str(e) != "list index out of range" else f'nFC81 T IND (BLOK) -> Done..')
                        break

                dfLogic.to_csv(directorySimpan + f"\\nFC81 T IND (BLOK) {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC9 IND TRACK"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC9 IND TRACK"

        generatenVFC9nFC8081(IT1, IT2, referensiCSV, directorySimpan, PM)

    ######################### nV FC10 IND BLOCK & IND ALARM ####################
    def nv_fc10_ind_block_and_ind_alarm(self, IT1, IT2, referensiCSV, directorySimpan):
        # nFC62 BLOCK IND W
        def generatenVFC10nFC62(IT1, IT2, referensiCSV, directorySimpan):
            allSignalTujuan = sorted(list(set([signal[15] for signal in IT1 if signal[15].startswith("A")])))
            signalCF = sorted(list(set([signal[15] for signal in IT1 if signal[15].startswith("A") and "(CF)" in signal[1]])))
            signalE = sorted(list(set([signal[2] for signal in IT1 if signal[6]])))
            signalT = sorted(list(set([signal[2] for signal in IT1 if signal[4] or signal[5]])))

            varEnumerated = allSignalTujuan
            jumlahGenFBD = 5
            FBDtujuan = "nFC62 BLOCK IND W"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        arahOut = ""
                        arahIn = ""
                        if signal.endswith("0"):
                            arahOut = "W"
                            arahIn = "E"
                        else :
                            arahOut = "E"
                            arahIn = "W"

                        cfOut = ""
                        cfIn = ""
                        if signal in signalCF:
                            cfOut = "-CF"
                        else:
                            cfIn = "-CF"

                        ################################# input ##############################
                        replaceVar(f'Axx-W/ETP_{indexFBD}', f'{signal}-{arahOut}TP')

                        trackBerangkat = []
                        for tb in IT1:
                             if signal in tb[15]:
                                trackBerangkat = tb[20].replace("T", "").split(" ")
                                break

                        trackMasuk = []
                        approachTM = ""
                        for tm in IT1:
                             if signal.replace("A", "J") in tm[2]:
                                trackMasuk = tm[20].replace("T", "").split(" ")
                                approachTM = tm[23]
                                break

                        trackBlok = []
                        start = False
                        for trackB in trackBerangkat:
                            if trackB == approachTM:
                                start = True
                            if start:
                                trackBlok.append(trackB)

                        if signal in signalCF:
                            trackBlok.append(trackMasuk[0])

                        for index, track in enumerate(trackBlok):
                            replaceVar(f'xx-TP_{indexFBD}-{index + 1}', f'{track}-TP')

                        for track in IT1:
                            if signal.replace("A", "J") in track[2]:
                                replaceVar(f'Axx-TP_{indexFBD}', f'{track[23].replace("T","")}-TP')
                                break
                        for track in IT1:
                            if signal in track[15]:
                                replaceVar(f'xx-TP_{indexFBD}', f'{tm[20].replace("T", "").split(" ")[0]}-TP')
                                break

                        if signal.replace("A", "J") in signalE:
                            replaceVar(f'Jxx-ER-DO_{indexFBD}', f'{signal.replace("A", "J")}-ER-DO')
                        if signal.replace("A", "J") in signalT:
                            replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{signal.replace("A", "J")}-HR-DO')

                        replaceVar(f'Axx-E/WS_{indexFBD}', f'{signal}-{arahIn}S')
                        replaceVar(f'Axx-TBMS_{indexFBD}', f'{signal}{cfOut}-TBMS')
                        replaceVar(f'Axx-W/EFL-CFR_{indexFBD}', f'{signal}-{arahOut}FL-CFR')
                        replaceVar(f'Axx-W/EFLR-DO_{indexFBD}', f'{signal}-{arahOut}FLR-DO')

                        ################################# output ##################################
                        replaceVar(f'Axx-AA_{indexFBD}', f'{signal}-AA')
                        replaceVar(f'Axx-ATE-F_{indexFBD}', f'{signal}-ATE-F')
                        replaceVar(f'Axx-ATE_{indexFBD}', f'{signal}-ATE')
                        replaceVar(f'Axx-ATE-DO_{indexFBD}', f'{signal}-ATE-DO')

                        replaceVar(f'Axx-W/EFE-F_{indexFBD}', f'{signal}{cfOut}-{arahOut}FE-F')
                        replaceVar(f'Axx-W/EFE_{indexFBD}', f'{signal}{cfOut}-{arahOut}FE')
                        replaceVar(f'Axx-W/EFE-DO_{indexFBD}', f'{signal}{cfOut}-{arahOut}FE-DO')

                        replaceVar(f'Axx-W/EFLE-F_{indexFBD}', f'{signal}{cfOut}-{arahOut}FLE-F')
                        replaceVar(f'Axx-W/EFLE_{indexFBD}', f'{signal}{cfOut}-{arahOut}FLE')
                        replaceVar(f'Axx-W/EFLE-DO_{indexFBD}', f'{signal}{cfOut}-{arahOut}FLE-DO')

                        replaceVar(f'Axx-E/WFE-DO_{indexFBD}', f'{signal}{cfIn}-{arahIn}FE-DO')
                        replaceVar(f'Axx-E/WFLE-DO_{indexFBD}', f'{signal}{cfIn}-{arahIn}FLE-DO')

                        for index in range(1, 6):
                            replaceVar(f'xx-TP_{indexFBD}-{index}', f'TRUE')
                        replaceVar(f'Jxx-ER-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'Jxx-HR-DO_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexFBD}.csv", index=False)

        # nV FC10 IND BLOCK & IND ALARM - nFC83 SYS PB FAIL
        def generatenVFC10nFC94(IT1, IT2, referensiCSV, directorySimpan):
            allSignalTujuan = sorted(list(set([signal[15] for signal in IT1 if signal[15].startswith("A")])))
            signalCF = sorted(list(set([signal[15] for signal in IT1 if signal[15].startswith("A") and "(CF)" in signal[1]])))
            signalE = sorted(list(set([signal[2] for signal in IT1 if signal[6]])))
            signalT = sorted(list(set([signal[2] for signal in IT1 if signal[4] or signal[5]])))

            varEnumerated = allSignalTujuan
            jumlahGenFBD = 5
            FBDtujuan = "nFC94 TBMS"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        arahOut = ""
                        arahIn = ""
                        if signal.endswith("0"):
                            arahOut = "W"
                            arahIn = "E"
                        else:
                            arahOut = "E"
                            arahIn = "W"

                        cfOut = ""
                        cfIn = ""
                        if signal in signalCF:
                            cfOut = "-CF"
                        else:
                            cfIn = "-CF"

                        ################################# input ##############################
                        replaceVar(f'Axx-TBMS_{indexFBD}', f'{signal}{cfOut}-TBMS')
                        replaceVar(f'Axx-TBMS-CTRL_{indexFBD}', f'{signal}{cfOut}-TBMS-CTRL')
                        replaceVar(f'Axx-E/WS_{indexFBD}', f'{signal}-{arahIn}S')
                        if signal.replace("A", "J") in signalE:
                            replaceVar(f'Jxx-E-AS_{indexFBD}', f'{signal.replace("A", "J")}-E-AS')
                        if signal.replace("A", "J") in signalT:
                            replaceVar(f'Jxx-T-AS_{indexFBD}', f'{signal.replace("A", "J")}-T-AS')

                        listSignalAsal = sorted(list(set([signalAs[2] for signalAs in IT1 if signalAs[15] == signal])))
                        for ind, sA in enumerate(listSignalAsal):
                            if sA in signalT:
                                replaceVar(f'J/JL/Lxx-T-AS_{indexFBD}-{ind+1}', f'{sA}-T-AS')
                            if sA in signalE:
                                replaceVar(f'J/JL/Lxx-E-AS_{indexFBD}-{ind+1}', f'{sA}-E-AS')

                        replaceVar(f'Jxx-T-AS_{indexFBD}', f'TRUE')
                        for ind in range(1,16):
                            replaceVar(f'J/JL/Lxx-T-AS_{indexFBD}-{ind + 1}', f'TRUE')
                            replaceVar(f'J/JL/Lxx-E-AS_{indexFBD}-{ind + 1}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexFBD}.csv", index=False)

        # nV FC10 IND BLOCK & IND ALARM - nFC71 BLK APP ALARM
        def generatenVFC10nFC71(IT1, IT2, referensiCSV, directorySimpan):
            signal = sorted(list(set([signal[15] for signal in IT1 if signal[15].startswith("A")])))\

            FBDtujuan = "nFC71 BLK APP ALARM"
            dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

            def replaceVar(varAwal, varBaru):
                dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

            try:
                for x in range(1, 9):
                    replaceVar(f'Axx-AA_{x}', f'{signal[x - 1]}-AA')
                    replaceVar(f'Axx-BZ-TE_{x}', f'{signal[x - 1]}-BZ-TE')
            except:
                pass

            for x in range(1, 9):
                replaceVar(f'Axx-AA_{x}', f'FALSE')
                replaceVar(f'Axx-BZ-TE_{x}', f'FALSE')

            dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} .csv", index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC10 IND BLOCK & IND ALARM"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC10 IND BLOCK & IND ALARM"

        generatenVFC10nFC62(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC10nFC94(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC10nFC71(IT1, IT2, referensiCSV, directorySimpan)

    ######################### nV FC11 IND PB & IND FAIL ########################
    def nv_fc11_ind_pb_and_ind_fail(self, IT1, IT2, referensiCSV, directorySimpan):
        # Generate nV FC11 IND PB & IND FAIL - nFC64 PB IND(J)
        def generatenVFC11nFC64(IT1, IT2, referensiCSV, directorySimpan):
            signalY = sorted(list(set([signal[2] for signal in IT1 if signal[4]])))
            signalG = sorted(list(set([signal[2] for signal in IT1 if signal[5]])))
            signalE = sorted(list(set([signal[2] for signal in IT1 if signal[6]])))
            signalS = sorted(list(set([signal[2] for signal in IT1 if signal[7]])))

            pbDestin = sorted(list(set([pb[15] for pb in IT1])))
            allPushButton = sorted(list(set([pb[2] for pb in IT1 if pb[2] not in pbDestin and not pb[2].startswith("L") and not pb[2].startswith("JL")])))

            varEnumerated = allPushButton
            jumlahGenFBD = 5
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC64 PB IND(J).csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        pushButton = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replaceVar(f'Jxx-RST-CTRL_{indexFBD}', f'{pushButton}-RST-CTRL')

                        if pushButton in signalY and pushButton in signalG:
                            replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{pushButton}-HR-DO')
                            replaceVar(f'Jxx-HR-RD_{indexFBD}', f'{pushButton}-HR-RD')
                            replaceVar(f'Jxx-T-AS_{indexFBD}', f'{pushButton}-T-AS')
                        elif pushButton not in signalY and pushButton in signalG:
                            replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{pushButton}-DR-DO')
                            replaceVar(f'Jxx-T-AS_{indexFBD}', f'{pushButton}-T-AS')

                        if pushButton in signalE:
                            replaceVar(f'Jxx-ER-DO_{indexFBD}', f'{pushButton}-ER-DO')
                            replaceVar(f'Jxx-ER-RD_{indexFBD}', f'{pushButton}-ER-RD')
                            replaceVar(f'Jxx-E-AS_{indexFBD}', f'{pushButton}-E-AS')

                        index = 1
                        for it in IT1:
                            if pushButton in it[2] and ("(E)" in it[1] or "(CF)" in it[1]):
                                CF = ""
                                if "(CF)" in it[1]:
                                    CF = "-CF"
                                replaceVar(f'Jxx-xx-E-RST-TE_{indexFBD}-{index}',
                                           f'{it[2]}-{simp(it[15])}{CF}-E-RST-TE')
                                index += 1

                        index = 1
                        rutePushButton = sorted(list(
                            set([rutePb[2] + "-" + simp(rutePb[15]) + ("-CF" if "(CF)" in rutePb[1] else "") for rutePb
                                 in IT1 if pushButton in rutePb[2]])))
                        for rtpb in rutePushButton:
                            replaceVar(f'Jxx-xx-RS_{indexFBD}-{index}', f'{rtpb}-RS')
                            index += 1

                        index = 1
                        rutePushButton = sorted(list(
                            set([rutePb[2] + "-" + simp(rutePb[15]) + ("-CF" if "(CF)" in rutePb[1] else "") for rutePb
                                 in IT1 if pushButton in rutePb[15] and not rutePb[2].startswith("L")])))
                        for rtpb in rutePushButton:
                            replaceVar(f'Jxx-xx-RS_{indexFBD}-{index}', f'{rtpb}-RS')
                            if rtpb[:rtpb.find("-")] in signalE:
                                replaceVar(f'Jxx-ER-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-ER-DO')
                            if rtpb[:rtpb.find("-")] in signalY:
                                replaceVar(f'Jxx-HR-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-HR-DO')
                            elif rtpb[:rtpb.find("-")] in signalG:
                                replaceVar(f'Jxx-HR-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-DR-DO')
                            index += 1

                        replaceVar(f'Jxx-RRLS_{indexFBD}', f'{pushButton}-RRLS')

                        replaceVar(f'Jxx-PBE-F_{indexFBD}', f'{pushButton}-PBE-F')
                        replaceVar(f'Jxx-PBE_{indexFBD}', f'{pushButton}-PBE')
                        replaceVar(f'Jxx-PBE-DO_{indexFBD}', f'{pushButton}-PBE-DO')

                        replaceVar(f'Jxx-HR-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'Jxx-HR-RD_{indexFBD}', f'FALSE')
                        replaceVar(f'Jxx-ER-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'Jxx-ER-RD_{indexFBD}', f'FALSE')
                        replaceVar(f'Jxx-T-AS_{indexFBD}', f'TRUE')
                        replaceVar(f'Jxx-E-AS_{indexFBD}', f'TRUE')

                        for index in range(1, 16):
                            replaceVar(f'Jxx-xx-E-RST-TE_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'Jxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'Jxx-ER-DO_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'Jxx-HR/DR-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'Jxx-HR/DR-DO_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"nFC64 PB IND(J) -> {e}" if str(e) != "list index out of range" else f'nFC64 PB IND(J) -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\nFC64 PB IND(J) {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC11 IND PB & IND FAIL - nFC65 PB IND(JL)
        def generatenVFC11nFC65(IT1, IT2, referensiCSV, directorySimpan):
            pbDestin = sorted(list(set([pb[15] for pb in IT1])))
            allPushButton = sorted(list(set([pb[2] for pb in IT1 if (pb[2] in pbDestin or pb[2].startswith("JL"))])))

            signalY = sorted(list(set([signal[2] for signal in IT1 if signal[4]])))
            signalG = sorted(list(set([signal[2] for signal in IT1 if signal[5]])))
            signalE = sorted(list(set([signal[2] for signal in IT1 if signal[6]])))
            signalS = sorted(list(set([signal[2] for signal in IT1 if signal[7]])))

            varEnumerated = allPushButton
            jumlahGenFBD = 5
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC65 PB IND(JL).csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        pushButton = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'{pushButton}-RST-CTRL')

                        if pushButton in signalY and pushButton in signalG:
                            replaceVar(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{pushButton}-DR-DO')
                            replaceVar(f'J/JL/Lxx-DR-RD_{indexFBD}', f'{pushButton}-DR-RD')
                            replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{pushButton}-HR-DO')
                            replaceVar(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'{pushButton}-HR-RD')
                            replaceVar(f'J/JL/Lxx-T-AS_{indexFBD}', f'{pushButton}-T-AS')
                        elif pushButton not in signalY and pushButton in signalG:
                            replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{pushButton}-DR-DO')
                            replaceVar(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'{pushButton}-DR-RD')
                            replaceVar(f'J/JL/Lxx-T-AS_{indexFBD}', f'{pushButton}-T-AS')

                        if pushButton in signalE:
                            replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{pushButton}-ER-DO')
                            replaceVar(f'J/JL/Lxx-ER-RD_{indexFBD}', f'{pushButton}-ER-RD')
                            replaceVar(f'J/JL/Lxx-E-AS_{indexFBD}', f'{pushButton}-E-AS')
                        if pushButton in signalS:
                            replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{pushButton}-GR-DO')
                            replaceVar(f'J/JL/Lxx-GR-RD_{indexFBD}', f'{pushButton}-GR-RD')
                            replaceVar(f'J/JL/Lxx-S-AS_{indexFBD}', f'{pushButton}-S-AS')

                        index = 1
                        for it in IT1:
                            if pushButton in it[2] and ("(E)" in it[1] or "(CF)" in it[1]):
                                CF = ""
                                if "(CF)" in it[1]:
                                    CF = "-CF"
                                replaceVar(f'J/JL/Lxx-xx-E-RST-TE_{indexFBD}-{index}',
                                           f'{it[2]}-{simp(it[15])}{CF}-E-RST-TE')
                                index += 1

                        index = 1
                        rutePushButton = sorted(list(
                            set([rutePb[2] + "-" + simp(rutePb[15]) + ("-CF" if "(CF)" in rutePb[1] else "") for rutePb
                                 in IT1 if pushButton in rutePb[2]])))
                        for rtpb in rutePushButton:
                            replaceVar(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'{rtpb}-RS')
                            index += 1

                        index = 1
                        for it in IT1:
                            if pushButton in it[15] and "(S)" in it[1] and it[2].startswith("L"):
                                replaceVar(f'Lxx-xx-RS_{indexFBD}-{index}', f'{it[2]}-{simp(it[15])}-RS')
                                replaceVar(f'Lxx-GR-DO_{indexFBD}-{index}', f'{it[2]}-GR-DO')
                                index += 1

                        index = 1
                        rutePushButton = sorted(list(
                            set([rutePb[2] + "-" + simp(rutePb[15]) + ("-CF" if "(CF)" in rutePb[1] else "") for rutePb
                                 in IT1 if pushButton in rutePb[15] and not rutePb[2].startswith("L")])))
                        for rtpb in rutePushButton:
                            replaceVar(f'J/JLxx-xx-RS_{indexFBD}-{index}', f'{rtpb}-RS')
                            if rtpb[:rtpb.find("-")] in signalE:
                                replaceVar(f'J/JLxx-ER-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-ER-DO')
                            if rtpb[:rtpb.find("-")] in signalY:
                                replaceVar(f'J/JLxx-HR/DR-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-HR-DO')
                            elif rtpb[:rtpb.find("-")] in signalG:
                                replaceVar(f'J/JLxx-HR/DR-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-DR-DO')
                            index += 1

                        replaceVar(f'J/JL/Lxx-RRLS_{indexFBD}', f'{pushButton}-RRLS')

                        replaceVar(f'J/JL/Lxx-PBE-F_{indexFBD}', f'{pushButton}-PBE-F')
                        replaceVar(f'J/JL/Lxx-PBE_{indexFBD}', f'{pushButton}-PBE')
                        replaceVar(f'J/JL/Lxx-PBE-DO_{indexFBD}', f'{pushButton}-PBE-DO')

                        replaceVar(f'J/JL/Lxx-DR-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-DR-RD_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-HR/DR-RD_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-ER-RD_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-GR-RD_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-T-AS_{indexFBD}', f'TRUE')
                        replaceVar(f'J/JL/Lxx-E-AS_{indexFBD}', f'TRUE')
                        replaceVar(f'J/JL/Lxx-S-AS_{indexFBD}', f'TRUE')

                        for index in range(1, 16):
                            replaceVar(f'J/JL/Lxx-xx-E-RST-TE_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JLxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'Lxx-GR-DO_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JLxx-ER-DO_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JLxx-HR/DR-DO_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"nFC65 PB IND(JL) -> {e}" if str(e) != "list index out of range" else f'nFC65 PB IND(JL) -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\nFC65 PB IND(JL) {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC11 IND PB & IND FAIL - nFC66 PB IND(L)
        def generatenVFC11nFC66(IT1, IT2, referensiCSV, directorySimpan):
            signalY = sorted(list(set([signal[2] for signal in IT1 if signal[4]])))
            signalG = sorted(list(set([signal[2] for signal in IT1 if signal[5]])))
            signalE = sorted(list(set([signal[2] for signal in IT1 if signal[6]])))
            signalS = sorted(list(set([signal[2] for signal in IT1 if signal[7]])))

            pbDestin = sorted(list(set([pb[15] for pb in IT1])))
            allPushButton = sorted(list(set([pb[2] for pb in IT1 if pb[2] not in pbDestin and pb[2].startswith("L")])))

            varEnumerated = allPushButton
            jumlahGenFBD = 5
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC66 PB IND(L).csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        pushButton = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replaceVar(f'Lxx-RST-CTRL_{indexFBD}', f'{pushButton}-RST-CTRL')

                        replaceVar(f'Lxx-GR-DO_{indexFBD}', f'{pushButton}-GR-DO')
                        replaceVar(f'Lxx-GR-RD_{indexFBD}', f'{pushButton}-GR-RD')
                        replaceVar(f'Lxx-S-AS_{indexFBD}', f'{pushButton}-S-AS')

                        index = 1
                        rutePushButton = sorted(list(
                            set([rutePb[2] + "-" + simp(rutePb[15]) for rutePb in IT1 if pushButton in rutePb[2]])))
                        for rtpb in rutePushButton:
                            replaceVar(f'Lxx-xx-RS_{indexFBD}-{index}', f'{rtpb}-RS')
                            index += 1

                        replaceVar(f'Lxx-RRLS_{indexFBD}', f'{pushButton}-RRLS')

                        replaceVar(f'Lxx-PBE-F_{indexFBD}', f'{pushButton}-PBE-F')
                        replaceVar(f'Lxx-PBE_{indexFBD}', f'{pushButton}-PBE')
                        replaceVar(f'Lxx-PBE-DO_{indexFBD}', f'{pushButton}-PBE-DO')

                        for index in range(1, 16):
                            replaceVar(f'Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"nFC64 PB IND(L) -> {e}" if str(e) != "list index out of range" else f'nFC64 PB IND(L) -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\nFC64 PB IND(L) {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC11 IND PB & IND FAIL - nFC67 PB IND(X)
        def generatenVFC11nFC67(IT1, IT2, referensiCSV, directorySimpan):
            pbDestin = sorted(list(set([pb[15] for pb in IT1])))
            allPushButton = sorted(
                list(set([pb[15] for pb in IT1 if pb[15].startswith("X") or pb[15].startswith("A")])))

            signalY = sorted(list(set([signal[2] for signal in IT1 if signal[4]])))
            signalG = sorted(list(set([signal[2] for signal in IT1 if signal[5]])))
            signalE = sorted(list(set([signal[2] for signal in IT1 if signal[6]])))
            signalS = sorted(list(set([signal[2] for signal in IT1 if signal[7]])))

            varEnumerated = allPushButton
            jumlahGenFBD = 5
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC67 PB IND(X).csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        pushButton = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        index = 1
                        rutePushButton = sorted(list(set([("S" if "S" in rutePb[1] else "") + rutePb[2] + "-" + simp(
                            rutePb[15]) + ("-CF" if "(CF)" in rutePb[1] else "") for rutePb in IT1 if
                                                          pushButton in rutePb[15]])))
                        for rtpb in rutePushButton:

                            if rtpb.startswith("S"):
                                replaceVar(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'{rtpb[1:]}-RS')
                                replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}-{index}', f'{rtpb[1:rtpb.find("-")]}-GR-DO')
                            else:
                                replaceVar(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'{rtpb}-RS')
                                if rtpb[:rtpb.find("-")] in signalE:
                                    replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}-{index}', f'{rtpb[:rtpb.find("-")]}-ER-DO')
                                if rtpb[:rtpb.find("-")] in signalY:
                                    replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}-{index}',
                                               f'{rtpb[:rtpb.find("-")]}-HR-DO')
                                elif rtpb[:rtpb.find("-")] in signalG:
                                    replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}-{index}',
                                               f'{rtpb[:rtpb.find("-")]}-DR-DO')
                            index += 1

                        replaceVar(f'X/Axx-RRLS_{indexFBD}', f'{pushButton}-RRLS')

                        replaceVar(f'X/Axx-PBE-F_{indexFBD}', f'{pushButton}-PBE-F')
                        replaceVar(f'X/Axx-PBE_{indexFBD}', f'{pushButton}-PBE')
                        replaceVar(f'X/Axx-PBE-DO_{indexFBD}', f'{pushButton}-PBE-DO')

                        for index in range(1, 16):
                            replaceVar(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}-{index}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"nFC67 PB IND(X) -> {e}" if str(e) != "list index out of range" else f'nFC67 PB IND(X) -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\nFC67 PB IND(X) {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC11 IND PB & IND FAIL"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC11 IND PB & IND FAIL"

        generatenVFC11nFC64(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC11nFC65(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC11nFC66(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC11nFC67(IT1, IT2, referensiCSV, directorySimpan)

    ########################## nV FC12 IND SIG FAIL ############################
    def nv_fc12_ind_sig_fail(self, IT1, IT2, referensiCSV, directorySimpan):
        # Generate nV FC12 IND SIG FAIL - Home Signal
        def generatenVFC12HomeSignal(IT1, IT2, referensiCSV, directorySimpan):
            homeSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and not signal[15].startswith('A')])))
            homeSignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0] for signal in homeSignal]
            for hsignal in homeSignal:
                for data in IT1:
                    if hsignal[0] == data[2]:
                        if data[3]:  hsignal[1] = 1  # R
                        if data[4]:  hsignal[2] = 1  # Y
                        if data[5]:  hsignal[3] = 1  # G
                        if data[6]:  hsignal[4] = 1
                        if data[7]:  hsignal[5] = 1
                        if data[8]:  hsignal[6] = 1  # Speed
                        if data[9]:  hsignal[7] = 1  # CF
                        if data[10]:  hsignal[8] = 1  # dir L
                        if data[11]:  hsignal[9] = 1  # dir R
                        if data[12]:  hsignal[10] = data[12]  # MJ
                        if data[13]:  hsignal[11] = 1
                        if data[14]:  hsignal[12] = 1
            homeSignal = [signal for signal in homeSignal if signal[1] or signal[2] or signal[3]]
            # print(f"start signal : {homeSignal}")
            varEnumerated = homeSignal
            jumlahGenFBD = 5
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\Home Signal.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        indexRuteStick = 1
                        # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                        hsignal = homeSignal[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'Jxx-ECR_{indexFBD}', f'{hsignal[0]}-ECR')
                        replaceVar(f'Jxx-EKR_{indexFBD}', f'{hsignal[0]}-EKR')
                        replaceVar(f'Jxx-ECRF_{indexFBD}', f'{hsignal[0]}-ECRF')
                        replaceVar(f'Jxx-FF-TE_{indexFBD}', f'{hsignal[0]}-FF-TE')
                        replaceVar(f'Jxx-FAIL-A_{indexFBD}', f'{hsignal[0]}-FAIL-A')
                        replaceVar(f'Jxx-EK-TE_{indexFBD}', f'{hsignal[0]}-EK-TE')
                        replaceVar(f'Jxx-EKR-A_{indexFBD}', f'{hsignal[0]}-EKR-A')

                        ### RS dan ECR diisi untuk rute CF bersinyal merah
                        # if hsignal[1] or hsignal[2] or hsignal[3]:
                        #     for data in IT1:
                        #         cf = ""
                        #         if "(CF)" in data[1]:
                        #             cf = "-CF"
                        #         if hsignal[2] or hsignal[3]:
                        #             if hsignal[0] in data[2] and "(T)" in data[1]:
                        #                 replaceVar(f'Jxx-xx-RS_{indexFBD}-{indexRuteStick}', f'{data[2]}-{simp(data[15])}-RS')
                        #                 indexRuteStick += 1
                        #         elif hsignal[1]:
                        #             if hsignal[0] in data[2] and ("(E)" in data[1] or "(CF)" in data[1]):
                        #
                        #                 replaceVar(f'Jxx-xx-RS_{indexFBD}-{indexRuteStick}', f'{data[2]}-{simp(data[15])}{cf}-RS')
                        #                 indexRuteStick += 1
                        #
                        # if hsignal[1] and hsignal[2]:
                        #     replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{hsignal[0]}-HR-DO')
                        # elif hsignal[1] and hsignal[3]:
                        #     replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{hsignal[0]}-DR-DO')
                        # else:
                        #     replaceVar(f'Jxx-HR-DO_{indexFBD}', f'TRUE')

                        ### RS dan HR kosong untuk rute CF bersinyal merah
                        if hsignal[1] or hsignal[2] or hsignal[3]:
                            for data in IT1:
                                if hsignal[2] or hsignal[3]:
                                    if hsignal[0] in data[2] and "(T)" in data[1]:
                                        replaceVar(f'Jxx-xx-RS_{indexFBD}-{indexRuteStick}', f'{data[2]}-{simp(data[15])}-RS')
                                        indexRuteStick += 1

                        if hsignal[1] and hsignal[2]:
                            replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{hsignal[0]}-HR-DO')
                        elif hsignal[1] and hsignal[3]:
                            replaceVar(f'Jxx-HR-DO_{indexFBD}', f'{hsignal[0]}-DR-DO')
                        else:
                            replaceVar(f'Jxx-HR-DO_{indexFBD}', f'FALSE')


                        for indexRuteStick in range(1, 21):
                            replaceVar(f'Jxx-xx-RS_{indexFBD}-{indexRuteStick}', f'FALSE')

                        indexRuteStick = 1
                        if hsignal[6]:
                            replaceVar(f'Jxx-SECR_{indexFBD}', f'{hsignal[0]}-SECR')
                            replaceVar(f'Jxx-SR-DO_{indexFBD}', f'{hsignal[0]}-SR-DO')
                            replaceVar(f'Jxx-SECRF_{indexFBD}', f'{hsignal[0]}-SECRF')
                            replaceVar(f'Jxx-I3-FF-TE_{indexFBD}', f'{hsignal[0]}-I3-FF-TE')
                            replaceVar(f'Jxx-S-FAIL-A_{indexFBD}', f'{hsignal[0]}-S-FAIL-A')
                            for data in IT1:
                                if hsignal[0] in data[2] and "(T)" in data[1] and data[8]:
                                    replaceVar(f'Jxx-xx-RS-SPEED_{indexFBD}-{indexRuteStick}',
                                               f'{data[2]}-{simp(data[15])}-RS')
                                    indexRuteStick += 1
                        if hsignal[10] and (hsignal[11] or hsignal[12]):
                            replaceVar(f'MJxx-ECR_{indexFBD}', f'{hsignal[10]}-ECR')
                            replaceVar(f'MJxx-EKR_{indexFBD}', f'{hsignal[10]}-EKR')
                            replaceVar(f'MJxx-FF-TE_{indexFBD}', f'{hsignal[10]}-FF-TE')
                            replaceVar(f'MJxx-FAIL-A_{indexFBD}', f'{hsignal[10]}-FAIL-A')
                            replaceVar(f'MJxx-EK-TE_{indexFBD}', f'{hsignal[10]}-EK-TE')
                            replaceVar(f'MJxx-EKR-A_{indexFBD}', f'{hsignal[10]}-EKR-A')

                        for indexRuteStick in range(1, 21):
                            replaceVar(f'Jxx-xx-RS-SPEED_{indexFBD}-{indexRuteStick}', f'FALSE')

                    except Exception as e:
                        print(f"Home Signal -> {e}" if str(e) != "list index out of range" else f'Home Signal -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\Home Signal {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC12 IND SIG FAIL - Depart Signal
        def generatenVFC12DepartSignal(IT1, IT2, referensiCSV, directorySimpan):
            departSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and signal[15].startswith('A')])))


            other = sorted(list(set([signal[15] for signal in IT1 if signal[17] and signal[15] not in departSignal and not signal[15].startswith('A')])))

            departSignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0] for signal in departSignal]
            other = [[signal, 1, 0, 0, 0, 0, 0, 0, 0, 0] for signal in other]

            departSignal += other
            for dsignal in departSignal:
                for data in IT1:
                    if dsignal[0] == data[2]:
                        if data[3]:  dsignal[1] = 1  # R
                        if data[4]:  dsignal[2] = 1  # Y
                        if data[5]:  dsignal[3] = 1  # G
                        if data[6]:  dsignal[4] = 1
                        if data[7]:  dsignal[5] = 1
                        if data[8]:  dsignal[6] = 1  # Speed
                        if data[9]:  dsignal[7] = 1  # CF
                        if data[10]:  dsignal[8] = 1  # dir L
                        if data[11]:  dsignal[9] = 1  # dir R
                        if data[12]:  dsignal[10] = data[12]  # MJ
                        if data[13]:  dsignal[11] = 1
                        if data[14]:  dsignal[12] = 1

            departSignal = [signal for signal in departSignal if signal[2] or signal[3]]


            varEnumerated = departSignal
            jumlahGenFBD = 10
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\Depart Signal.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        indexRuteStick = 1
                        # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                        dsignal = departSignal[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'J/JLxx-ECR_{indexFBD}', f'{dsignal[0]}-ECR')
                        replaceVar(f'J/JLxx-EKR_{indexFBD}', f'{dsignal[0]}-EKR')
                        replaceVar(f'J/JLxx-ECRF_{indexFBD}', f'{dsignal[0]}-ECRF')
                        replaceVar(f'J/JLxx-FF-TE_{indexFBD}', f'{dsignal[0]}-FF-TE')
                        replaceVar(f'J/JLxx-FAIL-A_{indexFBD}', f'{dsignal[0]}-FAIL-A')
                        replaceVar(f'J/JLxx-EK-TE_{indexFBD}', f'{dsignal[0]}-EK-TE')
                        replaceVar(f'J/JLxx-EKR-A_{indexFBD}', f'{dsignal[0]}-EKR-A')
                        # untuk sinyal masuk 1 aspek tidak perlu isi HR-DO dan Rute Stick
                        if dsignal[1] and (dsignal[2] or dsignal[3]):
                            if dsignal[1] and dsignal[2]:
                                replaceVar(f'J/JLxx-HR-DO_{indexFBD}', f'{dsignal[0]}-HR-DO')
                            elif dsignal[1] and not dsignal[2] and dsignal[3]:
                                replaceVar(f'J/JLxx-HR-DO_{indexFBD}', f'{dsignal[0]}-DR-DO')
                            elif dsignal[1] and not dsignal[2] and not dsignal[3]:
                                replaceVar(f'J/JLxx-HR-DO_{indexFBD}', f'FALSE')
                            for data in IT1:
                                if dsignal[0] in data[2] and "(T)" in data[1]:
                                    replaceVar(f'J/JLxx-xx-RS_{indexFBD}-{indexRuteStick}',
                                               f'{data[2]}-{simp(data[15])}-RS')
                                    indexRuteStick += 1

                        for indexRuteStick in range(1, 6):
                            replaceVar(f'J/JLxx-xx-RS_{indexFBD}-{indexRuteStick}', f'FALSE')

                        if dsignal[7]:
                            replaceVar(f'J/JLxx-CFEK_{indexFBD}', f'{dsignal[0]}-CFEK')
                            replaceVar(f'J/JLxx-CFR-DO_{indexFBD}', f'{dsignal[0]}-CFR-DO')
                            replaceVar(f'J/JLxx-CF-TE_{indexFBD}', f'{dsignal[0]}-CF-TE')
                            replaceVar(f'J/JLxx-CF-FAIL-A_{indexFBD}', f'{dsignal[0]}-CF-FAIL-A')

                        if dsignal[8]:
                            replaceVar(f'J/JLxx-DKR_{indexFBD}', f'{dsignal[0]}-DKR')
                            replaceVar(f'J/JLxx-LDR-DO_{indexFBD}', f'{dsignal[0]}-LDR-DO')
                            replaceVar(f'J/JLxx-LK-TE_{indexFBD}', f'{dsignal[0]}-LK-TE')
                            replaceVar(f'J/JLxx-LKR-A_{indexFBD}', f'{dsignal[0]}-LKR-A')

                        if dsignal[9]:
                            replaceVar(f'J/JLxx-DKR_{indexFBD}', f'{dsignal[0]}-DKR')
                            replaceVar(f'J/JLxx-RDR-DO_{indexFBD}', f'{dsignal[0]}-RDR-DO')
                            replaceVar(f'J/JLxx-RK-TE_{indexFBD}', f'{dsignal[0]}-RK-TE')
                            replaceVar(f'J/JLxx-RKR-A_{indexFBD}', f'{dsignal[0]}-RKR-A')

                        indexRuteStick = 1
                        if dsignal[6]:
                            replaceVar(f'J/JLxx-SECR_{indexFBD}', f'{dsignal[0]}-SECR')
                            replaceVar(f'J/JLxx-SR-DO_{indexFBD}', f'{dsignal[0]}-SR-DO')
                            replaceVar(f'J/JLxx-SECRF_{indexFBD}', f'{dsignal[0]}-SECRF')
                            replaceVar(f'J/JLxx-I3-FF-TE_{indexFBD}', f'{dsignal[0]}-I3-FF-TE')
                            replaceVar(f'J/JLxx-S-FAIL-A_{indexFBD}', f'{dsignal[0]}-S-FAIL-A')
                            for data in IT1:
                                if dsignal[0] in data[2] and "(T)" in data[1] and data[8]:
                                    replaceVar(f'Jxx-xx-RS-SPEED_{indexFBD}-{indexRuteStick}',
                                               f'{data[2]}-{simp(data[15])}-RS')
                                    indexRuteStick += 1

                        for indexRuteStick in range(1, 6):
                            replaceVar(f'Jxx-xx-RS-SPEED_{indexFBD}-{indexRuteStick}', f'FALSE')

                    except Exception as e:
                        print(f"Depart Signal -> {e}" if str(e) != "list index out of range" else f'Depart Signal -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\Depart Signal {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC12 IND SIG FAIL - nFC101 S FAIL(BUNDLE SS) MOD
        def generatenVFC12nFC101(IT1, IT2, referensiCSV, directorySimpan):
            homeSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and not signal[15].startswith('A')])))
            homeSignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0] for signal in homeSignal]

            mjSignal = sorted(list(set([signal[12] for signal in IT1 if signal[12] and (signal[13] or signal[14])])))
            mjSignal = [[signal, 1, 0, 0, 0, 0, 0, 0, 0, 0] for signal in mjSignal]

            departSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and signal[15].startswith('A')])))

            other = sorted(list(set([signal[15] for signal in IT1 if
                                     signal[17] and signal[15] not in departSignal and not signal[15].startswith(
                                         'A')])))
            departSignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0] for signal in departSignal]
            other = [[signal, 1, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0] for signal in other]

            allSignal = homeSignal + mjSignal + departSignal + other

            for alsignal in allSignal:
                for data in IT1:
                    if alsignal[0] == data[2]:
                        if data[3]:  alsignal[1] = 1  # R
                        if data[4]:  alsignal[2] = 1  # Y
                        if data[5]:  alsignal[3] = 1  # G
                        if data[6]:  alsignal[4] = 1
                        if data[7]:  alsignal[5] = 1
                        if data[8]:  alsignal[6] = 1  # Speed
                        if data[9]:  alsignal[7] = 1  # CF
                        if data[10]:  alsignal[8] = 1  # dir L
                        if data[11]:  alsignal[9] = 1  # dir R

            allSignal = [signal for signal in allSignal if signal[1] or signal[2] or signal[3] or "MJ" in signal[0]]

            indexSignal = 0
            varEnumerated = allSignal
            jumlahGenFBD = 10
            for indexCSV in range(0, len(varEnumerated) // 5, jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC101 S FAIL(BUNDLE SS) MOD.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    # print(indexFBD)
                    indexFBD += 1
                    try:
                        replaceVar(f'SIGNAL-FE-Fx_{indexFBD}', f'SIGNAL-FE-F{indexFBD + indexCSV}')
                        replaceVar(f'SIGNAL-FEx_{indexFBD}', f'SIGNAL-FE{indexFBD + indexCSV}')
                        for indexJxx in range(1, 6):
                            # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                            alsignal = allSignal[indexSignal]
                            indexSignal += 1
                            replaceVar(f'Jxx{indexJxx}-FF-TE_{indexFBD}', f'{alsignal[0]}-FF-TE')
                            replaceVar(f'Jxx{indexJxx}-FAIL-A_{indexFBD}', f'{alsignal[0]}-FAIL-A')
                            replaceVar(f'Jxx{indexJxx}-EK-TE_{indexFBD}', f'{alsignal[0]}-EK-TE')
                            replaceVar(f'Jxx{indexJxx}-EKR-A_{indexFBD}', f'{alsignal[0]}-EKR-A')

                            if alsignal[6]:
                                replaceVar(f'Jxx{indexJxx}-I3-FF-TE_{indexFBD}', f'{alsignal[0]}-I3-FF-TE')
                                replaceVar(f'Jxx{indexJxx}-S-FAIL-A_{indexFBD}', f'{alsignal[0]}-S-FAIL-A')

                            if alsignal[7]:
                                replaceVar(f'Jxx{indexJxx}-CF-TE_{indexFBD}', f'{alsignal[0]}-CF-TE')
                                replaceVar(f'Jxx{indexJxx}-CF-FAIL-A_{indexFBD}', f'{alsignal[0]}-CF-FAIL-A')

                            replaceVar(f'Jxx{indexJxx}-FF-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-FAIL-A_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-EK-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-EKR-A_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-I3-FF-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-S-FAIL-A_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-CF-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-CF-FAIL-A_{indexFBD}', 'FALSE')

                    except Exception as e:
                        print(f"nFC101 S FAIL(BUNDLE SS) MOD -> {e}" if str(e) != "list index out of range" else f'nFC101 S FAIL(BUNDLE SS) MOD -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\nFC101 S FAIL(BUNDLE SS) MOD {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                    index=False)

            allSignal = [signal for signal in allSignal if signal[8] or signal[9]]
            indexSignal = 0
            varEnumerated = allSignal
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC101 S FAIL(BUNDLE SS) MOD.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    try:
                        replaceVar(f'SIGNAL-FE-Fx_{indexFBD}', f'DIR-FE-F{indexFBD + indexCSV}')
                        replaceVar(f'SIGNAL-FEx_{indexFBD}', f'DIR-FE{indexFBD + indexCSV}')
                        for indexJxx in range(1, 6):
                            # jika tidak ada data yang dibutuhkan, ganti dengan nilai default
                            alsignal = allSignal[indexSignal]
                            indexSignal += 1
                            if alsignal[8]:
                                replaceVar(f'Jxx{indexJxx}-FF-TE_{indexFBD}', f'{alsignal[0]}-LK-TE')
                                replaceVar(f'Jxx{indexJxx}-FAIL-A_{indexFBD}', f'{alsignal[0]}-LKR-A')

                            if alsignal[9]:
                                replaceVar(f'Jxx{indexJxx}-EK-TE_{indexFBD}', f'{alsignal[0]}-RK-TE')
                                replaceVar(f'Jxx{indexJxx}-EKR-A_{indexFBD}', f'{alsignal[0]}-RKR-A')

                            alsignal = allSignal[indexSignal]
                            indexSignal += 1
                            # print(indexFBD * 10 + 4 + indexJxx)
                            if alsignal[8]:
                                replaceVar(f'Jxx{indexJxx}-I3-FF-TE_{indexFBD}', f'{alsignal[0]}-LK-TE')
                                replaceVar(f'Jxx{indexJxx}-S-FAIL-A_{indexFBD}', f'{alsignal[0]}-LKR-A')

                            if alsignal[9]:
                                replaceVar(f'Jxx{indexJxx}-CF-TE_{indexFBD}', f'{alsignal[0]}-RK-TE')
                                replaceVar(f'Jxx{indexJxx}-CF-FAIL-A_{indexFBD}', f'{alsignal[0]}-RKR-A')

                            replaceVar(f'Jxx{indexJxx}-FF-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-FAIL-A_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-EK-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-EKR-A_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-I3-FF-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-S-FAIL-A_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-CF-TE_{indexFBD}', 'FALSE')
                            replaceVar(f'Jxx{indexJxx}-CF-FAIL-A_{indexFBD}', 'FALSE')



                    except Exception as e:
                        print(f"nFC101 S FAIL(BUNDLE SS) MOD Direction-> {e}" if str(e) != "list index out of range" else f'nFC101 S FAIL(BUNDLE SS) MOD Direction -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\nFC101 S FAIL(BUNDLE SS) MOD Direction {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                    index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC12 IND SIG FAIL"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC12 IND SIG FAIL"

        generatenVFC12HomeSignal(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC12DepartSignal(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC12nFC101(IT1, IT2, referensiCSV, directorySimpan)

    ########################### nV FC12 IND SIG FAIL ###########################
    def nv_fc13_ind_point_fail(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # nFC70 SW FAIL
        def nfc70_sw_fail():
            varEnumerated = sorted([w for w in PM if w[0].startswith("W")])

            jumlahGenFBD = 10
            FBDtujuan = "nFC70 SW FAIL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        wesel = data_var[0]

                        replace_var(f'Wxx-TRAIL-CTRL_{indexFBD}', f'{wesel}-TRAIL-CTRL')
                        replace_var(f'Wxx-RST-CTRL_{indexFBD}', f'{wesel}-RST-CTRL')
                        replace_var(f'Wxx-NW-TE_{indexFBD}', f'{wesel}-NW-TE')
                        replace_var(f'Wxx-RW-TE_{indexFBD}', f'{wesel}-RW-TE')
                        replace_var(f'Wxx-NWC_{indexFBD}', f'{wesel}-NWC')
                        replace_var(f'Wxx-RWC_{indexFBD}', f'{wesel}-RWC')
                        replace_var(f'Wxx-NWP_{indexFBD}', f'{wesel}-NWP')
                        replace_var(f'Wxx-RWP_{indexFBD}', f'{wesel}-RWP')
                        replace_var(f'Wxx-LS_{indexFBD}', f'{wesel}-LS')
                        replace_var(f'Wxx-BACK-TO-N_{indexFBD}', f'{wesel}-BACK-TO-N')
                        replace_var(f'Wxx-BACK-TO-R_{indexFBD}', f'{wesel}-BACK-TO-R')
                        replace_var(f'Wxx-BLOCK_{indexFBD}', f'{wesel}-BLOCK')
                        replace_var(f'Wxx-N-BLOCK_{indexFBD}', f'{wesel}-N-BLOCK')
                        replace_var(f'Wxx-R-BLOCK_{indexFBD}', f'{wesel}-R-BLOCK')

                        replace_var(f'Wxx-SW-F-ACK_{indexFBD}', f'{wesel}-SW-F-ACK')
                        replace_var(f'Wxx-SW-FAIL_{indexFBD}', f'{wesel}-SW-FAIL')
                        replace_var(f'Wxx-OOC_{indexFBD}', f'{wesel}-OOC')
                        replace_var(f'Wxx-OOC-RD_{indexFBD}', f'{wesel}-OOC-RD')
                        replace_var(f'Wxx-TRAIL-CTRL-Z_{indexFBD}', f'{wesel}-TRAIL-CTRL-Z')
                        replace_var(f'Wxx-N-FAIL_{indexFBD}', f'{wesel}-N-FAIL')
                        replace_var(f'Wxx-R-FAIL_{indexFBD}', f'{wesel}-R-FAIL')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nFC70 DERAILEUR FAIL
        def nfc70_deraileur_fail():
            # list variable semua deraileur
            allDeraileur = list(
                set((' '.join([d[19].replace("-N", "").replace("-R", "").strip() for d in IT1])).split() +
                    (' '.join([d[8].replace("-N", "").replace("-R", "").strip() for d in IT2])).split()))

            sG = 10
            # pecah hasil generator menjadi per 10 output
            for x in range(0, len(allDeraileur), sG):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC70 DERAILEUR FAIL.csv")
                for y in range(sG):
                    # jika jumlah rute tidak kelipatan 10 dan iterasi terakhir selesaikan looping
                    if len(allDeraileur) % sG != 0 and x == (math.floor(len(allDeraileur) / sG) * sG) and y == len(
                            allDeraileur) % sG:
                        break
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-FAIL-ACK_' + str(y + 1): allDeraileur[y + x] + '-FAIL-ACK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-FAIL-A_' + str(y + 1): allDeraileur[y + x] + '-FAIL-A'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-FAIL_' + str(y + 1): allDeraileur[y + x] + '-FAIL'})

                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-REL-REQ_' + str(y + 1): allDeraileur[y + x] + '-REL-REQ'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-R-OK_' + str(y + 1): allDeraileur[y + x] + '-R-OK'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-NP_' + str(y + 1): allDeraileur[y + x] + '-NP'})
                    dfLogic['New Name'] = dfLogic['New Name'].replace(
                        {'Dxx-RP_' + str(y + 1): allDeraileur[y + x] + '-RP'})

                    dfLogic.to_csv(directorySimpan + "\\nFC89 nFC70 DERAILEUR FAIL " + str(
                        x) + "-" + str(x + sG) + ".csv", index=False)


        directorySimpan = directorySimpan + "\\Non Vital\\nV FC13 IND POINT FAIL"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC13 IND POINT FAIL"

        nfc70_sw_fail()
        nfc70_deraileur_fail()

    ######################### nV FC13 IND POINT FAIL ###########################
    def nv_fc14_counter(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # Generate nV FC14 COUNTER - nFC73 SYS PPR J
        def generatenVFC14nFC73(IT1, IT2, referensiCSV, directorySimpan):
            homeSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and not signal[15].startswith('A')])))
            homeSignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0] for signal in homeSignal]
            for hsignal in homeSignal:
                for data in IT1:
                    if hsignal[0] == data[2]:
                        if data[3]:  hsignal[1] = 1  # R
                        if data[4]:  hsignal[2] = 1  # Y
                        if data[5]:  hsignal[3] = 1  # G
                        if data[6]:  hsignal[4] = 1  # E
                        if data[7]:  hsignal[5] = 1  # SHUNT
                        if data[8]:  hsignal[6] = 1  # Speed
                        if data[9]:  hsignal[7] = 1  # CF
                        if data[10]:  hsignal[8] = 1  # dir L
                        if data[11]:  hsignal[9] = 1  # dir R
                        if data[12]:  hsignal[10] = data[12]  # MJ
                        if data[13]:  hsignal[11] = 1
                        if data[14]:  hsignal[12] = 1
            homeSignal = [signal for signal in homeSignal if signal[1] or signal[2] or signal[3]]

            Asignal = sorted(
                list(set([signal[15] for signal in IT1 if "(S)" not in signal[1] and signal[15].startswith('A')])))
            Asignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0] for signal in Asignal]

            varEnumerated = homeSignal + Asignal
            jumlahGenFBD = 10
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC73 SYS PPR J.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        hsignal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        if hsignal[0].startswith('A'):
                            replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-RST-CT_{indexFBD}', f'HAPUS VARIABLE INI')
                        else:
                            replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'{hsignal[0]}-RST-CTRL')
                            if hsignal[1] and hsignal[2]:
                                replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{hsignal[0]}-HR-DO')
                            elif hsignal[1] and not hsignal[2] and hsignal[3]:
                                replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{hsignal[0]}-DR-DO')
                            elif hsignal[1] and not hsignal[2] and not hsignal[3]:
                                replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'FALSE')
                            if hsignal[4]:
                                replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{hsignal[0]}-ER-DO')
                            else:
                                replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-RST-CT_{indexFBD}', f'{hsignal[0]}-RST-CT')
                        replaceVar(f'J/JL/Lxx-RRLS_{indexFBD}', f'{hsignal[0]}-RRLS')
                        replaceVar(f'J/JL/Lxx-RRLS-CT_{indexFBD}', f'{hsignal[0]}-RRLS-CT')

                    except Exception as e:
                        print(f"nFC73 SYS PPR J -> {e}" if str(e) != "list index out of range" else f'nFC73 SYS PPR J -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\nFC73 SYS PPR J {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC14 COUNTER - nFC74 SYS PPR JL
        def generatenVFC14nFC74(IT1, IT2, referensiCSV, directorySimpan):
            destS = sorted(list(set([signal[15] for signal in IT1])))
            departSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and signal[15].startswith('A')])))
            departSignal = [[signal, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", 0, 0] for signal in departSignal]
            for hsignal in departSignal:
                for data in IT1:
                    if hsignal[0] == data[2]:
                        if data[3]:  hsignal[1] = 1  # R
                        if data[4]:  hsignal[2] = 1  # Y
                        if data[5]:  hsignal[3] = 1  # G
                        if data[6]:  hsignal[4] = 1  # E
                        if data[7]:  hsignal[5] = 1  # SHUNT
                        if data[8]:  hsignal[6] = 1  # Speed
                        if data[9]:  hsignal[7] = 1  # CF
                        if data[10]:  hsignal[8] = 1  # dir L
                        if data[11]:  hsignal[9] = 1  # dir R
                        if data[12]:  hsignal[10] = data[12]  # MJ
                        if data[13]:  hsignal[11] = 1
                        if data[14]:  hsignal[12] = 1
            departSignal = [signal for signal in departSignal if (signal[1] or signal[2] or signal[3])]

            varEnumerated = departSignal
            jumlahGenFBD = 10
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC74 SYS PPR JL.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        hsignal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        if hsignal[0].startswith('A'):
                            replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-RST-CT_{indexFBD}', f'HAPUS VARIABLE INI')
                        elif hsignal[0] not in destS:
                            replaceVar(f'J/JL/Lxx-RRLS_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-RRLS-CT_{indexFBD}', f'HAPUS VARIABLE INI')
                        else:
                            replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'{hsignal[0]}-RST-CTRL')
                            if hsignal[1] and hsignal[2]:
                                replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{hsignal[0]}-HR-DO')
                            elif hsignal[1] and not hsignal[2] and hsignal[3]:
                                replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{hsignal[0]}-DR-DO')
                            elif hsignal[1] and not hsignal[2] and not hsignal[3]:
                                replaceVar(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'FALSE')
                            if hsignal[4]:
                                replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{hsignal[0]}-ER-DO')
                            else:
                                replaceVar(f'J/JL/Lxx-ER-DO_{indexFBD}', f'FALSE')
                            if hsignal[5]:
                                replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{hsignal[0]}-GR-DO')
                            else:
                                replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')
                            replaceVar(f'J/JL/Lxx-RST-CT_{indexFBD}', f'{hsignal[0]}-RST-CT')
                        replaceVar(f'J/JL/Lxx-RRLS_{indexFBD}', f'{hsignal[0]}-RRLS')
                        replaceVar(f'J/JL/Lxx-RRLS-CT_{indexFBD}', f'{hsignal[0]}-RRLS-CT')

                    except Exception as e:
                        print(f"nFC74 SYS PPR JL -> {e}" if str(e) != "list index out of range" else f'nFC74 SYS PPR JL  -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\nFC74 SYS PPR JL {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC14 COUNTER - nFC75 SYS PPR L
        def generatenVFC14nFC75(IT1, IT2, referensiCSV, directorySimpan):
            homeSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and not signal[15].startswith('A')])))
            departSignal = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" not in signal[1] and signal[15].startswith('A')])))

            homeSigShunt = sorted(
                list(set([signal[2] for signal in IT1 if "(S)" in signal[1] and signal[2] not in departSignal])))
            destSigShunt = sorted(
                list(set([signal[15] for signal in IT1 if "(S)" in signal[1] and signal[15] not in departSignal])))

            shuntSignal = sorted(list(set(homeSigShunt + destSigShunt)))

            varEnumerated = shuntSignal
            jumlahGenFBD = 10
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC75 SYS PPR L.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        hsignal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        if hsignal in destSigShunt:
                            replaceVar(f'J/JL/Lxx-RRLS_{indexFBD}', f'{hsignal}-RRLS')
                            replaceVar(f'J/JL/Lxx-RRLS-CT_{indexFBD}', f'{hsignal}-RRLS-CT')
                        if not hsignal.startswith('X'):
                            replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'{hsignal}-RST-CTRL')
                            replaceVar(f'J/JL/Lxx-RST-CT_{indexFBD}', f'{hsignal}-RST-CT')
                            replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{hsignal}-GR-DO')

                        replaceVar(f'J/JL/Lxx-RST-CTRL_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-RST-CT_{indexFBD}', f'HAPUS VARIABLE INI')
                        replaceVar(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-RRLS_{indexFBD}', f'FALSE')
                        replaceVar(f'J/JL/Lxx-RRLS-CT_{indexFBD}', f'HAPUS VARIABLE INI')

                    except Exception as e:
                        print(f"nFC75 SYS PPR L -> {e}" if str(e) != "list index out of range" else f'nFC75 SYS PPR L -> Done..')
                        break
                    finally:
                        pass
                replaceVar(f'OUTPUT-DO', f'TPR-COUNT-DO')
                dfLogic.to_csv(directorySimpan + f"\\nFC75 SYS PPR L {indexCSV} - {indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # Generate nV FC14 COUNTER - nFC76 SYS COUNTER
        def generatenVFC14nFC76(IT1, IT2, referensiCSV, directorySimpan, PM):
            ############ TPR COUNT DO ##########
            tpr_asal = sorted(list(set([signal[2] + "-RST-CT" for signal in IT1])))
            tpr_tujuan = sorted(list(set([signal[15] + "-RRLS-CT" for signal in IT1]))) + sorted(list(set([signal[2] + "-RRLS-CT" for signal in IT1 if "(S)" not in signal[1] and not signal[15].startswith("A")])))
            varEnumerated = tpr_asal + tpr_tujuan
            jumlahGenFBD = 100
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC76 SYS COUNTER.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'INPUT{indexFBD}', f'{signal}')
                    except Exception as e:
                        print(f"nFC76 SYS COUNTER - TPR COUNT DO -> {e}" if str(e) != "list index out of range" else f'nFC76 SYS COUNTER - TPR COUNT DO -> Done..')
                        break
                    finally:
                        pass
                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    replaceVar(f'INPUT{indexFBD}', f'FALSE')
                replaceVar(f'OUTPUT-DO', f'TPR-COUNT-DO')
                dfLogic.to_csv(directorySimpan + f"\\nFC76 SYS COUNTER - TPR COUNT DO {indexCSV}.csv", index=False)

            ############ TSD COUNT DO ##########
            allRute = sorted(list(
                set([signal[2] + "-" + simp(signal[15]) + ("-CF-E-COUNT" if "(CF)" in signal[1] else "-E-COUNT") for
                     signal in IT1 if "(E)" in signal[1] or "(CF)" in signal[1]])))
            varEnumerated = allRute
            jumlahGenFBD = 100
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC76 SYS COUNTER.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'INPUT{indexFBD}', f'{signal}')
                    except Exception as e:
                        print(f"nFC76 SYS COUNTER - TSD COUNT DO -> {e}" if str(e) != "list index out of range" else f'nFC76 SYS COUNTER - TSD COUNT DO -> Done..')
                        break
                    finally:
                        pass
                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    replaceVar(f'INPUT{indexFBD}', f'FALSE')
                replaceVar(f'OUTPUT-DO', f'TSD-COUNT-DO')
                dfLogic.to_csv(
                    directorySimpan + f"\\nFC76 SYS COUNTER - TSD COUNT DO {indexCSV}.csv", index=False)

            ############ TBW COUNT DO ##########
            allWesel = [wesel[0] + "-SWRLS" for wesel in PM if not wesel[0].startswith("D")]
            varEnumerated = allWesel
            jumlahGenFBD = 100
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC76 SYS COUNTER.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'INPUT{indexFBD}', f'{signal}')
                    except Exception as e:
                        print(f"nFC76 SYS COUNTER - TBW COUNT DO  -> {e}" if str(e) != "list index out of range" else f'nFC76 SYS COUNTER - TBW COUNT DO -> Done..')
                        break
                    finally:
                        pass
                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    replaceVar(f'INPUT{indexFBD}', f'FALSE')
                replaceVar(f'OUTPUT-DO', f'TBW-COUNT-DO')
                dfLogic.to_csv(directorySimpan + f"\\nFC76 SYS COUNTER - TBW COUNT DO {indexCSV}.csv", index=False)

            ############ TWT COUNT DO ##########
            allWesel = [wesel[0] + "-TRAIL-CTRL-Z" for wesel in PM if not wesel[0].startswith("D")]
            varEnumerated = allWesel
            jumlahGenFBD = 100
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC76 SYS COUNTER.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'INPUT{indexFBD}', f'{signal}')
                    except Exception as e:
                        print(f"nFC76 SYS COUNTER - TWT COUNT DO -> {e}" if str(e) != "list index out of range" else f'nFC76 SYS COUNTER - TWT COUNT DO -> Done..')
                        break
                    finally:
                        pass
                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    replaceVar(f'INPUT{indexFBD}', f'FALSE')
                replaceVar(f'OUTPUT-DO', f'TWT-COUNT-DO')
                dfLogic.to_csv(directorySimpan + f"\\nFC76 SYS COUNTER - TWT COUNT DO {indexCSV}.csv", index=False)

            ############ TBMS COUNT DO ##########
            allAsignal = sorted(list(
                set([signal[15] + ("-CF-TBMS" if "(CF)" in signal[1] else "-TBMS") for signal in IT1 if
                     signal[15].startswith("A")])))
            varEnumerated = allAsignal
            jumlahGenFBD = 100
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC76 SYS COUNTER.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'INPUT{indexFBD}', f'{signal}')
                    except Exception as e:
                        print(f"nFC76 SYS COUNTER - TBMS COUNT DO  -> {e}" if str(e) != "list index out of range" else f'nFC76 SYS COUNTER - TBMS COUNT DO -> Done..')
                        break
                    finally:
                        pass
                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    replaceVar(f'INPUT{indexFBD}', f'FALSE')
                replaceVar(f'OUTPUT-DO', f'TBMS-COUNT-DO')
                dfLogic.to_csv(directorySimpan + f"\\nFC76 SYS COUNTER - TBMS COUNT DO {indexCSV}.csv", index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC14 COUNTER"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC14 COUNTER"

        generatenVFC14nFC73(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC14nFC74(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC14nFC75(IT1, IT2, referensiCSV, directorySimpan)
        generatenVFC14nFC76(IT1, IT2, referensiCSV, directorySimpan, PM)

    ############################# nV FC15 COMM FUNCT & LAMPTEST  ###############
    def nv_fc15_com_func_and_lamptest(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        def nfc83_sys_pb_fail():
            homeSignal = sorted(list(set([signal[2] + "-PB-DI" for signal in IT1])))
            departSignal = sorted(list(set([signal[15] + "-PB-DI" for signal in IT1])))
            signal = sorted(list(set(homeSignal + departSignal)))
            allWesel = sorted(list(set([wesel[0] + "-PB-DI" for wesel in PM])))
            all_jpl = []
            for it in IT1:
                for jpl in it[25].split(" "):
                    if "JPL" in jpl:
                        all_jpl.append(jpl + "-PB-DI")
            pblist = sorted(list(
                set(["LAMPTEST-PB-DI", "TBKWM-PB-DI", "TBKW-PB-DI", "TBMS-PB-DI", "TBW-PB-DI", "THB-PB-DI",
                     "TKGWM-PB-DI", "TKGW-PB-DI", "TKW-PB-DI", "TPR-BANTU-PB-DI", "TPR-PB-DI", "TSD-PB-DI", "TUR-PB-DI",
                     "TWT-PB-DI"])))

            varEnumerated = pblist + signal + allWesel + sorted(list(set(all_jpl)))
            jumlahGenFBD = 200
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + "\\nFC83 SYS PB FAIL.csv")

                def replaceVar(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        signal = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        replaceVar(f'INPUT{indexFBD}', f'{signal}')
                    except Exception as e:
                        print(f"nFC83 SYS PB FAIL -> {e}" if str(e) != "list index out of range" else f'nFC83 SYS PB FAIL -> Done..')
                        break
                    finally:
                        pass
                for indexFBD in range(jumlahGenFBD):
                    indexFBD += 1
                    replaceVar(f'INPUT{indexFBD}', f'FALSE')
                dfLogic.to_csv(directorySimpan + f"\\nFC83 SYS PB FAIL {indexCSV}.csv", index=False)

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC15 COMM FUNCT & LAMPTEST"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC15 COMM FUNCT & LAMPTEST"

        nfc83_sys_pb_fail()

    ################################## nV FC16 LEVEL CROSSING ################################
    def nv_fc16_level_crossing(self, IT1, IT2, referensiCSV, directorySimpan, PM, jpldata):
        def nfc87_lx_nv():
            varEnumerated = jpldata
            jumlahGenFBD = 5
            FBDtujuan = "nFC87 LX NV"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        jpl_dir = data_var[0]
                        jpl_name = data_var[0].split("-")[0]
                        jpl_track = data_var[1]
                        jpl_wesel = data_var[2]
                        jpl_arah = "EAST" if data_var[0].split("-")[1].startswith("E") else "WEST"


                        replace_var(f'JPLxx-W/Exx-L_{indexFBD}', f'JPL{jpl_dir}-L')
                        replace_var(f'JPLxx-W/Exx-ON_{indexFBD}', f'JPL{jpl_dir}-ON')
                        replace_var(f'JPLxx-W/Exx-START_{indexFBD}', f'JPL{jpl_dir}-START')
                        replace_var(f'JPLxx-W/Exx-ACK_{indexFBD}', f'JPL{jpl_dir}-ACK')
                        replace_var(f'JPLxx-W/Exx-ACCNV_{indexFBD}', f'JPL{jpl_dir}-ACCNV')

                        replace_var(f'JPLxx-PB-DI_{indexFBD}', f'JPL{jpl_name}-PB-DI')
                        replace_var(f'JPLxx-PB-ERR_{indexFBD}', f'JPL{jpl_name}-ERR')
                        replace_var(f'JPLxx-ACK-DI_{indexFBD}', f'JPL{jpl_name}-ACK-DI')

                        index_subroute = 1
                        if "OL" not in jpl_dir:
                            for it in IT1:
                                if it[-1] == jpl_arah and "(T)" in it[1] and f'{jpl_track}T' in it[20].split(" "):
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{jpl_track}-T-{data_var[0].split("-")[1][0]}S')
                                    index_subroute += 1
                                    break
                            for it in IT1:
                                if it[-1] == jpl_arah and ("(E)" in it[1] or "(CF)" in it[1]) and f'{jpl_track}T' in it[20].split(" "):
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{jpl_track}-E-{data_var[0].split("-")[1][0]}S')
                                    index_subroute += 1
                                    break
                            for it in IT1:
                                if it[-1] == jpl_arah and "(T)" in it[1] and f'{jpl_track}T' in it[20].split(" "):
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{jpl_track}-S-{data_var[0].split("-")[1][0]}S')
                                    index_subroute += 1
                                    break


                        else:
                            for it in IT2:
                                if it[-1] == jpl_arah and f'{jpl_track}T' in it[9].split(" ") and jpl_wesel in it[7]:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}', f'{simp_number(it[6])}-T-{data_var[0].split("-")[1][0]}LAS')
                                    index_subroute += 1

                        for it in IT1:
                            if it[-1] == jpl_arah and "(T)" in it[1] and f'{jpl_track}T' in it[20].split(" ") and jpl_wesel in it[18] and "-R" not in it[18]:
                                replace_var(f'xx-TP_{indexFBD}', f'{jpl_track}-TP')
                                replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'{it[2]}-F-RS')
                                replace_var(f'J/JL/Lxx-xx-P_{indexFBD}', f'{it[2]}-{simp(it[15])}-P')

                        if jpl_wesel:
                            for i, j in enumerate(jpl_wesel.split(" ")):
                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{i+1}', f'{j}WZ')

                        index_rs = 1
                        index_srs = 1
                        for it in IT1:
                            if it[-1] == jpl_arah and ("(E)" in it[1] or "(CF)" in it[1]) and f'{jpl_track}T' in it[20].split(" ") and jpl_wesel in it[18] and "OL" not in jpl_dir:
                                replace_var(f'J/JL-xx-RS_{indexFBD}-{index_rs}', f'{it[2]}-{simp(it[15])}-RS')
                                replace_var(f'J/JLxx-ER-DO_{indexFBD}-{index_rs}', f'{it[2]}-ER-DO')
                                index_rs += 1
                            if it[-1] == jpl_arah and "(S)" in it[1] and f'{jpl_track}T' in it[20].split(" ") and jpl_wesel in it[18] and "OL" not in jpl_dir:
                                replace_var(f'Lxx-xx-RS_{indexFBD}-{index_srs}', f'{it[2]}-{simp(it[15])}-RS')
                                index_srs += 1

                        index_start = 1
                        for i, j in enumerate(jpldata):
                            if j[0].split("-")[0] == jpl_name and j[0] != jpl_dir:
                                replace_var(f'JPLxx-E/Wxx-START_{indexFBD}-{index_start}', f'{j[0]}-START')
                                index_start += 1

                        for index in range(1, 50):
                            if "OL" in jpl_dir:
                                replace_var(f'J/JL-xx-RS_{indexFBD}-{index}', f'TRUE')
                                replace_var(f'Lxx-xx-RS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JLxx-ER-DO_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'JPLxx-E/Wxx-START_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')

                        replace_var(f'xx-TP_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'FALSE')
                        replace_var(f'JPLxx-W/Exx-ACCNV_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-xx-P_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        def nfc93_lx_pbe():
            alljpl = sorted(list(set([j[0].split("-")[0] for j in jpldata])))

            FBDtujuan = "nFC93 LX PBE"
            for index, jpl in enumerate(alljpl):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")
                index += 1

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                replace_var(f'JPLxx-PB-ERR_1', f'JPL{jpl}-PB-ERR')
                replace_var(f'JPLxx-PBE_1', f'JPL{jpl}-PBE')
                replace_var(f'JPLxx-PBE-F_1', f'JPL{jpl}-PBE-F')
                replace_var(f'JPLxx-PBE-DO_1', f'JPL{jpl}-PBE-DO')
                replace_var(f'JPLxx-PB-DI_1', f'JPL{jpl}-PB-DI')
                replace_var(f'JPLxx-AA-F', f'JPL{jpl}-AA-F')

                ind_jpl = sorted(list(set([j[0] for j in jpldata if j[0].split("-")[0] == jpl])))

                index_start = 1
                for direction in ind_jpl:
                    replace_var(f'JPLxx-E/Wxx-START_{index}-{index_start}', f'JPL{direction}-START')
                    replace_var(f'JPLxx-E/Wxx-L_{index}-{index_start}', f'JPL{direction}-L')
                    replace_var(f'JPLxx-E/Wxx-ACCNV_{index}-{index_start}', f'JPL{direction}-ACCNV')
                    index_start += 1

                for ind in range(1, 50):
                    replace_var(f'JPLxx-E/Wxx-START_{index}-{ind}', f'FALSE')
                    replace_var(f'JPLxx-E/Wxx-L_{index}-{ind}', f'FALSE')
                    replace_var(f'JPLxx-E/Wxx-ACCNV_{index}-{ind}', f'FALSE')

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {jpl}.csv", index=False)
            print(f'{FBDtujuan} -> Done..')

        directorySimpan = directorySimpan + "\\Non Vital\\nV FC16 LEVEL CROSSING"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Non Vital\\nV FC16 LEVEL CROSSING"

        nfc87_lx_nv()
        nfc93_lx_pbe()

    #-------------------------------------------------------- VITAL ---------------------------------------------------#
    ################################# v FC1 Global Var ###############################
    def v_fc1_global_variable(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # vSFC2 DI to ECR2
        def vsfc2_di_to_ecr2():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))

            varEnumerated = sorted(list(set([it[2] for it in IT1 if it[3] or it[4] or it[5]]))) + \
                            sorted(list(set([s[12] for s in IT1 if s[12] and (s[13] or s[14])]))) + \
                            sorted(list(set([s[15] for s in IT1 if s[15].startswith("A") and "(T)" in s[1]])))

            jumlahGenFBD = 20
            FBDtujuan = "vSFC2 DI to ECR2"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'{data_var}-ECR')
                        replace_var(f'J/JLxx-ECR-DI_{indexFBD}', f'{data_var}-ECR-DI')
                        if data_var in signalHR:
                            replace_var(f'J/JLxx-HR/DR-DI_{indexFBD}', f'{data_var}-HR-DI')
                            replace_var(f'J/JLxx-HR/DR-DO_{indexFBD}', f'{data_var}-HR-DO')
                        if data_var in signalDR:
                            replace_var(f'J/JLxx-HR/DR-DI_{indexFBD}', f'{data_var}-DR-DI')
                            replace_var(f'J/JLxx-HR/DR-DO_{indexFBD}', f'{data_var}-DR-DO')
                        if data_var in signalGR:
                            replace_var(f'JL/Lxx-GR-DO_{indexFBD}', f'{data_var}-GR-DO')

                        replace_var(f'J/JLxx-HR/DR-DI_{indexFBD}', f'FALSE')
                        replace_var(f'J/JLxx-HR/DR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'JL/Lxx-GR-DO_{indexFBD}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # vSFC2 AS SR
        def vsfc2_as_sr():
            varEnumerated = sorted(list(set([f"{it[2]}-{simp(it[15])}" for it in IT1 if "(E)" in it[1]])))
            jumlahGenFBD = 20
            FBDtujuan = "vSFC2 AS SR"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-xx-E/T/S-L_1-{indexFBD}', f'{data_var}-E-L')
                        replace_var(f'J/JL/Lxx-xx-RS_1-{indexFBD}', f'{data_var}-RS')
                        replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_1-{indexFBD}', f'{data_var}-E-AS-SR')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} (E) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            varEnumerated = sorted(list(set([f"{it[2]}-{simp(it[15])}-CF" for it in IT1 if "(CF)" in it[1]])))
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-xx-E/T/S-L_1-{indexFBD}', f'{data_var}-E-L')
                        replace_var(f'J/JL/Lxx-xx-RS_1-{indexFBD}', f'{data_var}-RS')
                        replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_1-{indexFBD}', f'{data_var}-E-AS-SR')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} (CF) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            varEnumerated = sorted(list(set([f"{it[2]}-{simp(it[15])}" for it in IT1 if "(S)" in it[1]])))
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-xx-E/T/S-L_1-{indexFBD}', f'{data_var}-S-L')
                        replace_var(f'J/JL/Lxx-xx-RS_1-{indexFBD}', f'{data_var}-RS')
                        replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_1-{indexFBD}', f'{data_var}-S-AS-SR')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} (S) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # SWRLS
        def SWRLS():
            varEnumerated = [w[0] for w in PM if w[0].startswith("W")]
            FBDtujuan = "SWRLS"
            dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

            def replace_var(varAwal, varBaru):
                dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

            for indexFBD in range(len(varEnumerated)):
                try:
                    data_var = varEnumerated[indexFBD]
                    indexFBD += 1

                    replace_var(f'Wxx-SWRLS_{indexFBD}', f'{data_var}-SWRLS')

                except Exception as e:
                    print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                    break
                finally:
                    pass

            for index in range(1, 61):
                replace_var(f'Wxx-SWRLS_{index}', f'FALSE')

            dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan}.csv", index=False)

        # RRLS
        def RRLS():
            varEnumerated = sorted(list(set([it[15] for it in IT1]))) + \
                            sorted(list(set([it[2] for it in IT1 if "(T)" not in it[1] and "(S)" not in it[1] and not it[15].startswith("A")])))

            FBDtujuan = "RRLS"
            dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

            def replace_var(varAwal, varBaru):
                dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

            for indexFBD in range(len(varEnumerated)):
                try:
                    data_var = varEnumerated[indexFBD]
                    indexFBD += 1

                    replace_var(f'J/JL/L/A/Xxx-RRLS_{indexFBD}', f'{data_var}-RRLS')

                except Exception as e:
                    print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                    break
                finally:
                    pass

            for index in range(1, 61):
                replace_var(f'J/JL/L/A/Xxx-RRLS_{index}', f'FALSE')

            dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan}.csv", index=False)

        # vSFC2 RLS12
        def vsfc2_rls12():
            all_track = []
            for it in IT1:
                track_tes = []
                if it[27]:
                    track_tes = it[20].split(" ")[:-1]
                else:
                    track_tes = it[20].split(" ")
                for track in track_tes:
                    if track.endswith("T"):
                        all_track.append(track[:-1])
                    else:
                        all_track.append(track)
            all_track = sorted(list(set(all_track)))
            varEnumerated = all_track
            jumlahGenFBD = 5
            FBDtujuan = "vSFC2 RLS12"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'xx-RLS_{indexFBD}', f'{data_var}-RLS')

                        all_sinyal_tujuan = []
                        for it in IT1:
                            if f'{data_var}T' in it[20].split(" ") and it[15] not in all_sinyal_tujuan:
                                all_sinyal_tujuan.append(it[15])

                        index_rrls_te = 1
                        for sinyal in all_sinyal_tujuan:
                            replace_var(f'J/JL/L/A/Xxx-RRLS-TE_{indexFBD}-{index_rrls_te}', f'{sinyal}-RRLS-TE')

                            list_wesel = []
                            list_track = []
                            for it in IT1:
                                if sinyal == it[15] and f'{data_var}T' in it[20].split(" "):
                                    list_wesel = it[18].split(" ")
                                    tr = []
                                    for t in it[20].split(" "):
                                        if t.endswith("T"):
                                            tr.append(t[:-1])
                                        else:
                                            tr.append(t)
                                    list_track = tr[tr.index(data_var):]
                                    break
                            for it in IT1:
                                if sinyal == it[15] and f'{data_var}T' in it[20].split(" "):
                                    wesel_dump = []
                                    for wesel in it[18].split(" "):
                                        if wesel in list_wesel:
                                            wesel_dump.append(wesel)
                                    list_wesel = wesel_dump[:]

                            index_wesel = 1
                            for wesel in list_wesel:
                                for w in PM:
                                    if wesel.replace("-N", "").replace("-R", "")  == w[0].replace("W", "")  and (w[1] in list_track or w[2] in list_track):
                                        replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_rrls_te}-{index_wesel}', f'W{wesel}WZ')
                                        index_wesel += 1

                            index_rrls_te += 1

                        for index_te in range(1, 13):
                            replace_var(f'J/JL/L/A/Xxx-RRLS-TE_{indexFBD}-{index_te}', f'FALSE')
                            for index_wesel in range(1, 6):
                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_te}-{index_wesel}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # XX TES ESWS RL
        def tes_es_ws_rl():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))

            # E-ES-RL
            varEnumerated = sorted(list(set([it[20].split(" ")[0] for it in IT1 if "EAST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1])])))
            jumlahGenFBD = 10
            FBDtujuan = "XX TES ESWS RL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track = data_var
                        if data_var.endswith("T"):
                            track = data_var[:-1]
                        replace_var(f'xx-E-ES/WS-RL_{indexFBD}', f'{track}-E-ES-RL')

                        s_as = sorted(list(set([it[2] for it in IT1 if "EAST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]) and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(s_as):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index+1}', f'{data}-E-AS')
                        xx_s = sorted(list(set([f'{it[2]}-{simp(it[15])}{"-CF" if "(CF)" in it[1] else ""}' for it in IT1 if "EAST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]) and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(xx_s):
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index+1}', f'{data}-E')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index+1}', f'{data}-E-AS-SR')

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} (XX-E-ES-RL) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            # E-WS-RL
            varEnumerated = sorted(list(set([it[20].split(" ")[0] for it in IT1 if "WEST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1])])))
            jumlahGenFBD = 10
            FBDtujuan = "XX TES ESWS RL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track = data_var
                        if data_var.endswith("T"):
                            track = data_var[:-1]
                        replace_var(f'xx-E-ES/WS-RL_{indexFBD}', f'{track}-E-WS-RL')

                        s_as = sorted(list(set([it[2] for it in IT1 if "WEST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]) and data_var ==  it[20].split(" ")[0]])))
                        for index, data in enumerate(s_as):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index + 1}', f'{data}-E-AS')
                        xx_s = sorted(list(set([f'{it[2]}-{simp(it[15])}{"-CF" if "(CF)" in it[1] else ""}' for it in IT1 if "WEST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]) and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(xx_s):
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-E')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index + 1}', f'{data}-E-AS-SR')

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\{FBDtujuan} (XX-E-WS-RL) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)

            # T-ES-RL
            varEnumerated = sorted(list(set([it[20].split(" ")[0] for it in IT1 if "EAST" in it[-1] and "(T)" in it[1]])))
            jumlahGenFBD = 10
            FBDtujuan = "XX TES ESWS RL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track = data_var
                        if data_var.endswith("T"):
                            track = data_var[:-1]
                        replace_var(f'xx-E-ES/WS-RL_{indexFBD}', f'{track}-T-ES-RL')

                        s_as = sorted(list(set([it[2] for it in IT1 if "EAST" in it[-1] and "(T)" in it[1] and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(s_as):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index + 1}', f'{data}-T-AS')
                        xx_s = sorted(list(set([f'{it[2]}-{simp(it[15])}' for it in IT1 if "EAST" in it[-1] and "(T)" in it[1] and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(xx_s):
                            if data.split("-")[0] in signalHR:
                                replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-H')
                            else:
                                replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-D')

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\{FBDtujuan} (XX-T-ES-RL) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)

            # T-WS-RL
            varEnumerated = sorted( list(set([it[20].split(" ")[0] for it in IT1 if "WEST" in it[-1] and "(T)" in it[1]])))
            print(varEnumerated)
            jumlahGenFBD = 10
            FBDtujuan = "XX TES ESWS RL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track = data_var
                        if data_var.endswith("T"):
                            track = data_var[:-1]
                        replace_var(f'xx-E-ES/WS-RL_{indexFBD}', f'{track}-T-WS-RL')

                        s_as = sorted(list(set([it[2] for it in IT1 if "WEST" in it[-1] and "(T)" in it[1] and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(s_as):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index + 1}', f'{data}-T-AS')
                        xx_s = sorted(list(set([f'{it[2]}-{simp(it[15])}' for it in IT1 if "WEST" in it[-1] and "(T)" in it[1] and data_var == it[20].split(" ")[0]])))
                        for index, data in enumerate(xx_s):
                            if data.split("-")[0] in signalHR:
                                replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-H')
                            else:
                                replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-D')

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\{FBDtujuan} (XX-T-WS-RL) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)

            # S-ES-RL
            varEnumerated = sorted(
                list(set([it[20].split(" ")[0] for it in IT1 if "EAST" in it[-1] and "(S)" in it[1]])))
            jumlahGenFBD = 10
            FBDtujuan = "XX TES ESWS RL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track = data_var
                        if data_var.endswith("T"):
                            track = data_var[:-1]
                        replace_var(f'xx-E-ES/WS-RL_{indexFBD}', f'{track}-S-ES-RL')

                        s_as = sorted(list(set([it[2] for it in IT1 if
                                                "EAST" in it[-1] and "(S)" in it[1] and data_var ==
                                                it[20].split(" ")[0]])))
                        for index, data in enumerate(s_as):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index + 1}', f'{data}-S-AS')
                        xx_s = sorted(list(set([f'{it[2]}-{simp(it[15])}' for it in IT1 if
                                                "EAST" in it[-1] and "(S)" in it[1] and data_var ==
                                                it[20].split(" ")[0]])))
                        for index, data in enumerate(xx_s):
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-S')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index + 1}', f'{data}-S-AS-SR')

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\{FBDtujuan} (XX-S-ES-RL) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)

            # S-WS-RL
            varEnumerated = sorted(
                list(set([it[20].split(" ")[0] for it in IT1 if "WEST" in it[-1] and "(S)" in it[1]])))
            jumlahGenFBD = 10
            FBDtujuan = "XX TES ESWS RL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track = data_var
                        if data_var.endswith("T"):
                            track = data_var[:-1]
                        replace_var(f'xx-E-ES/WS-RL_{indexFBD}', f'{track}-S-WS-RL')

                        s_as = sorted(list(set([it[2] for it in IT1 if
                                                "WEST" in it[-1] and "(S)" in it[1] and data_var ==
                                                it[20].split(" ")[0]])))
                        for index, data in enumerate(s_as):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index + 1}', f'{data}-S-AS')
                        xx_s = sorted(list(set([f'{it[2]}-{simp(it[15])}' for it in IT1 if
                                                "WEST" in it[-1] and "(S)" in it[1] and data_var ==
                                                it[20].split(" ")[0]])))
                        for index, data in enumerate(xx_s):
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index + 1}', f'{data}-S')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index + 1}', f'{data}-S-AS-SR')

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E/T/S-AS-SR_{indexFBD}-{index}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(
                    directorySimpan + f"\\{FBDtujuan} (XX-S-WS-RL) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                    index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC1 Global Var"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC1 Global Var"

        vsfc2_di_to_ecr2()
        vsfc2_as_sr()
        RRLS()
        SWRLS()
        vsfc2_rls12()
        tes_es_ws_rl()

    ############################## v FC3 ROUTE CONFLICT LOCK ############################
    def v_fc3_route_conflict_lock(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # nV FC2 IL ROUTE - v FC70 E-L CONFLICT OUT
        def v_FC70_ELCONFLICTOUT():
            all_empl_langsir = sorted(list(set([it[20].replace("T", "").split(" ")[-1] for it in IT1 if "(S)" in it[1] and it[27]])))
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))

            varEnumerated = [it for it in IT1 if ("(E)" in it[1] or "(CF)" in it[1]) and not it[15].startswith("A")]
            jumlahGenFBD = 5
            FBDtujuan = "vFC 70 E-L CONFLICT OUT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        os_track = data_var[20].replace("T", "").split(" ")[0]
                        emplacement_track = data_var[20].replace("T", "").split(" ")[-1]
                        arah_rute = data_var[-1]
                        track_rute = data_var[20].replace("T", "").split(" ")[:-1]
                        track_rute_all = data_var[20].replace("T", "").split(" ")
                        wesel_rute = data_var[18].split(" ")
                        deraileur_rute = []
                        if data_var[19]:
                            deraileur_rute = data_var[19].split(" ")

                        cf = ""
                        if "(CF)" in data_var[1]:
                            cf = "-CF"

                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}{cf}-E-L')

                        ################################### conflict subroute rute #####################################
                        index_esws = 1

                        t_stop = False
                        e_stop = False
                        s_stop = False
                        for it in IT1:
                            if it[27]:
                                track_cek = it[20].replace("T", "").split(" ")[:-1]
                            else:
                                track_cek = it[20].replace("T", "").split(" ")

                            if os_track in track_cek and arah_rute != it[-1]:
                                if arah_rute == "EAST":
                                    arah_conflict = "W"
                                else:
                                    arah_conflict = "E"

                                if "(T)" in it[1] and not t_stop:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-T-{arah_conflict}S')
                                    t_stop = True
                                    index_esws += 1
                                if ("(E)" in it[1] or "(CF)" in it[1]) and not e_stop:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-E-{arah_conflict}S')
                                    e_stop = True
                                    index_esws += 1
                                if "(S)" in it[1] and not s_stop:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-S-{arah_conflict}S')
                                    s_stop = True
                                    index_esws += 1

                        trackbemplist = []
                        for track in track_rute_all:
                            if track in all_empl_langsir:
                                for it in IT1:
                                    if track == it[20].replace("T", "").split(" ")[-1] and "(S)" in it[1] and \
                                            it[20].replace("T", "").split(" ")[-2] in track_rute_all:
                                        track_before_empl = it[20].replace("T", "").split(" ")[-2]

                                        if it[-1] == "EAST":
                                            arah_conflict = "E"
                                        else:
                                            arah_conflict = "W"

                                        if f'{track_before_empl}-S-{arah_conflict}S' not in trackbemplist:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{track_before_empl}-S-{arah_conflict}S')
                                            trackbemplist.append(f'{track_before_empl}-S-{arah_conflict}S')
                                            index_esws += 1
                        ######################################### syarat wesel #########################################
                        index_wesel = 1
                        for w in wesel_rute:
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index_wesel}', f'W{w[:w.find("-")]}-{w[-1]}WC')
                            index_wesel += 1

                        ##################################### conflict ELASWLAS  #######################################
                        if arah_rute == "EAST" and not sinyal_tujuan.startswith("A"):
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data[20].replace("T", "").split(" ")[-1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-T-ELAS/WLAS_{indexFBD}', f'{emplacement_track}-T-WLAS')
                                    break
                        if arah_rute == "WEST" and not sinyal_tujuan.startswith("A"):
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data[20].replace("T", "").split(" ")[-1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-T-ELAS/WLAS_{indexFBD}', f'{emplacement_track}-T-ELAS')
                                    break

                        #################################### conflict opposing signal ##################################
                        index_signal_conflict = 1
                        for signal in data_var[22].split(" "):
                            if signal in signalHR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}', f'{signal}-HR-DO')
                                index_signal_conflict += 1
                            if signal in signalDR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}', f'{signal}-DR-DO')
                                index_signal_conflict += 1
                            if signal in signalER:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}', f'{signal}-ER-DO')
                                index_signal_conflict += 1
                            if signal in signalGR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}', f'{signal}-GR-DO')
                                index_signal_conflict += 1

                        ######################### conflict deraileur dan ECR sinyal asal ###############################
                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'{data_var[2]}-ECR')
                        if sinyal_asal in signalHR and "-R" not in data_var[18]:
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{data_var[2]}-EC-G-RD')

                        if deraileur_rute != []:
                            index_deraileur = 1
                            for d in deraileur_rute:
                                replace_var(f'Dxx-B-N/R_{indexFBD}-{index_deraileur}',f'{d[:-2]}-B-{d[-1]}')
                                index_deraileur += 1

                        ############################### conflict subroute emplacement ##################################
                        track_conflict_empl = ""
                        if not sinyal_tujuan.startswith("A"):
                            for it_data in IT1:
                                if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                                        arah_rute == "WEST" and it_data[-1] == "EAST"):
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        track_conflict_empl = it_data[20].replace("T", "").split(" ")[-2]
                                        break
                            index_esws = 1
                            for it_data in IT1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index_esws}', f'{track_conflict_empl}-T-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index_esws}', f'{track_conflict_empl}-T-ES')
                                            index_esws += 1
                                            break
                            for it_data in IT1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index_esws}', f'{track_conflict_empl}-E-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index_esws}', f'{track_conflict_empl}-E-ES')
                                            index_esws += 1
                                            break
                            for it_data in IT1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index_esws}', f'{track_conflict_empl}-S-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index_esws}', f'{track_conflict_empl}-S-ES')
                                            index_esws += 1
                                            break

                        # Generate WP back
                        # 1.cari wesel yang berada dalam 1 track
                        wesel_on_track = [w[0].replace("W", "") for w in PM if (track_conflict_empl == w[1] or track_conflict_empl == w[2]) and track_conflict_empl]
                        # cari posisi wesel tersebut di interlocking table jika berada sama2 dengan indikasi wesel yang di generate
                        all_wesel_pos = []
                        for wt in wesel_on_track:
                            for it in IT1:
                                if wt in it[18] and emplacement_track == \
                                        it[20].replace("T", "").split(" ")[-1]:
                                    for w_tes in it[18].split(" "):
                                        if wt == w_tes.replace("-R", "").replace("-N", ""):
                                            all_wesel_pos.append(w_tes)
                        all_wesel_pos = sorted(list(set(all_wesel_pos)))
                        # masukan posisi wesel jika saat bersamaan dengan wesel indikasi, wesel tersebut hanya mengarah ke 1 arah saja
                        index_wp_back = 1
                        for w in wesel_on_track:
                            if not (w + "-R" in all_wesel_pos and w + "-N" in all_wesel_pos):
                                if w + "-R" in all_wesel_pos:
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wp_back}', f'W{w}-NWZ')
                                    index_wp_back += 1
                                if w + "-N" in all_wesel_pos:
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wp_back}', f'W{w}-RWZ')
                                    index_wp_back += 1

                        ############################## normalisasi template tidak terpakai #############################
                        for index in range(1, 50):
                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-E/T/S-ES/WS-EMPLACEMENT_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Dxx-B-N/R_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index}', f'FALSE')
                        for index in range(1, 50):
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index}', f'TRUE')

                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')
                        replace_var(f'xx-T-ELAS/WLAS_{indexFBD}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nV FC2 IL ROUTE - v FC71 ELCONFLICT IN
        def v_FC71_ELCONFLICTIN():
            all_empl_langsir = sorted(list(set([it[20].replace("T", "").split(" ")[-1] for it in IT1 if "(S)" in it[1] and it[27]])))
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))

            varEnumerated = [it for it in IT1 if ("(E)" in it[1] or "(CF)" in it[1]) and it[15].startswith("A")]
            jumlahGenFBD = 5
            FBDtujuan = "vFC 71 E-L CONFLICT IN"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        os_track = data_var[20].replace("T", "").split(" ")[0]
                        emplacement_track = data_var[20].replace("T", "").split(" ")[-1]
                        arah_rute = data_var[-1]
                        track_rute = data_var[20].replace("T", "").split(" ")[:-1]
                        track_rute_all = data_var[20].replace("T", "").split(" ")
                        wesel_rute = data_var[18].split(" ")
                        deraileur_rute = []
                        if data_var[19]:
                            deraileur_rute = data_var[19].split(" ")

                        cf = ""
                        if "(CF)" in data_var[1]:
                            cf = "-CF"

                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}{cf}-E-L')

                        if arah_rute == "EAST":
                            replace_var(f'Axx-E/WS_{indexFBD}', f'{data_var[15]}-WS')
                        else:
                            replace_var(f'Axx-E/WS_{indexFBD}', f'{data_var[15]}-ES')
                        ################################### conflict subroute rute #####################################
                        index_esws = 1

                        t_stop = False
                        e_stop = False
                        s_stop = False
                        for it in IT1:
                            if it[27]:
                                track_cek = it[20].replace("T", "").split(" ")[:-1]
                            else:
                                track_cek = it[20].replace("T", "").split(" ")

                            if os_track in track_cek and arah_rute != it[-1]:
                                if arah_rute == "EAST":
                                    arah_conflict = "W"
                                else:
                                    arah_conflict = "E"

                                if "(T)" in it[1] and not t_stop:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-T-{arah_conflict}S')
                                    t_stop = True
                                    index_esws += 1
                                if ("(E)" in it[1] or "(CF)" in it[1]) and not e_stop:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-E-{arah_conflict}S')
                                    e_stop = True
                                    index_esws += 1
                                if "(S)" in it[1] and not s_stop:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-S-{arah_conflict}S')
                                    s_stop = True
                                    index_esws += 1

                        trackbemplist = []
                        for track in track_rute_all:
                            if track in all_empl_langsir:
                                for it in IT1:
                                    if track == it[20].replace("T", "").split(" ")[-1] and "(S)" in it[1] and \
                                            it[20].replace("T", "").split(" ")[-2] in track_rute_all:
                                        track_before_empl = it[20].replace("T", "").split(" ")[-2]

                                        if it[-1] == "EAST":
                                            arah_conflict = "E"
                                        else:
                                            arah_conflict = "W"

                                        if f'{track_before_empl}-S-{arah_conflict}S' not in trackbemplist:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{track_before_empl}-S-{arah_conflict}S')
                                            trackbemplist.append(f'{track_before_empl}-S-{arah_conflict}S')
                                            index_esws += 1

                        ######################################### syarat wesel #########################################
                        index_wesel = 1
                        for w in wesel_rute:
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index_wesel}', f'W{w[:w.find("-")]}-{w[-1]}WC')
                            index_wesel += 1

                        #################################### conflict opposing signal ##################################
                        index_signal_conflict = 1
                        for signal in data_var[22].split(" "):
                            if signal in signalHR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-HR-DO')
                                index_signal_conflict += 1
                            if signal in signalDR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-DR-DO')
                                index_signal_conflict += 1
                            if signal in signalER:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-ER-DO')
                                index_signal_conflict += 1
                            if signal in signalGR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-GR-DO')
                                index_signal_conflict += 1

                        ######################### conflict deraileur dan ECR sinyal asal ###############################
                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'{data_var[2]}-ECR')
                        if (sinyal_asal in signalDR and "-R" not in data_var[18]) or sinyal_asal in signalHR:
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{sinyal_asal}-EC-G-RD')

                        if deraileur_rute != []:
                            index_deraileur = 1
                            for d in deraileur_rute:
                                replace_var(f'Dxx-B-N/R_{indexFBD}-{index_deraileur}', f'{d[:-2]}-B-{d[-1]}')
                                index_deraileur += 1

                        ############################### conflict subroute emplacement ##################################
                        track_conflict_empl = ""
                        if not sinyal_tujuan.startswith("A"):
                            for it_data in IT1:
                                if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                                        arah_rute == "WEST" and it_data[-1] == "EAST"):
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        track_conflict_empl = it_data[20].replace("T", "").split(" ")[-2]
                                        break
                            index_esws = 1
                            for it_data in IT1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-T-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(T)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-T-ES')
                                            index_esws += 1
                                            break
                            for it_data in IT1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-E-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-E-ES')
                                            index_esws += 1
                                            break
                            for it_data in IT1:
                                if arah_rute == "EAST" and it_data[-1] == "WEST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-S-WS')
                                            index_esws += 1
                                            break
                                if arah_rute == "WEST" and it_data[-1] == "EAST":
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if "(S)" in it_data[1]:
                                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                                                        f'{track_conflict_empl}-S-ES')
                                            index_esws += 1
                                            break

                        # filter wesel conflict emplacement dari yang tidak perlu di syaratakan
                        wesel_conf_empl = [w[0].replace("W", "") for w in PM if track_conflict_empl and (
                                track_conflict_empl == w[1] or track_conflict_empl == w[2])]
                        wesel_delete = []

                        if not sinyal_tujuan.startswith("A"):
                            for w in wesel_conf_empl:
                                cekR = False
                                cekN = False
                                for it_data in IT1:
                                    wesel_it = it_data[18].replace("N", "").replace("R", "").split(" ")
                                    wesel_it_full = it_data[18].split(" ")
                                    if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                                            arah_rute == "WEST" and it_data[-1] == "EAST") and w in wesel_it:
                                        if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                            if f"{w}-R" in wesel_it_full:
                                                cekR = True
                                            if f"{w}-N" in wesel_it_full:
                                                cekN = True
                                if cekR and cekN:
                                    wesel_delete.append(w)
                        for w in wesel_delete:
                            wesel_conf_empl.remove(w)

                        index_wesel_conf = 1
                        for w in wesel_conf_empl:
                            for it_data in IT1:
                                wesel_it = it_data[18].replace("N", "").replace("R", "").split(" ")
                                wesel_it_full = it_data[18].split(" ")
                                if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                                        arah_rute == "WEST" and it_data[-1] == "EAST") and w in wesel_it:
                                    if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                                        if f"{w}-R" in wesel_it_full:
                                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wesel_conf}', f'W{w}-NWZ')
                                            index_wesel_conf += 1
                                            break
                                        if f"{w}-N" in wesel_it_full:
                                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wesel_conf}', f'W{w}-RWZ')
                                            index_wesel_conf += 1
                                            break

                        ############################## normalisasi template tidak terpakai #############################
                        for index in range(1, 50):
                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Dxx-B-N/R_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index}', f'FALSE')
                        for index in range(1, 50):
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index}', f'TRUE')
                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nV FC2 ROUTE - v FC72 T-L CONFLICT IN
        def v_FC72_TLCONFLICTIN():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))

            varEnumerated = [it for it in IT2 if not it[6].startswith("A")]
            jumlahGenFBD = 5
            FBDtujuan = "vFC 72 T-L CONFLICT IN"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[6]
                        wesel_rute = data_var[7].split(" ")

                        track_rute = []
                        for t in IT1:
                            if data_var[1] == t[1]:
                                track_rute = t[20].replace("T", "").split(" ")
                                if sinyal_tujuan in signalDR and "-R" not in t[18]:
                                    replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{sinyal_tujuan}-EC-G-RD')
                                break
                        track_overlap = data_var[9].replace("T", "").split(" ")

                        flank_rute = []
                        if data_var[4]:
                            flank_rute = data_var[4].split(" ")

                        flank_overlap = []
                        if data_var[12]:
                            flank_overlap= data_var[12].split(" ")

                        deraileur_rute = []
                        if data_var[8]: deraileur_rute = data_var[8].split(" ")

                        replace_var(f'J/JL/Lxx-xx-T-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}-T-L')
                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}-E-L')
                        replace_var(f'J/JL/Lxx-xx-E-REQ_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}-E-REQ')

                        ######################### conflict deraileur dan ECR sinyal asal ###############################
                        index_ecr = 1

                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'{sinyal_tujuan}-ECR')

                        for f in flank_rute:
                            replace_var(f'J/JLxx-ECR_{indexFBD}-{index_ecr}', f'{f}-ECR')
                            index_ecr += 1

                        for f in flank_overlap:
                            replace_var(f'J/JLxx-ECR_{indexFBD}-{index_ecr}', f'{f}-ECR')
                            index_ecr += 1

                        for d in deraileur_rute:
                                replace_var(f'Dxx-B-N/R_{indexFBD}-{index_ecr}',f'{d}-ECR')
                                index_ecr += 1

                        ################################### Track Luncuran #############################################
                        index_track = 1
                        for t in track_rute:
                            replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{t}-TP')
                            index_track += 1
                        for t in track_overlap:
                            replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{t}-TP')
                            index_track += 1

                        ######################################### syarat wesel #########################################
                        index_wesel = 1
                        for w in wesel_rute:
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index_wesel}', f'W{w[:w.find("-")]}-{w[-1]}WC')
                            index_wesel += 1

                        #################################### conflict opposing signal ##################################
                        index_signal_conflict = 1
                        for signal in data_var[10].split(" "):
                            if signal in signalHR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-HR-DO')
                                index_signal_conflict += 1
                            if signal in signalDR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-DR-DO')
                                index_signal_conflict += 1
                            if signal in signalER:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-ER-DO')
                                index_signal_conflict += 1
                            if signal in signalGR:
                                replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index_signal_conflict}',
                                            f'{signal}-GR-DO')
                                index_signal_conflict += 1

                        ############################## normalisasi template tidak terpakai #############################
                        for index in range(1, 50):
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index}', f'FALSE')
                        for index in range(1, 50):
                            replace_var(f'J/JLxx-ECR_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')

                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nV FC2 ROUTE - v FC73 T-L CONFLICT OUT
        def v_FC73_TLCONFLICTOUT():

            varEnumerated = [it for it in IT2 if it[6].startswith("A")]
            jumlahGenFBD = 5
            FBDtujuan = "vFC 73 T-L CONFLICT OUT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[6]
                        wesel_rute = data_var[7].split(" ")

                        track_rute = []
                        for t in IT1:
                            if data_var[1] == t[1]:
                                track_rute = t[20].replace("T", "").split(" ")
                                if "IB" not in t[16]:
                                    replace_var(f'Axx-ECR_{indexFBD}', f'{sinyal_tujuan}-ECR')
                                else:
                                    replace_var(f'J/JLxx-ECR_{indexFBD}', f'{t[16]}-ECR')
                                    replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{t[16]}-EC-G-RD')
                                break

                        arah_rute = data_var[-1]

                        flank_rute = []
                        if data_var[4]:
                            flank_rute = data_var[4].split(" ")

                        flank_overlap = []
                        if data_var[12]:
                            flank_overlap = data_var[12].split(" ")

                        deraileur_rute = []
                        if data_var[8]: deraileur_rute = data_var[8].split(" ")

                        replace_var(f'J/JL/Lxx-xx-T-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}-T-L')
                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}-E-L')
                        replace_var(f'J/JL/Lxx-xx-E-REQ_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}-E-REQ')



                        replace_var(f'Axx-W/ETP_{indexFBD}', f'{sinyal_tujuan}-{"E" if arah_rute == "EAST" else "W"}TP')

                        ######################### conflict deraileur dan ECR sinyal asal ###############################
                        index_ecr = 1
                        for f in flank_rute:
                            replace_var(f'J/JLxx-ECR_{indexFBD}-{index_ecr}', f'{f}-ECR')
                            index_ecr += 1

                        for f in flank_overlap:
                            replace_var(f'J/JLxx-ECR_{indexFBD}-{index_ecr}', f'{f}-ECR')
                            index_ecr += 1

                        ################################### Track Luncuran #############################################
                        index_track = 1
                        for t in track_rute:
                            replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{t}-TP')
                            index_track += 1

                        ############################## normalisasi template tidak terpakai #############################
                        for index in range(1, 50):
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JL/Lxx-ER/HR/DR/GR-DO_{indexFBD}-{index}', f'FALSE')
                        for index in range(1, 50):
                            replace_var(f'J/JLxx-ECR_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')

                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'TRUE')
                        replace_var(f'Axx-ECR_{indexFBD}', f'TRUE')
                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nV FC2 ROUTE - v FC74 S-L CONFLICT
        def v_FC74_SLCONFLICT():
            varEnumerated = [it for it in IT1 if "(S)" in it[1]]
            jumlahGenFBD = 5
            FBDtujuan = "vFC 74 S-L CONFLICT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        os_track = data_var[20].replace("T", "").split(" ")[0]
                        emplacement_track = data_var[20].replace("T", "").split(" ")[-1]
                        arah_rute = data_var[-1]
                        track_rute = data_var[20].replace("T", "").split(" ")[:-1]
                        track_rute_all = data_var[20].replace("T", "").split(" ")
                        wesel_rute = data_var[18].split(" ")

                        if len(track_rute_all) == 1:
                            trackujung = track_rute_all
                        elif data_var[27]:
                            trackujung = track_rute_all[-2]
                        else:
                            trackujung = track_rute_all[-1]

                        cf = ""

                        replace_var(f'J/JL/Lxx-xx-S-L_{indexFBD}', f'{sinyal_asal}-{simp(sinyal_tujuan)}{cf}-S-L')

                        # conflict WS
                        index_esws = 1
                        if arah_rute == "EAST":
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-T-WS')
                                        index_esws += 1
                                        break
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data != data_var and ("(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-E-WS')
                                        index_esws += 1
                                        break
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data != data_var and "(S)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-S-WS')
                                        index_esws += 1
                                        break
                        if arah_rute == "WEST":
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{trackujung}-T-WS')
                                        index_esws += 1
                                        break
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data != data_var and (
                                        "(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{trackujung}-E-WS')
                                        index_esws += 1
                                        break

                        # conflict ES
                        if arah_rute == "WEST":
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-T-ES')
                                        index_esws += 1
                                        break
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data != data_var and (
                                        "(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-E-ES')
                                        index_esws += 1
                                        break
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data != data_var and "(S)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if os_track in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{os_track}-S-ES')
                                        index_esws += 1
                                        break
                        if arah_rute == "EAST":
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data != data_var and "(T)" in it_data[1]:
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{trackujung}-T-ES')
                                        index_esws += 1
                                        break
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data != data_var and ("(E)" in it_data[1] or "(CF)" in it_data[1]):
                                    it_data_track = it_data[20].replace("T", "").split(" ")
                                    if trackujung in it_data_track:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{trackujung}-E-ES')
                                        index_esws += 1
                                        break

                        # conflict ELAS WLAS
                        if arah_rute == "EAST":
                            for it_data in IT1:
                                if it_data[-1] == "WEST" and it_data[20].replace("T", "").split(" ")[-1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{emplacement_track}-T-WLAS')
                                    index_esws += 1
                                    break
                        if arah_rute == "WEST":
                            for it_data in IT1:
                                if it_data[-1] == "EAST" and it_data[20].replace("T", "").split(" ")[-1] == emplacement_track and "(T)" in it_data[1]:
                                    replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}', f'{emplacement_track}-T-ELAS')
                                    index_esws += 1
                                    break

                        replace_var(f'J/JL/Lxx-RRLS_{indexFBD}', f'{data_var[15]}-RRLS')

                        index_wesel = 1
                        for w in wesel_rute:
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index_wesel}', f'W{w[:w.find("-")]}-{w[-1]}WC')
                            index_wesel += 1

                        # track_conflict_empl = ""
                        # if not sinyal_tujuan.startswith("A"):
                        #     for it_data in IT1:
                        #         if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                        #                 arah_rute == "WEST" and it_data[-1] == "EAST"):
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 track_conflict_empl = it_data[20].replace("T", "").split(" ")[-2]
                        #                 break
                        #     index_esws = 1
                        #     for it_data in IT1:
                        #         if arah_rute == "EAST" and it_data[-1] == "WEST":
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if "(T)" in it_data[1]:
                        #                     replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                        #                                 f'{track_conflict_empl}-T-WS')
                        #                     index_esws += 1
                        #                     break
                        #         if arah_rute == "WEST" and it_data[-1] == "EAST":
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if "(T)" in it_data[1]:
                        #                     replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                        #                                 f'{track_conflict_empl}-T-ES')
                        #                     index_esws += 1
                        #                     break
                        #     for it_data in IT1:
                        #         if arah_rute == "EAST" and it_data[-1] == "WEST":
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                        #                     replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                        #                                 f'{track_conflict_empl}-E-WS')
                        #                     index_esws += 1
                        #                     break
                        #         if arah_rute == "WEST" and it_data[-1] == "EAST":
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if "(E)" in it_data[1] or "(CF)" in it_data[1]:
                        #                     replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                        #                                 f'{track_conflict_empl}-E-ES')
                        #                     index_esws += 1
                        #                     break
                        #     for it_data in IT1:
                        #         if arah_rute == "EAST" and it_data[-1] == "WEST":
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if "(S)" in it_data[1]:
                        #                     replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                        #                                 f'{track_conflict_empl}-S-WS')
                        #                     index_esws += 1
                        #                     break
                        #         if arah_rute == "WEST" and it_data[-1] == "EAST":
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if "(S)" in it_data[1]:
                        #                     replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_esws}',
                        #                                 f'{track_conflict_empl}-S-ES')
                        #                     index_esws += 1
                        #                     break

                        # filter wesel conflict emplacement dari yang tidak perlu di syaratakan

                        # wesel_conf_empl = [w[0].replace("W", "") for w in PM if track_conflict_empl and (
                        #         track_conflict_empl == w[1] or track_conflict_empl == w[2])]
                        # wesel_delete = []
                        # if not sinyal_tujuan.startswith("A"):
                        #     for w in wesel_conf_empl:
                        #         cekR = False
                        #         cekN = False
                        #         for it_data in IT1:
                        #             wesel_it = it_data[18].replace("N", "").replace("R", "").split(" ")
                        #             wesel_it_full = it_data[18].split(" ")
                        #             if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                        #                     arah_rute == "WEST" and it_data[-1] == "EAST") and w in wesel_it:
                        #                 if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                     if f"{w}-R" in wesel_it_full:
                        #                         cekR = True
                        #                     if f"{w}-N" in wesel_it_full:
                        #                         cekN = True
                        #         if cekR and cekN:
                        #             wesel_delete.append(w)
                        # for w in wesel_delete:
                        #     wesel_conf_empl.remove(w)
                        #
                        # index_wesel_conf = 1
                        # for w in wesel_conf_empl:
                        #     for it_data in IT1:
                        #         wesel_it = it_data[18].replace("N", "").replace("R", "").split(" ")
                        #         wesel_it_full = it_data[18].split(" ")
                        #         if (arah_rute == "EAST" and it_data[-1] == "WEST") or (
                        #                 arah_rute == "WEST" and it_data[-1] == "EAST") and w in wesel_it:
                        #             if it_data[20].replace("T", "").split(" ")[-1] == emplacement_track:
                        #                 if f"{w}-R" in wesel_it_full:
                        #                     replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wesel_conf}',
                        #                                 f'W{w}-NWZ')
                        #                     index_wesel_conf += 1
                        #                     break
                        #                 if f"{w}-N" in wesel_it_full:
                        #                     replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wesel_conf}',
                        #                                 f'W{w}-RWZ')
                        #                     index_wesel_conf += 1
                        #                     break

                        # if deraileur_rute != []:
                        #     index_deraileur = 1
                        #     for d in deraileur_rute:
                        #         replace_var(f'Dxx-B-N/R_{indexFBD}-{index_deraileur}', f'{d[:-2]}-B-{d[-1]}')
                        #         index_deraileur += 1

                        replace_var(f'xx-TP_{indexFBD}', f'{os_track}-TP')

                        for index in range(1, 50):
                            replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Dxx-B-N/R_{indexFBD}-{index}', f'TRUE')
                        for index in range(1, 50):
                            replace_var(f'Wxx-N/RWC_{indexFBD}-{index}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\V FC3 ROUTE CONFLICT LOCK"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\V FC3 ROUTE CONFLICT LOCK"

        v_FC70_ELCONFLICTOUT()
        v_FC71_ELCONFLICTIN()
        v_FC72_TLCONFLICTIN()
        v_FC73_TLCONFLICTOUT()
        v_FC74_SLCONFLICT()

    ################################# v FC4 Track Timer ###############################
    def v_fc4_track_timer(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # vFC 50 TRACK TIMER
        def vfc_50_track_timer():
            track = []
            for it in IT1:
                list_track = it[20].split(" ")
                for data in list_track:
                    if data:
                        if data.endswith("T"):
                            track.append(data[:-1])
                        else:
                            track.append(data)
            for it in IT2:
                list_track = it[9].split(" ")
                for data in list_track:
                    if data:
                        if data.endswith("T"):
                            track.append(data[:-1])
                        else:
                            track.append(data)

            varEnumerated = sorted(list(set(track)))
            jumlahGenFBD = 20
            FBDtujuan = "vFC 50 TRACK TIMER"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'xx-TPR-DI_1-{indexFBD}', f'{data_var}-TPR-DI')
                        replace_var(f'xx-TP_1-{indexFBD}', f'{data_var}-TP')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC4 Track Timer"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC4 Track Timer"

        vfc_50_track_timer()

    ################################# v FC5 Point Control ###############################
    def v_fc5_point_control(self, IT1, IT2, referensiCSV, directorySimpan, pm):
        # vFC 51 POINT CTRL
        def vFC_51_POINT_CTRL():
            varEnumerated = sorted([w for w in pm if w[0].startswith("W")])

            jumlahGenFBD = 10
            FBDtujuan = "vFC 51 POINT CTRL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        wesel = data_var[0]
                        twesel1 = data_var[1]
                        twesel2 = data_var[2]
                        replace_var(f'xx-TP_{indexFBD}-1', f'{twesel1}-TP')
                        if twesel2:
                            replace_var(f'xx-TP_{indexFBD}-2', f'{twesel2}-TP')

                        replace_var(f'Wxx-NWP-DI_{indexFBD}', f'{wesel}-NWP-DI')
                        replace_var(f'Wxx-RWP-DI_{indexFBD}', f'{wesel}-RWP-DI')
                        replace_var(f'Wxx-N-REQ_{indexFBD}', f'{wesel}-N-REQ')
                        replace_var(f'Wxx-R-REQ_{indexFBD}', f'{wesel}-R-REQ')
                        replace_var(f'Wxx-OOC_{indexFBD}', f'{wesel}-OOC')
                        replace_var(f'Wxx-L_{indexFBD}', f'{wesel}-L')

                        replace_var(f'Wxx-NWP_{indexFBD}', f'{wesel}-NWP')
                        replace_var(f'Wxx-RWP_{indexFBD}', f'{wesel}-RWP')
                        replace_var(f'Wxx-NWR-DO_{indexFBD}', f'{wesel}-NWR-DO')
                        replace_var(f'Wxx-RWR-DO_{indexFBD}', f'{wesel}-RWR-DO')
                        replace_var(f'Wxx-WLPR-DO_{indexFBD}', f'{wesel}-WLPR-DO')
                        replace_var(f'Wxx-NWZ_{indexFBD}', f'{wesel}-NWZ')
                        replace_var(f'Wxx-RWZ_{indexFBD}', f'{wesel}-RWZ')
                        replace_var(f'Wxx-NWC_{indexFBD}', f'{wesel}-NWC')
                        replace_var(f'Wxx-RWC_{indexFBD}', f'{wesel}-RWC')
                        replace_var(f'Wxx-NW-TE_{indexFBD}', f'{wesel}-NW-TE')
                        replace_var(f'Wxx-RW-TE_{indexFBD}', f'{wesel}-RW-TE')
                        replace_var(f'Wxx-NWZ-CALL_{indexFBD}', f'{wesel}-NWZ-CALL')
                        replace_var(f'Wxx-RWZ-CALL_{indexFBD}', f'{wesel}-RWZ-CALL')
                        replace_var(f'Wxx-LS_{indexFBD}', f'{wesel}-LS')
                        replace_var(f'Wxx-OOC-CALL_{indexFBD}', f'{wesel}-OOC-CALL')

                        index_tpz = 1
                        for wesel in pm:
                            if twesel1 == wesel[1] or twesel1 == wesel[2] or (
                                    twesel2 and (twesel2 == wesel[1] or twesel2 == wesel[2])):
                                replace_var(f'Wxx-TPZ_{indexFBD}-{index_tpz}', f'{wesel[0]}-TPZ')
                                index_tpz += 1

                        for index in range(1, 11):
                            replace_var(f'Wxx-TPZ_{indexFBD}-{index}', f'FALSE')

                        replace_var(f'xx-TP_{indexFBD}-2', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC5 Point Control"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC5 Point Control"

        vFC_51_POINT_CTRL()

    ############################# v FC6 Lock From This Station ###########################
    def v_fc6_lock_from_this_station(self, IT1, IT2, referensiCSV, directorySimpan):
        # vFC 53 SIL TO SIL
        def vfc_53_sil_to_sil():
            varEnumerated = sorted(list(set([it[15] for it in IT1 if it[15].startswith("A")])))

            jumlahGenFBD = 5
            FBDtujuan = "vFC 53 SIL TO SIL"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1
                        arah = ""
                        cf = ""
                        for it in IT1:
                            if it[15] == data_var and "(CF)" in it[1]:
                                cf = "-CF"
                                break
                        for it in IT1:
                            if it[15] == data_var and "EAST" in it[-1]:
                                arah = "E"
                                break
                            elif it[15] == data_var and "WEST" in it[-1]:
                                arah = "W"
                                break

                        replace_var(f'Axx-TBMS_{indexFBD}', f'{data_var}{cf}-TBMS')

                        index_req = 1
                        for it in IT1:
                            if it[15] == data_var and "(T)" in it[1]:
                                replace_var(f'J/JLxx-xx-T/E-REQ_{indexFBD}-{index_req}', f'{it[2]}-{simp(it[15])}-T-REQ')
                                replace_var(f'xx-T-ES/WS_{indexFBD}', f'{it[20].replace("T", "").split(" ")[-1]}-T-{arah}S')
                                index_req += 1
                            if it[15] == data_var and "(E)" in it[1]:
                                replace_var(f'J/JLxx-xx-T/E-REQ_{indexFBD}-{index_req}', f'{it[2]}-{simp(it[15])}-E-REQ')
                                replace_var(f'xx-E-ES/WS_{indexFBD}', f'{it[20].replace("T", "").split(" ")[-1]}-E-{arah}S')
                                index_req += 1
                            if it[15] == data_var and "(CF)" in it[1]:
                                replace_var(f'J/JLxx-xx-T/E-REQ_{indexFBD}-{index_req}', f'{it[2]}-{simp(it[15])}-CF-E-REQ')
                                index_req += 1

                        replace_var(f'xx-TP_{indexFBD}-1', f'{data_var}-{arah}TP')
                        replace_var(f'Axx-RRLS-TE_{indexFBD}', f'{data_var}-RRLS-TE')

                        replace_var(f'J/JL/Lxx-RRLS-TE_{indexFBD}', f'J{data_var[1:]}-RRLS-TE')

                        replace_var(f'Axx-W/EFL-CFR_{indexFBD}', f'{data_var}-{arah}FL-CFR')
                        replace_var(f'Axx-W/EFLR-DO_{indexFBD}', f'{data_var}-{arah}FLR-DO')
                        replace_var(f'Axx-ECR-DO_{indexFBD}', f'{data_var}-ECR-DO')
                        if arah == "E":
                            replace_var(f'Axx-ES/WS_{indexFBD}', f'{data_var}-WS')
                            replace_var(f'Axx-E/WFLZR-DI_{indexFBD}', f'{data_var}-WFLZR-DI')
                        else:
                            replace_var(f'Axx-ES/WS_{indexFBD}', f'{data_var}-ES')
                            replace_var(f'Axx-E/WFLZR-DI_{indexFBD}', f'{data_var}-EFLZR-DI')

                        replace_var(f'Axx-BLOK-FAIL_{indexFBD}', f'{data_var}-BLOK-FAIL')

                        for index in range(1, 21):
                            replace_var(f'J/JLxx-xx-T/E-REQ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC6 Lock From This Station"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC6 Lock From This Station"

        vfc_53_sil_to_sil()

    ############################## v FC8 Route Check ############################
    def v_fc8_route_check(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # nFC 54 T ROUTE CHECK
        def nfc_54_t_route_check():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))
            signalSR = list(set([signal[2] for signal in IT1 if signal[8]]))
            signalLDR = list(set([signal[2] for signal in IT1 if signal[10]]))
            signalRDR = list(set([signal[2] for signal in IT1 if signal[11]]))
            rute_t = [it for it in IT1 if "(T)" in it[1]]
            rute_e = [it for it in IT1 if "(E)" in it[1]]
            rute_cf = [it for it in IT1 if "(CF)" in it[1]]

            varEnumerated = [rt for rt in rute_t if not (rt[4] and rt[5])]
            jumlahGenFBD = 10
            FBDtujuan = "nFC 54 T ROUTE CHECK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]

                        rute = f"{sinyal_asal}-{simp(sinyal_tujuan)}"

                        replace_var(f'J/JL/Lxx-xx-T-L_{indexFBD}', f'{rute}-T-L')
                        replace_var(f'J/JL/Lxx-xx-T-REQ_{indexFBD}', f'{rute}-T-REQ')
                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'{sinyal_asal}-ECR')
                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{rute}-E-L')
                        replace_var(f'J/JL/Lxx-xx-E-REQ_{indexFBD}', f'{rute}-E-REQ')
                        replace_var(f'J/JL/Lxx-xx-E_{indexFBD}', f'{rute}-E')

                        if sinyal_asal in signalHR:
                            replace_var(f'J/JL/Lxx-xx-H_{indexFBD}', f'{rute}-H')
                        else:
                            replace_var(f'J/JL/Lxx-xx-H_{indexFBD}', f'{rute}-D')

                        if "-R" not in data_var[18]:
                            replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'{sinyal_asal}-EC-R-RD')
                        else:
                            replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'{sinyal_asal}-ECR-DI')


                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            varEnumerated = [rt for rt in rute_t if rt[4] and rt[5]]
            jumlahGenFBD = 10
            FBDtujuan = "nFC 54 T ROUTE CHECK (3 ASPEK)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        rute = f"{sinyal_asal}-{simp(sinyal_tujuan)}"

                        replace_var(f'J/JL/Lxx-xx-T-L_{indexFBD}', f'{rute}-T-L')
                        replace_var(f'J/JL/Lxx-xx-T-REQ_{indexFBD}', f'{rute}-T-REQ')
                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'{sinyal_asal}-ECR')
                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{rute}-E-L')
                        replace_var(f'J/JL/Lxx-xx-E-REQ_{indexFBD}', f'{rute}-E-REQ')
                        replace_var(f'J/JL/Lxx-xx-E_{indexFBD}', f'{rute}-E')
                        if sinyal_asal in signalHR:
                            replace_var(f'J/JL/Lxx-xx-H_{indexFBD}', f'{rute}-H')
                        else:
                            replace_var(f'J/JL/Lxx-xx-H_{indexFBD}', f'{rute}-D')

                        if "-R" not in data_var[18]:
                            replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'{sinyal_asal}-EC-R-RD')
                            if sinyal_asal in signalHR:
                                replace_var(f'J/JL/Lxx-xx-D_{indexFBD}', f'{rute}-D')
                                replace_var(f'J/JL/Lxx-xx-D-REQ_{indexFBD}', f'{rute}-D-REQ')
                                replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{sinyal_asal}-EC-G-RD')
                                replace_var(f'J/JL/Lxx-EC-G-Y-TE_{indexFBD}', f'{sinyal_asal}-EC-G-Y-TE')
                                for it in IT1:
                                    if it[0] + ".0" == str(data_var[28]).strip():
                                        if it[2] in signalHR:
                                            replace_var(f'J/JL/Lxx-xx-D_{indexFBD}-1', f'{it[2]}-{simp(it[15])}-H')
                                            break
                                        else:
                                            replace_var(f'J/JL/Lxx-xx-D_{indexFBD}-1', f'{it[2]}-{simp(it[15])}-D')
                                            break
                                if sinyal_tujuan.startswith("A") or sinyal_tujuan in signalHR:
                                    replace_var(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{sinyal_tujuan}-HR-DI')
                                else:
                                    replace_var(f'J/JL/Lxx-HR/DR-DO_{indexFBD}', f'{sinyal_tujuan}-DR-DI')
                        else:
                            replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'{sinyal_asal}-ECR-DI')
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')
                            replace_var(f'J/JL/Lxx-EC-G-Y-TE_{indexFBD}', f'TRUE')


                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} 3 ASPEK {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            varEnumerated = rute_cf
            FBDtujuan = "nFC 54 T ROUTE CHECK (CF)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var[2]
                        sinyal_tujuan = data_var[15]
                        cf = ""
                        if '(CF)' in data_var[1]:
                            cf = "-CF"
                        rute = f"{sinyal_asal}-{simp(sinyal_tujuan)}{cf}"

                        replace_var(f'J/JL/Lxx-xx-T-L_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-xx-T-REQ_{indexFBD}', f'FALSE')
                        replace_var(f'J/JLxx-ECR_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-xx-E-L_{indexFBD}', f'{rute}-E-L')
                        replace_var(f'J/JL/Lxx-xx-E-REQ_{indexFBD}', f'{rute}-E-REQ')
                        replace_var(f'J/JL/Lxx-xx-E_{indexFBD}', f'{rute}-E')

                        replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-EC-G-Y-TE_{indexFBD}', f'TRUE')


                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} (CF) {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # nFC 55 S ROUTE CHECK
        def nfc_55_s_route_check():
            varEnumerated = sorted(list(set([f"{it[2]}-{simp(it[15])}-S" for it in IT1 if "(S)" in it[1]])))
            jumlahGenFBD = 10
            FBDtujuan = "nFC 55 S ROUTE CHECK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/Lxx-xx-S-REQ_{indexFBD}', f'{data_var}-REQ')
                        replace_var(f'J/JL/Lxx-xx-S-L_{indexFBD}', f'{data_var}-L')
                        replace_var(f'J/JL/Lxx-xx-S_{indexFBD}', f'{data_var}')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC8 Route Check"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC8 Route Check"

        nfc_54_t_route_check()
        nfc_55_s_route_check()

    ################################ v FC9 SIGNAL LIGHTING ##############################
    def v_fc9_signal_lighting(self, IT1, IT2, referensiCSV, directorySimpan, PM, jpldata):
        # V FC9 SIGNAL- vFC 61 S MASUK
        def vFC_61_S_MASUK():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))
            signalSR = list(set([signal[2] for signal in IT1 if signal[8]]))
            signalLDR = list(set([signal[2] for signal in IT1 if signal[10]]))
            signalRDR = list(set([signal[2] for signal in IT1 if signal[11]]))

            varEnumerated = sorted(list(set([it[2] for it in IT1 if not it[15].startswith("A") and "(S)" not in it[1]])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 61 S MASUK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var

                        if sinyal_asal in signalHR:
                            replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'{sinyal_asal}-HR-DO')
                        if sinyal_asal in signalDR:
                            replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{sinyal_asal}-DR-DO')
                        if sinyal_asal in signalER:
                            replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{sinyal_asal}-ER-DO')
                        if sinyal_asal in signalLDR:
                            replace_var(f'J/JL/Lxx-LDR-DO_{indexFBD}', f'{sinyal_asal}-LDR-DO')
                            for it in IT1:
                                if sinyal_asal == it[2] and it[10]:
                                    replace_var(f'J/JL/Lxx-xx-H-LD_{indexFBD}', f'{sinyal_asal}-{simp(it[15])}-H-LD')
                        if sinyal_asal in signalRDR:
                            replace_var(f'J/JL/Lxx-RDR-DO_{indexFBD}', f'{sinyal_asal}-RDR-DO')
                            for it in IT1:
                                if sinyal_asal == it[2] and it[11]:
                                    replace_var(f'J/JL/Lxx-xx-H-RD_{indexFBD}', f'{sinyal_asal}-{simp(it[15])}-H-RD')
                        if sinyal_asal in signalSR:
                            replace_var(f'J/JL/Lxx-SR-DO_{indexFBD}', f'{sinyal_asal}-SR-DO')
                            replace_var(f'J/JL/Lxx-SECR_{indexFBD}', f'{sinyal_asal}-SECR')

                        index_H_Divert = 1
                        index_E = 1
                        index_D = 1
                        for it in IT1:
                            accnv = ""
                            if "JPL" in it[25]:
                                for jpl in jpldata:
                                    if jpl[0].split("-")[0] in it[25] and f'{jpl[1]}T' in it[20].split(" ") and "OL" not in jpl[0]:
                                        cek = True
                                        for wjpl in jpl[2].split(" "):
                                            if wjpl not in it[18].split(" "):
                                                cek = False
                                        if cek:
                                            accnv = f" AND {jpl[0]}-ACCNV"
                            for it2 in IT2:
                                if it[1] == it2[1]:
                                    if "JPL" in it2[14]:
                                        for jpl in jpldata:
                                            if jpl[0].split("-")[0] in it2[14] and f'{jpl[1]}T' in it2[9].split(" ") and "OL" in jpl[0]:
                                                cek = True
                                                for wjpl in jpl[2].split(" "):
                                                    if wjpl not in it2[7].split(" "):
                                                        cek = False
                                                if cek:
                                                    accnv = f" AND {jpl[0]}-ACCNV"
                            if sinyal_asal == it[2] and "-R" not in it[18] and "(T)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-H_{indexFBD}', f'{sinyal_asal}-{simp(it[15])}-H{accnv}')
                            if sinyal_asal == it[2] and "-R" in it[18] and "(T)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-H-DIVERT_{indexFBD}-{index_H_Divert}', f'{sinyal_asal}-{simp(it[15])}-H{accnv}')
                                index_H_Divert += 1
                            if sinyal_asal == it[2] and ("(E)" in it[1] or "(CF)" in it[1]):
                                cf = ""
                                if "(CF)" in it[1]:
                                    cf = "-CF"
                                replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index_E}', f'{sinyal_asal}-{simp(it[15])}{cf}-E')
                                index_E += 1
                            if sinyal_asal == it[2] and "-R" not in it[18] and "(T)" in it[1] and it[4]:
                                replace_var(f'J/JL/Lxx-xx-D_{indexFBD}-{index_E}', f'{sinyal_asal}-{simp(it[15])}-D{accnv}')
                                index_D += 1
                        index_track = 1
                        for it in IT1:
                            if sinyal_asal == it[2] and it[23]:
                                for track in it[23].strip().replace("T", " ").split(" "):
                                    if track:
                                        replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{track}-TP')
                                        index_track += 1
                                break

                        if sinyal_asal in signalHR and sinyal_asal in signalDR:
                            replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'{sinyal_asal}-EC-R-RD')
                            replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{sinyal_asal}-EC-G-RD')
                            replace_var(f'J/JL/Lxx-EC-G-Y-TE_{indexFBD}', f'{sinyal_asal}-EC-G-Y-TE')
                            replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'{sinyal_asal}-ECR')
                            replace_var(f'J/JL/Lxx-DR_{indexFBD}', f'{sinyal_asal}-DR')
                            replace_var(f'J/JL/Lxx-SR_{indexFBD}', f'{sinyal_asal}-SR')
                            replace_var(f'J/JL/Lxx-SECR-DI_{indexFBD}', f'{sinyal_asal}-SECR-DI')
                            replace_var(f'J/JL/Lxx-EC-Y-RD_{indexFBD}', f'{sinyal_asal}-EC-Y-RD')

                        replace_var(f'J/JL/Lxx-xx-H_{indexFBD}', f'FALSE')
                        for index in range(1, 50):
                            replace_var(f'J/JL/Lxx-xx-H-DIVERT_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-D_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')
                        replace_var(f'J/JL/Lxx-xx-H-LD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-xx-H-RD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-SECR_{indexFBD}', f'TRUE')

                        replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-LDR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-RDR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-SR-DO_{indexFBD}', f'HAPUS VARIABLE INI')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # V FC9 SIGNAL- vFC 62 S BERANGKAT
        def vFC_62_S_BERANGKAT():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))
            signalSR = list(set([signal[2] for signal in IT1 if signal[8]]))
            signalCFR = list(set([signal[2] for signal in IT1 if signal[9]]))
            signalLDR = list(set([signal[2] for signal in IT1 if signal[10]]))
            signalRDR = list(set([signal[2] for signal in IT1 if signal[11]]))

            varEnumerated = sorted(list(set([it[2] for it in IT1 if it[15].startswith("A") and "(S)" not in it[1]])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 62 S BERANGKAT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var

                        if sinyal_asal in signalDR:
                            replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'{sinyal_asal}-DR-DO')
                        if sinyal_asal in signalER:
                            replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{sinyal_asal}-ER-DO')
                        if sinyal_asal in signalGR:
                            replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{sinyal_asal}-GR-DO')
                        if sinyal_asal in signalCFR:
                            replace_var(f'J/JL/Lxx-CFR-DO_{indexFBD}', f'{sinyal_asal}-CFR-DO')
                        if sinyal_asal in signalLDR:
                            replace_var(f'J/JL/Lxx-LDR-DO_{indexFBD}', f'{sinyal_asal}-LDR-DO')
                            for it in IT1:
                                if sinyal_asal == it[2] and it[10]:
                                    replace_var(f'J/JL/Lxx-xx-H-LD_{indexFBD}',
                                                f'{sinyal_asal}-{simp(it[15])}-H-LD')
                        if sinyal_asal in signalRDR:
                            replace_var(f'J/JL/Lxx-RDR-DO_{indexFBD}', f'{sinyal_asal}-RDR-DO')
                            for it in IT1:
                                if sinyal_asal == it[2] and it[11]:
                                    replace_var(f'J/JL/Lxx-xx-H-RD_{indexFBD}',
                                                f'{sinyal_asal}-{simp(it[15])}-H-RD')
                        if sinyal_asal in signalSR:
                            replace_var(f'J/JL/Lxx-SR-DO_{indexFBD}', f'{sinyal_asal}-SR-DO')
                            replace_var(f'J/JL/Lxx-SECR_{indexFBD}', f'{sinyal_asal}-SECR')

                        index_D_Divert = 1
                        index_E = 1
                        index_CF = 1
                        index_S = 1
                        for it in IT1:
                            accnv = ""
                            if "JPL" in it[25]:
                                for jpl in jpldata:
                                    if jpl[0].split("-")[0] in it[25] and f'{jpl[1]}T' in it[20].split(
                                            " ") and "OL" not in jpl[0]:
                                        cek = True
                                        for wjpl in jpl[2].split(" "):
                                            if wjpl not in it[18].split(" "):
                                                cek = False
                                        if cek:
                                            accnv = f" AND {jpl[0]}-ACCNV"
                            if sinyal_asal == it[2] and "-R" not in it[18] and "(T)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-D_{indexFBD}', f'{sinyal_asal}-{simp(it[15])}-D{accnv}')
                            if sinyal_asal == it[2] and "-R" in it[18] and "(T)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-D-DIVERT_{indexFBD}-{index_D_Divert}', f'{sinyal_asal}-{simp(it[15])}-D{accnv}')
                                index_D_Divert += 1
                            if sinyal_asal == it[2] and "(E)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index_E}', f'{sinyal_asal}-{simp(it[15])}-E')
                                index_E += 1
                            if sinyal_asal == it[2] and "(CF)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-CF-E_{indexFBD}-{index_CF}', f'{sinyal_asal}-{simp(it[15])}-CF-E')
                                index_CF += 1
                            if sinyal_asal == it[2] and "(S)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-S_{indexFBD}-{index_S}', f'{sinyal_asal}-{simp(it[15])}-S{accnv}')
                                index_S += 1

                        index_track = 1
                        for it in IT1:
                            if sinyal_asal == it[2] and it[23]:
                                for track in it[23].strip().replace("T", " ").split(" "):
                                    if track:
                                        replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{track}-TP')
                                        index_track += 1
                                break

                        for it in IT1:
                            if sinyal_asal == it[2] and "(T)" and "-R" not in it[18]:
                                replace_var(f'J/JL/Lxx-xx-T-L_{indexFBD}', f'{sinyal_asal}-{simp(it[15])}-T-L')
                                replace_var(f'J/JL/Lxx-ECR_{indexFBD}', f'{sinyal_asal}-ECR')
                                replace_var(f'J/JL/Lxx-EC-R-RD_{indexFBD}', f'{sinyal_asal}-EC-R-RD')
                                replace_var(f'J/JL/Lxx-EC-G-RD_{indexFBD}', f'{sinyal_asal}-EC-G-RD')
                                break

                        replace_var(f'J/JL/Lxx-xx-D_{indexFBD}', f'FALSE')
                        for index in range(1, 50):
                            replace_var(f'J/JL/Lxx-xx-D-DIVERT_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-CF-E_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-S_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')
                        replace_var(f'J/JL/Lxx-xx-H-LD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-xx-H-RD_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-SECR_{indexFBD}', f'TRUE')

                        replace_var(f'J/JL/Lxx-DR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-CFR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-LDR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-RDR-DO_{indexFBD}', f'HAPUS VARIABLE INI')
                        replace_var(f'J/JL/Lxx-SR-DO_{indexFBD}', f'HAPUS VARIABLE INI')


                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # V FC9 SIGNAL- vFC 63 S LANGSIR
        def vFC_63_S_LANGSIR():
            langsir_antara = map([[s[21].split(" ")] for s in IT1])
            print(langsir_antara)
            signal_berangakat = sorted( list(set([it[2] for it in IT1 if it[15].startswith("A") and "(S)" not in it[1]])))

            varEnumerated = sorted(list(set([it[2] for it in IT1 if "(S)" in it[1] and it[2] not in signal_berangakat])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 63 S LANGSIR"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var


                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{sinyal_asal}-GR-DO')

                        index_S = 1
                        for it in IT1:
                            accnv = ""
                            if "JPL" in it[25]:
                                if "JPL" in it[25]:
                                    for jpl in jpldata:
                                        if jpl[0].split("-")[0] in it[25] and f'{jpl[1]}T' in it[20].split(" ") and "OL" not in jpl[0]:
                                            cek = True
                                            for wjpl in jpl[2].split(" "):
                                                if wjpl not in it[18].split(" "):
                                                    cek = False
                                            if cek:
                                                accnv = f" AND {jpl[0]}-ACCNV"
                            if sinyal_asal == it[2] and "(S)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-S_{indexFBD}-{index_S}', f'{sinyal_asal}-{simp(it[15])}-S{accnv}')
                                index_S += 1

                        index_track = 1
                        for it in IT1:
                            if sinyal_asal == it[2] and it[23]:
                                for track in it[23].strip().replace("T", " ").split(" "):
                                    if track:
                                        replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{track}-TP')
                                        index_track += 1
                                break
                        replace_var(f'xx-TP_{indexFBD}-{1}', f'False')

                        for index in range(1, 50):
                            replace_var(f'J/JL/Lxx-xx-S_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # V FC9 SIGNAL- vFC 64 S LANGSIR (SHUNT)
        def vFC_64_S_LANGSIR_SHUNT():
            signal_berangakat = sorted(
                list(set([it[2] for it in IT1 if it[15].startswith("A") and "(S)" not in it[1]])))

            varEnumerated = sorted(
                list(set([it[2] for it in IT1 if "(S)" in it[1] and it[2] not in signal_berangakat])))

            jumlahGenFBD = 10
            FBDtujuan = "vFC 64 S LANGSIR SHUNT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var

                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{sinyal_asal}-GR-DO')

                        index_S = 1
                        for it in IT1:
                            accnv = ""
                            if "JPL" in it[25]:
                                if "JPL" in it[25]:
                                    for jpl in jpldata:
                                        if jpl[0].split("-")[0] in it[25] and f'{jpl[1]}T' in it[20].split(
                                                " ") and "OL" not in jpl[0]:
                                            cek = True
                                            for wjpl in jpl[2].split(" "):
                                                if wjpl not in it[18].split(" "):
                                                    cek = False
                                            if cek:
                                                accnv = f" AND {jpl[0]}-ACCNV"
                            if sinyal_asal == it[2] and "(S)" in it[1]:
                                replace_var(f'J/JL/Lxx-xx-S_{indexFBD}-{index_S}',
                                            f'{sinyal_asal}-{simp(it[15])}-S{accnv}')
                                index_S += 1

                        index_track = 1
                        for it in IT1:
                            if sinyal_asal == it[2] and it[23]:
                                for track in it[23].strip().replace("T", " ").split(" "):
                                    if track:
                                        replace_var(f'xx-TP_{indexFBD}-{index_track}', f'{track}-TP')
                                        index_track += 1
                                break
                        replace_var(f'xx-TP_{indexFBD}-{1}', f'False')

                        for index in range(1, 50):
                            replace_var(f'J/JL/Lxx-xx-S_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-TP_{indexFBD}-{index}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(
                            e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC9 Signal Lighting"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC9 Signal Lighting"

        vFC_61_S_MASUK()
        vFC_62_S_BERANGKAT()
        # vFC_63_S_LANGSIR()

    ################################# v FC10 Route Lock ###############################
    def v_fc10_route_lock(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # vFC 56 Route Lock
        def vfc_56_route_lock_es():
            track = []
            for it in IT1:
                if "EAST" in it[-1]:
                    list_track = []
                    if it[15].startswith("A"):
                        list_track = it[20].split(" ")
                    if it[27]:
                        list_track = it[20].split(" ")[:-1]
                    else:
                        list_track = it[20].split(" ")
                    for data in list_track:
                        if data:
                            if data.endswith("T"):
                                track.append(data[:-1])
                            else:
                                track.append(data)
            varEnumerated = sorted(list(set(track)))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 56 ROUTE LOCK (ES)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track_back = []
                        for it in IT1:
                            if f"{data_var}T" in it[20].split(" ")[1:] and "EAST" in it[-1]:
                                track_back.append(it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1])

                            if f"{data_var}T" in it[20].split(" ")[0] and "EAST" in it[-1] and "(T)" in it[1]:
                                replace_var(f'xx-T-ES-RL_{indexFBD}', f'{data_var}-T-ES-RL')
                            if f"{data_var}T" in it[20].split(" ")[0] and "EAST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]):
                                replace_var(f'xx-E-ES-RL_{indexFBD}', f'{data_var}-E-ES-RL')
                            if f"{data_var}T" in it[20].split(" ")[0] and "EAST" in it[-1] and "(S)" in it[1]:
                                replace_var(f'xx-S-ES-RL_{indexFBD}', f'{data_var}-S-ES-RL')

                            if it[15].startswith("A"):  track_cek = it[20].split(" ")
                            elif it[27]:                track_cek = it[20].split(" ")[:-1]
                            else:                       track_cek = it[20].split(" ")
                            if f"{data_var}T" in track_cek and "EAST" in it[-1] and "(T)" in it[1]:
                                replace_var(f'xx-T-ES/WS_{indexFBD}', f'{data_var}-T-ES')
                            if f"{data_var}T" in track_cek and "EAST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]):
                                replace_var(f'xx-E-ES/WS_{indexFBD}', f'{data_var}-E-ES')
                            if f"{data_var}T" in track_cek and "EAST" in it[-1] and "(S)" in it[1]:
                                replace_var(f'xx-S-ES/WS_{indexFBD}', f'{data_var}-S-ES')

                        track_back = sorted(list(set(track_back)))
                        for index_track, track in enumerate(track_back):
                            wesel = ""
                            cek_t = False
                            cek_e = False
                            cek_s = False
                            for it in IT1:
                                if it[15].startswith("A"):  track_cek = it[20].split(" ")[1:]
                                elif it[27]:                track_cek = it[20].split(" ")[1:-1]
                                else:                       track_cek = it[20].split(" ")[1:]
                                if f"{data_var}T" in track_cek and f"{track}" in it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1] and "EAST" in it[-1] and "(T)" in it[1]:
                                    replace_var(f'xx-T-ES/WS-BACK{index_track + 1}_{indexFBD}', f'{track[:-1]}-T-ES')
                                    cek_t = True
                                if f"{data_var}T" in track_cek and f"{track}" in it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1] and "EAST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]):
                                    replace_var(f'xx-E-ES/WS-BACK{index_track + 1}_{indexFBD}', f'{track[:-1]}-E-ES')
                                    cek_e = True
                                if f"{data_var}T" in track_cek and f"{track}" in it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1] and "EAST" in it[-1] and "(S)" in it[1]:
                                    replace_var(f'xx-S-ES/WS-BACK{index_track + 1}_{indexFBD}', f'{track[:-1]}-S-ES')
                                    cek_s = True
                                if f"{data_var}T" in it[20].split(" ") and f"{track}" in it[20].split(" ") and "EAST" in it[-1]: wesel += f" {it[18]}"

                            wesel_filtered1 = []
                            wesel_filtered2 = []
                            for w in sorted(list(set(wesel.strip().split(" ")))):
                                for wesel in PM:
                                    if w.replace("-N", "").replace("-R", "") == wesel[0].replace("W", "") and (track.replace("T", "") == wesel[1] or track.replace("T", "") == wesel[2]):
                                        wesel_filtered1.append(w)
                                        wesel_filtered2.append(w.replace("-N", "").replace("-R", ""))

                            for w in sorted(list(set(wesel_filtered2))):
                                if w + "-R" in wesel_filtered1 and w + "-N" in wesel_filtered1:
                                    wesel_filtered1.remove(w + "-R")
                                    wesel_filtered1.remove(w + "-N")

                            if wesel_filtered1:
                                for index_wesel, w in enumerate(wesel_filtered1):
                                    ws = w.replace("-R", "").replace("-N", "")
                                    if index_track == 0:
                                        if "-R" in w:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{1 + index_wesel}', f'W{ws}-NWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{5 + index_wesel}', f'W{ws}-NWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{9 + index_wesel}', f'W{ws}-NWZ')
                                        else:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{1 + index_wesel}', f'W{ws}-RWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{5 + index_wesel}', f'W{ws}-RWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{9 + index_wesel}', f'W{ws}-RWZ')
                                    if index_track == 1:
                                        if "-R" in w:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{3 + index_wesel}', f'W{ws}-NWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{7 + index_wesel}', f'W{ws}-NWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{11 + index_wesel}', f'W{ws}-NWZ')
                                        else:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{3 + index_wesel}', f'W{ws}-RWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{7 + index_wesel}', f'W{ws}-RWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{11 + index_wesel}', f'W{ws}-RWZ')

                        replace_var(f'xx-TP_{indexFBD}', f'{data_var}-TP')
                        replace_var(f'xx-RLS_{indexFBD}', f'{data_var}-RLS')

                        replace_var(f'xx-T-ES-RL_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES-RL_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES-RL_{indexFBD}', f'TRUE')
                        replace_var(f'xx-T-ES/WS_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES/WS_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES/WS_{indexFBD}', f'TRUE')

                        replace_var(f'xx-T-ES/WS-BACK1_{indexFBD}', f'TRUE')
                        replace_var(f'xx-T-ES/WS-BACK2_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES/WS-BACK1_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES/WS-BACK2_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES/WS-BACK1_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES/WS-BACK2_{indexFBD}', f'TRUE')

                        for index_track in range(1, 13):
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_track}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # vFC 57 Route Lock
        def vfc_56_route_lock_ws():
            track = []
            for it in IT1:
                if "WEST" in it[-1]:
                    list_track = []
                    if it[15].startswith("A"):
                        list_track = it[20].split(" ")
                    if it[27]:
                        list_track = it[20].split(" ")[:-1]
                    else:
                        list_track = it[20].split(" ")
                    for data in list_track:
                        if data:
                            if data.endswith("T"):
                                track.append(data[:-1])
                            else:
                                track.append(data)
            varEnumerated = sorted(list(set(track)))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 56 ROUTE LOCK (WS)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        track_back = []
                        for it in IT1:
                            if f"{data_var}T" in it[20].split(" ")[1:] and "WEST" in it[-1]:
                                track_back.append(
                                    it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1])

                            if f"{data_var}T" in it[20].split(" ")[0] and "WEST" in it[-1] and "(T)" in it[1]:
                                replace_var(f'xx-T-WS-RL_{indexFBD}', f'{data_var}-T-WS-RL')
                            if f"{data_var}T" in it[20].split(" ")[0] and "WEST" in it[-1] and (
                                    "(E)" in it[1] or "(CF)" in it[1]):
                                replace_var(f'xx-E-WS-RL_{indexFBD}', f'{data_var}-E-WS-RL')
                            if f"{data_var}T" in it[20].split(" ")[0] and "WEST" in it[-1] and "(S)" in it[1]:
                                replace_var(f'xx-S-WS-RL_{indexFBD}', f'{data_var}-S-WS-RL')

                            if it[15].startswith("A"):  track_cek = it[20].split(" ")
                            elif it[27]:                track_cek = it[20].split(" ")[:-1]
                            else:                       track_cek = it[20].split(" ")
                            if f"{data_var}T" in track_cek and "WEST" in it[-1] and "(T)" in it[1]:
                                replace_var(f'xx-T-ES/WS_{indexFBD}', f'{data_var}-T-WS')
                            if f"{data_var}T" in track_cek and "WEST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]):
                                replace_var(f'xx-E-ES/WS_{indexFBD}', f'{data_var}-E-WS')
                            if f"{data_var}T" in track_cek and "WEST" in it[-1] and "(S)" in it[1]:
                                replace_var(f'xx-S-ES/WS_{indexFBD}', f'{data_var}-S-WS')

                        track_back = sorted(list(set(track_back)))
                        for index_track, track in enumerate(track_back):
                            wesel = ""
                            cek_t = False
                            cek_e = False
                            cek_s = False
                            for it in IT1:
                                if it[15].startswith("A"):  track_cek = it[20].split(" ")[1:]
                                elif it[27]:                track_cek = it[20].split(" ")[1:-1]
                                else:                       track_cek = it[20].split(" ")[1:]
                                if f"{data_var}T" in track_cek and f"{track}" in it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1] and "WEST" in it[-1] and "(T)" in it[1]:
                                    replace_var(f'xx-T-ES/WS-BACK{index_track + 1}_{indexFBD}',
                                                f'{track[:-1]}-T-WS')
                                    cek_t = True
                                if f"{data_var}T" in track_cek and f"{track}" in it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1] and "WEST" in it[-1] and ("(E)" in it[1] or "(CF)" in it[1]):
                                    replace_var(f'xx-E-ES/WS-BACK{index_track + 1}_{indexFBD}', f'{track[:-1]}-E-WS')
                                    cek_e = True
                                if f"{data_var}T" in track_cek and f"{track}" in it[20].split(" ")[it[20].split(" ").index(f"{data_var}T") - 1] and "WEST" in it[-1] and "(S)" in it[1]:
                                    replace_var(f'xx-S-ES/WS-BACK{index_track + 1}_{indexFBD}',
                                                f'{track[:-1]}-S-WS')
                                    cek_s = True
                                if f"{data_var}T" in it[20].split(" ") and f"{track}" in it[20].split(" ") and "WEST" in it[-1]: wesel += f" {it[18]}"

                            wesel_filtered1 = []
                            wesel_filtered2 = []
                            for w in sorted(list(set(wesel.strip().split(" ")))):
                                for wesel in PM:
                                    if w.replace("-N", "").replace("-R", "") == wesel[0].replace("W", "") and (
                                            track.replace("T", "") == wesel[1] or track.replace("T", "") ==
                                            wesel[2]):
                                        wesel_filtered1.append(w)
                                        wesel_filtered2.append(w.replace("-N", "").replace("-R", ""))

                            for w in sorted(list(set(wesel_filtered2))):
                                if w + "-R" in wesel_filtered1 and w + "-N" in wesel_filtered1:
                                    wesel_filtered1.remove(w + "-R")
                                    wesel_filtered1.remove(w + "-N")

                            if wesel_filtered1:
                                for index_wesel, w in enumerate(wesel_filtered1):
                                    ws = w.replace("-R", "").replace("-N", "")
                                    if index_track == 0:
                                        if "-R" in w:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{1 + index_wesel}',
                                                            f'W{ws}-NWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{5 + index_wesel}',
                                                            f'W{ws}-NWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{9 + index_wesel}',
                                                            f'W{ws}-NWZ')
                                        else:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{1 + index_wesel}',
                                                            f'W{ws}-RWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{5 + index_wesel}',
                                                            f'W{ws}-RWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{9 + index_wesel}',
                                                            f'W{ws}-RWZ')
                                    if index_track == 1:
                                        if "-R" in w:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{3 + index_wesel}',
                                                            f'W{ws}-NWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{7 + index_wesel}',
                                                            f'W{ws}-NWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{11 + index_wesel}',
                                                            f'W{ws}-NWZ')
                                        else:
                                            if cek_t:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{3 + index_wesel}',
                                                            f'W{ws}-RWZ')
                                            if cek_e:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{7 + index_wesel}',
                                                            f'W{ws}-RWZ')
                                            if cek_s:
                                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{11 + index_wesel}',
                                                            f'W{ws}-RWZ')

                        replace_var(f'xx-TP_{indexFBD}', f'{data_var}-TP')
                        replace_var(f'xx-RLS_{indexFBD}', f'{data_var}-RLS')

                        replace_var(f'xx-T-WS-RL_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-WS-RL_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-WS-RL_{indexFBD}', f'TRUE')
                        replace_var(f'xx-T-ES/WS_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES/WS_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES/WS_{indexFBD}', f'TRUE')

                        replace_var(f'xx-T-ES/WS-BACK1_{indexFBD}', f'TRUE')
                        replace_var(f'xx-T-ES/WS-BACK2_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES/WS-BACK1_{indexFBD}', f'TRUE')
                        replace_var(f'xx-E-ES/WS-BACK2_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES/WS-BACK1_{indexFBD}', f'TRUE')
                        replace_var(f'xx-S-ES/WS-BACK2_{indexFBD}', f'TRUE')

                        for index_track in range(1, 13):
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_track}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC10 Route Lock"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC10 Route Lock"

        vfc_56_route_lock_es()
        vfc_56_route_lock_ws()

    ################################ v FC11 Overlap Approach Lock ###############################
    def v_fc11_overlap_aproach_lock(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # vFC 58 OVL APPR LOCK
        def vfc58_ovl_appr_lock():
            varEnumerated = sorted(list(set([it[20].replace("T", "").split(" ")[-1] for it in IT1 if
                                             "(T)" in it[1] and not it[15].startswith("A")])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 58 OVL APPR LOCK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'xx-TP_{indexFBD}', f'{data_var}-TP')

                        track_east = ""
                        for it in IT1:
                            if data_var in it[20].replace("T", "").split(" ") and "EAST" in it[-1]:
                                replace_var(f'xx-T-ELAS_{indexFBD}', f'{data_var}-T-ELAS')
                                replace_var(f'xx-T-ES_{indexFBD}', f'{it[20].replace("T", "").split(" ")[-2]}-T-ES')
                                track_east = it[20].replace("T", "").split(" ")[-2]
                                break
                        track_west = ""
                        for it in IT1:
                            if data_var in it[20].replace("T", "").split(" ") and "WEST" in it[-1]:
                                replace_var(f'xx-T-WLAS_{indexFBD}', f'{data_var}-T-WLAS')
                                replace_var(f'xx-T-WS_{indexFBD}', f'{it[20].replace("T", "").split(" ")[-2]}-T-WS')
                                track_west = it[20].replace("T", "").split(" ")[-2]
                                break

                        wesel_east = []
                        wesel_west = []
                        for w in PM:
                            if w[1].replace("T", "") == track_east or w[2].replace("T", "") == track_east:
                                wesel_east.append(w[0])
                            if w[1].replace("T", "") == track_west or w[2].replace("T", "") == track_west:
                                wesel_west.append(w[0])

                        wesel_east_filtered = []
                        for w in wesel_east:
                            wesel = w.replace("W", " ")
                            cek_r = False
                            cek_n = False
                            exist = False
                            for it in IT1:
                                if "EAST" in it[-1] and data_var == it[20].replace("T", "").split(" ")[-1] and f"{wesel}-R" in it[18] and not cek_r:
                                    cek_r = True
                                if "EAST" in it[-1] and data_var == it[20].replace("T", "").split(" ")[-1] and f"{wesel}-N" in it[18] and not cek_n:
                                    cek_n = True
                                if "EAST" in it[-1] and data_var == it[20].replace("T", "").split(" ")[-1] and wesel in it[18] and not exist:
                                    exist = True
                            if not (cek_r and cek_n) and exist:
                                if cek_r:
                                    wesel_east_filtered.append(f'{w}-NWZ')
                                if cek_n:
                                    wesel_east_filtered.append(f'{w}-RWZ')
                        wesel_west_filtered = []
                        for w in wesel_west:
                            wesel = w.replace("W", " ")
                            cek_r = False
                            cek_n = False
                            exist = False
                            for it in IT1:
                                if "WEST" in it[-1] and data_var == it[20].replace("T", "").split(" ")[-1] and f"{wesel}-R" in it[18] and not cek_r:
                                    cek_r = True
                                if "WEST" in it[-1] and data_var == it[20].replace("T", "").split(" ")[-1] and f"{wesel}-N" in it[18] and not cek_n:
                                    cek_n = True
                                if "WEST" in it[-1] and data_var == it[20].replace("T", "").split(" ")[-1] and wesel in it[18] and not exist:
                                    exist = True
                            if not (cek_r and cek_n) and exist:
                                if cek_r:
                                    wesel_west_filtered.append(f'{w}-NWZ')
                                if cek_n:
                                    wesel_west_filtered.append(f'{w}-RWZ')

                        index_east = 1
                        index_west = 11
                        for wesel in wesel_east_filtered:
                            if index_east <= 10:
                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_east}', f'{wesel}')
                            index_east += 1
                        for wesel in wesel_west_filtered:
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_west}', f'{wesel}')
                            index_west += 1

                        for index in range(1, 21):
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC11 Overlap Approach Lock"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC11 Overlap Approach Lock"

        vfc58_ovl_appr_lock()

    ################################ v FC12 Approach Lock ###############################
    def v_fc12_aproach_lock(self, IT1, IT2, referensiCSV, directorySimpan, PM):
        # vFC 59 APPR LOCK
        def vfc59_aproach_lock():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))
            signalSR = list(set([signal[2] for signal in IT1 if signal[8]]))
            signalLDR = list(set([signal[2] for signal in IT1 if signal[10]]))
            signalRDR = list(set([signal[2] for signal in IT1 if signal[11]]))

            varEnumerated = sorted(list(set([it[2] for it in IT1 if it[2] in signalHR or it[2] in signalDR or it[2] in signalER])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 59 APPR LOCK"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var

                        if sinyal_asal in signalHR:
                            replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'{sinyal_asal}-HR-DO')
                            replace_var(f'J/JL/Lxx-T-AS_{indexFBD}', f'{sinyal_asal}-T-AS')
                        if sinyal_asal in signalDR:
                            replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'{sinyal_asal}-DR-DO')
                            replace_var(f'J/JL/Lxx-T-AS_{indexFBD}', f'{sinyal_asal}-T-AS')
                        if sinyal_asal in signalER:
                            replace_var(f'J/JL/Lxx-ER-DO_{indexFBD}', f'{sinyal_asal}-ER-DO')
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}', f'{sinyal_asal}-E-AS')
                        if sinyal_asal in signalGR:
                            replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{sinyal_asal}-GR-DO')
                            replace_var(f'J/JL/Lxx-S-AS_{indexFBD}', f'{sinyal_asal}-S-AS')

                        for it in IT1:
                            if sinyal_asal == it[2]:
                                if it[23]:
                                    replace_var(f'xx-TPF_{indexFBD}', f'{it[23].replace("T", "")}-TP')
                                else:
                                    replace_var(f'xx-TPF_{indexFBD}', f'FALSE')
                                replace_var(f'xx-TPB_{indexFBD}', f'{it[20].replace("T", "").split(" ")[0]}-TP')

                        replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # vFC 60 APPR LOCK (SHUNT)
        def vfc60_aproach_lock_shunt():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))
            signalSR = list(set([signal[2] for signal in IT1 if signal[8]]))
            signalLDR = list(set([signal[2] for signal in IT1 if signal[10]]))
            signalRDR = list(set([signal[2] for signal in IT1 if signal[11]]))
            signalGRAntara = []
            for it in IT1:
                for langsir in it[21].split(" "):
                    signalGRAntara.append(langsir)

            varEnumerated = sorted(list(set([it[2] for it in IT1 if
                                             not (it[2] in signalHR or it[2] in signalDR or it[2] in signalER)
                                             and it[2] in signalGR
                                             and not it[2] in signalGRAntara])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 60 APPR LOCK (SHUNT)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var

                        if sinyal_asal in signalGR:
                            replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{sinyal_asal}-GR-DO')
                            replace_var(f'J/JL/Lxx-S-AS_{indexFBD}', f'{sinyal_asal}-S-AS')

                        for it in IT1:
                            if sinyal_asal == it[2]:
                                if it[23]:
                                    replace_var(f'xx-TPF_{indexFBD}', f'{it[23].replace("T", "")}-TP')
                                else:
                                    replace_var(f'xx-TPF_{indexFBD}', f'FALSE')
                                replace_var(f'xx-TPB_{indexFBD}', f'{it[20].replace("T", "").split(" ")[0]}-TP')

                        replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # vFC 60 APPR LOCK (SHUNT) MOD
        def vfc60_aproach_lock_shunt_mod():
            signalHR = list(set([signal[2] for signal in IT1 if signal[4]]))
            signalDR = list(set([signal[2] for signal in IT1 if signal[5]]))
            signalER = list(set([signal[2] for signal in IT1 if signal[6]]))
            signalGR = list(set([signal[2] for signal in IT1 if signal[7]]))
            signalSR = list(set([signal[2] for signal in IT1 if signal[8]]))
            signalLDR = list(set([signal[2] for signal in IT1 if signal[10]]))
            signalRDR = list(set([signal[2] for signal in IT1 if signal[11]]))
            signalGRAntara = []
            for it in IT1:
                for langsir in it[21].split(" "):
                    signalGRAntara.append(langsir)

            varEnumerated = sorted(list(set([it[2] for it in IT1 if
                                             not (it[2] in signalHR or it[2] in signalDR or it[2] in signalER)
                                             and it[2] in signalGR
                                             and it[2] in signalGRAntara])))
            jumlahGenFBD = 10
            FBDtujuan = "vFC 60 APPR LOCK (SHUNT)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        sinyal_asal = data_var

                        if sinyal_asal in signalGR:
                            replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'{sinyal_asal}-GR-DO')
                            replace_var(f'J/JL/Lxx-S-AS_{indexFBD}', f'{sinyal_asal}-S-AS')
                            replace_var(f'J/JL/Lxx-INT-AS_{indexFBD}', f'{sinyal_asal}-INT-AS')
                        for it in IT1:
                            if sinyal_asal == it[2]:
                                if it[23]:
                                    replace_var(f'xx-TPF_{indexFBD}', f'{it[23].replace("T", "")}-TP')
                                else:
                                    replace_var(f'xx-TPF_{indexFBD}', f'FALSE')
                                replace_var(f'xx-TPB_{indexFBD}', f'{it[20].replace("T", "").split(" ")[0]}-TP')

                        replace_var(f'J/JL/Lxx-HR-DO_{indexFBD}', f'FALSE')
                        replace_var(f'J/JL/Lxx-GR-DO_{indexFBD}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC12 Approach Lock"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC12 Approach Lock"

        vfc59_aproach_lock()
        vfc60_aproach_lock_shunt()
        vfc60_aproach_lock_shunt_mod()

    ################################ v FC13 Point Lock #############################
    def v_fc13_point_lock(self, IT1, IT2, referensiCSV, directorySimpan, pm):
        # v FC13 Point Lock - vFC 65 LOCKING POINT
        def vFC_65_LOCKING_POINT():
            varEnumerated = sorted([w for w in pm if w[0].startswith("W")])

            jumlahGenFBD = 10
            FBDtujuan = "vFC 65 LOCKING POINT"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        wesel = data_var[0]
                        twesel1 = data_var[1]
                        twesel2 = data_var[2]

                        replace_var(f'Wxx-L_{indexFBD}', f'{wesel}-L')
                        replace_var(f'xx-TP_{indexFBD}-1', f'{twesel1}-TP')

                        for it_data in IT1:
                            if twesel1 in it_data[20] and "(T)" in it_data[1] and "WEST" in it_data[-1]:
                                replace_var(f'xx-T-WS_{indexFBD}-1', f'{twesel1}-T-WS')
                            if twesel1 in it_data[20] and ("(E)" in it_data[1] or "(CF)" in it_data[1]) and "WEST" in it_data[-1]:
                                replace_var(f'xx-E-WS_{indexFBD}-1', f'{twesel1}-E-WS')
                            if twesel1 in it_data[20] and "(S)" in it_data[1] and "WEST" in it_data[-1]:
                                replace_var(f'xx-S-WS_{indexFBD}-1', f'{twesel1}-S-WS')

                            if twesel1 in it_data[20] and "(T)" in it_data[1] and "EAST" in it_data[-1]:
                                replace_var(f'xx-T-ES_{indexFBD}-1', f'{twesel1}-T-ES')
                            if twesel1 in it_data[20] and ("(E)" in it_data[1] or "(CF)" in it_data[1])  and "EAST" in it_data[-1]:
                                replace_var(f'xx-E-ES_{indexFBD}-1', f'{twesel1}-E-ES')
                            if twesel1 in it_data[20] and "(S)" in it_data[1] and "EAST" in it_data[-1]:
                                replace_var(f'xx-S-ES_{indexFBD}-1', f'{twesel1}-S-ES')

                            if twesel2:
                                replace_var(f'xx-TP_{indexFBD}-2', f'{twesel2}-TP')
                                if twesel2 in it_data[20] and "(T)" in it_data[1] and "WEST" in it_data[-1]:
                                    replace_var(f'xx-T-WS_{indexFBD}-2', f'{twesel2}-T-WS')
                                if twesel2 in it_data[20] and ("(E)" in it_data[1] or "(CF)" in it_data[1])  and "WEST" in it_data[-1]:
                                    replace_var(f'xx-E-WS_{indexFBD}-2', f'{twesel2}-E-WS')
                                if twesel2 in it_data[20] and "(S)" in it_data[1] and "WEST" in it_data[-1]:
                                    replace_var(f'xx-S-WS_{indexFBD}-2', f'{twesel2}-S-WS')

                                if twesel2 in it_data[20] and "(T)" in it_data[1] and "EAST" in it_data[-1]:
                                    replace_var(f'xx-T-ES_{indexFBD}-2', f'{twesel2}-T-ES')
                                if twesel2 in it_data[20] and ("(E)" in it_data[1] or "(CF)" in it_data[1])  and "EAST" in it_data[-1]:
                                    replace_var(f'xx-E-ES_{indexFBD}-2', f'{twesel2}-E-ES')
                                if twesel2 in it_data[20] and "(S)" in it_data[1] and "EAST" in it_data[-1]:
                                    replace_var(f'xx-S-ES_{indexFBD}-2', f'{twesel2}-S-ES')

                        index_elas = 1
                        index_wlas = 1
                        for it_data in IT2:
                            if twesel1 in it_data[9] and "WEST" in it_data[-1] and wesel[1:] in it_data[7]:
                                replace_var(f'xx-T-WLAS_{indexFBD}-{index_wlas}', f'{simp_number(it_data[6])}-T-WLAS')
                                index_wlas += 1
                            if twesel1 in it_data[9] and "EAST" in it_data[-1] and wesel[1:] in it_data[7]:
                                replace_var(f'xx-T-ELAS_{indexFBD}-{index_elas}', f'{simp_number(it_data[6])}-T-ELAS')
                                index_elas += 1
                            if twesel2:
                                if twesel2 in it_data[9] and "WEST" in it_data[-1] and wesel[1:] in it_data[7]:
                                    replace_var(f'xx-T-WLAS_{indexFBD}-{index_wlas}', f'{simp_number(it_data[6])}-T-WLAS')
                                    index_wlas += 1
                                if twesel2 in it_data[9] and "EAST" in it_data[-1] and wesel[1:] in it_data[7]:
                                    replace_var(f'xx-T-ELAS_{indexFBD}-{index_elas}', f'{simp_number(it_data[6])}-T-ELAS')
                                    index_elas += 1

                        index_tpz = 1
                        for wesel in pm:
                            if twesel1 == wesel[1] or twesel1 == wesel[2] or (twesel2 and (twesel2 == wesel[1] or twesel2 == wesel[2])):
                                replace_var(f'Wxx-TPZ_{indexFBD}-{index_tpz}', f'{wesel[0]}-TPZ')
                                index_tpz += 1

                        replace_var(f'xx-T-WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E-WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-S-WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-T-ES_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E-ES_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-S-ES_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-T-WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E-WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-S-WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-T-ES_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E-ES_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-S-ES_{indexFBD}-2', f'TRUE')

                        for index in range(1, 11):
                            replace_var(f'xx-T-WLAS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-T-ELAS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'Wxx-TPZ_{indexFBD}-{index}', f'FALSE')

                        replace_var(f'xx-TP_{indexFBD}-2', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC13 Point Lock"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC13 Point Lock"

        vFC_65_LOCKING_POINT()

    ################################ v FC14 Emerg R/P Release #############################
    def v_fc14_emerg_rp_release(self, IT1, IT2, referensiCSV, directorySimpan, pm):
        # vFC 66 EMERG POINT RELEASE
        def vFC_66_EMERG_POINT_RELEASE():
            varEnumerated = sorted([w for w in pm if w[0].startswith("W")])

            jumlahGenFBD = 10
            FBDtujuan = "vFC 66 EMERG POINT RELEASE"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        wesel = data_var[0]
                        twesel1 = data_var[1]
                        twesel2 = data_var[2]

                        replace_var(f'Wxx-SWRLS_{indexFBD}', f'{wesel}-SWRLS')
                        replace_var(f'Wxx-TPZ_{indexFBD}', f'{wesel}-TPZ')
                        replace_var(f'xx-TP_{indexFBD}-1', f'{twesel1}-TP')
                        if twesel2:
                            replace_var(f'xx-TP_{indexFBD}-2', f'{twesel2}-TP')
                        replace_var(f'Wxx-SWRLSPB-CTRL_{indexFBD}', f'{wesel}-SWRLSPB-CTRL')

                        for it_data in IT1:
                            if twesel1 in it_data[20] and "(T)" in it_data[1] and "WEST" in it_data[-1]:
                                replace_var(f'xx-T-WS_{indexFBD}-1', f'{twesel1}-T-WS')
                            if twesel1 in it_data[20] and (
                                    "(E)" in it_data[1] or "(CF)" in it_data[1]) and "WEST" in it_data[-1]:
                                replace_var(f'xx-E-WS_{indexFBD}-1', f'{twesel1}-E-WS')
                            if twesel1 in it_data[20] and "(S)" in it_data[1] and "WEST" in it_data[-1]:
                                replace_var(f'xx-S-WS_{indexFBD}-1', f'{twesel1}-S-WS')

                            if twesel1 in it_data[20] and "(T)" in it_data[1] and "EAST" in it_data[-1]:
                                replace_var(f'xx-T-ES_{indexFBD}-1', f'{twesel1}-T-ES')
                            if twesel1 in it_data[20] and (
                                    "(E)" in it_data[1] or "(CF)" in it_data[1]) and "EAST" in it_data[-1]:
                                replace_var(f'xx-E-ES_{indexFBD}-1', f'{twesel1}-E-ES')
                            if twesel1 in it_data[20] and "(S)" in it_data[1] and "EAST" in it_data[-1]:
                                replace_var(f'xx-S-ES_{indexFBD}-1', f'{twesel1}-S-ES')

                            if twesel2:
                                replace_var(f'xx-TP_{indexFBD}-2', f'{twesel2}-TP')
                                if twesel2 in it_data[20] and "(T)" in it_data[1] and "WEST" in it_data[-1]:
                                    replace_var(f'xx-T-WS_{indexFBD}-2', f'{twesel2}-T-WS')
                                if twesel2 in it_data[20] and (
                                        "(E)" in it_data[1] or "(CF)" in it_data[1]) and "WEST" in it_data[-1]:
                                    replace_var(f'xx-E-WS_{indexFBD}-2', f'{twesel2}-E-WS')
                                if twesel2 in it_data[20] and "(S)" in it_data[1] and "WEST" in it_data[-1]:
                                    replace_var(f'xx-S-WS_{indexFBD}-2', f'{twesel2}-S-WS')

                                if twesel2 in it_data[20] and "(T)" in it_data[1] and "EAST" in it_data[-1]:
                                    replace_var(f'xx-T-ES_{indexFBD}-2', f'{twesel2}-T-ES')
                                if twesel2 in it_data[20] and (
                                        "(E)" in it_data[1] or "(CF)" in it_data[1]) and "EAST" in it_data[-1]:
                                    replace_var(f'xx-E-ES_{indexFBD}-2', f'{twesel2}-E-ES')
                                if twesel2 in it_data[20] and "(S)" in it_data[1] and "EAST" in it_data[-1]:
                                    replace_var(f'xx-S-ES_{indexFBD}-2', f'{twesel2}-S-ES')

                        index_elas = 1
                        index_wlas = 1
                        for it_data in IT2:
                            if twesel1 in it_data[9] and "WEST" in it_data[-1]:
                                replace_var(f'xx-T-WLAS_{indexFBD}-{index_wlas}',
                                            f'{simp_number(it_data[6])}-T-WLAS')
                                index_wlas += 1
                            if twesel1 in it_data[9] and "EAST" in it_data[-1]:
                                replace_var(f'xx-T-ELAS_{indexFBD}-{index_elas}',
                                            f'{simp_number(it_data[6])}-T-ELAS')
                                index_elas += 1
                            if twesel2:
                                if twesel2 in it_data[9] and "WEST" in it_data[-1]:
                                    replace_var(f'xx-T-WLAS_{indexFBD}-{index_wlas}',
                                                f'{simp_number(it_data[6])}-T-WLAS')
                                    index_wlas += 1
                                if twesel2 in it_data[9] and "EAST" in it_data[-1]:
                                    replace_var(f'xx-T-ELAS_{indexFBD}-{index_elas}',
                                                f'{simp_number(it_data[6])}-T-ELAS')
                                    index_elas += 1

                        replace_var(f'xx-T-WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E-WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-S-WS_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-T-ES_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-E-ES_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-S-ES_{indexFBD}-1', f'TRUE')
                        replace_var(f'xx-T-WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E-WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-S-WS_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-T-ES_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-E-ES_{indexFBD}-2', f'TRUE')
                        replace_var(f'xx-S-ES_{indexFBD}-2', f'TRUE')

                        for index in range(1, 11):
                            replace_var(f'xx-T-WLAS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'xx-T-ELAS_{indexFBD}-{index}', f'TRUE')

                        replace_var(f'xx-TP_{indexFBD}-2', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        # vFC 67 EMERG ROUTE RELEASE
        def vFC_67_EMERG_ROUTE_RELEASE():
            varEnumerated = sorted(list(set([it[15] for it in IT1])))
            jumlahGenFBD = 5
            FBDtujuan = "vFC 67 EMERG ROUTE RELEASE"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/L/A/Xxx-RRLS_{indexFBD}', f'{data_var}-RRLS')
                        replace_var(f'J/JL/L/A/Xxx-RRLS-TE_{indexFBD}', f'{data_var}-RRLS-TE')
                        replace_var(f'J/JL/Lxx-RRLSPB-CTRL_{indexFBD}', f'{data_var}-RRLSPB-CTRL')

                        index_t = 1
                        index_e = 1
                        index_s = 1
                        arah = ""
                        for it in IT1:
                            if data_var in it[15]:
                                if "EAST" in it[-1]:
                                    arah = "E"
                                else:
                                    arah = "W"
                                if it[27]:
                                    track = it[20].split(" ")[-2]
                                else:
                                    track = it[20].split(" ")[-1]

                                if track.endswith("T"):
                                    track = track[:-1]
                                if "(T)" in it[1]:
                                    replace_var(f'xx-T-ES/WS_{indexFBD}', f'{track}-T-{arah}S')
                                    replace_var(f'J/JL/Lxx-T-AS_{indexFBD}-{index_t}', f'{it[2]}-T-AS')
                                    replace_var(f'J/JLxx-xx-T-REQ_{indexFBD}-{index_t}', f'{it[2]}-{simp(it[15])}-T-REQ')
                                    index_t += 1
                                if "(E)" in it[1] or "(CF)" in it[1]:
                                    cf = ""
                                    if "(CF)" in it[1]:
                                        cf = "-CF"
                                    replace_var(f'xx-E-ES/WS_{indexFBD}', f'{track}-E-{arah}S')
                                    replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index_e}', f'{it[2]}-E-AS')
                                    replace_var(f'J/JLxx-xx-E-REQ_{indexFBD}-{index_e}', f'{it[2]}-{simp(it[15])}{cf}-E-REQ')
                                    index_e += 1
                                if "(S)" in it[1]:
                                    replace_var(f'xx-S-ES/WS_{indexFBD}', f'{track}-S-{arah}S')
                                    replace_var(f'J/JL/Lxx-S-AS_{indexFBD}-{index_s}', f'{it[2]}-S-AS')
                                    replace_var(f'J/JLxx-xx-S-REQ_{indexFBD}-{index_s}', f'{it[2]}-{simp(it[15])}-S-REQ')
                                    index_s += 1

                        if data_var.startswith("A"):
                            replace_var(f'xx-S-ES/WS_{indexFBD}', f'{data_var}-{arah}FLR-DO')

                        wesel = []
                        for it in IT1:
                            if data_var in it[15]:
                                if it[27]:
                                    track = it[20].replace("T", "").split(" ")[-2]
                                else:
                                    track = it[20].replace("T", "").split(" ")[-1]
                                for w_r in it[18].split(" "):
                                    for w in pm:
                                        if (track in w[1] or track in w[2]) and w[0].replace("W", "") == w_r.replace("-R", "").replace("-N", ""):
                                            wesel.append(w_r)
                        wesel = sorted(list(set(wesel)))
                        index_wesel = 1
                        for w in wesel:
                            if not (f"{w.replace('-R','').replace('-N','')}-R" in ' '.join(wesel) and f"{w.replace('-R','').replace('-N','')}-N" in ' '.join(wesel)):
                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index_wesel}', f'W{w}WZ')
                                index_wesel += 1

                        for index in range(1, 16):
                            replace_var(f'xx-T-ES/WS_{indexFBD}', f'TRUE')
                            replace_var(f'J/JL/Lxx-T-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JLxx-xx-T-REQ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-E-ES/WS_{indexFBD}', f'TRUE')
                            replace_var(f'J/JL/Lxx-E-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JLxx-xx-E-REQ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'xx-S-ES/WS_{indexFBD}', f'TRUE')
                            replace_var(f'J/JL/Lxx-S-AS_{indexFBD}-{index}', f'TRUE')
                            replace_var(f'J/JLxx-xx-S-REQ_{indexFBD}-{index}', f'FALSE')
                            replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'TRUE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

            varEnumerated = sorted(list(set([it[2] for it in IT1 if "(T)" not in it[1] and "(S)" not in it[1] and not it[15].startswith("A")])))
            jumlahGenFBD = 5
            FBDtujuan = "vFC 67 EMERG ROUTE RELEASE (SINYAL MASUK)"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'J/JL/L/A/Xxx-RRLS_{indexFBD}', f'{data_var}-RRLS')
                        replace_var(f'J/JL/L/A/Xxx-RRLS-TE_{indexFBD}', f'{data_var}-RRLS-TE')
                        replace_var(f'J/JL/Lxx-RRLSPB-CTRL_{indexFBD}', f'{data_var}-RRLSPB-CTRL')
                        arah = ""
                        for it in IT1:
                            if data_var in it[2]:
                                if "EAST" in it[-1]:
                                    arah = "E"
                                    break
                                else:
                                    arah = "W"
                                    break
                        replace_var(f'Axx-E/WFLZR-DI_{indexFBD}', f'{data_var.replace("J", "A")}-{arah}FLZR-DI')
                        replace_var(f'Axx-E/WS_{indexFBD}', f'{data_var.replace("J", "A")}-{arah}S')

                        index = 1
                        for it in IT1:
                            if ("(E)" in it[1] or "(CF)" in it[1]) and data_var == it[2]:
                                cf = ""
                                if "(CF)" in it[1]:
                                    cf = "-CF"
                                replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'{it[2]}-{simp(it[15])}{cf}-RS')
                                index += 1

                        for index in range(1, 16):
                            replace_var(f'J/JL/Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC14 Emerg RP Release"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC14 Emerg RP Release"

        vFC_66_EMERG_POINT_RELEASE()
        vFC_67_EMERG_ROUTE_RELEASE()

        ################################## nV FC16 LEVEL CROSSING ################################
        def nv_fc16_level_crossing(self, IT1, IT2, referensiCSV, directorySimpan, PM, jpldata):
            def nfc87_lx_nv():
                varEnumerated = jpldata
                jumlahGenFBD = 5
                FBDtujuan = "nFC87 LX NV"
                for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                    dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                    def replace_var(varAwal, varBaru):
                        dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                    for indexFBD in range(jumlahGenFBD):
                        try:
                            data_var = varEnumerated[indexFBD + indexCSV]
                            indexFBD += 1

                            jpl_dir = data_var[0]
                            jpl_name = data_var[0].split("-")[0]
                            jpl_track = data_var[1]
                            jpl_wesel = data_var[2]
                            jpl_arah = "EAST" if data_var[0].split("-")[1].startswith("E") else "WEST"

                            replace_var(f'JPLxx-W/Exx-L_{indexFBD}', f'JPL{jpl_dir}-L')
                            replace_var(f'JPLxx-W/Exx-ON_{indexFBD}', f'JPL{jpl_dir}-ON')
                            replace_var(f'JPLxx-W/Exx-START_{indexFBD}', f'JPL{jpl_dir}-START')
                            replace_var(f'JPLxx-W/Exx-ACK_{indexFBD}', f'JPL{jpl_dir}-ACK')
                            replace_var(f'JPLxx-W/Exx-ACCNV_{indexFBD}', f'JPL{jpl_dir}-ACCNV')

                            replace_var(f'JPLxx-PB-DI_{indexFBD}', f'JPL{jpl_name}-PB-DI')
                            replace_var(f'JPLxx-PB-ERR_{indexFBD}', f'JPL{jpl_name}-ERR')
                            replace_var(f'JPLxx-ACK-DI_{indexFBD}', f'JPL{jpl_name}-ACK-DI')

                            index_subroute = 1
                            if "OL" not in jpl_dir:
                                for it in IT1:
                                    if it[-1] == jpl_arah and "(T)" in it[1] and f'{jpl_track}T' in it[20].split(" "):
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}',
                                                    f'{jpl_track}-T-{data_var[0].split("-")[1][0]}S')
                                        index_subroute += 1
                                        break
                                for it in IT1:
                                    if it[-1] == jpl_arah and ("(E)" in it[1] or "(CF)" in it[1]) and f'{jpl_track}T' in \
                                            it[20].split(" "):
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}',
                                                    f'{jpl_track}-E-{data_var[0].split("-")[1][0]}S')
                                        index_subroute += 1
                                        break
                                for it in IT1:
                                    if it[-1] == jpl_arah and "(T)" in it[1] and f'{jpl_track}T' in it[20].split(" "):
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}',
                                                    f'{jpl_track}-S-{data_var[0].split("-")[1][0]}S')
                                        index_subroute += 1
                                        break


                            else:
                                for it in IT2:
                                    if it[-1] == jpl_arah and f'{jpl_track}T' in it[9].split(" ") and jpl_wesel in it[
                                        7]:
                                        replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index_subroute}',
                                                    f'{simp_number(it[6])}-T-{data_var[0].split("-")[1][0]}LAS')
                                        index_subroute += 1

                            for it in IT1:
                                if it[-1] == jpl_arah and "(T)" in it[1] and f'{jpl_track}T' in it[20].split(
                                        " ") and jpl_wesel in it[18] and "-R" not in it[18]:
                                    replace_var(f'xx-TP_{indexFBD}', f'{jpl_track}-TP')
                                    replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'{it[2]}-F-RS')
                                    replace_var(f'J/JL/Lxx-xx-P_{indexFBD}', f'{it[2]}-{simp(it[15])}-P')

                            if jpl_wesel:
                                for i, j in enumerate(jpl_wesel.split(" ")):
                                    replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{i + 1}', f'{j}WZ')

                            index_rs = 1
                            index_srs = 1
                            for it in IT1:
                                if it[-1] == jpl_arah and ("(E)" in it[1] or "(CF)" in it[1]) and f'{jpl_track}T' in it[
                                    20].split(" ") and jpl_wesel in it[18] and "OL" not in jpl_dir:
                                    replace_var(f'J/JL-xx-RS_{indexFBD}-{index_rs}', f'{it[2]}-{simp(it[15])}-RS')
                                    replace_var(f'J/JLxx-ER-DO_{indexFBD}-{index_rs}', f'{it[2]}-ER-DO')
                                    index_rs += 1
                                if it[-1] == jpl_arah and "(S)" in it[1] and f'{jpl_track}T' in it[20].split(
                                        " ") and jpl_wesel in it[18] and "OL" not in jpl_dir:
                                    replace_var(f'Lxx-xx-RS_{indexFBD}-{index_srs}', f'{it[2]}-{simp(it[15])}-RS')
                                    index_srs += 1

                            index_start = 1
                            for i, j in enumerate(jpldata):
                                if j[0].split("-")[0] == jpl_name and j[0] != jpl_dir:
                                    replace_var(f'JPLxx-E/Wxx-START_{indexFBD}-{index_start}', f'{j[0]}-START')
                                    index_start += 1

                            for index in range(1, 50):
                                if "OL" in jpl_dir:
                                    replace_var(f'J/JL-xx-RS_{indexFBD}-{index}', f'TRUE')
                                    replace_var(f'Lxx-xx-RS_{indexFBD}-{index}', f'TRUE')
                                replace_var(f'J/JL-xx-RS_{indexFBD}-{index}', f'FALSE')
                                replace_var(f'Lxx-xx-RS_{indexFBD}-{index}', f'FALSE')
                                replace_var(f'J/JLxx-ER-DO_{indexFBD}-{index}', f'FALSE')
                                replace_var(f'JPLxx-E/Wxx-START_{indexFBD}-{index}', f'FALSE')
                                replace_var(f'Wxx-NWZ/RWZ_{indexFBD}-{index}', f'TRUE')
                                replace_var(f'xx-E/T/S-ES/WS_{indexFBD}-{index}', f'TRUE')

                            replace_var(f'xx-TP_{indexFBD}', f'FALSE')
                            replace_var(f'J/JL/Lxx-F-RS_{indexFBD}', f'FALSE')
                            replace_var(f'JPLxx-W/Exx-ACCNV_{indexFBD}', f'FALSE')
                            replace_var(f'J/JL/Lxx-xx-P_{indexFBD}', f'FALSE')

                        except Exception as e:
                            print(f"{FBDtujuan} -> {e}" if str(
                                e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                            break
                        finally:
                            pass

                    dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                                   index=False)

            def nfc93_lx_pbe():
                alljpl = sorted(list(set([j[0].split("-")[0] for j in jpldata])))

                FBDtujuan = "nFC93 LX PBE"
                for index, jpl in enumerate(alljpl):
                    dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")
                    index += 1

                    def replace_var(varAwal, varBaru):
                        dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                    replace_var(f'JPLxx-PB-ERR_1', f'JPL{jpl}-PB-ERR')
                    replace_var(f'JPLxx-PBE_1', f'JPL{jpl}-PBE')
                    replace_var(f'JPLxx-PBE-F_1', f'JPL{jpl}-PBE-F')
                    replace_var(f'JPLxx-PBE-DO_1', f'JPL{jpl}-PBE-DO')
                    replace_var(f'JPLxx-PB-DI_1', f'JPL{jpl}-PB-DI')
                    replace_var(f'JPLxx-AA-F', f'JPL{jpl}-AA-F')

                    ind_jpl = sorted(list(set([j[0] for j in jpldata if j[0].split("-")[0] == jpl])))

                    index_start = 1
                    for direction in ind_jpl:
                        replace_var(f'JPLxx-E/Wxx-START_{index}-{index_start}', f'JPL{direction}-START')
                        replace_var(f'JPLxx-E/Wxx-L_{index}-{index_start}', f'JPL{direction}-L')
                        replace_var(f'JPLxx-E/Wxx-ACCNV_{index}-{index_start}', f'JPL{direction}-ACCNV')
                        index_start += 1

                    for ind in range(1, 50):
                        replace_var(f'JPLxx-E/Wxx-START_{index}-{ind}', f'FALSE')
                        replace_var(f'JPLxx-E/Wxx-L_{index}-{ind}', f'FALSE')
                        replace_var(f'JPLxx-E/Wxx-ACCNV_{index}-{ind}', f'FALSE')

                    dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {jpl}.csv", index=False)
                print(f'{FBDtujuan} -> Done..')

            directorySimpan = directorySimpan + "\\Non Vital\\nV FC16 LEVEL CROSSING"
            if not os.path.exists(directorySimpan):
                os.makedirs(directorySimpan)

            referensiCSV = referensiCSV + "\\Non Vital\\nV FC16 LEVEL CROSSING"

            nfc87_lx_nv()
            nfc93_lx_pbe()

    ################################## nV FC16 LEVEL CROSSING ################################
    def v_fc18_level_crossing(self, IT1, IT2, referensiCSV, directorySimpan, PM, jpldata):
        def vfc_69():
            alljpl = sorted(list(set([j[0].split("-")[0] for j in jpldata])))

            FBDtujuan = "vFC 69 VITAL LX WOUT CONTROLLER"
            for index, jpl in enumerate(alljpl):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")
                jpl_name = alljpl[index]
                index += 1

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                ind_jpl = sorted(list(set([j[0] for j in jpldata if j[0].split("-")[0] == jpl and "OL" not in j[0]])))
                ind_jpl_ol = sorted(list(set([j[0] for j in jpldata if j[0].split("-")[0] == jpl and "OL" in j[0]])))

                replace_var(f'JPLxx-BUZZ-DO', f'JPL{jpl_name}-BUZZ-DO')

                index_start = 1
                for direction in ind_jpl:
                    arah = direction.split("-")[1][0]
                    jalur = direction.split("-")[1][-1]
                    replace_var(f'JPLxx-E/Wxx-L_{index_start}', f'JPL{direction}-L')
                    replace_var(f'JPLxx-E/Wxx-ACCNV_{index_start}', f'JPL{direction}-ACCNV')
                    replace_var(f'JPLxx-E/WAR-DO_{index_start}', f'JPL{arah}AR{jalur}-DO')
                    index_start += 1

                index_start = 1
                for direction in ind_jpl_ol:
                    arah = direction.split("-")[1][0]
                    jalur = direction.split("-")[1][-1]
                    replace_var(f'JPLxx-E/WOLxx-L_{index_start}', f'JPL{direction}-L')
                    replace_var(f'JPLxx-E/WOLxx-ACCNV_{index_start}', f'JPL{direction}-ACCNV')
                    replace_var(f'JPLxx-E/WAR-DO_{index_start}', f'JPL{arah}AR{jalur}-DO')
                    index_start += 1

                for ind in range(1, 50):
                    replace_var(f'JPLxx-E/Wxx-L_{ind}', f'FALSE')
                    replace_var(f'JPLxx-E/Wxx-ACCNV_{ind}', f'FALSE')
                    replace_var(f'JPLxx-E/WOLxx-L_{ind}', f'FALSE')
                    replace_var(f'JPLxx-E/WOLxx-ACCNV_{ind}', f'FALSE')
                    replace_var(f'JPLxx-E/WAR-DO_{ind}', f'HAPUS VARIABLE')

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {jpl}.csv", index=False)
            print(f'{FBDtujuan} -> Done..')

        directorySimpan = directorySimpan + "\\Vital\\v FC18 Level Crossing"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC18 Level Crossing"

        vfc_69()

    ################################ v FC19 Key Lock Point #############################
    def v_fc19_Key_Lock_Point(self, IT1, IT2, referensiCSV, directorySimpan, pm):
        # V FC9 SIGNAL- vFC 61 S MASUK
        def vFC_68_DERAILEUR():
            varEnumerated = [d[0] for d in pm if d[0].startswith("D")]
            jumlahGenFBD = 10
            FBDtujuan = "vFC 68 DERAILEUR"
            for indexCSV in range(0, len(varEnumerated), jumlahGenFBD):
                dfLogic = pd.read_csv(referensiCSV + f"\\{FBDtujuan}.csv")

                def replace_var(varAwal, varBaru):
                    dfLogic['New Name'] = dfLogic['New Name'].replace({varAwal: varBaru})

                for indexFBD in range(jumlahGenFBD):
                    try:
                        data_var = varEnumerated[indexFBD + indexCSV]
                        indexFBD += 1

                        replace_var(f'Dxx-REL-REQ_{indexFBD}', f'{data_var}-REL-REQ')
                        replace_var(f'Dxx-NKR-DI_{indexFBD}', f'{data_var}-NKR-DI')
                        replace_var(f'Dxx-RKR-DI_{indexFBD}', f'{data_var}-RKR-DI')
                        replace_var(f'Dxx-NPR-DO_{indexFBD}', f'{data_var}-NPR-DO')
                        replace_var(f'Dxx-NP_{indexFBD}', f'{data_var}-NP')
                        replace_var(f'Dxx-RP_{indexFBD}', f'{data_var}-RP')

                    except Exception as e:
                        print(f"{FBDtujuan} -> {e}" if str(e) != "list index out of range" else f'{FBDtujuan} -> Done..')
                        break
                    finally:
                        pass

                dfLogic.to_csv(directorySimpan + f"\\{FBDtujuan} {indexCSV}-{indexCSV + jumlahGenFBD}.csv",
                               index=False)

        directorySimpan = directorySimpan + "\\Vital\\v FC19 Key Lock Point"
        if not os.path.exists(directorySimpan):
            os.makedirs(directorySimpan)

        referensiCSV = referensiCSV + "\\Vital\\v FC19 Key Lock Point"

        vFC_68_DERAILEUR()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

"""
########### cheat note ########

1. add 2 list
data1 = [1, 2]
data2 = [3,4]
data = data1 + data2
result:
data = [1,2,3,4]

or can use append
data = data1.append(3)
data = data1.append(4)
result:
data = [1,2,3,4]

other use of append
data = data1.append(data2)
result:
data = [1,2,[3,4]]

2. convert string to list
data = "ABCD"
data = map(str, data)
resutl:
data = ['A', 'B', 'C', 'D']

data = TES SATU DUA
data = data.split(" ")
result:
data = ['TES', 'SATU', 'DUA']

3. filter unique value of list
data = [1,1,2,3,1]
data = list(set(data))
result:
data = [1,2,3]

4. join all value on list and convert to text
data = [1,2,3]
data = ' '.join(data)

5. filter data kosong
data = [1,2,3,,2,1,'']
list(filter(None, data))

data = [1,2,3,2,1]

6. flaten list
data = [1,2,[3,4]]
data = sum(list(map(list,data)),[])

data = [1,2,3,4]

***************************
Shift+Tab "tabs backwards
***************************
"""""