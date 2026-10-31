"""This file defines the local paths to the data files used in the analysis.
The origins of the data files are documented here as comments. Also see the README in this folder.
Some of them are computed in postprocessing, when script names are noted look for them in `source/data_processing`.
"""

import pathlib

data_path = pathlib.Path(__file__).parent.parent / "data"

# source for 220+221 ringdown areas:
# https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220+221/<filename>
# source for 220 ringdown areas:
# https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220/<filename>

ringdown_times = sorted(list(range(6, 21)) + [10.5])

all_sources_names = {
    "bayeswave_H1": "signal_median_time_domain_waveform_H1.dat",
    "bayeswave_L1": "signal_median_time_domain_waveform_L1.dat",
    "PE_data_dump": "bilby-NRSur7dq4_prod_data0_1420878141-222656_generation_data_dump.pickle", # CIT path: /home/teagan.clarke/public_html/S250114ax_analysis/working/S250114ax/bilby-NRSur7dq4_prod/data/bilby-NRSur7dq4_prod_data0_1420878141-222656_generation_data_dump.pickle
    "PE_result": "bilby-NRSur7dq4_prod_data0_1420878141-222656_analysis_H1L1_merge_result.hdf5", # CIT path: /home/teagan.clarke/public_html/S250114ax_analysis/working/S250114ax/bilby-NRSur7dq4_prod/final_result/bilby-NRSur7dq4_prod_data0_1420878141-222656_analysis_H1L1_merge_result.hdf5
    "PE_summary": "posterior_samples_NRSur7dq4.h5",  # on CIT: /home/teagan.clarke/public_html/S250114ax_analysis/cosmo_reweighting/results/NRSUR_posterior_samples.h5
    "ringdown_220_posterior_with_areas": "ringdown_areas/220_10.5M_final_mass_spin_area.hdf5",  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220/220_10.5M_final_mass_spin_area.hdf5
    "ringdown_220+221_posterior_with_areas": "ringdown_areas/220+221_6M_final_mass_spin_area.hdf5",  # https://git.ligo.org/nicolemelissa.khusid/gw25014-ringdown-analysis/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220+221/220+221_6M_final_mass_spin_area.hdf5
    "reference_sample": "analysis_settings_maxL_sample.txt",  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/production_NRSur7dq4_srate4kHz_calibration_run_settings/analysis_settings_maxL_sample.txt
    "pyring_220_posterior": "pyring_220_posterior.dat",  # on CIT: /home/vasco.gennari/public_html/pyRing/O4b/GW250114_AreaLaw/GW250114_AreaLaw/GW250114A_NRSur7dq4HighFCalDownloadedDataExternalCustomPSDs_Kerr_220_10M_weighted_posterior/Nested_sampler/posterior.dat
    "pyring_220_areas": "remnant_area_pyring_reweighted.npy",  # computed by `reweight_pyring_220.ipynb`
    "ringdown_220_221_delta_posterior": "220+221+df221+dg221_6M_f220meas_f221meas_df221meas_120Ksamps.hdf5",  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220%2B221/220%2B221%2Bdf221%2Bdg221_6M_f220meas_f221meas_df221meas_120Ksamps.hdf5
    "pyring_220_221_delta_posterior": "posterior_with_qnm_frequencies.dat",  # obtained with the script convert_221_posterior_pyring.py
    "pyring_220_221_delta_posterior_without_frequencies": "pyring_220_221_delta_posterior_without_frequencies.dat",  # /home/vasco.gennari/public_html/pyRing/O4b/GW250114_AreaLaw/GW250114_AreaLaw/GW250114A_NRSur7dq4HighFCalDownloadedDataExternalCustomPSDs_Kerr_221_domega_dtau_221_6M_weighted_posterior/Nested_sampler/posterior.dat
    "ringdown_220": "220_amps_fs_gammas_merged_timescans.hdf5",  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220/mode_amps_fg/220_amps_fs_gammas_merged_timescans.hdf5
    "ringdown_220_snrs": "220_med_snrs_merged_timescans.txt",
    "ringdown_220+221": "220+221_amps_fs_gammas_merged_timescans.hdf5",  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220+221/mode_amps_fg/220+221_amps_fs_gammas_merged_timescans.hdf5
    "ringdown_220+221_snrs": "220+221_med_snrs_merged_timescans.txt",
    "ringdown_waveform_reconstruction": "hdet_raw_220_10.5M.hdf5",  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220/reconstructions/hdet_raw_220_10.5M.hdf5
    "inspiral_areas": "area_law_inspiral_data.hdf5",  # computed by `compute_inspiral_area.py` (see README)
    "inspiral_waveform_reconstruction": "pre_-40M_waveforms_CIs.h5",  # https://git.ligo.org/will-farr/arealawrescue/-/blob/main/inspiral_analysis/results/pre_-40M/pre_-40M_waveforms_CIs.h5
    "inspiral_SNR": "pre_-40M_with_lnL_cut.dat",  # https://git.ligo.org/will-farr/arealawrescue/-/blob/main/inspiral_analysis/results/pre_-40M/pre_-40M_with_lnL_cut.dat
    "area_change_prior": "area_change_prior.dat",  # comes from "save_area_change_prior.ipynb"
    "phenom_posterior_samples": "posterior_samples_PhenomXPHM.h5",  # on CIT: /home/teagan.clarke/public_html/S250114ax_analysis/cosmo_reweighting/results/XPHM_posterior_samples.h5
    "SEOB_posterior_samples": "posterior_samples_SEOBNRv5PHM.h5",  # on CIT: /home/teagan.clarke/public_html/S250114ax_analysis/cosmo_reweighting/results/SEOB_posterior_samples.h5
    "NRSur_posterior_samples": "posterior_samples_NRSur7dq4.h5",  # on CIT: /home/teagan.clarke/public_html/S250114ax_analysis/cosmo_reweighting/results/NRSUR_posterior_samples.h5
    "XO4a_posterior_samples": "posterior_samples_PhenomXO4a.h5",  # on CIT: /home/teagan.clarke/public_html/S250114ax_analysis/cosmo_reweighting/results/XO4a_posterior_samples.h5
    "NRSur_nocal_posterior_samples": "posterior_samples_NRSur7dq4_no_calibration.h5",  # on CIT: /home/teagan.clarke/public_html/S250114ax_analysis/cosmo_reweighting/results/NRSUR_nocal_posterior_samples.h5
    "NRSur_auxiliary_waveform_data": "NRSur7dq4.h5"
}

all_sources_names.update(
    {
        f"ringdown_areas_220_{time}": f"ringdown_areas/220_{time}M_final_mass_spin_area.hdf5"
        for time in ringdown_times
    }
)  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220/<filename>

all_sources_names.update(
    {
        f"ringdown_areas_220+221_{time}": f"ringdown_areas/220+221_{time}M_final_mass_spin_area.hdf5"
        for time in ringdown_times
    }
)  # https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/ringdown_analysis_results/data_product/production_NRSur7dq4_srate4kHz_calibration/220+221/<filename>


all_source_paths = {
    key: (data_path / value).as_posix() for key, value in all_sources_names.items()
}

if __name__ == "__main__":
    # to update the gitignore
    for key, value in all_sources_names.items():
        print(f"!/source/data/{value}")
