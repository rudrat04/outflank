You don’t need a SaaS to track competitors. I wrote a cron job instead.

If you work in sales ops, you know the moment: a buyer mentions a competitor’s new pricing, and nobody on your side knew. The battlecard still shows last quarter.

My bet: competitor tracking can be a cron job, not a subscription.

So I built one. It’s called Outflank. Once a week, a GitHub Action in your own private repo fetches your competitors’ pages, strips the noise and diffs them against last week. AI only reads what actually changed: a fast model triages, and a stronger one analyzes material changes. Then it updates your battlecards and sends a digest.

211 tests passed. Then I pointed it at real pages from four AI sales-coaching vendors, as an example. Real websites broke three assumptions:

→ One site redirected my server to a different product, built for the US market.
→ One pricing page quietly redirected to /pricing-b. That looks like an A/B test, and a variant flip would look like a price change.
→ One page came back as 208 characters until a single selector pulled in 4.7k.

Then the moment it earned its keep. For an example tool selling to Indian enterprise teams, Hindi roleplays looked like the obvious edge. The battlecard disagreed: one competitor already lists Hindi, Gujarati, Marathi and Tamil. Don’t lead with “we support Hindi”; lead with BFSI and pharma depth.

The second run was the real argument: 8 pages, nothing changed, 0 AI calls, $0. A subscription costs the same on a quiet week.

And across the whole build, what broke wasn’t the AI. It was the plumbing: a request format the API doesn’t support, an npm install that deleted its own engine, Docker reading a comment as an API key, alerts that could ping a whole Slack channel.

My checklist before trusting any AI tool for GTM:
1. Run it on three real sites.
2. Read what it extracted, not what it concluded.
3. Run it twice. The second run should be quiet.
4. Check the final URL. Geo redirects and A/B tests are real.
5. Filter before you call a model.
6. Cap the cost of every run.
7. Escape everything you send to Slack or GitHub.

My rule of thumb: if the pages you care about change weekly or slower, a cron job beats a subscription.

Outflank is free and open source. Template and repo are in the first comment. If you want something like this built for your team, message me.

What would you watch first: pricing pages, changelogs or careers pages?

#GTMEngineering #RevOps #SalesOps
