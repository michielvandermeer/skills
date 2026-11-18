# CONTEXT.md Format

## Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, never how the application uses it or is built. A business fact that is part of what the term means stays.
- **Only include terms specific to this project's context.** A term belongs when people who work in this domain use the word with a meaning the domain gives it. Two kinds of word stay out even when the project uses them extensively: a word that means the same in any codebase (timeouts, error types, retries, test doubles, utility patterns), and a word that names how the app is built (a class, file, table, flag, API method, or layout control). UI element names stay out too, unless the context's own subject is the UI, such as a component library. Before adding a term, ask: would a newcomer to this domain need it defined?
- **Hold the intro and `## Language` only.** Example dialogues, flagged ambiguities, status notes, and how-to prose belong elsewhere. Facts the code shows stay in the code, and an ADR holds what the code cannot explain.
- **Group terms under subheadings** when natural clusters emerge. If all terms belong to a single cohesive area, a flat list is fine.

## Single vs multi-context repos

**Single context (most repos):** One `CONTEXT.md` at the repo root.

**Multiple contexts:** A `CONTEXT-MAP.md` at the repo root lists the contexts, where they live, and how they relate to each other:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md): generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md): manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events, and Fulfillment consumes them to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events, and Billing consumes them to generate invoices
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

The skill infers which structure applies:

- If `CONTEXT-MAP.md` exists, read it to find contexts
- If only a root `CONTEXT.md` exists, single context
- If neither exists, create a root `CONTEXT.md` lazily when the first term is resolved

When multiple contexts exist, infer which one the current topic relates to. If unclear, ask.
