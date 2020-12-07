from datetime import date
from re import sub
import pandas as pd 
from pathlib import Path
import requests
import click
import re
import subprocess
import json
from pprint import pprint
import datetime

github_repo = re.compile(r"https?://github.com/([^/]+/[^/]+)/?")
DIR = Path(__file__).parent

def transform_source(code):
    if (m := github_repo.fullmatch(code)):
        repo = m.groups()[0]
        url = f"https://github.com/{repo}/raw/master/parser.py"
        return requests.get(url).text
    return code

data = (
    pd.read_csv(DIR / "responses.csv")
        .rename(columns={"Nome": "name", "Matrícula": "id", "Código": "source", "Timestamp": "timestamp"})
        .astype({"name": "string", "id": "string", "source": "string"})
)
data["timestamp"] = pd.to_datetime(data["timestamp"])


deadline = datetime.datetime(2020, 11, 3, 23, 59, 59)
deadline_soft = datetime.datetime(2020, 11, 7, 23, 59, 59)

test_file = "test_parser.py"
tests = (DIR / test_file).read_text()
results = []
for i, (_, row) in enumerate(data.iterrows()):
    print(f'{i + 1}. Grading submission by {row["name"]} ({row["id"]})...')

    path = DIR / "run" / row["id"]
    path.mkdir(parents=True, exist_ok=True)
    
    # Link test file
    if not (test_path := path / test_file).exists():
        test_path.symlink_to(f"../../{test_file}")
    
    # Save source
    src = transform_source(row["source"])
    # if click.prompt('See source? [yN]', default='N') == 'y':
    #    click.echo_via_pager(src)
    (data_path := path / "parser.py").write_text(src)

    # Save meta
    meta = json.loads(row[["id", "name", "timestamp"]].to_json())
    timestamp = row["timestamp"]
    meta["timestamp"] = timestamp.strftime("%c")
    (meta_path := path / "meta.json").write_text(json.dumps(meta))

    # Run tests and process
    subprocess.run("pytest --json-report > test.log", shell=True, cwd=path)

    # Summarize
    result = json.loads((report_path := path / ".report.json").read_text())
    try:
        meta["passed"] = n = result["summary"]["passed"]
    except KeyError:
        meta["passed"] = n = result["summary"]["total"] - result["summary"]["failed'"]

    meta["competencies"] = competencies = []
    if deadline < timestamp <= deadline_soft:
        n -= 2
    elif timestamp > deadline:
        n = 0

    if n >= 6:
        competencies.append("cfg-bnf")
    if n >= 8:
        competencies.append("cfg-ebnf")
    if n >= 10:
        competencies.append("cfg-reduce")
    meta["considered"] = n

    meta_path.write_text(json.dumps(meta))
    results.append(meta)
    print('    OK:', n, competencies)

# Save results
(DIR / "results.json").write_text(json.dumps(results))
pprint(results)

items = []
for item in results:
    comps = {k: True for k in item["competencies"]}
    items.append({"id": item["id"], **comps})

data = pd.DataFrame.from_records(items, index="id").fillna(False)
data.to_csv("results.csv")
data.to_excel("results.xlsx")
print(data)