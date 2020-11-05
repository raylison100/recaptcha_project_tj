from json import JSONEncoder

class Result:
    def __init__(self, grupos):
        self.grupos = grupos


class Grupo:
    def __init__(self, processos):
        self.processos = processos

class Processo:
    def __init__(self, processo, numero_processo, movimentacoes):
        self.processo = processo
        self.numero_processo = numero_processo
        self.movimentacoes = movimentacoes


class Movimentacoes:
    def __init__(self, data, complemento):
        self.data = data
        self.complemento = complemento


class EmployeeEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__