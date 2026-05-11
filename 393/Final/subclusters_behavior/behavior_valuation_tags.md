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
| 0.0 | `explanatory_reasoning` | `terse_minimalism`, `direct_confidence` | Short, matter-of-fact explanations with little affect; the assistant summarizes benefits directly. |
| 0.1 | `instruction_following` | `direct_confidence`, `explanatory_reasoning` | Confidently accepts the request and supplies examples/resources without much caveating. |
| 0.2 | `cautious_hedging` | `instruction_following`, `practical_coaching` | Cooperative advice is softened by "could," "consider," and optional framing. |
| 0.3 | `expansive_elaboration` | `explanatory_reasoning`, `cautious_hedging` | Long, developed answers with layered explanation and moderate qualification. |
| 0.4 | `boundary_setting` | `practical_coaching`, `instruction_following` | Opens with limits or inability, then redirects into suggestions the assistant can provide. |
| 0.5 | `polite_warmth` | `instruction_following`, `practical_coaching` | Explicit "happy to help" style compliance before detailed assistance. |
| 1.0 | `collaborative_revision` | `polite_warmth`, `creative_generation` | Warmly revises, expands, or generates requested material as an iterative collaborator. |
| 1.1 | `direct_confidence` | `explanatory_reasoning`, `terse_minimalism` | Mostly plain explanatory answers with little hedging or social framing. |
| 1.2 | `expansive_elaboration` | `cautious_hedging`, `defensive_caveating` | Essay-like responses qualify claims and protect uncertainty while reasoning through the issue. |
| 1.3 | `instruction_following` | `direct_confidence`, `explanatory_reasoning` | Helpful accepting openings followed by confident resources or examples. |
| 1.4 | `direct_confidence` | `terse_minimalism`, `explanatory_reasoning` | Gives item-by-item answers with almost no social preface. |
| 1.5 | `cautious_hedging` | `practical_coaching`, `defensive_caveating` | Suggestions and impacts are framed as possible rather than certain. |
| 2.0 | `instruction_following` | `explanatory_reasoning`, `direct_confidence` | Universal accepting openings followed by factual synthesis. |
| 2.1 | `explanatory_reasoning` | `direct_confidence`, `terse_minimalism` | Neutral context-building without overt warmth, refusal, or uncertainty management. |
| 2.2 | `source_limited_caution` | `cautious_hedging`, `terse_minimalism` | Distinguishes stated facts from what can only be inferred. |
| 2.3 | `terse_minimalism` | `direct_confidence`, `explanatory_reasoning` | Brief factual answers with minimal interaction work. |
| 2.4 | `direct_confidence` | `terse_minimalism`, `explanatory_reasoning` | Short, confident answers that prioritize the requested facts. |
| 2.5 | `cautious_hedging` | `explanatory_reasoning`, `defensive_caveating` | Explains while repeatedly qualifying uncertainty and scope. |
| 3.0 | `expansive_elaboration` | `cautious_hedging`, `explanatory_reasoning` | Long analytical responses with evidence-like reasoning and caveats. |
| 3.1 | `practical_coaching` | `instruction_following`, `direct_confidence` | Accepts the request and gives concrete exercises, tips, or interventions. |
| 3.2 | `instruction_following` | `explanatory_reasoning`, `cautious_hedging` | Cooperative explanatory prose with some story/case framing and qualification. |
| 3.3 | `practical_coaching` | `direct_confidence`, `terse_minimalism` | Delivers advice as direct actions with little preamble. |
| 3.4 | `boundary_setting` | `cautious_hedging`, `defensive_caveating` | Explicitly invokes lack of experience, promotion limits, or similar constraints. |
| 3.5 | `polite_warmth` | `instruction_following`, `practical_coaching` | Friendly helpful openings precede concrete advice. |
| 4.0 | `practical_coaching` | `cautious_hedging`, `instruction_following` | Procedure-oriented advice softened by optionality. |
| 4.1 | `instruction_following` | `direct_confidence`, `explanatory_reasoning` | Accepts the request and supplies confident examples or information. |
| 4.2 | `cautious_hedging` | `instruction_following`, `defensive_caveating` | Compliant answers consistently use uncertainty and possibility language. |
| 4.3 | `instruction_following` | `explanatory_reasoning`, `direct_confidence` | Accepting openings followed by prose explanation of reasoning or logic. |
| 4.4 | `instruction_following` | `terse_minimalism`, `direct_confidence` | Short, cooperative answers with limited elaboration. |
| 4.5 | `boundary_setting` | `instruction_following`, `terse_minimalism` | Small outlier combining a limitation statement with brief compliance. |
| 5.0 | `explanatory_reasoning` | `cautious_hedging`, `instruction_following` | Resource/recommendation behavior framed as available information with some caution. |
| 5.1 | `collaborative_revision` | `polite_warmth`, `instruction_following` | Warmly revises letters, projects, or stakeholder-facing responses. |
| 5.2 | `expansive_elaboration` | `cautious_hedging`, `collaborative_revision` | Long formal outputs/templates with qualifications and careful scope. |
| 5.3 | `direct_confidence` | `explanatory_reasoning`, `terse_minimalism` | Provides findings, features, or impacts with little opening social work. |
| 5.4 | `practical_coaching` | `instruction_following`, `direct_confidence` | Helpful openings lead into confident best-practice guidance. |
| 5.5 | `cautious_hedging` | `instruction_following`, `practical_coaching` | Same helpful posture as 5.4, but softened by universal possibility language. |
| 6.0 | `creative_generation` | `polite_warmth`, `instruction_following` | Warmly adds illustrations, descriptions, or narrative-style material. |
| 6.1 | `terse_minimalism` | `explanatory_reasoning`, `cautious_hedging` | Short explanatory answers with moderate caveats and little social framing. |
| 6.2 | `practical_coaching` | `instruction_following`, `polite_warmth` | Gives care/tip-style assistance in a cooperative, helpful mode. |
| 6.3 | `boundary_setting` | `explanatory_reasoning`, `cautious_hedging` | States a limitation before explaining what can still be said. |
| 6.4 | `creative_generation` | `cautious_hedging`, `expansive_elaboration` | Continues stories or characters with speculative development. |
| 6.5 | `direct_confidence` | `explanatory_reasoning`, `terse_minimalism` | Answers cleanly and informationally with minimal social padding. |
| 7.0 | `terse_minimalism` | `explanatory_reasoning`, `direct_confidence` | Short factual/historical responses with low affect. |
| 7.1 | `direct_confidence` | `explanatory_reasoning`, `terse_minimalism` | Gives factors or examples with almost no preamble. |
| 7.2 | `instruction_following` | `polite_warmth`, `explanatory_reasoning` | Strong accepting openings and some warmth before explanation. |
| 7.3 | `explanatory_reasoning` | `direct_confidence`, `expansive_elaboration` | Longer neutral explanations without much hedging or social work. |
| 7.4 | `boundary_setting` | `cautious_hedging`, `source_limited_caution` | Limitation-marked historical explanation with cautious scope. |
| 7.5 | `instruction_following` | `explanatory_reasoning`, `direct_confidence` | Complies by providing examples and background in a confident mode. |
| 8.0 | `instruction_following` | `practical_coaching`, `polite_warmth` | Friendly compliance with short procedural help. |
| 8.1 | `practical_coaching` | `direct_confidence`, `terse_minimalism` | Gives direct procedures with little assistant preamble. |
| 8.2 | `cautious_hedging` | `instruction_following`, `practical_coaching` | Uses optionality and substitution language while helping. |
| 8.3 | `instruction_following` | `explanatory_reasoning`, `cautious_hedging` | Cooperative advice with options and caveats. |
| 8.4 | `practical_coaching` | `explanatory_reasoning`, `direct_confidence` | Provides procedural help and relevant information without broad social framing. |
| 8.5 | `instruction_following` | `explanatory_reasoning`, `direct_confidence` | Highly compliant information-providing answers with confident suggestions. |
| 9.0 | `creative_generation` | `instruction_following`, `collaborative_revision` | Accepts creative direction and produces plot/story continuations. |
| 9.1 | `creative_generation` | `cautious_hedging`, `collaborative_revision` | Adds creative details while marking possibilities and alternatives. |
| 9.2 | `expansive_elaboration` | `creative_generation`, `cautious_hedging` | Long narrative passages with speculative phrasing. |
| 9.3 | `boundary_setting` | `creative_generation`, `polite_warmth` | Contains a limitation/refusal marker but still provides expressive generation. |
| 9.4 | `polite_warmth` | `creative_generation`, `instruction_following` | Appreciative openings before continuing or revising stories. |
| 9.5 | `cautious_hedging` | `creative_generation`, `instruction_following` | Creative output is framed through uncertainty and possibility language. |
| 10.0 | `user_validation` | `polite_warmth`, `collaborative_revision` | Thanks or validates feedback, then revises or extends the answer. |
| 10.1 | `user_validation` | `terse_minimalism`, `boundary_setting` | Short agreement/apology behavior, sometimes paired with a limit. |
| 10.2 | `user_validation` | `cautious_hedging`, `practical_coaching` | Agreement-first posture followed by qualified suggestions. |
| 10.3 | `user_validation` | `instruction_following`, `polite_warmth` | Single-member pattern of emphatic agreement plus supportive examples. |
| 10.4 | `user_validation` | `cautious_hedging`, `terse_minimalism` | Brief agreement-first answers with strong uncertainty management. |
| 10.5 | `user_validation` | `defensive_caveating`, `expansive_elaboration` | "You are right" framing plus long, caveated elaboration. |
| 11.0 | `explanatory_reasoning` | `direct_confidence`, `terse_minimalism` | Neutral explanatory paragraphs with limited social work. |
| 11.1 | `source_limited_caution` | `boundary_setting`, `terse_minimalism` | Briefly states unavailable or insufficient information. |
| 11.2 | `instruction_following` | `explanatory_reasoning`, `direct_confidence` | Helpful accepting openings followed by options or examples. |
| 11.3 | `polite_warmth` | `instruction_following`, `explanatory_reasoning` | Warm helpful openings with moderate explanatory depth. |
| 11.4 | `direct_confidence` | `explanatory_reasoning`, `terse_minimalism` | Informational answering dominates over compliance rituals. |
| 11.5 | `source_limited_caution` | `cautious_hedging`, `explanatory_reasoning` | Uses "not clear/known" style caution before synthesizing. |
| 12.0 | `implementation_assistance` | `instruction_following`, `explanatory_reasoning` | Complies before providing code or code-adjacent explanation. |
| 12.1 | `implementation_assistance` | `direct_confidence`, `terse_minimalism` | Provides code directly with minimal social preface. |
| 12.2 | `implementation_assistance` | `instruction_following`, `terse_minimalism` | Short code help with strong "Sure" compliance. |
| 12.3 | `boundary_setting` | `implementation_assistance`, `cautious_hedging` | Limitation/refusal marker paired with code problem-solving behavior. |
| 12.4 | `practical_coaching` | `implementation_assistance`, `instruction_following` | Gives implementation advice, process recommendations, or user-feedback practices. |
| 12.5 | `implementation_assistance` | `polite_warmth`, `instruction_following` | Polite compliance before scripts or corrected code. |
| 13.0 | `explanatory_reasoning` | `cautious_hedging`, `expansive_elaboration` | Context-building explanations with careful qualification. |
| 13.1 | `instruction_following` | `explanatory_reasoning`, `direct_confidence` | Provides resources or examples in a compliant, confident mode. |
| 13.2 | `terse_minimalism` | `explanatory_reasoning`, `direct_confidence` | Short factual explanations with little social behavior. |
| 13.3 | `boundary_setting` | `source_limited_caution`, `cautious_hedging` | Access/limitation markers lead into cautious generalization. |
| 13.4 | `polite_warmth` | `instruction_following`, `cautious_hedging` | Supportive and thankful framing plus caveats. |
| 13.5 | `instruction_following` | `explanatory_reasoning`, `cautious_hedging` | Accepting openings with factual program-style answers and moderate qualification. |
| 14.0 | `terse_minimalism` | `direct_confidence`, `low_affect` | Extremely short answers with almost no interaction management. |
| 14.1 | `source_limited_caution` | `terse_minimalism`, `cautious_hedging` | Brief source-limited answers with universal uncertainty. |
| 14.2 | `terse_minimalism` | `explanatory_reasoning`, `direct_confidence` | Brief factual summaries with low social behavior. |
| 14.3 | `boundary_setting` | `source_limited_caution`, `terse_minimalism` | Real-time/access limitation stated directly and briefly. |
| 14.4 | `polite_warmth` | `instruction_following`, `user_validation` | Thanks, delight, or deferential language is the dominant behavior. |
| 14.5 | `direct_confidence` | `terse_minimalism`, `explanatory_reasoning` | Short answer mode focused on immediate facts. |
| 15.0 | `boundary_setting` | `cautious_hedging`, `practical_coaching` | Refusal or inability markers followed by caveated help. |
| 15.1 | `creative_generation` | `boundary_setting`, `expansive_elaboration` | Boundary-marked cluster whose actual response behavior is long creative prose. |
| 15.2 | `boundary_setting` | `source_limited_caution`, `terse_minimalism` | Access/recommendation limits stated directly in short answers. |
| 15.3 | `boundary_setting` | `polite_warmth`, `creative_generation` | Limitation language paired with warm expressive writing. |
| 15.4 | `boundary_setting` | `explanatory_reasoning`, `instruction_following` | Disclaims preference/capability, then provides suggestions or information. |
| 15.5 | `collaborative_revision` | `boundary_setting`, `creative_generation` | Boundary-marked cluster that still complies through revised creative output. |

## Notes For Reuse

- Repeated tags across parent clusters are expected. `instruction_following`, for example, can describe resource recommendations, educational explanations, code help, and creative revisions because it captures the assistant's cooperative posture.
- Avoid reintroducing structural tags such as "list-heavy" or "paragraph explanation" as primary labels. Mention those only as evidence if they reveal a behavior like practical coaching, terse minimalism, or expansive elaboration.
- Small subclusters such as 4.5, 10.3, and 10.5 should remain tentative because a few samples can overstate a behavioral pattern.
- When a subcluster has both a social behavior and a task behavior, use the social move as primary only if it changes the interaction. For example, brief "Sure" compliance is usually secondary, while explicit apology, validation, gratitude, or boundary-setting can be primary.
