# Fixed Milestone 3 evaluation samples

`samples.json` preserves every text verbatim. `scenarios.py` declares which
fixtures and expected labels each criterion uses, before the evaluation.

Criteria 1 and 2 use two personal paragraphs from the existing `my own writing`
scenario plus the first three human-labelled files in lexicographic order from
`calibration_samples/hc3_50_100/validation`. Criterion 2 adds the first five
AI-labelled files from that same directory. Selection does not depend on
scores. These ten pieces are submitted separately for each criterion and each
trial; previous results are not reused. The two personal paragraphs are not
split or duplicated to claim five independent pieces of personal writing.

HC3 attribution: Guo et al. (2023), *How Close is ChatGPT to Human Experts?
Comparison Corpus, Evaluation, and Detection*, arXiv:2301.07597.
Dataset: Hello-SimpleAI/HC3, revision
`4d0ff18143b5a7e1b1e79beb540c04549d1e59d3`. The local export records
CC-BY-SA-4.0; upstream source terms also apply. Individual entries preserve
source row, answer index, split, dataset label, original path, and file hash.
Dataset labels supply the authorship reference; they are not independent
verification of the author. Only `own_1` and `own_2` are personal writing.

Criterion 3 preserves the old three coverage texts (salt: AI; livestock:
human; edited Tina Turner synopsis: unsure), adds the first personal paragraph
(human), and the original instructor time-management AI sample (AI). These are
expected labels, not labels assigned retrospectively from this run. The test
also checks the explicit Unit 7 bands: human <= 0.45, unsure between 0.45 and
0.60, AI >= 0.60. A case is correct only if its returned label matches both its
expected label and the documented band. The running service's human cutoff
is 0.40; this discrepancy is left unchanged and reported. All three labels
reached are also listed separately, without replacing the original 4/5 target.

Criterion 4 seeds five new submissions per trial and appeals each with
nonempty reasoning. It checks acceptance, status readback, both appeal audit
events, three scored variants, 60/40 arithmetic, majority vote, and the
required uncertainty or human-review message. The AI warning is checked for
meaning, rather than requiring the spelling errors in the original criterion.

Criterion 5 sends two valid texts, three malformed text bodies, and five
invalid/missing creator-ID bodies. Every POST is bracketed by GET /log so a
missing record, extra record, or mismatched field fails visibly. Invalid
creator IDs must appear as `unknown`, as specified in criteria.md. These
requests deliberately test the existing behavior; the service is not repaired
before the baseline.
