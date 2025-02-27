# Quick script to overplot power colour values
# Written by David Gardenier, 2015-2016

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import math
from collections import defaultdict
from scipy.stats import binned_statistic
import numpy as np
from pyx import *

ns={'4u_1705_m44':'4U 1705-44',
        '4U_0614p09':'4U 0614+09',
        '4U_1636_m53':'4U 1636-53',
        '4U_1702m43':'4U 1702-43',
        '4U_1728_34':'4U 1728-34',
        'aquila_X1':'Aql X-1',
        'cyg_x2':'Cyg X-2',
        'gx_5m1':'GX 5-1',
        'gx_17p2':'GX 17+2',
        'gx_339_d4':'GX 339-4', #BH system
        'gx_340p0':'GX 340+0',
        'gx_349p2':'GX 349+2',
        'HJ1900d1_2455':'HETE J1900.1-2455',
        'IGR_J00291p5934':'IGR J00291+5934',
        'IGR_J17498m2921':'IGR J17498-2921',
        'J1701_462':'XTE J1701-462',
        'KS_1731m260':'KS 1731-260',
        'sco_x1':'Sco X-1',
        'sgr_x1':'Sgr X-1',
        'sgr_x2':'Sgr X-2',
        'S_J1756d9m2508':'SWIFT J1756.9-2508',
        'v4634_sgr':'V4634 Sgr',
        'XB_1254_m690':'XB 1254-690',
        'xte_J0929m314':'XTE J0929-314',
        'xte_J1550m564':'XTE J1550-564', #BH system
        'xte_J1751m305':'XTE J1751-305',
        'xte_J1807m294':'XTE J1807-294',
        'xte_J1808_369':'SAX J1808.4-3648',
        'xte_J1814m338':'XTE J1814-338',
        'xte_J2123_m058':'XTE J2123-058'}


def getdata(obj,obsid,mode):

    path = '/scratch/david/master_project/' + obj + '/P' + obsid[:5] + '/' + obsid + '/' +mode + '_*.ps'
    ps = glob.glob(path)

    # Import data
    try:
        all_data = np.loadtxt(ps[0],dtype=float)
        inverted_data = np.transpose(all_data)
    except IOError:
        print 'No power spectrum'
        return

    # Give the columns their names
    ps = inverted_data[0]
    ps_error = inverted_data[1]
    freq = inverted_data[2]
    freq_error = inverted_data[3]
    ps_squared = inverted_data[4]
    num_seg = inverted_data[5][0]

    freqps_err = []
    for i in range(len(freq)):
        err = math.fabs(freq[i]*ps[i])*math.sqrt((freq_error[i]/float(freq[i]))**2 + (ps_error[i]/float(ps[i]))**2 + 2*(freq_error[i]*ps_error[i])/float(freq[i]*ps[i]))
        freqps_err.append(err)

    bin_means, bin_edges, binnumber = binned_statistic(freq, freq*ps, bins=np.logspace(-3,2, num=50))
    counts, bin_edges, binnumber = binned_statistic(freq, freq*ps, statistic='count', bins=np.logspace(-3,2, num=50))

    bin_errs = []
    old_count = 0
    for c in counts:
        if c==0:
            bin_errs.append(0)
            continue
        c = int(c)
        indexes = [i for i in range(old_count,old_count+c)]
        bin_err = 1/float(c)*math.sqrt(sum([e**2 for i, e in enumerate(freqps_err) if i in indexes]))
        bin_errs.append(bin_err)
        old_count = c

    bin_centres = np.logspace(-2.95,2.05, num=50)

    return bin_means, bin_edges, bin_centres, bin_errs

class empty:

    def __init__(self):
        pass
    def labels(self, ticks):
        for tick in ticks:
            tick.label=""

def plot_colours(n,N):

    cl = color.gradient.Rainbow.select(n, N)
    hststyle = [graph.style.histogram(lineattrs=[cl, style.linewidth.Thick,],autohistogrampointpos=0,fromvalue=1e-6,steps=1)]
    errstyle= [graph.style.symbol(size=0.0, symbolattrs=[cl]),
               graph.style.errorbar(size=0.0,errorbarattrs=[cl])]

    return hststyle,errstyle

def plotps():

    objects = [('IGR_J00291p5934', '90425-01-02-05', 'event'),#0-20
               ('aquila_X1', '50049-01-03-01', 'event'),#20-40
               ('aquila_X1','40432-01-05-00','event'),#40-60
               ('aquila_X1','50049-01-03-02','event'),#60-80
               ('S_J1756d9m2508', '94065-06-02-02', 'event'),#80-100
               ('S_J1756d9m2508', '94065-02-01-04', 'event'),#100-120
               ('HJ1900d1_2455', '92049-01-08-00', 'event'),#120-140
               ('v4634_sgr', '92703-01-02-01', 'event'),#140-160
               ('aquila_X1', '93076-01-05-00', 'event'),#160-180
               ('cyg_x2', '30046-01-12-00', 'binned'),#180-200
               ('cyg_x2', '90030-01-56-01', 'binned'),#200-220
               ('cyg_x2', '91009-01-46-00', 'binned'),#220-240
               ('sco_x1', '40020-01-01-07', 'binned'),#240-260
               ('sco_x1', '20053-01-01-05', 'binned'),#260-280
               ('sco_x1', '20053-01-02-05', 'binned'),#280-300
               ('cyg_x2', '30046-01-02-00', 'binned'),#300-320
               ('cyg_x2', '90030-01-32-00', 'binned'),#320-340
               ('sgr_x2', '30051-01-03-00', 'binned')]#340-360

    allinfo = zip(*objects)
    objects = allinfo[0]
    obsids = allinfo[1]
    modes = allinfo[2]

    # Set up plot details
    c=canvas.canvas()

    # Calculate coordinates of all plots
    plot_width = 4
    plot_height = 6
    xposition = []
    xposition += 3*[i for i in range(0,6*plot_width,plot_width)]
    yposition = [0 for i in range(0,6)]
    for i in range(2):
        yposition += [e-plot_height for e in yposition[-6:]]

    for q in range(len(objects)):
        obj = objects[q]
        obsid = obsids[q]
        mode = modes[q]

        print ns[obj]

        binmeans, binedges, bincentres, binerrs = getdata(obj,obsid,mode)
        nbinmeans = []
        for b in binmeans:
            if b < 1e-6 or math.isnan(b): #y axis limit
                nbinmeans.append(1e-6)
            else:
                nbinmeans.append(b)

        values = graph.data.values(x=binedges[:-1], y=nbinmeans)

        myticks = []
        if yposition[q]!=yposition[-1]:
            xtitle = " "
            xtexter=empty()
        else:
            xtitle = "Frequency (Hz)"
            xtexter=graph.axis.texter.mixed()
        if xposition[q]!=0.0:
            ytitle = ""
            ytexter=empty()
        else:
            ytitle="Power $\cdot$ Frequency"
            ytexter=graph.axis.texter.mixed()

        g=c.insert(graph.graphxy(width=plot_width,
                                 height=plot_height,
                                 xpos=xposition[q],
                                 ypos=yposition[q],
                                 x=graph.axis.log(min=1e-2,max=60,title=xtitle,texter=xtexter),
                                 y=graph.axis.log(min=1e-6,max=0.8,title=ytitle,texter=ytexter)))

        hststyle,errstyle = plot_colours(q,len(objects))
        g.plot(values,hststyle)
        g.plot(graph.data.values(x=bincentres[:-1], y=nbinmeans, dy=binerrs), errstyle)
        #xtext, ytext = g.pos(0.5, 0.5)
        xtext, ytext = xposition[q]+0.5*g.width, yposition[q]+0.95*g.height
        g.text(xtext,ytext, ns[obj], [text.halign.boxcenter, text.valign.top, text.size.small])
        xtext, ytext = xposition[q]+0.5*g.width, yposition[q]+0.05*g.height
        g.text(xtext,ytext, str(q*20) + '$^\circ$-' + str((q+1)*20) + '$^\circ$', [text.halign.boxcenter, text.valign.bottom, text.size.normalsize])

    outputfile = '/scratch/david/master_project/plots/publication/ps/overview'
    c.writePDFfile(outputfile)


if __name__=='__main__':
    plotps()
