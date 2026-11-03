# Worked example: B2B distributor customer portal (fictional)

A regional distributor of industrial supplies sells to about 400 business customers. Today customers order by email and phone, and the distributor's staff re-key orders and invoices into QuickBooks Online. The distributor wants a customer portal.

**What it must do**

- **Customer logins and roles.** Each customer company has its own account. A company admin invites colleagues and gives each a role: buyer (places orders), approver (approves orders above a limit set by the company admin), or viewer (sees orders and invoices only). Users see only their own company's data.
- **Order history and one-click reorder.** Customers see their past orders and order lines, search and filter them, and reorder a past order in one click (current prices and stock apply, and the cart shows what changed).
- **Invoice payment by card through Stripe.** Customers see open invoices and pay one or several by card. Payment status updates from Stripe webhooks. Card data never touches the portal's servers.
- **Two-way sync with QuickBooks Online.** Customers, products and prices, invoices and payments sync between the portal and the distributor's QuickBooks Online company. Orders placed in the portal become invoices in QuickBooks; invoices and payments recorded in QuickBooks appear in the portal. Conflicts are flagged for staff, not overwritten silently.
- **Admin back office for the distributor's staff.** Staff manage customer companies and users, see and edit orders, see the sync log and resolve sync conflicts, and see payments.
- **Responsive web app.** Works on desktop and phone browsers. No native mobile app.

**Context**

- New codebase, mainstream stack (TypeScript, React, Node, Postgres), hosted on a mainstream cloud.
- About 400 customer companies and 1,500 users at launch; a few thousand orders a month.
- No regulated data beyond business contact details and payment status; payments are handled by Stripe.

**Run settings used**

- Rate regions: United States (onshore), Latin America (nearshore), Eastern Europe.
- Engagement type: firms (development companies), billed hourly rates.
- Team: 2 senior software engineers, a part-time UI/UX designer, a part-time QA engineer, a part-time project manager; target timeline 4 months.
- AI practice: senior engineers use agentic coding tools such as Claude Code every day; the repository has agent instructions and test commands from day one.
