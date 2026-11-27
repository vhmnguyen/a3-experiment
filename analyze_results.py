"""Summarize the experiment CSVs and make the required results figure.

Put all participant CSV files in the 'results' folder and run:
    python analyze_results.py

Requires matplotlib (install with: pip install matplotlib).
"""

import csv
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

RESULTS = Path("results")
OUTPUT = Path("analysis")
CONDITIONS = ["Bar chart", "Stacked bar", "Pie chart"]
BOOTSTRAP_SAMPLES = 5000


def percentile(numbers, fraction):
    """Simple percentile using linear interpolation."""
    values = sorted(numbers)
    position = fraction * (len(values) - 1)
    low = int(position)
    high = min(low + 1, len(values) - 1)
    weight = position - low
    return values[low] * (1 - weight) + values[high] * weight


def load_results():
    files = sorted(RESULTS.glob("*.csv"))
    if not files:
        raise SystemExit("No CSV files found in results/. Add participant files first.")

    records = []
    seen = set()
    for file in files:
        with file.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                try:
                    participant = row["participant_id"].strip()
                    trial = int(row["trial"])
                    condition = row["chart_type"].strip()
                    error = float(row["log2_error"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid row in {file}: {row}") from exc
                if condition not in CONDITIONS:
                    raise ValueError(f"Unexpected chart type '{condition}' in {file}")
                if not participant:
                    raise ValueError(f"Missing participant ID in {file}")
                key = (participant, trial)
                if key in seen:
                    raise ValueError(f"Duplicate participant/trial {key}; check CSV files")
                seen.add(key)
                records.append((participant, condition, error))
    return records


def bootstrap_ci(participant_errors, seed=42):
    """Resample participants with replacement to respect repeated trials."""
    rng = random.Random(seed)
    ids = list(participant_errors)
    simulated_means = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sampled_ids = [rng.choice(ids) for _ in ids]
        errors = [error for pid in sampled_ids for error in participant_errors[pid]]
        simulated_means.append(mean(errors))
    return percentile(simulated_means, 0.025), percentile(simulated_means, 0.975)


def main():
    rows = load_results()
    by_condition = defaultdict(lambda: defaultdict(list))
    for participant, condition, error in rows:
        by_condition[condition][participant].append(error)

    summary = []
    for condition in CONDITIONS:
        participant_errors = by_condition[condition]
        if not participant_errors:
            raise ValueError(f"Missing results for {condition}")
        errors = [e for participant in participant_errors.values() for e in participant]
        lower, upper = bootstrap_ci(participant_errors)
        summary.append({
            "chart_type": condition,
            "participants": len(participant_errors),
            "trials": len(errors),
            "mean_log2_error": mean(errors),
            "lower_95_ci": lower,
            "upper_95_ci": upper
        })

    summary.sort(key=lambda r: r["mean_log2_error"])
    OUTPUT.mkdir(exist_ok=True)
    with (OUTPUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    names = [r["chart_type"] for r in summary]
    means = [r["mean_log2_error"] for r in summary]
    left = [r["mean_log2_error"] - r["lower_95_ci"] for r in summary]
    right = [r["upper_95_ci"] - r["mean_log2_error"] for r in summary]

    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.errorbar(means, names, xerr=[left, right], fmt="o", capsize=5)
    ax.invert_yaxis()
    ax.set_xlabel("Average log2 error (lower is better)")
    ax.set_title("Accuracy by chart type (95% bootstrap confidence intervals)")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT / "error_comparison.png", dpi=180)
    plt.close(fig)

    print("Results ordered from lowest to highest error:\n")
    for r in summary:
        print(f"{r['chart_type']:<16} n={r['trials']:>3} "
              f"participants={r['participants']:>2} "
              f"mean={r['mean_log2_error']:.3f} "
              f"95% CI=[{r['lower_95_ci']:.3f}, {r['upper_95_ci']:.3f}]")
    print("\nSaved analysis/summary.csv and analysis/error_comparison.png")
    if len({participant for participant, _, _ in rows}) < 10:
        print("WARNING: Fewer than 10 unique participants. The study may be incomplete.")
    for r in summary:
        if r["trials"] < 200:
            print(f"WARNING: {r['chart_type']} has fewer than 200 trials.")


if __name__ == "__main__":
    main()
