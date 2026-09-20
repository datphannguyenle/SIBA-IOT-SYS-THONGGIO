# Original ventilation illustration

`ventilation-barn-v1.png` — generated with the built-in imagegen tool on 20/09/2026.
Source: the tool's local generated artifact, copied into this repository without visual edits.
Displayed as conceptual architecture only, with an explicit caption. Not a photograph,
installation drawing, equipment inventory, airflow direction or live status evidence.
The ThingsBoard builder embeds `ventilation-barn-v1.webp`, encoded at the same resolution
for transport by `tools/encode_dashboard_asset.py`; no third-party image request is needed.
The original PNG is retained unchanged. The conversion changes compression, not geometry
or composition. It is necessary because live TB rejects oversized descriptor strings
with PostgreSQL `value too long for type character varying(1000000)`.

## Final generation prompt

Use case: stylized-concept. Asset type: original compact dashboard illustration for a Vietnamese industrial livestock ventilation monitoring module called SIBA; this is an illustration asset, NOT an image of a dashboard. Create a premium, restrained isometric 3D architectural miniature of a long modern ventilated livestock barn, showing a partial roof cutaway, subtle roof and side air inlets, industrial axial exhaust fan modules, metal structural ribs and a clean simplified interior floor. Elevated three-quarter view, whole building visible, centered composition with generous margins, landscape 3:2. Matte navy and slate materials, restrained cyan accents matching #00d4e0, silver-gray structural details, background solid flat #152737 so it integrates in a dark navy monitoring panel. Soft clear studio lighting, crisp high-quality geometry, not futuristic sci-fi, not photoreal farm photography, no ornamental glow. Subject should read well at a small 360px size. No people, no livestock, no vegetation, no arbitrary props. No labels, no text, no letters, no logos, no watermark, no gauges, no dashboards, no telemetry, no arrows, no motion trails, no operational status indicators. This is conceptual architecture only, not an engineering drawing or exact physical installation.
