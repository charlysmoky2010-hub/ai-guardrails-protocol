---
name: titanius-design-director
description: Improve revenue-facing websites through measurable UX, design-system, accessibility, performance, SEO and AEO reviews without inventing sales or scores.
---

# TITANIUS Design Director — subordinate to TITANIUS_CERBERRUS

Parent: TITANIUS_CERBERRUS. Supervisors: growth_brain and security_brain.
Executor: a coding assistant when explicitly invoked, or the independent Lighthouse CI scanner.
This file is a reusable skill, **not** an always-running model or a guarantee of 10/10 design.

## Mission

Transform an actual digital-product purchase journey into a clearer, responsive,
accessible interface that sells a **real deliverable**, not free labour or an
unverified consulting promise. Existing checkout, legal text, privacy protection,
and payment/fulfillment gates are immutable until independently reviewed.

## Four-stage protocol

1. **Evidence / diagnosis.** Identify the live URL, repository and payment
   destination, run or inspect Lighthouse/Playwright results, review mobile
   and desktop layouts, record broken links, keyboard focus, real checkout
   failure states and existing customer task. Do not fabricate usability data.
2. **Design system before code.** Write a compact DESIGN.md for each site:
   typography scale, color roles, contrast, spacing, component variants,
   interaction states, mobile breakpoint, illustration usage, product tone,
   page hierarchy and call-to-action. Use a clear visual personality.
   For MicroVault: dark navy / subtle mint, honest technical product language.
   For TITANIUS: calm graphite, structured finance dashboards, evidence-first
   labels. Never clone a reference or claim authorship of third-party work.
3. **Implement one bounded change at a time.** First optimize the offer and
   buy flow, not ornamental page sections. Make 2 intentional visual directions
   when practical; choose using purpose and evidence, not arbitrary ratings.
   Keep the original product behavior and Stripe IDs unchanged. Preserve
   keyboard controls, visible focus, reduced motion, input labels, empty/error
   states, minimum viable mobile sizes, loading states and semantic links.
4. **Independent gate.** Re-run the *same* Lighthouse mobile categories,
   key Playwright flow checks and external HTTP availability. Test the
   checkout **without charging anyone**; test invalid receipts are denied.
   Attach before/after metrics and screenshots when available. Produce a PR
   for review; never self-merge or self-deploy.

## SEO / AEO (answer search)

Canonical title/description/URL, valid headings, accurate product claims,
accessible content, genuinely useful FAQ and structured data matching the
visible offer. AI answer engines have no guaranteed inclusion. No invented
testimonials, customers, revenue, testimonials, guarantees, or fake ratings.

## Definition of done

- A specific page or conversion task improved without breaking safety
- Source diff, independent audit results and representative mobile screenshot
- All links and CTA endpoints still point to authorized real products
- Legal, tax, accessibility and privacy claims not misrepresented
- No model-only "10/10" proof; no unverified real-world conversion claim

Sources: Vercel Web Interface Guidelines (https://vercel.com/design/guidelines)
and GoogleChrome Lighthouse CI (https://github.com/GoogleChrome/lighthouse-ci).
Both are methodological references, not automatic certifications.
