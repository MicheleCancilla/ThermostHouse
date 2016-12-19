#!/usr/bin/env python
# -*- coding:utf-8 -*-


class ConfigurationReader:
    """
        Classe per la lettura e la gestione dei file di configurazione e dei file dei segreti

    """

    def __init__(self, filename):
        """

        :param filename: nome del file di configurazione
        :return:
        """

        # La clausola with gestisce automaticamente le eccezioni, apre e chiude automaticamente il file
        self.confg_file = filename
        self.secret_dict = {}
        with open(filename) as _file:
            for line in _file:
                if line[0] == "#":
                    # Questo è un commento del file di configurazione, quindi non mi interessa
                    pass
                else:
                    key, separator, value = line.partition("=")
                    correct_key = (key.strip()).lower()
                    correct_value = ((value.strip("\n")).strip()).strip("'")
                    # print key, " ", correct_key, " ", value, " ", correct_value # Test

                    # Salvo la nuova coppia chiave valore in un dizionario
                    self.secret_dict.update({correct_key: correct_value})

    def __getitem__(self, key):
        """
        Il metodo restituisce il valore associato alla chiave cercata o lancia una eccezione se la chiave non è presente
        nel file di configurazione.

        :param key: chiave che si desidera recuperare dal file di configurazione
        :return: valore associato alla chiave

        """

        if key.lower() in self.secret_dict:
            # La chiave è presente quindi posso concludere correttamente l'operazione
            return self.secret_dict[key.lower()]
        else:
            # La chiave non è presente, lancio quindi una eccezione
            error_msg = "Either set the env variable '{var}' or place it in your {confg_file} file as {var}='VALUE'"
            raise ConfigurationError(error_msg.format(var=key, confg_file=self.confg_file))

    def __setitem__(self, key, value):
        raise InvalidOperationException('Environment Settings are read-only')

    def __delitem__(self, key):
        raise InvalidOperationException('Environment Settings are read-only')


class ConfigurationError(Exception):
    pass


class InvalidOperationException(Exception):
    pass

# ###################################################################### #
# VARIABILE DI CONFIGURAZIONE "configuration"                            #
# ###################################################################### #
conf = ConfigurationReader("conf/configuration.txt")

# ###################################################################### #
# VARIABILE DI CONFIGURAZIONE "secret"                                   #
# ###################################################################### #
secret = ConfigurationReader("conf/confsecret.txt")

"""
# Classe per il test
class main():
    conf = ConfigurationReader("conf/configuration.txt")
    KEY = conf['CLIENT_ID']
    print KEY
"""