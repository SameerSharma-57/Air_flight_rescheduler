import dimod
from dimod import ConstrainedQuadraticModel, quicksum
from dwave.system import LeapHybridCQMSampler
import numpy as np
from Data_preprocessing import graph_init
from score import ScoreGenerator
import numpy as np
import dwave.cloud as dc
import json

with open('parameter_values.json','r') as f:
    data = json.load(f)

cqm = ConstrainedQuadraticModel()
def init():
    g = graph_init()
    s = ScoreGenerator(g)
    return s, g


def cqm_formulation():

    s, g = init()
    cqm = ConstrainedQuadraticModel()
    g.gen_path_pnr_compatibility_matrix()

    K = len(g.path_pnr_compatibility)
    M = len(g.path_pnr_compatibility[0])
    print(K)
    print(M)
    for i in range(K):
        for j in range(M):
            cqm.add_variable('BINARY', f'X_{i}_{j}')
    
    X = {(i, j): dimod.Binary(f'X_{i}_{j}')
         for i in range(K)
         for j in range(M)}
    
    qubo = dimod.BinaryQuadraticModel.empty("BINARY")
    for i in range(K):
        for j in range(M):
            qubo.add_variable(f'X_{i}_{j}',1)

    for i in range(K):
        for j in range(M):
            qubo += s.get_score(i, j)
        
    cqm.set_objective(qubo)

    for i in range(K):
        cqm.add_constraint((quicksum(X[i,j] for j in range(M)))==1)

    comp = g.path_pnr_compatibility
    for i in range(K):
        cqm.add_constraint( (quicksum(X[i,j]*comp[i][j] for j in range(M))) == 1)

    for class_column,inv_column in zip(['FirstClass', 'BusinessClass', 'PremiumEconomyClass', 'EconomyClass'],['FC_AvailableInventory', 'BC_AvailableInventory', 'PC_AvailableInventory', 'EC_AvailableInventory']):
        for j, inventory in g.inv.iterrows():
            paths = g.path_flight_mapping[j]

            cqm.add_constraint( ((quicksum(X[i,j]*((int)(g.pnr.loc[i]['COD_CD']==class_column))*g.pnr.loc[i]['PAX_CNT'] for i in range(K))for k in paths)) <= g.inv.loc[j][inv_column])

    if(data['Flight Connection']['Max Arrival delay']['selected'] == True):
        for i in range(K):
            f_i_d= g.pnr.loc[i]['ARR_DTML'].split(" ")
            def F(j):
                inv_no = g.path_mapping[j][0]
                f_j_d = g.inv.loc[inv_no]['ArrivalDateTime']
                return g.get_time_diff(f_i_d,f_j_d)    
            cqm.add_constraint( (quicksum(F(j)*X[i,j] for j in range(M)))<=data['Flight Connection']['Max Arrival delay']['value'])

    sampler = LeapHybridCQMSampler()  
cqm_formulation()


