from __future__ import division
import sys, os, numpy, subprocess, multiprocessing, time, gc
'''
Boostrap to obtain distribution of scores
1. Read applications and scores; consolidate in a single dictionnary. The source
files are:
    1.1.
2. For each bootstrap iteration
    2.1. Sample with replacement students from the original dictionary
    2.2. Run the algorithm to obtain the allocation and the cutoffs
    3.3 Write vector of cutoffs and keep going.
'''


import Core.Algoritmo, Core.Entidades


# we start with reading the data. We use the files provided by DEMRE (from 2004 to 2017)
def ReadStudents(filename):
    stime = time.time()
    f = open(filename, 'r')
    lines = f.readlines()
    students = {}
    ct = 0
    print 'Storing information of students'
    for line in lines:
        if ct%10000 == 0:
            print '    Students processed:', ct
        ct+=1
        line = line.strip().rstrip('\r')
        pieces = line.split(';')
        if 'P' in pieces[0]:
            continue
        if pieces[65] == '':
            continue
        id_s = int(pieces[0])
        students[id_s] = {}

        for i in range(10):
            idx = 66 + 4*i # this is the column in the csv where the information of applications begins
            if int(pieces[idx]) == 0:
                continue
            students[id_s][i+1] = {'cc':0, 'mc':0, 'pp':0, 'od':0}
            students[id_s][i+1]['cc'] = int(pieces[idx])
            if int(pieces[idx+1]) in [24,25,26]:
                students[id_s][i+1]['mc'] = 25
            else:
                students[id_s][i+1]['mc'] = int(pieces[idx+1])
            students[id_s][i+1]['pp'] = int(pieces[idx+2])
            students[id_s][i+1]['od'] = int(pieces[idx+3])

    f.close()
    print 'Elapsed time:', time.time()-stime
    return students

def ReadPrograms(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    programs = {}
    ct = 0
    print 'Storing information of programs'
    for line in lines:
        line = line.strip().rstrip('\r')
        pieces = line.split(';')
        if 'CODIGO' in pieces[0]:
            continue
        id_c = int(pieces[0])
        programs[id_c] = Core.Entidades.Carrera(id_c)
        programs[id_c].ponderado_minimo = int(pieces[10])
        programs[id_c].cutoff = int(pieces[10])*100 # we just initialize the cutoff to be the min pond
        programs[id_c].vacantes_reg = int(pieces[12]) + int(pieces[13]) + int(pieces[14]) + int(pieces[15])
        programs[id_c].vacantes_bea = int(pieces[-1])

    f.close()
    return programs

def BootstrapIteration(data):
    dat_pg, dat_st, boot_list, s, indir = data[0], data[1], data[2], data[3], data[4]
    procesos = ['reg']
    carreras = dat_pg
    alumnos = {}
    ct = 0
    for i in range(len(boot_list)):
        alumnos[ct] = Core.Entidades.Alumno(ct)
        dat_aux = dat_st[boot_list[i]]
        alumnos[ct].pref = {j: dat_aux[j]['cc'] for j in dat_aux}
        alumnos[ct].puntpond = {j: dat_aux[j]['pp'] for j in dat_aux}
        alumnos[ct].marca = {j: dat_aux[j]['mc'] for j in dat_aux}
        ct+=1

    Core.Algoritmo.EjecutarSeleccion(alumnos, carreras, procesos)

    f = open(os.path.join(indir, 'cutoffs_bootstrap_s='+str(s)+'.txt'), 'w')
    for c in sorted(carreras):
        f.write(str(c)+';'+str(carreras[c].cutoff)+'\n')
    f.close()



if __name__ == '__main__':
    # 0. Parameters and inputs
    S = 1 # bootstrap iterations
    outdir = '../outputs'
    # 1. read programs and vacancies
    programs = ReadPrograms('../Solicitud DEMRE 2004-2017/carreras_requisitos.csv')

    # 2. read applications
    students = ReadStudents('../Solicitud DEMRE 2004-2017/ADM2015.csv')

    # 3. Sample students for bootstrap
    print 'Sampling students for boostrap'
    student_ids = students.keys()
    bootstrap_samples = numpy.random.choice(student_ids, (S,len(student_ids)), True)

    indata = []
    for sim in range(S):
        indata.append((programs, students, bootstrap_samples[sim], sim, outdir))

    np = min(3,multiprocessing.cpu_count())
    # We execute our process for each replication with a pool
    pool = multiprocessing.Pool(processes=min(np, len(indata)))
    pool.map(BootstrapIteration, indata)
    pool.close()
    pool.join()
