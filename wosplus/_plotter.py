from matplotlib import pyplot as plt
from venn import draw_venn, generate_colors


def _plot_sets(wps, title, figsize):
    """
    Plot the venn diagram given and wosplus object,
    Params:
        wps:  wosplus object
    Returns:
        plt: matplotlib pyplot object
        v  : venn3 object
    """
    if not hasattr(wps, 'WOS'):
        raise Exception('plotter', 'Web of Science data no loaded')
    if not hasattr(wps, 'SCP'):
        raise Exception('plotter', 'Scopus data no loaded')
    if not hasattr(wps, 'SCI'):
        raise Exception('plotter', 'Scielo data no loaded')

    labels = ["SCP", "SCI", "WOS"]

    petal_labels = {}
    petal_labels["001"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo == "WOS"].shape[0]
    petal_labels["010"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo == "SCI"].shape[0]
    petal_labels["011"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo ==
                                          "WOS_SCI"].shape[0]
    petal_labels["100"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo == "SCP"].shape[0]
    petal_labels["101"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo ==
                                          "WOS_SCP"].shape[0]
    petal_labels["110"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo ==
                                          "SCI_SCP"].shape[0]
    petal_labels["111"] = wps.WOS_SCI_SCP[wps.WOS_SCI_SCP.Tipo ==
                                          "WOS_SCI_SCP"].shape[0]
    plt.figure(figsize=figsize)
    v = draw_venn(
        petal_labels=petal_labels, dataset_labels=labels,
        hint_hidden=False, colors=generate_colors(n_colors=3),
        figsize=(8, 8), fontsize=14, legend_loc="best", ax=None)
    plt.title(title)
    plt.show()
    return plt, v
