# Behavior-Oriented Valuation Tags

This framework tags subclusters by assistant behavior rather than topic, answer format, or semantic domain. A tag should describe the interaction move the assistant is making: complying, reassuring, hedging, setting a boundary, giving practical direction, validating the user, generating creatively, or answering with terse confidence. Formatting evidence such as bullets or headings can support a judgment, but should not be the tag itself.

## Core Tag Set

- `instruction_following`: Accepts the user's task and carries it out in a cooperative, low-friction way.
- `polite_warmth`: Adds explicit friendliness, gratitude, enthusiasm, or "happy to help" affect.
- `direct_confidence`: Answers with certainty and little social padding or uncertainty management.
- `cautious_hedging`: Uses uncertainty, caveats, conditionals, or "could/may/might" framing to avoid overclaiming.
- `boundary_setting`: States limits, lack of access, lack of personal experience, inability, or refusal-like constraints.
- `practical_coaching`: Gives concrete next steps, recommendations, methods, or implementation advice.
- `explanatory_reasoning`: Builds context, causal logic, comparisons, or background to help the user understand.
- `expansive_elaboration`: Develops a long, comprehensive answer with multiple layers of reasoning or detail.
- `creative_generation`: Produces or revises expressive material such as stories, scripts, pitches, letters, or imagined scenes.
- `collaborative_revision`: Treats the user request as an iterative edit, expansion, or improvement to prior material.
- `user_validation`: Explicitly agrees with, acknowledges, thanks, apologizes to, or validates the user's point before continuing.
- `source_limited_caution`: Separates known information from inference, often because evidence is incomplete or unavailable.
- `terse_minimalism`: Gives a short answer with little framing, affect, or scaffolding.
- `low_affect`: Avoids warmth, validation, enthusiasm, apology, or expressive tone.
- `implementation_assistance`: Produces code, code-adjacent explanation, debugging help, or implementation guidance.
- `defensive_caveating`: Protects the answer from critique by justifying assumptions, narrowing claims, or emphasizing uncertainty.

## Tagging Rules

- Prefer behavior over shape. For example, a numbered list of tips is usually `practical_coaching` or `instruction_following`, not a list/structure tag.
- Prefer interaction posture over subject matter. Environmental, educational, code, travel, or story content should not become tags unless it changes the assistant's behavior.
- Use `instruction_following` when the main signal is compliance with the user's requested transformation, expansion, or answer.
- Use `practical_coaching` when the answer pushes the user toward action, process, or next steps.
- Use `cautious_hedging`, `source_limited_caution`, or `defensive_caveating` when the answer manages uncertainty. `source_limited_caution` is evidence-focused; `defensive_caveating` is stance-protective.
- Use `boundary_setting` only when the assistant explicitly invokes a limitation or refusal-like constraint.
- Use `user_validation` when the assistant first aligns with the user's critique, feedback, or correction.
- Secondary tags should capture modifiers of the primary behavior: warm, cautious, direct, creative, practical, terse, or boundary-aware.

## Cross-Cluster Patterns

The strongest recurring behaviors are `instruction_following`, `practical_coaching`, `explanatory_reasoning`, and `cautious_hedging`. These appear across unrelated subject areas because they describe how the assistant behaves, not what it talks about. Many subclusters that were previously separated by list or paragraph structure are now separated by posture: warm compliance, direct confidence, cautious advice, boundary-aware assistance, creative generation, or user-validating revision.

## Subcluster Matrix

| Subcluster | Primary behavior | Secondary behaviors | Behavioral evidence |
|---|---|---|---|
| 0.0 | `source_limited_caution` | `cautious_hedging`, `explanatory_reasoning` | Universal uncertainty, no social opening, and many "unfortunately/however/not enough information" style answers. |
| 0.1 | `instruction_following` | `cautious_hedging`, `explanatory_reasoning` | Universal accepting openings plus universal uncertainty; examples comply while staying qualified. |
| 0.2 | `cautious_hedging` | `explanatory_reasoning`, `defensive_caveating` | No social framing, universal "could/however/while" qualification, and explanatory synthesis. |
| 0.3 | `source_limited_caution` | `cautious_hedging`, `explanatory_reasoning` | Universal information-opening language such as "based/according" paired with universal uncertainty. |
| 0.4 | `terse_minimalism` | `cautious_hedging`, `source_limited_caution` | Shortest cautious cluster; brief answers hedge or point to missing context. |
| 0.5 | `practical_coaching` | `cautious_hedging`, `explanatory_reasoning` | Universal uncertainty plus concrete procedures, recommendations, and option-style help. |
| 1.0 | `practical_coaching` | `direct_confidence`, `terse_minimalism` | Short confident lists of actions, additions, or options with no hedging. |
| 1.1 | `practical_coaching` | `explanatory_reasoning`, `direct_confidence` | Fully practical, confident guidance with moderate explanation and no social padding. |
| 1.2 | `practical_coaching` | `expansive_elaboration`, `explanatory_reasoning` | Long stepwise/action-oriented answers about creating, adding, or organizing material. |
| 1.3 | `practical_coaching` | `instruction_following`, `explanatory_reasoning` | Confident list-form help with many add/create/improve moves. |
| 1.4 | `direct_confidence` | `practical_coaching`, `explanatory_reasoning` | Confident applied answers without hedging or social ritual. |
| 1.5 | `expansive_elaboration` | `practical_coaching`, `explanatory_reasoning` | Longest non-code practical cluster; develops multi-step plans or comprehensive guidance. |
| 2.0 | `instruction_following` | `cautious_hedging`, `practical_coaching` | Universal helpful/informative openings plus universal uncertainty and practical advice. |
| 2.1 | `instruction_following` | `practical_coaching`, `explanatory_reasoning` | Universal helpful/informative openings with confident suggestions and examples. |
| 2.2 | `instruction_following` | `cautious_hedging`, `explanatory_reasoning` | Helpful openings and universal uncertainty; answers explain while qualifying. |
| 2.3 | `instruction_following` | `direct_confidence`, `explanatory_reasoning` | Prose responses with universal helpful/informative openings and little hedging. |
| 2.4 | `instruction_following` | `practical_coaching`, `terse_minimalism` | Short confident suggestions, additions, or examples after "sure/here" openings. |
| 2.5 | `creative_generation` | `instruction_following`, `explanatory_reasoning` | Helpful prose dominated by narrative/character terms such as she/her/he/had. |
| 3.0 | `user_validation` | `boundary_setting`, `creative_generation` | Tiny cluster with universal validation plus refusal markers and narrative-style samples. |
| 3.1 | `user_validation` | `terse_minimalism`, `direct_confidence` | Short agreement-first answers with little hedging or additional framing. |
| 3.2 | `user_validation` | `creative_generation`, `cautious_hedging` | Validation-first narrative/prose answers with very high uncertainty. |
| 3.3 | `user_validation` | `implementation_assistance`, `direct_confidence` | Single code-heavy validation case; keep tentative. |
| 3.4 | `user_validation` | `polite_warmth`, `practical_coaching` | Validation is universal, with frequent warmth and applied suggestions. |
| 3.5 | `user_validation` | `instruction_following`, `cautious_hedging` | Validation plus helpful openings and high uncertainty. |
| 4.0 | `creative_generation` | `instruction_following`, `explanatory_reasoning` | Accepting openings before narrative or character-centered continuation. |
| 4.1 | `creative_generation` | `direct_confidence`, `explanatory_reasoning` | Narrative-heavy prose with no hedging or social opening. |
| 4.2 | `creative_generation` | `expansive_elaboration`, `explanatory_reasoning` | Long narrative/character development dominated by she/her/had terms. |
| 4.3 | `creative_generation` | `instruction_following`, `direct_confidence` | Helpful openings before concise narrative or content continuation. |
| 4.4 | `direct_confidence` | `explanatory_reasoning`, `low_affect` | Neutral confident prose with no hedging, refusal, or social framing. |
| 4.5 | `expansive_elaboration` | `creative_generation`, `explanatory_reasoning` | Very long developed prose, often narrative or scenario continuation. |
| 5.0 | `creative_generation` | `cautious_hedging`, `expansive_elaboration` | Long helpful narrative/prose answers with universal uncertainty. |
| 5.1 | `practical_coaching` | `cautious_hedging`, `expansive_elaboration` | Long list-based recommendations with universal caveats. |
| 5.2 | `practical_coaching` | `cautious_hedging`, `explanatory_reasoning` | Action-oriented advice with universal uncertainty and moderate depth. |
| 5.3 | `creative_generation` | `expansive_elaboration`, `cautious_hedging` | Longest narrative/prose cluster with universal uncertainty. |
| 5.4 | `source_limited_caution` | `instruction_following`, `cautious_hedging` | Based/according-style openings, universal uncertainty, and narrative/explanatory synthesis. |
| 5.5 | `creative_generation` | `instruction_following`, `cautious_hedging` | Helpful prose with narrative terms and universal uncertainty. |
| 6.0 | `practical_coaching` | `instruction_following`, `direct_confidence` | Universal helpful openings and concise confident recipes, additions, or steps. |
| 6.1 | `practical_coaching` | `instruction_following`, `cautious_hedging` | Helpful practical answers with universal uncertainty. |
| 6.2 | `practical_coaching` | `instruction_following`, `explanatory_reasoning` | Confident helpful guidance with moderate detail and no hedging. |
| 6.3 | `practical_coaching` | `terse_minimalism`, `instruction_following` | Shortest practical/helpful cluster, often recipes or quick suggestions. |
| 6.4 | `practical_coaching` | `cautious_hedging`, `instruction_following` | Helpful suggestions with universal "could" optionality. |
| 6.5 | `practical_coaching` | `instruction_following`, `direct_confidence` | Confident helpful lists of additions, options, or advice. |
| 7.0 | `polite_warmth` | `creative_generation`, `cautious_hedging` | Universal politeness and uncertainty with narrative/prose terms. |
| 7.1 | `polite_warmth` | `practical_coaching`, `cautious_hedging` | Warm, helpful, information-opening practical advice with universal uncertainty. |
| 7.2 | `polite_warmth` | `creative_generation`, `expansive_elaboration` | Long warm narrative/prose answers with universal uncertainty. |
| 7.3 | `polite_warmth` | `source_limited_caution`, `cautious_hedging` | Warm requests for information or caveated replies; short and uncertainty-heavy. |
| 7.4 | `polite_warmth` | `practical_coaching`, `cautious_hedging` | Warm list-based advice with universal uncertainty. |
| 7.5 | `polite_warmth` | `creative_generation`, `cautious_hedging` | Warm first-person/narrative prose with universal uncertainty. |
| 8.0 | `implementation_assistance` | `instruction_following`, `explanatory_reasoning` | Code blocks are universal; helpful openings and examples dominate. |
| 8.1 | `implementation_assistance` | `direct_confidence`, `terse_minimalism` | Code-focused direct answers with little social framing. |
| 8.2 | `implementation_assistance` | `instruction_following`, `explanatory_reasoning` | Code generation/explanation with helpful openings and moderate detail. |
| 8.3 | `implementation_assistance` | `polite_warmth`, `instruction_following` | Code-heavy answers with universal politeness and frequent helpful openings. |
| 8.4 | `implementation_assistance` | `instruction_following`, `direct_confidence` | Direct code assistance with universal helpful openings. |
| 8.5 | `boundary_setting` | `implementation_assistance`, `source_limited_caution` | Code-heavy outlier with universal refusal markers and access/limit behavior. |
| 9.0 | `boundary_setting` | `source_limited_caution`, `low_affect` | Universal refusal/access limits, brief explanatory redirection, little warmth. |
| 9.1 | `boundary_setting` | `terse_minimalism`, `source_limited_caution` | Shortest access-limit cluster; mostly "no/specific information unavailable" behavior. |
| 9.2 | `boundary_setting` | `polite_warmth`, `source_limited_caution` | Access limits paired with polite requests for more specific information. |
| 9.3 | `boundary_setting` | `cautious_hedging`, `source_limited_caution` | Universal refusal/access language with universal uncertainty. |
| 9.4 | `boundary_setting` | `practical_coaching`, `terse_minimalism` | Limitation statements followed by short option lists or redirects. |
| 9.5 | `boundary_setting` | `instruction_following`, `direct_confidence` | Limitation-marked cluster with strong helpful openings and concise redirection. |
| 10.0 | `polite_warmth` | `creative_generation`, `instruction_following` | Universal warmth/helpfulness before narrative or prose continuation. |
| 10.1 | `polite_warmth` | `instruction_following`, `explanatory_reasoning` | Warm helpful information-opening answers with confident explanation. |
| 10.2 | `polite_warmth` | `terse_minimalism`, `instruction_following` | Short warm replies, often thanks/happy-to-help style. |
| 10.3 | `polite_warmth` | `user_validation`, `terse_minimalism` | Warm personal or conversational replies with thanks/name language. |
| 10.4 | `polite_warmth` | `practical_coaching`, `instruction_following` | Warm, helpful practical guidance and suggestions. |
| 10.5 | `polite_warmth` | `expansive_elaboration`, `explanatory_reasoning` | Longer warm prose, often names/company/person-centered content. |
| 11.0 | `practical_coaching` | `cautious_hedging`, `explanatory_reasoning` | Information-opening practical guidance with universal uncertainty. |
| 11.1 | `explanatory_reasoning` | `practical_coaching`, `direct_confidence` | Confident information-opening examples or recommendations. |
| 11.2 | `direct_confidence` | `explanatory_reasoning`, `terse_minimalism` | Confident information-opening answers with short examples. |
| 11.3 | `source_limited_caution` | `explanatory_reasoning`, `direct_confidence` | Based/according-style factual answers with no social opening. |
| 11.4 | `terse_minimalism` | `direct_confidence`, `explanatory_reasoning` | Short information-opening examples or additions. |
| 11.5 | `expansive_elaboration` | `explanatory_reasoning`, `practical_coaching` | Longer information-opening explanations with step/data/learning terms. |
| 12.0 | `terse_minimalism` | `source_limited_caution`, `direct_confidence` | Very short according/text-based answers. |
| 12.1 | `terse_minimalism` | `direct_confidence`, `low_affect` | Very short yes/sure factual answers with little affect. |
| 12.2 | `boundary_setting` | `terse_minimalism`, `source_limited_caution` | Single tiny limitation outlier; keep tentative. |
| 12.3 | `polite_warmth` | `terse_minimalism`, `cautious_hedging` | Short polite replies with some information requests or caveats. |
| 12.4 | `terse_minimalism` | `direct_confidence`, `low_affect` | Extremely short yes/no style answers. |
| 12.5 | `cautious_hedging` | `terse_minimalism`, `polite_warmth` | Short replies with universal uncertainty and occasional glad/help framing. |
| 13.0 | `direct_confidence` | `explanatory_reasoning`, `low_affect` | Neutral concise factual/prose answers with no hedging or social framing. |
| 13.1 | `terse_minimalism` | `direct_confidence`, `explanatory_reasoning` | Short confident factual/prose answers. |
| 13.2 | `practical_coaching` | `terse_minimalism`, `direct_confidence` | Short applied tips/options, often recipe-like. |
| 13.3 | `instruction_following` | `direct_confidence`, `explanatory_reasoning` | Helpful openings before concise confident answers. |
| 13.4 | `source_limited_caution` | `direct_confidence`, `explanatory_reasoning` | According/based factual answers with evidence-oriented framing. |
| 13.5 | `terse_minimalism` | `direct_confidence`, `low_affect` | Very concise factual answers with little social or uncertainty behavior. |
| 14.0 | `boundary_setting` | `polite_warmth`, `creative_generation` | Universal refusal markers plus universal politeness; long narrative/prose continuations. |
| 14.1 | `boundary_setting` | `creative_generation`, `cautious_hedging` | Boundary-marked long narrative/prose answers with high uncertainty. |
| 14.2 | `boundary_setting` | `creative_generation`, `explanatory_reasoning` | Boundary-marked prose with some helpful redirection. |
| 14.3 | `boundary_setting` | `polite_warmth`, `creative_generation` | Boundary and politeness markers in personal/narrative prose. |
| 14.4 | `boundary_setting` | `polite_warmth`, `practical_coaching` | Boundary-marked warm list guidance with frequent caveats. |
| 14.5 | `boundary_setting` | `polite_warmth`, `source_limited_caution` | Boundary, politeness, information openings, and high uncertainty all co-occur. |
| 15.0 | `boundary_setting` | `practical_coaching`, `cautious_hedging` | Universal refusal markers plus list-based caveated suggestions. |
| 15.1 | `boundary_setting` | `polite_warmth`, `creative_generation` | Tiny warm boundary cluster with expressive first-person/life language. |
| 15.2 | `boundary_setting` | `source_limited_caution`, `practical_coaching` | Boundary plus information-opening practical or data/create guidance. |
| 15.3 | `boundary_setting` | `instruction_following`, `practical_coaching` | Universal boundary behavior but strong helpful/information openings and suggestions. |
| 15.4 | `boundary_setting` | `source_limited_caution`, `explanatory_reasoning` | Boundary plus provide/according-style factual redirection. |
| 15.5 | `boundary_setting` | `practical_coaching`, `expansive_elaboration` | Boundary-marked longer list guidance with user/create/process terms. |

## Notes For Reuse

- Repeated tags across parent clusters are expected. `instruction_following`, for example, can describe resource recommendations, educational explanations, code help, and creative revisions because it captures the assistant's cooperative posture.
- Avoid reintroducing structural tags such as "list-heavy" or "paragraph explanation" as primary labels. Mention those only as evidence if they reveal a behavior like practical coaching, terse minimalism, or expansive elaboration.
- Small subclusters such as 4.5, 10.3, and 10.5 should remain tentative because a few samples can overstate a behavioral pattern.
- When a subcluster has both a social behavior and a task behavior, use the social move as primary only if it changes the interaction. For example, brief "Sure" compliance is usually secondary, while explicit apology, validation, gratitude, or boundary-setting can be primary.
