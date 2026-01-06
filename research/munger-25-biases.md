# Charlie Munger's 25 Cognitive Biases

**From: "The Psychology of Human Misjudgment" (1995, revised 2005)**

> "I went through life constantly practicing the multi-disciplinary approach and I can't tell you what that's done for me. It's made life more fun, it's made me more constructive, it's made me more helpful to others, it's made me enormously rich." — Charlie Munger

---

## The 25 Biases

### 1. Reward and Punishment Super-Response Tendency
People are heavily influenced by incentives and disincentives. Behavior is shaped almost entirely by what is believed to bring rewards or help avoid punishment.

**Trading Application:** Follow the money. If market makers profit from volatility, they'll create it. If insiders are selling, there's usually a reason.

---

### 2. Liking/Loving Tendency
We favor and trust people or things we like, which skews judgment. We overlook flaws in those we like and make decisions in their favor.

**Trading Application:** Don't fall in love with a position. "Marry your thesis, not your trade."

---

### 3. Disliking/Hating Tendency
We reject ideas, opportunities, or information from sources we dislike, regardless of merit. We distort facts to facilitate hatred.

**Trading Application:** If you hate a project/team, you might miss valid bullish signals. Separate emotion from analysis.

---

### 4. Doubt-Avoidance Tendency
When facing uncertainty, we make quick decisions to alleviate discomfort, even when more careful consideration would help.

**Trading Application:** The urge to "just do something" in volatile markets. Patience is often the right play.

---

### 5. Inconsistency-Avoidance Tendency
We resist changing our beliefs, opinions, or habits, even when presented with new evidence. We're reluctant to abandon previous commitments.

**Trading Application:** "I've already bought, so I'll hold" — the sunk cost fallacy. New information should override old positions.

---

### 6. Curiosity Tendency
A natural inclination to seek knowledge, which can sometimes be misdirected or distract from more important matters.

**Trading Application:** Shiny object syndrome. Chasing the latest narrative instead of sticking to your edge.

---

### 7. Kantian Fairness Tendency
A strong desire for fairness and reciprocity, leading to irrational decisions or overreactions to perceived unfairness.

**Trading Application:** "The market is unfair" — it doesn't matter. The market owes you nothing.

---

### 8. Envy/Jealousy Tendency
We resent the success of others, leading to destructive behavior and poor decisions. We take risks we wouldn't otherwise.

**Trading Application:** "He made 10x on that trade, I need to catch up" — leads to overleverage and poor entries.

---

### 9. Reciprocation Tendency
A compulsion to return favors and respond in kind. Can strengthen social bonds but also be exploited.

**Trading Application:** "The founder gave me alpha, so I owe them loyalty" — No. Your capital doesn't owe anyone loyalty.

---

### 10. Influence-from-Mere-Association Tendency
We're swayed by simple associations, making irrational choices based on superficial connections.

**Trading Application:** "This team worked at Google, so the project must be good" — Association ≠ causation.

---

### 11. Simple, Pain-Avoiding Psychological Denial
We deny uncomfortable facts to avoid the pain they might cause. Reality gets distorted to become bearable.

**Trading Application:** "It'll come back" — refusing to look at the chart because it hurts. The loss exists whether you check or not.

---

### 12. Excessive Self-Regard Tendency
Overconfidence in our own abilities. We think our possessions are more valuable and our decisions better than they are.

**Trading Application:** "I'm smarter than the market" — You're not. The market has more capital, more information, and more time.

---

### 13. Overoptimism Tendency
An unrealistic level of optimism causing us to underestimate risks and challenges.

**Trading Application:** "95% chance it hits 20k ETH" — Without rigorous probability assessment, optimism is just hope.

---

### 14. Deprival-Superreaction Tendency ⭐
**An intense overreaction to perceived or actual losses.** This includes the pain of losing something almost possessed.

**Trading Application:** THIS IS THE BIG ONE. When a market drops 30%, people panic sell. When they almost win, they double down irrationally. **This is the emotional volatility we want to trade against.**

---

### 15. Social-Proof Tendency ⭐
The inclination to follow the actions or beliefs of others. Herd mentality, especially in uncertain situations.

**Trading Application:** When everyone is buying, prices overshoot. When everyone is selling, prices undershoot. **Fade the crowd at extremes.**

---

### 16. Contrast-Misreaction Tendency
Judgment distorted by contrast between two options. We overvalue or undervalue based on comparison.

**Trading Application:** "It was at $100, now it's at $30 — it's cheap!" — No, it might be going to $10. Anchor to fundamentals, not past prices.

---

### 17. Stress-Influence Tendency ⭐
**Stress significantly impairs judgment.** We make quick, often suboptimal, conclusions under stress.

**Trading Application:** In market panics, EVERYONE is stressed. Their decisions are worse. If you can stay calm, you have an edge.

---

### 18. Availability-Misweighing Tendency ⭐
We overestimate the likelihood of events that are easily recalled or vividly imagined.

**Trading Application:** The last big news story dominates thinking. "Trump tweeted about Venezuela" → Maduro removal probability jumps 20%, even if tweet is meaningless.

---

### 19. Use-It-or-Lose-It Tendency
Skills deteriorate if not regularly used.

**Trading Application:** If you don't trade for months, you'll be rusty. Keep practicing with small stakes.

---

### 20. Drug-Misinfluence Tendency
Judgment distorted by intoxicating substances.

**Trading Application:** Don't trade drunk/high. Obvious but violated constantly.

---

### 21. Senescence-Misinfluence Tendency
Cognitive decline due to aging reduces decision-making capabilities.

**Trading Application:** Know when your edge is slipping. Systems > discretion as you age.

---

### 22. Authority-Misinfluence Tendency
Giving excessive weight to opinions of perceived authorities.

**Trading Application:** "Vitalik said X, so it must be true" — Authorities are often wrong. Verify independently.

---

### 23. Twaddle Tendency
Being distracted by irrelevant or trivial information.

**Trading Application:** 99% of crypto Twitter is noise. Filter ruthlessly.

---

### 24. Reason-Respecting Tendency
We're more likely to accept an idea if a reason is provided, even if the reason is weak or irrelevant.

**Trading Application:** "Buy because of fundamentals" sounds smart but might mean nothing. Demand specific, testable reasons.

---

### 25. Lollapalooza Tendency ⭐
**When several tendencies act in combination, creating extreme consequences more powerful than individual biases.**

**Trading Application:** A market panic combines: Social Proof (everyone selling) + Stress (fear) + Deprival Superreaction (loss aversion) + Availability (vivid bad news) = EXTREME MISPRICING. This is where the opportunity is.

---

## The 5 Most Relevant for Prediction Markets

| Bias | How It Creates Opportunity |
|------|---------------------------|
| **#14 Deprival-Superreaction** | Panic selling on losses, doubling down on near-wins |
| **#15 Social-Proof** | Herd behavior at extremes — fade the crowd |
| **#17 Stress-Influence** | Everyone's decisions worse in crisis — stay calm |
| **#18 Availability-Misweighing** | Overreaction to vivid recent news |
| **#25 Lollapalooza** | Combined biases create extreme mispricings |

---

## What To Build

A system that detects when multiple biases are firing simultaneously:

```
IF sudden_price_drop > 20%           # Deprival-Superreaction triggered
AND volume_spike > 3x average        # Social-Proof (herd selling)
AND recent_news_is_vivid             # Availability bias
AND market_sentiment = "FEAR"        # Stress-Influence
THEN lollapalooza_signal = TRUE      # Combined effect
→ Consider BUYING (fade the panic)
```

---

## Source

Charlie Munger, "The Psychology of Human Misjudgment"  
Harvard Law School, 1995 (revised 2005)  
Also published in: *Poor Charlie's Almanack*
