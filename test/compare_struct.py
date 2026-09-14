"""Compare the atmospheric structures of converged TLUSTY models.
Usage:
  python3 compare_struct.py out.pdf label1:path1.7 label2:path2.7 [label3:path3.7]
The first model is the reference (residuals are computed relative to it).
Figure: top row T, ne, rho vs column mass M (log-log); bottom row relative
differences vs depth index.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

STYLE = ['-', '--', ':']
LW = [3.4, 2.2, 1.2]
ALPHA = [0.45, 0.75, 1.0]
COLOR = ['b', 'g', 'r']


def read_tlusty_model7(filename):
    with open(filename) as f:
        lines = f.readlines()
    n_depth, n_params = (int(x) for x in lines[0].split()[:2])
    all_data = []
    for line in lines[1:]:
        if line.strip():
            all_data.extend(float(x) for x in
                            line.replace('D', 'E').replace('d', 'e').split())
    all_data = np.array(all_data)
    dm = all_data[:n_depth]
    par = all_data[n_depth:].reshape(n_depth, n_params)
    return dm, par


def main():
    output = sys.argv[1]
    specs = [a.split(':', 1) for a in sys.argv[2:]]
    labels = [s[0] for s in specs]
    models = [read_tlusty_model7(s[1]) for s in specs]
    dm0, par0 = models[0]

    quants = [(0, r'$T$ (K)', r'$|\Delta T|/T$'),
              (1, r'$n_e$ (cm$^{-3}$)', r'$|\Delta n_e|/n_e$'),
              (2, r'$\rho$ (g cm$^{-3}$)', r'$|\Delta\rho|/\rho$')]
    depth = np.arange(1, len(dm0) + 1)

    fig = plt.figure(figsize=(9.5, 5.8))
    gs = GridSpec(2, 3, hspace=0.25, wspace=0.45)
    for k, (col, ylab, dlab) in enumerate(quants):
        v0 = par0[:, col]
        ax = fig.add_subplot(gs[0, k])
        axd = fig.add_subplot(gs[1, k])
        for i, (lab, (dm, par)) in enumerate(zip(labels, models)):
            v = par[:, col]
            ax.loglog(dm, v, COLOR[i] + STYLE[i], linewidth=LW[i],
                      alpha=ALPHA[i], label=lab)
            if i > 0:
                r = np.abs(v - v0) / np.maximum(np.abs(v0), 1e-300)
                axd.semilogy(depth, r, COLOR[i] + STYLE[i],
                             linewidth=LW[i], alpha=ALPHA[i],
                             label=f"{lab} med={np.median(r):.1e}")
                print(f"{lab:24s} {['T','ne','rho'][col]:4s} "
                      f"median={np.median(r):.3e}  max={r.max():.3e}")
        ax.set_xlabel(r'$M$ (g cm$^{-2}$)')
        ax.set_ylabel(ylab)
        ax.legend(frameon=False, loc='upper left', fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=9)
        axd.set_xlabel('depth index')
        axd.set_ylabel(dlab)
        axd.legend(frameon=False, fontsize=8)
        axd.tick_params(axis='both', which='major', labelsize=9)

    fig.savefig(output, dpi=300, bbox_inches='tight')
    plt.close()
    print('saved:', output)


if __name__ == '__main__':
    main()
