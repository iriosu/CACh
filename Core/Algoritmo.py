import sys, platform, Queue, gc
import Entidades

def CrearGrafo(alumnos, carreras, procesos):
	sys.stdout.write('\nInicializando diccionarios de procesamiento')
	sys.stdout.flush()
	# Ingresamos postulaciones procesadas
	lista_alumnos = alumnos.keys()
	for a in lista_alumnos:
		alumno = alumnos[a]
		if alumno.pref_proc == {}: # misma inicializacion, independiente de la modalidad que se este ejecutando
			aux = 1
			for p in alumno.pref:
				if alumno.pref[p] not in carreras: # significa que la carrera no esta adscrita a ningun programa de ingreso especial
					sys.stdout.write('\n***ERROR: postulacion a carrera que no esta ingresada. Codigo carrera '+ str(alumno.pref[p]))
					sys.stdout.write('\n***Solucion: Revisar lectura de carreras.')
					sys.exit('Error durante la creacion del grafo; carrera especificada es desconocida; metodo CrearGrafo, Algoritmo.py')
				carrera = carreras[alumno.pref[p]]

				alumno.pref_proc[aux] = [carrera.codigo_carrera, 'reg']
				alumno.marca_proc[aux] = alumno.marca[p]
				alumno.puntpond_proc[aux] = alumno.puntpond[p]
				alumno.orden_proc[aux] = '00000'
				aux +=1

	sys.stdout.write('\nCreando el grafo de postulaciones')
	sys.stdout.flush()

	# Creo diccionario con postulaciones procesadas
	postulaciones = {c:{pr.lower():Queue.PriorityQueue() for pr in procesos} for c in carreras}

	# Llenado del diccionario de postulaciones
	ct, old_percent = 0,0
	for a in alumnos:
		ct += 1
		percent = int(ct*10/len(alumnos))*10
		if percent != old_percent:
			sys.stdout.write("\n    Llenando diccionario de postulaciones. (completado: " + "%d%% " % percent + ").")
			sys.stdout.flush()
			old_percent = percent
		alumno = alumnos[a]
		for p in alumno.pref_proc:
			if alumno.marca_proc[p] in [24,25,26]: # solo entran a competir postulantes con marca 25; agregamos la marca 24 para la asignacion con transferencia; para la normal no tiene ningun efecto
				codigo_carrera, proceso = alumno.pref_proc[p][0], alumno.pref_proc[p][1]
				carrera = carreras[codigo_carrera]
				puntaje = alumno.puntpond_proc[p]
				for q in alumno.pref:
					if alumno.pref[q] == carrera.codigo_carrera:
						break
				postulaciones[codigo_carrera][proceso].put(Entidades.Nodo(a, codigo_carrera, int(puntaje), proceso, q, p, int(getattr(carrera, 'vacantes_' + proceso))))

	topa, topu, mapa_nodos = {},{},{} #map me retorna el nodo asociado a la postulacion (alumno, carrera, proceso)

	# Crear relaciones en carreras
	ct, old_percent = 0,0
	for c in postulaciones:
		ct += 1
		percent = int(ct*10/len(postulaciones))*10
		if percent != old_percent:
			sys.stdout.write("\n    Creando nodos y relaciones entre carreras. (completado: " + "%d%% " % percent + ").")
			sys.stdout.flush()
			old_percent = percent
		for pr in postulaciones[c]:
			if postulaciones[c][pr].empty(): # la carrera no tiene postulantes
				continue
			elif int(getattr(carreras[c], 'vacantes_' + pr)) == 0: # la carrera  no tiene vacantes
				continue
			else:
				if c not in topu:
					topu[c] = {}
				nodo = postulaciones[c][pr].get()
				topu[c][pr] = nodo
				nodo.nexta = Entidades.Nodo(-1, -1) # nodo artificial de inicio
				if postulaciones[c][pr].empty():
					nodo.preva = Entidades.Nodo(-1, -1) # nodo artificial de termino
				while not postulaciones[c][pr].empty():
					father = nodo
					nodo = postulaciones[c][pr].get()
					father.preva = nodo
					nodo.nexta = father
					if postulaciones[c][pr].empty():
						nodo.preva = Entidades.Nodo(-1, -1) # nodo artificial de termino
						break

	for c in topu:
		for pr in topu[c]:
			mapa_nodos[c,pr] = {}
			nodo = topu[c][pr]
			while True:
				mapa_nodos[c,pr][nodo.alumno] = nodo
				nodo = nodo.preva
				if nodo.alumno == -1:
					break

	# Crear relaciones en alumnos
	ct, old_percent = 0,0
	for a in alumnos:
		ct += 1
		percent = int(ct*10/len(alumnos))*10
		if percent != old_percent:
			sys.stdout.write("\n    Creando relaciones entre alumnos. (completado: " + "%d%% " % percent + ").")
			sys.stdout.flush()
			old_percent = percent

		alumno = alumnos[a]
		prefs = [p for p in alumno.marca_proc if alumno.marca_proc[p] in [24,25] and tuple(alumno.pref_proc[p]) in mapa_nodos]
		prefs.sort()
		if len(prefs) == 0: # el postulante no tiene preferencias con marca 24 o 25 (que son donde puede competir)
			continue
		else:
			nodo = mapa_nodos[tuple(alumno.pref_proc[prefs[0]])][a]
			nodo.nextu = Entidades.Nodo(-1, -1) # nodo artificial de inicio
			topa[a] = nodo
			if len(prefs) == 1:
				nodo.prevu = Entidades.Nodo(-1, -1) # nodo artificial de termino
			else:
				for i in range(1, len(prefs)):
					father = nodo
					nodo = mapa_nodos[tuple(alumno.pref_proc[prefs[i]])][a]
					nodo.nextu = father
					father.prevu = nodo
					if i == len(prefs)-1:
						nodo.prevu = Entidades.Nodo(-1, -1) # nodo artificial de termino

	return topa, topu

def ApplicantDomination(topa, topu):
	# Cuento cuantos postulantes estan en primera preferencia y borro los que estan sobre la capacidad
	tb = 0 # total nodos borrados
	for c in topu:
		for pr in topu[c]: # iteramos sobre cada carrera y cada proceso
			father = topu[c][pr]
			cont, nodo = 0, father
			while True:
				if nodo.nextu.alumno == -1: # vemos si es la primera preferencia del alumno
					cont+=1
				if cont >= nodo.vacantes and nodo.puntaje != nodo.preva.puntaje:
					# Borramos los alumnos que vienen despues de nodo pues estan dominados
					aux = nodo
					nodo = aux.preva
					while nodo.alumno != -1:
						if nodo.nextu.alumno == -1: #primera preferencia del alumno del nodo
							topa[nodo.alumno] = nodo.prevu # cambiamos la preferencia top del alumno a y la seteamos a la siguiente universidad
							if nodo.prevu.alumno == -1: # si no tiene otra preferencia, borramos a ese alumno de topa
								del topa[nodo.alumno]
						nodo.Borrar()
						tb+=1
						nodo = aux.preva
						if nodo.alumno == -1:
							break
				else:
					nodo = nodo.preva
				if nodo.alumno == -1:
					break
	return tb

def UniversityDomination(topa, topu):
	tb = 0
	for a in sorted(topa, key=lambda a: topa[a].puntaje, reverse=True):#topa:
		nodo_alumno = topa[a]
		while nodo_alumno.alumno != -1:
			father = topu[nodo_alumno.carrera][nodo_alumno.proceso] # primera preferencia de la carrera a la cual esta postulando a
			pos = 0 # vemos en que posicion esta el alumno a en su primera preferencia
			nodo = father
			while nodo.alumno != -1:
				pos+=1
				if nodo.alumno == a and pos <= father.vacantes:
					# El alumno esta dentro de la capacidad de su primera preferencia -> borramos sus preferencias posteriores
					nodo_aux = nodo
					nodo = nodo_aux.prevu
					while nodo.alumno != -1:
						if nodo.nexta.alumno == -1: #primera preferencia de la carrera
							topu[nodo.carrera][nodo.proceso] = nodo.preva
							if nodo.preva.alumno == -1:
								del topu[nodo.carrera][nodo.proceso]
						nodo.Borrar()
						nodo = nodo_aux.prevu
						tb+=1
					break
				elif pos > father.vacantes:
					break # concluimos que ya no esta en la capacidad asi que no podremos borrar sus preferencias anteriores
				else:
					if pos == father.vacantes and nodo.puntaje == nodo.preva.puntaje:
						pos-=1
					nodo = nodo.preva
			nodo_alumno = nodo_alumno.prevu

	return tb

def StudentOptimal(alumnos, carreras, topa, topu):
	sys.stdout.write('\nLimpiando dominancias')
	sys.stdout.flush()
	while True:
		#nbu = Algoritmo.UniversityDomination(topu, topa) #nodos borrados por university domination
		nba = ApplicantDomination(topa, topu) #nodos borrados por applicant domination
		if nba == 0:  #si ya no hay nodos dominados el proceso de limpieza termina
			break
		else:
			sys.stdout.write('\n    Nodos limpiados: ' +  str(nba))
			sys.stdout.flush()

	sys.stdout.write('\nEjecutando algoritmo Student Optimal')
	sys.stdout.flush()
	for a in topa:
		nodo = topa[a]
		alumno = alumnos[a]
		alumno.marca[nodo.preferencia], alumno.marca_proc[nodo.preferencia_proc] = 24, 24
		# Ponemos la marca 26 en el listado de marcas original y en el de procesamiento
		for q in [pref for pref in alumno.pref if pref > nodo.preferencia]:
			if alumno.marca[q] in [24,25]:
				alumno.marca[q] = 26
		for q in [pref for pref in alumno.pref_proc if pref > nodo.preferencia_proc]:
			if alumno.marca_proc[q] in [24,25]:
				alumno.marca_proc[q] = 26

def UniversityOptimal(alumnos, carreras, topa, topu):
	sys.stdout.write('\nLimpiando dominancias')
	sys.stdout.flush()
	while True:
		#nba = ApplicantDomination(topa, topu) #nodos borrados por applicant domination
		nbu = UniversityDomination(topa, topu) #nodos borrados por university domination
		if nbu == 0: #si ya no hay nodos dominados el proceso de limpieza termina
			break
		else:
			sys.stdout.write('\n    Nodos limpiados: ' +  str(nbu))
			sys.stdout.flush()

	# Creamos la seleccion university optimal procesando las marcas.
	sys.stdout.write('\nEjecutando algoritmo University Optimal')
	sys.stdout.flush()
	for c in topu:
		for pr in topu[c]:
			pos = 0
			nodo = topu[c][pr]
			while True:
				pos +=1
				if pos <= nodo.vacantes:
					alumnos[nodo.alumno].marca[nodo.preferencia], alumnos[nodo.alumno].marca_proc[nodo.preferencia_proc] = 24, 24
					# Ponemos la marca 26 en el listado de marcas original y en el de procesamiento
					for q in [pref for pref in alumnos[nodo.alumno].pref if pref > nodo.preferencia]:
						if alumnos[nodo.alumno].marca[q] in [24,25]:
							alumnos[nodo.alumno].marca[q] = 26
					for q in [pref for pref in alumnos[nodo.alumno].pref_proc if pref > nodo.preferencia_proc]:
						if alumnos[nodo.alumno].marca_proc[q] in [24,25]:
							alumnos[nodo.alumno].marca_proc[q] = 26
				if pos == nodo.vacantes and nodo.puntaje == nodo.preva.puntaje:
					pos-=1
				nodo = nodo.preva
				if nodo.alumno == -1:
					break

def ProcesoPostSeleccion(alumnos, carreras):
	nodos = {}
	ct, old_percent = 0,0
	for a in alumnos:
		ct += 1
		percent = int(ct*10/len(alumnos))*10
		if percent != old_percent:
			sys.stdout.write("\nEjecutando proceso post-seleccion. (completado: " + "%d%% " % percent + ").")
			sys.stdout.flush()
			old_percent = percent
		alumno = alumnos[a]
		for p in alumno.pref_proc:
			if alumno.marca_proc[p] in [24,25]:
				codigo_carrera, proceso = alumno.pref_proc[p][0], alumno.pref_proc[p][1]
				if codigo_carrera not in nodos:
					nodos[codigo_carrera] = {}
				if proceso not in nodos[codigo_carrera]:
					nodos[codigo_carrera][proceso] = Queue.PriorityQueue()

				puntaje = alumno.puntpond_proc[p]
				for q in alumno.pref:
					if alumno.pref[q] == codigo_carrera:
						break
				nodos[codigo_carrera][proceso].put(Entidades.Nodo(a, codigo_carrera, int(puntaje), proceso, q, p))

	for c in nodos:
		for pr in nodos[c]:
			cont = 1
			carrera = carreras[c]
			if nodos[c][pr].empty():
				continue
			while True:
				nodo = nodos[c][pr].get()
				alumnos[nodo.alumno].orden_proc[nodo.preferencia_proc] = cont
				if alumnos[nodo.alumno].marca_proc[nodo.preferencia_proc] == 24:
					carrera.cutoff = nodo.puntaje
				if nodos[c][pr].empty():
					break
				cont+=1
			if cont < int(getattr(carrera, 'vacantes_' + pr)):
				carrera.cutoff = 45000

def EjecutarSeleccion(alumnos, carreras, procesos):
	topa, topu = CrearGrafo(alumnos, carreras, procesos)

	StudentOptimal(alumnos, carreras, topa, topu)
	# UniversityOptimal(alumnos, carreras topa, topu)

	ProcesoPostSeleccion(alumnos, carreras)

	sys.stdout.write('\nLiberando memoria (puede tardar algunos segundos...)')
	sys.stdout.flush()
	del topa, topu
	gc.collect()
