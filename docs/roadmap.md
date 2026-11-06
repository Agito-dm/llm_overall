
# llm_overall — Development Roadmap

## Day 1 — Basic LLM Pipeline
- [x] Python environment and dependencies
- [x] OpenAI-compatible LLM client
- [x] System and user prompts
- [x] Summary, key points, helpful response
- [x] Three successful API examples
- [x] Unit tests and Ruff checks
- [x] Request timing and logging
- [x] README and documentation

## Day 2 — Prompt Engineering
- [x] Three prompt variants
- [x] System prompt and user templates
- [x] Length and format constraints
- [x] Comparison on identical inputs
- [x] Quality evaluation and final selection (B — Constrained)

## Day 3 — Structured Output
- [x] Extended JSON schema
- [x] Pydantic validation
- [x] Missing fields and invalid types
- [x] Five successful examples
- [x] 18 passing tests

## Day 4 — Classification and Routing
- [x] Five categories and intent detection
- [x] Explicit Python routing logic
- [x] Category-dependent response generation
- [x] Ten evaluation inputs
- [x] Pydantic validation of routed output
- [x] CLI integration with --routed
- [x] 55 passing automated tests
- [x] Real Gemini evaluation (8/10 successful before output normalization)

## Day 5 — Multi-step Chain
- [ ] Extract meaning
- [ ] Classify request
- [ ] Build structured fields
- [ ] Generate final answer
- [ ] Self-check
- [ ] Step-by-step logs

## Day 6 — Reliability
- [ ] Retry on temporary API errors
- [ ] Fallback behavior
- [ ] Invalid JSON and empty responses
- [ ] Response length guards
- [ ] At least three negative scenarios

## Day 7 — Finalization
- [ ] Complete CLI workflow
- [ ] Five demo scenarios
- [ ] Updated README
- [ ] Full test suite
- [ ] Clean-clone reproducibility test
