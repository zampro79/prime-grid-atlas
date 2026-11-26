# Research I source provenance

## Provenance status

The complete source snapshot that generated the original Research I outputs
has not been cryptographically identified. The datasets first entered the
public repository in commit
`a853dfd19e53264d5fa3542d294083ebeb2db1ee` on 2026-11-26, together with
release-preparation sources that already used the fixed non-DC normalization.
That public commit is therefore not the generating snapshot recorded by the
historical manifest.

The original generation time is not recorded. The outputs existed no later
than the public import commit above. Filesystem checkout times are not treated
as generation timestamps.

## Historical manifest

The preserved manifest records Linux, CPU/NumPy, Python 3.14.7, NumPy 2.5.3,
seed `20260910`, 500 trials and 50 replicates. Its required application hashes
are:

| Module | Required SHA-256 | Recovered candidate |
|---|---|---|
| `app_config.py` | `64002e74658ef47099a2e6fe32de9f31162d8747589f3a559c8a98e5fcca0ebe` | match |
| `atlas_engine.py` | `8949df32b932d040b713742a0446e9640d96fea209457db4b1f125724c03b821` | missing |
| `compute_backend.py` | `771fbdf2fc6dfdaa7e5c04493b6f6e00473f8638c7eded9feb5c921b4efad54a` | match |
| `grid_model.py` | `8a6ce29ae0f13163dd7fb4bb58b74dc506f258fc209a37c8f42deea07349df5d` | match |
| `main.py` | `fd325f55103dedf46b061c6c7be66bf1982cb8b00b01a0156c83a6d60a272528` | missing |
| `metrics.py` | `7850e4761c69bf00d1c26ae2ebbc1587229afd6a83433004f5bd84b8e3701b9a` | missing |
| `mode_catalog.py` | `4a782844f07d489364155eacd1e4e68a428a9732bf23778c3f050878606bf09d` | missing |
| `number_theory.py` | `48eb64f91f822f848b8a81f92860dcd29712541f8ced61de9d38482c3da47f74` | match |
| `qt_app.py` | `0b50bde0e6939888ae0352359203cc392e1f9a8ba80fa5032e75d79b3c68fa87` | missing |

Four of nine source hashes were recovered exactly. Five remain unavailable.

## Partial historical candidate

A partial candidate was recovered at commit
`4bf12b311d0ed391133ad98d5f0231d03a349058`. The commit is later than the
public v1.0.0 release and must not be described as the commit that generated
the original outputs. It contains:

- all published Research I evidence files byte for byte;
- a byte-identical copy of the experimental script published in v1.0.0;
- the audit-era positive-support formula;
- four of the nine required source hashes.

The script match establishes identity with the published script only. It does
not establish identity with an unavailable earlier script version. Running the
unmodified candidate in isolation reproduced all eleven CSV files exactly, but
tested functional equivalence is not complete source identity.

## Environment distinction

| Property | Historical manifest | Verified reruns |
|---|---|---|
| Python | 3.14.7 | 3.14.10 |
| NumPy | 2.5.3 | 2.4.6 |
| Backend | CPU / NumPy | CPU / NumPy |
| Platform | Linux | Linux x86-64 |
| CUDA | unavailable/not verified | unavailable/not verified |

The historical environment was not restored. Exact CSV equality across these
two recorded environments is evidence of stability for this protocol, not a
general cross-version guarantee.

## Conclusions

- **Cryptographic identity:** partial, four of nine modules.
- **Numerical reproduction:** exact for all eleven CSV files.
- **Functional equivalence:** verified only for the exercised protocol.
- **Complete historical snapshot identity:** not verified.
