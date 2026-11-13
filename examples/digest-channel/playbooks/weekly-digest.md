---
id: PB-001
status: active
version: 2
owner: dana
applies_to: [atlas, scout]
approved_by: dana
approved_on: 2026-11-03
supersedes: PB-001@1
---

# PB-001: Weekly digest sourcing

## Purpose

Find, verify and assemble the week's database release and deprecation news.

## Steps

1. **Scout, by Wednesday 17:00.** Search public sources for releases and deprecation
   notices from the past seven days. Send one `handoff` to Atlas, titled
   `[handoff] Digest sources, week of <Monday's date>`, with one entry per item:
   project, what changed, URL, and a verbatim quote of the line that supports it.
   One handoff a week. If more turns up later, comment on that handoff.
2. **Atlas, by Thursday 12:00.** Open every URL and confirm the quote is there and
   says what the entry claims. Record each source in `ledgers/sources.csv` as
   `verified` or `rejected`, with the reason. Reply on the handoff with the outcome.
3. **Atlas, by Thursday 17:00.** Draft the digest from verified entries only and send
   Dana a `decision` message with the draft linked.
4. **Dana** sends the digest, or returns it with changes.

## Limits

- Scout takes no external action under this playbook. It reads public pages; it does
  not sign up, post, email or fill in forms.
- An entry without a primary source (RULES rule 5) is rejected, however good the lead.
- v2 change (Dana, 2026-11-03): *"Preprints and vendor benchmarks are out. Releases
  and deprecations only."*
