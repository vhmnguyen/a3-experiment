# CS 4804 A3: How Does Visual Encoding Affect Value Comparison?

**Experiment link:** [ADD GITHUB PAGES LINK]

## Research question

Which visual encoding makes it easiest for people to estimate the relative sizes of two values?

This experiment compares three conditions: a vertical bar chart, a single stacked bar, and a pie chart. It is based on the Cleveland and McGill graphical perception experiment.

## Hypotheses

1. **Bar chart:** Lowest average error, since the bars share a baseline.
2. **Stacked bar:** Higher error, because users compare segment lengths at different positions.
3. **Pie chart:** Highest error, because users compare angles.

## Design and procedure

- A trial shows 5–10 randomly generated values between 1 and 100.
- Two values are marked with black dots; the remaining values are distractors.
- The participant estimates what percentage the smaller marked value is of the larger.
- For each chart type, 20 randomized trials are shown (60 trials total).
- Target ratios cover 5%, 10%, ..., 95% with one additional randomly chosen target per chart condition. Rounding may make the actual ratio differ slightly from the target; scoring always uses the actual ratio.
- Conditions and trial order are shuffled for each participant.
- No correctness feedback is shown between trials.
- Each participant downloads one CSV at the end.

### Scoring

`true_percent = 100 * min(marked1, marked2) / max(marked1, marked2)`

`absolute_error = abs(reported_percent - true_percent)`

`log2_error = 0 if absolute_error == 0 else log2(absolute_error + 1/8)`

Percentages are represented on the 0–100 scale, not the 0–1 scale.

## Experiment screenshots

- Bar chart: `img/bar.png`
- Stacked bar: `img/stacked.png`
- Pie chart: `img/pie.png`

## Participant data and analysis

Collect results from **10 participants**, with 20 trials per visualization per participant. This gives **200 trials per condition** (600 total). 

1. Have each participant download their CSV.
2. Put each file into the `results/` directory. Use unique IDs.
3. Run `python analyze_results.py` from this project's folder.
4. Insert `analysis/error_comparison.png` below.

### Results

**[Complete this section after real data have been collected.]**

`![Mean log2 error and 95% bootstrap confidence intervals](analysis/error_comparison.png)`


## Technical achievements

- Implemented all three chart types with **D3** in a single HTML file.
- Randomly generated values, chosen two unique marked elements, and randomized trial order.
- Automatically calculated true percentages, absolute errors, and Cleveland–McGill log2 errors.
- Recorded anonymous IDs, chart types, trial numbers, raw data, indices, estimates, and errors.
- Added client-side CSV downloads and a separate Python analysis script for average errors and bootstrap confidence intervals.

## Design achievements

- Kept the charts in grayscale with identical black-dot markings, so color does not affect the comparison.
- Used one question and one input field across all trials, changing only the visualization type.
- Included instructions, a progress bar, numeric input validation, and a completion/download screen.
- Avoided showing correctness feedback during the experiment, reducing the chance of learning across trials.

