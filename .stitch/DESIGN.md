---
name: SIBA Operations Dark
colors:
  background: "#0c1622"
  panel: "#152737"
  input: "#203747"
  border: "#345163"
  text: "#edf5f9"
  text-muted: "#aec4d1"
  teal: "#00d4e0"
  success: "#2ee6a8"
  warning: "#ffc857"
  danger: "#ff3b42"
---

# SIBA Operations Dark

Extracted from the live `SIBA · Khử mùi` dashboard and its repository sources on
2026-09-17. This is the visual baseline for the isolated ventilation demo.

## Foundations

- Font: Arial, with SIBA Helvetica Neue / Helvetica Neue as compatible fallbacks.
- Canvas: deep navy `#0c1622`; panels are flat `#152737` with a 1 px `#345163` border.
- Radius: 6 px panels, 4–6 px badges and inputs. No shadows or decorative gradients.
- Spacing: 8 px base rhythm; 12–16 px panel padding; 8–12 px gaps.
- Primary text `#edf5f9`; secondary text `#aec4d1`; cyan `#00d4e0` marks active
  navigation and primary monitoring values.
- Status colors are semantic: success `#2ee6a8`, warning `#ffc857`, danger `#ff3b42`.
  Missing/unknown values remain muted and are never displayed as zero.

## Components

- Compact header: 42–48 px title row, cyan product title, right-aligned context, and a
  persistent amber outlined `DEMO DATA` badge.
- State tabs: 44–48 px touch targets, transparent background, cyan active underline.
- Panels: flat bordered blocks; titles are 16–18 px and body text is 12–14 px.
- KPI cards: small outlined icon, muted label, 24 px tabular value, optional quality line.
- Tables: transparent rows, muted headers, subtle separators, horizontal pan on mobile.
- Equipment: compact bordered cards and a schematic using muted pipes plus semantic
  status outlines. All interactions are navigation/filter only.

## Responsive behavior

- Desktop retains the ThingsBoard shell and a dense multi-column monitoring canvas.
- Tablet collapses secondary columns below primary content.
- Mobile hides the preview sidebar, stacks cards in one column, keeps state tabs
  horizontally scrollable, and confines schematic/table overflow to their panels.

## Safety character

The ventilation V1 surface is observational. Do not add toggles, sliders, setpoint
inputs, command buttons, alarm lifecycle actions, RPC, or write endpoints.
