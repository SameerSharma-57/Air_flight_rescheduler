import json
import pandas as pd
def get_score(pnr, arrival_delay, equipment, flight_path, std):
    with open('./backend/parameter_values.json','r') as f:
        data = json.load(f)
    
    score1, score2 = 0, 0
    pnr_data_b = pd.read_csv('D:\Adarsh\C++\Other\Tinkering_Lab_Project\Backend\\final_data\PNRB.csv')
    pnr_data_p = pd.read_csv('D:\Adarsh\C++\Other\Tinkering_Lab_Project\Backend\\final_data\PNRP.csv')

    req_pnr = {}
    req_flight = {}
    for i in data['PNR']:
        if data['PNR'][i]['selected'] == True:
            req_pnr[i] = data['PNR'][i]
    for i in data['Flight']:
        if data['Flight'][i]['selected'] == True:
            req_flight[i] = data['Flight'][i]
    print(req_flight)
    print(req_pnr)
    print(data['PNR']['SSR'])
    p = pnr_data_p[pnr_data_p['RECLOC'] == pnr]
    b = pnr_data_b[pnr_data_b['RECLOC'] == pnr]
    p.index = range(len(p))
    b.index = range(len(b))
    b = b.iloc[0:1,:]
    print(p)
    print(b)
    l = ['INFT', 'WCHR', 'WCHS', 'WCHC', 'LANG', 'CHLD', 'MAAS', 'UNMR', 'BLND', 'DEAF', 'EXST', 'MEAL', 'NSST', 'NRPS']
    # FirstClass -> F and class A
    # BusinessClass -> J and class C
    # Economy -> Y and class K
    for i in req_pnr:
        if i == 'SSR':
            for j in range(len(p)):
                if p['SSR_CODE_CD1'][j] in l:
                    score1 += req_pnr[i]['score']
            print("SSR", score1)
        elif i == 'cabinF':
            for j in range(len(b)):
                if "First" in b['COS_CD'][j] or "first" in b['COS_CD'][j]:
                    score1 += req_pnr[i]['score']
            print("cabinF", score1)
        elif i == 'cabinB':
            for j in range(len(b)):
                if "Business" in b['COS_CD'][j] or "business" in b['COS_CD'][j]:
                    score1 += req_pnr[i]['score']
            print("cabinB", score1)

        elif i == 'cabinY':
            for j in range(len(b)):
                if "Economy" in b['COS_CD'][j] or "economy" in b['COS_CD'][j]:
                    score1 += req_pnr[i]['score']
            print("cabinY", score1)
        elif i == 'classA':
            for j in range(len(b)):
                if "First" in b['COS_CD'][j] or "first" in b['COS_CD'][j]:
                    score1 += req_pnr[i]['score']
            print("classA", score1)
        elif i == 'classC':
            for j in range(len(b)):
                if "Business" in b['COS_CD'][j] or "business" in b['COS_CD'][j]:
                    score1 += req_pnr[i]['score']
            print("classC", score1)
        elif i == 'classK':
            for j in range(len(b)):
                if "Economy" in b['COS_CD'][j] or "economy" in b['COS_CD'][j]:
                    score1 += req_pnr[i]['score']
            print("classK", score1)
        elif i == 'connection':
            pass
        elif i == 'booking_type':
            pax = b['PAX_CNT'][0]
            if pax > 1:
                score1 += req_pnr[i]['score']
            print("booking_type", score1)
        elif i == 'no_of_pax':
            pax = b['PAX_CNT'][0]
            score1 += req_pnr[i]['score'] * pax
            print("no_of_pax", score1, pax)
        elif i == 'loyalty':
            for j in range(len(p)):
                if p['TierLevel'][j].lower() == 'gold':
                    score1 += 1600
                elif p['TierLevel'][j].lower() == 'silver':
                    score1 += 1500
                elif p['TierLevel'][j].lower() == 'platinum':
                    score1 += 1800
                elif 'presidential' in p['TierLevel'][j].lowers():
                    score1 += 2000

    if arrival_delay <= 6*60 and 'arrival_delay_6' in req_flight:
        score2 += req_flight['arrival_delay_6']['score']
    elif arrival_delay <= 12*60 and 'arrival_delay_12' in req_flight:
        score2 += req_flight['arrival_delay_12']['score']
    elif arrival_delay <= 24*60 and 'arrival_delay_24' in req_flight:
        score2 += req_flight['arrival_delay_24']['score']
    elif arrival_delay <= 48*60 and 'arrival_delay_48' in req_flight:
        score2 += req_flight['arrival_delay_48']['score']

    if 'equipment' in req_flight:
        score2 += req_flight['equipment']['score']

    if len(flight_path) == 2 and 'city_pairs_same' in req_flight:
        score2 += req_flight['city_pairs_same']['score']
    elif len(flight_path) == 3 and 'city_pairs_near' in req_flight:
        score2 += req_flight['city_pairs_near']['score']
    elif 'city_pairs_different' in req_flight:
        score2 += req_flight['city_pairs_different']['score']
    
    if std <= 6*60 and 'std6' in req_flight:
        score2 += req_flight['std6']['score']
    elif std <= 12*60 and 'std12' in req_flight:
        score2 += req_flight['std12']['score']
    elif std <= 24*60 and 'std24' in req_flight:
        score2 += req_flight['std24']['score']
    elif std <= 48*60 and 'std48' in req_flight:
        score2 += req_flight['std48']['score']

    if len(flight_path) > 2 and 'stopover' in req_flight:
        score2 += req_flight['stopover']['score']
    
    return score1*score2

# print(get_score('DRGS80', 5*60, 'A320', ['DEL', 'BOM'], 5*60))

    
