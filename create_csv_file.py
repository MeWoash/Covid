import os
import pandas as pd
import datetime as dt
import sys

def load_DF():
    """
    Zwraca Dataframe z pliku combined_data.csv, tworzy obiekty typu datetime
    """
    if not os.path.isfile("./Dane/combined_data.csv"):
        create_csv()
    tmp=pd.read_csv("./Dane/combined_data.csv",encoding="UTF-8",delimiter=";")
    tmp['data'] = tmp["data"].apply(lambda str: dt.datetime.strptime(str, "%Y-%m-%d"))
    return tmp


#Dane podawane przez MZ czesto zmienialy swoj format, stad trzeba bylo je podzielic na grupy i masowo dodawac do Data Frame
def create_csv():
    """
    Tworzy 'combined_data.csv', ktory jest sklejeniem wielu plikow csv podanych przez Ministerstwo Zdrowia.
    Uzupelnia niektore brakujace wartosci.
    """
    if not os.path.isdir("./Dane/1"):
        raise NotADirectoryError("Brak folderu 1 z danymi")
    elif not os.path.isdir("./Dane/2"):
        raise NotADirectoryError("Brak folderu 2 z danymi")
    combined_data=pd.DataFrame()

    #Wczytywanie danych z folderu 1
    os.chdir("./Dane/1")
    try:
        df=pd.read_csv(*os.listdir(),encoding='UTF-8',delimiter=";")
    except BaseException as e:
        print(e)
        exit(-1)

    combined_data=df
    combined_data = combined_data.rename(columns={'Data':'data',
                            'Nowe przypadki':'nowe przypadki',
                            'Zgony':'zgony',
                            'Ozdrowieńcy (dzienna)':'ozdrowieńcy',
                            'Kwarantanna':'kwarantanna'})

    combined_data['data']=combined_data["data"].apply(lambda str:dt.datetime.strptime(str, "%d.%m.%Y"))
    combined_data=combined_data.rename(columns={"Unnamed: 0": "Dzien tygodnia"})
    combined_data['wojewodztwo']="cały kraj"

    os.chdir("./..")
    #Wczytywanie dnaych z folderu 2
    csv2=[file for file in os.listdir("./2") if file[-4:]==".csv"]
    os.chdir("./2")
    days={0:"poniedziałek",1:"wtorek",2:"środa",3:"czwartek",4:"piątek",5:"piątek",6:"sobota",7:"niedziela"}

    for plik in csv2:
        try:
            df=pd.read_csv(plik,encoding="UTF-8",delimiter=";")
        except BaseException as e:
            print(e)
            exit(-1)

        df=df.rename(columns={'stan_rekordu_na':'data',
                              'liczba_osob_objetych_kwarantanna':'kwarantanna',
                              'zgony':'zgony',
                              "liczba_przypadkow":"nowe przypadki",
                              "liczba_ozdrowiencow":"ozdrowieńcy",
                              "liczba_wykonanych_testow":"testy"})

        df.iloc[0,:1]='cały kraj'


        #Data podana w pliku dla tych danych bledna, prawdziwa jest ta z nazwy pliku
        df['data']=dt.datetime.strptime(plik[6:8]+"."+plik[4:6]+"."+plik[:4],"%d.%m.%Y")
        df['Dzien tygodnia'] = days[df['data'][0].weekday()]
        #Laczenie Data Frameow
        combined_data=combined_data.append(df)


    os.chdir("./..")

    to_del=['liczba_na_10_tys_mieszkancow', 'zgony_w_wyniku_covid_bez_chorob_wspolistniejacych',
            'zgony_w_wyniku_covid_i_chorob_wspolistniejacych','liczba_zlecen_poz','Aktywne przypadki','Ozdrowieńcy (suma)','Wszystkie przypadki kumulatywnie',
            'Wszystkie zgony kumulatywnie','Nadzór','teryt','liczba_pozostalych_testow','liczba_testow_z_wynikiem_negatywnym','liczba_testow_z_wynikiem_pozytywnym']
    combined_data.drop(columns=to_del,inplace=True)
    combined_data=combined_data.reset_index(drop=True)

    combined_data.to_csv("combined_data.csv",encoding="UTF-8",sep=";")
    print("Utworzono plik 'combined_data.csv'")
    os.chdir("./..")