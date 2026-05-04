# Behavior-Oriented Valuation Tags

This tag-in analyzes subclusters by response behavior, not subject matter. Topic words in the samples were used only as evidence for how the assistant behaves: how it opens, structures, hedges, refuses, elaborates, or collaborates.

## Tag Set

- `agreeable_compliance`: Opens by accepting the task or aligning with the user's request.
- `polite_warmth`: Uses explicit social warmth, gratitude, delight, or "happy to help" phrasing.
- `informative_exposition`: Prioritizes explanation, background, comparison, or factual synthesis.
- `structured_enumeration`: Strong list, step, bullet, recipe, or option formatting.
- `hedged_caution`: Uses could/might/however, caveats, uncertainty, or source-limited inference.
- `boundary_disclaimer`: Explicitly states inability, lack of access, lack of personal experience, non-preference, or refusal-like limits.
- `actionable_guidance`: Gives procedural advice, concrete recommendations, next steps, or implementation tips.
- `concise_answering`: Short, direct response with little scaffolding or social framing.
- `deep_elaboration`: Long-form, essay-like, comprehensive development.
- `creative_continuation`: Continues, revises, or generates expressive material in response to the user's creative direction.
- `user_validation`: Explicitly agrees with, validates, or praises the user's point before answering.

## Cross-Cluster Patterns

The most reusable behavioral tags are `structured_enumeration`, `agreeable_compliance`, `informative_exposition`, and `hedged_caution`. These appear across many unrelated parent clusters because they describe answer style rather than content. Within the same parent cluster, repeated tags are separated by stricter secondary tags: for example, a list-heavy subcluster can be distinguished as confident, hedged, boundary-prefaced, warm, concise, or deeply elaborative. Some secondary tags are narrower behavior modifiers, not separate topic labels.

## Subcluster Matrix

| Subcluster | Primary valuation | Secondary valuations | Behavioral evidence |
|---|---|---|---|
| 0.0 | `informative_exposition` | `concise_answering`, `low_scaffold` | Short paragraph answers, few lists, low politeness/opening markers; samples summarize benefits directly. |
| 0.1 | `structured_enumeration` | `agreeable_compliance`, `informative_exposition` | Near-universal "Certainly/Sure, here are..." openings and list format; confident itemized examples. |
| 0.2 | `hedged_caution` | `structured_enumeration`, `agreeable_compliance` | List-heavy but every member has uncertainty markers; many "could work", "consider", optional suggestions. |
| 0.3 | `deep_elaboration` | `informative_exposition`, `moderate_hedging` | Longest subcluster in its parent group, more essay/proposal structure, lower compliance openings. |
| 0.4 | `structured_enumeration` | `boundary_disclaimer`, `actionable_guidance` | List format plus refusal/inability prefaces such as "I am not capable... however I can suggest". |
| 0.5 | `polite_warmth` | `agreeable_compliance`, `structured_enumeration` | Politeness markers are universal; "I'd be happy..." openings before detailed lists. |
| 1.0 | `polite_warmth` | `agreeable_compliance`, `collaborative_revision` | Warm "happy/glad" compliance and revised/generated copy, scripts, or expanded material. |
| 1.1 | `informative_exposition` | `concise_answering`, `low_scaffold` | Mostly paragraph explanations with limited list scaffolding and low uncertainty. |
| 1.2 | `deep_elaboration` | `hedged_caution`, `informative_exposition` | Essay-length answers with many caveats, qualifications, and comparative reasoning. |
| 1.3 | `structured_enumeration` | `agreeable_compliance`, `informative_exposition` | Confident examples/resources in list form with high compliance openings and little hedging. |
| 1.4 | `structured_enumeration` | `direct_answering`, `low_social_framing` | Almost all lists, almost no assistive openings, direct item-by-item explanation. |
| 1.5 | `hedged_caution` | `structured_enumeration`, `actionable_guidance` | Every sample contains uncertainty language; gives possible incentives, impacts, and options. |
| 2.0 | `agreeable_compliance` | `informative_exposition`, `concise_answering` | Universal accepting openings but paragraph-style factual summaries rather than lists. |
| 2.1 | `informative_exposition` | `neutral_tone`, `low_scaffold` | Explanatory paragraphs without list formatting, hedging, or overt agreement. |
| 2.2 | `hedged_caution` | `concise_answering`, `source_limited_inference` | Universal uncertainty markers; samples distinguish what is stated from what can be inferred. |
| 2.3 | `concise_answering` | `informative_exposition`, `low_social_framing` | Shortest nontrivial paragraph answers with minimal openings and no lists. |
| 2.4 | `structured_enumeration` | `concise_answering`, `informative_exposition` | Fully list-form answers, shorter than other enumerative clusters. |
| 2.5 | `hedged_caution` | `informative_exposition`, `moderate_elaboration` | Paragraph explanations with universal uncertainty/caveat behavior. |
| 3.0 | `deep_elaboration` | `hedged_caution`, `informative_exposition` | Long essay-style responses with evidence-style explanation and caveats. |
| 3.1 | `structured_enumeration` | `agreeable_compliance`, `actionable_guidance` | List-heavy "Sure/Certainly, here are..." advice with many practical exercises. |
| 3.2 | `agreeable_compliance` | `informative_exposition`, `hedged_caution` | Warm but mostly paragraph explanations, often story/case oriented and moderately hedged. |
| 3.3 | `structured_enumeration` | `actionable_guidance`, `low_social_framing` | Pure numbered tips with little opening agreement; instructions are the main behavior. |
| 3.4 | `boundary_disclaimer` | `structured_enumeration`, `hedged_caution` | Refusal/disclaimer markers are universal, usually about no personal experience or no promotion. |
| 3.5 | `polite_warmth` | `agreeable_compliance`, `actionable_guidance` | Universal warmth and helpful openings before practical advice. |
| 4.0 | `structured_enumeration` | `actionable_guidance`, `moderate_hedging` | Fully procedural step lists with some "can/may" optionality. |
| 4.1 | `structured_enumeration` | `agreeable_compliance`, `informative_exposition` | Universal list format and information openings; confident examples. |
| 4.2 | `hedged_caution` | `structured_enumeration`, `agreeable_compliance` | Universal uncertainty markers inside otherwise highly compliant lists. |
| 4.3 | `agreeable_compliance` | `informative_exposition`, `paragraph_explanation` | High compliance and information openings but no list format; explains logic in prose. |
| 4.4 | `structured_enumeration` | `concise_answering`, `agreeable_compliance` | Short itemized answers with "here are..." openings and limited elaboration. |
| 4.5 | `boundary_disclaimer` | `structured_enumeration`, `agreeable_compliance` | Tiny outlier; refusal marker plus list-form compliance, so keep separate from 4.1. |
| 5.0 | `informative_exposition` | `structured_enumeration`, `hedged_caution` | Resource/recommendation lists framed as available information, with some uncertainty. |
| 5.1 | `polite_warmth` | `agreeable_compliance`, `collaborative_revision` | Universal politeness in revision, letter, project, or stakeholder-facing responses. |
| 5.2 | `deep_elaboration` | `hedged_caution`, `formal_generation` | Long generated artifacts/templates with caveats and formal structure. |
| 5.3 | `structured_enumeration` | `informative_exposition`, `low_social_framing` | Lists of findings, features, or impacts with little opening compliance. |
| 5.4 | `agreeable_compliance` | `structured_enumeration`, `actionable_guidance` | Universal helpful openings and confident best-practice lists. |
| 5.5 | `hedged_caution` | `agreeable_compliance`, `structured_enumeration` | Same helpful list posture as 5.4 but universal "could/may" uncertainty. |
| 6.0 | `polite_warmth` | `agreeable_compliance`, `creative_continuation` | Warm compliance before adding illustrations, descriptions, or narrative material. |
| 6.1 | `concise_answering` | `informative_exposition`, `hedged_caution` | Short paragraph answers, low structure, moderate caveats. |
| 6.2 | `structured_enumeration` | `agreeable_compliance`, `actionable_guidance` | High list and information-opening rates; practical care/tip style. |
| 6.3 | `boundary_disclaimer` | `informative_exposition`, `hedged_caution` | Refusal marker outlier; often states limits before explaining. |
| 6.4 | `creative_continuation` | `hedged_caution`, `narrative_elaboration` | Paragraph storytelling, character continuation, and speculative development. |
| 6.5 | `structured_enumeration` | `informative_exposition`, `direct_answering` | Fully list-form explanations with minimal social framing. |
| 7.0 | `concise_answering` | `informative_exposition`, `low_social_framing` | Short historical/factual paragraphs, few lists, few openings. |
| 7.1 | `structured_enumeration` | `informative_exposition`, `direct_answering` | Fully listed factors/examples with almost no social preface. |
| 7.2 | `agreeable_compliance` | `informative_exposition`, `polite_warmth` | Very high compliance openings and some warmth, but mostly prose explanation. |
| 7.3 | `informative_exposition` | `moderate_elaboration`, `low_social_framing` | Longer neutral explanations with minimal hedging or list scaffolding. |
| 7.4 | `boundary_disclaimer` | `informative_exposition`, `hedged_caution` | Refusal marker outlier with caveated historical explanation. |
| 7.5 | `structured_enumeration` | `informative_exposition`, `agreeable_compliance` | List-heavy examples with high information openings. |
| 8.0 | `structured_enumeration` | `agreeable_compliance`, `concise_answering` | Short procedural lists with friendly compliance openings. |
| 8.1 | `structured_enumeration` | `actionable_guidance`, `low_social_framing` | Full procedure formatting, less assistant preamble. |
| 8.2 | `hedged_caution` | `structured_enumeration`, `agreeable_compliance` | Universal optionality and substitution language in list form. |
| 8.3 | `agreeable_compliance` | `informative_exposition`, `moderate_hedging` | Paragraph advice with some options and caveats, fewer lists. |
| 8.4 | `structured_enumeration` | `informative_exposition`, `direct_answering` | Procedural list response with information opening but little broad compliance. |
| 8.5 | `structured_enumeration` | `agreeable_compliance`, `informative_exposition` | Universal compliance and information openings; confident listed suggestions. |
| 9.0 | `creative_continuation` | `agreeable_compliance`, `narrative_generation` | Accepts creative direction and produces plot/story continuations. |
| 9.1 | `creative_continuation` | `agreeable_compliance`, `hedged_caution` | Adds character/detail revisions with high uncertainty/conditional language. |
| 9.2 | `deep_elaboration` | `creative_continuation`, `hedged_caution` | Long narrative passages with high speculative/uncertain phrasing. |
| 9.3 | `boundary_disclaimer` | `creative_continuation`, `polite_warmth` | Refusal marker outlier but still long creative generation. |
| 9.4 | `polite_warmth` | `creative_continuation`, `agreeable_compliance` | Universal warmth and appreciative openings before continuing stories. |
| 9.5 | `hedged_caution` | `creative_continuation`, `agreeable_compliance` | Creative/prose output with universal uncertainty markers. |
| 10.0 | `user_validation` | `polite_warmth`, `structured_enumeration` | Tiny cluster; explicitly thanks/validates feedback and then revises. |
| 10.1 | `user_validation` | `concise_answering`, `boundary_disclaimer` | Agreement/apology behavior with short response style. |
| 10.2 | `user_validation` | `structured_enumeration`, `hedged_caution` | Explicit agreement pattern plus list formatting and uncertainty. |
| 10.3 | `user_validation` | `agreeable_compliance`, `polite_warmth` | Single-member pattern: "Absolutely, I agree..." plus satisfied-customer examples. |
| 10.4 | `user_validation` | `hedged_caution`, `concise_answering` | Agreement-first short paragraphs with universal uncertainty. |
| 10.5 | `user_validation` | `boundary_disclaimer`, `deep_elaboration` | Explicit "You are right" plus long-form elaboration and refusal markers. |
| 11.0 | `informative_exposition` | `paragraph_explanation`, `low_social_framing` | Neutral explanatory paragraphs with limited lists or openings. |
| 11.1 | `concise_answering` | `boundary_disclaimer`, `source_limited_inference` | Short answers, many "unfortunately/no specific information" limits. |
| 11.2 | `structured_enumeration` | `agreeable_compliance`, `informative_exposition` | Helpful "Sure, here are..." list of options/examples. |
| 11.3 | `polite_warmth` | `agreeable_compliance`, `informative_exposition` | Warm helpful openings and moderate explanatory depth. |
| 11.4 | `structured_enumeration` | `informative_exposition`, `low_social_framing` | Near-universal lists, more informational than compliant. |
| 11.5 | `hedged_caution` | `informative_exposition`, `source_limited_inference` | Universal uncertainty; often "not clear/known" then cautious synthesis. |
| 12.0 | `agreeable_compliance` | `code_generation`, `informative_exposition` | High compliance before code/explanation, low list behavior. |
| 12.1 | `informative_exposition` | `code_generation`, `direct_answering` | Provides code directly with minimal compliance opening. |
| 12.2 | `agreeable_compliance` | `concise_answering`, `code_guidance` | Short code explanations with strong "Sure" compliance. |
| 12.3 | `boundary_disclaimer` | `code_generation`, `hedged_caution` | Refusal marker outlier with code/problem-solving explanation. |
| 12.4 | `structured_enumeration` | `actionable_guidance`, `code_guidance` | Fully list-based implementation advice and user-feedback practices. |
| 12.5 | `polite_warmth` | `agreeable_compliance`, `code_generation` | Universal politeness before scripts or corrected code. |
| 13.0 | `informative_exposition` | `deep_context`, `hedged_caution` | Context-building explanations, moderate length, low social scaffolding. |
| 13.1 | `structured_enumeration` | `agreeable_compliance`, `informative_exposition` | List-heavy resources with high information openings. |
| 13.2 | `concise_answering` | `informative_exposition`, `low_social_framing` | Short factual explanations with little structure. |
| 13.3 | `boundary_disclaimer` | `hedged_caution`, `informative_exposition` | Universal refusal/access-limit markers; cautious generalizing. |
| 13.4 | `polite_warmth` | `agreeable_compliance`, `hedged_caution` | Warm responses with thanks/supportive framing and caveats. |
| 13.5 | `agreeable_compliance` | `informative_exposition`, `moderate_hedging` | High accepting openings, lower list dependence, factual program-style answers. |
| 14.0 | `concise_answering` | `direct_answering`, `low_scaffold` | Extremely short answers with minimal tone or structure. |
| 14.1 | `hedged_caution` | `concise_answering`, `source_limited_inference` | Short source-limited answers; universal uncertainty. |
| 14.2 | `concise_answering` | `informative_exposition`, `low_social_framing` | Brief factual summaries, almost no list or social behavior. |
| 14.3 | `boundary_disclaimer` | `concise_answering`, `source_limited_inference` | Real-time/access limitation refusal, very short. |
| 14.4 | `polite_warmth` | `agreeable_compliance`, `deferential_response` | Universal politeness; thanks and delighted-to-help framing. |
| 14.5 | `structured_enumeration` | `concise_answering`, `direct_answering` | Short bullet-list answers. |
| 15.0 | `boundary_disclaimer` | `structured_enumeration`, `hedged_caution` | Universal refusal markers plus list format and caveats. |
| 15.1 | `boundary_disclaimer` | `creative_continuation`, `deep_elaboration` | Refusal-marker parent cluster but behavior is long creative/narrative prose. |
| 15.2 | `boundary_disclaimer` | `concise_answering`, `hedged_caution` | Access/recommendation limits stated directly in short responses. |
| 15.3 | `boundary_disclaimer` | `polite_warmth`, `creative_continuation` | Refusal marker plus universal warmth, often letters or expressive writing. |
| 15.4 | `boundary_disclaimer` | `structured_enumeration`, `informative_exposition` | Disclaims preferences/capability, then gives list-form suggestions. |
| 15.5 | `boundary_disclaimer` | `agreeable_compliance`, `creative_continuation` | Refusal-marker cluster with high compliance and revised creative output. |

## Notes For Reuse

- Repeated tags across top-level clusters are expected and useful. For example, `structured_enumeration` recurs in 0.1, 1.3, 3.1, 8.5, 11.2, and 13.1 even though their topics differ.
- Inside a parent cluster, repeated tags should be interpreted with secondary tags. For example, 8.1 and 8.5 are both `structured_enumeration`, but 8.1 is lower-social procedural formatting while 8.5 is highly agreeable and information-opening heavy.
- Small subclusters such as 4.5, 10.3, and 10.5 should be treated as tentative behavioral tags because sample count is low.
