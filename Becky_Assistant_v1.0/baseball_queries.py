"""Domain logic for baseball questions ("queries") about a team roster.

Today this is a small starter set of "GM-style" queries over a roster export.
The key design goal is: *never invent data*. If a field is missing, we say so.

Data shape expected for each player:
- name: str
- age: int
- salary: int  (annual salary; may be 0 if unknown)
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def analyze_team(team_data: Iterable[Mapping[str, Any]]) -> str:
    """Roster summary: average age and total payroll."""
    players = _as_players(team_data)
    if not players:
        return "Sorry, I couldn't find your team data."

    ages = [p["age"] for p in players if isinstance(p.get("age"), int) and p["age"] > 0]
    salaries = [p["salary"] for p in players if isinstance(p.get("salary"), int) and p["salary"] >= 0]

    if not ages:
        return "Sorry, no valid ages were found in the export."
    if not salaries:
        return "Sorry, no valid salaries were found in the export."

    avg_age = sum(ages) / len(ages)
    payroll = sum(salaries)

    return f"Roster: avg age {avg_age:.1f}. Total payroll ${payroll:,.0f}."


def youngest_player(team_data: Iterable[Mapping[str, Any]]) -> str:
    players = _as_players(team_data)
    players = [p for p in players if p["age"] > 0]
    if not players:
        return "I can't determine the youngest player (no valid ages)."
    p = min(players, key=lambda x: x["age"])
    return f"Youngest: {p['name']} ({p['age']})"


def oldest_player(team_data: Iterable[Mapping[str, Any]]) -> str:
    players = _as_players(team_data)
    players = [p for p in players if p["age"] > 0]
    if not players:
        return "I can't determine the oldest player (no valid ages)."
    p = max(players, key=lambda x: x["age"])
    return f"Oldest: {p['name']} ({p['age']})"


def highest_salary(team_data: Iterable[Mapping[str, Any]]) -> str:
    players = _as_players(team_data)
    players = [p for p in players if p["salary"] > 0]
    if not players:
        return "I can't determine the highest salary (no valid salaries)."
    p = max(players, key=lambda x: x["salary"])
    return f"Highest salary: {p['name']} (${p['salary']:,.0f})"


def top_salaries(team_data: Iterable[Mapping[str, Any]], n: int = 5) -> str:
    players = _as_players(team_data)
    players = [p for p in players if p["salary"] > 0]
    if not players:
        return "I can't list top salaries (no valid salaries)."
    players.sort(key=lambda x: x["salary"], reverse=True)
    lines = [f"Top {min(n, len(players))} salaries:"]
    for p in players[:n]:
        lines.append(f"- {p['name']}: ${p['salary']:,.0f}")
    return "\n".join(lines)


def help_text() -> str:
    return (
        "Commands:\n"
        "  setroot <folder>   - load a folder of OOTP CSV exports\n"
        "  autodetect         - try to find your OOTP 26 saved games + export folders\n"
        "  tables             - list discovered CSV tables under export root\n"
        "  describe <table>   - show columns + a few sample rows\n"
        "  search <t> <c> <s> - find rows where column contains substring\n"
        "  analyze            - roster summary (avg age, payroll)\n"
        "  youngest           - youngest player\n"
        "  oldest             - oldest player\n"
        "  highest salary     - highest-paid player\n"
        "  top salaries [n]   - list top salaries (default 5)\n"
        "  reload             - re-read exports from disk\n"
        "  where              - show current export path\n"
        "  help               - show this message\n"
        "  quit               - exit\n"
    )


def _as_players(team_data: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    players: list[dict[str, Any]] = []
    for row in team_data:
        name = str(row.get("name") or row.get("Name") or "").strip() or "(unknown)"
        age = row.get("age", row.get("Age", 0))
        salary = row.get("salary", row.get("Salary", 0))
        try:
            age_i = int(age) if age is not None else 0
        except Exception:
            age_i = 0
        try:
            sal_i = int(salary) if salary is not None else 0
        except Exception:
            sal_i = 0
        players.append({"name": name, "age": age_i, "salary": sal_i})
    return players
