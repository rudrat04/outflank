# Carousel alt text

LinkedIn takes one description for a document upload. Paste the **Document description** below when you upload `carousel.pdf`. The per-slide text is for accessibility on other platforms, or if you post the slides as images.

## Document description

An 8-slide carousel about Outflank, an open-source competitor tracker that runs as a weekly cron job. It covers the method, the numbers from a first live run, three ways real websites broke the author’s assumptions, a battlecard that advised against pitching Hindi, and a checklist for trusting AI tools in GTM.

## Per slide

1. **Hook.** On a sunset-gradient background, large cream text reads: “You don’t need a SaaS to track competitors.” A pill below says: “I wrote a cron job instead.” A handwritten note says “a true story”, and another says “swipe →”.
2. **The question.** Headline: “What does it take to know when a competitor changes pricing?” Four cards list the jobs: Watch the pages that matter, Notice real changes (not timestamps), Explain what it means for your pitch, and Update the battlecard before the next deal. Note: “none of these needs a server running all day.”
3. **The method.** Headline: “Code watches. AI reads only what changed.” Six steps: a weekly cron in GitHub Actions; fetch and clean (free); diff and filter with keyword triggers and a size threshold (free); AI triage with a fast model (capped); AI analysis of material changes only (capped); then the digest and battlecards are committed to your repo and sent via issue, Slack or Discord.
4. **The numbers.** Headline: “What the first runs showed.” Four tiles: 211 passing tests before the first real website; 8 real pages across 4 example competitors; 0 AI calls on the second run because nothing changed; $0 spent on that run. A note says the first run, which writes 4 battlecards, costs an estimated $0.10 to $0.25 on Claude Opus. Handwritten: “the boring run is the whole argument.”
5. **The limits.** Headline: “Real websites broke 3 assumptions.” Labelled as examples, not a review. Convin: from the author’s server it redirected to a US product for home-service businesses. Hyperbound: /pricing quietly redirected to /pricing-b, likely an A/B test. Second Nature: a page came back almost empty until one include selector pulled in 4.7k characters. Handwritten: “and: no real competitor change caught yet.”
6. **The insight.** Dark slide. Headline: “The AI was the easy part. The plumbing was the product.” A quote card: the battlecard said “Don’t lead with ‘we support Hindi’,” because Hyperbound already lists Hindi, Gujarati, Marathi and Tamil. Four pills list what actually broke: a request format the API rejects, an npm install that deleted the engine, Docker reading a comment as the key, and alerts that could ping a Slack channel. All fixed.
7. **The rule.** Headline: “Before you trust any AI tool.” A checklist: run it on three real sites; read what it extracted, not what it concluded; run it twice; check the final URL; filter before you call a model; cap the cost of every run. Rule of thumb: if the pages change weekly or slower, a cron job beats a subscription.
8. **Takeaway.** Headline: “Competitor tracking can be a cron job.” Outflank is free and open source, with the template and repo link in the first comment, and an offer to build something similar for your team. Closing question: “What would you watch first: pricing pages, changelogs or careers pages?”
