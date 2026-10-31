# EFMW-BH-AREA-003 — frozen execution protocol

Frozen before numerical outcomes on 31 October 2026. This is a complete bounded reproducibility and robustness experiment, not a new detector-strain analysis or a completed physical test of EFMW.

## Questions

1. Do the public, separately inferred GW250114 premerger and ringdown area samples reproduce the published reference area-growth statistic?
2. How much can a specified waveform mismatch bias a Kerr-based area inference in controlled synthetic data?
3. Which additional equations would be needed to interpret this as a test of EFMW C1?

## Observational arm

Use LVK Zenodo 16877102 v1, released 10 September 2025, archive MD5 `58c00488e66bc87d588b642cbdf33e2d`. Inspect the supplied area scripts before reconstructing their pooling and reference windows. Reference premerger cut: -40 total-mass times; reference ringdown fundamental: 10.5 remnant-mass times. Reproduce the authors' mean/variance significance to their quoted 4.4 (tolerance 0.15); do not reinterpret this Gaussian summary as a resolved posterior-tail probability. Report other cuts/models without selecting the most favorable one. Preserve archive and member hashes. No full-signal posterior shall be used as evidence for an independent area theorem test.

Compute fractional area change R-1, R=Af/Ai, using independent pre/post posterior draws. Report equal-tail 90% intervals. A sensitivity factor eta changes the comparison to eta*R-1; eta is an assumed common remnant/progenitor area (or stationary entropy) correction, not an inferred modified-gravity parameter. Report eta crossing thresholds at posterior quantiles. Post-processing Kerr posteriors does not refit alternative-gravity likelihoods.

## Synthetic arm

Seed 20261031; 200 noise realizations per case; sample rate 4096 Hz; duration 0.08 s. One ideal whitened channel with independent unit Gaussian noise, known onset, unknown linear cosine/sine amplitudes. Baseline detector-frame remnant mass 68 solar masses, spin 0.68; fundamental initial matched-filter SNR 30. Standard Kerr QNM fitting formulas of Berti, Cardoso & Will (2006), Table VIII; these are approximations, not exact Kerr spectra. Initial area specified independently through baseline ratios R=1.5 and R=1.02. Independent initial-area measurement has 3% Gaussian uncertainty in log area. No merger relation is used to predict the final area.

Frequency-scale arms: s in {0.8,0.9,1,1.1,1.2,1.3}, f=s*fKerr and tau=tauKerr/s (constant Q). Recover with the undeformed single-mode Kerr interpretation. Exact noiseless expectations: inferred spin unchanged, inferred mass M/s, inferred area A/s^2. This family is deliberately degenerate with a mass change in a single mode; it is a phenomenological stress test, not an EFMW waveform or a self-consistent merger solution.

Contamination arms: add the conventional Kerr 221 overtone with initial amplitude 1 times the 220 amplitude and relative phase 1 radian. Fit fundamental only at starts 0, 5, 10 ms; fit a shared-mass/spin 220+221 model at 0 ms as a correctly specified comparator. Keep the full injected amplitude fixed across start cuts, so later analyses really lose SNR. Run these at R=1.5 only. Control: pure fundamental at 0 ms is already in the frequency-scale grid.

Use bounded nonlinear least squares with linear amplitudes profiled out and multiple fixed starting points. Derive local Gaussian parameter uncertainties from the full waveform Jacobian and propagate to log area; combine independently with the 3% log-initial-area uncertainty. These are approximate frequentist 90% intervals, not Bayesian posteriors. Record optimizer failures, physical-domain failures, boundary fits and unavailable covariance; do not silently clip them. Report median area bias, 90% interval coverage, inferred decrease rate, significant decrease rate (upper 90% endpoint below zero), retained SNR and residual fit diagnostics. Wilson 95% intervals apply only to Monte Carlo proportions, not astrophysical credibility.

## Numerical gates and interpretation

- Schwarzschild and extremal area limits, dimensional scaling and common-redshift cancellation: relative tolerance 1e-12.
- QNM forward/inverse closure over spins 0.05–0.95 and masses 20–100 solar masses: relative tolerance 1e-10.
- Exact constant-Q deformation law and noiseless injection/recovery: relative area tolerance 1e-5.
- Correctly specified pure-mode 90% interval coverage: diagnostic PASS if the Wilson 95% interval contains 0.90; otherwise FAIL, without changing thresholds.
- Public reference significance reproduction: PASS within 0.15 of 4.4.
- Any positive area sign is conditional on the selected waveform and area mapping. No gate validates EFMW, proves Hawking's theorem, or establishes a violation.

## EFMW obligations

Consult the frozen C1 action. In a scalar-only curvature-linear restriction, identify the coefficient of R, and derive the corresponding stationary Wald entropy. Gauge-curvature terms and higher-curvature extensions are outside this restriction. Require regular black-hole backgrounds, stable perturbations, source excitation, detector waveform, matter/frame choice and entropy/area mapping before an EFMW-specific parameter bound. No Zoo animal certification or Lean proof is claimed by this protocol.
