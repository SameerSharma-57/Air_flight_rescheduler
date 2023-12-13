import dimod
import pandas as pd
from dimod import Binary, ConstrainedQuadraticModel, quicksum
from dwave.system import LeapHybridCQMSampler
import numpy as np
from Data_preprocessing import graph_init
from dwave.system import DWaveSampler, EmbeddingComposite, FixedEmbeddingComposite
from minorminer.busclique import find_clique_embedding
import numpy as np
import dwave.cloud as dc

cqm = ConstrainedQuadraticModel()
def init():
    inv = pd.read_csv('data/inv.csv')
    pnr = pd.read_csv('data/pnr.csv')
    sch = pd.read_csv('data/sch.csv')

    inv.set_index('InventoryId',inplace=True)
    sch.set_index('ScheduleID',inplace=True)
    

    return inv,sch,pnr


def cqm_formulation():

    inv,sch,pnr = init()
    cqm = ConstrainedQuadraticModel()
    g=graph_init()
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
    
    for i in range(K):
        cqm.add_constraint((quicksum(X[i,j] for j in range(M)))==1)

    comp = g.path_pnr_compatibility
    for i in range(K):
        cqm.add_constraint( (quicksum(X[i,j]*comp[i][j] for j in range(M))) == 1)

    for i in range(K):
        f_i_d,f_i_t = pnr.loc[i]['DEP_DTMZ'].split(" ")
        def F(j):
            inv_no = g.path_mapping[j][0]
            f_j_d = inv.loc[inv_no]['DepartureDate']
            f_j_t = sch.loc[inv.loc[inv_no]['ScheduleId']]['DepartureTime'] 
            return g.get_time_diff(f_i_d,f_i_t,f_j_d,f_j_t)

            
        cqm.add_constraint( (quicksum(F(j)*X[i,j] for j in range(M)))<=72)
cqm_formulation()


