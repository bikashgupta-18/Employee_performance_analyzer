# Employee Performance Analyzer
**21CSC203P — Advanced Programming Practice | Individual Integrated Assignment (Roll 61–65)**

One integrated Python application combining all four required paradigms:

| Requirement | Where it is used |
|---|---|
| **Functional Programming** (min. 3) | `map()`, `filter()`, `reduce()`, `lambda`, dict/set comprehensions, higher-order function `make_score_band()` — all in `server.py → analyze()` |
| **TCP Client–Server** (`socket`) | `client.py` sends a 12-employee JSON dataset over TCP; `server.py` listens on port **65432**, processes and replies |
| **FSM** (min. 3 states) | `PerformanceFSM` class in `server.py` — **5 states** × **4 input events** = 20 transitions |
| **SymPy** | Symbolic score formula, exact rational weights, `solve()` for required quality, `diff()` for sensitivity, `simplify()` weight check |
| **Testing** | `test_cases.py` — **3 test cases**, one command each, **32 automated checks**, all passing |

## Files
- `server.py` — TCP server + functional pipeline + FSM + SymPy engine
- `client.py` — TCP client + 12-employee dataset (3 departments) + report printer
- `test_cases.py` — 3 independent test cases (each runs with its own command)
- `START SERVER.bat` / `START CLIENT.bat` / `RUN 3 TESTS.bat` — double-click launchers (work from any folder)
- `test_case_1_output.txt` — output of Test Case 1 (functional pipeline)
- `test_case_2_output.txt` — output of Test Case 2 (FSM + edge cases)
- `test_case_3_output.txt` — output of Test Case 3 (SymPy + TCP round trip)
- `demo_output.txt` — printed client report from a live client→server run
- `server_log.txt` — server console output from the same run
- `test_output.txt` — full test-run transcript of all 3 test cases (32/32 PASS)

## How to run

### Option A — easiest: double-click the launcher files (no typing, no wrong folder)
| Double-click | What it does |
|---|---|
| `START SERVER.bat` | Opens a window in the correct folder and starts the TCP server (keep it open) |
| `START CLIENT.bat` | Opens a window in the correct folder, connects to the server, prints the report (run after the server) |
| `RUN 3 TESTS.bat` | Runs Test Case 1, 2 and 3 one after another in one window (server not needed) |

Each launcher automatically switches to the project folder before running, so it works from anywhere.

### Option B — typing commands in a terminal
**Important:** you MUST be inside this folder, otherwise Python reports
`can't open file '...server.py': [Errno 2] No such file or directory`.
Always start with:
```
cd C:\Users\DELL\Downloads\app_project\employee_performance_analyzer
```

1. **Terminal 1 (server first):**
   ```
   python server.py
   ```
2. **Terminal 2 (client):**
   ```
   python client.py
   ```
3. **Tests — one command per test case (either terminal):**
   ```
   python test_cases.py 1     # Test Case 1 : Full dataset - functional analysis pipeline
   python test_cases.py 2     # Test Case 2 : FSM verification with edge-case employees
   python test_cases.py 3     # Test Case 3 : SymPy symbolic model + TCP client-server round trip
   ```
   Run all three together (no argument):
   ```
   python test_cases.py
   ```

> Python 3.10+ and SymPy required: `pip install sympy`

## How the scoring model works (SymPy symbolic formula)
```
Score = 100·w_task·task_ratio + w_quality·quality + w_attendance·attendance + w_overtime·overtime_norm
weights: w_task = 35/100, w_quality = 35/100, w_attendance = 20/100, w_overtime = 10/100   (sum = 1 exactly)
```
- `task_ratio = tasks_completed / tasks_assigned` (guarded against 0)
- `overtime_norm = min(overtime, 40)/40 × 100`
- `solve(Score − 75, quality)` → quality needed to reach 75 (e.g., Ravi Kumar needs **91.71**)
- `diff(Score, w_quality)` → `quality` → Kavya Menon (92) is most sensitive to quality-weight changes

## FSM (5 states, 4 inputs: LOW<60, OK<75, GOOD<85, EXCELLENT≥85)
```
             LOW          OK           GOOD             EXCELLENT
NEW_JOINER → PROBATION / AVERAGE / HIGH_PERFORMER / HIGH_PERFORMER   (new joiners capped)
PROBATION  → PROBATION / AVERAGE / HIGH_PERFORMER / HIGH_PERFORMER
AVERAGE    → PROBATION / AVERAGE / HIGH_PERFORMER / TOP_PERFORMER
HIGH_PERFORMER → PROBATION / AVERAGE / HIGH_PERFORMER / TOP_PERFORMER
TOP_PERFORMER  → AVERAGE / HIGH_PERFORMER / TOP_PERFORMER / TOP_PERFORMER
```
Recommendations: PROBATION→PIP, AVERAGE→training, HIGH_PERFORMER→bonus, TOP_PERFORMER→promotion.

## Live-run results (demo)
- 12 employees, company average **77.16**
- Best: **Kavya Menon (E108)** — 89.93 → TOP_PERFORMER
- State distribution: 2 PROBATION, 2 AVERAGE, 6 HIGH_PERFORMER, 2 TOP_PERFORMER
- Department averages: Development 83.56 > QA 74.25 > Design 73.66

---

# Guide for the 4-page A4 written work (write in your own handwriting/words)

**Page 1 — Title, Problem Statement & Objectives**
- Title: "Employee Performance Analyzer — Integrating Functional Programming, TCP Client–Server, FSM and SymPy"
- Problem: organisations need a unified tool that ingests raw employee data over a network, computes a transparent weighted performance score, classifies each employee through an appraisal lifecycle, and answers "what-if" questions symbolically.
- Objectives: (1) transmit employee data over TCP sockets, (2) process it functionally (no loops where FP works), (3) model appraisal as a deterministic FSM, (4) use SymPy to solve for required performance inputs, (5) produce ranked, department-wise reports.

**Page 2 — System Architecture + Algorithm/Flowchart**
- Architecture diagram: `[Client PC: dataset → JSON over TCP:65432] → [Server: functional pipeline → FSM → SymPy → JSON report] → [Client: printed report]`
- Algorithm: 1) Prepare dataset (12 records, 9 fields). 2) Client serialises to JSON, sends one line over TCP. 3) Server receives, `map()` attaches SymPy score to each record. 4) `map()` runs each record through FSM (start state from experience). 5) `filter()` separates weak (<60) and star (≥85) performers. 6) `reduce()` computes company average and best employee. 7) dict comprehension builds department summary. 8) SymPy: weight-sum check, `solve()` for required quality, `diff()` sensitivity. 9) Server sends JSON report; client prints tables. 10) 3 test cases verify everything.
- Draw a flowchart: Start → Prepare Data → Client Send (socket) → Server Receive → Score (SymPy) → FSM Transition → Filters/Reduce → Report → Reply → Display → Tests → End.

**Page 3 — Functional Programming + FSM + SymPy**
- List each FP construct with the exact line from the code (e.g., `map(lambda r: {**r, "performance_score": compute_score(r)}, records)`; `filter(make_score_band(upper=60), evaluated)`; `reduce(lambda acc, r: acc + r["performance_score"], evaluated, 0.0) / len(evaluated)`; `sorted(evaluated, key=lambda r: -r["performance_score"])`; dict comprehension for department summary; higher-order function `make_score_band(lower, upper)` returning a predicate).
- Draw the FSM with circles (5 states) and labelled arrows (event + score band).
- SymPy: write the formula, weight values as rationals, the `solve` example (Ravi Kumar: 91.71), the `diff` example (∂Score/∂w_quality = quality).

**Page 4 — Test Cases + Output Analysis + Conclusion**
- Table of the 3 test cases with what each verifies and observed values: TC1 (`python test_cases.py 1`, output in `test_case_1_output.txt`) — mixed dataset, best = E108, avg 77.16; TC2 (`python test_cases.py 2`, output in `test_case_2_output.txt`) — FSM + edge cases: zero tasks → 29.5 PROBATION, perfect → 100.0 TOP, newcomer capped, 5×4 = 20-transition table verified; TC3 (`python test_cases.py 3`, output in `test_case_3_output.txt`) — SymPy (weights sum = 1, solve → 91.71, diff sensitivity) + live TCP round-trip with identical results.
- Output analysis: Development is the strongest department; 2 employees need PIP; 2 employees cannot reach 75 by quality alone — they need task/attendance improvement (this is the kind of insight SymPy's symbolic solve provides).
- Conclusion: the integrated design gives a transparent, networked, analytically rigorous appraisal system; all 32 automated checks passed.

## Final checklist (from the PDF) — all satisfied
- ✔ Own individual application (your dataset/logic is unique to you)
- ✔ TCP client–server socket programming
- ✔ ≥3 functional programming concepts (7 used)
- ✔ FSM with ≥3 states (5 states, 20 transitions)
- ✔ SymPy used meaningfully (formula, solve, diff, simplify)
- ✔ ≥3 test cases (4 cases, 32 checks)
- Print `server.py`, `client.py`, `test_cases.py` as the source-code section
- Print `test_case_1_output.txt`, `test_case_2_output.txt`, `test_case_3_output.txt` (the three test-case runs), plus `demo_output.txt` and `server_log.txt` as the output section
