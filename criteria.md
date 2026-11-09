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
This is the most critical requirement and is the core requirement . Ideally I would like it to be 20% or above but as we dont know how much of training has been done I will keep it at false positive max allowed 40%) . 


---

## 2. Spread between clearlyAI and clearly Human 

<!-- Your criterion. -->
For 5 confirmed AI-written pieces and 5 confirmed human-written pieces, the average combined score of the AI-written pieces must be at least 0.3 higher than the average combined score of the human-written pieces.


**Why this target:**
Since the AI authored articles will have higher combined score. Without a gap of 0.3 we will have mis-classification 


---

## 3. Label reachability

<!-- Your criterion. -->
Atleast 4 of 5 cases the label should be correctly reached based on below thresholds for combined score :
Any score equal or more than 0.65 is  AI generated
Any score >= 0 and less than 0.35 is  clearly_human
Any score  between 0.35 but lower than 0.65 is borderline 


**Why this target:**
I feel we should only classify it as AI written when we have high degree of confidence so keeping that score threshold as 0.65 for AI generated. If we make it too low there is a possibility that writers actual writings will be falsely classified as AI written.  


---

## 4. Process of Appeal

<!-- Your criterion. -->
Every  appeal must record the content_id and reasoning, set the status to under_review, and return confirmation. For appealed requests we will rescore 5 times , and if of the five 3 or more comes human then we will term it as human else will send a response "we could not confirm the content to be written by human after appeals process content review.

**Why this target:**
We will not reduce the threshold for appeal but we will make sure majority of five evaluation comes out positive. THis gives us enough confidence 


---

## 5. Eval logging

<!-- Your criterion. -->
Every request to `POST /submit` (100% of test requests), including blank or
invalid input, must create a JSON entry in `logs/audit.jsonl`.

Each entry must include `timestamp`, `creator_id`, `content_id`, `guess`,
`model_score`, `style_score`, `combined_score`, `confidence`, `label`, `status`,
`http_status`, and `http_status_meaning`.

For successful submissions, the logged results must match the response, and
`confidence` must equal `combined_score`. For blank, missing, or invalid input,
log `event="rejected"`, `status="rejected"`, the rejection `reason`, and HTTP
`400` (`Bad Request`). Use `unknown` if no valid creator ID is available and
`null` for results that do not exist, such as scores, a label, or a content ID.

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
