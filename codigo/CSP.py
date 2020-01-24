import random

import sys


class DefinicionProblema(object):
    # idea de numberjack

    def __init__(self):

        self._restricciones = []
        self._variables = {}
        self._algoritmoBacktracking = Backtracking()
        self._algoritmoTabu = BusquedaTabu()

    # la variable no puede ser repetida ya que la usaremos como key en el diccionario
    # dominio tiene que ser de tipo lista o tupla

    def AnadirVariable(self, variable, dominio):

        if variable in self._variables:
            raise ValueError
            print ("Variable duplicada %s")
        if type(dominio) in (list, tuple):
            dominio = Dominio(dominio)
        if not dominio:
            raise ValueError
            print("Dominio vacio")
        self._variables[variable] = dominio


    def MultiplesVariables(self, variables, dominio):
        for variable in variables:
            self.AnadirVariable(variable, dominio)

    def getVariables(self):
        return self._variables

    def AnadirRestriccion(self, restriccion, variable=None):
        if not isinstance(restriccion, Restriccion):
            if callable(restriccion):
                restriccion = FuncionRestriccion(restriccion)
            else:
                raise ValueError
                print ("Las restricciones tienen que ser instancies de la clase Restricciones")
        self._restricciones.append((restriccion, variable))

    def GetVariables(self):
        return self._variables

    def GetRestricciones(self):
        return self._restricciones

    def _Argumentos(self):
        dominios = self._variables.copy()
        todaslasvariables = dominios.keys()
        restricc = []
        for restriccion, var in self._restricciones:
            if not var:
                var = todaslasvariables
            restricc.append((restriccion, var))
        vrestricciones = {}
        for variable in dominios:
            vrestricciones[variable] = []
        for restriccion, var in restricc:
            for variable in var:
                vrestricciones[variable].append((restriccion, var))
        for dominio in dominios.values():
                dominio.resetEstado()
                if not dominio:
                    return None, None, None
        return dominios, restricc, vrestricciones

    def SolucionBacktracking(self,forwardcheck):
        dominio, restricciones, vrestricciones= self._Argumentos()
        self._algoritmoBacktracking.__init__(forwardcheck)
        return self._algoritmoBacktracking.Backtracking([],dominio,vrestricciones,{},True)

    def SolucionBusquedaTabu(self, nDominio):
        dominio, restricciones, vrestricciones= self._Argumentos()
        SolucionInicial = self._algoritmoTabu.SolucionAleatoria(self._variables, len(self._variables), dominio)
        return self._algoritmoTabu.BusquedaTabu(len(dominio),500,SolucionInicial,dominio,vrestricciones, nDominio)

class Backtracking():

    def __init__(self, forwardcheck=False):
        self._forwardcheck = forwardcheck

    def Backtracking(self, soluciones, dominios, vrestricciones,
                     asignados, single):
        lst = [(-len(vrestricciones[variable]),
                len(dominios[variable]), variable) for variable in dominios]
        lst.sort()
        for item in lst:
            if item[-1] not in asignados:
                # Hemos encontrado una variable que no tiene asignado un valor
                break
        else:
            soluciones.append(asignados.copy())
            return soluciones[0]

        variable = item[-1]
        asignados[variable] = None

        forwardcheck = self._forwardcheck
        if forwardcheck:
            pushdominios = [dominios[x] for x in dominios if x not in asignados]
        else:
            pushdominios = None

        for value in dominios[variable]:
            asignados[variable] = value
            if pushdominios:
                for domain in pushdominios:
                    domain.meterEstado()
            for constraint, variables in vrestricciones[variable]:
                if not constraint(variables, dominios, asignados,
                                  pushdominios):
                    # Si el valor no es bueno, salimos
                    break
            else:
                # VSi el valor es correcto, ejecutamos recursividad y miramos siguiente variable no asignada
                self.Backtracking(soluciones, dominios, vrestricciones,
                                           asignados, single)
                if soluciones and single:
                    return soluciones
            if pushdominios:
                for domain in pushdominios:
                    domain.sacarEstado()
        del asignados[variable]
        return soluciones

    def getSolucion(self, dominios, constraints, vconstraints):
        soluciones = self.Backtracking([], dominios, vconstraints,
                                                {}, True)
        return soluciones and soluciones[0] or None


class Variable(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


Unassigned = Variable("Unassigned")

# clase dominio
class Dominio(list):

    def __init__(self, set):
        list.__init__(self, set)
        self._estadosOcultos = []
        self._estados = []

    def resetEstado(self):
        self.extend(self._estadosOcultos)
        del self._estadosOcultos[:]
        del self._estados[:]

    def meterEstado(self):
        self._estados.append(len(self))

    def sacarEstado(self):
        diff= self._estados.pop()-len(self)
        if diff:
            self.extend(self._estadosOcultos[-diff:])
            del self._estadosOcultos[-diff:]

    def ocultarEstado(self, valor):
        list.remove(self, valor)
        self._estadosOcultos.append(valor)


class Restriccion(object):
    def __call__(self, variables, dominios, asignaciones, forwardcheck=False):
        return True

    def forwardCheck(self, variables, dominios, asignaciones, _unassigned=Unassigned):
        variablenoasignada = _unassigned
        for variable in variables:
            if variable not in asignaciones:
                if variablenoasignada is _unassigned:
                    variablenoasignada = variable
                else:
                    break
        else:
            # Eliminamos de la lista de dominio de variables no asignadas los valores que no cumples la restricciones de la variable
            if variablenoasignada is not _unassigned:
                dominio = dominios[variablenoasignada]
                if dominio:
                    for valor in dominio[:]:
                        asignaciones[variablenoasignada] = valor
                        if not self(variables, dominios, asignaciones):
                            dominio.ocultarEstado(valor)
                    del asignaciones[variablenoasignada]
                if not dominio:
                    return False
        return True

class FuncionRestriccion(Restriccion):

    def __init__(self, func, asignado=True):
        self._func = func
        self._asignado = asignado

    def __call__(self, variables, dominios, asignaciones, forwardcheck=False,
                 _unassigned=Unassigned):
        parms = [asignaciones.get(x, _unassigned) for x in variables]
        noencontrado = parms.count(_unassigned)
        if noencontrado:
            return ((self._asignado or self._func(*parms)) and
                    (not forwardcheck or noencontrado != 1 or
                     self.forwardCheck(variables, dominios, asignaciones)))
        return self._func(*parms)

class RestriccionTodasDiferentes(Restriccion):

    def __call__(self, variables, dominios, asignaciones, forwardcheck=False,
                 _unassigned=Unassigned):
        vistos = {}
        for variable in variables:
            valor = asignaciones.get(variable, _unassigned)
            if valor is not _unassigned:
                if valor in vistos:
                    return False
                vistos[valor] = True
        if forwardcheck:
            for variable in variables:
                if variable not in asignaciones:
                    dominio = dominios[variable]
                    for value in vistos:
                        if value in dominio:
                            dominio.ocultarEstado(value)
                            if not dominio:
                                return False
        return True


class BusquedaTabu():

    def BusquedaTabu(self, maxtabu, maxitera, solucion, dominio, vrestricciones, nDominio):
        n_iter = 0
        mejor = list(solucion)
        tabu=[]
        tabu = dominio.copy()
        for var in dominio:
            tabu[var] = [None for j in range(len(dominio[var]))]
        sol = []
        solucionBuena = False
        while n_iter < maxitera and not solucionBuena:
            n_iter += 1
            contador = 0
            # if n_iter % (nDominio*10) == 0:
            #     for var in dominio:
            #         tabu[var] = [None for j in range(len(dominio[var]))]
            solucion, esSolucion = self.EncontrarMovimiento(n_iter,tabu,maxtabu,solucion,dominio, vrestricciones)
            for delta in esSolucion:
                if delta == 0:
                    contador = contador +1
            if contador == nDominio:
                solucionBuena = True
            #print solucion

        return solucion,solucionBuena


    def EncontrarMovimiento(self,n_iter,tabu,maxtabu,solucion,dominio, vrestricciones):
        n = len(dominio)
        mejor_delta = n
        delta = 0
        lst = []
        esSolucion = {}
        #esSolucion = [0 for i in range(len(dominio))]
        #asignados = [0 for i in range(len(dominio))]
        asignados = solucion.copy()
        deltas = [0 for i in range(len(dominio))]
        esSolucion = solucion.copy()
        for variable in dominio:
            lst.append(variable)
        for indice in range(len(dominio)):
            variable = lst.pop(0)
            asignados[variable] = None
            deltas = [0 for i in range(len(dominio[variable]))]
            indiceCero = False
            for valor in dominio[variable]:
                asignados[variable] = valor
                for constraint, variables in vrestricciones[variable]:
                    if not constraint(variables,dominio,asignados):
                        delta = delta + 1
                if int(valor) == 0:
                    indiceCero = True
                if indiceCero:
                    deltas[int(valor)] = delta
                else:
                    deltas[int(valor)-1] = delta
                delta = 0
            movimiento = self.EvaluarMovimiento(deltas,len(dominio),tabu,variable)
            asignados[variable] = int(dominio[variable][movimiento])
            if indiceCero:
                esSolucion[variable] = deltas[movimiento]
                tabu[variable][asignados[variable]] = solucion[variable]
            else:
                esSolucion[variable] = deltas[movimiento]
                if solucion[variable] != Unassigned:
                    tabu[variable][int(solucion[variable])-1] = solucion[variable]
        return asignados,esSolucion

    def EvaluarMovimiento(self,deltas,peorDelta,tabu,variable):
        cualquiera = True
        mejorMovimiento = 0
        esTabu = False
        for i in range(len(deltas)):
            if deltas[i] < peorDelta and i not in tabu[variable]:
                mejorMovimiento = i
                peorDelta = deltas[i]
        # for i in range(len(deltas)):
        #     if deltas[i] < deltas[mejorMovimiento]:
        #         mejorMovimiento = i
        #         esTabu = True
        for x in range(len(deltas)):
            if deltas[x] == 0:
                 mejorMovimiento = x
        # for x in range(len(deltas)-1):
        #     if deltas[x] != deltas[x+1]:
        #         cualquiera = False
        # if cualquiera:
        #     fin = False
        #     while not fin:
        #         movimiento = random.choice(range(len(deltas)))
        #         if movimiento not in tabu[variable]:
        #             mejorMovimiento = movimiento
        #             fin = True
        return mejorMovimiento

    def SolucionAleatoria(self,variables,nvariables,dominio):
        solucion = variables.copy()
        dom = dominio.copy()
        for variable in variables:
            #asignacion = random.choice(dom[variable])
            solucion[variable] = Unassigned
        return solucion