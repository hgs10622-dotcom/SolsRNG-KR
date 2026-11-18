# AETHER RNG online services setup

This repository now contains a GitHub Pages deployment workflow and a Supabase database schema. The hosted site can be served by GitHub Pages; shared accounts and player data require a Supabase project.

## 1. Publish the static site
1. Open repository Settings → Pages.
2. Choose **GitHub Actions** as the Build and deployment source.
3. The workflow at `.github/workflows/pages.yml` deploys automatically on every push to `main`.
4. The default address is `https://hgs10622-dotcom.github.io/SolsRNG-KR/`.

## 2. Create the shared database
1. Create a project at https://supabase.com (free tier is sufficient for a prototype).
2. Open SQL Editor → New query.
3. Paste and run all of `supabase/schema.sql`.
4. In Project Settings → API, copy the Project URL and the **publishable/anon public key**.
5. Never put a service-role key in browser code or commit it to GitHub.

## 3. Configure the browser client
Create `supabase-config.js` locally with:
```js
window.AETHER_SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co";
window.AETHER_SUPABASE_ANON_KEY = "YOUR_PUBLIC_ANON_KEY";
```
Do not commit real keys if you prefer to keep project details private. The anon/publishable key is designed for browser use only when Row Level Security is correctly enabled. Service-role keys are secret and must remain server-side.

## 4. Important status
The database schema creates player profiles, inventory, roll history, a global leaderboard view, and a server-side weighted-roll RPC protected by authentication and row-level security. The current v0.1 browser game still uses local browser storage until the Supabase project is configured and the frontend integration is completed. No shared player database is live yet.

## Custom domain and 24/7 availability
A custom domain must be registered by its owner and then connected in GitHub Pages DNS settings. GitHub Pages serves the static website continuously, but it is not an always-on application server. Supabase hosts the database service. Free tiers can have usage limits or project pausing policies; they do not guarantee contractual 24/7 uptime.
