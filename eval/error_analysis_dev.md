# Error analysis (dev set only)

System analysed: hybrid search (dense BGE embeddings + BM25, RRF with weights 1:2),
clause-aware chunks with max size 1500 characters.
Only dev contracts were read. The test set was not used.

## 1. Where the right chunk lands (Non-Compete)

Dev contracts that contain the clause: n = 75.

| Rank of first correct chunk | Share |
|---|---|
| 1 | 43% |
| 2-3 | 32% |
| 4-10 | 13% |
| 11 or worse | 12% |

The right chunk is in the top 10 for 88% of contracts but first only 43% of the time.
So most misses are near misses (rank 2-3), which a reranker can fix.
Only 12% are total misses that a reranker cannot reach.

## 2. Where the right chunk lands (Termination For Convenience)

Dev contracts that contain the clause: n = 118.

| Rank of first correct chunk | Share |
|---|---|
| 1 | [FILL]% |
| 2-3 | [FILL]% |
| 4-10 | [FILL]% |
| 11 or worse | [FILL]% |

What this shows: [FILL: one sentence, for example whether most misses are near misses.]

## 3. Why Non-Compete fails: failures I read

I read [FILL: number] failures where the right chunk was not ranked first.

| Cause | Count |
|---|---|
| A different clause won (confidentiality or liability text with similar wording) | [FILL] |
| A definitions section won on shared words | [FILL] |
| A neighbouring chunk of the same clause won | [FILL] |
| Highlight looks doubtful or incomplete | [FILL] |
| Other | [FILL] |

First impressions from the first 7 failures I looked at (these need checking
against the full chunk text, because the notebook output was truncated):

- Pacira: a "Commercial Launch" definition ranked first.
- Impresse: the "Affiliate" definition ranked first. It contains "directly or
  indirectly", which is one of my Non-Compete keywords, so that keyword backfires.
- Allied: a limitation of liability clause ranked first.
- Fuse Medical and Inmode: confidentiality clauses ranked first. They share the
  phrase "shall not" with non-compete clauses.
- WPP: the top chunk looked like a neighbouring part of the same clause.

What I learned: [FILL: one or two sentences in your own words.]

## 4. Why Termination For Convenience fails

I read [FILL: number] failures.

| Cause | Count |
|---|---|
| [FILL] | [FILL] |

What I learned: [FILL]

## 5. Are gold clauses split across chunks?

Share of lawyer highlights that do not fit fully inside a single chunk (dev):

| Clause | Highlights | Split |
|---|---|---|
| Governing Law | 327 | 0.9% |
| Termination For Convenience | 164 | 1.8% |
| Notice Period To Terminate Renewal | 79 | 2.5% |
| Renewal Term | 140 | 4.3% |
| Cap On Liability | 477 | 6.9% |
| Uncapped Liability | 130 | 9.2% |
| Non-Compete | 173 | 11.0% |

Chunk boundaries are not the main cause of failures. Even for Non-Compete, the
worst case, only 11% of