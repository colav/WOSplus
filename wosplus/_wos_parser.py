import pandas as pd
import re
import sys
def wos_parser(wos_file):
    '''
    Convert a Web of Science text file into a pandas DataFrame.
    The input text file need to be generated according the instructions in:
    
    http://diging.github.io/tethne/getting_data.html
    '''

    f=open(wos_file)
    return wos_to_list_to_pandas(f)

def wos_to_list_to_pandas(f):
    '''
    Convert a Web of Science object file into a pandas DataFrame
    '''
    wostxt=f.readlines()
    return list_to_pandas(wostxt)
    
def list_to_pandas(wostxt):
    '''
    Convert a list of strings from in Web of Science format, into a pandas DataFrame
    '''
    if type(wostxt)!=list:
        sys.exit("Input must be a list: e.g. wos_txt.split('\n')")
    i=0
    wos=pd.DataFrame()
    row=pd.Series()
    #def wos(file,wos):
    record=False
    #saverow=False
    #addline=False
    for l in wostxt:
        i=i+1
        k=re.match('^[A-Z][A-Z0-9]\s',l) #Find element of record, eg: 'XX '
        if k:
            ky=k.group()
            if len(ky.strip())==2: # remove blank spaces: 'XX' 
                #addline=False
                key=ky.strip()
                if key=='PT': #'PT'
                    record=True #Initialize record
                    #saverow=True
                        
                value=ky.join(l.split(ky)[1:]) #remove 'XX ' from BEGINING of line
                    

        else: #continuation of element 
            ky='   ' #3 blanck spaces
            if re.match(ky,l):
                #addline=True
                value=value+ky.join(l.split(ky)[1:]) #remove '   ' from BEGINING of line
                
        #special cases
        k=re.match('^[A-Z][A-Z]$',l)
        if k:
            if k.group()=='ER': #''
                record=False #Finalize record
                    
        #print(record,':',l,end='')
        
        #Actions
        if record:
            row[key]=value #store elements in pandas Series
        else:
            if row.shape[0]>0:# and saverow:
                #print('store df',i)
                wos=wos.append(row,ignore_index=True) #store record in pandas DataFrame
                row=pd.Series() # row.shape[0]==0
                #saverow=False
        
        #if i>128:
        #    break
    return wos