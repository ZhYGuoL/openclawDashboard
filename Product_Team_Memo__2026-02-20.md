# Notification Intelligence System — Measurement & Experimentation Review

---

## Executive Summary

- The product team is building a smart notification system with tiered delivery, burst protection, quiet hours, and user-controlled suppression — designed to reduce notification fatigue across iOS, Android, and Web.
- Five A/B experiments have been designed and staged across three launch phases, covering cold-start preference elicitation, burst protection visibility, suppression prompt UX, notification center IA, and transparency copy framing.
- A mandatory 4-week instrumentation-only baseline period precedes all experiments; no experiment runs without pre-established baselines, as retroactive data reconstruction is impossible.
- The full notification event schema (9 event types, covering the full created → evaluated → delivered → interacted lifecycle) must be locked before Phase 1 development freeze — this is the single highest-leverage pre-launch action.
- Key unresolved dependencies include: privacy/legal review of the `held_reason` inference field, support ticket linkage infrastructure for Experiment 2, feasibility of the hybrid notification center IA build, and a primary device heuristic for cross-device attribution.

---

## What We Decided

**1. Lock the Event Schema Before Phase 1 Ships**
Retroactive instrumentation is not possible. All 9 event types — `notification_created`, `notification_evaluated`, `notification_delivered`, `notification_interacted`, `notification_center_opened`, `suppression_prompt_shown`, `suppression_prompt_responded`, `burst_protection_fired`, and `settings_accessed` — must be fully instrumented before Phase 1 launches. Schema gaps mean permanently lost baseline data.

**2. Mandatory 4-Week Baseline Period Before Any Experiment Runs**
Without pre-established baselines, treatment effects cannot be separated from system-level trends. The baseline window is non-negotiable. Deliverables include: CTR by tier and category, current settings access rates, burst protection trigger rate distributions, and sample size inputs for all five experiments.

**3. Run Experiments 1 and 2 Simultaneously at Phase 1 Launch**
Experiment 1 (cold-start preference elicitation) targets new users; Experiment 2 (burst protection visibility) targets users experiencing burst protection events. The segments do not overlap and present no interference risk. Running in parallel compresses the overall measurement timeline without methodological compromise.

**4. Stage Experiments 3, 4, and 5 Into Phase 2 and Phase 3**
Experiment 3 (suppression prompt flow) requires post-Phase 1 baseline data to define meaningful thresholds. Experiment 4 (notification center IA hybrid) may require build work not yet scoped into Phase 1. Experiment 5 (transparency copy) is Phase 3 scope by design. Forcing these earlier creates analytical and engineering risk.

**5. Never Report Aggregate CTR in Isolation**
Simpson's Paradox is an explicit risk: aggregate CTR can appear to improve while high-value category CTR declines, if low-value volume grows. All CTR reporting must be segmented by notification tier and category from day one. This is a standing analytical standard, not experiment-specific guidance.

**6. Define Experiment 3 Success Criteria as Quality-Adjusted, Not Funnel-Based**
The win condition for Experiment 3 is a lower suppression reversal rate within 7 days — not a higher prompt acceptance rate. A lower acceptance rate paired with lower reversal rate is a better outcome than higher acceptance with high reversal. This framing must be pre-registered in the experiment brief before data collection begins, to prevent post-hoc reframing.

**7. Flag `held_reason` for Privacy/Legal Review Before Instrumentation**
The `held_reason` field contains implicit behavioral inference (e.g., inferred sleep state). This may carry privacy classification implications in certain jurisdictions. Legal review is a pre-instrumentation gate — not a post-launch cleanup task.

**8. Mandate 90-Day Follow-Up Reads for All Phase 1 Experiments**
Four-week experiment windows capture short-run effects. User habituation may erode or reverse those effects over time. Ninety-day follow-up reads are built into the experiment plan and must be calendared at launch, not added retroactively.

**9. Define a Primary Device Heuristic for Cross-Device Attribution Before Launch**
Users active on multiple devices create noise in notification interaction attribution. A documented primary device heuristic must be established and socialized before any experiment attribution is run, ensuring consistent comparability across all five experiments.

---

## What We Considered

**Cold-Start Preference Elicitation Approaches (Experiment 1)**
The team evaluated three approaches for bootstrapping notification preferences for new users: no onboarding (purely reactive, suppress/adapt over time), a lightweight in-app card asking users to rate notification categories, and a full onboarding flow requesting explicit preferences upfront. The risk with explicit onboarding is activation drop-off — longer flows are a known friction point. Onboarding completion rate was added as a guardrail metric to monitor this in real time.

**Burst Protection Visibility: Silence vs. Transparency (Experiment 2)**
Two philosophies were considered: make intelligent holding behavior invisible to avoid confusion, or surface it explicitly so users understand why notifications were delayed. The team chose to test explicit transparency (an in-app banner: "Some notifications were grouped to reduce interruptions") while monitoring whether visibility drives panic-settings behavior. The support contact rate among burst-protection users is the primary signal.

**Notification Center IA: History Log vs. Hybrid (Experiment 4)**
Design recommended a pure history log (chronological, read-only, unread state). An alternative hybrid IA — chronological with an explicit "needs attention" group at the top — was also considered. The hybrid is potentially more actionable but risks burying time-sensitive items for users arriving from notification CTAs. Task completion rate is the designated guardrail. Whether this experiment can run in Phase 1 or requires a Phase 2 build is still an open question.

**Transparency Copy Framing (Experiment 5)**
Three arms were considered: no transparency copy at all, technical framing ("Held by burst protection"), and user-readable framing ("Grouped to reduce interruptions — 3 notifications held"). The 3-arm design allows the team to isolate whether *any* transparency improves held-notification recovery, and separately whether *human-readable* framing outperforms *technical* framing. Held notification recovery rate is the primary metric; analysis should be segmented by notification tier, as transparency may matter more for high-tier holds.

**Experiment Infrastructure: Build vs. Defer**
The team discussed whether to build full experiment infrastructure (persistent assignment service, experiment-event join, holdout groups, support ticket linkage) before Phase 1 or defer to later phases. The decision was to build all infrastructure before Phase 1, as retroactive joins across different event pipelines are technically non-trivial and the data gaps from delayed infrastructure cannot be recovered.

---

## Risks & Unknowns

**Simpson's Paradox on CTR Aggregation**
Aggregate notification CTR can improve while CTR for high-value categories declines, if low-value category volume grows simultaneously. Never interpret aggregate CTR movement without tier and category segmentation.

**Novelty Effects Inflating Early Experiment Results**
New UI patterns — transparency cards, digest formats, hybrid IA — will show inflated engagement in the first two weeks as users explore. All experiments run a minimum of 3 weeks; week 1 and week 3 data should be analyzed separately to detect and discount novelty inflation.

**Selection Bias in Suppression Experiments**
Users who reach suppression prompt thresholds are definitionally low-engagers. Their behavior is not representative of the general user population. Experiment 3 results must be reported with this caveat and should not be extrapolated to the full user base.

**Cross-Device Notification Attribution Noise**
Users active on multiple devices will generate interaction attribution noise, particularly given known cross-device read-state sync difficulties. Without a documented primary device heuristic, experiment results will be inconsistent across runs. This is a pre-launch requirement, not an analytics refinement.

**`held_reason` Privacy Classification Risk**
This field implicitly records inferred behavioral states (e.g., inferred sleep). Several jurisdictions may require consent, restricted retention windows, or regional exclusions for this type of behavioral inference. Legal review must be completed before instrumentation ships — not after.

**Hybrid IA Build Feasibility (Experiment 4)**
The Experiment 4 treatment (hybrid notification center IA) may not be buildable within Phase 1 scope. If it cannot be scoped in, Experiment 4 must be explicitly deferred to Phase 2 or Phase 3. This cannot remain an open dependency — a go/no-go decision is required before Phase 1 planning closes.

**Long-Run Habituation Effects**
Four-week experiment windows are sufficient for short-run detection, but habituation may erode or reverse observed effects over 90 days. All Phase 1 experiment results should be treated as provisional until the 90-day follow-up is read.

**Support Ticket Linkage as a Cross-Team Dependency**
Experiment 2 requires joining support ticket data to product event data by user_id and topic category. This is a cross-team dependency involving Support Ops. If it is not resolved before launch, Experiment 2 results will be unreadable. Early coordination is critical.

---

## Next Steps

| Owner | Action | Target |
|---|---|---|
| Engineering (Data/Backend) | Finalize and lock the full notification event schema — all 9 event types, no fields dropped, no deferred instrumentation | Before Phase 1 development freeze |
| Data Engineering | Build persistent user-level experiment assignment service with holdout group support, joinable to notification events by user_id across pipelines | Before Phase 1 launch |
| Data Engineering | Establish support ticket linkage by user_id and topic category; coordinate with Support Ops | Before Experiment 2 launch |
| Analytics | Run 4-week baseline measurement period starting Week 0; deliver CTR by tier/category, settings access rate, burst protection distribution, and sample size inputs | Week 0–4 |
| Analytics | Define and document the primary device heuristic for cross-device users; circulate for PM and Engineering sign-off | Before any experiment attribution runs |
| Analytics | Pre-register Experiment 3 success criteria in the experiment brief — quality-adjusted acceptance (low reversal rate) is the win condition, not raw acceptance volume | Before Experiment 3 data collection begins |
| Analytics | Build all experiment dashboards with iOS/Android/Web platform segmentation from day one; no experiment results shared without platform breakdowns | At experiment activation |
| Analytics | Calendar 90-day follow-up reads for all Phase 1 experiments at time of launch | At Phase 1 launch |
| Legal/Privacy | Review `held_reason` field for privacy classification; rule on whether special handling is required (consent, restricted retention, regional exclusion) | Before instrumentation ships |
| PM | Define and get legal sign-off on data retention policy for all event types before instrumentation begins | Pre-instrumentation |
| PM + Design/Engineering | Deliver go/no-go on hybrid notification center IA (Experiment 4 treatment) for Phase 1 vs. post-Phase 1 scope | Before Phase 1 planning close |
| PM | Publish and distribute phased experiment roadmap to all stakeholders (Engineering, Design, Data, Support Ops) | Week 0 |
| PM | Add onboarding completion rate as a real-time guardrail metric to the Experiment 1 Treatment A brief | Before Experiment 1 activation |

---

## Metrics to Watch

### North Star
- **Notification interaction rate** — overall engagement with delivered notifications, segmented by tier and category (never aggregate only)

### Phase 1 Experiment Primary Metrics
- **Experiment 1 (Cold-Start):** Notification CTR at day 7 and day 30 for users who completed preference elicitation vs. control; guardrail: onboarding completion rate
- **Experiment 2 (Burst Protection Visibility):** Support contact rate (notification-related tickets) among users who experience burst protection events; guardrail: overall notification interaction rate

### Phase 2 Experiment Primary Metrics
- **Experiment 3 (Suppression Prompt Flow):** Suppression reversal rate within 7 days — lower reversal = higher quality acceptance; guardrail: prompt dismissal rate

### Phase 3 Experiment Primary Metrics
- **Experiment 4 (Notification Center IA):** Notification center session depth (items viewed per session); guardrail: task completion rate for users arriving from a notification CTA
- **Experiment 5 (Transparency Copy):** Held notification recovery rate, segmented by notification tier

### Ongoing Analytical Standards
- All CTR reporting segmented by **notification tier** and **category** — no aggregate-only reads
- All experiment results segmented by **platform (iOS / Android / Web)** from day one
- Week 1 vs. Week 3 **novelty effect comparison** for all new UI pattern experiments
- **90-day follow-up reads** scheduled for all Phase 1 experiments at time of launch
- **Suppression experiment results** flagged with selection bias caveat; not extrapolated to general population
