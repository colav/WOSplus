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
        raise Exception('wosplus', 'Web of Science data no loaded')
    if not hasattr(wps, 'SCP'):
        raise Exception('wosplus', 'Scopus data no loaded')
    if not hasattr(wps, 'SCI'):
        raise Exception('wosplus', 'Scielo data no loaded')

    WOS_DOIS = set(wps.WOS["DI"])
    SCP_DOIS = set(wps.SCP["SCP_DOI"])
    SCI_DOIS = set(wps.SCI["SCI_DI"])
    plt.figure(figsize=figsize)
    v = venn3([WOS_DOIS, SCP_DOIS, SCI_DOIS], ('WOS', 'SCP', 'SCI'))
    plt.title(title)
    plt.show()
    return plt, v
