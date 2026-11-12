# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positive rate

<!-- Your criterion. It must name a number. -->
Out of five confirmed human-written pieces, no more than two may receive the label as AI written (i.e max false positive rate of 0.4).  


**Why this target:**
This is the most critical requirement and is the core requirement . Ideally I would like it to be 20% or below but as we dont know how much of training has been done I will keep it at false positive max allowed 40%) . 


---

## 2. Spread between clearlyAI and clearly Human 

<!-- Your criterion. -->
For 5 confirmed AI-written pieces and 5 confirmed human-written pieces, the average combined score of the AI-written pieces must be at least 0.3 higher than the average combined score of the human-written pieces.


**Why this target:**
Since the AI authored articles will have higher combined score. Without a gap of 0.3 we will have mis-classification 


---

## 3. Label reachability

<!-- Your criterion. -->
At least 4 of 5 test cases should receive the correct label. The combined-score
ranges match `config.py` and the README:

- `0.00 <= score <= 0.45`: `human`.
- `0.45 < score < 0.60`: `unsure` (borderline).
- `0.60 <= score <= 1.00`: `ai`.


**Why this target:**
The AI boundary is `0.60`, and the human boundary is `0.45`, leaving an unsure
range between them. Lowering the AI boundary can increase false accusations
against human writers. These are decision settings to evaluate on labeled
samples, not calibrated probabilities of authorship.


---

## 4. Process of Appeal

<!-- Your criterion. -->
Every appeal with an existing content_id and non-empty reasoning must be logged and marked under_review. Rescore the text three times based on below and receive label. 
- Original Text
- Original text with first sentence removed
- Original text with last sentence removed 

Based on majority lable the application will confirm the result. If the majority is either AI or Human then the application will respond withe lable for the majority. In appeals process we will use slightly different weightage model where we will take 0.6 of Models_score and 0.4 of style_score thereby increasing the style component. 

In case the majority is `unsure' then the application will respond with  :
“Based on revaluation we do not have enough evidence to determine how this text was written. Your appeal has been recorded.”

Incase the response lable is AI  after an Appeal was revaluated, the application will also send a message : "Due to the nature the mathematical computation involved in arriving at the conclusion, it is possible that it has been evaluated as unsure though it was written by human. If that is the casae please request for human re-evaluation and submit various vesions of the work product so as it can be human evaluated"

**Why this target:**
We will make sure majority of three comes out to give us the result. The reason we are modifying the body because the scores are deterministic as we are not using LLM and instead using detector for modelscore and the Style_score is also deterministic. We are putting more emphasis on style this time


---

## 5. Eval logging

<!-- Your criterion. -->
Every request to `POST /submit` (100% of test requests), including blank or
invalid input, must create a JSON entry in `logs/audit.jsonl`.

Each successful evaluation entry must include these ten fields:
`timestamp`, `content_id`, `creator_id`, `guess`, `model_score`, `style_score`,
`combined_score`, `label`, `status`, and `confidence`.

For successful submissions, the logged results must match the response, and
`confidence` must equal `combined_score`. The status must be `decided`.

For blank, missing, or invalid input, use the existing rejection log format:
`timestamp`, `creator_id`, `event="rejected"`, `status="rejected"`, and
`reason`. Use `unknown` if no valid creator ID is available. A rejected entry
does not need scores or a classification because no evaluation was completed.

**Why this target:**

Every request should leave a record so I can explain a decision or rejection.
The individual scores help locate mistakes, and matching the response shows
what the writer actually received.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
