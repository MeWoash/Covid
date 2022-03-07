import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdt
from create_csv_file import *
from datetime import datetime
import datetime as dt
from scipy import interpolate
import numpy as np

#create_csv()
df=load_DF()


class Graph_settings:
    """
    Przechowuje dane do narysowania
    """
    liczba_mieszkancow={'cały kraj':38354173,
                        'mazowieckie':5428031,
                        'śląskie':4508078,
                        'wielkopolskie':3500361,
                        'małopolskie':3413931,
                        'dolnośląskie':2898525,
                        'łódzkie':2448713,
                        'pomorskie':2346717,
                        'lubelskie':2103342,
                        'podkarpackie':2125901,
                        'kujawsko-pomorskie':2069273,
                        'zachodniopomorskie':1693219,
                        'warmińsko-mazurskie':1420514,
                        'świętokrzyskie':1230044,
                        'podlaskie':1176576,
                        'lubuskie':1010177,
                        'opolskie':980771}#GUS 2020-10-20

    grid=True
    legend=True
    przelicznik=True
    ekstrapolacja=False
    liczba_dni="3"
    added = []
    def __init__(self, data_b, data_e, wojewodztwo, temat,metoda):
        try:
            self.data_b = datetime.strptime(data_b, "%d.%m.%Y")
        except:
            self.data_b = min(df['data'])
        try:
            self.data_e = datetime.strptime(data_e, "%d.%m.%Y")
        except:
            self.data_e = max(df['data'])

        if self.data_b<min(df['data']):
            self.data_b=min(df['data'])

        if self.data_e>max(df['data']):
            self.data_e=max(df['data'])

        self.metoda = metoda.lower()
        self.wojewodztwo = wojewodztwo.lower()
        self.temat = temat.lower()

    @staticmethod
    def draw_all(graph):
        """
        Rysuje wszystkie przechowywane dane
        """
        graph.axes.clear()
        if len(Graph_settings.added)!=0:
            Graph_settings.axis_settings(graph)
        graph.draw()

    @staticmethod
    def axis_settings(graph):
        for el in Graph_settings.added:
            el.draw(graph.axes)

        graph.axes.grid(Graph_settings.grid)
        if Graph_settings.legend:
            graph.axes.legend()

        #OS X
        graph.axes.tick_params(axis="x", which="both", rotation=60)
        graph.axes.xaxis.set_major_locator(mdt.AutoDateLocator(minticks=20))    #mdt.MonthLocator()
        graph.axes.xaxis.set_major_formatter(mdt.DateFormatter('%d.%m.%y'))
        graph.axes.xaxis.set_minor_locator(mdt.AutoDateLocator(minticks=20))    #mdt.DayLocator([5,10,15,20,25])
        graph.axes.xaxis.set_minor_formatter(ticker.NullFormatter())
        #OS Y
        graph.axes.set_ylim(ymin=0)
        graph.axes.yaxis.set_major_locator(ticker.LinearLocator(20))

    def draw(self,ax):
        """
        Rysuje jeden wykres
        """

        #Filtruje wg wojewodztwa
        tmp=df.loc[(df['wojewodztwo'] == self.wojewodztwo)]

        # Odrzuca inne kategorie
        tmp = tmp[['data', self.temat]]

        if self.metoda=="średnia tygodniowa":
            self.calculate_avrg(tmp)

        #filtruje wg daty
        tmp = tmp.loc[(tmp['data'] >= self.data_b) & (tmp['data'] <= self.data_e)]

        if self.przelicznik==2:
            self.per_100_converter(tmp)

        x = tmp['data']
        y = tmp[self.temat]
        p=ax.plot(x, y,label=self.temat + " : " + self.wojewodztwo)

        try:
            if self.ekstrapolacja:
                x,y=self.extrapolate(x,y)
                ax.plot(x, y,':',color=p[0].get_color())
        except BaseException as e:
            print(e)


    def extrapolate(self,x,y):
        try:
            maximum=max(x)
            x=list(map(lambda x: datetime.timestamp(x),x))
            y.fillna(1,inplace=True)
            f=interpolate.interp1d(x,y,kind='cubic',fill_value="extrapolate")
            forward_x=[datetime.timestamp(maximum+dt.timedelta(days=i)) for i in range(int(Graph_settings.liczba_dni)+1)]
            x=[datetime.fromtimestamp(i) for i in forward_x]
            y=f(forward_x)
            return x,y
        except BaseException as e:
            print(e)
            return np.nan,np.nan

    def calculate_avrg(self,dataframe):
        """
        Oblicza średnią tygodniową
        """
        try:
            dataframe[self.temat]=dataframe.rolling(7).mean()
        except BaseException as e:
            print(e)

    def per_100_converter(self,dataframe):
        """
        Przelicza dane na 100tys. mieszkańców
        """
        dataframe[self.temat]=dataframe[self.temat].apply(lambda x: (x/Graph_settings.liczba_mieszkancow[self.wojewodztwo])*100000)