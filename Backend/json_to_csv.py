import json
import pandas as pd

with open('sample_output.json','r') as f:
    best_samples = json.load(f)


df = []
for i in best_samples:
    if(best_samples[i]==1.0):
        
        x = i.split('_')
        df.append([int(x[1]),int(x[2]),['hi','hello']])

df.sort()
df=pd.DataFrame(df)
df.to_csv('final_output.csv',index=False,header=['pnr','path','temp'])
