import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec


def read_tlusty_model7(filename):
    """读取 TLUSTY 模型大气文件（fort.7 / MOD.7 格式）。

    返回 dict，含深度点数、参数数、深度尺度（DM，质量深度）和
    各深度参数（T, ne, rho, 各能级布居）。
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    first_line = lines[0].split()
    n_depth = int(first_line[0])
    n_params = int(first_line[1])

    all_data = []
    for line in lines[1:]:
        if line.strip():
            line_processed = line.replace('D', 'E').replace('d', 'e')
            line_data = [float(x) for x in line_processed.split()]
            all_data.extend(line_data)

    all_data = np.array(all_data)

    # 注意：.7 文件中第 2 条记录是 DM（质量深度），不是光学深度
    dm_values = all_data[:n_depth]

    param_data = all_data[n_depth:]
    parameters = param_data.reshape(n_depth, n_params)

    column_names = ['T', 'ne', 'rho']
    n_levels = n_params - 3

    for i in range(n_levels):
        column_names.append(f'level_{i+1}')

    df = pd.DataFrame(parameters, columns=column_names)
    df.insert(0, 'dm', dm_values)
    df.insert(0, 'depth_index', range(1, n_depth + 1))

    return {
        'n_depth': n_depth,
        'n_params': n_params,
        'n_levels': n_levels,
        'dm': dm_values,
        'parameters': parameters,
        'dataframe': df,
        'column_names': column_names}


def compare_models(model_data1, model_data2):
    """数值比较两个模型，返回每个物理量的相对差统计。"""
    stats = {}
    df1, df2 = model_data1['dataframe'], model_data2['dataframe']
    for col in ['T', 'ne', 'rho']:
        x, y = df1[col].values, df2[col].values
        rd = np.abs(x - y) / np.maximum(np.abs(y), 1e-300)
        stats[col] = {
            'rel_diff': rd,
            'max': rd.max(),
            'imax': int(rd.argmax()) + 1,
            'median': float(np.median(rd))}
    # 能级布居用 log10 空间比较
    pa = np.log10(np.maximum(model_data1['parameters'][:, 3:], 1e-300))
    pb = np.log10(np.maximum(model_data2['parameters'][:, 3:], 1e-300))
    dlog = np.abs(pa - pb)
    stats['popul'] = {
        'rel_diff': dlog.max(axis=1),   # 每个深度取最大，供画图
        'max': dlog.max(),
        'median': float(np.median(dlog))}
    return stats


def plot_combined_comparison(model_data1, model_data2, stats,
                             label1, label2, output_file):
    """上排：T、ne、rho 随质量深度的 log-log 曲线对比；
    下排：对应的相对差（布居为 log10 空间逐深度最大差）。"""
    fig = plt.figure(figsize=(16, 9), dpi=300)
    gs = GridSpec(2, 3, hspace=0.25, wspace=0.25)

    dm1 = model_data1['dm']
    dm2 = model_data2['dm']
    depth = model_data1['dataframe']['depth_index'].values

    quantities = [('T', r'$T$ (K)'),
                  ('ne', r'n$_e$ (cm$^{-3}$)'),
                  ('rho', r'$\rho$ (g cm$^{-3}$)')]
    diff_labels = {'T': r'$|\Delta T|/T$',
                   'ne': r'$|\Delta n_e|/n_e$',
                   'rho': r'$|\Delta\rho|/\rho$'}

    for k, (col, ylabel) in enumerate(quantities):
        ax = fig.add_subplot(gs[0, k])
        v1 = model_data1['dataframe'][col]
        v2 = model_data2['dataframe'][col]
        ax.loglog(dm1, v1, 'b-', linewidth=1.0, label=label1)
        ax.loglog(dm2, v2, 'r--', linewidth=1.0, label=label2)
        ax.set_xlabel(r'$M$ (g cm$^{-2}$)', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(fontsize=11, frameon=False)
        ax.tick_params(axis='both', which='major', labelsize=10)

        axd = fig.add_subplot(gs[1, k])
        rd = stats[col]['rel_diff']
        axd.semilogy(depth, rd, 'k-', linewidth=1.0)
        axd.set_xlabel('depth index', fontsize=12)
        axd.set_ylabel(diff_labels[col], fontsize=12)
        axd.tick_params(axis='both', which='major', labelsize=10)
        axd.set_title(f"median={stats[col]['median']:.2e}, "
                      f"max={stats[col]['max']:.2e}", fontsize=10)

    # plt.suptitle(f'{label1}  vs  {label2}', fontsize=14)
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    # 命令行：compare_all.py [参考模型.7] [待比较模型.7] [输出.pdf]
    filename1 = sys.argv[1] if len(sys.argv) > 1 else \
        '/home/ubuntu/transform/teddy/test/tlusty_22500_fortran/FF.7'    # Fortran 参考
    filename2 = sys.argv[2] if len(sys.argv) > 2 else \
        '/home/ubuntu/transform/teddy/test/tlusty_22500_py_serial/FF.7'  # Python 版结果
    output_file = sys.argv[3] if len(sys.argv) > 3 else \
        '/home/ubuntu/transform/teddy/test/combined_comparison.pdf'
    label1 = 'Fortran'
    label2 = 'Python'

    try:
        model_data1 = read_tlusty_model7(filename1)
        model_data2 = read_tlusty_model7(filename2)

        if (model_data1['n_depth'] != model_data2['n_depth'] or
                model_data1['n_params'] != model_data2['n_params']):
            print('警告：两个文件的 ND/NUMPAR 不一致，'
                  f"({model_data1['n_depth']},{model_data1['n_params']}) vs "
                  f"({model_data2['n_depth']},{model_data2['n_params']})")

        stats = compare_models(model_data1, model_data2)

        print(f'比较: {filename1}  vs  {filename2}')
        print(f"{'量':<8}{'中位差':>12}{'最大差':>12}{'最大差位置':>10}")
        for col in ['T', 'ne', 'rho']:
            s = stats[col]
            print(f"{col:<8}{s['median']:>12.3e}{s['max']:>12.3e}"
                  f"{s['imax']:>10d}")
        s = stats['popul']
        print(f"{'log10(pop)':<8}{s['median']:>12.3e}{s['max']:>12.3e}")

        plot_combined_comparison(model_data1, model_data2, stats,
                                 label1, label2, output_file)
        print(f"Comparison plot saved to {output_file}")

    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
