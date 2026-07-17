# Multi-agent pattern diagrams

The pattern diagrams are **hand-authored SVG** — edit the `.svg` files
directly (they are small, structured, and text-labelled; a label swap
is a one-line change). Keep examples general agentic work (research,
support, data, content); security-themed labels belong only in the
diagrams embedded by the security concept pages.

The `tulip-patterns.drawio` file was an earlier authoring source and
is **out of date** with the current SVGs. If you prefer editing in
[draw.io](https://app.diagrams.net/), re-import first — don't export
over the current SVGs from the stale source.

## Files

| | |
|---|---|
| **`tulip-patterns.drawio`** | Legacy authoring source (stale — see note above). Seven tabs — Composition, Orchestrator, Swarm, Handoff, StateGraph, Functional, A2A. |
| `composition.svg` | Rendered Composition diagram. Embedded in `docs/concepts/multi-agent/composition.md`. |
| `orchestrator.svg` | Rendered Orchestrator diagram. |
| `swarm.svg` | Rendered Swarm diagram. |
| `handoff.svg` | Rendered Handoff diagram. |
| `graph.svg` | Rendered StateGraph diagram. |
| `functional.svg` | Rendered Functional API diagram. |
| `a2a.svg` | Rendered A2A diagram. |

## Edit workflow

1. Open the `.svg` in your editor — labels are plain `<text>` elements;
   geometry (rects, arrows) rarely needs to move for a wording change.
2. Keep the palette below, keep `text-anchor="middle"` labels centred on
   their boxes, and sanity-check long labels against their box width.
3. Rebuild the site (`hatch run build`) and eyeball the page.
4. Commit the `.svg`. (If you edited via draw.io instead, commit the
   updated `.drawio` too so it stops being stale.)

## Colour palette (matches the tulip brand)

These come from the tuliplabs
brand sheet:

| Use | Hex |
|---|---|
| Think / source / structure | `#E2570E` (deep teal · accent1) |
| Execute / primary action / final | `#D6336C` (tulip pink) |
| Reflect / data plane / sage cards | `#F4A6C2` (sage teal · accent5) |
| Terminate / shared state / decision | `#F7A21E` (sand · accent4) |
| Mauve / dashed result-flow arrows | `#9D174D` (mauve · accent2) |
| Card text on dark cards | `#FFFFFF` |
| Card text on light cards | `#1F2828` / `#3A2A0F` |
| Hairlines, default text | `#2A2F2F` (dk1) |

The dashed-mauve arrow style is the convention for **derived /
result data flowing back** (the merge step in Composition's parallel
mode, the responses returning to the Coordinator in Orchestrator,
the gather step in Functional). The solid pink arrow is for
**primary cross-boundary connections** (handoff, A2A wire).

## Why draw.io

- **Open format** — the `.drawio` file is XML, diff-friendly under
  git.
- **Editable in browser** — no install needed; <https://app.diagrams.net/>.
- **Exports SVG** that renders crisply at any size.
- **Works offline** — the desktop app at <https://github.com/jgraph/drawio-desktop>
  reads the same files.
