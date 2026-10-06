# Use of AI tools

This statement follows the AAMAS 2027 policy on AI-assisted technologies. No AI tool is an author of the paper.

## Tool

Claude Code (Anthropic's command-line coding agent) with the model Claude Opus 5.5 (`claude-opus-5-5`), in three
sessions on 5 and 6 October 2026, during the revision of the paper for this submission. The sessions read and
modified the code of KRROOD and of the experiments, ran tests and experiments on a development machine, and drafted
and revised the text of the paper. The authors reviewed every change, decided what to keep, and ran the measured
experiments.

TODO-AUTHORS: state whether AI tools were used for the earlier version of the experiments (January 2026), and how.

## What the AI tool did

**Code and scripts** (permitted without disclosure, listed for completeness): corrections of Ontomatic's loader
(only sufficient conditions classify individuals; no relations guessed from shared properties; the OWL 2 RL/RDF rules
of Table 2, including the necessary conditions, the data-property rules and the check of the equality and
inconsistency rules), the translation of EQL queries over collection-valued attributes to SQL (Section 6), the
measurement scripts, the tests, and the Docker set-up of this supplementary material.

**Experimental design and methodology** (proposed by the AI tool and approved by the authors):

* the answer-set check: the answers of every system are normalized to sets of tuples and compared with GraphDB's
  answer set, instead of comparing the numbers of answers (Section 7.1);
* the assertion-by-assertion comparison of KRROOD's knowledge base with GraphDB's OWL 2 RL closure, and the check of
  the equality and inconsistency rules (Sections 5 and 7.1);
* GraphDB's OWL 2 RL closure as the reference, justified by Theorem PR1 of the OWL 2 Profiles specification and by
  the punning in OWL2Bench (Section 7);
* running every system in its own process, and measuring peak memory as the peak resident set size of the process
  tree sampled every 50 ms (for GraphDB, of its server);
* the two-hour limit of the ablation.

**Analysis and text**: the statements and proof sketches of Propositions 5.1 and 5.2 and Algorithm 1 were drafted
by the AI tool from the code and revised by the authors; the AI tool also drafted and revised other parts of the
text.

## Decisions of the authors

Given as comments on a revision plan written by the AI tool (verbatim, anchors shortened):

* On a measurement claim without data: "yes this should be definitly measured"; "attempt a quick measurement for the
  possible ones."
* On queries with empty answers that had been omitted: "what's the cleanest fix for these, I prefer if we can show
  the results instead of removing."
* On the claim that Pellet is complete: "well this has not been proven on this benchmark, check the OWL2Bench paper
  and reverify this."
* On a count-only result check: "which ones are you talking about, I think we do somewhere check the uris are the
  same."
* On the scope of Ontomatic: "we are targetting OWL RL, we can do some of DL but we haven't finished that. Whatever is
  required for RL and is not done correctly in the code needs to be modified to be done correctly [...]"
* On the code version to evaluate: "use the most correct version."

## Prompts

The prompts that shaped the experiments, verbatim except for redacted paths and names (marked [...]). The other
prompts of the sessions concerned the text of the paper, file transfers and version control.

> Ok this is going to be a big multi step multi repository task that includes code modifying, and paper writing, so
> I need a good multi step plan where each step is verified, reviewed and tested. We are modifying our KRROOD paper
> for submission to AAMAS 2027 conference in vietnam. [...] I want the krrood paper to focus on one theme and one
> application, and go in depth into the important parts that serve its arguments, the knowledge representation and
> reasoning and the experiments focus on how we represent knowledge that is represented in ontologies and how it is
> reasoned with in krrood. You do not have to take my comments as commands but as comments to be discussed and
> challenged and grounded in the literature. [...] Also discuss with me how to handle the deprecation (if we ever need
> to handle it) of the expriments with the current [code], maybe merge main and update the dl branch or just leave
> it as it is. Brainstorm and discuss with me.

> do the recommended approached, and do what you can do on this maching and I can run what is needed again in the
> original machine tomorrow, but make everything ready for it with steps and documentation. [...]

> Can you fix these? Provenance: recorded only for facts inferred through sub-properties and equivalent, inverse and
> symmetric properties, not for transitive, chain or type inferences. Connected-components step: its facts don't
> propagate further, now listed as a source of incompleteness. Rules: they create new objects on each evaluation, with
> no deduplication.

> yes do this, and can we fix the ResearchGroup incompleteness issue? discuss that with me please.

> Commit and push and tell me what to do to run the experiments in the pc, I prefer one command needed if possible.
> Also fix the issues you found.

> Yes go ahead (also make sure that these are really OWL 2 RL rule sets and are the ones the owl2bench benchmark
> expects for the RL profile).

> [Task for the review of the third draft, written by the AI tool at the authors' request and given to a new
> session:] Every claim must be true of the code and of what was measured: The experiments' SQL queries were
> hand-written with SQLAlchemy; they were not produced by the EQL-to-SQL translator. The translator [...] supports
> only a subset of EQL. Check what it supports before claiming anything about it. Any new performance claim needs a
> measurement or a citation.

> Also if space allows, you can do a easiniess and simplicity of queries between eql, sparql and sql. [...]
> [After the AI tool reported that the measured simplicity did not favor EQL:] Ok then leave it out.

> Do you think it's better if we make all this run in a docker? so add a docker script with all needed instructions
> and that's what we ship?

The complete session logs are kept by the authors.
