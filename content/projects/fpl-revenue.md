---
id: fpl-revenue
title: FPL Revenue
tagline: Server-hosted FPL analytics with private financial rules layered on synced leagues
stack:
  - React 19
  - TypeScript
  - Vite
  - Tailwind CSS v4
  - ASP.NET Core 10
  - EF Core
  - SQL Server
  - JWT
  - BCrypt
links:
  repo: https://github.com/schendel2606/fpl-revenue
  live: https://fpl.schendel.me
order: 2
---

FPL Revenue came from a very practical problem: I play Fantasy Premier League with several groups of friends, and the financial side of those leagues is usually managed in WhatsApp, PayBox, and memory. Some leagues have season prizes, some reward the best score in a gameweek, and once you join enough of them, tracking what you paid, what you might win, and where you stand becomes annoying fast.

The product connects to the official FPL API and turns that data into a more useful layer for league managers and competitive players. It tracks league context, live points, financial rules, and projected outcomes, without replacing FPL as the source of truth.

The feature I would highlight from v0.9 is live points. I use real-time match data to estimate scores before FPL finishes its official update, and I also sample top global players to approximate live rank movement. Once FPL publishes its final update, the app returns to the official data.

The result is a more premium FPL experience: not just "how many points did I get," but what those points mean for rank, league position, and potential money outcomes.
