"""Compare synthetic spectra with laspec spline normalization (same scheme
and style as figure/f5.py of the paper).
Usage:
  python3 compare_spec_fixed.py out.pdf label1:ref.spec label2:test.spec
Top: normalized spectra (continuum normalization with the iterative
double-smoothing spline ported from laspec.normalization.normalize_spectrum_spline,
Zhang Bo, https://github.com/hypergravity/laspec, after the normSpectrum.m of
Chao Liu); bottom: residual F2 - F1 in normalized flux. matplotlib default fonts.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.interpolate import interp1d

PLOT_LO, PLOT_HI = 3600.0, 7500.0


def read_spec(fn):
    d = np.loadtxt(fn)
    return d[:, 0], d[:, 1]


def smooth_spline(x, y, p):
    """Reinsch/de Boor cubic smoothing spline, equal weights, 0<p<1.
    Ported from laspec.extern.interpolate.SmoothSpline (de Boor 1978,
    Practical Guide to Splines, Eq. XIV.6-9)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = x.size
    dx = np.diff(x)
    dx1 = 1.0 / dx
    dydx = np.diff(y) / dx
    R = sparse.spdiags([dx[1:], 2.0 * (dx[:-1] + dx[1:]), dx[:-1]],
                       [-1, 0, 1], n - 2, n - 2)
    Q = sparse.spdiags([dx1[:-1], -(dx1[:-1] + dx1[1:]), dx1[1:]],
                       [0, -1, -2], n, n - 2)
    QQ = 6.0 * (1.0 - p) * (Q.T @ Q) + p * R
    u = 2.0 * sparse.linalg.spsolve((QQ + QQ.T).tocsc(), np.diff(dydx))
    Qu = np.diff(np.concatenate(
        [[0.0], np.diff(np.concatenate([[0.0], u, [0.0]])) * dx1, [0.0]]))
    a = y - 6.0 * (1.0 - p) * Qu
    c = np.concatenate([[0.0], 3.0 * p * u])
    d = np.diff(np.concatenate([c, [0.0]])) * dx1 / 3.0
    b = np.diff(a) * dx1 - (c + d * dx) * dx
    a = a[:n - 1]

    def evaluate(xnew):
        xnew = np.asarray(xnew, float)
        i = np.clip(np.searchsorted(x, xnew) - 1, 0, n - 2)
        t = xnew - x[i]
        return a[i] + b[i] * t + c[i] * t**2 + d[i] * t**3

    return evaluate


def normalize_spectrum_spline(wave, flux, p=1e-6, q=0.5, lu=(-1, 3),
                              binwidth=30, niter=2):
    """Iterative double-smoothing spline normalization, ported from
    laspec.normalization.normalize_spectrum_spline."""
    wave = np.asarray(wave, float)
    flux = np.asarray(flux, float)
    ind_good = np.isfinite(flux)
    nbins = int(np.ceil((wave[-1] - wave[0]) / binwidth) + 1)
    bincenters = np.linspace(wave[0], wave[-1], nbins)

    for _ in range(niter):
        flux_smoothed = smooth_spline(wave[ind_good], flux[ind_good], p)(wave)
        res = flux - flux_smoothed
        stdres = np.zeros(nbins)
        for ibin in range(nbins):
            in_bin = ind_good & (np.abs(wave - bincenters[ibin]) <= binwidth)
            stdres[ibin] = np.std(res[in_bin]) if in_bin.sum() > 1 else np.nan
        if np.isnan(stdres).any():
            good_bins = np.isfinite(stdres)
            stdres = interp1d(bincenters[good_bins], stdres[good_bins],
                              kind='linear', fill_value='extrapolate')(bincenters)
        stdres_interp = interp1d(bincenters, stdres, kind='linear')(wave)
        res1 = (res - np.percentile(res, 100 * q)) / stdres_interp
        ind_good = ind_good & (res1 > lu[0]) & (res1 < lu[1])
        if ind_good.sum() == 0:
            ind_good = np.isfinite(flux)
            break

    cont = smooth_spline(wave[ind_good], flux[ind_good], p)(wave)
    return flux / cont, cont


def main():
    output = sys.argv[1]
    (lab1, fn1), (lab2, fn2) = [a.split(':', 1) for a in sys.argv[2:4]]
    w1, f1 = read_spec(fn1)
    w2, f2 = read_spec(fn2)
    n1, _ = normalize_spectrum_spline(w1, f1)
    n2, _ = normalize_spectrum_spline(w2, f2)
    rd = np.interp(w1, w2, n2) - n1
    ard = np.abs(rd)
    imax = ard.argmax()
    print(f'residual ({lab2}-{lab1}): median|d|={np.median(ard):.3e}  '
          f'max|d|={ard.max():.3e} @ {w1[imax]:.1f} A')

    fig, (ax, axd) = plt.subplots(2, 1, figsize=(7.0, 5.0), sharex=True,
                                  gridspec_kw={'height_ratios': [1.5, 1.0],
                                               'hspace': 0.08})
    ax.plot(w1, n1, 'k-', lw=0.9, label=lab1)
    ax.plot(w1, np.interp(w1, w2, n2), 'r--', lw=0.7, label=lab2)
    ax.set_ylabel('normalized flux')
    ax.set_ylim(0.2, 1.4)
    ax.set_xlim(PLOT_LO, PLOT_HI)
    ax.legend(frameon=False, loc='upper right')

    axd.plot(w1, rd, 'k-', lw=0.5)
    axd.axhline(0, color='0.5', lw=0.6)
    axd.plot(w1[imax], rd[imax], 'rv', ms=6, zorder=5)
    axd.set_xlabel(r'wavelength ($\mathrm{\AA}$)')
    axd.set_ylabel(f'$F_{{\\rm {lab2}}} - F_{{\\rm {lab1}}}$')
    axd.set_xlim(PLOT_LO, PLOT_HI)
    axd.set_ylim(-1.4 * ard.max(), 1.4 * ard.max())

    fig.savefig(output, bbox_inches='tight')
    plt.close(fig)
    print('saved:', output)


if __name__ == '__main__':
    main()
