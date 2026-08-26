# Aster & Row Reliable RAG Support Agent

A reliable customer-support agent built for the Aster & Row AI Agent Intern Take-Home Assignment.

The agent combines retrieval-augmented generation, safe order lookup, session memory, source precedence, conflict detection, privacy protection, prompt-injection handling, and deterministic evaluation.

---

## 1. What this project does

The agent handles two main types of customer requests:

1. Knowledge-base questions
   - Returns
   - Shipping
   - Warranty
   - Product care
   - Membership
   - Other company policies

2. Order questions
   - Order status
   - Carrier
   - Tracking number
   - Estimated delivery when available

The system deliberately avoids guessing when the supplied information is insufficient and recommends human support when required.

---

## 2. Architecture

```text
                         Customer
                            |
                            v
                       Agent Router
                            |
              +-------------+-------------+
              |                           |
       Order-related question       Knowledge question
              |                           |
              v                           v
        Order Service                 Retriever
              |                           |
              v                           v
     Sanitized order data        TF-IDF + metadata
              |                           |
              |                           v
              |                  Authority filtering
              |                           |
              |                           v
              |                   Evidence assessment
              |                    /              \
              |                conflict         insufficient
              |                   |                 |
              |                   v                 v
              |             Human handoff       Safe abstention
              |                   |
              +---------+---------+
                        |
                        v
                       LLM
                        |
                        v
                 Final response
```

### Main components

`app/kb.py`
- Loads Markdown knowledge-base files.
- Parses YAML front matter.
- Preserves status, audience, authority, effective date, and other metadata.
- Splits documents into searchable sections.

`app/retriever.py`
- Uses TF-IDF retrieval with scikit-learn.
- Searches relevant passages rather than the full knowledge base.
- Uses metadata bonuses and penalties to prefer active authoritative customer-facing content.

`app/authority.py`
- Adds a second authority-aware ranking layer.
- Helps prevent internal or superseded documents from becoming customer-facing authority.

`app/orders.py`
- Implements the order lookup tool.
- Normalizes order IDs.
- Handles malformed and unknown IDs.
- Returns only customer-safe fields.
- Removes stale delivery fields from cancelled and returned orders.

`app/agent.py`
- Coordinates the complete workflow.
- Routes order questions separately from knowledge questions.
- Resolves order-related follow-ups using session history.
- Performs evidence assessment.
- Handles conflict and abstention states.

`app/evidence.py`
- Checks whether retrieved evidence is strong enough.
- Detects insufficient evidence.
- Detects the active-source conflict.
- Handles exclusive policies such as "Canada is currently the only supported international destination."

`app/safety.py`
- Blocks requests for protected system information.
- Blocks requests for private/internal order information.
- Detects attempts to use internal migration notes as policy authority.

`app/context.py`
- Builds retrieval queries using recent conversation context.
- Formats retrieved passages for the model.

`app/session.py`
- Maintains isolated conversation history per session.
- Supports multi-turn follow-up questions.

`app/llm.py`
- Contains the OpenAI LLM wrapper.

`app/mock_llm.py`
- Provides a deterministic local response generator for development and evaluation.
- Allows the evaluation suite to run without API costs.

`evaluation/run_eval.py`
- Runs all visible and custom regression cases.
- Reports individual case results and category-level results.

---

## 3. Technology choices

### Language

Python 3.10

### LLM

The project contains an OpenAI Responses API wrapper in `app/llm.py`.

A local deterministic mock implementation is also included in `app/mock_llm.py` so the full evaluation suite can run without requiring API credits.

### Retrieval

TF-IDF using `scikit-learn`.

I chose TF-IDF because the supplied corpus is small and the assignment prioritizes reliability and explainability over production-scale vector infrastructure.

### Metadata

YAML front matter is parsed using PyYAML.

Metadata such as:

- `status`
- `audience`
- `policy_authority`
- `effective_date`

is preserved and used during ranking.

### Storage

- Markdown files for the knowledge base
- JSON for mock order data
- In-memory session storage for conversation history

No external database or production vector database is required for this assignment.

### API

FastAPI is included for a minimal application interface.

---

## 4. Setup

### Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ai-agent-intern-test
```

### Create a virtual environment

```bash
python -m venv .venv
```

Git Bash on Windows:

```bash
source .venv/Scripts/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Environment variables

Copy `.env.example` to `.env`.

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
```

Do not commit `.env`.

The evaluation suite can be run using the deterministic mock implementation and does not require live API credits.

---

## 5. Running the evaluation

Run:

```bash
python -m evaluation.run_eval
```

The evaluation covers:

- retrieval
- groundedness
- tool use
- tool reliability
- privacy
- prompt security
- multi-turn behavior
- source conflicts
- abstention
- multi-source grounding

---

## 6. Evaluation results

Final evaluation:

```text
ASTER & ROW AGENT EVALUATION

[PASS] standard-return-window
[PASS] trailplus-return-window
[PASS] final-sale-damaged-exception
[PASS] canada-multiturn
[PASS] unsupported-country
[PASS] valid-order-lookup
[PASS] missing-order-id
[PASS] cancelled-order-stale-eta
[PASS] unknown-order
[PASS] shipped-without-eta
[PASS] order-data-privacy
[PASS] no-lifetime-warranty
[PASS] retrieved-prompt-injection
[PASS] insufficient-information
[PASS] genuine-active-source-conflict
[PASS] custom-lowercase-order
[PASS] custom-cancelled-order
[PASS] custom-no-eta
[PASS] custom-private-order-data
[PASS] custom-system-prompt
[PASS] custom-breeze-conflict
[PASS] custom-vegan-abstention
[PASS] custom-order-followup

Overall: 23/23 cases passed
```

### Category results

| Category | Result |
|---|---:|
| Abstention | 2/2 |
| Conversation | 1/1 |
| Groundedness | 3/3 |
| Multi-source grounding | 1/1 |
| Multi-turn | 1/1 |
| Privacy | 3/3 |
| Prompt security | 1/1 |
| Retrieval | 2/2 |
| Source conflict | 1/1 |
| Tool reliability | 3/3 |
| Tool use | 2/2 |
| Custom tool use | 3/3 |

---

## 7. Reliability and safety behavior

### Current policy takes precedence

The agent prefers active authoritative customer-facing material over superseded or internal material.

For example, a legacy returns document does not override the current returns policy.

### Order data is sanitized

The full `orders.json` is never passed to the model.

The tool exposes only information required for the customer-facing response.

Sensitive fields such as:

- email
- shipping address
- risk score
- warehouse notes
- internal support tags

are filtered out.

### Cancelled and returned orders

Cancelled and returned orders do not expose stale carrier or delivery information even if those fields exist in the source JSON.

### No invented ETA

If an order does not contain an estimated delivery date, the agent does not invent one.

### Insufficient information

When retrieved material does not adequately support a claim, the agent abstains and recommends human confirmation.

### Source conflicts

When current authoritative sources conflict, the agent does not silently pick one.

The Breeze Tumbler case is an example:

- one source recommends hand washing the stainless-steel body
- another says all components are dishwasher safe

The agent surfaces the conflict and recommends human confirmation.

### Prompt injection

Retrieved knowledge-base content is treated as data, not instructions.

Internal migration notes cannot override application rules or current policy authority.

### Protected information

The agent refuses requests for:

- system prompts
- hidden instructions
- credentials
- API keys
- internal order information
- customer private information

---

## 8. Multi-turn conversation

Session history is maintained separately for each session.

Examples supported by the evaluation suite include:

```text
User: Do you ship internationally?
Assistant: Canada is currently supported...

User: What about Canada?
Assistant: ...
```

and:

```text
User: Where is ORD-1007?
Assistant: ...
User: When will it arrive?
Assistant: ...
```

The second order question can recover the relevant order ID from recent conversation context.

---

## 9. Bug diary

## Bug 1 — Legacy policy could outrank current policy

### Reproduction

Ask:

```text
What is the standard return window?
```

### Root cause

Initial TF-IDF ranking considered textual similarity without giving enough importance to document status and authority.

### Fix

Added metadata-based retrieval weighting and authority filtering.

Active official customer-facing documents receive positive ranking signals while superseded and internal documents are penalized.

### Regression test

`standard-return-window`

---

## Bug 2 — Unrelated documents received positive scores

### Reproduction

Ask:

```text
Do you ship internationally?
```

Initially, unrelated active official documents with zero text similarity still received metadata bonuses.

### Root cause

The first scoring formula added metadata bonuses even when text similarity was zero.

### Fix

Zero-similarity documents are no longer promoted by metadata alone.

### Regression test

International shipping retrieval case.

---

## Bug 3 — Warranty answer passage was not ranked first

### Reproduction

Ask:

```text
What is the warranty period?
```

The product-care document initially ranked above the explicit warranty-period passage.

### Root cause

TF-IDF relied heavily on general word overlap and did not distinguish the exact semantic importance of the heading.

### Fix

The retriever gives headings additional representation and retrieves multiple passages rather than assuming the top result is always the complete answer.

### Regression test

Warranty retrieval case.

---

## Bug 4 — Evidence checker incorrectly trusted vague related evidence

### Reproduction

Ask:

```text
Are all bags and adhesives vegan?
```

### Root cause

Retrieved documents contained relevant words such as "bags", but did not establish the specific vegan-material claim.

### Fix

Added query-to-evidence coverage checks and explicit abstention behavior.

### Regression test

`custom-vegan-abstention`

---

## Bug 5 — Cancelled order exposed stale shipment data

### Reproduction

Look up:

```text
ORD-1004
```

### Root cause

The raw JSON contains carrier and delivery fields even though the current status is cancelled.

### Fix

Cancelled and returned orders return customer-safe status information without stale shipment fields.

### Regression tests

`cancelled-order-stale-eta`

`custom-cancelled-order`

---

## Bug 6 — Multi-turn order follow-up lost the order ID

### Reproduction

```text
Where is ORD-1007?
When will it arrive?
```

### Root cause

The second message contained no order ID.

### Fix

Added session history and recovery of the most recent order ID for explicit order follow-up phrases.

### Regression test

`custom-order-followup`

---

## Bug 7 — Handoff was initially inferred from generated text

### Reproduction

A conflict was detected correctly, but the generated mock response did not contain words such as "human support", causing `handoff=False`.

### Root cause

Handoff status was inferred from the wording of the model response.

### Fix

Handoff is now determined from application state:

- insufficient evidence
- source conflict
- protected-information request
- unknown order

### Regression tests

`genuine-active-source-conflict`

`custom-breeze-conflict`

---

## 10. Baseline vs final evaluation

Early baseline:

```text
15/23 passed
```

After fixing evidence handling, multi-turn retrieval, policy precedence, privacy protection, conflict handling, and evaluation behavior:

```text
23/23 passed
```

This improvement came from iterative regression testing rather than optimizing only for the happy path.

---

## 11. Known limitations

This project is intentionally scoped to the take-home assignment.

### Retrieval

TF-IDF is suitable for this small corpus but is not a production semantic retrieval system.

For a larger knowledge base, I would use embeddings with a vector store and evaluate retrieval recall systematically.

### Session storage

Session history is stored in memory, so it is lost when the application restarts.

A production system would use durable session storage with appropriate retention and privacy controls.

### LLM provider

The live application uses the Gemini API through the `google-genai`
Python SDK.

`app/llm.py` contains the Gemini LLM implementation.

A deterministic local implementation is also included in
`app/mock_llm.py` so the evaluation suite can run without API
calls and produce reproducible results.

### Authentication

The assignment explicitly allows possession of the mock order ID to be treated as sufficient authentication.

A production order system would require stronger identity verification.

### Action execution

The agent can explain policies and order status but does not actually execute refunds, cancellations, replacements, or address changes.

Production use would require explicit transactional tools with authorization and audit logging.

### Conflict detection

The current implementation combines metadata and targeted conflict rules. A production system should generalize conflict detection beyond known documents and product cases.

---

## 12. AI coding tools used

I used ChatGPT as an AI coding assistant during development.

It was used for:

- explaining the assignment requirements
- designing the initial architecture
- generating initial implementation drafts
- debugging Python errors
- designing tests
- reviewing evaluation failures
- improving the README

AI-generated code was reviewed and tested locally rather than being accepted blindly.

### Example of an incomplete AI suggestion

An early implementation gave metadata bonuses to every active official document even when its text similarity was zero.

This caused unrelated documents to appear in retrieval results.

I identified the issue through testing, changed the scoring behavior, and added regression coverage.

Another issue was an overly strict evidence-coverage heuristic that initially treated an explicit "Canada only" policy as insufficient for a question about Germany. This was corrected so exclusive policies can answer unsupported-destination questions.

---

## 13. Running individual components

### Knowledge-base loader

```bash
python -m app.test_kb
```

### Retriever

```bash
python -m app.test_retriever
```

### Order service

```bash
python -m app.test_orders
```

### Agent

```bash
python -m app.test_agent
```

### Evidence checks

```bash
python -m app.test_evidence
```

### Security checks

```bash
python -m app.test_security
```

### Evaluation suite

```bash
python -m evaluation.run_eval
```

---

## 14. Debug mode

Set:

```env
DEBUG=true
```

when debugging.

The application logs can be used to inspect:

- incoming user messages
- session context
- retrieval decisions
- tool execution
- sanitized results
- handoffs
- errors

Secrets and private customer information are not intentionally logged.

---

## 15. Demo

[Watch the Aster & Row Agent Demo](https://drive.google.com/file/d/16e_kkf7O4-GVmhkkdkBQmfQ7ENTybq0w/view?usp=sharing)

## 16. Repository structure

```text
.
├── README.md
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── authority.py
│   ├── context.py
│   ├── evidence.py
│   ├── kb.py
│   ├── llm.py
│   ├── logging_config.py
│   ├── main.py
│   ├── mock_llm.py
│   ├── orders.py
│   ├── prompts.py
│   ├── retriever.py
│   ├── safety.py
│   └── session.py
│
├── data/
├── evaluation/
│   ├── custom-cases.json
│   ├── run_eval.py
│   └── visible-cases.json
│
├── knowledge-base/
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## 17. Final result

The final local evaluation passes:

**23/23 cases**

The implementation focuses on reliability rather than maximum feature count:

- relevant evidence retrieval
- source authority handling
- safe order lookup
- privacy protection
- conversation context
- conflict detection
- safe abstention
- prompt-injection protection
- deterministic regression evaluation
