import sys, os, numpy, copy

numpy.random.seed(1)
# example with independent admission probabilities
N = 3 # number of programs
K = 2 # maximum number of applications

# random example
# utilities = numpy.random.uniform(0,1,N)
# cost = numpy.random.uniform(0,0.25,N)
# probs = numpy.random.uniform(0,1,N)

# exmaple Ajayi, Siddebe
utilities = [7.9,10,11.4]
probs = [1,0.8,0.7]
cost = [0,0,0]

# sort utilities to make them sense
utilities = sorted(utilities, reverse=True)
probs = sorted(probs)



assump = 'indep' # or 'dep'

U = {i: utilities[i] for i in range(N)}
p = {i: probs[i] for i in range(N)}
C = {i: cost[i] for i in range(N)}

def MIA(U,p,C,assump,N,K):
    '''
    Implementation of the MIA algorithm in Chade and Smith 2006.
    Inputs:
    0. Programs are numbered from 0 to N-1
    1. U = dictionary of utilities
    2. p = dictionary with probabilities of admission
    3. C = dictionary of costs
    4. assump = 'indep' or 'dep', for independent and dependent admission probabilities
    5. N = number of programs
    6. K = uppper bound in the number of applications
    '''
    def value_portfolio(ls, verbose=False):
        pna = 1
        val = 0
        last = 0
        ls.sort()
        if verbose: print ls
        for i in ls:
            if assump == 'indep':
                val += pna*U[i]*p[i]
                pna = pna*(1-p[i])
            elif assump == 'dep':
                val += abs(p[i]-last)*U[i]
                if verbose: print last, p[i], abs(last-p[i])
                if verbose: print U[i]
                last = p[i]
        return val

    programs = range(N)
    pna, last = 1,0
    aux, out = [],[]
    remaining = range(N)
    while len(out) < K:
        aux = copy.copy(out)
        options, candidates = [],[]
        for i in range(len(remaining)):
            candidates = copy.copy(out)
            candidates.append(remaining[i])
            options.append(value_portfolio(candidates))
        mx = max(options)
        idx = options.index(mx)
        aux.append(remaining[idx])
        remaining = [i for i in remaining if i!= remaining[idx]]
        pna, last = pna*(1-p[idx]), p[idx]
        print aux
        print out
        if value_portfolio(aux)-value_portfolio(out) > C[idx]:
            out = copy.copy(aux)
            out.sort()
        else:
            break

    print out, value_portfolio(out, True)





#-----------------------
# CVXOPT implementation
#-----------------------
from cvxopt import matrix, solvers
from cvxopt.modeling import op, dot, variable

x = variable(N)
y = variable(N)

u = matrix(utilities)
c = matrix(cost)

print u
print c

P = matrix(probs)


A = numpy.identity(N)
A = matrix(A)
e = matrix(numpy.ones(N))
z = matrix(numpy.zeros(N))
ineq = []
ineq.append((A*x <= P))
ineq.append((A*y <= e))
ineq.append((A*x >= z))
ineq.append((A*y >= z))
ineq.append((A*x <= A*y))
ineq.append((dot(e,y) <= K))

print c
print A

obj = -dot((u-c), x)
lp2 = op(obj, ineq)
lp2.solve()
print(lp2.objective.value())
print x.value
print y.value
