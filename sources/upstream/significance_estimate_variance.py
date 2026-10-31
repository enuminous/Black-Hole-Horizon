import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt
from matplotlib import patheffects
from tqdm import tqdm
import matplotlib
from numba import njit
from scipy.stats import norm

# matplotlib.rcParams['text.usetex'] = True
# matplotlib.rcParams['font.family'] =  "serif"


fig_path = Path(__file__).parent.parent / "figures"
data_path = Path(__file__).parent.parent / "data"

# components_area = np.load(data_path / 'components_area.npy')
# remnant_area = np.load(data_path / 'remnant_area.npy')

rng = np.random.default_rng(seed=1)


@njit
def count_below_zero(dist_1, dist_2):
    total = 0
    for i in range(len(dist_1)):
        for j in range(len(dist_2)):
            if dist_2[j] - dist_1[i] < 0:
                total += 1
    return total


def get_dist(samples_r, samples_i, n_iterations):
    n_below_0_bootstrap = []

    for _ in tqdm(range(n_iterations)):
        resampled_remnant_area = rng.choice(
            samples_r, size=len(samples_r), replace=True
        )
        resampled_components_area = rng.choice(
            samples_i, size=len(samples_i), replace=True
        )

        n_below_0_bootstrap.append(
            count_below_zero(resampled_components_area, resampled_remnant_area)
        )
    return n_below_0_bootstrap


def get_percentiles(dist, n_total, percentiles=(5, 95)):
    sigmas = norm.isf(np.asarray(dist) / n_total)

    sigmas[~np.isfinite(sigmas)] = 10

    return np.percentile(sigmas, percentiles)


def get_gaussian_significance(samples_r, samples_i):

    mu_r = samples_r.mean()
    sigma_r = samples_r.std()

    mu_i = samples_i.mean()
    sigma_i = samples_i.std()

    return (mu_r - mu_i) / np.sqrt(sigma_r**2 + sigma_i**2)


def get_gaussian_approx(samples_r, samples_i):

    mu_r = samples_r.mean()
    sigma_r = samples_r.std()

    mu_i = samples_i.mean()
    sigma_i = samples_i.std()
    return norm(
        loc=mu_r / mu_i - 1,
        scale=(mu_r / mu_i) * np.sqrt(((sigma_r / mu_r) ** 2 + (sigma_i / mu_i) ** 2)),
    ).pdf


def get_gaussian_percentiles(samples_r, samples_i, n_iterations, percentiles=(5, 95)):

    significance_bootstrap = []

    for _ in tqdm(range(n_iterations)):
        resampled_remnant_area = rng.choice(
            samples_r, size=len(samples_r), replace=True
        )
        resampled_components_area = rng.choice(
            samples_i, size=len(samples_i), replace=True
        )

        significance_bootstrap.append(
            get_gaussian_significance(resampled_remnant_area, resampled_components_area)
        )

    return np.percentile(significance_bootstrap, percentiles)
