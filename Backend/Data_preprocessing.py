import pandas as pd
import numpy as np
import sys
from datetime import datetime
from more_itertools import collapse
import json

#import data from parameter_values.json
with open('parameter_values.json','r') as f:
    data = json.load(f)


inv = pd.read_csv('final_data/inv.csv')
pnr = pd.read_csv('final_data/pnrb.csv')
sch = pd.read_csv('final_data/sch.csv')
pnrp = pd.read_csv('final_data/pnrp.csv')

inv.set_index('InventoryId',inplace=True)
sch.set_index('ScheduleID',inplace=True)

pnr.set_index('RECLOC',inplace=True)

cancelled_flights = pd.read_csv('final_data/Cancelled.csv')
pnr['COS_CD'] = pnr['COS_CD'].astype(str)
# cancelled_flights.set_index('InventoryId',inplace=True)





# Make a general graph structure using class



def print_matrix(matrix):
    for entry in matrix:
        print(entry)


# def get_impacted_passengers():




class Graph:

    def get_time_diff(self,d1,d2):
        
        format = '%Y-%m-%d %H:%M:%S'
        t1 = datetime.strptime(d1,format)
        t2 = datetime.strptime(d2,format)
        return (t2-t1).total_seconds()/3600
    
    def update_db(self):
        self.inv = inv
        self.pnr = pnr
        self.sch = sch
        self.prnp = pnrp


    def __init__(self, vertices , affected_vertices = []):
        self.V = len(vertices)
        # print(vertices)
        self.graph = [[[] for x in range(self.V)] for y in range(self.V)]
        # print(self.graph)
        vertices.sort()
        self.city_mapping = dict(zip(vertices,range(self.V)))
        self.path_city_compatibility = None
        self.path_mapping=None
        self.all_paths=[[[] for x in range(self.V)] for y in range(self.V)]
        self.affected_vertices = affected_vertices
        self.path_flight_mapping = None
        
    def add_edge(self, u, v, w):
        u=self.city_mapping[u]
        v=self.city_mapping[v]

        self.graph[u][v]+=[w]

    def find_all_paths_single_pair(self,source,dest,path=[]):
        if(len(path)>4):
            return []
        path=path+[source]
        if(source==dest):
            return [path]
        paths=[]
        for i in range(self.V):
            if(self.graph[source][i]!=[] and i not in path):
                newpaths=self.find_all_paths_single_pair(i,dest,path)
                for newpath in newpaths:
                    if(len(newpath)!=0):
                        paths.append(newpath)
        return paths
    
    def all_city_paths_all_pairs(self):
        self.all_paths=[[[] for x in range(self.V)] for y in range(self.V)]
        for i in range(self.V):
            print(f"Processing city {i+1}/{self.V}")
            for j in range(self.V):
                if(i!=j):
                    
                    paths=self.find_all_paths_single_pair(i,j)
                    self.all_paths[i][j]=paths

        # print_matrix(all_paths)
        return self.all_paths
    

    def find_all_flight_paths_all_pairs(self):
        self.path_mapping=[]
        possible_paths_all_pairs=self.all_city_paths_all_pairs()

        affected_cities = [self.city_mapping[city] for city in self.affected_vertices]
        for _i,possible_paths_one_pair in enumerate(possible_paths_all_pairs):
            for _j,possible_paths in enumerate(possible_paths_one_pair):
                if(_i not in affected_cities or _j not in affected_cities):
                    possible_paths_all_pairs[_i][_j]=[]
                    continue
                if(len(possible_paths_all_pairs[_i][_j])>0):
                    print(f"Processing city pair {_i+1}/{self.V} {_j+1}/{self.V}")
                    for _k,path in enumerate(possible_paths_all_pairs[_i][_j]):
                        
                        curr_paths = [[entry] for entry in self.graph[path[0]][path[1]]]
                        temp_paths = []
                        
                        for i in range(2,len(path)):
                            if(len(curr_paths)==0):
                                break
                            available_flights = self.graph[path[i-1]][path[i]]
                            # print(available_flights)
                            temp_paths = []
                            for flight in available_flights:
                                for curr_path in curr_paths:
                                    # print(curr_path)
                                    
                                    prev_arrival_date = inv.loc[curr_path[-1]]['ArrivalDateTime']
                                    # print(prev_arrival_time,prev_arrival_date)

                                     
                                    curr_departure_date = inv.loc[flight]['DepartureDateTime']

                                    time_diff = self.get_time_diff(prev_arrival_date,curr_departure_date)

                                    if(not data['Flight Connection']['Min Connection Time']['selected'] or data['Flight Connection']['Min Connection Time']['value']<=time_diff):
                                        if(not data['Flight Connection']['Max Connection Time']['selected'] or data['Flight Connection']['Max Connection Time']['value']>=time_diff):
                                            temp_paths.append(curr_path+[flight])
                                       
                                    

                            curr_paths = temp_paths
                        
                        curr_path_mapping=[]
                        m=0
                        for path in curr_paths:
                            if(len(path)>0):
                                self.path_mapping.append(path)
                                curr_path_mapping.append(len(self.path_mapping)-1)
                        # print(curr_paths)
                        # print(curr_path_mapping)
                        # print()
                        possible_paths_all_pairs[_i][_j][_k] = curr_path_mapping

                    possible_paths_all_pairs[_i][_j] = list(filter(lambda x: len(x)>0,possible_paths_all_pairs[_i][_j]))
                    possible_paths_all_pairs[_i][_j] = list(collapse(possible_paths_all_pairs[_i][_j]))

        self.path_city_compatibility = possible_paths_all_pairs
        return possible_paths_all_pairs
    

    def gen_path_pnr_compatibility_matrix(self):
        if self.path_city_compatibility is None:
            self.find_all_flight_paths_all_pairs()
        self.path_pnr_compatibility = [[0 for x in range(len(self.path_mapping))] for y in range(len(pnr))]

        for index,row in pnr.iterrows():
            source = self.city_mapping[row['ORIG_CD']]
            dest = self.city_mapping[row['DEST_CD']]

            for path in self.path_city_compatibility[source][dest]:
                self.path_pnr_compatibility[row['ind']][path]=1

        self.gen_path_flight_mapping()
        return self.path_pnr_compatibility
        

    def gen_path_flight_mapping(self):
        path_flight_mapping  = {inv.index[i]:[] for i in range(len(inv))}
        for i,path in enumerate(self.path_mapping):
            for flight in path:
                path_flight_mapping[flight].append(i)
        self.path_flight_mapping = path_flight_mapping
        return path_flight_mapping
    



    def print_graph(self):
        print_matrix(self.graph)


def graph_init(affected_cities):
    all_cities = list(set(inv['DepartureAirport']).union(set(inv['ArrivalAirport'])))

    g = Graph(all_cities,affected_cities)

    for index,row in inv.iterrows():
        g.add_edge(row['DepartureAirport'],row['ArrivalAirport'],index)

    g.gen_path_pnr_compatibility_matrix()
    return g

def main():
    global inv,pnr,sch,cancelled_flights
    inv = inv[~inv.index.isin(cancelled_flights['InventoryId'].to_list())]
    required_cities = list(set(cancelled_flights['DepartureAirport']).union(set(cancelled_flights['ArrivalAirport'])))
    pnr = pnr[pnr['DEP_KEY'].isin(cancelled_flights['Dep_Key'].to_list())]
    pnr['ind'] = [i for i in range(len(pnr))]
    print(required_cities)
    
    g = graph_init(required_cities)
    # sys.stdout = open('output.txt','w')

    with open('output.txt','w') as f:
        
        print(g.path_pnr_compatibility,file=f)
    # print(g.find_all_flight_paths_all_pairs())
    # g.print_graph()
    # print()
    # print_matrix(g.city_mapping)
    # print()
    # print_matrix(g.path_mapping)

    # print()
    
    # print()
    # print_matrix(g.path_city_compatibility)
    # print()
    # print_matrix(g.path_pnr_compatibility)
    



if __name__ == "__main__":
    main()






            







