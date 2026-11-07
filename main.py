
# WSZYTSKIE ZADANIA ZALICZENIOWE Z DNIA 17.10.2026 ZNAJDUJĄ SIĘ W TYM PLIKU: 
# Ćwiczenie I i ćwiczenie II połączone w jedno
# Ćwiczenie III i ćwiczenie IV połączone w jedno

#------------------------------------------------------------------------------


# Ćwiczenie I – instalacja UV, stworzenie nowej aplikacji i definicja funkcji
# 1. Zainstaluj uv i stwórz nową aplikację. Zainstaluj bibliotekę requests.
# 2 W pliku main.py zdefiniuj funkcję pobierającą plik z podanego URL i  zapisującą pobrany plik na dysku o podanej nazwie. 
# 3. Upewnij się, że funkcja oczekuje dwa parametry: adres url do pobrania pliku oraz nazwę pliku do zapisywania na dysku.
# Jeśli nazwa pliku nie została podana, powinna domyślnie wynosić 'latest.txt'. URL z którego należy pobrać plik: https://oleksandr-fedoruk.com/sggw/podyplomowe/file

# Ćwiczenie II – dodanie obsługi wyjątków
# W aplikacji z poprzedniego ćwiczenia zdefiniuj klasę wyjątku dziedziczącą po Exception.
# Stwórz dwie klasy wyjątków dziedziczące po tej klasie – NotFoundError i AccessDeniedError.
# Dodaj obsługę kodów odpowiedzi serwera 404 i 403 by pojawienie się takich kodów rzucało odpowiedni wyjątek. 
# Adresy do testowania wyjątków: http://oleksandr-fedoruk.com/sggw/podyplomowe/404  http://oleksandr-fedoruk.com/sggw/podyplomowe/40


#Blad 403 (zabroniony)
class AccessDeniedError(Exception):
    """Brak dostępu (403)."""
    def __init__(self, odpowiedz):
        self.odpowiedz= odpowiedz
        super().__init__(f"brak dostepu: {odpowiedz.status_code}")

#Blad 404 (nie znaleziono)
class NotFoundError(Exception):
    """Nie znaleziono pliku (404)."""
    def __init__(self, odpowiedz):
        self.odpowiedz= odpowiedz
        super().__init__(f"nie znaleziono: {odpowiedz.status_code}")

import requests
import os
# terminal: uv init moj-projekt
# terminal uv add requests
def download_and_save(url='https://oleksandr-fedoruk.com/sggw/podyplomowe/file', name='latest.txt'): 
    r=requests.get(url)

    if r.status_code==404:
        raise NotFoundError(r)
    
    if r.status_code==403:
        raise AccessDeniedError(r)
        
    if r.status_code==200:
        my_file = os.path.dirname(os.path.abspath(__file__))
        my_path = os.path.join(my_file, name)
        with open(my_path, 'w') as f:
            f.write(r.text)
            print(f'Plik {name} został zapisany w folderze: {os.getcwd()}')
    else:
        print("Nie udalo się pobrac pliku, sprawdz URL. Kod: ",r.status_code)


if __name__ == "__main__":
    try:
        download_and_save()
        #download_and_save(url='http://oleksandr-fedoruk.com/sggw/podyplomowe/404')
        #download_and_save(url='http://oleksandr-fedoruk.com/sggw/podyplomowe/403')
    except NotFoundError as e:
        print(e)
    except AccessDeniedError as e:
        print(e)

# terminal: uv run python main.py

#---------------------------------------------------------------------------------------------------------------------------------------------------
# Ćwiczenie III – transformacja plików
# Przejrzyjmy się pobieranym przez nas plikom – są to pliki CSV, zawierające 8 kolumn z liczbami. Kolumna o indeksie 0 oznacza numer porządkowy.
# Niektóre wartości nie są wypełnione, zamiast nich są wpisane myślniki. 
# Napisz klasę która symuluje prosty proces ETL korzystając z generatorów:
# Wczytuje pobrany plik linijka po linijce
# Dla każdej linijki liczy sumę, średnią oraz zapsuje indeksy brakujących wartości (użyj list comprehension)
# Zapisuje dwa pliki CSV: values.csv z kolumnami: numer porządkowy, suma, średnia. 
#                        missing_values.csv z kolumnami: numer porządkowy oraz indeksami kolumn ze myślnikami zamiast wartości

# Ćwiczenie IV – dodanie dekoratorów
# Dodaj dekorator do logowania (printowania) czasu przed i po wywołaniu funkcji. 
# Opakuj funkcję przetwarzającą plik tym dekoratorem

import csv
from datetime import datetime
def execution_time(func):
    def wrapper(*args, **kwargs):
        start=datetime.now()
        print(f'czas rozpoczecai: {start}')
        result=func(*args, **kwargs)
        stop=datetime.now()
        print(f'czas zakonczenia: {stop}')
        print(f'Funkcja wykonala sie w ciagu {(stop - start).total_seconds():.4f} s.')
        return result
    return wrapper

class ETL:
    def __init__(self, name= 'latest.txt'):
        self.name=name

    @staticmethod
    def _is_missing(value):
        return value.strip() in  ('-', '')

    def _numbers(self, row): #tylko poprawne, bez idx i '-'
        return [float(x) for x in row[1:] if not self._is_missing(x)]

    def extract(self):
        with open(self.name, newline='', encoding='utf-8') as f:
            for row in csv.reader(f):
                if row:
                    yield row

    def transform_statistics(self):
        for row in self.extract():
            values=self._numbers(row)
            if values:
                yield (row[0],sum(values), sum(values)/len(values))

    def transform_non_value(self):
        for row in self.extract():
            missing=[i for i, x in enumerate(row) if self._is_missing(x)]
            yield (row[0], missing)

    @execution_time
    def load(self):
        with open('values.csv', 'w', newline='', encoding='utf-8') as f:
            writer=csv.writer(f) 
            writer.writerow(['numer_porzadkowy', 'suma', 'srednia'])
            writer.writerows(self.transform_statistics())

        with open('missing_values.csv', 'w', newline='', encoding='utf-8') as f:
            writer= csv.writer(f)
            writer.writerow(['numer_porzadkowy', 'indeksy_brakujacych'])
            for numer, indeksy in self.transform_non_value():
                writer.writerow([numer, ';'.join(map(str, indeksy))])

if __name__ == "__main__":
    etl = ETL()
    etl.load()
    print("zapisano values.csv i missing_values.csv")