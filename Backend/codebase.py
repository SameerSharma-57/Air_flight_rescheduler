import dimod
from dimod import ConstrainedQuadraticModel, quicksum
from dwave.system import LeapHybridCQMSampler
import numpy as np
from Backend.Data_preprocessing import graph_init,Graph
from Backend.score import ScoreGenerator

import numpy as np
import dwave.cloud as dc
import json
import os
import pandas as pd

with open('Backend/parameter_values.json','r') as f:
    data = json.load(f)
feasible_sampleset=None
g=None
cqm = ConstrainedQuadraticModel()
s=None
def init():
    global g,s
    g = graph_init()
    s = ScoreGenerator(g)
    return s, g


def cqm_formulation():
    global g,feasible_sampleset
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
    print("Qubo done")
    for i in range(K):
        for j in range(M):
            qubo += X[i,j]*s.get_score(i, j)
        
    cqm.set_objective(qubo)
    print('score calculated')
    for i in range(K):
        cqm.add_constraint((quicksum(X[i,j] for j in range(M)))==1)

    comp = g.path_pnr_compatibility
    for i in range(K):
        cqm.add_constraint( (quicksum(X[i,j]*comp[i][j] for j in range(M))) == 1)

    for class_column,inv_column in zip(['FirstClass', 'BusinessClass', 'PremiumEconomyClass', 'EconomyClass'],['FC_AvailableInventory', 'BC_AvailableInventory', 'PC_AvailableInventory', 'EC_AvailableInventory']):
        for j, inventory in g.inv.iterrows():
            paths = g.path_flight_mapping[j]
            # print(j,inventory)
            cqm.add_constraint( (quicksum(quicksum(X[i,k] * ((int)(g.pnr.loc[i]['COS_CD']==class_column)) * g.pnr.loc[i]['PAX_CNT'] for i in range(K))for k in paths)) <= float(g.inv.loc[j][inv_column]))

    if(data['Flight Connection']['Max Arrival delay']['selected'] == True):
        for i in range(K):
            f_i_d= g.pnr.loc[i]['ARR_DTML']
            def F(j):
                inv_no = g.path_mapping[j][0]
                f_j_d = g.inv.loc[inv_no]['ArrivalDateTime']
                return g.get_time_diff(f_i_d,f_j_d)    
            cqm.add_constraint( (quicksum(F(j)*X[i,j] for j in range(M)))<=data['Flight Connection']['Max Arrival delay']['score'])

    sampler = LeapHybridCQMSampler()  
    sampleset = sampler.sample_cqm(cqm, time_limit=10)
    print("samples generated")
    feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)  
    print(feasible_sampleset.info) 
    qpu_access_time = feasible_sampleset.info['qpu_access_time']
    
    #all_feasible_samples = feasible_sampleset.samples
    #return all_feasible_samples
    # output_dir = 'tempData'
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # for idx, record in enumerate(feasible_sampleset.record.sample):
    #     sample = record
    #     output_file = os.path.join(output_dir, f'feasible_solution_{idx}.txt')
    #     with open(output_file, 'w') as f:
    #         f.write(str(sample))

    # best = feasible_sampleset.first.sample
    return feasible_sampleset
def get_best_sample():

    sample_set = cqm_formulation()
    # with open('Backend/best.txt', 'w')as f1:
    #     print(best, file=f1)
    # with open('Backend/vars.txt', 'w')as f2:
    #     print(vars, file=f2)
    output_dir = 'tempData'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    total_score=0
    score_list=[]
    for idx,best in enumerate(sample_set):
        df = []
        total_score=0
        for i in best:
            if(best[i]==1.0):
                
                x = i.split('_')
                x[1] = int(x[1])
                x[2] = int(x[2])
                passenger_details = g.pnr.loc[x[1]]
                path = g.path_mapping[x[2]]
                score = s.get_score(x[1],x[2])
                score*=-1
                total_score+=score
                
                df.append([passenger_details['RECLOC'],passenger_details['DEP_KEY'],path,score])
        print(total_score)
        score_list.append(total_score)
    
        df.sort()
        df=pd.DataFrame(df)
        output_file = os.path.join(output_dir, f'feasible_solution_{idx}.csv')
        df.to_csv(output_file,index=False,header=['RECLOC','DEP_KEY','Path','Score'])
    print(score_list)
    df = pd.DataFrame(score_list)
    df.to_csv('tempData/score.csv',index=False,header=['score'])
    
get_best_sample()