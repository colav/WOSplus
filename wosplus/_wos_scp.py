import time
import sys
def get_close_matches_Levenshtein(word, possibilities,n=3,cutoff=0.6,full=False):
    '''Replaces difflib.get_close_matches with faster algortihm based on
       Levenshtein.ratio.
       HINT: Similarity increase significatively after lower() and unidecode()
 
       Refs: https://en.wikipedia.org/wiki/Levenshtein_distance
    '''
    import pandas as pd
    import Levenshtein
    if isinstance(possibilities,str):
        possibilities=[possibilities]
    rl=['']
    rs=pd.DataFrame()
    MATCH=False
    for p in possibilities:
        similarity=Levenshtein.ratio(word,p)
        #print(word,'::',p,similarity)
        #sys.exit()
        if similarity>=cutoff:
            MATCH=True
            rs=rs.append({'similarity':similarity,'match':p},ignore_index=True)

    if MATCH:
        rs=rs.sort_values('similarity',ascending=False).reset_index(drop=True)
        if full:
            return list(rs['match'][:n].values),list(rs['similarity'][:n].values)
        else:
            return list(rs['match'][:n].values)
    else:
        if full:
            return ([],0)
        else:
            return []
    
def check_hash(df,hashseries,in_hash,min_match=10):
    ''' hashseries obtained from dataframe df, e.g
          hashseris=df.some_column.str.replace('\W+','').str.lower().map(unicode)
        within which in_hash will be searched for match at least min_match characters
    '''
    comparision=True
    for si in reversed(range(0,len(in_hash)+1)):
        chk=df[hashseries.str.match(in_hash[:si])]
        if chk.shape[0]>0:
            return comparision,chk
            #break
        if si<min_match:
            comparision=False
            return comparision,pd.DataFrame()
        
            
def columns_add_prefix(df,prefix):
    return df.rename_axis( dict( (key,prefix+'_'+key) for key in df.columns.values) , axis=1)

def fill_NaN(df):
    '''Fill NaN entries with proper empty values
     Type  : dtype: Fill with
     string: "0"  : ''
     float : "float64"
    '''
    for key in df.columns:
        if df[key].dtype=='O':
            df[key]=df[key].fillna('')
        elif df[key].dtype=='float64':
            df[key]=df[key].fillna(0.0)
    return df
def read_excel_fill_NaN(*args, **kwargs):
    '''Fill NaN entries with proper empty values
     Type  : dtype: Fill with
     string: "0"  : ''
     float : "float64"
    '''
    df=pd.read_excel(*args, **kwargs)
    df=fill_NaN(df)
    return df
    
#To add to main publications object:
def add_sjr_info_from_issn(self,SJR,column_issn='SN',SJR_column_journal='SJR_Title',SJR_column_issn='SJR_Issn'):
    '''self is an publication object and SJR is the info for a journal in column SJR_Issn'''
    if not SJR_column_journal in self.articles.columns:
        sys.exit("Run first the the more exact and fast add_sjr_info")
            
    self.articles=fill_NaN(self.articles)
    kk=self.articles[self.articles[SJR_column_journal]=='']
    for issn in kk[column_issn].str.replace('-','').unique():
        mtch=SJR[SJR[SJR_column_issn].str.contains(issn)].reset_index(drop=True)
        if mtch.shape[0]==1:
            moa=kk[ kk[column_issn].str.replace('-','')==issn ]
            if moa.shape[0]>=1:
                #DEBUG: more filters if 
                for key in SJR.columns.values:
                    self.articles.loc[moa.index.values,key]=mtch.ix[0][key]
                    
    return self

def add_sjr_info_from_journal(self,SJR,column_journal='SO',SJR_column_journal='SJR_Title'):
    '''self is an publication object and SJR is the info for a journal in column SJR_Issn'''
    if not SJR_column_journal in self.articles.columns:
        sys.exit("Run first the more exact and fast add_sjr_info")
        
    self.articles=fill_NaN(self.articles)
    kk=self.articles[self.articles[SJR_column_journal]=='']
    #kk_hash_SO=kk[column_journal].str.replace('\W+','').str.lower().str.strip().map(unidecode)
    SJR_hash_Title=SJR[SJR_column_journal].str.replace('\W+','').str.lower().str.strip().map(unidecode)
    for title in kk[column_journal].str.lower().str.strip().unique():
        hash_match,mtch=check_hash(SJR,SJR_hash_Title,re.sub('\W+','',title).lower().strip() )
        if hash_match:
            mtch=mtch.reset_index(drop=True)
            if mtch.shape[0]>1:
                newtitle=re.sub('\W+',' ',title)
                mtch=SJR[SJR[SJR_column_journal].str.lower().str.strip().str.match('%s ' %newtitle)]
                if mtch.shape[0]:
                    mtch=mtch.reset_index(drop=True)
             
            if mtch.shape[0]==1:
                moa=kk[ kk[column_journal].str.lower().str.strip()==title ]
                if moa.shape[0]>=1:
                    for key in SJR.columns.values:
                        self.articles.loc[moa.index.values,key]=mtch.ix[0][key]
    return self

def add_sjr_info(self,SJR,column_journal='SO',SJR_column_journal='SJR_Title'):
    '''self is an publication object and SJR is the info for a journal in column SJR_Title'''
    self.articles=self.articles.reset_index(drop=True)
    for joa in np.intersect1d( self.articles[column_journal].str.lower().str.strip().unique(),\
                                   SJR[SJR_column_journal].str.lower().str.strip().unique() ):
        moa=self.articles[ self.articles[column_journal].str.lower() == joa ]
        if moa.shape[0]:
            mtch=SJR[SJR[SJR_column_journal].str.lower().str.strip()==joa].reset_index(drop=True)
            if mtch.shape[0]==1:
                #DEBUG: filter by ISSN if >1:
                for key in SJR.columns.values:
                    self.articles.loc[moa.index.values,key]=mtch.ix[0][key]
    
    return self
        
def merge_with_close_matches(left,right,left_on='ST',right_on='UDEA_simple_título',\
                             left_extra_on='SO',right_extra_on='UDEA_nombre revista o premio',\
                             how='inner',\
                                 n=1,cutoff=0.6,full=True,cutoff_extra=0.6):
    '''For each entry of the column: left_on of DataFrame left (cannot have empty fields),
       try to find the close match inside each row of right DataFrame, by comparing with
       the right_on entry of the row. When a row match is found, the full right row is appended
       to the matched row in the left DataFrame.
       If the similarity between the entries at left_on and right_on is less than 0.8,
       an additional check is performed between the entries left_extra_on and right_extra_on
       of the matched row.
       
       how implemented: inner and left (Default: inner)
    '''
    import numpy as np
    from unidecode import unidecode
    import pandas as pd
    #import sys #import globally
    #print(left[left_on][0])
    #sys.exit()
    words=left[left_on].str.lower().map(unidecode)
    possibilities=right[right_on].str.lower().map(unidecode)
    
    joined=pd.DataFrame()
    mi=np.array([])
    for i in left.index:
        if i%100==0:
            print('.', end="")
        joined_series=left.loc[i]
        #joined_series=joined_series.append(pd.Series( {similarity_column:0} ))
        title,similarity=get_close_matches_Levenshtein(words[i],possibilities,n=n,cutoff=cutoff,full=full)
        #print(i,words[i],title,similarity) #cutuff 0.6 0.7 0.8 0.85 0.91 0.95
        #sys.exit()
        if title:
            mtch=right[possibilities==title[0]]
            chk_cutoff=similarity[0] # >=cutoff, e.g 0.65 0.95 0.81 0.86 0.9 0.96
            crosscheck=cutoff+0.2 #0.8 # e.g. 0.8 0.9 0.9 0.9 0.9 0.9
            if crosscheck>=1:
                crosscheck=0.95 #force check if match worst than this (by experience)
            if chk_cutoff<crosscheck:  #e.g 0.65<0.8 0.95~<0.9 0.81~<0.0 0.86<0.9 0.91<~0.9 0.96~<0.9
                if get_close_matches_Levenshtein( unidecode(left[left_extra_on][i].lower()),\
                                                 [unidecode(mtch[right_extra_on][mtch.index[0]].lower())],cutoff=cutoff_extra ): #cutoff=0.6
                    chk_cutoff=crosscheck+0.1
            if chk_cutoff>=crosscheck:
                joined_series=joined_series.append(mtch.loc[mtch.index[0]])
                if how=='outer':
                    mi=np.concatenate((mi,mtch.index.values))
                #joined_series[similarity_column]=similarity[0]
            if how=='inner':
                joined=joined.append(joined_series,ignore_index=True)
        if how=='left' or 'outer':
            joined=joined.append(joined_series,ignore_index=True)
    if how=='outer':
        joined=joined.append( right.drop(right.index[ list(mi.astype(int)) ] ).reset_index(drop=True)   )
    return joined


def merge_udea_points(original_df,target_df,check_columns=['UDEA_simple_title','UDEA_título','UDEA_título'],\
                      check_against_colums=['TI','SCP_Title','TI'],\
                      drop_not_UDEA_columns=True,old_extra_column='UDEA_nombre revista o premio',\
                      new_extra_column='SO',DEBUG=False):
    '''
    # STEPS: 0:Simplified, 1:full title including translations, 2:reverse translation in UDEA  
    drop_not_UDEA_columns=True:  Remove other columns, if False remove UDEA_ ones
    '''
    #Specific of STEP
    STEP=0
    old=original_df #100

    old_column=check_columns[STEP]
    new=target_df[target_df[check_against_colums[STEP]]!='']
    new_column=check_against_colums[STEP]

    st=time.time()
    
    joined=merge_with_close_matches(old,new,old_column,new_column,old_extra_column,new_extra_column,\
                                 n=1,cutoff=0.6,full=True)
    print(time.time()-st)
    joined=fill_NaN(joined)
    if DEBUG:
        print('check final shape after STEP %d: %d' %(STEP,joined.shape[0]) )

    udea_found=joined[joined[new_column]!=''].reset_index(drop=True)  #42
    original_df=joined[joined[new_column]==''].reset_index(drop=True) #58

    if DEBUG:
        print(STEP,'->',udea_found.shape,original_df.shape,udea_found.shape[0]+original_df.shape[0])

    original_df_not_scp_title=original_df[original_df.SCP_Title==''].reset_index(drop=True) #33
    original_df=original_df[original_df.SCP_Title!=''].reset_index(drop=True) #25
    print(STEP,':',udea_found.shape[0],original_df_not_scp_title.shape[0],original_df.shape[0])
    if DEBUG:
        print(STEP,'->',original_df_not_scp_title.shape,original_df.shape,original_df_not_scp_title.shape[0]+original_df.shape[0])

    
    for STEP in [1,2]:
        for k in original_df.columns:
            if drop_not_UDEA_columns:
                if k.find('UDEA')==-1:
                    original_df=original_df.drop(k,axis=1)
            else:
                if k.find('UDEA')>-1:
                    original_df=original_df.drop(k,axis=1)

        old=original_df #1:25; #2: 58
        old_column=check_columns[STEP]
        new=target_df[target_df[check_against_colums[STEP]]!='']
        new_column=check_against_colums[STEP]

        st=time.time()
        
        joined=merge_with_close_matches(old,new,old_column,new_column,old_extra_column,new_extra_column,\
                                     n=1,cutoff=0.6,full=True)
        print(time.time()-st)

        joined=fill_NaN(joined)

        if STEP==1:
            original_df=original_df_not_scp_title #1: 33

        if new_column in joined: #1: False; #2: True
            udea_found        =udea_found.append(joined[joined[new_column]!=''],ignore_index=True) #2:7+42=49
            if STEP==1:
                original_df=original_df.append(joined[joined[new_column]==''],ignore_index=True)
            else:
                original_df=joined[joined[new_column]==''] #2:51
            if DEBUG:
                print(STEP,':::>',joined[joined[new_column]!=''].shape[0],joined[joined[new_column]==''].shape[0])
        else: #1: True; 2: False
            #udea found is the same because not new mathc was found
            if STEP==1:
                original_df=original_df.append(joined,ignore_index=True) #1: 33+25=58
        
        print(STEP,':',udea_found.shape[0],original_df.shape[0])

    target_df_UDEA=udea_found #2: 49
    target_df_UDEA=target_df_UDEA.append(original_df,ignore_index=True) #49+51
    target_df_UDEA=fill_NaN(target_df_UDEA)

    print(udea_found.shape[0],original_df.shape[0],target_df_UDEA.shape[0])
    return target_df_UDEA

def merge_udea_points_new(original_df,target_df,check_columns=['UDEA_simple_title','UDEA_título','UDEA_título'],\
                      check_against_colums=['TI','SCP_Title','TI'],\
                      drop_not_UDEA_columns=True,old_extra_column='UDEA_nombre revista o premio',\
                      new_extra_column='SO',how='inner',DEBUG=False):
    '''
    # STEPS: 0:Simplified, 1:full title including translations, 2:reverse translation in UDEA  
    drop_not_UDEA_columns=True:  Remove other columns, if False remove UDEA_ ones
    '''
    #Specific of STEP
    STEP=0
    old=original_df #100

    old_column=check_columns[STEP]
    new=target_df[target_df[check_against_colums[STEP]]!='']
    new_column=check_against_colums[STEP]

    st=time.time()
    
    joined=merge_with_close_matches(old,new,old_column,new_column,old_extra_column,new_extra_column,\
                                 how=how,n=1,cutoff=0.6,full=True)
    print(time.time()-st)
    joined=fill_NaN(joined)
    if DEBUG:
        print('check final shape after STEP %d: %d' %(STEP,joined.shape[0]) )

    udea_found=joined[joined[new_column]!=''].reset_index(drop=True)  #42
    original_df=joined[joined[new_column]==''].reset_index(drop=True) #58 

    if DEBUG:
        print(STEP,'->',udea_found.shape,original_df.shape,udea_found.shape[0]+original_df.shape[0])

    original_df_not_scp_title=original_df[original_df.SCP_Title==''].reset_index(drop=True) #33
    original_df=original_df[original_df.SCP_Title!=''].reset_index(drop=True) #25
    print(STEP,':',udea_found.shape[0],original_df_not_scp_title.shape[0],original_df.shape[0])
    if DEBUG:
        print(STEP,'->',original_df_not_scp_title.shape,original_df.shape,original_df_not_scp_title.shape[0]+original_df.shape[0])

    
    for STEP in [1,2]:
        for k in original_df.columns:
            if drop_not_UDEA_columns:
                if k.find('UDEA')==-1:
                    original_df=original_df.drop(k,axis=1)
            else:
                if k.find('UDEA')>-1:
                    original_df=original_df.drop(k,axis=1)

        old=original_df #1:25; #2: 58
        old_column=check_columns[STEP]
        new=target_df[target_df[check_against_colums[STEP]]!='']
        new_column=check_against_colums[STEP]

        st=time.time()
        
        joined=merge_with_close_matches(old,new,old_column,new_column,old_extra_column,new_extra_column,\
                                     how=how,n=1,cutoff=0.6,full=True)
        print(time.time()-st)

        joined=fill_NaN(joined)

        if STEP==1:
            original_df=original_df_not_scp_title #1: 33

        if new_column in joined: #1: False; #2: True
            udea_found        =udea_found.append(joined[joined[new_column]!=''],ignore_index=True) #2:7+42=49
            if STEP==1:
                original_df=original_df.append(joined[joined[new_column]==''],ignore_index=True) 
            else:
                original_df=joined[joined[new_column]==''] #2:51
            if DEBUG:
                print(STEP,':::>',joined[joined[new_column]!=''].shape[0],joined[joined[new_column]==''].shape[0])
        else: #1: True; 2: False
            #udea found is the same because not new mathc was found
            if STEP==1:
                original_df=original_df.append(joined,ignore_index=True) #1: 33+25=58
        
        print(STEP,':',udea_found.shape[0],original_df.shape[0])

    target_df_UDEA=udea_found #2: 49
    target_df_UDEA=target_df_UDEA.append(original_df,ignore_index=True) #49+51
    target_df_UDEA=fill_NaN(target_df_UDEA)

    print(udea_found.shape[0],original_df.shape[0],target_df_UDEA.shape[0])
    return target_df_UDEA

def get_doi(
        surname=None,#'florez',
        title=r'Baryonic violation of R-parity from anomalous $U(1)_H$',
        other='',
        DOI=None,
        check_text=None,
        check_mesagges_key=None,
        similarity=0.6,
        JSON=False):
        '''
        Search for a DOI and check against the full DOI info. If JSON is set True, the full
        info is returned as a python dictionary
        
        Implementations:
        
        1) Search and check for a DOI by surname and title or if only DOI is given, just check the DOI.
        
          The checking is doing by comparing check_text with the check_mesagges_key from the full info.
          By default the given 'title' is used for the check.
          
          For other possible check_mesagges_key's, see in a browser the several keys of the 'mesagges'
          dictionary at:
             https://api.crossref.org/v1/works/DOI, 
          for example:
             https://api.crossref.org/v1/works/10.1103/physrevd.87.095010
          
        
        2) if only DOI is given, just get full info about the DOI without any checks.
           (only the key 'messages' is checed to exists)
        
        Examples:
        2) get_doi(surname='Florez',title='Baryonic violation of R-parity from anomalous U(1)H',JSON=True)
        3) get_doi(DOI)
        '''
        import requests
        #import time imported globally
        import sys
        import random
        
        if not check_text:
            check_text=title.lower()
        if not check_mesagges_key:
            check_mesagges_key='title' #'container-title'
        if not surname and DOI:
            if not check_text and not check_mesagges_key:
                similarity=0.1
                check_text='http://dx.doi.org/'
                check_mesagges_key='DOI'
                JSON=True
            
        doi=''
        if JSON:
            doi={}
        if not DOI:
            search=''
            if surname:
                search=surname
            if title:
                if len(search)>0:
                    search=search+', '+title
                else:
                    search=search+title
            if other:
                if len(search)>0:
                    search=search+', '+other

            r=requests.get('http://search.crossref.org/?q=%s' %search)
            urldoi='http://dx.doi.org/'

            DOI=''
            try:
                DOI=r.text.split(urldoi)[1].split("\',")[0].split('>\n')[0]
            except IndexError:
                DOI=''                        
        if DOI:
            json='https://api.crossref.org/v1/works/'
            rr=requests.get( json+DOI )
            if rr.status_code==200:
                if 'message' in rr.json():
                    if check_mesagges_key in rr.json()['message']:
                        if len(rr.json()["message"][check_mesagges_key]):
                            chk=get_close_matches_Levenshtein(check_text,\
                                                              rr.json()["message"][check_mesagges_key][0].lower(),\
                                                              n=1,cutoff=similarity)
                            if chk:
                                if "DOI" in rr.json()["message"]:
                                    doi=rr.json()["message"]["DOI"]
                    if JSON:  # Overwrite upon previous doi
                        doi=rr.json()["message"]
                                
                                    
        time.sleep( random.randint(1,3) )
        return doi
