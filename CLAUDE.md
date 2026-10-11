# Working in this repository

The project is a Streamlit app (`data_app_gestao.py`) on top of `transform.py`, which reads the project's tables from Supabase. The study notes are in `learning/`.

## Study sessions

When the user says they are studying a part (for example "I'm in Part E"), this is a study session, not a build session:

- Read `learning/README.md` and the part's file in `learning/`. Follow "How a part is studied" there.
- Teach in the chat, one concept at a time, in the order of the part's concept map: a plain definition, a tiny example worked by hand, then the same idea computed on the project's real data (through `transform._ler`, read-only). Then ask the user to explain it back in their own words, correct them, and ask one or two check questions before the next concept. Do not explain the whole part at once.
- Show only aggregates (counts, percentages, percentiles, column names). Never print rows, identifier values or credentials.
- Do not change the app in a study session. The only files to edit are in `learning/`: update the "Understood on" column, the study log and "Still unclear" of the part file, and its status in `learning/README.md`.
- The books are in the repository root; cite the page numbers listed in the part file.

The Supabase settings (`DA_LEARN_SUPABASE_URL`, `DA_LEARN_SUPABASE_KEY`) come from the environment; never write them into a file.
