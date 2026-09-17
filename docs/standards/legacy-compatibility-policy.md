# SIBA ThingsBoard legacy compatibility policy

## Purpose

This policy allows new Rev A-compliant ventilation entities to coexist with the current
production tenant without forcing a broad migration. It is a planning rule only and
does not authorize creation, rename, relation change or other ThingsBoard mutation.

## Grandfathered live topology

Authenticated VENT-002 evidence confirms the current shared hierarchy:

```text
Farm
  -> FarmToArea -> Area
    -> AreaToBarn -> Barn
```

Existing Farm, Area and Barn names, profiles and the two relation types above are
classified as `LEGACY EXCEPTION`. They are not immediate migration blockers and must
not be renamed or rewired by VENT-004.

Grandfathering means compatibility, not retroactive Rev A compliance. New work must not
copy a legacy deviation unless this policy explicitly requires it for integration.

## Greenfield ventilation extension

New ventilation entities attach below an existing Barn:

```text
Existing Barn                         LEGACY EXCEPTION upstream
  -> Contains -> Ventilation System   new Rev A system Asset
    -> Contains -> Ventilation PLC    new Rev A controller Device

Gateway
  -> ConnectedTo -> Ventilation PLC   optional communication relation
```

Rules for this boundary:

- The existing Barn remains the canonical parent of the new ventilation System Asset.
- Each new System Asset and controller Device has exactly one `Contains` parent.
- `ConnectedTo` is a cross-link and never a second `Contains` parent.
- No `FarmToArea` or `AreaToBarn` relation is deleted, replaced or duplicated.
- No existing deodorization, feeding or other production dashboard is modified.
- No existing UUID is embedded into a reusable dashboard or provisioning definition.

## New-entity naming and profiles

| Object | Target technical name | Target profile |
|---|---|---|
| Ventilation System Asset | `<SITE>-<AREA>-<BUILDING>-VEN-SYS-01` | `AP-SYSTEM-V1` |
| VentilationController Device | `<SITE>-<AREA>-<BUILDING>-VEN-PLC-01` | `DP-VEN-CTRL-V1` |

`<SITE>`, `<AREA>` and `<BUILDING>` are unresolved tokens until their approved canonical
codes are mapped to the selected legacy Barn. A future executor must not derive these
codes from labels by guesswork.

## Future provisioning safeguards

Any later mutation task must, before writing:

1. Record the selected Barn ID and its current incoming/outgoing relations using GET.
2. Obtain approved site, area and building codes.
3. Prove that target names and profiles do not already exist.
4. Produce an exact create/reuse/no-op manifest and rollback manifest.
5. Preserve customer/tenant ownership of the selected Barn.
6. Stop on name collision, ambiguous Barn selection, profile mismatch or relation
   cardinality conflict.
7. Validate the new branch without changing legacy upstream relations.

Provisioning must be idempotent: an exact pre-existing object may be reused only after
its type, profile, ownership and relations match the approved manifest. A partial or
conflicting object is a blocker, not permission to overwrite it.

## Acceptance boundary

VENT-004 planning succeeds when a reviewer can distinguish:

- unchanged legacy objects;
- new Rev A objects;
- optional cross-links;
- source-data prerequisites;
- ordered future mutations and their rollback; and
- checks that remain impossible until real telemetry exists.

It does not succeed by creating any of those objects.
