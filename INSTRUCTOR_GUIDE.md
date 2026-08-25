# CHM345_FA26 JupyterLite — Instructor Guide

> A typeset version of this guide lives in `docs/` (`instructor_guide.tex`,
> compiled to PDF with `tectonic`) — nicer for printing or sharing with
> colleagues. When editing one, update the other.

*Last verified 2026-08-24 against the pinned versions in `requirements.txt`
(jupyterlite-core 0.8.3, pyodide-kernel 0.8.5, ipympl 0.10.0; Pyodide ships
numpy 2.4.6, matplotlib 3.10.8, pandas 3.0.2, h5py 3.13.0).*

## How the site works (30-second model)

- `content/` **is** the students' file browser. At every push to `main`, GitHub
  Actions rebuilds the site and deploys it. What students open in their browser
  is a *seed copy*; their edits live in their own browser's storage, layered on
  top. Anything they haven't touched always mirrors `content/`.
- **A student's local copy shadows the seed.** Once someone opens a notebook,
  pushing edits to that same file won't reach them. Publish a `_v2` filename to
  fix a notebook people have started.
- The pinned `requirements.txt` freezes every version for the semester. Don't
  upgrade anything until winter break.

## Weekly publishing rhythm

1. Author/edit the week's notebook wherever you like (drafts stay OUT of this
   repo — everything in `content/` is world-readable the moment you push).
   Steven's released student versions arrive cell-locked by nbgrader
   (markdown uneditable); unlock before editing:
   ```bash
   python3 tools/unlock_notebook.py path/to/Notebook.ipynb
   ```
2. When final, copy the week folder in: `content/Week_05a.WhateverItIs/` —
   **student files only.** Instructor/solution notebooks often live in the
   same working folder; they must never come along. (`.gitignore` blocks any
   `*instructor*.ipynb` as a backstop, but check what you copied.)
3. Preview locally (see below), then:
   ```bash
   git add content/Week_05a.WhateverItIs
   git commit -m "Publish week 5a"
   git push
   ```
4. ~2 minutes later it's live. Verify **in a private/incognito window** —
   incognito always shows exactly what's published, with no local shadow.

To *unpublish*: `git rm -r content/<folder>`, commit, push. It vanishes from
the seed (students who already opened it keep their local copy).

## Previewing and iterating

- **Local preview (identical to production):**
  ```bash
  mkdir -p content   # git drops the dir entirely if it's empty
  ~/miniforge3/envs/chm345lite/bin/jupyter lite build --contents content --output-dir _output
  cd _output && ~/miniforge3/envs/chm345lite/bin/python -m http.server 8898
  ```
  then open http://127.0.0.1:8898 — same Pyodide, same wheels, same everything.
- **On the live site:** iterate freely *before* sharing the link. Test in
  incognito each time, or delete your local copy of the file in the JupyterLite
  file browser (that restores the fresh seed). The "can't update an opened
  notebook" rule is per-browser-profile, not global.

## Adapting each notebook for JupyterLite (checklist)

1. **Interactive plots:** the install cell must run **before any code cell
   that imports matplotlib** (once matplotlib is imported, the widget backend
   can't register until kernel restart). Will's convention: the notebook's
   opening markdown/title cell stays first — markdown doesn't affect this —
   then these two code cells, then the usual imports:
   ```
   %pip install -q ipympl
   ```
   ```
   %matplotlib widget
   import numpy as np
   import matplotlib.pyplot as plt
   ...
   ```
   Wheels are bundled in the site (`pypi/`), so `%pip install` works offline
   and always gets the pinned version. Delete any `%matplotlib inline` lines.
2. **MECLib weeks:** copy `MECLib.py` into that week's folder (visible to
   students, same folder as the notebook) and change the collaborator's
   `import meclib.cl as cl` to `import MECLib as cl`. Notes:
   - MECLib.py (2024) imports `h5io` at the top, so add `h5io` to the header
     install cell (`%pip install -q ipympl h5io`) — or delete the `import h5io`
     line from MECLib.py if you've dropped HDF5 (2026 notebooks use pickle).
   - The 2024 file **lacks** functions the 2026 notebooks call:
     `SaveMyScenario`, `LoadMyScenario` (2024 has HDF5-based `GetMyScenario`),
     `CS_list_plots` (2024: `Climatestate_list_plots`, different args), and
     `CS_list_compare`. Get the current source from your collaborator or add
     pickle-based versions before the first MECLib week (his notebooks first
     import it in Week 4).
3. **Scenario files:** notebooks reference `../../ScenarioLibrary/…`, which
   escapes the student drive. Keep a `ScenarioLibrary/` folder at `content/`
   root and change paths to `../ScenarioLibrary/…`. Ship pre-built `.pkl`
   fixtures for later weeks so a student who lost their Week-4 output isn't
   stuck. (Verified: the existing course `.pkl` files load fine in Pyodide.)
4. **Week 11 (ClimateStats):** the NOAA `https://gml.noaa.gov/...` downloads
   will NOT work in the browser (CORS). Use the local `brw/` data folder that
   already exists next to the notebook and point `pd.read_csv` at
   `brw/met_brw_insitu_1_obop_hour_YYYY.txt`. The folder has 1977–2000 and
   2017–2021; the notebook currently asks for 2020–2025 — reconcile the years.
5. **Images:** `http://` images (webspace.pugetsound.edu) are blocked on an
   HTTPS site. Save them into the week folder and use relative paths.
6. **HDF5:** works for arrays/scalars (h5py, h5io). One limitation: reading
   *DataFrames stored inside* HDF5 (the 2024 scenario format) needs pytables,
   which Pyodide doesn't have. Use pickle for anything with a DataFrame —
   which is what the 2026 notebooks already do.

## Hard rules

- **Never** put instructor/solution notebooks anywhere in this repo. The
  `.gitignore` blocks `*instructor*` paths as a backstop, but the real rule is:
  solutions live outside `~/Desktop/Courses/CHM345/JupyterLite` entirely.
- Don't push half-finished notebooks to `main` — pushing = publishing.
- Don't change `requirements.txt` or `pypi/*.whl` mid-semester.

## Student-facing habits — the week-1 talk

**Where your work lives.** Student edits are stored by the browser (IndexedDB),
keyed to the site address. Their "Jupyter" is: *same computer + same browser +
same profile*. Within that combination, work persists indefinitely — across
closed tabs, restarts, and weeks away.

**What wipes or "loses" work — warn students explicitly:**

- **Clearing browsing data.** Strictly it's "cookies and site data" (not the
  image cache) that deletes work, but students won't distinguish — treat any
  clear-my-browser action as fatal to unsaved-elsewhere work.
- **Switching browser, profile, or computer** — work doesn't follow. It's not
  deleted (it's still in the original browser), but they'll see a fresh copy
  and panic. Lab machines that reset profiles on logout lose work every time —
  students on lab computers MUST download at the end of each session.
- **Safari auto-evicts** site storage after ~7 days without a visit. Weekly
  class use mostly protects them; a break doesn't. Recommend Chrome/Firefox.
- **Nearly-full disks** can trigger the browser to evict site storage.
- **Incognito/private windows**: everything evaporates when the window closes.
  Say it explicitly: *never do coursework in a private window.*
- Deleting a file in the Jupyter file browser resets that file to the
  published version (this is also the fix if they've mangled a notebook and
  want a fresh start).

**The safety net: download your notebook at the end of every session.** This
is self-enforcing here, since submitting to Gradescope requires downloading —
every submission doubles as an off-browser backup. Recovery is the Upload
button. A system-check cell that verifies file storage is active
(`os.getcwd()` starts with `/drive`) is in `tests/smoke/Welcome.ipynb` —
paste it into your own week-1 notebook; run it if anyone's saves vanish.
(Per Will's rule, only notebooks authored by Will or Steven are published,
so that reference notebook itself stays out of `content/`.)

**If plots or `%matplotlib widget` misbehave:** Kernel → Restart, then **Run
All** (not "continue where you were"). Two things students should understand:
(1) if matplotlib gets imported before the `%pip install -q ipympl` cell has
run, `%matplotlib widget` errors with "'widget' is not a recognised GUI loop
or backend name" — the backend list is frozen at first matplotlib import;
(2) restarting wipes `%pip`-installed packages along with everything else, so
the install cell must be re-run after every restart. It's instant (wheels are
served from the course site) — but "restart, then run from the top" is the
reflex to drill, and it fixes this error every time.

## Semester watch list (from the August 2026 notebook audit)

- **Week 4 prep — MECLib: RESOLVED Aug 2026.** Steven's current `MECLib.py`
  (in `~/Desktop/Past MEC materials/`) has every function the 2026 notebooks
  call, is pickle-based (no h5io), and passed a full in-browser model run
  (Cambio2, 599 steps). Before publishing it: strip the leaked
  `### END SOLUTION` marker (~line 233). Known latent bug, not course-blocking:
  `Diagnose_Delta_T_from_albedo` reads underscore-style keys
  (`'albedo_sensitivity'`) that `CreateClimateParams` never creates (it uses
  spaces) — KeyErrors if ever called; worth reporting to Steven. A few
  functions lack docstrings (`run_Cambio`, `CS_list_plots`, `CS_list_compare`).
- **Week 4:** create `content/ScenarioLibrary/` + fix `../../` → `../` paths
  (9 notebooks). Generate fixture .pkls — `Peaks_in_2040_LTE.pkl` (weeks 6,
  11, 13) doesn't exist yet; only `Peaks_in_2040.pkl` and `RCP4_5.pkl` do.
- **Week 6:** delete `%matplotlib inline` from Cambio1.0 (kills the widget
  backend). The hardcoded `index_of_2003` value is tied to the fixture's
  time grid — regenerating .pkls with different `nsteps` silently breaks it
  (wrong answers, not errors).
- **Weeks 3/4c/7/10:** vendor the four `http://webspace.pugetsound.edu`
  images (mixed content = blocked) + the two hotlinked HTTPS images in 10b.
- **Weeks 10/13:** add `pint` to the install cell; warn students its first
  import takes a few seconds (not hung).
- **Week 11:** NOAA `https://gml.noaa.gov` downloads fail in-browser (CORS).
  Use the local `brw/` folder (17 MB, already next to the notebook) — but
  reconcile years: notebook wants 2020–2025, folder has 1977–2000 + 2017–2021.
- **Every week:** copy only the needed files into `content/` — source folders
  contain hidden `.hdf5`/`.pkl` dotfiles, a 2.9 MB `.ClimateStats.ipynb` old
  draft, `__pycache__`, checkpoints, `.DS_Store`. And remember several student
  notebooks (04a, 11a, 11b, 13b) NameError on Restart-&-Run-All *by design*
  until blanks are filled — word the closing instruction accordingly.
- **Never regenerate student-facing .pkl files casually** — pickles are tied
  to the (frozen) pandas version. Safe only because nothing gets upgraded.

## Local machinery reference

- Build env: conda env `chm345lite` (`~/miniforge3/envs/chm345lite`).
- `tests/smoke/` (gitignored): `SmokeTest.ipynb` runs 11 automated checks and
  prints `SMOKE_OK`; `MiniTest.ipynb` is the minimal widget-pattern test.
  Build with `--contents content --contents tests/smoke` to include them
  locally; the deploy workflow builds `--contents content` only, so they can
  never reach the public site.
