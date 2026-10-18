"""
================================================================================
 EMPLOYEE PERFORMANCE ANALYZER - TCP CLIENT
 21CSC203P - Advanced Programming Practice (CO4 & CO5)
 Individual Integrated Assignment - Topic allotted to Roll Nos. 61-65

 The client prepares a small employee dataset (Step 1) and sends it to the
 server over TCP (Step 2). The server analyses it and returns the report,
 which this client prints (Step 7).
================================================================================
"""

import json
import socket

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432
BUFFER_SIZE = 65536

# ---------------------------------------------------------------------------
# STEP 1 : DATASET  (12 employees, 3 departments)
# ---------------------------------------------------------------------------
EMPLOYEE_DATASET = [
    {"emp_id": "E101", "name": "Aarav Sharma",   "department": "Development", "experience_years": 2, "tasks_assigned": 40, "tasks_completed": 38, "quality_score": 88, "attendance_pct": 96, "overtime_hours": 12},
    {"emp_id": "E102", "name": "Priya Nair",     "department": "QA",          "experience_years": 4, "tasks_assigned": 35, "tasks_completed": 30, "quality_score": 82, "attendance_pct": 92, "overtime_hours": 8},
    {"emp_id": "E103", "name": "Rahul Verma",    "department": "Design",      "experience_years": 6, "tasks_assigned": 30, "tasks_completed": 22, "quality_score": 75, "attendance_pct": 85, "overtime_hours": 5},
    {"emp_id": "E104", "name": "Sneha Iyer",     "department": "Development", "experience_years": 1, "tasks_assigned": 25, "tasks_completed": 24, "quality_score": 90, "attendance_pct": 98, "overtime_hours": 20},
    {"emp_id": "E105", "name": "Karthik Rao",    "department": "QA",          "experience_years": 3, "tasks_assigned": 30, "tasks_completed": 18, "quality_score": 65, "attendance_pct": 78, "overtime_hours": 2},
    {"emp_id": "E106", "name": "Ananya Das",     "department": "Design",      "experience_years": 5, "tasks_assigned": 40, "tasks_completed": 36, "quality_score": 86, "attendance_pct": 94, "overtime_hours": 15},
    {"emp_id": "E107", "name": "Imran Khan",     "department": "Development", "experience_years": 2, "tasks_assigned": 35, "tasks_completed": 28, "quality_score": 78, "attendance_pct": 88, "overtime_hours": 10},
    {"emp_id": "E108", "name": "Kavya Menon",    "department": "QA",          "experience_years": 7, "tasks_assigned": 30, "tasks_completed": 29, "quality_score": 92, "attendance_pct": 97, "overtime_hours": 18},
    {"emp_id": "E109", "name": "Sanjay Gupta",   "department": "Design",      "experience_years": 1, "tasks_assigned": 20, "tasks_completed": 12, "quality_score": 60, "attendance_pct": 70, "overtime_hours": 1},
    {"emp_id": "E110", "name": "Meera Joshi",    "department": "Development", "experience_years": 4, "tasks_assigned": 35, "tasks_completed": 32, "quality_score": 84, "attendance_pct": 90, "overtime_hours": 14},
    {"emp_id": "E111", "name": "Ravi Kumar",     "department": "QA",          "experience_years": 3, "tasks_assigned": 28, "tasks_completed": 20, "quality_score": 72, "attendance_pct": 82, "overtime_hours": 6},
    {"emp_id": "E112", "name": "Divya Reddy",    "department": "Design",      "experience_years": 2, "tasks_assigned": 32, "tasks_completed": 29, "quality_score": 85, "attendance_pct": 93, "overtime_hours": 16},
]


# ---------------------------------------------------------------------------
# STEP 2 : TCP CLIENT
# ---------------------------------------------------------------------------
def send_dataset(records, host=SERVER_HOST, port=SERVER_PORT):
    """
    Send employee records to the server as one JSON line,
    receive the analysis report as one JSON line.
    """
    payload = json.dumps({"action": "analyze", "records": records})
    with socket.create_connection((host, port), timeout=10) as sock:
        print(f"[CLIENT] Connected to server {host}:{port}")
        sock.sendall((payload + "\n").encode("utf-8"))
        print(f"[CLIENT] Sent {len(records)} employee record(s), waiting for reply ...")

        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                break
            data += chunk

    print("[CLIENT] Analysis report received from server\n")
    return json.loads(data.decode("utf-8"))


# ---------------------------------------------------------------------------
# STEP 7 : DISPLAY THE FINAL ANALYSIS
# ---------------------------------------------------------------------------
def print_report(report):
    analysis = report["analysis"]

    print("=" * 74)
    print(" EMPLOYEE PERFORMANCE ANALYSIS REPORT".center(74))
    print("=" * 74)

    print(f"\nTotal employees analysed : {analysis['total_employees']}")
    print(f"Company average score    : {analysis['company_average_score']}")

    best = analysis["best_employee"]
    print(f"Best employee            : {best['name']} ({best['emp_id']}, "
          f"{best['department']}) - score {best['performance_score']}")

    print("\n--- MERIT RANKING " + "-" * 56)
    print(f"{'Rank':<6}{'ID':<7}{'Name':<16}{'Department':<14}{'Score':<9}{'FSM State'}")
    print("-" * 74)
    for row in analysis["rankings"]:
        print(f"{row['rank']:<6}{row['emp_id']:<7}{row['name']:<16}"
              f"{row['department']:<14}{row['performance_score']:<9}{row['final_state']}")

    print("\n--- FSM DECISIONS (start state + input event -> final state) " + "-" * 14)
    print(f"{'ID':<7}{'Name':<16}{'Start State':<15}{'Event':<11}{'Final State':<17}Recommendation")
    print("-" * 74)
    for d in analysis["fsm_decisions"]:
        print(f"{d['emp_id']:<7}{d['name']:<16}{d['start_state']:<15}"
              f"{d['event']:<11}{d['final_state']:<17}{d['recommendation']}")

    print("\n--- DEPARTMENT SUMMARY " + "-" * 51)
    for dept, info in analysis["department_summary"].items():
        print(f"{dept:<14} headcount={info['headcount']:<3} "
              f"average={info['average_score']:<7} "
              f"top={info['top_performers']}  probation={info['on_probation']}")

    print("\n--- FSM STATE DISTRIBUTION " + "-" * 46)
    for state, count in analysis["fsm_state_distribution"].items():
        print(f"  {state:<17}: {count}")

    print("\n--- SymPy SYMBOLIC ANALYSIS " + "-" * 44)
    sym = analysis["sympy_analysis"]
    print(f"  Symbolic score formula : {sym['score_formula']}")
    print(f"  Sum of weights         : {sym['weight_sum']}  "
          f"(= 100% ? {sym['weights_add_to_100_percent']})")
    print(f"  dScore/dquality        : {sym['marginal_gain_per_quality_point']} "
          f"(each quality point adds 0.35 to the score)")
    ms = sym["most_sensitive_to_quality_weight"]
    print(f"  Most sensitive employee: {ms['name']} ({ms['emp_id']}) - "
          f"dScore/dw_quality = {ms['dScore/dw_quality']}")
    print("  Required quality score to reach target 75:")
    for r in sym["required_quality_to_reach_75"]:
        verdict = "YES" if r["achievable_by_quality_alone"] else "NO - needs task/attendance improvement too"
        print(f"    {r['name']:<15} current={r['current_score']:<7} "
              f"required quality={r['required_quality']:<7} achievable={verdict}")

    weak = analysis["weak_performers"]
    stars = analysis["star_performers"]
    print(f"\n  Employees below score 60 (PIP required) : "
          f"{', '.join(r['name'] for r in weak) or 'None'}")
    print(f"  Top performers (score >= 85)            : "
          f"{', '.join(r['name'] for r in stars) or 'None'}")

    print("\n" + "=" * 74)
    print(" END OF REPORT".center(74))
    print("=" * 74)


def main():
    print("=" * 74)
    print(" EMPLOYEE PERFORMANCE ANALYZER - TCP CLIENT")
    print(" Functional Programming + TCP Sockets + FSM + SymPy")
    print("=" * 74)
    report = send_dataset(EMPLOYEE_DATASET)
    if report.get("status") == "ok":
        print_report(report)
    else:
        print("[CLIENT] Server returned an error:", report)


if __name__ == "__main__":
    main()
