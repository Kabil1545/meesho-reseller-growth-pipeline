"""Run every named query in queries.sql against data/meesho_reseller.db and save CSVs."""
import csv
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = HERE.parent / "data" / "meesho_reseller.db"
SQL_FILE = HERE / "queries.sql"
OUT = HERE / "output"


def load_queries(text: str) -> dict:
    blocks = re.split(r"^-- name:\s*(\S+)\s*$", text, flags=re.M)
    # blocks = [preamble, name1, body1, name2, body2, ...]
    return {blocks[i]: blocks[i + 1].strip() for i in range(1, len(blocks), 2)}


def fmt(v):
    return f"{v:.2f}" if isinstance(v, float) else v


def main():
    OUT.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    for name, sql in load_queries(SQL_FILE.read_text()).items():
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(OUT / f"{name}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            w.writerows([[fmt(v) for v in row] for row in rows])
        print(f"{name}: {len(rows)} row(s) -> part1_sql/output/{name}.csv")
    conn.close()


if __name__ == "__main__":
    main()
