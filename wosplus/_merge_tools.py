import pandas as pd
import numpy as np

from unidecode import unidecode
try:
    from ._wos_scp import *
except (SystemError, ImportError):
    from _wos_scp import *
def df_split(dff,on,on_contains=None,Operator=None,condition=None,on_condition=None,on_not_condition=False):
    """
    After divide df DataFrame in two parts acording either a condition or str.contains or 
    check for empty string in the column 'on':
    The pair of returned dataframes corresponds to
    * on_contains='text' -> True,False
    * Operator='operator' (e.g: '=='); condition='text'
          -> True (e.g == 'text'), False (e.g != 'text')
    * on_not_condition or on_not_conditions are deprecated usage
    """
    import sys
    import operator
    otrue  = {">":  operator.gt,">=": operator.ge,"<":  operator.lt,
              "<=": operator.le,"!=": operator.ne,"==": operator.eq}
    ofalse = {">":  operator.le,">=": operator.lt,"<":  operator.ge,
              "<=": operator.gt,"!=": operator.eq,"==": operator.ne}
    if on_not_condition:
        Operator='!='
        condition=''
    elif on_condition is not None: 
        Operator='=='
        condition=condition
    df=dff.copy()
    if on_contains is not None:
        df_pureLEFT=df[df[on].str.contains(on_contains)].reset_index(drop=True)
        df_pureRIGHT=df[~df[on].str.contains(on_contains)].reset_index(drop=True)
    elif Operator is not None and condition is not None:
        df_pureLEFT=df[otrue[Operator](df[on],condition)].reset_index(drop=True)
        df_pureRIGHT=df[ofalse[Operator](df[on],condition)].reset_index(drop=True)
    else:
        sys.exit('on_contains or Operator conditions must be given')
        
    return df_pureLEFT,df_pureRIGHT

def cp_RIGHTcolumn_to_LEFTcolumn(df,on='UT',on_contains=None,on_condition=None,on_not_condition=False,\
                                 left='AU',right='SCP_Authors'):
    """
    After divide df DataFrame in two parts acording either a condition or str.contains on
    the column 'on': 
    cp one the column 'right' of the second part into the column 'left' of the second part.
    Returns the full dataframe organized according to the criteria in the 'on' column
    """
    df_pureLEFT,df_pureRIGHT=df_split(df,on,on_contains=on_contains,\
                                            on_condition=on_condition,on_not_condition=on_not_condition)     
    df_pureRIGHT[left]=df_pureRIGHT[right]

    return fill_NaN(df_pureLEFT.append(df_pureRIGHT,ignore_index=True))

def merge_by_series(left,right,\
            left_on='ST',right_on='Simple_Title',\
            left_series=pd.Series(),right_series=pd.Series(),\
            left_extra_on='SO',right_extra_on='UDEA_nombre revista o premio',\
            close_matches=False,cutoff=0.6,cutoff_extra=0.6):
    '''
    Merge with outer but returning left-inner, inner, right-inner
    WARNING: right_on cannot be empty
    '''
    #DEBUG:
    import sys
    left_keys=left.keys().values
    right_keys=right.keys().values
    if left_series.shape[0] and right_series.shape[0]:
        left[left_on]=left_series
        right[right_on]=right_series
    
        
    if right[right[right_on]==''].shape[0]:
        sys.exit('Right series cannot have empty elements with outer method')

    if not close_matches:
        kk=fill_NaN( left.merge(right,how='outer',left_on=left_on,right_on=right_on ) )
    else:
        kk=fill_NaN( merge_with_close_matches(left,right,left_on=left_on,right_on=right_on,\
            left_extra_on=left_extra_on,right_extra_on=right_extra_on,how='outer',cutoff=cutoff,full=True,\
                                      cutoff_extra=cutoff_extra) )        
        
    new_left=kk[kk[right_on]==''].drop( right_keys,axis='columns')
    if left_series.shape[0] or right_series.shape[0]:
        new_left=new_left.drop( [left_on,right_on],axis='columns')
    
    inner=kk[np.logical_and(kk[left_on]!='',kk[right_on]!='')]
    if left_series.shape[0] or right_series.shape[0]:
        inner=inner.drop([left_on,right_on],axis='columns')
    
    new_right= kk[np.logical_and(kk[left_on]=='',kk[right_on]!='')].drop(left_keys,axis='columns') 
    if left_series.shape[0] or right_series.shape[0]:
        new_right=new_right.drop( [left_on,right_on] ,axis='columns')

    #if left_series.shape[0] and right_series.shape[0]:
    #    left=left.drop(left_on,axis='columns')
        
    return new_left.reset_index(drop=True),inner.reset_index(drop=True),new_right.reset_index(drop=True)

def clean(pds):
    if pds.shape[0]:
        return pds.str.lower().str.strip().str.replace('\"','').str.replace(\
                                '\n',' ').str.replace('\.','').map(unidecode)
    else:
        return pds

def split_translated_columns(df,on='SCP_Title',sep='\[',min_title=10,initialize=''):
    ''' 
    Creates new columns with the splite results of translates titles in the format lang1 `sep`lang2]`sep`.
    The new colums are called `on`_0 (not translated) `on`_1, and `on`_2.
    '''    
    if sep=='\[':
        trail='\]'
    elif sep=='\(':
        trail='\)'
    else:
        trail=''    

    it0=df[~df[on].str.contains('.* %s[A-Za-z0-0\s]{%d}' %(sep,min_title))\
               ][on].str.split('\s%s' %sep).str[0]
    it1=df[df[on].str.contains('.* %s[A-Za-z0-0\s]{%d}' %(sep,min_title))\
               ][on].str.split('\s%s' %sep).str[0]
    it2=df[df[on].str.contains('.* %s[A-Za-z0-0\s]{%d}' %(sep,min_title))\
               ][on].str.replace('%s$' %trail,'').str.split('\s%s' %sep).str[1]

    df['%s_0' %on]=initialize
    df['%s_1' %on]=initialize
    df['%s_2' %on]=initialize

    df.loc[it0.index.values,'%s_0' %on]=it0
    df.loc[it1.index.values,'%s_1' %on]=it1
    df.loc[it2.index.values,'%s_2' %on]=it2
    return df

def force_to_excel(df,file,**kwargs):
    '''
    Write to excel in case of exception:
       IllegalCharacterError
    '''
    try: 
        df.to_excel(file,**kwargs)
    except:
        print('Data frame unicode_escape replaced. Trying to save again...')
        df=wos_sci.applymap(lambda x: x.encode('unicode_escape').
                 decode('utf-8') if isinstance(x, str) else x).to_excel(file,**kwargs)
