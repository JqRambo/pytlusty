"""Generate publication-quality figures (f1-f4) for the PyTLUSTY/PySYNSPEC paper.

All figures are vector PDFs saved into the RAA journal directory (and copied to
the ApJS directory). Data sources: Fortran TLUSTY/SYNSPEC reference runs and
the Python reimplementation test runs under teddy/test/ (this script lives in
teddy/test/compare/ alongside the other comparison scripts).

Style note: matplotlib default fonts are used throughout (no explicit font
settings); the convergence plot (f3) follows the style of tlusty/gui/tlusty.py
(pconv): log10 of the maximum relative change versus iteration, 'ko--' style.
"""

import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

_HERE = os.path.dirname(os.path.abspath(__file__))
TEST = os.path.abspath(os.path.join(_HERE, '..'))                  # teddy/test
BASE = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))      # project root
OUT = os.path.join(BASE, 'RAA__Research_in_Astronomy_and_Astrophysics__journal')
OUT2 = os.path.join(BASE, 'ApJS_PyTLUSTY')

F_FORT = os.path.join(TEST, 'tlusty_22500_fortran/FF.7')
F_SER = os.path.join(TEST, 'tlusty_22500_py_serial/FF.7')
F_PAR = os.path.join(TEST, 'tlusty_22500_py_parallel/FF.7')
M6_FORT = os.path.join(TEST, 'tlusty_22500_fortran/FF.6')
M6_SER = os.path.join(TEST, 'tlusty_22500_py_serial/FF.6')
M6_PAR = os.path.join(TEST, 'tlusty_22500_py_parallel/FF.6')
L_FORT = os.path.join(TEST, 'tlusty_22500_fortran/FF.9')
L_SER = os.path.join(TEST, 'tlusty_22500_py_serial/FF.9')
SPEC_FORT = os.path.join(TEST, 'synspec_fortran/FF.spec')
SPEC_PY = os.path.join(TEST, 'synspec_python/FF.spec')


def save(fig, name):
    """Save into both paper directories."""
    for out in (OUT, OUT2):
        fig.savefig(os.path.join(out, name), bbox_inches='tight')
    plt.close(fig)
    print(name, 'done')


# ---------------------------------------------------------------- data I/O
def read_tlusty_model7(filename):
    """Read a TLUSTY model atmosphere file (fort.7 format)."""
    with open(filename) as f:
        lines = f.readlines()
    first = lines[0].split()
    n_depth, n_params = int(first[0]), int(first[1])
    data = []
    for line in lines[1:]:
        if line.strip():
            line = line.replace('D', 'E').replace('d', 'e')
            data.extend(float(x) for x in line.split())
    data = np.array(data)
    dm = data[:n_depth]
    params = data[n_depth:].reshape(n_depth, n_params)
    return {'n_depth': n_depth, 'n_params': n_params,
            'dm': dm, 'parameters': params}


def read_convergence(filename):
    """Read FF.9 log; return (iteration numbers, global max |change|)."""
    rows = []
    with open(filename) as f:
        for line in f:
            t = line.split()
            if len(t) >= 9:
                try:
                    rows.append((int(t[0]),
                                 float(t[6].replace('D', 'E'))))
                except ValueError:
                    continue
    rows = np.array(rows)
    iters = np.unique(rows[:, 0]).astype(int)
    chmax = np.array([np.abs(rows[rows[:, 0] == it, 1]).max()
                      for it in iters])
    return iters, chmax


def read_spec(filename):
    """Read a SYNSPEC spectrum: keep only lines with exactly 2 floats."""
    wave, flux = [], []
    with open(filename) as f:
        for line in f:
            t = line.split()
            if len(t) != 2:
                continue
            try:
                wave.append(float(t[0].replace('D', 'E')))
                flux.append(float(t[1].replace('D', 'E')))
            except ValueError:
                continue
    return np.array(wave), np.array(flux)


# ------------------------------------------------------------------- f1
def make_f1():
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(9.6, 3.9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis('off')

    ec = '#3a3a3a'
    fc_input = '#f2f2f2'
    fc_tlusty = '#eef3f9'
    fc_synspec = '#f6f1e7'

    def box(x, y, w, h, text, fc='white', lw=0.9, weight='normal'):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle='round,pad=0,rounding_size=1.2',
                                    fc=fc, ec=ec, lw=lw))
        ax.text(x + w / 2, y + h / 2, text,
                va='center', ha='center', weight=weight)

    def panel(x, y, w, h, title, fc):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.0))
        ax.text(x + w / 2, y + h - 3.4, title,
                weight='bold', va='center', ha='center')

    def arrow(x1, y1, x2, y2, dashed=False):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                     arrowstyle='-|>', lw=1.0,
                                     mutation_scale=11, color=ec,
                                     linestyle='--' if dashed else '-',
                                     shrinkA=0, shrinkB=0))

    # input
    box(0.5, 13, 15, 14, 'input\n$T_{\\rm eff}$, $\\log g$,\nelements &\nabundances',
        fc=fc_input)
    arrow(15.5, 20, 20.5, 20)

    # PyTLUSTY panel
    panel(20.5, 5, 26, 31, 'PyTLUSTY (atmosphere)', fc_tlusty)
    box(23, 26.5, 21, 5, 'TT: LTE (gray start)')
    box(23, 19.5, 21, 5, 'TF: NLTE/C (continua)')
    box(23, 12.5, 21, 5, 'FF: NLTE/L (blanketed)')
    arrow(33.5, 26.4, 33.5, 24.7)
    arrow(33.5, 19.4, 33.5, 17.7)
    ax.text(34.6, 25.5, '.7', style='italic', va='center', color='#555555')
    ax.text(34.6, 18.5, '.7', style='italic', va='center', color='#555555')
    ax.text(34.0, 7.0, 'CL/ALI + Ng acceleration',
            style='italic', va='center', ha='center', color='#555555')
    arrow(21.5, 4.4, 23.5, 12.3, dashed=True)
    ax.text(19.5, 2.2, 'optional start: previous grid model (.7)',
            style='italic', va='center', ha='left', color='#555555')

    arrow(46.5, 20, 51, 20)

    # converged model
    box(51, 14.5, 11, 11, 'converged\nmodel (.7)')
    arrow(62, 20, 66.5, 20)

    # PySYNSPEC panel
    panel(66.5, 7, 19, 27, 'PySYNSPEC\n(synthesis)', fc_synspec)
    box(68.5, 22.5, 15, 5.5, 'model + line list\n(+ NLTE b-factors)')
    box(68.5, 14.5, 15, 5.5, 'per-wavelength\nformal solution')
    arrow(76, 22.4, 76, 20.2)
    ax.text(76, 9.0, 'natural/Stark/vdW\nbroadening',
            style='italic', va='center', ha='center', color='#555555')

    arrow(85.5, 20, 89.5, 20)

    # outputs
    box(89.5, 8, 10, 24,
        '.spec\nspectrum\n\n.cont\ncontinuum\n\n.id\nline IDs\n\n.eqw\nEWs')

    save(fig, 'f1.pdf')


def read_tauross(filename6):
    """Read the TAUROSS column from the FINAL MODEL ATMOSPHERE table in the
    FF.6 run log (the .7 file stores only the mass depth, not the optical
    depth). Follows compare/compare3_tau.py."""
    with open(filename6) as f:
        lines = f.readlines()
    ih = next(i for i, l in enumerate(lines) if 'TAUROSS' in l)
    tau = []
    for line in lines[ih + 1:]:
        t = line.split()
        if len(t) < 3:
            if tau:
                break
            continue
        try:
            int(t[0])
            tau.append(float(t[2]))
        except ValueError:
            if tau:
                break
    return np.array(tau)


# ------------------------------------------------------------------- f2
def make_f2():
    m_fort = read_tlusty_model7(F_FORT)
    m_ser = read_tlusty_model7(F_SER)
    m_par = read_tlusty_model7(F_PAR)
    t_fort = read_tauross(M6_FORT)
    t_ser = read_tauross(M6_SER)
    t_par = read_tauross(M6_PAR)
    depth = np.arange(1, m_fort['n_depth'] + 1)

    pf, ps, pp = m_fort['parameters'], m_ser['parameters'], m_par['parameters']

    quantities = [(0, r'$T$ (K)', r'$|\Delta T|/T$'),
                  (1, r'$n_e$ (cm$^{-3}$)', r'$|\Delta n_e|/n_e$'),
                  (2, r'$\rho$ (g cm$^{-3}$)', r'$|\Delta\rho|/\rho$')]
    panel_ids = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']

    fig, axes = plt.subplots(2, 3, figsize=(7.0, 4.6),
                             gridspec_kw={'hspace': 0.32, 'wspace': 0.52,
                                          'height_ratios': [1.4, 1.0]})
    stats = {}
    for k, (icol, ylab, dlab) in enumerate(quantities):
        vf, vs, vp = pf[:, icol], ps[:, icol], pp[:, icol]
        rs = np.abs(vs - vf) / np.abs(vf)
        rp = np.abs(vp - vf) / np.abs(vf)
        stats[ylab] = (np.median(rs), rs.max(), np.median(rp), rp.max())

        ax = axes[0, k]
        ax.loglog(t_fort, vf, 'k-', lw=1.2, label='Fortran')
        ax.loglog(t_ser, vs, 'r--', lw=0.9, label='PyTLUSTY')
        ax.loglog(t_par, vp, color='b', ls=':', lw=1.4,
                  label='PyTLUSTY-MP')
        ax.set_xlabel(r'$\tau_{\rm ross}$')
        ax.set_ylabel(ylab)
        if k == 0:
            ax.legend(frameon=False, loc='upper left', handlelength=1.4,
                      borderaxespad=0.2)
        ax.text(0.95, 0.06, panel_ids[k], transform=ax.transAxes,
                va='bottom', ha='right')

        axd = axes[1, k]
        axd.semilogy(depth, rs, 'r-', lw=1.0)
        axd.semilogy(depth, rp, 'b--', lw=1.0)
        axd.set_ylabel(dlab)
        axd.set_xlabel('depth index')
        axd.text(0.96, 0.95, panel_ids[k + 3], transform=axd.transAxes,
                 va='top', ha='right')
        axd.set_ylim(bottom=1e-6)
        axd.set_xlim(1, m_fort['n_depth'])

    save(fig, 'f2.pdf')
    for k, v in stats.items():
        print('  %s: serial med %.2e max %.2e; parallel med %.2e max %.2e'
              % ((k,) + v))


# ------------------------------------------------------------------- f3
def make_f3():
    """Convergence history, following the pconv style of tlusty/gui/tlusty.py:
    log10 of the global maximum relative change versus iteration."""
    it_f, mx_f = read_convergence(L_FORT)
    it_s, mx_s = read_convergence(L_SER)

    fig, ax = plt.subplots(figsize=(4.8, 3.4))
    ax.plot(it_f, np.log10(mx_f), 'ko', ls='--', label='Fortran TLUSTY')
    ax.plot(it_s, np.log10(mx_s), 'rs', ls='--', mfc='none',
            label='PyTLUSTY (serial)')
    ax.axhline(-3, color='0.35', ls=':')
    ax.text(1.0, -2.85, r'convergence threshold CHMAX $= 10^{-3}$',
            color='0.25')
    ax.set_xlabel('iteration')
    ax.set_ylabel(r'log(max. relative change)')
    ax.set_xlim(0.5, max(it_f.max(), it_s.max()) + 0.5)
    ax.set_ylim(-4, 1.6)
    ax.legend(frameon=False, loc='upper right')
    ax.xaxis.set_major_locator(plt.MultipleLocator(4))
    fig.tight_layout()
    save(fig, 'f3.pdf')
    fmt = lambda a: ' '.join('%.2e' % v for v in a)
    print('  Fortran  iters 1..%d: first: %s ... last: %s'
          % (len(mx_f), fmt(mx_f[:3]), fmt(mx_f[-3:])))
    print('  PySerial iters 1..%d: first: %s ... last: %s'
          % (len(mx_s), fmt(mx_s[:3]), fmt(mx_s[-3:])))


# ------------------------------------------------------------------- f4
def normalize_spectrum_flux(w, f):
    """Normalize by the median flux in 4500-5500 A (compare_all_normal2.py)."""
    mask = (w >= 4500) & (w <= 5500)
    med = np.median(f[mask]) if mask.any() else 0.0
    return f / med if med > 0 else f


def make_f4():
    w1, f1 = read_spec(SPEC_FORT)
    w2, f2 = read_spec(SPEC_PY)
    n1 = normalize_spectrum_flux(w1, f1)
    n2 = normalize_spectrum_flux(w2, f2)
    rd = n2 - n1
    ard = np.abs(rd)
    nz = ard[ard > 0]
    imax = ard.argmax()
    frac_ident = 100.0 * np.mean(ard == 0)

    fig, (ax, axd) = plt.subplots(2, 1, figsize=(7.0, 5.0), sharex=True,
                                  gridspec_kw={'height_ratios': [1.5, 1.0],
                                               'hspace': 0.08})
    ax.plot(w1, n1, 'k-', lw=0.9, label='Fortran SYNSPEC')
    ax.plot(w2, n2, 'r--', lw=0.7, label='PySYNSPEC')
    ax.set_ylabel('normalized flux')
    ax.set_ylim(0, 3.5)
    ax.legend(frameon=False, loc='upper right')
    ax.text(0.02, 0.05, '(a)', transform=ax.transAxes)

    axd.plot(w1, rd, 'k-', lw=0.5)
    axd.axhline(0, color='0.5', lw=0.6)
    axd.plot(w1[imax], rd[imax], 'rv', ms=6, zorder=5)
    axd.annotate('max deviation %.1e\nat %.1f $\\mathrm{\\AA}$'
                 % (rd[imax], w1[imax]),
                 xy=(w1[imax], rd[imax]), xytext=(w1[imax] + 900,
                 rd[imax] * 0.65),
                 arrowprops=dict(arrowstyle='->', lw=0.8))
    axd.text(0.02, 0.92,
             'median $|\\Delta F|$ = 0 '
             '(identical at %.1f%% of points)' % frac_ident,
             transform=axd.transAxes, va='top')
    axd.set_xlabel(r'wavelength ($\mathrm{\AA}$)')
    axd.set_ylabel(r'$F_{\rm py} - F_{\rm Fortran}$')
    axd.text(0.02, 0.06, '(b)', transform=axd.transAxes)
    axd.set_xlim(3600, 7500)
    ax.set_xlim(3600, 7500)
    axd.set_ylim(-1.4 * ard.max(), 1.4 * ard.max())

    save(fig, 'f4.pdf')
    print('  spectrum: median |dF| = %.3e (over all %d points, normalized); '
          'median of nonzero = %.3e; max = %.3e at %.2f A; '
          'identical fraction %.1f%%'
          % (np.median(ard), len(ard), np.median(nz), ard.max(),
             w1[imax], frac_ident))


# ------------------------------------------------------------------- f5
def make_f5():
    """Benchmark bar chart (not used in the paper; kept for reference)."""
    labels = ['Fortran\nTLUSTY', 'PyTLUSTY\nserial',
              'PyTLUSTY\n10 processes']
    times = [30.0, 25200.0, 2700.0]
    human = [r'$\approx$30 s', r'$\approx$7 h', r'$\approx$45 min']
    colors = ['#444444', '#c23b3b', '#3b6fc2']

    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    x = np.arange(3)
    ax.bar(x, times, width=0.58, color=colors, edgecolor='k', lw=0.7)
    ax.set_yscale('log')
    ax.set_ylabel('wall-clock time (s)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(10, 1.5e6)
    for xi, t, h in zip(x, times, human):
        ax.text(xi, t * 1.3, h, ha='center', va='bottom')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'f5.pdf'), bbox_inches='tight')
    plt.close(fig)
    print('f5.pdf done')


if __name__ == '__main__':
    make_f1()
    make_f2()
    make_f3()
    make_f4()
