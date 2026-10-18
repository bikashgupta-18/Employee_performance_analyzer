"""
================================================================================
 EMPLOYEE PERFORMANCE ANALYZER - TCP SERVER
 21CSC203P - Advanced Programming Practice (CO4 & CO5)
 Individual Integrated Assignment - Topic allotted to Roll Nos. 61-65

 Integrated Components:
   1. Functional Programming : lambda, map(), filter(), reduce(),
                               dictionary comprehension, higher-order functions
   2. Network Programming    : TCP Client-Server using the socket module
   3. Automata / FSM         : 5-state Employee Performance FSM
   4. Symbolic Computing     : SymPy symbolic performance model
================================================================================
"""

import json
import socket
from functools import reduce

from sympy import Rational, diff, lambdify, solve, simplify, symbols

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 65432
BUFFER_SIZE = 65536

OVERTIME_CAP = 40          # overtime hours/month counted as "full" credit

# ---------------------------------------------------------------------------
# STEP 6 : SYMBOLIC PERFORMANCE MODEL  (SymPy)
# ---------------------------------------------------------------------------
# Symbolic WEIGHTS of the performance model
w_task, w_quality, w_attendance, w_overtime = symbols(
    "w_task w_quality w_attendance w_overtime"
)

# Exact rational weight values (35% + 35% + 20% + 10% = 100%)
WEIGHT_VALUES = {
    "w_task": Rational(35, 100),
    "w_quality": Rational(35, 100),
    "w_attendance": Rational(20, 100),
    "w_overtime": Rational(10, 100),
}

# Symbolic placeholders for ONE employee's raw attributes
task_ratio, quality, attendance, overtime_norm = symbols(
    "task_ratio quality attendance overtime_norm"
)

# SYMBOLIC PERFORMANCE FORMULA:
#   Score = 100*w_task*task_ratio + w_quality*quality
#         + w_attendance*attendance + w_overtime*overtime_norm
SCORE_EXPR = simplify(
    100 * w_task * task_ratio
    + w_quality * quality
    + w_attendance * attendance
    + w_overtime * overtime_norm
)

# Fast numeric evaluator generated from the symbolic expression
score_fn = lambdify(
    (w_task, w_quality, w_attendance, w_overtime,
     task_ratio, quality, attendance, overtime_norm),
    SCORE_EXPR,
    modules="math",
)


def _extract_features(record):
    """Pure helper: raw record -> numeric features for the model."""
    assigned = max(int(record.get("tasks_assigned", 0)), 0)
    completed = max(int(record.get("tasks_completed", 0)), 0)
    ratio = (completed / assigned) if assigned > 0 else 0.0
    overtime_norm = (
        min(max(float(record.get("overtime_hours", 0)), 0.0), OVERTIME_CAP)
        / OVERTIME_CAP * 100
    )
    return (
        ratio,
        float(record.get("quality_score", 0)),
        float(record.get("attendance_pct", 0)),
        overtime_norm,
    )


def compute_score(record):
    """Evaluate the symbolic performance model for one employee."""
    ratio, q, att, ot = _extract_features(record)
    raw = score_fn(
        WEIGHT_VALUES["w_task"], WEIGHT_VALUES["w_quality"],
        WEIGHT_VALUES["w_attendance"], WEIGHT_VALUES["w_overtime"],
        ratio, q, att, ot,
    )
    return round(float(raw), 2)


def required_quality_for_target(record, target=75):
    """
    SymPy solve(): symbolically solve the score equation for 'quality'.
    Returns the quality score this employee would need to reach 'target'.
    """
    ratio, _q, att, ot = _extract_features(record)
    substituted = SCORE_EXPR.subs({
        w_task: WEIGHT_VALUES["w_task"],
        w_quality: WEIGHT_VALUES["w_quality"],
        w_attendance: WEIGHT_VALUES["w_attendance"],
        w_overtime: WEIGHT_VALUES["w_overtime"],
        task_ratio: ratio,
        attendance: att,
        overtime_norm: ot,
    })
    solution = solve(substituted - target, quality)   # symbolic solution
    return round(float(solution[0]), 2) if solution else None


def quality_sensitivity(record):
    """
    SymPy diff(): sensitivity of the score to the quality WEIGHT
    (dScore/dw_quality = quality). Employees with a higher quality score are
    affected the most when the quality weight is raised.
    """
    _ratio, q, _att, _ot = _extract_features(record)
    return round(float(diff(SCORE_EXPR, w_quality).subs(quality, q)), 2)


# ---------------------------------------------------------------------------
# STEP 5 : FINITE STATE MACHINE  (Automata)
# ---------------------------------------------------------------------------
class PerformanceFSM:
    """
    Deterministic FSM for employee performance appraisal.

        States (5)  : NEW_JOINER, PROBATION, AVERAGE, HIGH_PERFORMER, TOP_PERFORMER
        Inputs      : LOW / OK / GOOD / EXCELLENT  (score bands  <60, <75, <85, >=85)
        Transitions : complete state -> event -> next-state table (see TRANSITIONS)
    """

    STATES = ("NEW_JOINER", "PROBATION", "AVERAGE", "HIGH_PERFORMER", "TOP_PERFORMER")
    EVENTS = ("LOW", "OK", "GOOD", "EXCELLENT")

    TRANSITIONS = {
        # state            LOW            OK             GOOD              EXCELLENT
        "NEW_JOINER":     {"LOW": "PROBATION", "OK": "AVERAGE", "GOOD": "HIGH_PERFORMER", "EXCELLENT": "HIGH_PERFORMER"},
        "PROBATION":      {"LOW": "PROBATION", "OK": "AVERAGE", "GOOD": "HIGH_PERFORMER", "EXCELLENT": "HIGH_PERFORMER"},
        "AVERAGE":        {"LOW": "PROBATION", "OK": "AVERAGE", "GOOD": "HIGH_PERFORMER", "EXCELLENT": "TOP_PERFORMER"},
        "HIGH_PERFORMER": {"LOW": "PROBATION", "OK": "AVERAGE", "GOOD": "HIGH_PERFORMER", "EXCELLENT": "TOP_PERFORMER"},
        "TOP_PERFORMER":  {"LOW": "AVERAGE",   "OK": "HIGH_PERFORMER", "GOOD": "TOP_PERFORMER", "EXCELLENT": "TOP_PERFORMER"},
    }

    RECOMMENDATIONS = {
        "PROBATION": "Enroll in Performance Improvement Plan (PIP)",
        "AVERAGE": "Regular appraisal + skill-upgradation training",
        "HIGH_PERFORMER": "Eligible for annual performance bonus",
        "TOP_PERFORMER": "Promotion recommended - leadership track",
    }

    @staticmethod
    def event_for(score):
        """Map a numeric score to an FSM input event."""
        if score < 60:
            return "LOW"
        if score < 75:
            return "OK"
        if score < 85:
            return "GOOD"
        return "EXCELLENT"

    @staticmethod
    def start_state(experience_years):
        """Initial state: employees with <= 1 year experience start as NEW_JOINER."""
        return "NEW_JOINER" if experience_years <= 1 else "AVERAGE"

    @classmethod
    def run(cls, start, score):
        """Feed one input event into the FSM and read the resulting state."""
        event = cls.event_for(score)
        final = cls.TRANSITIONS[start][event]
        return {
            "start_state": start,
            "event": event,
            "final_state": final,
            "recommendation": cls.RECOMMENDATIONS[final],
        }


# ---------------------------------------------------------------------------
# STEP 4 : FUNCTIONAL PROCESSING PIPELINE
# ---------------------------------------------------------------------------
def make_score_band(lower=None, upper=None):
    """
    HIGHER-ORDER FUNCTION: returns a filter predicate that keeps records whose
    performance score lies inside the band [lower, upper).
    """
    return lambda record: (
        (lower is None or record["performance_score"] >= lower)
        and (upper is None or record["performance_score"] < upper)
    )


def analyze(records):
    """Full analysis pipeline built from functional programming constructs."""

    # (1) map() + lambda : attach the SymPy-computed score to every record
    scored = list(map(
        lambda r: {**r, "performance_score": compute_score(r)},
        records,
    ))

    # (2) map() + lambda : run every employee through the FSM
    evaluated = list(map(
        lambda r: {
            **r,
            **PerformanceFSM.run(
                PerformanceFSM.start_state(r["experience_years"]),
                r["performance_score"],
            ),
        },
        scored,
    ))

    # (3) filter() + higher-order function : weak (<60) and star (>=85) performers
    weak = list(filter(make_score_band(upper=60), evaluated))
    stars = list(filter(make_score_band(lower=85), evaluated))

    # (4) reduce() : company-wide average performance score
    company_average = round(
        reduce(lambda acc, r: acc + r["performance_score"], evaluated, 0.0)
        / len(evaluated),
        2,
    )

    # (5) reduce() : best employee of the organisation
    best = reduce(
        lambda a, b: a if a["performance_score"] >= b["performance_score"] else b,
        evaluated,
    )

    # (6) sorted() + lambda : merit ranking (highest score first)
    rankings = sorted(evaluated, key=lambda r: -r["performance_score"])

    # (7) dictionary comprehension : department-wise summary
    departments = {r["department"] for r in evaluated}
    department_summary = {
        d: {
            "headcount": len(d_list := [r for r in evaluated if r["department"] == d]),
            "average_score": round(
                sum(r["performance_score"] for r in d_list) / len(d_list), 2
            ),
            "top_performers": sum(
                1 for r in d_list if r["final_state"] == "TOP_PERFORMER"
            ),
            "on_probation": sum(
                1 for r in d_list if r["final_state"] == "PROBATION"
            ),
        }
        for d in sorted(departments)
    }

    # FSM state distribution  (dictionary comprehension)
    state_distribution = {
        state: sum(1 for r in evaluated if r["final_state"] == state)
        for state in PerformanceFSM.STATES[1:]          # skip initial NEW_JOINER
    }

    return {
        "total_employees": len(evaluated),
        "company_average_score": company_average,
        "best_employee": {
            "emp_id": best["emp_id"],
            "name": best["name"],
            "department": best["department"],
            "performance_score": best["performance_score"],
            "final_state": best["final_state"],
        },
        "rankings": [
            {
                "rank": i,
                "emp_id": r["emp_id"],
                "name": r["name"],
                "department": r["department"],
                "performance_score": r["performance_score"],
                "final_state": r["final_state"],
            }
            for i, r in enumerate(rankings, start=1)
        ],
        "weak_performers": [
            {"emp_id": r["emp_id"], "name": r["name"],
             "performance_score": r["performance_score"]}
            for r in weak
        ],
        "star_performers": [
            {"emp_id": r["emp_id"], "name": r["name"],
             "performance_score": r["performance_score"]}
            for r in stars
        ],
        "department_summary": department_summary,
        "fsm_state_distribution": state_distribution,
        "fsm_decisions": [
            {
                "emp_id": r["emp_id"],
                "name": r["name"],
                "start_state": r["start_state"],
                "event": r["event"],
                "final_state": r["final_state"],
                "recommendation": r["recommendation"],
            }
            for r in evaluated
        ],
        "sympy_analysis": sympy_analysis(evaluated),
    }


def sympy_analysis(evaluated):
    """Symbolic (SymPy) computations attached to the final report."""
    below_target = list(filter(make_score_band(upper=75), evaluated))
    weight_sum = simplify(sum(WEIGHT_VALUES.values()))
    most_sensitive = max(evaluated, key=lambda r: quality_sensitivity(r))

    return {
        "score_formula": str(SCORE_EXPR),
        "weight_sum": str(weight_sum),
        "weights_add_to_100_percent": bool(weight_sum == 1),
        "marginal_gain_per_quality_point": str(round(float(
            diff(SCORE_EXPR, quality).subs(WEIGHT_VALUES)), 2)),
        "most_sensitive_to_quality_weight": {
            "emp_id": most_sensitive["emp_id"],
            "name": most_sensitive["name"],
            "dScore/dw_quality": quality_sensitivity(most_sensitive),
        },
        "required_quality_to_reach_75": [
            {
                "emp_id": r["emp_id"],
                "name": r["name"],
                "current_score": r["performance_score"],
                "required_quality": required_quality_for_target(r, 75),
                "achievable_by_quality_alone": (
                    (required_quality_for_target(r, 75) or 999.0) <= 100
                ),
            }
            for r in below_target
        ],
    }


# ---------------------------------------------------------------------------
# STEP 3 : TCP SERVER
# ---------------------------------------------------------------------------
def handle_client(conn, _addr):
    """Receive one JSON request line, process it, send one JSON response line."""
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk

    request = json.loads(data.decode("utf-8"))
    print(f"[SERVER] Received action='{request.get('action')}' with "
          f"{len(request.get('records', []))} employee record(s)")

    if request.get("action") == "ping":
        response = {"status": "ok",
                    "message": "Employee Performance Analyzer server is alive"}
    else:
        analysis = analyze(request["records"])
        response = {"status": "ok", "analysis": analysis}
        print(f"[SERVER] Analysis complete: company average = "
              f"{analysis['company_average_score']}")

    conn.sendall((json.dumps(response, indent=2) + "\n").encode("utf-8"))


def start_server(host=HOST, port=PORT):
    """Create, bind and listen. Returns the server socket (useful for tests)."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Employee Performance Analyzer listening on {host}:{port} ...")
    return server


def serve_forever(host=HOST, port=PORT):
    """Accept TCP connections until interrupted (Ctrl+C)."""
    server = start_server(host, port)
    try:
        while True:
            conn, addr = server.accept()
            print(f"[SERVER] Connection accepted from {addr}")
            handle_client(conn, addr)
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down. Goodbye!")
    finally:
        server.close()


if __name__ == "__main__":
    print("=" * 70)
    print(" EMPLOYEE PERFORMANCE ANALYZER - SERVER")
    print(" Functional Programming + TCP Sockets + FSM + SymPy")
    print("=" * 70)
    serve_forever()
