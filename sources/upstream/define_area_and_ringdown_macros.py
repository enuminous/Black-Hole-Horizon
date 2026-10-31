import pathlib
from data_sources import all_source_paths
import pandas as pd
import numpy as np
import h5py
from bilby.gw.result import CompactBinaryCoalescenceResult
from bilby_pipe.utils import DataDump
import lal
from scipy.stats import gaussian_kde, norm
from significance_estimate_variance import get_gaussian_significance

# define constants
M_sun = lal.MSUN_SI  # kg
G = lal.G_SI  # m^3 kg^-1 s^-2
c = lal.C_SI  # m/s
MsolTokm = M_sun * G / c**2 / 1e3  # conversion factor from solar masses to km


def format_scientific(val, sigfigs=1):
    exp = int(np.log10(val))
    base = val / 10**exp
    return f"{base:.{sigfigs}f}\\times10^{exp}"


def zero_z_score_direct_integration(samples):
    """Directly integrate a KDE estimate of the density of `samples` to find the z-score of zero.
    See our Supplemental Material for details.

    From Will Farr:
    https://git.ligo.org/publications/o4/cbc/tgr_companion_s250114ax/-/blob/main/misc/221_significance.ipynb
    """
    kde = gaussian_kde(samples)

    p0 = 2 * kde(0)  # 2 because of the reflection symmetry

    mu = np.mean(samples)
    sigma = np.std(samples)
    grid = np.linspace(
        max(0, mu - 10 * sigma), mu + 10 * sigma, 4096
    )  # Lots of samples!
    pgrid = kde(grid) + kde(-grid)  # Reflection trick!

    pgrid_cut = np.copy(pgrid)
    pgrid_cut[pgrid >= p0] = 0  # Zero out the region above that is not shaded

    P_tail = np.trapz(pgrid_cut, grid)  # Integrate the area under the curve in the tail
    z_tail = norm.isf(P_tail / 2)  # Convert to a z-score
    return z_tail


macros_area_law_path = pathlib.Path(__file__).parent.parent / "macros_area_law.tex"
macros_ringdown_path = pathlib.Path(__file__).parent.parent / "macros_ringdown.tex"


percent_width = None

credibility_level = 90
one_sigma_credibility_level = 68.2689492

data_ringdown_221_dev = h5py.File(
    all_source_paths["ringdown_220_221_delta_posterior"], "r"
)

all_runs_ringdown_220 = pd.read_hdf(all_source_paths["ringdown_220"], key="samples")
all_runs_ringdown_221 = pd.read_hdf(all_source_paths["ringdown_220+221"], key="samples")

t_ref_220 = 10.5
t_ref_221 = 6
data_ringdown_220 = all_runs_ringdown_220[
    all_runs_ringdown_220["start time [M]"] == t_ref_220
]
data_ringdown_221 = all_runs_ringdown_221[
    all_runs_ringdown_221["start time [M]"] == t_ref_221
]

df221_percent_width = int(
    np.round(
        100
        * (
            np.percentile(
                data_ringdown_221_dev["df_221"], (100 + credibility_level) / 2
            )
            - np.percentile(
                data_ringdown_221_dev["df_221"], (100 - credibility_level) / 2
            )
        )
        / 2,
        decimals=0,
    )
)

# QNM significance calculation

# obtain significances for each start time
sigma_220 = all_runs_ringdown_220.groupby("start time [M]").apply(
    lambda x: zero_z_score_direct_integration(x["A_220"])
)
sigma_221 = all_runs_ringdown_221.groupby("start time [M]").apply(
    lambda x: zero_z_score_direct_integration(x["A_221"])
)

t_fundamental_early = 20  # time chosen to report fundamental significance bound
fundamental_significance = sigma_220[
    (sigma_220.index <= t_fundamental_early)
].min()  # minimum significance before the chosen time
fundamental_significance_3sigma_time = sigma_220[
    (sigma_220 < 3)
].index.min()  # first time at which fundamental significance falls below 3 sigma

t_overtone_early = t_ref_221  # inflection point of overtone amplitude trend
overtone_detection_threshold_sigma = 1
t_overtone = sigma_221[
    (sigma_221 < overtone_detection_threshold_sigma)
    & (sigma_221.index > t_overtone_early)
].index.min()  # first time at which overtone significance falls below 2 sigma after the inflection point
overtone_significance_6M = np.round(
    sigma_221[t_overtone_early], 1
)  # overtone significance at the inflection point
overtone_significance_3sigma_time = sigma_221[
    (sigma_221 < 3) & (sigma_221.index > t_overtone_early)
].index.min()  # first time at which overtone significance falls below 3 sigma after the inflection point


# REFERENCE VALUES

data = DataDump.from_pickle(all_source_paths["PE_data_dump"])
res = CompactBinaryCoalescenceResult.from_hdf5(filename=all_source_paths["PE_result"])

# from the ringdown review page https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/wikis/Ringdown-Analysis-Review-Page
T_MSUN = lal.GMSUN_SI / lal.C_SI**3

pe_path = all_source_paths["PE_summary"]
with h5py.File(pe_path, "r") as f:
    pe_df = pd.DataFrame(f["bilby-NRSur7dq4_prod-reweighted"]["posterior_samples"][()])

reference_parameters = np.genfromtxt(
    all_source_paths["reference_sample"], names=True, dtype=np.float64
)
t_final_mass = reference_parameters["final_mass"] * T_MSUN

ref_gps_time = reference_parameters["geocent_time"]
ref_gps_time_h1 = reference_parameters["H1_time"]
ref_gps_time_l1 = reference_parameters["L1_time"]
final_mass_seconds = reference_parameters["final_mass"] * T_MSUN
final_mass = reference_parameters["final_mass"]
total_mass = reference_parameters["total_mass"]
total_mass_seconds = reference_parameters["total_mass"] * T_MSUN
final_spin = reference_parameters["final_spin"]
ra = reference_parameters["ra"]
dec = reference_parameters["dec"]
psi = reference_parameters["psi"]

ifos = ["H1", "L1"]

trigger_time = np.median((pe_df["H1_time"] + pe_df["L1_time"]) / 2)  # 1420878141.218
relative_times = {
    i: pe_df[f"{i}_time"] - reference_parameters[f"{i}_time"] for i in ifos
}

alpha = credibility_level / 100
peak_times_gps = {}
for i in ifos:
    t = pe_df[f"{i}_time"]
    lo, m, hi = np.quantile(t, [(1 - alpha) / 2, 0.5, 1 - (1 - alpha) / 2])
    peak_times_gps[i] = f"{m:.4f}^{{+{hi - m:.4f}}}_{{-{m - lo:.4f}}}"

peak_times_relative = {}
peak_times_relative_std = {}
peak_time_ci = 0
for i in ifos:
    t = (pe_df[f"{i}_time"] - reference_parameters[f"{i}_time"]) / t_final_mass
    lo, m, hi = np.quantile(t, [(1 - alpha) / 2, 0.5, 1 - (1 - alpha) / 2])
    peak_times_relative[i] = f"{m:.2f}^{{+{hi - m:.2f}}}_{{-{m - lo:.2f}}}"
    peak_times_relative_std[i] = f"{np.std(t):.2f}"
    peak_time_ci += (hi - lo) / 2

peak_time_ci = peak_time_ci / len(ifos)
peak_times_overall_ci = f"{peak_time_ci:.1f}"

# PyRing properties
pyring_delay_at_6M = 0.5  # how late PyRing actually starts relative to the requested start time in units of Mf https://git.ligo.org/cbc-testinggr/pyring/-/wikis/S250114ax#--area-law-paper
pyring_seglen = 64  # initial PyRing segment length for conditioning https://git.ligo.org/cbc-testinggr/pyring/-/wikis/Area-Law-Results-Review#data-provenance

# SNR numbers from analysis signed off by Eliot
# https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/notebooks/snrs_fg.ipynb
overtone_snr = 26
t_fundamental_snr = t_ref_220
snr_fundamental_early = 20.61

# ringdown properties
# https://git.ligo.org/nicolemelissa.khusid/gw250114-ringdown-analysis/-/blob/main/notebooks/eff_start_times.ipynb
t_ringdown_fundamental_ref_h = np.round(1420878141.2225342, 6)
t_ringdown_fundamental_ref_l = np.round(1420878141.2200317, 6)
t_ringdown_fundamental_ref_h_delta = np.round(-0.045992905439770505, 4)
t_ringdown_fundamental_ref_l_delta = np.round(-0.06722040025812612, 4)

t_ringdown_overtone_ref_h = np.round(1420878141.2210083, 6)
t_ringdown_overtone_ref_l = np.round(1420878141.218567, 6)
t_ringdown_overtone_ref_h_delta = -0.07500381502485652
t_ringdown_overtone_ref_l_delta = 0.08490997927342248

# PyRing properties
t_ref_220_pyring = 10
t_pyring_fundamental_ref_h = np.round(1420878141.222412, 6)
t_pyring_fundamental_ref_l = np.round(1420878141.2199707, 6)
t_pyring_fundamental_ref_h_delta = -0.40827548367303973
t_pyring_fundamental_ref_l_delta = -0.24836168937476072

t_pyring_overtone_ref_h = np.round(1420878141.2211914, 6)
t_pyring_overtone_ref_l = np.round(1420878141.21875, 6)
t_pyring_overtone_ref_h_delta = 0.4684200523250473
t_pyring_overtone_ref_l_delta = 0.6283338466233263

t_pyring_ringdown_delta_fundamental_h = (
    t_pyring_fundamental_ref_h_delta - t_ringdown_fundamental_ref_h_delta
)
t_pyring_ringdown_delta_fundamental_l = (
    t_pyring_fundamental_ref_l_delta - t_ringdown_fundamental_ref_l_delta
)

t_pyring_ringdown_delta_overtone_h = (
    t_pyring_overtone_ref_h_delta - t_ringdown_overtone_ref_h_delta
)
t_pyring_ringdown_delta_overtone_l = (
    t_pyring_overtone_ref_l_delta - t_ringdown_overtone_ref_l_delta
)
t_pyring_ringdown_delta_overtone = (
    np.abs(t_pyring_ringdown_delta_overtone_h + t_pyring_ringdown_delta_overtone_l) / 2
)


def median_with_interval(data, decimals, credibility_level=credibility_level):

    median = np.median(data)
    lower, upper = np.percentile(data, (100 - credibility_level) / 2), np.percentile(
        data, (100 + credibility_level) / 2
    )
    return f"{median:.{decimals}f}^{{{upper-median:+.{decimals}f}}}_{{{lower-median:+.{decimals}f}}}"


ringdown_text = f"""% Ringdown properties
% programmatically generated, do not modify
\\newcommand{{\\Specsign}}{{{{{{\\pm{{{df221_percent_width}\\%}}}}}}\\xspace}}
\\newcommand{{\\tFundamental}}{{{{{{{fundamental_significance_3sigma_time}}}}}\\xspace}}  % last time for the fundamental
\\newcommand{{\\tFundamentalEarly}}{{{{{{{t_fundamental_early}}}}}\\xspace}}  % some earlier time for the fundamental
\\newcommand{{\\tFundamentalSNR}}{{{{{{{t_fundamental_snr}}}}}\\xspace}}  % some earlier time for the fundamental
\\newcommand{{\\SNRFundamentalEarly}}{{{{{{{snr_fundamental_early:.0f}}}}}\\xspace}}  % SNR for the fundamental at at tFundamentalSNR
\\newcommand{{\\tOvertone}}{{{{{{{t_overtone}}}}}\\xspace}}  % last time for the overtone
\\newcommand{{\\tSecondOvertone}}{{{{{{{t_overtone_early}}}}}\\xspace}}  % last time for the second overtone

\\newcommand{{\\OvertoneThreeSigmaTime}}{{\\ensuremath{{{{{overtone_significance_3sigma_time}}}}}\\xspace}}
\\newcommand{{\\OvertoneSignificance}}{{\\ensuremath{{{{{overtone_significance_6M:.1f}\\sigma}}}}\\xspace}}
\\newcommand{{\\FundamentalSignificance}}{{\\ensuremath{{{{{{>}}{{{fundamental_significance:.0f}}}\\sigma}}}}\\xspace}}
\\newcommand{{\\PyRingDelay}}{{{{{pyring_delay_at_6M}}}\\xspace}}

\\newcommand{{\\tRef}}{{{{{{{ref_gps_time}}}}}\\xspace}}
\\newcommand{{\\tRefH}}{{{{{{{ref_gps_time_h1}}}}}\\xspace}}
\\newcommand{{\\tRefL}}{{{{{{{ref_gps_time_l1}}}}}\\xspace}}
\\newcommand{{\\raRef}}{{{{{{{ra:.3f}}}}}\\xspace}}
\\newcommand{{\\decRef}}{{{{{{{dec:.3f}}}}}\\xspace}}
\\newcommand{{\\psiRef}}{{{{{{{psi:.3f}}}}}\\xspace}}
\\newcommand{{\\mfRef}}{{{{{{{final_mass:.3f}}}}}\\xspace}}
\\newcommand{{\\tMfRef}}{{{{{{{1000*final_mass_seconds:.3f}}}\\, {{\\rm ms}}}}\\xspace}}

\\newcommand{{\\mRef}}{{\\ensuremath{{{{{total_mass:.3f}}}\\, \\Msun}}\\xspace}}
\\newcommand{{\\tMRef}}{{\\ensuremath{{{{{1000*total_mass_seconds:.3f}}}\\, {{\\rm ms}}}}\\xspace}}
\\newcommand{{\\chiRem}}{{\\ensuremath{{{{{final_spin:.3f}}}\\, }}\\xspace}}

\\newcommand{{\\tPeakH}}{{{{{{{peak_times_gps['H1']}}}\\, {{\\rm s}}}}\\xspace}}
\\newcommand{{\\tPeakL}}{{{{{{{peak_times_gps['L1']}}}\\, {{\\rm s}}}}\\xspace}}
\\newcommand{{\\tPeakHrel}}{{{{{{{peak_times_relative['H1']}}}\\, \\tMf}}\\xspace}}
\\newcommand{{\\tPeakLrel}}{{{{{{{peak_times_relative['L1']}}}\\, \\tMf}}\\xspace}}
\\newcommand{{\\tPeakHrelStd}}{{{{{{{peak_times_relative_std['H1']}}}\\, \\tMf}}\\xspace}}
\\newcommand{{\\tPeakLrelStd}}{{{{{{{peak_times_relative_std['L1']}}}\\, \\tMf}}\\xspace}}
\\newcommand{{\\tPeakOverallCI}}{{{{{{{peak_times_overall_ci}}}\\, \\tMf}}\\xspace}}

\\newcommand{{\\dfConstraint}}{{{{{{\\ensuremath{{{median_with_interval(data_ringdown_221_dev['df_221'], decimals=1)}}}}}}}\\xspace}}
\\newcommand{{\\dfConstraintOneSigma}}{{\\ensuremath{{{{{median_with_interval(data_ringdown_221_dev['df_221'], decimals=1, credibility_level=one_sigma_credibility_level)}}}}}\\xspace}}
\\newcommand{{\\dfCredibility}}{{{{{{{credibility_level}\\%}}}}\\xspace}}

\\newcommand{{\\FundamentalFreq}}{{\\ensuremath{{{{{median_with_interval(data_ringdown_220['f_220'], decimals=0)}}}}}\\xspace}}
\\newcommand{{\\FundamentalDamp}}{{\\ensuremath{{{{{median_with_interval(data_ringdown_220['g_220'], decimals=0)}}}}}\\xspace}}
\\newcommand{{\\OvertoneFreq}}{{\\ensuremath{{{{{median_with_interval(data_ringdown_221['f_221'], decimals=0)}}}}}\\xspace}}
\\newcommand{{\\OvertoneDamp}}{{\\ensuremath{{{{{median_with_interval(data_ringdown_221['g_221'], decimals=0)}}}}}\\xspace}}
\\newcommand{{\\OvertoneSNR}}{{\\ensuremath{{{{{overtone_snr}}}}}\\xspace}}

\\newcommand{{\\PyRingSeglen}}{{{{{pyring_seglen}}}}}

\\newcommand{{\\TimingDiscussionFundamentalTimeRingdown}}{{{{{t_ref_220}}}}}
\\newcommand{{\\tGPSringdownFundamentalRefH}}{{{{{t_ringdown_fundamental_ref_h}}}}}
\\newcommand{{\\tGPSringdownFundamentalRefL}}{{{{{t_ringdown_fundamental_ref_l}}}}}
\\newcommand{{\\tGPSringdownFundamentalRefHdelta}}{{{{{t_ringdown_fundamental_ref_h_delta:.3f}}}}}
\\newcommand{{\\tGPSringdownFundamentalRefLdelta}}{{{{{t_ringdown_fundamental_ref_l_delta:.3f}}}}}

\\newcommand{{\\TimingDiscussionFundamentalTimePyring}}{{{{{t_ref_220_pyring}}}}}
\\newcommand{{\\tGPSpyringFundamentalRefH}}{{{{{t_pyring_fundamental_ref_h}}}}}
\\newcommand{{\\tGPSpyringFundamentalRefL}}{{{{{t_pyring_fundamental_ref_l}}}}}
\\newcommand{{\\tGPSpyringFundamentalRefHdelta}}{{{{{t_pyring_fundamental_ref_h_delta:.2f}}}}}
\\newcommand{{\\tGPSpyringFundamentalRefLdelta}}{{{{{t_pyring_fundamental_ref_l_delta:.2f}}}}}

\\newcommand{{\\tGPSfundamentalPyringRingdownH}}{{{{{t_pyring_ringdown_delta_fundamental_h:.2f}}}}}
\\newcommand{{\\tGPSfundamentalPyringRingdownL}}{{{{{t_pyring_ringdown_delta_fundamental_l:.2f}}}}}
\\newcommand{{\\tGPSovertonePyringRingdownH}}{{{{{t_pyring_ringdown_delta_overtone_h:.2f}}}}}
\\newcommand{{\\tGPSovertonePyringRingdownL}}{{{{{t_pyring_ringdown_delta_overtone_l:.2f}}}}}

\\newcommand{{\\TimingDiscussionOvertoneTimeRingdown}}{{6}}
\\newcommand{{\\TimingDiscussionOvertoneTimePyring}}{{6}}
\\newcommand{{\\tGPSpyringOvertoneRefDelta}}{{{{{t_pyring_ringdown_delta_overtone:.2f}}}}}
"""

with open(macros_ringdown_path, "w") as f:
    f.write(ringdown_text)

# get inspiral SNR
inspiral_samples = np.genfromtxt(all_source_paths["inspiral_SNR"], names=True)
inspiral_snrs = inspiral_samples["network_matched_filter_SNR"]

# load all times and histogram data at reference_time
reference_inspiral_time = -40  # featured time for inspiral truncation
inspiral_dataset = h5py.File(all_source_paths["inspiral_areas"], "r")
times = inspiral_dataset["times"][:]
hist_idx = np.where(np.isclose(times, reference_inspiral_time, rtol=0, atol=0.5))[0][0]
hist_components_area = inspiral_dataset[f"area_insp_{hist_idx}"][:]

remnant_data_file = h5py.File(
    all_source_paths["ringdown_220_posterior_with_areas"], "r"
)
remnant_area_ringdown = remnant_data_file["Area_f"][:]
remnant_area_pyring = np.load(all_source_paths["pyring_220_areas"])

remnant_data_file_221 = h5py.File(
    all_source_paths["ringdown_220+221_posterior_with_areas"], "r"
)
remnant_area_ringdown_221 = remnant_data_file_221["Area_f"][:]

# make sure the two samples sets have the same length
prng = np.random.default_rng(seed=250114)
n = min(len(remnant_area_ringdown), len(remnant_area_pyring))
remnant_area_ringdown = prng.choice(remnant_area_ringdown, size=n, replace=False)
remnant_area_pyring = prng.choice(remnant_area_pyring, size=n, replace=False)
all_remnant_areas = np.concatenate([remnant_area_ringdown, remnant_area_pyring])

# get minimum inspiral significance with 220 mode
min_inspiral_significance = np.inf
first_5sigma_time = np.inf
for i in range(len(times)):
    insp_areas = inspiral_dataset[f"area_insp_{i}"][:]
    sigma = get_gaussian_significance(all_remnant_areas, insp_areas)
    min_inspiral_significance = min(min_inspiral_significance, sigma)
    if sigma >= 5:
        first_5sigma_time = min(first_5sigma_time, times[i])

# get AL significance with 221 mode at 6M
al_significance_221 = get_gaussian_significance(
    remnant_area_ringdown_221, hist_components_area
)

# flux numbers from notebook in this repo
# https://git.ligo.org/publications/o4/cbc/s250114ax/-/blob/main/misc/energy_flux.ipynb
flux_peak = 6
t_10percent = -36
t_1percent = -232

area_law_text = f"""% Area Law properties
% programmatically generated, do not modify
\\newcommand{{\\ALsign}}{{{{\\ensuremath{{{get_gaussian_significance(all_remnant_areas, hist_components_area):.1f}\\sigma}}}}\\xspace}}
\\newcommand{{\\ALsignminimum}}{{{{{{\\ensuremath{{{min_inspiral_significance:.1f}\\sigma}}}}}}\\xspace}}
\\newcommand{{\\Pretime}}{{{{{{{reference_inspiral_time}}}}}}}
\\newcommand{{\\PreSNR}}{{{{{{{np.median(inspiral_snrs):.0f}}}}}\\xspace}}
\\newcommand{{\\InitialAreaMedian}}{{{{{{\\ensuremath{{{format_scientific(np.median(hist_components_area*MsolTokm**2))}}}}}\\xspace}}}}
\\newcommand{{\\FinalAreaMedian}}{{{{{{\\ensuremath{{{format_scientific(np.median(all_remnant_areas*MsolTokm**2))}}}}}\\xspace}}}}

\\newcommand{{\\ALsignOvertone}}{{{{{al_significance_221:.1f}}}}}
\\newcommand{{\\AreaLawFiveSigmaTime}}{{{{{first_5sigma_time:.0f}}}}}

\\newcommand{{\\FluxPeak}}{{{{{{{flux_peak:.0f}}}}}}}
\\newcommand{{\\FluxOnePercent}}{{{{{{{t_1percent:.0f}}}}}}}
\\newcommand{{\\FluxTenPercent}}{{{{{{{t_10percent:.0f}}}}}}}

\\newcommand{{\\TDinfSeglen}}{{{{1.4}}}}
\\newcommand{{\\TDinfTimeStd}}{{{{0.01}}}}
"""

with open(macros_area_law_path, "w") as f:
    f.write(area_law_text)
