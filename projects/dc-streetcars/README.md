# DC Streetcars — temporal specification implementation

This is the updated runnable project, based on Claude's September 30, 2026 editor and saved draft. The `legacy` directory preserves the recovered original editor, draft, OSM export, research JSON and large spreadsheet. No historical return directions or stop sequences have been inferred.

## Run

Extract this folder, run `python3 serve.py` inside it, and open http://127.0.0.1:8765. No runtime package install is required. Leaflet is bundled locally; optional Google Fonts may fall back to the system font when offline.

The starting model contains 1,578 nodes, 381 ways and 277 research relations. All original coordinates, topology, IDs, tags and ordered relation members are retained. Generic inherited traction is also recorded under the proposed `streetcar:traction` key, without inferring power collection technology. The original research-map coloring remains a research summary; use **Verified services only** to inspect explicitly verified service paths.

## Workflows

- **Edit map → Services & evidence → New service** creates only explicitly supplied directional variants, with stable service and direction identities, ordered members, from/to nodes and citations. Add another direction explicitly using the workbench. A research line identifier is an association, not an official route ref.
- Select a dated service master in the workbench. Leave the transition date blank for a correction. Enter a date for an actual historical transition: this creates a new master and synchronized child states, including copies of unchanged directions. The chronology preserves continuity. “Merge with next equal state” requires complete ordered semantic and evidence equality.
- **Physical transition** splits a track's temporal state and updates service dependencies. Provisional corridor records are split faithfully at the same boundary, retaining their unresolved research status. Geometry reshaping in the original map tools is a correction. For a historical geometry change, construct the evidenced geometry and enter its ordered node IDs in the physical transition form; the old geometry remains available to earlier states.
- **Track evidence** records citations and explicit retracing/gauge claims. A citation alone does not clear inherited OSM geometry restrictions.
- **Inspect date** filters using actual calendar dates. Years and months retain their input precision and normalize to the first day solely for deterministic comparisons. Intervals include the start and exclude the end.
- **Check issues** separates structural errors, publication blockers and review warnings. Contemporaneous geometric crossings are flagged for historical review; they are not automatically converted into switches or diamonds. A marked diamond prohibits turning between intersecting tracks.
- **Export / import** provides a working JSON archive with metadata/evidence, working XML, selected-service strict temporal XML and exact-date snapshots. Snapshots include complete node/way dependencies and omit chronologies. Strict export refuses structural errors. The publication checkbox additionally refuses unresolved evidence/provenance. XML is always marked `upload="never"`; publication readiness is a review status, not an upload action. Export manifests retain evidence metadata and issue lists.
- Older `dcsc-model-v1` browser drafts are left untouched. **Recover older browser draft** downloads them; explicitly import that file to migrate it. A new v2 browser storage key protects the original. Imports validate IDs and references before replacing the model; failed edits roll back atomically. Undo/redo includes metadata. Audit entries are retained in the working archive; undo history itself is session-local.

## Source and build

`index.html` is the runnable built editor with embedded baseline data and model engine. `temporal.js` is the independently testable profile engine; `workbench.js` supplies the new editor controls. `python3 build.py` regenerates the editor and the baseline working archive from the recovered originals. Keep these files together when making future changes.

The specification is included under `docs`. The `exports/dcsc-project-v2.json` file is the migrated baseline, not a verified service dataset. Gauge 1435 is preserved as inherited data and receives an evidence warning. The one inherited undated way remains unresolved. No track offsets, stop locations, switch movements, electric collection systems or official route numbers are manufactured.

## Verification

Run `node --test tests/profile.test.js` (or `npm test`). Twenty-two regression tests cover calendar validity, date precision, half-open boundaries, synchronized transitions, atomic rollback, reverse and repeated members, conservative combination/merging, physical dependency updates, stop order, crossing time/grade separation, strict/snapshot exports and exact baseline preservation.

Browser checks exercise the actual workbench, transition form, undo/redo, reload, snapshot download and publication gate. To rerun, install Playwright and its Chromium browser, start `serve.py`, then run `node tests/browser.cjs`. `CHROMIUM_PATH` can select an already installed Chromium executable. Browser-only fixtures are created in that test's isolated browser session and are not included in the baseline.

## Historical work still required

The implementation provides the specification's model and authoring/validation/export workflows. Existing 216 route-like research relations are provisional corridors, not automatically converted passenger services. Historical directional paths, service continuity, stops, gauge, topology and independent track geometry still require evidence. Crossing review is a geometric screening aid and does not establish historical grade or permitted movements. Generalized original street-centerline geometry remains visibly provisional and blocked from publication.
