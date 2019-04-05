#!/usr/bin/env python3

from wosplus import *

WOS_file = 'CIB_Wos.xlsx'
SCI_file = 'CIB_Scielo.xlsx'
SCP_file = 'CIB_Scopus.csv'

cib = wosplus('tests/drive.cfg')

cib.load_biblio(WOS_file)
cib.load_biblio(SCI_file, prefix='SCI')
cib.load_biblio(SCP_file, prefix='SCP')

print('before merge: {}'.format(
    cib.WOS.shape[0] + cib.SCI.shape[0] + cib.SCP.shape[0]))

cib.merge(left="WOS", right="SCI", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
          right_DOI="SCI_DI", right_TI="SCI_TI", right_extra_journal="SCI_SO", right_author="SCI_AU", right_year="SCI_PY")


if True:
    print('intial: {}'.format(cib.WOS.shape[0] + cib.SCI.shape[0]))
    print('final : {}'.format(cib.WOS_SCI.shape))

cib.merge(left="WOS_SCI", right="SCP", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
          right_DOI="SCP_DOI", right_TI="SCP_Title", right_extra_journal="SCP_Source title", right_author="SCP_Authors", right_year="SCP_Year")


if True:
    print('intial: {}'.format(cib.WOS_SCI.shape[0] + cib.SCP.shape[0]))
    print('final : {}'.format(cib.WOS_SCI_SCP.shape))
