from matplotlib_venn import venn3
from matplotlib import pyplot as plt


def _plot_sets(wps, title, figsize):
    '''
    Plot the venn diagram given and wosplus object,
    Params:
        wps:  wosplus object
    Returns:
        plt: matplotlib pyplot object
        v  : venn3 object
    '''
    if not hasattr(wps, 'WOS'):
        raise Exception('plotter', 'Web of Science data no loaded')
    if not hasattr(wps, 'SCP'):
        raise Exception('plotter', 'Scopus data no loaded')
    if not hasattr(wps, 'SCI'):
        raise Exception('plotter', 'Scielo data no loaded')

    WOS_1 = wps.WOS.shape[0]
    SCP_2 = wps.SCP.shape[0]
    WOS_SCP_3 = wps.WOS_SCP.shape[0]
    SCI_4 = wps.SCI.shape[0]
    WOS_SCI_5 = wps.WOS_SCI.shape[0]
    SCI_SCP_6 = wps.SCI_SCP.shape[0]
    WOS_SCI_SCP_7 = wps.WOS_SCI_SCP.shape[0]
    plt.figure(figsize=figsize)
    v = venn3(subsets=(WOS_1, SCP_2, WOS_SCP_3, SCI_4, WOS_SCI_5,
                       SCI_SCP_6, WOS_SCI_SCP_7), set_labels=('WOS', 'SCP', 'SCI'))
    plt.title(title)
    plt.show()
    return plt, v
