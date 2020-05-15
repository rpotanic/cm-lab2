import sys
import math
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
import untitled
import RK_methods as rk
import pickle


class MainWindow(QtWidgets.QMainWindow, untitled.Ui_MainWindow):
    def __init__(self):
        global ax
        global axx
        super().__init__()
        self.setupUi(self)

        # инициализация фигуры и тулбара для графика
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # обработка нажатия кнопок
        self.button_go.clicked.connect(self.AddPlot)
        self.button_clear.clicked.connect(self.ClearPlot)
        self.tabs.activated.connect(self.LoadTab)

        # установка графика
        self.verticalLayout_2.addWidget(self.toolbar)
        self.verticalLayout_2.addWidget(self.canvas)
        axx = self.figure.add_subplot(122)
        plot = plt.xlabel(r'$u1$')
        plot = plt.ylabel(r'$u2$')
        plot = plt.title('Фазовый портрет')
        plot = plt.grid(True)
        plt.tight_layout()
        ax = self.figure.add_subplot(121)
        plot = plt.xlabel(r'$x$')
        plot = plt.ylabel(r'$u1, u2$')
        plot = plt.title('График')
        plot = plt.grid(True)
        plt.tight_layout()


    def LoadTab(self):
        table = self.load_obj("table_" + self.tabs.currentText())
        info = self.load_obj("info_" + self.tabs.currentText())
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(len(table['X']))
        self.tableWidget.verticalHeader().hide()
        for i in range(len(table['X'])):
            if i == 0:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(table['H'][i])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(table['X'][i])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(table['Y1'][i])))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(table['Y2'][i])))
            else:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(table['H'][i])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(table['X'][i])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(table['Y1'][i])))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(table['Y2'][i])))
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(table['W1'][i])))
                self.tableWidget.setItem(i, 6, QTableWidgetItem(str(table['W2'][i])))
                self.tableWidget.setItem(i, 7, QTableWidgetItem(str(table['W-V'][i])))
                self.tableWidget.setItem(i, 8, QTableWidgetItem(str(table['S'][i])))
                self.tableWidget.setItem(i, 9, QTableWidgetItem(str(table['deg_count'][i])))
                self.tableWidget.setItem(i, 10, QTableWidgetItem(str(table['inc_count'][i])))
                header = self.tableWidget.horizontalHeader()
                for i in range(0, 11, 1):
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        self.label_8.setText("Задача основная, вариант №7, метод = РК* (4 порядка)")
        self.label_7.setText(
                "x0 = " + str(table['X'][0]) + ", y10 = " + str(table['Y1'][0]) + ", y20 = " + str(table['Y2'][0]) + ", T = " + str(info['x1']) + ", h0 = " + str(table['H'][0]) + ", ε = " + str(info['eps']) + ", ε гр = " + str(info['eps_bord']))
        self.label_9.setText(
                "Nmax = " + str(info['n']) + ", ε min = " + str(info['eps'] / 32) + ", n = " + str(info['n'] - 1) + ", b-xn = " + str(info['x1'] - table['X'][info['n'] - 1]))
        self.label_10.setText("max|S| = " + str(info['max err est']) + " при х = " + str(info['X on max err est']))
        self.label_20.setText("min|S| = " + str(info['min err est']) + " при х = " + str(info['X on min err est']))
        self.label_11.setText("ум. шага = " + str(info['deg']) + ", ув. шага = " + str(info['inc']))
        self.label_12.setText(
                "max h = " + str(max(table['H'])) + " при х = " + str(table['X'][table['H'].index(max(table['H'])) + 1]))
        if table['H'].index(min(table['H'])) == (info['n'] - 1):
            self.label_21.setText(
                    "min h = " + str(min(table['H'])) + " при х = " + str(table['X'][table['H'].index(min(table['H']))]))
        else:
            self.label_21.setText("min h = " + str(min(table['H'])) + " при х = " + str(
                    table['X'][table['H'].index(min(table['H'])) + 1]))

    def ClearPlot(self): # функция очистки графика
        global ax
        global axx
        ax.clear()
        axx.clear()
        plt.sca(ax)
        plot = plt.xlabel(r'$x$')
        plot = plt.ylabel(r'$u1, u2$')
        plot = plt.title('График')
        plot = plt.grid(True)
        plt.sca(axx)
        plot = plt.xlabel(r'$u1$')
        plot = plt.ylabel(r'$u2$')
        plot = plt.title('Фазовый портрет')
        plot = plt.grid(True)
        self.canvas.draw()
        self.tableWidget.setRowCount(0)
        self.tabs.clear()

    def AddPlot(self): # функция добавления графика
        global ax
        global axx

        # получение флагов увеличения/уменьшения
        if self.check_not_inc.isChecked():
            check_not_inc = 0
        else:
            check_not_inc = 1

        if self.check_not_deg.isChecked():
            check_not_deg = 0
        else:
            check_not_deg = 1

        # получение параметров диффура
        param_a = np.float64(self.param_a.text())

        # получение начальных условий
        x0 = np.float64(self.start_value_x.text())

        # получение начального шага
        h = np.float64(self.start_step.text())

        # получение точности выхода за границу
        eps_bord = np.float64(self.eps_border.text())

        # получение контроля локальной погрешности
        eps = np.float64(self.control_error.text())

        # получение y10,y20
        y10 = np.float64(self.start_value_y1.text())
        y20 = np.float64(self.start_value_y2.text())

        # получение макс. числа шагов
        n = np.int(self.max_step.text())

        # получение конечного значения отрезка Х
        x1 = np.float64(self.finish_value.text())

        table, info = rk.rk4_for_system(self.f2, self.f3, x0, y10, y20, x1, h, n, param_a, eps_bord, check_not_inc, check_not_deg, eps)
        ax.plot(table['X'], table['Y1'], '*-', label='(1)L=' + str(param_a) + ', x0=' + str(x0) + ', y10 = ' + str(y10))
        ax.plot(table['X'], table['Y2'], '*-', label='(2)L=' + str(param_a) + ', x0=' + str(x0) + ', y20 = ' + str(y20))
        ax.legend()
        axx.plot(table['Y1'], table['Y2'], '-', label='L=' + str(param_a) + ', x0=' + str(x0) + ', y10 = ' + str(y10) + ', y20 = ' + str(y20))
        axx.legend()
        self.tabs.addItem("ml=" + str(param_a) + "x0=" + str(x0) + "y10=" + str(y10) + "y20=" + str(y20) + "eps=" + str(eps) + "eps_bord=" + str(eps_bord) + "h=" + str(h) + "n=" + str(n))
        self.save_obj(table, "table_ml=" + str(param_a) + "x0=" + str(x0) + "y10=" + str(y10) + "y20=" + str(y20) + "eps=" + str(eps) + "eps_bord=" + str(eps_bord) + "h=" + str(h) + "n=" + str(n))
        self.save_obj(info, "info_ml=" + str(param_a) + "x0=" + str(x0) + "y10=" + str(y10) + "y20=" + str(y20) + "eps=" + str(eps) + "eps_bord=" + str(eps_bord) + "h=" + str(h) + "n=" + str(n))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(len(table['X']))
        self.tableWidget.verticalHeader().hide()
        for i in range(len(table['X'])):
            if i == 0:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(h)))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(table['X'][i])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(table['Y1'][i])))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(table['Y2'][i])))
            else:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(table['H'][i])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(table['X'][i])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(table['Y1'][i])))
                self.tableWidget.setItem(i, 4, QTableWidgetItem(str(table['Y2'][i])))
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(table['W1'][i])))
                self.tableWidget.setItem(i, 6, QTableWidgetItem(str(table['W2'][i])))
                self.tableWidget.setItem(i, 7, QTableWidgetItem(str(table['W-V'][i])))
                self.tableWidget.setItem(i, 8, QTableWidgetItem(str(table['S'][i])))
                self.tableWidget.setItem(i, 9, QTableWidgetItem(str(table['deg_count'][i])))
                self.tableWidget.setItem(i, 10, QTableWidgetItem(str(table['inc_count'][i])))
                header = self.tableWidget.horizontalHeader()
                for i in range(0, 11, 1):
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            self.label_8.setText("Задача основная, вариант №7, метод = РК* (4 порядка)")
            self.label_7.setText("x0 = " + str(x0) + ", y10 = " + str(y10) + ", y20=" + str(y20) + ", T = " + str(x1) + ", h0 = " + str(h) + ", ε = " + str(eps) + ", ε гр = " + str(eps_bord))
            self.label_9.setText("Nmax = " + str(n) + ", ε min = " + str(eps/32) + ", n = " + str(info['n']-1) + ", b-xn = " + str(x1-table['X'][info['n']-1]))
            self.label_10.setText("max|S| = " + str(info['max err est']) + " при х = " + str(info['X on max err est']))
            self.label_20.setText("min|S| = " + str(info['min err est']) + " при х = " + str(info['X on min err est']))
            self.label_11.setText("ум. шага = " + str(info['deg']) + ", ув. шага = " + str(info['inc']))
            self.label_12.setText("max h = " + str(max(table['H'])) + " при х = " + str(table['X'][table['H'].index(max(table['H']))+1]))
            if table['H'].index(min(table['H'])) == (info['n']-1):
                self.label_21.setText("min h = " + str(min(table['H'])) + " при х = " + str(table['X'][table['H'].index(min(table['H']))]))
            else:
                self.label_21.setText("min h = " + str(min(table['H'])) + " при х = " + str(table['X'][table['H'].index(min(table['H']))+1]))
        self.canvas.draw()

    def GetTab(self): # функция получения информации из tabs
        item = self.tabs.currentText()
        return item

    def save_obj(self, obj, name):
        with open('obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name):
        with open('obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)


    # def f3(self, x, y1, y2, param_a):
    #     return ((-9.8)/param_a) * math.sin(y1)

    def f2(self, x, y1, y2, param_a):
        return y2

    #def f3(self, x, y1, y2, param_a):
     #   return 2 * param_a - 2 * x

    def f3(self, x, y1, y2, param_a):
        return 2 * (math.pow(param_a,-1) - x * math.pow(param_a, -2))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = MainWindow()
    main.show()

    sys.exit(app.exec_())