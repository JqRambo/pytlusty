import matplotlib
import matplotlib.pyplot as plt
import os
import subprocess
import sys
import numpy as np
import pandas as pd
import subprocess
import threading
from matplotlib.gridspec import GridSpec


def read_tlusty_model7(filename):
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
    
    tau_values = all_data[:n_depth]
    
    param_data = all_data[n_depth:]
    
    parameters = param_data.reshape(n_depth, n_params)
    
    column_names = ['T', 'ne', 'rho']  
    n_levels = n_params - 3  
    
    for i in range(n_levels):
        column_names.append(f'level_{i+1}')
    
    df = pd.DataFrame(parameters, columns=column_names)
    
    df.insert(0, 'tau', tau_values)
    df.insert(0, 'depth_index', range(1, n_depth + 1))
    
    return {
        'n_depth': n_depth,
        'n_params': n_params,
        'n_levels': n_levels,
        'tau': tau_values,
        'parameters': parameters,
        'dataframe': df,
        'column_names': column_names}


def normalize_spectrum_flux(spectrum):

    if isinstance(spectrum, pd.DataFrame):
        waveobs = spectrum['waveobs'].values
        flux = spectrum['flux'].values
    else:
        waveobs = spectrum['waveobs']
        flux = spectrum['flux']
    
    ha_region_mask = (waveobs >= 4500) & (waveobs <= 5500)
    if np.sum(ha_region_mask) > 0:
        median_flux = np.median(flux[ha_region_mask])
        if median_flux > 0:
            normalized_flux = flux / median_flux
        else:
            normalized_flux = flux
    else:
        normalized_flux = flux
    
    # Create normalized spectrum (without error field since template has no errors)
    if isinstance(spectrum, pd.DataFrame):
        normalized_spectrum = pd.DataFrame({
            'waveobs': waveobs,
            'flux': normalized_flux
        })
    else:
        # For recarray or structured array
        normalized_spectrum = np.recarray((len(spectrum),), dtype=[('waveobs', float), ('flux', float)])
        normalized_spectrum['waveobs'] = waveobs
        normalized_spectrum['flux'] = normalized_flux
    
    return normalized_spectrum


def compare_spec(spec_path1, spec_path2):
    spec1 = pd.read_csv(spec_path1, sep='\s+', header=None, names=['waveobs', 'flux'])
    spec2 = pd.read_csv(spec_path2, sep='\s+', header=None, names=['waveobs', 'flux'])
    
    spec1 = normalize_spectrum_flux(spec1)
    spec2 = normalize_spectrum_flux(spec2)
    
    return spec1, spec2


def plot_combined_comparison(model_data1, model_data2, spec1, spec2, output_file):    
    
    fig = plt.figure(figsize=(16, 7), dpi=600)
    
    gs = GridSpec(2, 3, height_ratios=[1, 1], hspace=0.3, wspace=0.24)
    
    ax_spectrum = fig.add_subplot(gs[0, :])
    
    ax_temp = fig.add_subplot(gs[1, 0])
    ax_ne = fig.add_subplot(gs[1, 1])
    ax_rho = fig.add_subplot(gs[1, 2])
    
    # Plot two normalized spectra
    ax_spectrum.plot(spec1['waveobs'], spec1['flux'], color='b', linestyle='-', linewidth=2.0, label='This work')
    ax_spectrum.plot(spec2['waveobs'], spec2['flux'], color='darkorange', linestyle='-', linewidth=1.0, label='Ivan')
    
    ax_spectrum.set_xlabel(r'Wavelength ($\mathrm{\AA}$)', fontsize=14)
    ax_spectrum.set_ylabel('Normalized Flux', fontsize=14)
    ax_spectrum.legend(loc='upper right', fontsize=12)
    ax_spectrum.tick_params(axis='both', which='major', labelsize=10)
    ax_spectrum.set_xlim(3600, 7500)
    ax_spectrum.set_ylim(0, 3.5)
    # ax_spectrum.set_ylim(0.5, 1.1)  # Reasonable range for normalized spectra

    # Plot model comparisons (model_data1 vs model_data2)
    tau1 = model_data1['tau']
    tau2 = model_data2['tau']
    
    temperature1 = model_data1['dataframe']['T']
    temperature2 = model_data2['dataframe']['T']
    
    ne1 = model_data1['dataframe']['ne']
    ne2 = model_data2['dataframe']['ne']
    
    rho1 = model_data1['dataframe']['rho']
    rho2 = model_data2['dataframe']['rho']
    
    # Temperature plot with two models
    ax_temp.loglog(tau1, temperature1, 'b-', linewidth=6.0 , alpha=0.5, label='This work')
    # ax_temp.loglog(tau1, temperature1, 'ko', markersize=1.2, alpha=0.7, markevery=5) 
    ax_temp.loglog(tau2, temperature2, 'darkorange', linewidth=2.0, label='Ivan')  
    # ax_temp.loglog(tau2, temperature2, 'g^', markersize=1.2, alpha=0.7, markevery=5)
    
    ax_temp.set_xlabel(r'$M\ (\mathrm{g\,cm^{-2}})$', fontsize=14)
    ax_temp.set_ylabel(r'$T$ (K)', fontsize=14)
    # ax_temp.set_title(r'$\tau$ vs Temperature', fontsize=10)
    ax_temp.legend(fontsize=12, frameon=False)
    ax_temp.tick_params(axis='both', which='major', labelsize=10)
    # ax_temp.grid(True, alpha=0.3, linestyle='--')
    
    # Electron density plot with two models
    ax_ne.loglog(tau1, ne1, 'b-', linewidth=6.0 , alpha=0.5, label='This work')
    # ax_ne.loglog(tau1, ne1, 'ro', markersize=1.2, alpha=0.7, markevery=5)
    ax_ne.loglog(tau2, ne2, 'darkorange', linewidth=2.0, label='Ivan')
    # ax_ne.loglog(tau2, ne2, 'g^', markersize=1.2, alpha=0.7, markevery=5)
    
    ax_ne.set_xlabel(r'$M\ (\mathrm{g\,cm^{-2}})$', fontsize=14)

    ax_ne.set_ylabel(r'n$_e$ (cm$^{-3}$)', fontsize=14)
    # ax_ne.set_title(r'$\tau$ vs Electron Density', fontsize=10)
    ax_ne.legend(fontsize=12, frameon=False)
    ax_ne.tick_params(axis='both', which='major', labelsize=10)
    # ax_ne.grid(True, alpha=0.3, linestyle='--')
    
    # Density plot with two models
    ax_rho.loglog(tau1, rho1, 'b-', linewidth=6.0 , alpha=0.5, label='This work')
    # ax_rho.loglog(tau1, rho1, 'ro', markersize=1.2, alpha=0.7, markevery=5)
    ax_rho.loglog(tau2, rho2, 'darkorange', linewidth=2.0, label='Ivan')
    # ax_rho.loglog(tau2, rho2, 'g^', markersize=1.2, alpha=0.7, markevery=5)
    
    ax_rho.set_xlabel(r'$M\ (\mathrm{g\,cm^{-2}})$', fontsize=14)
    ax_rho.set_ylabel(r'$\rho$ (g cm$^{-3}$)', fontsize=14)
    # ax_rho.set_title(r'$\tau$ vs Density', fontsize=10)
    ax_rho.legend(fontsize=12, frameon=False)
    ax_rho.tick_params(axis='both', which='major', labelsize=10)
    # ax_rho.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    fig.savefig(output_file, dpi=600, bbox_inches='tight')
    plt.close()
    # plt.show()


def main():
    try:
        # Model data files
        filename1 = '/home/ubuntu/phd/hhen/paper/compare_all/teff_29000_logg_4.500/spec/FF.7'
        filename2 = '/home/ubuntu/phd/hhen/paper/compare_all/ivan/FF.7'
        
        # Read two models
        model_data1 = read_tlusty_model7(filename1)
        model_data2 = read_tlusty_model7(filename2)
        
        spec_path1 = "/home/ubuntu/phd/hhen/paper/compare_all/teff_29000_logg_4.500/spec/FF.spec"
        spec_path2 = "/home/ubuntu/phd/hhen/paper/compare_all/ivan/FF.spec"
        
        spec1, spec2 = compare_spec(spec_path1, spec_path2)
        
        # Output file
        output_file = '/home/ubuntu/phd/hhen/paper/combined_comparison_two_normal.pdf'
        
        # Generate comparison plot
        plot_combined_comparison(model_data1, model_data2, spec1, spec2, output_file)
        
        print(f"Comparison plot saved to {output_file}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()