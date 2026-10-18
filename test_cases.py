"""
================================================================================
 EMPLOYEE PERFORMANCE ANALYZER - TEST CASES
 21CSC203P - Advanced Programming Practice (CO4 & CO5)
 Individual Integrated Assignment - Topic allotted to Roll Nos. 61-65

 Three independent test cases - each can be run with its own command:

     python test_cases.py 1    Test Case 1 : Full mixed dataset - functional
                                             analysis pipeline (12 employees)
     python test_cases.py 2    Test Case 2 : FSM verification with edge-case
                                             employees (zero work, perfect work)
     python test_cases.py 3    Test Case 3 : SymPy symbolic model checks +
                                             TCP client-server round trip
     python test_cases.py      Run ALL THREE test cases together
================================================================================
"""

import json
import sys
import threading

import client
import server
from server import (
    PerformanceFSM,
    analyze,
    compute_score,
    quality_sensitivity,
    required_quality_for_target,
)


# ---------------------------------------------------------------------------
# Tiny PASS / FAIL helper (counts are kept per test case and overall)
# ---------------------------------------------------------------------------
class Tally:
    """Counts passed / failed checks and the running check number."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.number = 0


CURRENT = Tally()   # tally of the test case running right now
GRAND = Tally()     # tally across every test case in this run


def check(description, condition, detail=""):
    """Record and print PASS / FAIL for one expectation."""
    CURRENT.number += 1
    if condition:
        CURRENT.passed += 1
        GRAND.passed += 1
        print(f"  [PASS] {CURRENT.number}. {description}")
    else:
        CURRENT.failed += 1
        GRAND.failed += 1
        print(f"  [FAIL] {CURRENT.number}. {description} {detail}")


# ---------------------------------------------------------------------------
# TEST CASE 1 : Full mixed dataset (12 employees, 3 departments)
# ---------------------------------------------------------------------------
def test_case_1():
    print("\n  Dataset : 12 employees across Development, QA and Design")
    print("  Checks  : functional pipeline (map/filter/reduce/comprehensions)\n")

    analysis = analyze(client.EMPLOYEE_DATASET)

    print(f"  Company average score : {analysis['company_average_score']}")
    print(f"  Best employee         : {analysis['best_employee']['name']} "
          f"({analysis['best_employee']['performance_score']})")
    print(f"  FSM state distribution: {analysis['fsm_state_distribution']}")
    print("  Department summary:")
    for dept, info in analysis["department_summary"].items():
        print(f"    {dept:<14} headcount={info['headcount']:<3} "
              f"average={info['average_score']:<7} "
              f"top={info['top_performers']}  probation={info['on_probation']}")

    check("All 12 employees analysed",
          analysis["total_employees"] == 12)
    check("Every employee received a performance score between 0 and 100",
          all(0 <= r["performance_score"] <= 100 for r in analysis["rankings"]))
    check("Ranking is sorted highest-score-first (reduce/sorted + lambda)",
          all(analysis["rankings"][i]["performance_score"]
              >= analysis["rankings"][i + 1]["performance_score"]
              for i in range(len(analysis["rankings"]) - 1)))
    check("Kavya Menon (E108) is the best employee (score 89.93)",
          analysis["best_employee"]["emp_id"] == "E108",
          f"(got {analysis['best_employee']})")
    check("filter() found both weak (<60) and star (>=85) performers",
          len(analysis["weak_performers"]) >= 1
          and len(analysis["star_performers"]) >= 1)
    check("Dictionary comprehension summarised all 3 departments",
          sorted(analysis["department_summary"].keys())
          == ["Design", "Development", "QA"])
    check("FSM produced only valid states for every employee",
          all(r["final_state"] in PerformanceFSM.STATES
              for r in analysis["rankings"]))
    check("Company average lies inside the observed score range",
          min(r["performance_score"] for r in analysis["rankings"])
          <= analysis["company_average_score"]
          <= max(r["performance_score"] for r in analysis["rankings"]))


# ---------------------------------------------------------------------------
# TEST CASE 2 : FSM verification with edge-case employees
# ---------------------------------------------------------------------------
def test_case_2():
    print("\n  [2a] Edge-case employees fed through the FSM")

    edge_records = [
        # Zero tasks completed, poor attendance -> must be PROBATION
        {"emp_id": "X001", "name": "Zero Work",     "department": "Dev", "experience_years": 3,
         "tasks_assigned": 30, "tasks_completed": 0,  "quality_score": 50,  "attendance_pct": 60,  "overtime_hours": 0},
        # tasks_assigned = 0 -> division guard must give ratio 0, no crash
        {"emp_id": "X002", "name": "No Task Given", "department": "Dev", "experience_years": 2,
         "tasks_assigned": 0,  "tasks_completed": 0,  "quality_score": 70,  "attendance_pct": 90,  "overtime_hours": 4},
        # Perfect employee -> must reach TOP_PERFORMER
        {"emp_id": "X003", "name": "Perfect Work",  "department": "QA",  "experience_years": 4,
         "tasks_assigned": 40, "tasks_completed": 40, "quality_score": 100, "attendance_pct": 100, "overtime_hours": 40},
        # New joiner with excellent score -> FSM must cap at HIGH_PERFORMER
        {"emp_id": "X004", "name": "Star Newcomer", "department": "QA",  "experience_years": 1,
         "tasks_assigned": 20, "tasks_completed": 20, "quality_score": 100, "attendance_pct": 100, "overtime_hours": 40},
    ]

    analysis = analyze(edge_records)
    states = {r["emp_id"]: r["final_state"] for r in analysis["rankings"]}
    scores = {r["emp_id"]: r["performance_score"] for r in analysis["rankings"]}

    print(f"  Computed scores : {json.dumps(scores)}")
    print(f"  FSM final states: {json.dumps(states)}\n")

    check("Program did not crash on tasks_assigned = 0",
          len(analysis["rankings"]) == 4)
    check("'Zero Work' scored below 60 and FSM put them on PROBATION",
          scores["X001"] < 60 and states["X001"] == "PROBATION",
          f"(score {scores['X001']}, state {states['X001']})")
    check("'No Task Given' got a valid score despite 0 assigned tasks",
          0 <= scores["X002"] < 60)
    check("'Perfect Work' scored exactly 100.0 -> TOP_PERFORMER",
          scores["X003"] == 100.0 and states["X003"] == "TOP_PERFORMER",
          f"(score {scores['X003']}, state {states['X003']})")
    check("'Star Newcomer' (1 yr experience) capped at HIGH_PERFORMER",
          states["X004"] == "HIGH_PERFORMER",
          f"(state {states['X004']})")
    check("Every employee received an FSM recommendation",
          all(r["recommendation"] for r in analysis["fsm_decisions"]))

    print("\n  [2b] FSM structure - states, inputs and transitions")

    print(f"\n  States ({len(PerformanceFSM.STATES)}): {PerformanceFSM.STATES}")
    print(f"  Input events ({len(PerformanceFSM.EVENTS)}): {PerformanceFSM.EVENTS}")
    print("\n  Transition table (state x event -> next state):\n")
    header = f"    {'STATE':<18}" + "".join(f"{e:<16}" for e in PerformanceFSM.EVENTS)
    print("    " + "-" * (len(header) - 4))
    print(header)
    for state in PerformanceFSM.STATES:
        row = f"    {state:<18}"
        for event in PerformanceFSM.EVENTS:
            row += f"{PerformanceFSM.TRANSITIONS[state][event]:<16}"
        print(row)
    print()

    check("FSM has at least 3 states (it has 5)",
          len(PerformanceFSM.STATES) >= 3)
    check("Transition table is complete (5 states x 4 events = 20 transitions)",
          all(event in PerformanceFSM.TRANSITIONS[state]
              for state in PerformanceFSM.STATES
              for event in PerformanceFSM.EVENTS))
    check("Score band 59.99 maps to LOW input event",
          PerformanceFSM.event_for(59.99) == "LOW")
    check("Boundary score 75.00 maps to GOOD input event",
          PerformanceFSM.event_for(75.0) == "GOOD")
    check("NEW_JOINER + EXCELLENT -> HIGH_PERFORMER (new joiners capped)",
          PerformanceFSM.TRANSITIONS["NEW_JOINER"]["EXCELLENT"] == "HIGH_PERFORMER")
    check("AVERAGE + EXCELLENT -> TOP_PERFORMER",
          PerformanceFSM.TRANSITIONS["AVERAGE"]["EXCELLENT"] == "TOP_PERFORMER")
    check("TOP_PERFORMER + LOW -> AVERAGE (grace demotion)",
          PerformanceFSM.TRANSITIONS["TOP_PERFORMER"]["LOW"] == "AVERAGE")
    check("Experience <= 1 year starts in NEW_JOINER state",
          PerformanceFSM.start_state(1) == "NEW_JOINER"
          and PerformanceFSM.start_state(2) == "AVERAGE")
    check("Every reachable state has a recommendation defined",
          all(s in PerformanceFSM.RECOMMENDATIONS
              for s in PerformanceFSM.STATES[1:]))


# ---------------------------------------------------------------------------
# TEST CASE 3 : SymPy symbolic model + TCP client-server round trip
# ---------------------------------------------------------------------------
def test_case_3():
    print("\n  [3a] SymPy symbolic checks")

    report = analyze(client.EMPLOYEE_DATASET)
    sym = report["sympy_analysis"]
    print(f"    Score formula      : {sym['score_formula']}")
    print(f"    Sum of weights     : {sym['weight_sum']}")
    print(f"    dScore/dquality    : {sym['marginal_gain_per_quality_point']}")

    check("Symbolic weights add up to exactly 1 (100%)",
          sym["weights_add_to_100_percent"] is True)
    check("Score derivative w.r.t. quality is the quality weight (0.35)",
          sym["marginal_gain_per_quality_point"] == "0.35")

    # The solve() result must satisfy the equation when substituted back
    ravi = next(r for r in client.EMPLOYEE_DATASET if r["emp_id"] == "E111")
    needed = required_quality_for_target(ravi, 75)
    verified = {**ravi, "quality_score": needed}
    check(f"solve(): E111 needs quality {needed} to reach 75 (substitution check)",
          abs(compute_score(verified) - 75) < 0.05,
          f"(score became {compute_score(verified)})")

    infeasible = [r for r in sym["required_quality_to_reach_75"]
                  if not r["achievable_by_quality_alone"]]
    print(f"    Employees who cannot reach 75 by quality alone: "
          f"{[r['name'] for r in infeasible]}")
    check("At least one employee flagged 'quality improvement alone insufficient'",
          len(infeasible) >= 1)
    check("diff() sensitivity equals the employee's quality score",
          quality_sensitivity(ravi) == float(ravi["quality_score"]))

    print("\n  [3b] TCP client-server round trip (real sockets on 127.0.0.1)")

    test_port = 65490
    srv = server.start_server("127.0.0.1", test_port)
    thread = threading.Thread(
        target=lambda: server.handle_client(*srv.accept()), daemon=True
    )
    thread.start()

    response = client.send_dataset(client.EMPLOYEE_DATASET, "127.0.0.1", test_port)
    thread.join(timeout=5)
    srv.close()

    direct = analyze(client.EMPLOYEE_DATASET)
    check("Server answered with status = ok",
          response.get("status") == "ok")
    check("Server returned a full analysis (12 rankings)",
          len(response["analysis"]["rankings"]) == 12)
    check("Network result is identical to direct computation",
          response["analysis"]["company_average_score"]
          == direct["company_average_score"])
    check("FSM decisions returned for every employee over the socket",
          len(response["analysis"]["fsm_decisions"]) == 12)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
TEST_CASES = {
    1: ("Full mixed dataset - functional analysis pipeline", test_case_1),
    2: ("FSM verification with edge-case employees", test_case_2),
    3: ("SymPy symbolic model + TCP client-server round trip", test_case_3),
}


def run_case(number):
    """Run one test case and print its banner and result."""
    global CURRENT
    CURRENT = Tally()
    title, fn = TEST_CASES[number]
    print("\n" + "=" * 74)
    print(f" TEST CASE {number} : {title}")
    print("=" * 74)
    fn()
    print(f"\n  TEST CASE {number} RESULT: {CURRENT.passed} passed, "
          f"{CURRENT.failed} failed")


def main():
    args = sys.argv[1:]
    if args:
        try:
            selected = [int(a) for a in args]
            if not all(n in TEST_CASES for n in selected):
                raise ValueError
        except ValueError:
            print("Usage: python test_cases.py [1|2|3] ...   "
                  "(no argument runs all three test cases)")
            sys.exit(2)
    else:
        selected = [1, 2, 3]

    print("=" * 74)
    print(" EMPLOYEE PERFORMANCE ANALYZER - AUTOMATED TEST RUN")
    print(" 21CSC203P | Roll 61-65 | CO4 & CO5 | K4 - Analyze")
    print(f" Running test case(s): {selected}")
    print("=" * 74)

    for number in selected:
        run_case(number)

    print("\n" + "=" * 74)
    print(f" TOTAL: {GRAND.passed + GRAND.failed} checks | "
          f"PASSED: {GRAND.passed} | FAILED: {GRAND.failed}")
    print(" RESULT:", "ALL TEST CASES PASSED" if GRAND.failed == 0
          else "SOME TESTS FAILED")
    print("=" * 74)

    sys.exit(1 if GRAND.failed else 0)


if __name__ == "__main__":
    main()
