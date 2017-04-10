
# Temporary fix: Required in order to work with pycharm.
import matplotlib as mpl
#mpl.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd

from .analysis import reshape_timeseries, clean_convert, get_LDC

__all__ = ['plot_heatmap', 'plot_3d', 'plot_percentiles', 'plot_rug', 'plot_boxplot', 'plot_LDC' ]

def plot_heatmap(Load, x='dayofyear', y='hour', aggfunc='sum', bins=8,
                palette='Oranges', colorbar=True, ax=None, **pltargs):
    """ Returns a 2D heatmap of the reshaped timeseries based on x, y
    Parameters:
        Load: 1D pandas with timed index
        x: Parameter for reshape_timeseries()
        y: Parameter for reshape_timeseries()
        bins: Number of bins for colormap
        palette: palette name (from colorbrewer, matplotlib etc.)
        **pltargs: Exposes matplotlib.plot arguments
    Returns
        2d heatmap
    """
    x_y = reshape_timeseries(Load, x=x, y=y, aggfunc=aggfunc)
    if ax is None:
        fig, ax = plt.subplots(figsize=(16, 6))

    cmap_obj = cm.get_cmap(palette, bins)
    heatmap = ax.pcolor(x_y, cmap=cmap_obj, edgecolors='w', **pltargs)
    if colorbar:
        fig.colorbar(heatmap)
    ax.set_xlim(xmax=len(x_y.columns))
    ax.set_ylim(ymax=len(x_y.index))
    ax.set_xlabel(x)
    ax.set_ylabel(y)


def plot_3d(Load, x='dayofyear', y='hour', aggfunc='sum', bins=15,
           palette='Oranges', colorbar=True, **pltargs):
    """ Returns a 30 plot of the reshaped timeseries based on x, y
    Parameters:
        Load: 1D pandas with timed index
        x: Parameter for reshape_timeseries()
        y: Parameter for reshape_timeseries()
        bins: Number of bins for colormap
        palette: palette name (from colorbrewer, matplotlib etc.)
        **pltargs: Exposes matplotlib.plot arguments
    Returns
        3d plot
    """
    import mpl_toolkits.mplot3d  # necessary for orojection=3d

    x_y = reshape_timeseries(Load, x=x, y=y, aggfunc=aggfunc)

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')
    cmap_obj = cm.get_cmap(palette, bins)
    X, Y = np.meshgrid(range(len(x_y.columns)), range(len(x_y.index)))
    surf = ax.plot_surface(X, Y, x_y, cmap=cmap_obj, rstride=1, cstride=1,
                           shade=False, antialiased=True, lw=0)
    if colorbar:
        fig.colorbar(surf)
    # Set viewpoint.
    # ax.azim = -130
    ax.elev = 45
    ax.auto_scale_xyz([0, len(x_y.columns)],
                      [0, len(x_y.index)],
                      [0, x_y.max().max()])
    ax.set_xlabel(x)
    ax.set_ylabel(y)


def plot_percentiles(Load, x='hour', zz='week', perc_list=[[5, 95], [25, 75], 50], ax=None, figsize=(10, 5),color='blue', **kwargs):
    """Plot predefined percentiles per timestep
    Arguments:
        Load: 1D pandas with timed index
        x (str): x axis aggregator. See reshape_timeseries()
        y (str): similar to above for y axis
        perc_list(list): List of percentiles to plot. If it is an integer then it will be plotted as a line.
        If it is list it has to contain two items and it will be plotted using fill_between()
        **kwargs: exposes arguments of plt.fill_between()
    Returns:
        Plot

    """
    if ax is None: #TODO
        ax=plt.gca()
    a = reshape_timeseries(Load, x=x, y=zz, aggfunc='mean')
    xx = a.columns.values

    #fig = plt.figure(figsize=figsize)
    #ax = fig.add_subplot(111)


    # TODO: s 2s 3s instead of percentiles

    for i in perc_list:
        if len(np.atleast_1d(i)) == 1:
            perc = a.apply(lambda x: np.nanpercentile(x.values, i), axis=0)
            ax.plot(xx, perc.values, color='black')
        elif len(np.atleast_1d(i)) == 2:
            perc0 = a.apply(lambda x: np.nanpercentile(x.values, i[0]), axis=0)
            perc1 = a.apply(lambda x: np.nanpercentile(x.values, i[1]), axis=0)

            ax.fill_between(xx, perc0, perc1, lw=.5, alpha=.3,color=color, **kwargs)
        else:
            raise ValueError('List items should be scalars or 2-item lists')

    ax.set_xlim(left=min(xx), right=max(xx))
    ax.set_xlabel(x)



def plot_boxplot(Load, by='day', **pltargs):
    """Return boxplot plot for each day of the week
    Arguments:
        Load : 1D pandas Series with timed index
        by: make plot by day or hour
        **pltargs: Exposes matplotlib.plot arguments
    """
    Load = clean_convert(Load,force_timed_index=True)

    if by == 'day':
        iter = Load.groupby(Load.index.weekday)
        labels = "Mon Tue Wed Thu Fri Sat Sun".split()
    elif by == 'hour':
        iter = Load.groupby(Load.index.hour)
        labels = np.arange(0, 24)
    else:
        raise NotImplementedError('Only "day" and "hour" are implemented')
    a = []
    for timestep, value in iter:
        a.append(value)
    plt.boxplot(a, labels=labels, **pltargs)
    # TODO : Generalize to return monthly, hourly etc.
    # TODO Is it really needed? pd.boxplot()


def plot_LDC(Load, x_norm=True, y_norm=False, color='black', **kwargs):
    a = get_LDC(Load, x_norm=x_norm, y_norm=y_norm,  **kwargs)
    #TODO: make it work with 2d
    plt.plot(*a, color=color)
    if x_norm:
        plt.xlim(0, 1)
        plt.xlabel('Normalized duration')
    else:
        plt.xlim(0, len(Load))
        plt.xlabel('Duration')
    if y_norm:
        plt.ylim(0,1)
        plt.ylabel('Normalized Power')
    else:
        plt.ylim(0, max(Load))
        plt.ylabel('Power')


def plot_rug(df_series, on_off=False, cmap='Greys', fig_title=''):
    """Create multiaxis rug plot from pandas Dataframe
    Parameters:
        df_series: 2D pandas with timed index
        on_off: if True all points that are above 0 will be plotted as one color.
                If False all values will be colored based on their value.
        cmap: palette name (from colorbrewer, matplotlib etc.)
    Returns:
        plot

    """
    def format_axis(iax):
        # Formatting: remove all lines (not so elegant)
        for spine in ['top','right','left','bottom']:
            iax.axes.spines[spine].set_visible(False)
            #iax.spines['right'].set_visible(False)

        # iax.xaxis.set_ticks_position('none')
        iax.yaxis.set_ticks_position('none')
        iax.get_yaxis().set_ticks([])
        iax.yaxis.set_label_coords(-.05, -.1)

    def flag_operation(v):
        if np.isnan(v) or v == 0:
            return False
        else:
            return True

    # check if Series or dataframe
    if len(df_series.shape) == 2:
        rows = len(df_series.columns)
    elif len(df_series.shape) == 1:
        df_series = df_series.to_frame()
        rows = 1
    else:
        raise ValueError("Has to be either Series or Dataframe")

    fig, axes = plt.subplots(nrows=rows, ncols=1, sharex=True,
                             figsize=(16, 0.25 * rows), squeeze=False,
                             frameon=False, gridspec_kw={'hspace': 0.15})

    for (item, iseries), iax in zip(df_series.iteritems(), axes.ravel()):
        format_axis(iax)
        iax.set_ylabel(item, rotation=0)
        if iseries.sum() > 0:
            if on_off:
                i_on_off = iseries.apply(flag_operation).replace(False, np.nan)
                i_on_off.plot(ax=iax, style='|', lw=.7, cmap=cmap)
            else:
                x = iseries.index
                y = np.ones(len(iseries))
                iax.scatter(x, y, marker='|', s=100,
                            c=iseries.values * 100, cmap=cmap)

    axes.ravel()[0].set_title(fig_title)
    axes.ravel()[-1].spines['bottom'].set_visible(True)  # axes.ravel()[-1] instead of iax?
    axes.ravel()[-1].set_xlim(min(x), max(x))


def plot_line_holidays():
    #ax.vspan if day == holiday
    #should work only with daily
    pass

def describe_load(Load):
    """Summary plot that describes the most important features of the passed timeseries """
    pass