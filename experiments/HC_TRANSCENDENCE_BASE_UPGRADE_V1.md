# HC-Brain → Transcendence Base Upgrade Simulation V1

Status: **EXPERIMENTING / FIRST REAL BASE-UPGRADE EVENT**

The exact reconstruction experiment established that current Transcendence can
be factored as pinned HC PR #22 plus an explicit overlay.

This follow-up asks a different question:

> When the HC base moves, how much does the Transcendence overlay itself have to
> change?

## Upgrade subjects

Old base:

- HC main `618245b54fb923c7a204892c6953ab6d1c5dac57`
- tree `623f272aa9060ad9e222a5cfaea801082bb5a562`

New base:

- HC PR #22 `5929da3e8904e23e484df0deac920a008ec33d52`
- tree `e4c7fcedaa77cf5d2794491a99326db67740a272`

Fixed target:

- Transcendence PR #7 `be3785c83dbe89b0d4236b43eda97a277eb6baad`
- tree `112a44d8042556b87f19b3dac05ec34a5ea2f796`

## Measured overlay churn

Against old HC main, the exact target overlay requires:

- 37 deletes;
- 9 overwrites;
- 25 additions;
- 71 instructions total;
- 34 payload files;
- 286,362 payload bytes.

Against HC PR #22:

- 39 deletes;
- 9 overwrites;
- 25 additions;
- 73 instructions total;
- 34 payload files;
- 286,362 payload bytes.

Only **8 overlay instructions** change.

Of the current 73 instructions, **65 remain unchanged**.

Current instruction churn share: **10.958904110%**.

Only two instructions are genuinely new: the new HC motor-control implementation
and its test are explicitly deleted from the Transcendence reconstruction.

The other changes update base preimages for files Transcendence already deletes
or overwrites.

## Important limitation

This upgrade is favorable, but it is not yet a hard conflict test.

HC changed eight paths between these bases. None of those changes touched a
target path that Transcendence currently inherits byte-for-byte.

Therefore this event demonstrates:

`ONE_REAL_LOW_CHURN_BASE_UPGRADE`

but not:

`LOW_COST_WHEN_SHARED_INHERITED_BYTES_CHANGE`.

That distinction matters. A dependency can look cheap while all upstream change
happens outside the inherited surface.

## Current implication

The factorization remains technically plausible:

- overlay payload bytes did not grow;
- Transcendence-specific payload did not change;
- new HC functionality did not leak into Transcendence;
- explicit deletion semantics safely excluded the new motor-control surface.

This strengthens the case enough to continue the experiment, but not enough to
adopt the dependency.

## Next falsifier

Use real HC history to find a base transition that modifies at least one path
that the Transcendence target otherwise inherits unchanged.

Then measure whether the overlay can preserve the Transcendence target with a
small explicit override, or whether shared-byte evolution creates substantial
conflict/qualification burden.

Synthetic edits should not substitute for a real historical base transition if
one is available.
