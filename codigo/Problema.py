import sys

from CSP import *
from Tkinter import Tk
from tkFileDialog import askopenfilename
from time import time

class Problemas:

    def __init__(self):
        self._dominio = []
        self._fichero = ''
        self._nvariables = 0
        self._nDominio = 0

    def Problema(self):
        definicionProb = DefinicionProblema()

        Tk().withdraw()
        nombreFichero = askopenfilename()
        self._fichero = open(nombreFichero,'r')
        vars = []
        tiempo_inicial = time()
        for linea in self._fichero:

            objetos = linea.split(';')

            if objetos[0] =="Dominio":
               # tipo = objetos[2]
                self._nDominio = int(objetos[1])
                self._dominio = [] * self._nDominio
                for i in range(int(objetos[1])):
                    self._dominio.append(objetos[i+2])

            if objetos[0] == "Variables":
                self._nvariables = int(objetos[1])
                for variable in range(self._nvariables):
                    vtemp = objetos[variable+2].split(',')
                    if len(vtemp) > 1:
                        definicionProb.MultiplesVariables(range(int(vtemp[0]),int(vtemp[1])), self._dominio)
                    else:
                        definicionProb.AnadirVariable(int(objetos[variable+2]), self._dominio)

            if objetos[0] == "Restricciones":
                for restriccion in range(int(objetos[1])):
                    if objetos[2] == "nofuncion":
                        comas = objetos[restriccion+3].split('#')
                        func = comas[0]
                        vtemp = comas[1].split(',')

                        definicionProb.AnadirRestriccion(eval(comas[0]), map(int,vtemp))
                        #definicionProb.AnadirRestriccion(eval(comas[0]), (int(vtemp[0]),int(vtemp[1])))
                    elif objetos[2] == "funcion":
                        almoadilla = objetos[restriccion+3].split('#')
                        comas = almoadilla[1].split(',')
                        if len(comas) == 2:
                            definicionProb.AnadirRestriccion(RestriccionTodasDiferentes(),range(int(comas[0]),int(comas[1])))
                        elif len(comas) == 3:
                            definicionProb.AnadirRestriccion(RestriccionTodasDiferentes(),range(int(comas[0]), int(comas[1]),int(comas[2])))
                        elif len(comas) > 3:
                            lista = []
                            for i in range(len(comas)):
                                if i == 0:
                                    tmp = comas[i].split('[')
                                    v = tmp[1]
                                elif i != len(comas)-1:
                                    v = comas[i]
                                else:
                                    tmp = comas[i].split(']')
                                    v = tmp[0]
                                lista.append(int(v))
                            definicionProb.AnadirRestriccion(RestriccionTodasDiferentes(), lista)

            if objetos[0] == "algoritmo":

                if objetos[1] == "tabu":
                    #print(definicionProb.SolucionBusquedaTabu())
                    solution, esSolucion = definicionProb.SolucionBusquedaTabu(self._nDominio)
                    print solution

                if objetos[1] == "backtracking":
                    solution = []
                    if objetos[2] == "forwardcheck":
                        solution = definicionProb.SolucionBacktracking(True)
                    elif objetos[2] == "noforwardcheck":
                        solution = definicionProb.SolucionBacktracking(False)

        tiempo_final = time()
        tiempo_total = tiempo_final-tiempo_inicial
        print ("Tiempo de ejecucion: "+ str(tiempo_total))



problema = Problemas()

problema.Problema()