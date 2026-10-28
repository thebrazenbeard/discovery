# Public identity receipt: structural check V1

Status: **SOURCE-ONLY INTERNAL CONSISTENCY CHECK — NOT A BASELINE ADMISSION**

`tools/validate_public_identity_probe.py /absolute/path/to/captured-receipt.json` checks a read-only 2026-10-28 public identity observation without rewriting any historical V1 evidence or proposing itself as authority. The receipt may live outside this repository.

It requires:

- the correct owner, receipt schema, timestamps, and explicit non-admission state;
- 1:1 counts of B0, B1 and captured subjects, with a matching archive count;
- sorted, case-insensitively unique names; unique positive numeric repository IDs; and valid exact Git commit/tree IDs;
- empty reported collection errors/head drift, reported stable membership, and independently recomputed SHA-256 identity/name digest values;
- JSON object keys that do not repeat.

On success it reports `LOCAL_IDENTITY_STRUCTURE_PASS_ONLY`, not `ADMITTED`. A valid hash proves the receipt's internally stated subject vector matches its digest, **not** that GitHub supplied it or that the B0/B1 observation was stable. The 2026-10-28 receipt retained one subject vector and summary flags, **not** both independent full B0/B1 vectors. Its claimed stability therefore cannot be replayed from that file alone.

Independent evidence remains necessary for: source-bound policy and profile digests; independently replayable B0/B1 exact membership, HEAD and tree; V1-to-new membership transition dispositions (including redirect verification); authorized independent review; and runtime/currentness/installation effects. This command does not create a grant, change a watcher baseline, merge, deploy, update historical evidence, or perform network I/O.

The tests live in `tests/test_public_identity_probe_receipt.py`. Run `python -m unittest discover -s tests -p 'test_public_identity_probe_receipt.py' -v`.
