import baseball_queries


def test_analyze_team_empty() -> None:
    assert "couldn't find" in baseball_queries.analyze_team([])


def test_analyze_team_stats() -> None:
    team = [
        {"name": "A", "age": 20, "salary": 100},
        {"name": "B", "age": 30, "salary": 900},
    ]
    out = baseball_queries.analyze_team(team)
    assert "avg age 25.0" in out
    assert "Total payroll $1,000" in out


def test_youngest_oldest() -> None:
    team = [
        {"name": "A", "age": 20, "salary": 100},
        {"name": "B", "age": 30, "salary": 900},
    ]
    assert "Youngest: A (20)" == baseball_queries.youngest_player(team)
    assert "Oldest: B (30)" == baseball_queries.oldest_player(team)


def test_highest_salary() -> None:
    team = [
        {"name": "A", "age": 20, "salary": 100},
        {"name": "B", "age": 30, "salary": 900},
    ]
    assert "Highest salary: B ($900)" == baseball_queries.highest_salary(team)
