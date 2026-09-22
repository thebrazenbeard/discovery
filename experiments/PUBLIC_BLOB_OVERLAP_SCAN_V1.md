# Public portfolio blob-overlap scan V1

Status: **EXACT BYTE-IDENTITY MEASUREMENT / NO LINEAGE OR CONSOLIDATION CLAIM**

This scan binds 23 public repositories at exact default-branch heads and computes all 253 unordered pairs.

The strongest same-path overlaps by share of the smaller repository are:

- `god-brain` ↔ `hc-brain`: 299 identical same-path blobs / 300 common paths; 2181434 identical same-path bytes; 99.618593% of smaller-repo bytes; 299 shared blob SHAs anywhere.
- `god-brain` ↔ `transcendence`: 255 identical same-path blobs / 263 common paths; 1718257 identical same-path bytes; 95.352510% of smaller-repo bytes; 255 shared blob SHAs anywhere.
- `hc-brain` ↔ `transcendence`: 255 identical same-path blobs / 263 common paths; 1718257 identical same-path bytes; 95.352510% of smaller-repo bytes; 255 shared blob SHAs anywhere.
- `bt2` ↔ `transcendence`: 179 identical same-path blobs / 188 common paths; 1021406 identical same-path bytes; 56.681641% of smaller-repo bytes; 179 shared blob SHAs anywhere.
- `bt2` ↔ `god-brain`: 178 identical same-path blobs / 188 common paths; 1011147 identical same-path bytes; 46.175608% of smaller-repo bytes; 178 shared blob SHAs anywhere.
- `bt2` ↔ `hc-brain`: 178 identical same-path blobs / 188 common paths; 1011147 identical same-path bytes; 46.140315% of smaller-repo bytes; 178 shared blob SHAs anywhere.

These are discovery leads, not architectural conclusions. High overlap can be copied scaffolding, deliberate experimental isolation, generated/vendor files, shared documentation, or a genuine base/overlay family. Every candidate still requires source/provenance and maintenance-economics analysis.
