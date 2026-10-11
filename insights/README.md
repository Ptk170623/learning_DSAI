# Insights

Analyses of the project's data that use what was learned in `learning/` (Parts A to D so far): data types and keys, typical values, variation, percentiles. The result is a report with a few dashboards, published as an artifact: https://claude.ai/artifact/XaoiTYCfnBZSAUuFTPd49E

- `build_report_data.py` reads the tables through `transform._ler` and writes one JSON file per table of the report (`python insights/build_report_data.py [folder]`, default `insights/out/`). Only aggregates are written: counts, shares, medians, spreads.
- `dashboard.html` and `dashboard.js` are the page of the artifact (the script follows the html in one file).

To refresh the artifact: run the script, then upload each JSON file as the data of the dashboard source with the same name, and publish the page again.
