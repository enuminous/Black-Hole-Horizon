# Black hole collision lab

[Open the lab](https://enuminous.github.io/Black-Hole-Horizon/collision/) or open index.html locally with the CSS and JavaScript files beside it. Play, pause, scrub, change playback speed, or jump to the first common horizon. The two views have independent clocks.

## Binary collision

The orbital plane shows the x–y projection of inertial-frame apparent-horizon centers from SpEC run **SXS:BBH:0305, Lev5**. Its reference mass ratio is 1.22117. The simulation covers about 15.18 orbits. The default window runs from 260 M before to 50 M after the first common-horizon record. The full window includes the entire source time range. Distances and times use the original code units with initial total mass approximately one. The separation chart uses all three spatial coordinates.

Time zero corresponds to t=3691.89200847 in the original file. The earliest sample in AhC marks the first *recorded* common apparent horizon. The display preserves the brief overlap with AhA and AhB and interpolates only within each track's measured times. Circle radii represent 2 times the irreducible mass of each horizon. Their 2D appearance illustrates area-equivalent size in coordinate space. The simulation data provide no lensing image or shape contours for these circles.

**Credit.** SXS Collaboration, *Binary black-hole simulation SXS:BBH:0305*, Zenodo release 13182440, CC BY 4.0. This lab selects and interpolates coordinate centers, irreducible masses, Christodoulou masses and spin magnitudes from Lev5:Horizons.h5. It shifts the time origin, subsamples, rounds and renders the records. Original source MD5 d1e13bc439f3bc71a912cce697783ba6; metadata MD5 0d573928205effecc3c13d576774c83e. [Dataset](https://doi.org/10.5281/zenodo.13182440) · [Field definitions](https://data.black-holes.org/waveforms/documentation.html) · [License](https://creativecommons.org/licenses/by/4.0/).

## Scalar scattering

This view solves a separate equal-mass, nonspinning **head-on** model. The close-limit expansion evolves the exterior of an initially common horizon at leading order in the Brill–Lindquist binary distortion. The computation covers t=0–36 M and uses half separation 0.03 M. The birth of a common horizon and the earlier two-body approach lie outside that approximation. The SXS orbital data do not supply this scalar solver's geometry. No detector strain or astrophysical magnetic field measurement enters either scalar experiment.

The color map gives the signed coordinate field rφ on tortoise-radius shells from 4 to 28 M. The radius on screen is proportional to r*, and the field multiplies φ by the areal radius r. The center is unsampled. The map reconstructs the Legendre coefficients at 0.4 M intervals in radius and time, interpolates them, and compresses magnitude with a fixed asinh color scale for each case family. Negative is blue and positive is orange. The probe plot gives signed, uncompressed coefficient values every 0.2 M at r*=20 M. The field snapshots use per-mode signed 16-bit quantization for display; probe data are retained as double-precision decimal values in [signals.csv](signals.csv).

The initial-pulse cases reproduce BH-SCAT-001 for the monopole and quadrupole. The nominal 0.06 M half separation exceeded the original small-perturbation screen (0.1514 versus 0.10). The 0.03 M repeat passed (0.03785). The pulse comparison uses the latter. The archive contains both geometries, signed arms, resolved errors, conventional Klein–Gordon controls, source, protocol and raw results. [BH-SCAT-001 replay](BH-SCAT-001-Replay.zip).

### Magnetic source from a zero scalar

The test field has a prescribed stationary axisymmetric vector potential Aφ=b s(r) sin²θ. Its radial envelope is s(r)=r² exp[−(r−9)²/18]/2. C1 couples the scalar to the invariant FμνF^μν with illustrative coefficient c=10⁻⁵. The field strength b, mass mM=0.20 and kinetic coefficient Z=2.5 are code parameters. The initial scalar and scalar velocity are zero. The test neglects magnetic stress backreaction, plasma dynamics and scalar feedback on the prescribed electromagnetic field. Maintaining this field generally requires external currents. Starting it with zero scalar defines a transient.

On the spherical background put E=f(s′)²/r², P=4s²/r⁴, u=cos θ. Here E and P denote equatorial and polar coefficients of the **magnetic invariant**, not electric field components. The spherical-background source is 2 c b² [E(1−u²)+P u²]. With K,H the angular and diagonal geometric perturbations, the first-order correction to its densitized form is 2 c b² P₂(u)[−H E(1−u²)−K P u²]. The conservative scalar solver evolves zeroth-order ℓ=0,2 and first-order ℓ=0,2,4. A spherical initial scalar pulse is an independent case in this solver.

| Probe test, magnetic +B | Monopole | Quadrupole | ℓ=4 |
|---|---:|---:|---:|
| Peak absolute rφ | 1.64886 × 10⁻³ | 1.61014 × 10⁻⁴ | 1.86539 × 10⁻⁸ |
| Last grid difference / fine waveform norm | 0.00091% | 0.00871% | 0.02122% |
| Measured convergence order | 2.003 | 2.004 | 1.998 |

The −B waveform equaled the +B waveform at every probe sample. Doubling B gave four times the waveform in all three modes. The field-off signal stayed zero. This scaling follows from linear scalar evolution with a source quadratic in the field. It is shared by an ordinary scalar–photon model. The simulation supplies a possible mechanism in a prescribed environment; its occurrence or amplitude in an observed binary is unresolved. [Source protocol](SOURCE-PROTOCOL.md) · [Results](source-results.json) · [Frozen C1 action](https://github.com/enuminous/EFMW-Lagrangian/blob/83f9d2ec03e055c6cd09aa6359189161ad1571f6/candidate/CANDIDATE.md).

## Reproduce

From this directory, use Python 3.12 and the NumPy, SciPy, h5py and Matplotlib packages listed in the repository requirements. Node is used only for the offline data and control checks. The orbit extractor needs internet access on its first run. All scalar calculations and the browser lab work offline. These commands regenerate both data scripts, the probe CSV, and the magnetic-source result ledger.

```sh
python orbits.py /tmp/bh-horizons-cache
export OPENBLAS_NUM_THREADS=1
for h in .2 .1 .05; do python simulate.py --grid "$h" --work /tmp/bh-source-runs || exit 1; done
python simulate.py --work /tmp/bh-source-runs
node verify.cjs
```

The geometry and numerical operators in scatter.py come directly from the archived BH-SCAT-001 solver. Browser playback interpolates the recorded numerical solutions. The time slider does not launch a new 3D numerical-relativity computation.
