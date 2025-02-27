import pandas as pd
from plot_power_colours import findbestdataperobsid, findbestdata

objects = ['sgr_x1',
           '4u_1705_m44',
           'sgr_x2',
           'v4634_sgr',
           'XB_1254_m690',
           'xte_J2123_m058']

def path(o):
    return '/scratch/david/master_project/' + o + '/info/database.csv'


for obj in objects:

    print obj

    db = pd.read_csv(path(obj))
    db = db[(db.pc1.notnull())]
    df = db.groupby('obsids').apply(findbestdataperobsid)
    df = df.reset_index(drop=True)
    c = ['obsids','pc1','pc1_err','pc2','pc2_err']
    df.to_csv('/scratch/david/master_project/' + obj + '/info/pcs_' + obj + '.csv', cols = c, names=c)
 
