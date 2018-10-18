import pandas as pd
import numpy as np
try:
    from ._google_drive_tools import *
    from ._wos_parser import *
    from ._wos_scp import *
except (SystemError, ImportError):
    from _google_drive_tools import *
    from _wos_parser import *
    from _wos_scp import *

def wos_to_excel(wos_txt_google_drive_key='0B5o48PQb6nBUZm82UGNYSVRiaE0'):
    gf={'savedrecs.txt':wos_txt_google_drive_key}
    wos_txt=download_file_from_google_drive(gf['savedrecs.txt'],binary=False)
    wos=wos_to_list_to_pandas(wos_txt)
    wos=fill_NaN(wos)
    return wos

def DataFame_to_pajek(\
    wos_dataframe,
    pajek_file='fichero.net',
    emisor_column='TI',
    receptor_column='CR',
    receptor_separator='\n',
    receptor='CR',
    emisor_index='TI_IND',
    receptor_index='CR_IND'):
    """
       ========= WOS to Pajek ==============
                     
       From a DataFrame with the columns of Web of Science txt file, 
       convert the data from an emisor and a receptor WOS identifiers
       (see sample input below), into a Pajek .net file. 
       
       Also returns a simplified DataFrame with emisor (receptor) column, 
       the corresponding emisor (receptor) index starting from 1 
       (number of emisor entries + 1), along with the edges of the network. 
           
    Input:
    
    wos_txt_google_drive_key='0B5o48PQb6nBUZm82UGNYSVRiaE0',
    pajek_file='fichero.net',
    emisor_column='TI',
    receptor_column='CR',
    receptor_separator='\n',
    receptor='CR',
    emisor_index='TI_IND',
    receptor_index='CR_IND'
    
    Referencias:
    http://mrvar.fdv.uni-lj.si/pajek/
    """ 
    

    if pajek_file.find('.net')==-1:
        pajek_file=pajek_file+'.net'
    wos=wos_dataframe
    wos[emisor_index]=wos.index.values+1
    wos[receptor_column]=wos[receptor_column].str.strip()

    CR=pd.DataFrame()
    step=10
    print(wos.shape[0]-step)
    for i in wos.index:
        if i%step==0:
            print(i,end='\r')

        cr=wos.loc[i,receptor_column].split(receptor_separator)
        tmp=pd.DataFrame({emisor_index:wos.loc[i,emisor_index]*np.ones(len(cr)).astype(int),\
                          receptor:cr,\
                          emisor_column:((wos.loc[i,emisor_column].strip()+':::')*len(cr)).split(':::')[:-1]})
        CR=CR.append(tmp).reset_index(drop=True)

    CR_u=CR.drop_duplicates(receptor).reset_index(drop=True)
    CR_u[receptor_index]=CR_u.index.values+1+wos.shape[0]
    RR=CR_u[[receptor_index,receptor]]
    vinc=CR.merge(RR,on=receptor,how='left')
    vinc=vinc.sort_values(receptor).reset_index(drop=True)
    vinc['Edges']=vinc[emisor_index].astype(str)+' '+vinc[receptor_index].astype(str)+' '+'1'

    #write file:
    a1=vinc[[emisor_index,emisor_column]].drop_duplicates(emisor_index).sort_values(emisor_index).reset_index(drop=True)
    a1[emisor_column]=a1[emisor_column].str.replace('\n',' ').str.replace('^([0-0a-zA-Z]+)$',r'\1 ')
    a2=vinc[[receptor_index,receptor]].drop_duplicates(receptor).sort_values(receptor_index).reset_index(drop=True)
    a2[receptor]=a2[receptor].str.replace('\n',' ').str.replace('^([0-0a-zA-Z]+)$',r'\1 ')
    a3=vinc[['Edges']]
    
    f=open(pajek_file,'w')
    f.write('*Vertices %d %d\n' %(CR_u.shape[0]+wos.shape[0],wos.shape[0]))
    a1.to_csv(f,sep=' ',header=False,index=False)
    a2.to_csv(f,sep=' ',header=False,index=False)
    f.write('*Edges\n')
    a3.to_csv(f,header=False,index=False)
    f.close()
    print('Created Pajek file name is: %s' %pajek_file)
    
    return vinc

def wos_to_pajek(\
    wos_txt_google_drive_key='0B5o48PQb6nBUZm82UGNYSVRiaE0',
    pajek_file='fichero.net',
    emisor_column='TI',
    receptor_column='CR',
    receptor_separator='\n',
    receptor='CR',
    emisor_index='TI_IND',
    receptor_index='CR_IND'):
    """
       ========= WOS to Pajek ==============
                     
       From the google drive key of a Web of Science txt file with public link,
       convert the data from an emisor and a receptor WOS identifiers 
       (see sample input below), into a Pajek .net file. 
       
       Also returns a simplified DataFrame with emisor (receptor) column, 
       the corresponding emisor (receptor) index starting from 1 
       (number of emisor entries + 1), along with the edges of the network. 
           
    Input:
    
    wos_txt_google_drive_key='0B5o48PQb6nBUZm82UGNYSVRiaE0',
    pajek_file='fichero.net',
    emisor_column='TI',
    receptor_column='CR',
    receptor_separator='\n',
    receptor='CR',
    emisor_index='TI_IND',
    receptor_index='CR_IND'
    
    Referencias:
    http://mrvar.fdv.uni-lj.si/pajek/
    """ 
    wos=wos_to_excel(wos_txt_google_drive_key=wos_txt_google_drive_key)
    vinc=DataFame_to_pajek(\
    wos,
    pajek_file=pajek_file,
    emisor_column=emisor_column,
    receptor_column=receptor_column,
    receptor_separator=receptor_separator,
    receptor=receptor,
    emisor_index=emisor_index,
    receptor_index=receptor_index)
    return vinc
