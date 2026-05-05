---
id: taskmanagement
title: TaskManagement
tagline: A local-first work-management platform operated by humans AND AI agents
stack:
  - React 19
  - TypeScript
  - Vite
  - Tailwind CSS
  - ASP.NET Core 10
  - EF Core
  - SQL Server
  - Zustand
  - TanStack Query
links:
  repo: https://github.com/schendel2606/taskManagement
  live: https://tasks.schendel.me
order: 1
---

TaskManagement started from a real workflow problem. At Inspiria, we used ClickUp for a period of time, and I liked how much clarity it gave to internal work and customer communication. After moving away from it, I felt the team lost some operational efficiency: tasks were less visible, customer-facing updates were harder to track, and ownership became easier to blur.

I started building my own task system around that gap. The first idea was simple: a ClickUp-style workspace where each customer can receive a dedicated link and see only their own tasks, without leaking anything from other customers.

Then the project became more interesting. Since I already use AI heavily in personal and work projects, I started asking: why should only humans be assignees? The system now supports assigning work to AI agents such as Claude or Codex inside a controlled sandbox. Each agent can work on its own scope, update statuses, and ask for human input when it is blocked.

The most interesting part was learning how much product design changes once agents are treated as real operators in the system — not as a chat window, but as workers with boundaries, responsibilities, and escalation paths.
