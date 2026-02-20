# Smart Notification Fatigue System — February 19, 2026\n\n## Executive Summary\n\n- The product team aligned on a **measurement-first launch strategy**: no experiments ship until baseline instrumentation, notification taxonomy, and ML logging spec are in place — without these, results will tell us *what* happened but not *why*.\n- **Experiment 4 (Notification History / \"Why Did I Get This?\")** is prioritized as the first-to-ship feature, selected for its high leverage, low engineering complexity, and interpretable funnel.\n- The engineering architecture is considered ready; the critical gap is the **measurement foundation** — taxonomy, identity resolution, timezone coverage, and event instrumentation are all pre-Sprint 1 blockers.\n- **Concurrent experiments require a mutual exclusion layer** or a sequenced holdout schedule; running Experiments 1–3 simultaneously without one will produce confounded, unactionable data.\n- The ML system carries strict operational guardrails: suppression regret rate <5%, explicit signal incorporation lag <1 hour, and model staleness recalibration target of <7 days.\n\n---\n\n## What We Decided\n\n| # | Decision | Rationale |\n|---|----------|-----------|\n| 1 | **Baseline instrumentation is a non-negotiable pre-condition** | Open rate, opt-out rate, and mute rate baselines by notification type must exist before any experiment runs. Without them, there is no valid control to measure against. |\n| 2 | **Notification taxonomy finalized before Sprint 1** | All segmentation and experiment analysis requires a consistent type taxonomy (sender, topic, type, priority tier). PM owns delivery. |\n| 3 | **Experiments 1–3 cannot run concurrently without mutual exclusion** | Overlapping treatment arms produce confounded results. Either a bucketing framework is built or experiments are sequenced with defined holdout periods. |\n| 4 | **Experiment 4 ships first** | Notification History (\"Why Did I Get This?\") has the highest leverage-to-complexity ratio, a clear causal mechanism, and the most interpretable funnel of all candidates. |\n| 5 | **Experiment 5 (Digest vs. Real-Time) uses propensity score matching, not A/B** | Digest is opt-in; self-selection bias invalidates a raw A/B comparison. Matched cohort analysis is the only valid methodology. Raw opt-in comparisons will not be used to declare treatment effects. |\n| 6 | **\"Tomorrow\" snooze is blocked until timezone coverage is confirmed** | Undefined timezone behavior in the control arm introduces noise. Feature requires a fallback if coverage is <95%. |\n| 7 | **Fatigue score logged at send time, not reconstructed post-hoc** | Retroactive ML score reconstruction is unreliable. `fatigue_score_at_send` must be captured in real time in the `notification.delivered` event. This is a pipeline requirement. |\n| 8 | **P0 classification tracked per team as a governance metric** | P0 status bypasses suppression logic. Without audit visibility, teams have direct incentive to abuse the label. Team-level `p0_classification_rate` added to the analytics dashboard. |\n| 9 | **Digest experiment requires a minimum 6-week measurement window** | Novelty effect will inflate early open rates; Week-1 data is not actionable. Evaluation gate set at 6 weeks minimum. |\n| 10 | **ML guardrails codified: suppression regret <5%, signal incorporation lag <1 hour** | These are launch-gate requirements tracked in the model evaluation framework separately from product KPIs. |\n\n---\n\n## What We Considered\n\n**Experiment methodology alternatives:**\n- *A/B test for Digest vs. Real-Time* was considered and rejected due to self-selection bias inherent in the opt-in model. Propensity score matching is the correct approach despite higher analytical complexity.\n- *Running all experiments simultaneously* was evaluated for speed but rejected because without a mutual exclusion layer, treatment arm overlap makes results uninterpretable. Sequencing was accepted as a viable fallback to a formal bucketing framework.\n\n**ML signal timing:**\n- *Post-hoc fatigue score reconstruction* was explored as a lower-effort alternative to real-time logging, but dismissed as unreliable — model state at send time cannot be accurately reproduced from downstream signals.\n\n**Preference center reliance:**\n- Sole reliance on preference center data for understanding fatigue was noted as analytically insufficient. The preference center has **survivorship bias by design** — the most fatigued users disengage before ever visiting it. An opt-out cohort analysis pipeline was added to address this gap.\n\n**P0 bypass governance:**\n- The option of not tracking P0 usage per team was briefly considered. Rejected on the basis that it creates an unchecked incentive to game suppression logic.\n\n---\n\n## Risks & Unknowns\n\n| Risk | Severity | Notes |\n|------|----------|-------|\n| **Timezone data completeness below 95%** | High | Blocks \"Tomorrow\" snooze and digest timing; fallback behavior undefined until audit is complete |\n| **Cross-device identity resolution gaps** | High | Required for Experiment 2 (cross-channel dedup); current accuracy of the identity graph is unconfirmed |\n| **ML model staleness** | High | If user behavior shifts post-launch and recalibration takes >7 days, suppression decisions degrade in real time |\n| **P0 classification abuse** | Medium | Teams learn the P0 label bypasses suppression; without governance controls, label inflation erodes system integrity |\n| **Experiment mutual exclusion framework delivery risk** | Medium | If bucketing layer is delayed, experiments must be strictly sequenced — extending the overall roadmap |\n| **Feedback signal decay** | Medium | User feedback submitted long after notification delivery is lower quality; time-weighted signals require agreed weighting spec with ML |\n| **Accessibility signal coverage** | Low-Medium | Screen reader UA string and OS accessibility SDK flags are unconfirmed as reliable proxies; could affect guardrail coverage for timing optimization experiments |\n| **Novelty effect in Digest experiment** | Medium | Early open rate inflation is expected; the 6-week window mitigates but does not eliminate this risk |\n\n---\n\n## Next Steps\n\n**Pre-Sprint 1 gate items — nothing ships until these are resolved or have a signed-off mitigation plan:**\n\n| Action | Owner | Priority |\n|--------|-------|----------|\n| Finalize notification taxonomy (sender, topic, type, priority tier) | PM | 🔴 Blocker |\n| Draft experiment sequencing plan (Experiments 1–4 with holdout periods); circulate for Engineering + Analytics sign-off | PM | 🔴 Blocker |\n| Establish P0 classification audit process (who can set P0, review cadence, governance trigger threshold) | Product / PM | 🔴 Blocker |\n| Deploy baseline measurement pass: open rates, opt-out rates, mute rates by notification type (segmented by volume, multi-device status, account age) | Analytics | 🔴 Blocker |\n| Build opt-out cohort analysis pipeline (to address preference center survivorship bias) | Analytics | 🔴 Blocker |\n| Define and implement experiment mutual exclusion / bucketing layer; propose sequencing plan if blocked | Analytics | 🔴 Blocker |\n| Instrument feedback timing (`time_since_delivery_ms` on all `feedback.rated` events); coordinate weighting spec with ML | Analytics | 🔴 Blocker |\n| Instrument all required events (`notification.delivered`, `.opened`, `.dismissed`, `.snoozed`, `.muted`, `.duplicate_sent`, `preference.center.*`, `feedback.rated`) — deploy to production | Engineering | 🔴 Blocker |\n| Agree on and implement ML model logging spec (`fatigue_score_at_send` captured in real time in `notification.delivered`) | Engineering / ML | 🔴 Blocker |\n| Audit timezone data completeness across user base; report % with confirmed timezone; propose fallback if <95% | Engineering | 🔴 Blocker |\n| Build cross-device identity graph; confirm dedup_window_ms and resolution accuracy | Engineering | 🔴 Blocker |\n| Assess cross-device dedup experiment infrastructure feasibility; report constraints | Engineering | 🟡 High |\n| Investigate accessibility user signal availability (screen reader UA, OS accessibility SDK); provide proxy coverage estimate | Engineering | 🟡 High |\n| Define ML model staleness decay monitoring (target: <7 days to recalibrate); implement before production | ML | 🔴 Blocker |\n\n---\n\n## Metrics to Watch\n\n**Product KPIs:**\n\n| Metric | Target / Threshold |\n|--------|--------------------|\n| Notification open rate | Baseline TBD; directional improvement expected |\n| Opt-out rate by notification type | Directional decrease post-experiment |\n| Mute rate | Directional decrease post-experiment |\n| Preference center engagement | Increase as transparency features ship |\n| Digest open rate (6-week window minimum) | Compared to propensity-matched real-time cohort |\n| Snooze utilization rate | Tracked post-Experiment 3 |\n\n**ML Model Guardrails:**\n\n| Metric | Hard Limit |\n|--------|------------|\n| Suppression regret rate | < 5% |\n| Explicit signal incorporation lag | < 1 hour |\n| Model staleness / recalibration time post behavior shift | < 7 days |\n\n**Governance:**\n\n| Metric | Purpose |\n|--------|---------|\n| `p0_classification_rate` per team | Detect and deter P0 label abuse |\n| Experiment bucketing integrity | Track treatment arm contamination rate |\n| Timezone data completeness | Gate for snooze and digest features |\n\n---\n\n> **Bottom line:** The engineering architecture is sound. The measurement foundation is not yet in place. Shipping experiments without baselines, taxonomy, and the ML logging spec means we'll know *what* happened but not *why* — and that means we can't iterate. The pre-Sprint 1 gate is firm.",
"mediaUrl": null
,
"meta": {
"durationMs": 71512,
"agentMeta": {
"sessionId": "3b0e7802-67a5-4aa6-9879-4ed8b1294e7d",
"provider": "anthropic",
"model": "claude-sonnet-4-6",
"usage": {
"input": 18,
"output": 2933,
"cacheRead": 41754,
"cacheWrite": 12249,
"total": 29931
},
"lastCallUsage": {
"input": 8,
"output": 2831,
"cacheRead": 26911,
"cacheWrite": 181,
"total": 29931
},
"promptTokens": 27100
},
"aborted": false,
"systemPromptReport": {
"source": "run",
"generatedAt": 1771543188488,
"sessionId": "3b0e7802-67a5-4aa6-9879-4ed8b1294e7d",
"provider": "anthropic",
"model": "claude-sonnet-4-6",
"workspaceDir": "/Users/zhiyuanguo/.openclaw/workspace",
"bootstrapMaxChars": 20000,
"bootstrapTotalMaxChars": 150000,
"sandbox": {
"mode": "off",
"sandboxed": false
},
"systemPrompt": {
"chars": 25306,
"projectContextChars": 13631,
"nonProjectContextChars": 11675
},
"injectedWorkspaceFiles": [
{
"name": "AGENTS.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/AGENTS.md",
"missing": false,
"rawChars": 7804,
"injectedChars": 7804,
"truncated": false
},
{
"name": "SOUL.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/SOUL.md",
"missing": false,
"rawChars": 1664,
"injectedChars": 1664,
"truncated": false
},
{
"name": "TOOLS.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/TOOLS.md",
"missing": false,
"rawChars": 850,
"injectedChars": 850,
"truncated": false
},
{
"name": "IDENTITY.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/IDENTITY.md",
"missing": false,
"rawChars": 633,
"injectedChars": 633,
"truncated": false
},
{
"name": "USER.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/USER.md",
"missing": false,
"rawChars": 474,
"injectedChars": 474,
"truncated": false
},
{
"name": "HEARTBEAT.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/HEARTBEAT.md",
"missing": false,
"rawChars": 167,
"injectedChars": 167,
"truncated": false
},
{
"name": "BOOTSTRAP.md",
"path": "/Users/zhiyuanguo/.openclaw/workspace/BOOTSTRAP.md",
"missing": false,
"rawChars": 1449,
"injectedChars": 1449,
"truncated": false
}
],
"skills": {
"promptChars": 2504,
"entries": [
{
"name": "coding-agent",
"blockChars": 627
},
{
"name": "healthcheck",
"blockChars": 507
},
{
"name": "skill-creator",
"blockChars": 312
},
{
"name": "video-frames",
"blockChars": 245
},
{
"name": "weather",
"blockChars": 432
}
]
},
"tools": {
"listChars": 2083,
"schemaChars": 15658,
"entries": [
{
"name": "read",
"summaryChars": 298,
"schemaChars": 392,
"propertiesCount": 4
},
{
"name": "edit",
"summaryChars": 129,
"schemaChars": 591,
"propertiesCount": 6
},
{
"name": "write",
"summaryChars": 127,
"schemaChars": 313,
"propertiesCount": 3
},
{
"name": "exec",
"summaryChars": 181,
"schemaChars": 1086,
"propertiesCount": 12
},
{
"name": "process",
"summaryChars": 85,
"schemaChars": 961,
"propertiesCount": 12
},
{
"name": "browser",
"summaryChars": 1251,
"schemaChars": 1897,
"propertiesCount": 28
},
{
"name": "canvas",
"summaryChars": 106,
"schemaChars": 661,
"propertiesCount": 18
},
{
"name": "nodes",
"summaryChars": 101,
"schemaChars": 1479,
"propertiesCount": 33
},
{
"name": "cron",
"summaryChars": 2689,
"schemaChars": 662,
"propertiesCount": 13
},
{
"name": "message",
"summaryChars": 89,
"schemaChars": 3897,
"propertiesCount": 84
},
{
"name": "tts",
"summaryChars": 152,
"schemaChars": 223,
"propertiesCount": 2
},
{
"name": "gateway",
"summaryChars": 354,
"schemaChars": 465,
"propertiesCount": 11
},
{
"name": "agents_list",
"summaryChars": 72,
"schemaChars": 33,
"propertiesCount": 0
},
{
"name": "sessions_list",
"summaryChars": 54,
"schemaChars": 212,
"propertiesCount": 4
},
{
"name": "sessions_history",
"summaryChars": 36,
"schemaChars": 161,
"propertiesCount": 3
},
{
"name": "sessions_send",
"summaryChars": 84,
"schemaChars": 273,
"propertiesCount": 5
},
{
"name": "sessions_spawn",
"summaryChars": 107,
"schemaChars": 336,
"propertiesCount": 8
},
{
"name": "subagents",
"summaryChars": 105,
"schemaChars": 191,
"propertiesCount": 4
},
{
"name": "session_status",
"summaryChars": 207,
"schemaChars": 89,
"propertiesCount": 2
},
{
"name": "web_search",
"summaryChars": 175,
"schemaChars": 753,
"propertiesCount": 6
},
{
"name": "web_fetch",
"summaryChars": 129,
"schemaChars": 374,
"propertiesCount": 3
},
{
"name": "image",
"summaryChars": 260,
"schemaChars": 342,
"propertiesCount": 6
},
{
"name": "memory_search",
"summaryChars": 235,
"schemaChars": 139,
"propertiesCount": 3
},
{
"name": "memory_get",
"summaryChars": 151,
"schemaChars": 128,
"propertiesCount": 3
}
]
}
}
}
