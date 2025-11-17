from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        self.load_impianti()
        risultato = []

        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            consumo_mese = 0
            count = 0

            for consumo in consumi:
                if consumo.data.month == int(mese):
                    consumo_mese += float(consumo.kwh)
                    count += 1

            media = consumo_mese / count if count > 0 else 0
            risultato.append((impianto.nome, media))
        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        indice = giorno - 1

        if ultimo_impianto is None:
            if consumi_settimana[1][indice] >= consumi_settimana[2][indice]:
                ultimo_impianto = 2
                valore = consumi_settimana[2][indice]
            else:
                ultimo_impianto = 1
                valore = consumi_settimana[1][indice]
            costo_corrente += valore
            sequenza_parziale.append(ultimo_impianto)
            giorno += 1

        elif ultimo_impianto == 1:
            if consumi_settimana[1][indice] >= consumi_settimana[2][indice] + 5:
                ultimo_impianto = 2
                valore = consumi_settimana[2][indice]
                costo_corrente += valore + 5
            else:
                valore = consumi_settimana[1][indice]
                costo_corrente += valore
            sequenza_parziale.append(ultimo_impianto)
            giorno += 1

        else:  # ultimo_impianto == 2
            if consumi_settimana[1][indice] + 5 >= consumi_settimana[2][indice]:
                ultimo_impianto = 2
                valore = consumi_settimana[2][indice]
                costo_corrente += valore
            else:
                ultimo_impianto = 1
                valore = consumi_settimana[1][indice]
                costo_corrente += valore + 5
            sequenza_parziale.append(ultimo_impianto)
            giorno += 1

        self.__ricorsione(sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana)

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        self.load_impianti()
        risultato = dict()

        for impianto in self._impianti:
            cons = []
            consumi = impianto.get_consumi()
            for consumo in consumi:
                if consumo.data.month == int(mese) and 1 <= consumo.data.day <= 7:
                    cons.append(consumo.kwh)
            risultato[impianto.id] = cons

        return risultato


