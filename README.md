# System Capacity & Care Load Analytics for Unaccompanied Children

## Contents
- `app.py`: interactive Streamlit dashboard
- `uac_cleaned_analytics_dataset.csv`: cleaned source data and derived metrics
- `research_paper.pdf`: research-style report with charts, methods, findings and limitations
- `executive_summary.pdf`: short stakeholder summary
- `images/`: PNG charts for use in GitHub, presentations and reports
- `analysis_summary.json`: computed descriptive statistics

## Run locally
Use Python 3.10+: `pip install -r requirements.txt` then `streamlit run app.py`.

## Deploy
Push this folder to a GitHub repository. In Streamlit Community Cloud, create a new app, choose the repository and branch, and set the main file to `app.py`.

## Metric definitions
- Total system load = reported CBP custody + reported HHS care.
- Net HHS intake (simplified) = transfers out of CBP custody − HHS discharges.
- Rolling averages are by observation count, not guaranteed calendar days.

## Limitations
The input has irregular reporting dates; missing dates are not imputed. Combined load may not represent unique children if counts overlap. Flow and snapshot measures have different meanings. Facility capacity, staffing, acuity, and placement wait data are absent, so this is workload-pattern analysis, not proof of overcrowding or care quality. Verify the dataset against official documentation before academic or policy use.
