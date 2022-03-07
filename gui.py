import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication,QWidget, QLabel,QComboBox, QHBoxLayout, QVBoxLayout,\
    QLineEdit,QCheckBox,QGroupBox,QTabWidget,QFrame,QColorDialog,QPushButton,QScrollArea
from PyQt5.QtGui import QIcon, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from Graphs import *


class MplCanvas(FigureCanvasQTAgg):
    """
    Uchwyt matplotlib
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(1,1,1)
        super().__init__(self.fig)

class AddItemWidget(QGroupBox):
    """
    Widget dodawania wykresów
    """
    def __init__(self,parent):
        self.bar=parent.bar
        super(AddItemWidget, self).__init__()
        self.Windows_Layout()

    def Windows_Layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Początek:"))
        self.date_b = QLineEdit()
        self.date_b.setPlaceholderText("DD.MM.YYYY")
        self.date_b.setText(min(df['data']).strftime("%d.%m.%Y"))
        layout.addWidget(self.date_b)

        layout.addWidget(QLabel("Koniec:"))
        self.date_e = QLineEdit()
        self.date_e.setPlaceholderText("DD.MM.YYYY")
        self.date_e.setText(max(df['data']).strftime("%d.%m.%Y"))
        layout.addWidget(self.date_e)

        self.CB_wojewodztwa = QComboBox()
        wojewodztwa_nazwy = ["Cały kraj", 'Dolnośląskie', 'Kujawsko-pomorskie', 'Lubelskie',
                                  'Lubuskie', 'Łódzkie', 'Mazowieckie', 'Małopolskie',
                                  'Opolskie', 'Podkarpackie', 'Podlaskie',
                                  'Pomorskie', 'Śląskie', 'Świętokrzyskie', 'Warmińsko-mazurskie', 'Wielkopolskie',
                                  'Zachodniopomorskie']
        self.CB_wojewodztwa.addItems(wojewodztwa_nazwy)
        layout.addWidget(QLabel("Województwo"))
        layout.addWidget(self.CB_wojewodztwa)

        temat_nazwy=["Nowe przypadki","Zgony","Ozdrowieńcy","Kwarantanna","Testy"]
        layout.addWidget(QLabel("Temat"))
        self.CB_temat = QComboBox()
        self.CB_temat.addItems(temat_nazwy)
        layout.addWidget(self.CB_temat)

        layout.addWidget(QLabel("Metoda"))
        self.CB_metoda = QComboBox()
        metody = ["Średnia Tygodniowa","Dzienna"]
        self.CB_metoda.addItems(metody)
        layout.addWidget((self.CB_metoda))

        self.dodaj = QPushButton("Dodaj")
        self.dodaj.clicked.connect(self.add)
        layout.addWidget(self.dodaj)

    def add(self):
        data_b = self.date_b.text()
        data_e = self.date_e.text()
        wojewodztwo = self.CB_wojewodztwa.currentText()
        temat = self.CB_temat.currentText()
        metoda = self.CB_metoda.currentText()

        tmp=Graph_settings(data_b,data_e,wojewodztwo,temat,metoda)
        Graph_settings.added.append(tmp)
        self.bar.put_widget(tmp)

class SingleItemWidget(QGroupBox):
    """
    Pojedyncza dana listy dodanych wykresów
    """
    def __init__(self,obj):
        super(SingleItemWidget, self).__init__()
        #Dana, ktorej wyglad jest przedstawiany
        self.obj=obj
        self.Windows_Layout()

    def Windows_Layout(self):
        """
        Wyglad widgetu
        """
        font=QFont('Arial', 8)
        vbox=QVBoxLayout()
        self.setLayout(vbox)
        hbox1=QHBoxLayout()
        hbox2=QHBoxLayout()
        hbox3=QHBoxLayout()

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)

        lab1=QLabel(self.obj.data_b.strftime("%d.%m.%y") + "-" + self.obj.data_e.strftime("%d.%m.%y"))
        lab1.setFont(QFont('Arial', 11))
        hbox1.addWidget(lab1)
        lab2=QLabel(str(self.obj.temat).capitalize())
        lab2.setFont(font)
        hbox2.addWidget(lab2)

        lab2_1=QLabel(self.obj.metoda.capitalize())
        lab2_1.setFont(font)
        hbox2.addWidget(lab2_1)

        lab3=QLabel(str(self.obj.wojewodztwo).capitalize())
        lab3.setFont(font)
        hbox3.addWidget(lab3)


        self.delete_btn = QPushButton("X")
        btn_font=QFont("Arial",10)
        btn_font.setBold(True)
        self.delete_btn.setFont(btn_font)
        self.delete_btn.setMaximumSize(25, 25)
        self.delete_btn.clicked.connect(self.btn_clicked)
        hbox1.addStretch(20)
        hbox1.addWidget(self.delete_btn)
        vbox.addStretch(100)

    def btn_clicked(self):
        Graph_settings.added.remove(self.obj)
        ItemsStatusWidget.ItemsList.remove(self)
        self.deleteLater()

class ItemsStatusWidget(QScrollArea):
    """
    Lista dodanych wykresów
    """
    ItemsList = []
    def __init__(self):
        super(ItemsStatusWidget, self).__init__()

        tmp=QGroupBox()
        self.layout = QVBoxLayout()
        tmp.setLayout(self.layout)
        self.setWidget(tmp)
        self.setWidgetResizable(True)
        self.layout.addStretch(20)
        self.setMinimumWidth(250)

    def put_widget(self, obj):
        tmp=SingleItemWidget(obj)
        ItemsStatusWidget.ItemsList.append(tmp)
        self.layout.insertWidget(0,tmp)


class MainWindow(QWidget):
    """
    Podstawowe okno
    """
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Arial",10))
        self.Windows_Layout()

    def Windows_Layout(self):
        """
        Wygląd GUI
        """
        self.setWindowTitle("Covid w Polsce")
        self.setWindowIcon(QIcon("./IMG/coronavirus.png"))  # https://www.flaticon.com/authors/kosonicon
        self.setMinimumSize(1000,600)
        #MATLAB GRAPH
        self.graph = MplCanvas(width=5, height=4, dpi=100)
        #TAB1
        tab1 = QFrame()
        vbox_tab1 = QVBoxLayout()
        tab1.setLayout(vbox_tab1)
        self.bar = ItemsStatusWidget()
        add = AddItemWidget(self)
        vbox_tab1.addWidget(QLabel("Wybierz:"))
        vbox_tab1.addWidget(add)
        vbox_tab1.addWidget(self.bar)
        hbox = QHBoxLayout()
        vbox_tab1.addLayout(hbox)
        self.reset = QPushButton("Reset")
        self.reset.clicked.connect(self.reset_btn)
        hbox.addWidget(self.reset)
        self.rysuj = QPushButton("Rysuj")
        self.rysuj.clicked.connect(self.btn_rysuj)
        hbox.addWidget(self.rysuj)

        #TAB2
        tab2 = QFrame()
        vbox_tab2 = QVBoxLayout()
        tab2.setLayout(vbox_tab2)

        tab2_settings_grp=QGroupBox("Ustawienia wykresu")
        tab2_settings_grp_vbox=QVBoxLayout()
        tab2_settings_grp.setLayout(tab2_settings_grp_vbox)
        tab2_metoda_grp=QGroupBox("Ustawienia liczenia")
        tab2_metoda_grp_vbox=QVBoxLayout()
        tab2_metoda_grp.setLayout(tab2_metoda_grp_vbox)
        vbox_tab2.addWidget(tab2_settings_grp)
        vbox_tab2.addWidget(tab2_metoda_grp)
        vbox_tab2.addStretch(10)

        self.grid = QCheckBox()
        self.grid.setText("Siatka")
        self.grid.setCheckState(2)
        tab2_settings_grp_vbox.addWidget(self.grid)

        self.legenda = QCheckBox()
        self.legenda.setText("Legenda")
        self.legenda.setCheckState(2)
        tab2_settings_grp_vbox.addWidget(self.legenda)

        self.przelicznik = QCheckBox("Przelicznik na 100 tys. osób")
        self.przelicznik.setCheckState(2)
        tab2_metoda_grp_vbox.addWidget(self.przelicznik)
        self.ekstrapolacja = QCheckBox("Ekstrapolacja")
        self.ekstrapolacja.clicked.connect(self.btn_ekstrapolacja)
        tab2_metoda_grp_vbox.addWidget(self.ekstrapolacja)
        self.liczba_dni=QLineEdit()
        self.liczba_dni.setText("3")
        self.liczba_dni.setEnabled(self.ekstrapolacja.checkState())
        tab2_metoda_grp_vbox.addWidget(QLabel("Liczba dni"))
        tab2_metoda_grp_vbox.addWidget(self.liczba_dni)

        tab = QTabWidget()
        tab.addTab(tab1, "Dodaj")
        tab.addTab(tab2, "Opcje")

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        hbox.addWidget(tab,1)
        hbox.addStretch()
        hbox.addWidget(self.graph,20)

        self.setLayout(hbox)
        self.show()

    def btn_ekstrapolacja(self):
        self.liczba_dni.setEnabled(self.ekstrapolacja.checkState())

    def btn_rysuj(self):
        """
        Akcja przycisku Rysuj
        """
        Graph_settings.grid = self.grid.checkState()
        Graph_settings.legend = self.legenda.checkState()
        Graph_settings.przelicznik = self.przelicznik.checkState()
        Graph_settings.ekstrapolacja = self.ekstrapolacja.checkState()
        Graph_settings.liczba_dni = self.liczba_dni.text()
        Graph_settings.draw_all(self.graph)


    def reset_btn(self):
        """
        Akcja przycisku Reset
        """
        #print(ItemsStatusWidget.ItemsList)
        #print(Graph_settings.added)
        try:
            for i in ItemsStatusWidget.ItemsList:
                i.deleteLater()
            Graph_settings.added.clear()
            ItemsStatusWidget.ItemsList.clear()
        except BaseException as e:
            print(e)

