import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec


def read_tlusty_model7(filename):
    """读取 TLUSTY 模型大气文件（fort.7 / MOD.7 格式）。"""
    with open(filename, 'r') as f:
        lines = f.readlines()

    first_line = lines[0].split()
    n_depth = int(first_line[0])
    n_params = int(first_line[1])

    all_data = []
    for line in lines[1:]:
        if line.strip():
            line_processed = line.replace('D', 'E').replace('d', 'e')
            all_data.extend(float(x) for x in line_processed.split())

    all_data = np.array(all_data)
    dm_values = all_data[:n_depth]
    parameters = all_data[n_depth:].reshape(n_depth, n_params)

    column_names = ['T', 'ne', 'rho'] + \
        [f'level_{i+1}' for i in range(n_params - 3)]
    df = pd.DataFrame(parameters, columns=column_names)
    df.insert(0, 'dm', dm_values)
    df.insert(0, 'depth_index', range(1, n_depth + 1))
    return {'n_depth': n_depth, 'n_params': n_params,
            'dm': dm_values, 'parameters': parameters, 'dataframe': df}


def rel_diff(x, y):
    return np.abs(x - y) / np.maximum(np.abs(y), 1e-300)


def main():
    # 三方比较: Fortran 参考 / Python 串行 / Python 并行
    # (质量深度 M 横轴版本; 光深横轴版本见 compare3_tau.py)
    f_fort = '/home/ubuntu/transform/teddy/test/tlusty_22500_fortran/FF.7'
    f_ser = '/home/ubuntu/transform/teddy/test/tlusty_22500_py_serial/FF.7'
    f_par = '/home/ubuntu/transform/teddy/test/tlusty_22500_py_parallel/FF.7'
    output_file = sys.argv[1] if len(sys.argv) > 1 else \
        '/home/ubuntu/transform/teddy/test/comparison3_22500.pdf'

    try:
        m_fort = read_tlusty_model7(f_fort)
        m_ser = read_tlusty_model7(f_ser)
        m_par = read_tlusty_model7(f_par)
        for name, m in [('串行', m_ser), ('并行', m_par)]:
            if (m['n_depth'], m['n_params']) != \
                    (m_fort['n_depth'], m_fort['n_params']):
                print(f"警告: {name} 与 Fortran 的 ND/NUMPAR 不一致: "
                      f"({m['n_depth']},{m['n_params']}) vs "
                      f"({m_fort['n_depth']},{m_fort['n_params']})")

        fig = plt.figure(figsize=(9.5, 5.8))
        gs = GridSpec(2, 3, hspace=0.25, wspace=0.45)
        quantities = [('T', r'$T$ (K)'),
                      ('ne', r'n$_e$ (cm$^{-3}$)'),
                      ('rho', r'$\rho$ (g cm$^{-3}$)')]
        diff_labels = {'T': r'$|\Delta T|/T$',
                       'ne': r'$|\Delta n_e|/n_e$',
                       'rho': r'$|\Delta\rho|/\rho$'}
        depth = m_fort['dataframe']['depth_index'].values

        print(f"{'量':<6}{'串行中位':>11}{'串行最大':>11}"
              f"{'并行中位':>11}{'并行最大':>11}   (相对 Fortran)")
        for k, (col, ylabel) in enumerate(quantities):
            vf = m_fort['dataframe'][col].values
            vs = m_ser['dataframe'][col].values
            vp = m_par['dataframe'][col].values
            rs, rp = rel_diff(vf, vs), rel_diff(vf, vp)
            print(f"{col:<6}{np.median(rs):>11.2e}{rs.max():>11.2e}"
                  f"{np.median(rp):>11.2e}{rp.max():>11.2e}")

            ax = fig.add_subplot(gs[0, k])
            ax.loglog(m_fort['dm'], vf, 'b-', linewidth=3.4, alpha=0.45,
                      label='Fortran')
            ax.loglog(m_ser['dm'], vs, 'g--', linewidth=2.2, alpha=0.75,
                      label='Python serial')
            ax.loglog(m_par['dm'], vp, 'r:', linewidth=1.2, alpha=1.0,
                      label='Python parallel')
            ax.set_xlabel(r'$M$ (g cm$^{-2}$)')
            ax.set_ylabel(ylabel)
            ax.legend(frameon=False, loc='upper left')
        ax.tick_params(axis='both', which='major', labelsize=9)
            ax.tick_params(axis='both', which='major')

            axd = fig.add_subplot(gs[1, k])
            axd.semilogy(depth, rs, 'g-', linewidth=2.2, alpha=0.75,
                         label=f"serial med={np.median(rs):.1e}")
            axd.semilogy(depth, rp, 'r--', linewidth=1.2, alpha=1.0,
                         label=f"parallel med={np.median(rp):.1e}")
            axd.set_xlabel('depth index')
            axd.set_ylabel(diff_labels[col])
            axd.legend(frameon=False, fontsize=8)
        axd.tick_params(axis='both', which='major', labelsize=9)
            axd.tick_params(axis='both', which='major')

        # 能级布居(log10 空间, 逐深度最大)
        for name, m in [('串行', m_ser), ('并行', m_par)]:
            pa = np.log10(np.maximum(m_fort['parameters'][:, 3:], 1e-300))
            pb = np.log10(np.maximum(m['parameters'][:, 3:], 1e-300))
            dlog = np.abs(pa - pb)
            print(f"log10(pop) {name}: 中位 {np.median(dlog):.3e}  "
                  f"最大 {dlog.max():.3e}")

        # plt.suptitle('TLUSTY 22500K logg=4.0: Fortran vs Python serial/parallel',
        #              fontsize=14)
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Comparison plot saved to {output_file}")

    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
