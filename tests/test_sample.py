#!/usr/bin/env python3

from wosplus import *

WOS_file='CIB_Wos.xlsx'
SCI_file='CIB_Scielo.xlsx'
SCP_file='CIB_Scopus.csv'

cib=wosplus('drive.cfg')

cib.load_biblio(WOS_file)
cib.load_biblio(SCI_file,prefix='SCI')
cib.load_biblio(SCP_file,prefix='SCP')

print('before merge: {}'.format( cib.WOS.shape[0]+cib.SCI.shape[0]+cib.SCP.shape[0] )  )

cib.merge(left='WOS',right='SCI')

if True:
    print('intial: {}'.format( cib.WOS.shape[0]+cib.SCI.shape[0]) )
    print('final : {}'.format(  cib.WOS_SCI.shape) )

cib.merge(left='WOS_SCI',right='SCP')

if True:
    print('intial: {}'.format( cib.WOS_SCI.shape[0]+cib.SCP.shape[0]) )
    print('final : {}'.format(  cib.WOS_SCI_SCP.shape) )
