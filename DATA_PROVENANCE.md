# Data provenance

Original source: **LIGO Scientific Collaboration, Virgo Collaboration and KAGRA Collaboration**, *GW250114 discovery paper figure scripts*, Zenodo v1, published **10 September 2025**, [doi:10.5281/zenodo.16877102](https://doi.org/10.5281/zenodo.16877102). Dataset metadata identifies **CC BY 4.0**. Accessed 31 October 2026.

Associated peer-reviewed paper: *GW250114: Testing Hawking’s Area Law and the Kerr Nature of Black Holes*, PRL 135, 111403 (2025), [doi:10.1103/kw5g-d732](https://doi.org/10.1103/kw5g-d732). The collaboration does not endorse this downstream work.

The original archive is retained only in the local download cache, not committed to Git. Its MD5 matches the publisher's value; SHA-256 and selected member hashes are in `sources/data-manifest.json`. The original metadata is preserved in `sources/zenodo-record.json`.

The committed `data/area_inputs.npz` changes storage format and selects arrays, without rounding, resampling or altering the selected original numbers. Keys:

| Cache key | Original source |
|---|---|
| times; pre_0 through pre_15 | data/area_law_inspiral_data.hdf5: times; area_insp_0 through area_insp_15 |
| post_ringdown; mass; spin | data/ringdown_areas/220_10.5M_final_mass_spin_area.hdf5: Area_f; M_f; chi_f |
| post_pyring | data/remnant_area_pyring_reweighted.npy |
| ring_MODEL_TIME | Corresponding data/ringdown_areas/MODEL_TIMEM_final_mass_spin_area.hdf5: Area_f |
| post_pooled | Derived selection: 2,000 samples from each reference ringdown code, seed 250114, without replacement, matching the upstream numerical-macro script |

The cache does not include strain, all source parameter posteriors or a standalone likelihood. Native area arrays use (G M_sun/c²)². The supplied mass/spin arrays reproduce these areas with the Kerr formula. Multiplying by the squared solar gravitational radius gives detector-frame km².

`sources/upstream/` includes the selected original source scripts used to identify data paths and reproduce pooling/statistics, with their original content unchanged and this attribution. Other extracted files remain in the ignored download cache. Local synthetic data are separately generated from the frozen protocol and are never labeled observational.
