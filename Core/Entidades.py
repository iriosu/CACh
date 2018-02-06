
class Alumno:
    def __init__(self, ident=None):
        self.id_alumno = ident

        # Datos academicos del postulante y rendimiento en pruebas
        self.tipo_egreso, self.tipo_doc, self.sexo = None,None,None
        self.ano_egreso, self.region_egreso, self.provincia_egreso = None, None, None

        self.inscrito_proceso = 1 # por default asumimmos que el alumno esta inscrito en el proceso actual; luego con la lectura de los datos esto puede cambiar
        self.nem, self.rank = 0, 0

        self.matematica_actual, self.lenguaje_actual, self.ciencias_actual, self.historia_actual = 0,0,0,0
        self.modulo_actual, self.promLM_actual = None, None

        self.matematica_anterior, self.lenguaje_anterior, self.ciencias_anterior, self.historia_anterior = 0,0,0,0
        self.modulo_anterior, self.promLM_anterior = None, None

        self.prueba_electiva = {} # entrega el puntaje en la prueba electiva utilizada
        self.prueba_especial = None
        self.tabu = None

        self.reg, self.bea = True, False

        # el sufijo _proc se refiere a cosas procesadas
        self.pref, self.pref_proc  = {},{}
        self.puntpond, self.puntpond_proc = {},{}
        self.marca, self.marca_proc = {},{}
        self.orden, self.orden_proc = {},{}
        self.puntano, self.puntano_proc = {},{}


class Carrera:
    def __init__(self, codigo_carrera=None):
        self.codigo_carrera = codigo_carrera
        self.vacantes_reg, self.vacantes_bea = None, None

        self.nem, self.rank = None, None
        self.lenguaje, self.matematica = None, None
        self.historia, self.ciencias = None, None

        self.prueba_electiva, self.restringe_sexo = False, False
        self.prueba_especial = None

        self.promedio_minimo, self.ponderado_minimo, self.ponderado_minimo_antes_pe_pond = None, None, None
        self.max_post, self.excluye_desde_pref, self.excluye_egresado_antes = None, None, None
        self.provincias = None
        self.cutoff = 0

class Nodo:
    def __init__(self, a=None, c=None, punt=0, proc=None, pref=None, pref2=None, vac=0):
        self.alumno = a # id del alumno asociado al nodo
        self.carrera = c # codigo de la carrera asociada al nodo
        self.puntaje = punt # puntaje con que el alumno compite en la carrera
        self.proceso = proc # proceso al que esta asociado el nodo. Por ejemplo, Regular, BEA, etc.
        self.preferencia = pref # preferencia original
        self.preferencia_proc = pref2 # preferencia para el procesamiento del grafo

        self.vacantes = vac # vacantes de la carrera asociada al nodo

        self.nexta = None
        self.nextu = None
        self.preva = None
        self.prevu = None

    def __cmp__(self, other, criterio='puntaje'):
        if criterio == 'puntaje':
            return cmp(other.puntaje, self.puntaje)
        elif criterio == 'preferencia':
            return cmp(self.preferencia, other.preferencia)

    def Borrar(self):
        if self.alumno != -1:
            self.preva.nexta = self.nexta
            self.nexta.preva = self.preva
            self.nextu.prevu = self.prevu
            self.prevu.nextu = self.nextu
