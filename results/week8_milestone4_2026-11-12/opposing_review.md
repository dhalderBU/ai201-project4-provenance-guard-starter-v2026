# Opposing-verdict review — criterion 1

This is a self-review by the coding assistant, **not a response from Claude**.
The requested Claude CLI call timed out after 180 seconds without output.
Browser access was also unavailable. `claude_attempt.json` records the attempt;
`claude_prompt.txt` preserves the original criterion, target, three trials,
verdict, and the requested challenge prompt for a later Claude conversation.

## Criterion presented for review

Original: “Out of five confirmed human-written pieces, no more than two may
receive the label as AI written (i.e max false positive rate of 0.4).”

Target: at most 2 of 5. Trials: 0/5, 0/5, 0/5. Proposed verdict: MET.
The five fixtures are two personal paragraphs plus three HC3 human-labelled
answers. The separate staff attack set produced six false AI labels among
eight human-labelled inputs (one unsure and one short-text rejection).

## Strongest case for the opposite verdict

“Confirmed human-written” is an evidentiary condition, not merely a filename.
If the three HC3 records were mislabelled, edited, duplicated, selected after
seeing scores, or sourced from ChatGPT answers, the five-piece denominator
would not be established. Two pieces alone would not satisfy the original
five-piece test. An unsupported denominator could invalidate the claimed pass
without changing the numeric target.

The broader interpretation of “max false positive rate of 0.4” is also under
pressure: six of eight human-reference attacks were labelled AI. The personal
paragraphs and three informal HC3 answers do not cover the formal, technical,
and repetitive writing that failed. If the criterion is meant to establish a
general false-positive ceiling, this cohort does not establish it. Repeating
the same five texts demonstrates stability, not fifteen independent samples
of writing or a population error bound.

The eight-attack result cannot simply replace the original five-text cohort.
Doing that after seeing the results changes the evaluation sample. The issue
to resolve is whether the criterion is a fixed five-piece acceptance test or
a population guarantee, and whether the five pieces have adequate provenance.

## Evidence that would settle the challenge

- Match the two personal paragraphs to the pre-run own-writing scenario.
- Match each HC3 text, source row, and answer index to the original
  `human_answers` field, and distinguish dataset attribution from independent
  confirmation by an author.
- Check that all five texts are distinct, existed before the evaluation, and
  were submitted in each of the three trials without substitutions.
- Count labels from raw HTTP responses and match their content IDs and scores
  to audit entries. A request rejected before scoring must not silently count
  as a successful human classification.
- Read the original criterion and report its scope explicitly. A fixed
  five-piece result and a claim about all human writing require different
  evidence. A broader estimate would require a new, prospectively defined
  cohort with formal, technical, repetitive, and informal human writing; it
  would be an additional evaluation, not a retrospective target change.

These arguments and evidence requests intentionally do not choose a verdict.
The final decision and its scope are recorded separately in the README.
