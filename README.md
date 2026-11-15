# GeometricNeuronV30 — The Order of Falls

**Fade-triggered units on a shared wave field: what five experiments showed on 15 November 2026.**

Antti Luode (direction and the picture being tested) · Sol / ChatGPT (built and ran experiments 001–005) · Fable 5.2 (analysis, independent re-run, this write-up)

This repository is a write-up, not a codebase. It is the nail on the wall for one day's round, so the result survives outside the working directory. The nodes, workflows, runners and numerical receipts live in:

- [anttiluode/PerceptionLabAI](https://github.com/anttiluode/PerceptionLabAI) — the working repo where the experiments were built and run
- [anttiluode/PerceptionLab](https://github.com/anttiluode/PerceptionLab) — the node laboratory itself

---

## Summary

A unit that fires **when its record of recent activity fades** was placed on a two-dimensional wave field and its pulse was written back into that field.

1. One unit and one field make a self-sustaining rhythm from a single starting pulse, with no clock.
2. Two units with different fade rates either **suppress** one another (the faster fader wins) or **take turns**, depending only on how strongly one of them writes back.
3. In the turn-taking regime the fast unit cannot keep itself going alone; it depends on the slow one. (Corrected after experiment 007: the dependence is one-way. See section 10.)
4. The order of two input pulses (A then B, or B then A) stays readable from the ongoing pulse trains long after the passive field has decayed below a stated measurement floor.
5. Adding a third active unit seemed to make that order harder to read. (With six times the test runs this did not hold up. See section 11.)

Nothing here is a new mechanism. It is a delayed-feedback relaxation oscillator, and the family is old. What the round adds is a controlled, reproducible ladder from "a wave carries an event" to "the past changes later pulse trains, and an outside reader can sometimes tell which past it was".

---

## 1. The picture being tested

The round began with this description (Antti, lightly edited):

> Imagine billions of neurons, each holding a little bit of wave. A little bit, like a token, that fires or not, influenced by other fading pulses with their own individuality. Now imagine music, or a scene: a complex wave. The brain learns little bits that can build up to a multimodal complex wave.

And later, after the first closed loop ran:

> A continual fall, leading to the next moment. Seen from outside, noise. Seen from inside, the past getting caught in signal trains, leading to new signal trains.

The experiments below are the smallest versions of those sentences that can be measured.

---

## 2. The two parts

### 2.1 The field

`WaveFieldNode` is a damped second-order wave equation on a square grid:

```math
\ddot F = c^2 \nabla^2 F - \gamma \dot F + \text{drive}
```

Every cell carries a value and a velocity. A local kick therefore travels, at $`c \times \text{substeps}`$ pixels per frame (here $`0.5 \times 4 = 2`$). Eight read apertures sit in a line at increasing distance from the source, and each aperture also has a write port.

An earlier first-order version of the field, $`\dot F = D\nabla^2 F - \gamma F`$, had failed: a kick died into one common mode with zero lag between apertures. That contrast is the subject of section 3.

### 2.2 The unit

`FadingHistorySpikeNode` keeps one number, a leaky trace of the absolute field value at its aperture:

```math
m_{t+1} = d \, m_t + (1-d)\,\lvert r_t \rvert
```

where $`r_t`$ is the aperture reading and $`d`$ is the decay (the unit's one self-weight).

- When $`m`$ rises above an **arm** threshold, the unit is armed.
- When $`m`$ then falls below a lower **release** threshold, the unit emits one fixed-size pulse and disarms.
- From silence it never fires.

The pulse is written into the field at a *different* aperture, so it has to travel to come back.

This node is a deliberately simple test component. It is **not** a port of the GeometricNeuron V26–V29 equations and not a model of an action potential. It takes one idea from that line, that a pulse is generated when the history fades, and isolates it.

---

## 3. Two ways to hold the past

### 3.1 Delay and decay

| | Where the past is kept | How age is read |
|---|---|---|
| **Delay** (wave field) | Spread out in space | *Where* a disturbance is tells you *when* it happened |
| **Decay** (the unit's trace, a dendritic cable) | In how much is left | *How much remains* tells you *how long ago* |

On a beach: the first is the wave running along the shore, the second is the wet sand drying.

A population of decay units with many different rates $`s`$ holds

```math
x_s(t) = \int_{-\infty}^{t} e^{-s(t-\tau)}\, u(\tau)\, d\tau
```

which is the Laplace transform of the recent input $`u`$. This is an existing theory of how a population can represent "what happened how long ago" (Shankar and Howard, 2012). "Each neuron holds a little bit of fading wave" has a mathematical form already.

### 3.2 Cable versus wave

Both live on the same graph, so they share the same spatial modes, with Laplacian eigenvalues $`\mu_k \ge 0`$. They differ in what time does to each mode:

```math
\text{cable:}\quad a_k(t) = a_k(0)\, e^{-(\gamma + D\mu_k)\,t}
```

```math
\text{wave:}\quad a_k(t) \approx a_k(0)\, e^{-\gamma t/2}\cos\!\left(c\sqrt{\mu_k}\; t\right)
```

Cable modes only fade. An event smears and shrinks and has no sharp arrival. Wave modes ring while they fade, so an event keeps a front and distance becomes delay. That is why the first-order field died into a common mode and the second-order field carries a lag.

### 3.3 Weights as a lag family

For a linear system $`\dot x = A x`$, the state evolves as $`x(t) = e^{At}x(0)`$, where $`A`$ is the weight matrix on the graph. The eigenvalues of $`A`$ are the ways of fading: the real part is how fast a mode dies, the imaginary part how fast it rings.

The effective weight from point $`i`$ to point $`j`$ at lag $`t`$ is

```math
W_{ji}(t) = \left[e^{At}\right]_{ji}
```

So one graph gives a different weight matrix for every lag, and a static weight matrix is that family frozen at one lag.

### 3.4 Lag matrices coupled by pings

The whole system of this round fits in one line. Between pulses the field evolves linearly. At a pulse, a fixed stamp $`b_k`$ is added at unit $`k`$'s write site:

```math
x(t_{n+1}) = e^{A\,(t_{n+1}-t_n)}\,\bigl(x(t_n) + b_{k_n}\bigr)
```

The next time $`t_{n+1}`$ and the next unit $`k_{n+1}`$ are decided by a **race**: whichever armed unit's trace falls to its release threshold first. Each pulse resets the race for the others by refilling their traces.

So the state is carried forward by lag matrices, and the pings are what couple one stretch to the next. The field part is exactly linear; the traces are a rectified leaky readout of it, and the race is where the nonlinearity lives.

---

## 4. The experiments

All five were built and run by Sol in PerceptionLabAI on 15 November 2026, using the real upstream `WaveFieldNode` and `PulseSourceNode` classes under a headless shim. Each links to its own report with full methods and controls.

### 001 — Wave transit as a causal-age readout
[Report](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/001_causal_age)

Does a near aperture at $`t-D`$ predict a far aperture at $`t`$ better than the near aperture at $`t`$ does?

- Headless (128×128, $`D=7`$): mean advantage **+11.9 dB** for the delayed predictor; the zero-delay control gave exactly 0 dB.
- In the GUI (256×256): predicted lag 13.2 frames per gap. The scope measured a mean lag of 22.2 frames over six aperture pairs spanning on average 10/6 gaps, and $`13.2 \times 10/6 = 21.9`$. Agreement to about 1%.

One current field state contains the same event at several ages.

### 002 — Travel time meets a resonator XOR
[Report](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/002_wave_xor)

Two wave lanes of different length feed a pre-built XOR. The offset that makes the two arrivals coincide followed the geometry: **−5 frames** for one extra gap (predicted 4.94) and **−10 frames** for two (predicted 9.87). The XOR itself is wired in, not emergent. The measured variable is arrival-time compensation.

### 003 — One fade-triggered unit closes the loop
[Report](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/003_fade_closed_loop)

`read_1 → FadingHistorySpike → write_0`, one starting pulse, no clock.

| Configuration | Spikes in 550 frames | Late interval |
|---|---:|---:|
| Reference (decay 0.90) | 14 | 36 frames, perfectly regular |
| Slower fade (decay 0.96) | 5 | 104 frames |
| Return wire disconnected | 1 | none |
| No starting pulse | 0 | none |
| Unit disabled | 0 | none |

This one is also confirmed in the interactive GUI: 12 pulses by frame 464, about 37 frames apart.

Two things found on the way are worth keeping:

- The reference run hit the field's ±4 amplitude clamp on 100 of 550 frames. Experiments 004 and 005 use pulses about 8× smaller and record **zero** clipped frames.
- The GUI first fired once and died. The cause was a loader bug: a saved `size: 96` was stored as a number while the actual arrays stayed 256×256, so thresholds calibrated for one geometry were applied to another. It is fixed in PerceptionLab main.

### 004 — Two histories in one field
[Report](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/004_two_histories)

Fast unit A (decay 0.86) and slow unit B (decay 0.95) share one field. The hypothesis was that they would interleave. At full strength they did not.

| A's return weight | A spikes | B spikes | Regime (650 frames) |
|---|---:|---:|---|
| 1.00 | 21 | 0 | B suppressed |
| 0.50 | 25 | 0 | B suppressed |
| 0.45 | 8 | 6 | alternating |
| 0.30 | 6 | 5 | alternating |
| 0.25 | 5 | 5 | alternating |

The mechanism was measured, not guessed: under full A feedback, B stays armed with its trace **above its release threshold for 100% of the late period**. A's repeated pulses keep refilling B's record, so B's history never fades far enough to fire.

Over 1,800 frames:

| Case | Outcome |
|---|---|
| A return 0.30 | A and B alternate, both at 118 frames |
| A return 0.45 | A and B alternate, both at about 97 frames |
| A return 0.50 | A alone at 24 frames, B silent |
| A return 0.30, **B's return disconnected** | both die after one pulse |
| A return 0.30, sites swapped | still alternate, both at 70 frames |
| A return 0.30, decay rates swapped | B dominates at 81 frames, A silent |

In the alternating regime A does not sustain itself: with B's return disconnected both die. *Correction after experiment 007:* B does sustain itself, and turn-taking continues even with A's return at zero (section 10). The dependence is one-way. Swapping positions kept the behaviour; swapping fade rates flipped it. What decides the outcome is the unit's temporal identity, not its place.

### 005 — Can the order of falls remember AB versus BA?
[Report](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/005_order_of_falls) · [Three-active follow-up](https://github.com/anttiluode/PerceptionLabAI/blob/main/experiments/005_order_of_falls/THREE_ACTIVE.md)

Two equal pulses enter at two sites, in order AB or BA. A separate read-only linear readout, trained on 8 pairs, is tested on 8 held-out pairs (16 runs) at fixed later frames.

**With unlimited numerical precision, feedback gives no advantage:**

| Frame | Recurrent | Passive field |
|---|---:|---:|
| 160 | 15/16 | 16/16 |
| 360 | 14/16 | 16/16 |
| 650 | 15/16 | 16/16 |

A deterministic passive wave keeps order information forever in arbitrarily small numbers. This negative control is the most important row in the table.

**With a finite measurement floor** (traces below 1% of their calibration peak count as unreadable), at frame 650:

| System | Held-out accuracy |
|---|---:|
| Recurrent, all features | 15/16 |
| Recurrent, spike history only | 15/16 |
| Passive field | 8/16 (chance) |

By then the passive traces are of order $`10^{-6}`$. The order is still present in the continuing pulse trains.

**Three active units did worse.** In the first configuration the slowest unit never fired. A scan found a setting (C decay 0.93) where all three fire. On fresh held-out pairs at frame 650:

| System | Held-out accuracy |
|---|---:|
| All three returns active | 10/16 |
| Same units, C's return disconnected | 15/16 |
| Passive | 8/16 |

More interacting histories did not make a better memory. C's feedback scrambled the simpler code that A and B were holding, at least for a linear reader.

---

## 5. Fable's independent re-run of the single loop

To see what sets the rhythm, the 003 loop was re-implemented from the node sources in plain numpy and re-run with **thresholds held frozen** while one parameter changed at a time. Script and output: [`receipts/fable_rerun_003.py`](receipts/fable_rerun_003.py), [`receipts/fable_rerun_003_output.txt`](receipts/fable_rerun_003_output.txt).

Base period: **35 frames** (Sol's runner: 36; GUI: about 37; the small differences are one-frame transfer ordering).

| Changed | Values | Period (frames) |
|---|---|---|
| Trace decay | 0.80, 0.85, 0.90, 0.95 | 27, 29, 35, about 52 |
| Pulse amplitude | 1.0, 1.5, 2.0 | 27, about 30, 35 |
| Field damping | 0.006, 0.012, 0.020 | 35, 35, 35 |
| Reader aperture | 1, 2 | 35, 37 |
| Reader aperture | 3, 4, 5 | fires at most once, then dies |
| Amplitude clamp removed | | 34 |

Reading it:

- The rhythm is mostly the unit's own fade. A bigger pulse takes longer to fade, so it *slows* the loop.
- The field acts largely as the wire. Moving the reader one gap further adds 2 frames.
- The unit has a short reach. Three gaps away the wave arrives too weak to arm it.
- The clamp is not what holds the loop up.

These differ from Sol's 003 table (reader at aperture 2: 82.5 frames; damping 0.035: 44 frames) because Sol **recalibrates** the thresholds for every changed geometry, and his damping value is larger. Frozen thresholds ask "what does this parameter do to the same unit"; recalibrated thresholds ask "what does the loop look like when the unit is re-tuned to its new input". Both are valid and they are not the same question.

### The inverted response

One extra pulse was injected at aperture 4 at nine different points in the 35-frame cycle.

| Kick phase (frames after a spike) | Shift of the next spike |
|---|---:|
| 2 | +8 |
| 6 | +10 |
| 10 | +11 |
| 14 | +13 |
| 18 | +13 |
| 22 | +14 |
| 26, 30, 34 | 0 |

Every kick either delayed the next spike or did nothing. None advanced it.

An ordinary integrate-and-fire neuron does the opposite: excitation makes it fire sooner. This unit is **silenced by activity and fires into silence**. That single property is what experiment 004 then showed at the level of two units: the fast unit's activity holds the slow unit's trace up, and the slow unit never falls.

Only positive kicks at one location were tested.

---

## 6. What this is, and what it is not

**It is:**

- A constructed delayed-feedback relaxation oscillator. Reverberating loops, pacemaker cells and OFF/rebound cells are in the same family.
- For 005, a small case of reservoir computing: fixed dynamics, trained outside reader (Maass, Natschläger and Markram, 2002).
- A small case of state that never settles and moves from one condition to the next, which has an established theory as winnerless competition (Rabinovich and colleagues, 2001, 2008).

**It is not:**

- A new neural mechanism, a biological neuron model, or a port of the GeometricNeuron V26–V29 dynamics.
- Learning. Every parameter in the physical system is fixed. The only trained thing is the outside linear readout.
- Statistics. Each condition is one deterministic run. The 005 scores rest on eight held-out pairs.
- Noise-like. Two units give clean periodic turn-taking. "Seen from outside, noise" is known for large balanced networks (van Vreeswijk and Sompolinsky, 1996), not shown here.

**Honest ledger**

| Claim | Status |
|---|---|
| A wave field holds one event at several ages, at the predicted lag | Verified headless and in the GUI |
| A fade-triggered unit sustains a rhythm from one pulse, and dies without its return wire | Verified headless and in the GUI |
| Activity delays this unit and never advances it | Verified in one re-run, positive kicks only |
| Feedback strength switches two units between suppression and turn-taking | Verified headless, single runs; GUI not yet checked |
| In turn-taking, each unit needs the other | **Half true.** A needs B (B's return disconnected: both die). B does not need A's return (007: turn-taking continues at A weight 0.00) |
| A return edge can reach turn-taking from its own firing rate alone | Verified headless from five starting weights (007). Seen in the GUI on the both-homeostatic graph: A weight 0.61 with B silent, later 0.36 with B at 11 pulses |
| That rule is safe for a unit on its own | **False**: an isolated loop dies under it and does not restart (007) |
| Order AB/BA is readable from pulse trains after the passive field is below a 1% floor | Verified headless; the floor was chosen after the fact |
| Feedback improves order memory at unlimited precision | **False** in this model: passive 16/16 |
| More active units give more memory | Not shown. The 16-run result (10/16 against 15/16) did not hold up at 96 runs: 81/96 with the third return, 85/96 without, not distinguishable (008) |
| A self-tuned network holds order better than hand-set weights | **False**: 60/96 against 81/96 held-out, paired p = 0.0003 (008) |
| Grown branch structure keeps event order after all activity is wiped | Verified headless: one probe reads it in 89/96 held-out bodies; growth off 48/96; scrambled positions 55/96 (009) |
| A grown body recalls the missing event from a cue | **False**: one cue went opposite to prediction in 42 of 48 pairs (009) |
| Pruning protects that record from later experience | **Not shown**: 64/96 against 57/96 after interference, p = 0.28 (009) |

---

## 7. Where the picture stands

**Supported in miniature.** A unit's "little bit of wave" is best read as its own way of fading, not a piece of the scene. The scene is which fades are under way and how far along each one is. The past does get caught in pulse trains and shape later ones (004, 005).

**Not supported yet.** A wave holds a complex signal because waves add. Firing does not add. In this system the adding (the field) and the deciding (the race) take turns, and the present result is that the deciding part is harsh: the fastest fader silences slower ones within its reach, and slow units are the ones with long memory. Heterogeneity survived only under weak coupling.

**The pulse carries no payload.** Every pulse here is identical, so the trains carry timing and nothing else. The preprint that prompted part of this round (Martin-Burgos et al., 2026) reports that in real neurons the *shape* of an action potential carries information about the cell's input over the preceding 200 to 500 ms. A pulse whose size or shape depends on the sender's state is the obvious missing piece.

---

## 8. Open questions

1. **Does a kick change the order of falls repeatably?** With three or more weakly coupled units, does one input change the firing sequence in a way that depends on which input it was? 005 answered this for two-pulse order through an outside reader; the direct sequence test is still open.
2. **Why did the third unit hurt?** Is the order information destroyed by C's feedback, or only moved somewhere a linear reader cannot reach?
3. **Reach and territory.** Suppression is local, because a wave arrives weaker with distance. In a larger field, do fast faders carve out territories with slow faders surviving between them?
4. **Payload.** Let the pulse amplitude depend on the trace at the moment of firing, and test whether a reader gains anything beyond timing.
5. **Noise.** Every result is deterministic. None has been checked against perturbation.
6. **The network does not learn.** Thresholds are calibrated by hand and the graph is fixed. The harder step is a system that itself decides which histories are worth keeping, and whose wiring grows toward what it uses, the way a vine keeps the feelers that found something and drops the ones that did not.

---

## 9. Addendum — The first attempt to make a connection learn

*Sol / ChatGPT, 15 November 2026. Follow-up to experiments 001–005. Fable's preceding paper and its independent re-run remain unchanged above.*

The sixth open question in section 8 was whether the physical network could learn which of its own histories were useful, rather than leaving its graph fixed and training only an outside reader. The next test took one cautious step: insert a **trainable gain** on C's return path to the shared wave field.

The work is in [PerceptionLabAI — experiment 006](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/006_reward_selected_return); full [first receipt](https://github.com/anttiluode/PerceptionLabAI/blob/main/results/006_reward_selected_return.json).

### 9.1 What changed in the physical system

The original A and B loops remain. C is another fade-triggered unit, and its pulse previously travelled through a constant-weight edge to the field. We replaced that **one edge** with [PlasticReturnGateNode](https://github.com/anttiluode/PerceptionLabAI/blob/main/nodes/plastic_return_gate_node.py):

C's pulse → **bounded gain** → the wave field.

The gate holds its weight between experiences, and its emitted pulse is scaled by that weight. During training it evaluates slightly stronger and slightly weaker connections on matched AB/BA input sequences. An **external, label-aware evaluator** scores the frozen readout and supplies a scalar reward *difference* through a real node input. The node then updates its retained weight.

This is genuine parameter plasticity **inside the physical graph**, but the task and reward are supplied from outside. It is not autonomous valuation, learned physiology, Hebbian plasticity, or the growth of dendrites.

The two-sided update was

```math
w_{n+1}
=\operatorname{clip}_{[0,1]}\!\left(
w_n + \eta\,
\frac{R_n(w_n+\delta)-R_n(w_n-\delta)}{2\delta}
\right).
```

There was no built-in resource penalty pushing the weight toward zero.

### 9.2 Two tests, two negative results

| Test and held-out split | Learned C weight | Learned order readout | Frozen C return | Permanently pruned C return |
|---|---:|---:|---:|---:|
| **006:** first two-sided reward rule | 0.848 | **6/16** | **14/16** (w=0.50) | **14/16** (w=0) |
| **006b:** slower updates, capped at 0.05 and averaged over two contexts | 0.420 | **8/16** | **10/16** (w=0.50) | **14/16** (w=0) |

The two rows use **different, disjoint final-test contexts**. They must not be pooled as if they were repeated samples of one identical test. All four conditions within a row use the same physical gate and its extra one-frame delay.

In 006 the first reward comparison jumped from w=0.50 straight to w=1.00; seven further comparisons left it close to saturation. The resulting weight **hurt** unseen order recognition. The complete [weight trajectory](https://github.com/anttiluode/PerceptionLabAI/blob/main/results/006_reward_selected_return.json) is retained.

The separate, explicitly **post-hoc** [006b follow-up](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/006b_bounded_selection) limited each update to 0.05 and compared two input contexts at a time. It moved from w=0.50 to w=0.420 without saturating, but still failed the generalization comparison. [Complete 006b receipt](https://github.com/anttiluode/PerceptionLabAI/blob/main/results/006b_bounded_selection.json).

**Verdict:** a connection can learn a *new number* without learning the *right thing to keep*. That distinction is now experimentally visible. Neither test demonstrated that reward-shaped feedback beat a frozen or pruned control.

### 9.3 The vine question survives the failed rule

The [vine observation that prompted the analogy](https://www.youtube.com/watch?v=gdCdY2nkG5I) was about branches exploring, coiling around supports, and sometimes being abandoned. That is a problem of **growth, local sensing, resource allocation and persistent structure**.

Our gate does **none** of those things. It does not grow branches, move an aperture, create an edge, or generate its own notion of usefulness. It adjusts one scalar in response to an externally provided task reward. The failed tests argue against confusing these two achievements.

A next honest test must ask whether delayed local consequences can tell a branch that its continued existence helps future computation. It must compare learned structure with the best **fixed** graph on untouched contexts and keep an explicit cost for maintaining unnecessary branches.

The nail on the wall is therefore not “the network learned.” It is:

> **Fading histories and recurrent pings give us a temporal substrate. Plastic connections give us the ability to change it. We still lack a reliable rule that makes those changes useful.**

---

## 10. Addendum — A return edge that tunes itself

*Fable 5.2, 15 November 2026. Follow-up to section 9. Full report: [PerceptionLabAI — experiment 007](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/007_homeostatic_return); [receipt](https://github.com/anttiluode/PerceptionLabAI/blob/main/results/007_homeostatic_return.json).*

Section 9 ended without a reliable rule for changing a connection. Both attempts there used a reward computed by an outside reader that knew the labels. Experiment 007 removes the reward, the reader and the labels.

A's return edge watches one thing, how often A fires, and moves its own weight toward a target rate:

```math
r_{t+1} = r_t + \frac{s_t - r_t}{\tau}, \qquad w_{t+1} = \operatorname{clip}_{[0,1]}\bigl(w_t + \eta\,(r^\ast - r_{t+1})\bigr)
```

where $`s_t`$ is 1 on a frame where A fired, $`r`$ is its running rate, $`r^\ast`$ the target and $`w`$ the return weight. Firing too often lowers the weight; firing too rarely raises it. This is firing-rate homeostasis, a long-known mechanism. The only question was whether it works here.

### 10.1 Result

The system is the two-unit one from experiment 004, 6,000 frames per run, zero clipped frames throughout.

| Case | Final A weight | Last quarter of the run |
|---|---:|---|
| Homeostatic, start 1.00 | 0.41 | A and B take turns, 104 frames |
| Frozen at 1.00 | 1.00 | A alone at 29 frames, B silent |
| Homeostatic, start 0.75 / 0.50 / 0.30 | 0.41 / 0.42 / 0.42 | A and B take turns |
| Homeostatic, start 0.05 (12,000 frames) | 0.41 | A and B take turns |
| Homeostatic, **B's return disconnected** | back at 1.00 | **silent** |

Starting where A silences B, the edge lowers itself, B starts firing, and the two take turns. Learning rates from 0.005 to 0.32 reach the same regime.

### 10.2 What the target does

With a target that turn-taking can deliver (up to about one pulse per 97 frames), the weight settles and the target sets the tempo. With a higher target the weight does not settle. It swings across the switch point near 0.45–0.50, A meets its rate on average, and B fires in the gaps: 12, 9 or 4 times per 1,500 frames as the target rises from 0.016 to 0.030. No fixed weight in the tested sweep gave such in-between ratios.

### 10.3 What it corrected

A fixed-weight sweep through the same gate showed that turn-taking continues with A's return at **0.00**, at 154 frames. B's loop carries the pattern and A fires in answer. A's return only speeds it up, to 97 frames at 0.45. So the statement in the first version of this paper, that neither unit can keep itself going alone, was wrong about B. It has been corrected in the summary, section 4 and the ledger.

### 10.4 Limits

- **GUI coverage is partial.** One of the five graphs (both returns self-tuning) has been watched in PerceptionLab, where field energy fell from 0.0040 to 0.0001 as B joined. The rest are headless only.
- **An isolated loop dies.** Without B's return, A's weight falls as intended, the loop stops near weight 0.40, and nothing restarts it. A unit that cannot fire from silence cannot recover from its own caution.
- **One planned control was uninformative.** The sign-flipped rule started at 0.30 drifted to 0.04 and turn-taking continued, because every weight from 0.00 to 0.45 takes turns.
- **Nothing here measures memory.** The AB/BA test of experiment 005 was not run on the self-tuned system.
- **The target is chosen by hand**, and this is two units, one geometry, one deterministic run per condition.
- **The three-unit case is untested.** Experiment 005 found a third active unit made order harder to read. Whether three self-tuning returns do better is the next test.

Against the nail at the end of section 9: there is now one rule that changes a connection in a direction the system can use, without being told what useful means. It is a rule for sharing the field, not yet a rule for remembering.

---

## 11. Addendum — The deciding test for memory

*Fable 5.2, 15 November 2026. Full report: [PerceptionLabAI — experiment 008](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/008_self_tuned_order); [receipt](https://github.com/anttiluode/PerceptionLabAI/blob/main/results/008_self_tuned_order.json).*

Section 10 ended with a rule for sharing the field and the note that it was not yet a rule for remembering. Experiment 008 tested exactly that, with the decision rule committed before the run: self-tuning wins only if it beats the hand-set weights on a paired test.

The three-unit circuit of experiment 005 was given a self-tuning gate on every return. The gates settled with no labels, the weights were frozen, and the AB/BA order test was run on 96 held-out runs (the earlier experiments used 16).

| Condition | Return weights A, B, C | Correct of 96 at frame 650 |
|---|---|---:|
| Hand-set (experiment 005) | 0.30, 1.00, 0.50 | 81 |
| Hand-set, third return cut | 0.30, 1.00, 0.00 | 85 |
| **Self-tuned, frozen** | 0.22, 0.90, 0.47 | **60** |
| Self-tuned, still learning | starts as above | 75 |
| Passive field | 0, 0, 0 | 48 |

**The self-tuned network remembers order worse** (paired sign test p = 0.0003). A small shift in the weights cost 21 runs. Two other target rates, tried as a side check, also came out below hand-set.

### 11.1 A correction to section 4

Experiment 005 reported that a third active unit made order harder to read: 10/16 against 15/16. At 96 runs it is 81 against 85, and the paired test cannot separate them (p = 0.48). That finding was small-sample noise, as far as this test can tell. The summary and ledger are corrected.

### 11.2 Why, probably

During settling, runs that began with AB and runs that began with BA ended at almost the same weights and the same firing, about 22 pulses per unit per 2,000 frames. The rule pulls every unit toward the same rate and the circuit falls into one regular rotation whatever came first.

A system that always ends in the same rhythm has forgotten how it started. Self-tuning is a way of converging; remembering needs different pasts to stay apart. That tension was not measured directly here, so it stays an explanation, not a result.

### 11.3 Limits

The weights were still drifting when they were frozen, the reader is one linear type, and it is one deterministic circuit. None of this points toward a hidden win.

### 11.4 Where the round ends

- A wave field holds one event at several ages. **Shown.**
- A unit that fires when its history fades sustains a rhythm, and is delayed by activity, never advanced. **Shown.**
- Order of past inputs survives in the pulse trains after the passive field is unreadable. **Shown**, at about 84% on 96 runs.
- A connection can tune itself into sharing the field, from its own firing rate alone. **Shown.**
- A connection can learn what is worth remembering, by reward (section 9) or by self-tuning (this section). **Not shown; both failed.**

The last line is the open problem, and it is the old one: a system that can change itself still needs a reason to change in a direction that keeps the past.

---

## 12. Addendum — Morphology as memory

*Fable 5.2, from Sol's proposal, 15 November 2026. Full report: [PerceptionLabAI — experiment 009](https://github.com/anttiluode/PerceptionLabAI/tree/main/experiments/009_morphology_as_memory); [receipt](https://github.com/anttiluode/PerceptionLabAI/blob/main/results/009_morphology_as_memory.json).*

Sections 9 and 11 changed one number per connection and failed twice. Experiment 009 changes where a unit's output goes. The picture behind it is a vine: it sends out feelers, keeps the ones that found something and lets the rest die.

Each unit gets eight candidate return branches, one per site along the field, sharing a fixed budget:

```math
w_s \leftarrow w_s + \eta\,\bigl(p_s - \bar p\bigr), \qquad p_s = \frac{e_s}{\sum_k e_k}
```

where $`e_s`$ is how busy the field has recently been at the tip of branch $`s`$. The update happens when the unit fires. Weights are then rescaled to the budget, and a branch that falls below a threshold is removed for good. The rule sees only the unit's own pulse and the field at its branch tips.

A body lives through twenty episodes of A-then-B or B-then-A. Between episodes every signal is wiped, so only the branch structure carries anything forward. Decision rules were committed before the full run.

### 12.1 What passed

After a full wipe, one identical probe pulse was sent into each of 96 held-out bodies and a linear reader looked at the response.

| Body | History read correctly |
|---|---:|
| Grown | 89/96 |
| Growth switched off | 48/96 |
| Same branches, positions scrambled | 55/96 |
| Weights read directly (upper bound) | 91/96 |

The order of past events is in the arrangement of the branches, it survives total silence, and the body's ordinary response to one pulse gives almost all of it back. This is the first positive result in the round for a change the system made to itself.

### 12.2 What failed

- **No recall.** The prediction was that a body grown on A-then-B would answer cue A with activity at B's place. For cue A the result was the opposite in 42 of 48 pairs. Branches grow toward the middle of the field, where the two waves overlap, not toward the partner.
- **Pruning did not protect the record.** After ten episodes of the opposite order the first history was read in 64/96 bodies with pruning and 57/96 without (p = 0.28). Pruned bodies changed more, not less: dead branches cannot return, but the living ones keep trading weight.

### 12.3 How to read it

Section 3.4 described this system as lag matrices coupled by pings, with a fixed matrix. Here the matrix itself is moved by the pings, and because two changes applied in different orders do not give the same matrix, order ends up in structure. That much was close to expected: any timing-sensitive growth rule will do it. What the experiment adds is that it holds across varied histories, that position and not branch count carries it, and that it can be read through dynamics.

It does not show usefulness. The record does not help the body do anything, it is overwritten by later experience, and a plain Hebbian weight matrix was not compared.

### 12.4 The round, updated

- Order in ongoing pulse trains, fixed structure: about 84%, gone when activity stops.
- Order in grown structure: about 93%, survives silence, lost to later experience.
- A rule that makes either of these serve a task: still missing.

---

## References

- Martin-Burgos B., Juavinett A., Rivière P. D., Hammonds R., Voytek B. (2026). *Action potential waveforms are state-dependent.* bioRxiv. doi:10.64898/2026.09.15.751814
- Maass W., Natschläger T., Markram H. (2002). *Real-time computing without stable states: a new framework for neural computation based on perturbations.* Neural Computation 14.
- Shankar K. H., Howard M. W. (2012). *A scale-invariant internal representation of time.* Neural Computation 24.
- Rabinovich M., Volkovskii A., Lecanda P., Huerta R., Abarbanel H. D. I., Laurent G. (2001). *Dynamical encoding by networks of competing neuron groups: winnerless competition.* Physical Review Letters 87.
- Rabinovich M., Huerta R., Laurent G. (2008). *Transient dynamics for neural processing.* Science 321.
- van Vreeswijk C., Sompolinsky H. (1996). *Chaos in neuronal networks with balanced excitatory and inhibitory activity.* Science 274.

## Reproduce

Sol's experiments, with the real upstream nodes:

```bash
git clone https://github.com/anttiluode/PerceptionLabAI
cd PerceptionLabAI
git clone https://github.com/anttiluode/PerceptionLab PerceptionLab
python -m pip install numpy opencv-python-headless
python -m unittest discover -s tests -v
python experiments/004_two_histories/run.py --upstream PerceptionLab
python experiments/005_order_of_falls/run.py --upstream PerceptionLab
```

Fable's re-run of the single loop (numpy only):

```bash
python receipts/fable_rerun_003.py
```

Do not hype. Do not lie. Just show.

MIT licence.
