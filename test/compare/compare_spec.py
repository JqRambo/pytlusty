import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import numpy as np


def read_spec(filename):
    """读取 SYNSPEC 光谱文件(fort.7/.spec 或 fort.17/.cont 格式):
    两列, 波长[Å] 和流量。返回 (wave, flux)。"""
    data = np.loadtxt(filename)
    return data[:, 0], data[:, 1]


def compare_spec(w1, f1, w2, f2):
    """把 f2 线性插值到 f1 的波长网格上, 返回相对差数组。"""
    f2i = np.interp(w1, w2, f2)
    rd = np.abs(f1 - f2i) / np.maximum(np.abs(f1), 1e-300)
    return rd


def plot_comparison(w1, f1, w2, f2, rd, label1, label2, output_file):
    """上图: 两条光谱(log 流量); 下图: 相对差。"""
    fig, (ax, axd) = plt.subplots(2, 1, figsize=(14, 8), sharex=True,
                                  gridspec_kw={'height_ratios': [2, 1],
                                               'hspace': 0.08})
    ax.semilogy(w1, f1, 'b-', linewidth=0.8, label=label1)
    ax.semilogy(w2, f2, 'r--', linewidth=0.8, label=label2)
    ax.set_ylabel(r'$H_\lambda$ (erg cm$^{-2}$ s$^{-1}$ Å$^{-1}$)',
                  fontsize=12)
    ax.legend(fontsize=11, frameon=False)
    ax.tick_params(axis='both', which='major', labelsize=10)

    axd.semilogy(w1, rd, 'k-', linewidth=0.6)
    axd.set_xlabel('wavelength (Å)', fontsize=12)
    axd.set_ylabel(r'$|\Delta H|/H$', fontsize=12)
    axd.tick_params(axis='both', which='major', labelsize=10)
    # axd.set_title(f"median={np.median(rd):.2e}, max={rd.max():.2e} "
    #               f"@ {w1[rd.argmax()]:.2f} Å", fontsize=10)

    # fig.suptitle(f'{label1}  vs  {label2}', fontsize=14)
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    # 命令行: compare_spec.py [Fortran.spec] [Python.spec] [输出.pdf]
    filename1 = sys.argv[1] if len(sys.argv) > 1 else \
        '/home/ubuntu/transform/teddy/test/synspec_fortran/FF.spec'
    filename2 = sys.argv[2] if len(sys.argv) > 2 else \
        '/home/ubuntu/transform/teddy/test/synspec_python/FF.spec'
    output_file = sys.argv[3] if len(sys.argv) > 3 else \
        '/home/ubuntu/transform/teddy/test/comparison_spec.pdf'
    label1, label2 = 'Fortran', 'Python'

    try:
        w1, f1 = read_spec(filename1)
        w2, f2 = read_spec(filename2)
        print(f'比较: {filename1}  vs  {filename2}')
        print(f'点数: {len(w1)} vs {len(w2)};  '
              f'波段: {w1[0]:.2f}-{w1[-1]:.2f} vs {w2[0]:.2f}-{w2[-1]:.2f} Å')

        rd = compare_spec(w1, f1, w2, f2)
        print(f"{'量':<8}{'中位差':>12}{'最大差':>12}{'最大差位置':>14}")
        print(f"{'flux':<8}{np.median(rd):>12.3e}{rd.max():>12.3e}"
              f"{w1[rd.argmax()]:>12.2f} Å")

        plot_comparison(w1, f1, w2, f2, rd, label1, label2, output_file)
        print(f"Comparison plot saved to {output_file}")

    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
