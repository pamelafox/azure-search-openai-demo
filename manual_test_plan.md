# Manual Test Plan: Responses API Migration

## Core Functionality

- [X] **Non-streaming chat** — Disable streaming in settings, ask a question, verify answer + citations render
- [X] **Streaming chat** — Enable streaming, ask a question, verify text streams smoothly with citations
- [X] **Multi-turn conversation** — Ask a follow-up question that references prior context, verify coherent answer
- [X] **Follow-up questions** — Enable "suggest follow-up questions", verify they appear after the answer
- [X] **Query rewriting** — Open thought process panel, verify the rewritten search query is shown
- [X] **Temperature setting** — Change temperature to 0 and 1, verify responses work at both extremes

## Reasoning Models (if deployed)

- [X] **Streaming with reasoning model** — Switch to a GPT-5 deployment, verify streaming works
- [X] Change reasoning efforts to each allowed effort level
- [X] **Reasoning token usage** — Check thought process panel shows reasoning token count
- [X] Follow-up questions
- [X] Multi-turn
- [X] Temperature is hidden in Settings in UI

## Multimodal (if configured)

- [ ] **Image sources in response** — Ask a question that triggers image sources, verify images render
- [ ] **Image describer via ingestion** — Run `prepdocs` on a PDF with images, verify image descriptions are generated

## Agentic Retrieval (if configured)

- [ ] **Agentic knowledgebase** — Enable agentic knowledgebase in settings, ask a question, verify answer
- [ ] **Web source** — Enable web source (non-streaming only), verify web results appear
- [ ] **SharePoint source** — Enable SharePoint source, verify SharePoint results appear

## Error Handling

- [ ] **Content filter** — Ask something that triggers content filtering, verify error message renders gracefully - cant replicate!
- [ ] **Auth error** — Test with invalid/expired credential, verify auth error surfaces properly

## Code cleanliness

- [ ] Check mocks: tests are running slow, is everything mocked fully?
