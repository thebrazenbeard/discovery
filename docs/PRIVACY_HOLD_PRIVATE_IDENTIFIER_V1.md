# Discovery Privacy Hold — Historical Private-Identifier Filename

Status: **HOLD / REMEDIATION REQUIRES SEPARATE AUTHORITY**

A public Discovery source candidate historically introduced a filename whose basename contains the identifier of a private portfolio project.

The candidate's current contents no longer identify that private repository and Discovery's current public-facing rules prohibit expanding private repository identities without authorization.

However, the filename and prior public Git objects remain provenance.

The Exodus does not authorize destructive deletion, branch deletion, force-push, history rewrite, visibility change, or other destructive/publication remediation.

Therefore:

- do not cite or repeat the private identifier unnecessarily in future public material;
- do not treat current content sanitization as historical erasure;
- preserve this as a known privacy defect;
- if Patrick later authorizes remediation, define the exact target objects and whether the goal is current-tree cleanup, branch/PR cleanup, or history rewrite;
- verify the effect after any authorized remediation.

This hold does not block Discovery's reconstructibility or read-only/source experimentation, but it does block any claim that the accidental public identifier exposure was fully removed.
