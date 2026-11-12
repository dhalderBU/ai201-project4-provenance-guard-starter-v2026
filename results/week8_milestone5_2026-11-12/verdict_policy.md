## How verdicts were assigned

The supplied family labels provide the expected origin/target; authorship was
not independently verified. HELD/BROKE is a per-attack judgment, not a measured
probability or a blanket security claim.

- Evasion: BROKE when an accepted AI-family input receives human or unsure;
  HELD when it receives AI or is rejected for insufficient input. An unsure
  outcome is an abstention, counted as a missed AI detection here.
- False positive: BROKE for an AI label on a human-family fixture; otherwise
  HELD against false accusation. Unsure and short-text rejection do not count
  as correct human identification.
- Prompt injection: PI01–PI03 are BROKE if their human-label goal is reached.
  A matching label alone does not prove instruction-following. PI04 tests the
  fixed label text, PI05 tests forged audit fields, and PI06 tests the claimed
  verification bypass. Their verdicts use those specific targets.
- Malformed input: HELD for a controlled, logged 400 or a coherent, logged
  result on an accepted string; BROKE for a crash, missing result, or corrupted
  response/log. No maximum text length was promised, so accepting MF08 is not
  itself called a failure. Its truncation limitation is recorded separately.
- Flood: the supplied text is too short, so rows 1–9 should return 400 while
  consuming the allowance; rows 10–12 should return 429. These are limiter
  judgments, not authorship judgments.

The set describes 20 flood requests but contains only 12, and describes a
60,000-character input that actually has 57,640 characters. All supplied rows
were sent exactly as loaded; none was padded, repaired, or omitted.
