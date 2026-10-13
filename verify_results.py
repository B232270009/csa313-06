"""Verify generated design artifacts, not a transfer implementation."""
import csv
import itertools
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
BROWSER = [("Allow", "Restrict", "Block")] * 2 + [("Yes", "No")] * 4
TRANSFER = [("Valid", "Frozen", "Missing"), ("Valid", "Missing", "SameAsFrom"),
            ("Normal", "Zero", "Negative", "OverBalance", "OverLimit"),
            ("Same", "Different"), ("Fresh", "NearLimit")]


def error_choices(row):
    f, t, a, _, _ = row
    return int(f != "Valid") + int(t != "Valid") + int(a != "Normal")


def allowed(row, mode):
    f, t, a, c, r = row
    if mode == "nc":
        return True
    if f == "Missing" and (t, a, c, r) != ("Valid", "Normal", "Same", "Fresh"):
        return False
    if mode == "neg":
        return error_choices(row) <= 1
    if f == "Frozen" and (a != "Normal" or t not in ("Valid", "Missing")):
        return False
    if f == "Frozen" and t == "Missing" and (c, r) != ("Same", "Fresh"):
        return False
    if t != "Valid" and (a != "Normal" or f == "Missing"):
        return False
    if t == "SameAsFrom" and f != "Valid":
        return False
    return a == "Normal" or (f, t) == ("Valid", "Valid")


def interactions(rows, order):
    return {(indices, tuple(row[i] for i in indices))
            for row in rows for indices in itertools.combinations(range(len(row)), order)}


jobs = [("browser.model", "browser-2way.txt", 2, None),
        ("browser.model", "browser-3way.txt", 3, None),
        ("transfer-nc.model", "transfer-nc.txt", 2, "nc"),
        ("transfer.model", "transfer.txt", 2, "constrained"),
        ("transfer-neg.model", "transfer-neg.txt", 2, "neg")]
summary = []
for model, output, order, mode in jobs:
    target = ROOT / "results" / output
    with target.open() as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        raw = list(reader)
    rows = [tuple(value.removeprefix("~") for value in row) for row in raw]
    universe = list(itertools.product(*(BROWSER if mode is None else TRANSFER)))
    valid = [row for row in universe if mode is None or allowed(row, mode)]
    assert len(set(rows)) == len(rows), output + ": duplicate rows"
    assert all(row in valid for row in rows), output + ": invalid row"
    required = interactions(valid, order)
    covered = interactions(rows, order)
    # Two simultaneous negative choices cannot form a feasible interaction.
    assert required <= covered, f"{output}: {len(required - covered)} uncovered interactions"
    regenerated = subprocess.check_output(["pict", model, f"/o:{order}"], cwd=ROOT)
    assert regenerated == target.read_bytes(), output + ": regeneration changed"
    if mode != "neg":
        exhaustive = subprocess.check_output(["pict", model, "/o:max"], cwd=ROOT).decode()
        exhaustive_rows = {tuple(line.split("\t")) for line in exhaustive.splitlines()[1:]}
        assert exhaustive_rows == set(valid), output + ": exhaustive model disagrees with frame enumeration"
    if mode == "neg":
        assert all(sum(value.startswith("~") for value in row) <= 1 for row in raw)
    line = f"{output}: rows={len(rows)}, admissible_frames={len(valid)}, {order}-way={len(required)}/{len(required)}, deterministic=PASS"
    if mode is not None:
        counts = [error_choices(row) for row in rows]
        line += f", happy={counts.count(0)}, error_choices_0_1_2_3={[counts.count(i) for i in range(4)]}"
    summary.append(line)
assert len([r for r in itertools.product(*TRANSFER) if allowed(r, "constrained")]) == 34
text = "\n".join(summary) + "\nAll verification checks passed. HTTP calls were not executed.\n"
(ROOT / "results" / "verification.txt").write_text(text)
print(text, end="")
