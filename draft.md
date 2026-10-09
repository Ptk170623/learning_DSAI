#
Add a new page with a new analysis: you need to analyze the [map of concepts of the part] in the data in the new page with the better visuals, segmenters... You need to give insights with the analysis in the page, using graphics, images... when necessary, and so return - after to analyze it with the concepts - a detailed relatory with all the information, insights by the analysis.

Structured data
Variable (column)
Observation (row)
Data type
Numeric
Continuous
Discrete
Categorical
Nominal
Binary
Ordinal
Level
Stored type vs. statistical type
Identifier

#
Add a new page to this project: "Data types profile". It analyzes the real data of this project using these concepts: Structured data; Variable (column); Observation (row); Data type; Numeric (continuous, discrete); Categorical (nominal, binary, ordinal); Level; Stored type vs. statistical type; Identifier.

Rules:
- New page only. Do not change existing pages, data or logic. Use the same stack and style as the project.
- Generic: loop over every table or dataframe the project already loads. Do not hardcode column names.
- No personal data on the page or in your answer: only column names, counts, percentages and aggregates. Never show raw rows or values of identifier or personal columns (levels of non-personal categorical columns are fine).

What the page shows (name the concept in each section title):
1. Overview (structured data, variable, observation): per table, the number of rows (observations) and columns (variables), as summary cards.
2. Column inventory (data type, stored vs. statistical type): one row per column with the stored type (dtype) and the statistical type you decide: continuous, discrete, nominal, binary, ordinal, identifier, or other (date/text). Add a "why" column with the rule you used, in a few words. Mark the columns where the stored type misleads: numbers stored as text, codes or IDs stored as numbers, flags stored as integers, dates stored as text.
3. Segmenters: filters by table, stored type, statistical type, and "only mismatches".
4. Charts: columns by statistical type (bar); stored type x statistical type (heatmap or matrix); for the selected column: a histogram if numeric, the levels with counts if categorical (in their natural order if ordinal), and for identifiers the unique % and duplicate count.
5. Insights box: 5 to 8 findings with numbers. Each one names the risk it creates (for example an identifier that could be averaged, or a binary column treated as numeric) and the fix you suggest.

Classification rules: identifier = unique per row, or a key-like name. Binary = exactly 2 distinct values. Discrete = integers that count things. Continuous = measured values with many distinct values. Ordinal = levels with a natural order; flag it as "assumed" and show the order. Nominal = any other category.

Run the page with the project's own command and fix any errors. Then answer with a RESULT REPORT I can paste to my tutor:
- PAGE: where it is and how to run it.
- One block per group (1. structured data, variable, observation; 2. data type and stored vs. statistical type; 3. numeric: continuous and discrete; 4. categorical: nominal, binary, ordinal and level; 5. identifier), each with: WHERE (tables, columns) / WHAT I RAN / WHAT IT SHOWED (numbers and column names) / WHAT IT MEANS FOR THE PROJECT / PROBLEMS OR SURPRISES.
- MISMATCH LIST: column, stored type -> statistical type, why.
- TOP INSIGHTS.
If a concept does not appear in the data, say so instead of inventing an example.