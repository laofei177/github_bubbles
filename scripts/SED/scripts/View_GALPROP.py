""" Plots fits file integrated over energy """

import numpy as np
import pyfits
import healpy
from matplotlib import pyplot
import healpylib as hlib

##################################################################################################### parameters


binmin = 11
binmax = 15

smooth_map = True
mask_point_sources = True

scale_min = -4e-6
scale_max = 8e-6

normalized = False
unit = 'GeV / (s sr cm^2)'

cmap = pyplot.cm.hot_r # jet, hot

map_fn = '../data/Source_refit_3FGL_40PS_resid_signal_bubbles_flux.fits'
save_fn = '../plots/Source_refit_3FGL_40PS_resid_signal_bubbles_flux_highlowE_hot.pdf'
mask_fn = '../data/ps_mask_3FGL_OG_nside128.npy'

View_GALPROP = True

##################################################################################################### constants

GeV2MeV = 1000.
delta = 0.346573590092441
smooth_sigma = np.deg2rad(.5)
npix = 196608
nside = healpy.npix2nside(npix)

##################################################################################################### load data from a fits file

hdu = pyfits.open(map_fn)
data = hdu[1].data.field('Spectra')
Es = hdu[2].data.field('MeV')/GeV2MeV


if normalized:
    data /= (binmax - binmin + 1)


##################################################################################################### transpose the data matrix

data = data.T
if View_GALPROP:
    plot_map = Es[binmax]**2 * data[binmax]
else:
    plot_map = data[binmax]
    
##################################################################################################### find the mask

mask = np.ones(npix)
if mask_point_sources:
    mask = np.load(mask_fn)

##################################################################################################### sum over energy bins (from binmin to binmax)

print 'sum over energy bins...'
for i in range(binmin, binmax):
    for j in range(len(plot_map)):
        if View_GALPROP:
            plot_map[j] += Es[i]**2 * data[i][j]
        else:
            plot_map[j] += data[i][j]


##################################################################################################### smooth with smooth_sigma Gaussian

if smooth_map:
    plot_map = np.array(hlib.heal(plot_map, mask), dtype = np.float64)
    plot_map = healpy.smoothing(plot_map, sigma=smooth_sigma)

for pixel in xrange(npix):
    if mask[pixel] == 0:
        plot_map[pixel] = None

  

##################################################################################################### show Mollweide view skymap

emin = Es[binmin] * np.exp(-delta/2)
emax = Es[binmax] * np.exp(delta/2)

title = 'E = %.1f' %emin + ' - %.1f' %emax + ' GeV'

healpy.mollview((plot_map), unit=unit, title = title,  min=scale_min, max=scale_max, cmap=cmap)
healpy.graticule(dpar=10., dmer=10.)

pyplot.savefig(save_fn)