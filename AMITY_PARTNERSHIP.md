# Partnership Proposal: Amity × Masonic Business Registry

**Status:** Draft for discussion
**Prepared for:** Jeremy (CEO, Amity) and the Amity advisory board
**Prepared by:** Siege Analytics
**Last updated:** 2026-04-23

---

## 1. One-page summary (for the advisory board)

We're building a **registry of businesses owned by Freemasons** — a
searchable, map-based directory where any verified Brother can find
Masonic-owned businesses and list his own. It is **entirely
authenticated**: an unauthenticated visitor sees a landing page and a
"Sign in with Amity" button, nothing more. **No business listings, no
owner names, no Lodge names, no map data** — nothing Masonic — is
exposed before verified login. A public listing of Masonic-owned
businesses is itself a security risk to the Craft and its members, and
we refuse to create one.

**This is a public service, not a business.** The registry is
underwritten by Siege Analytics and operated at cost. We are not
seeking profit from it, there is no paid tier, and no revenue share is
being proposed to anyone, including Amity. The ask here is mission
alignment, not a commercial deal.

For this to work, we need two things we don't have and that Amity does:

1. **Proof that a user is actually a Mason.** We don't want to build our
   own vetting pipeline; Amity already does this well and is trusted by
   the Craft.
2. **A way for a Brother to import his Masonic identity and memberships
   once**, so that adding a business to the registry takes thirty
   seconds instead of thirty minutes of paperwork.

In exchange, Amity gets:

- A concrete, member-facing reason for Brethren who *haven't* signed up
  for Amity yet to do so. Every business listing becomes a soft
  recruitment channel.
- A showcase integration demonstrating Amity as identity infrastructure
  for the Masonic world, not just a standalone app. This is what OAuth
  integrations did for LinkedIn a decade ago.
- Co-branded visibility in front of a very specific, high-intent
  audience: Brethren looking to support Masonic businesses, and Brethren
  business owners looking to be found.
- A partner whose incentives are aligned with yours by construction:
  because the registry isn't trying to monetize Brethren, there is no
  scenario in which our growth goals ever pull against Amity's.

Nothing in the proposal asks Amity to share raw membership data outside
of what an individual Brother explicitly authorizes about himself, on a
consent basis, in the standard OAuth model.

---

## 2. What we're building

A GeoDjango web application where **every meaningful surface is behind
verified-Brother authentication**. There is no public listing side.

### Unauthenticated surface (what the world sees)
- A marketing landing page explaining what the registry is and who
  it's for.
- A "Sign in with Amity" button.
- Nothing else. No search, no map, no business names, no Lodge data,
  no counts, no teasers.

### Members-only surface (verified Brother, logged in via Amity)
- Browse a map / search a directory of businesses.
- See business name, category, address, website, contact info.
- See owner — whether that's a **Lodge, Temple Association, Grand
  Lodge, appendant body, or a named Brother**.
- Filter by category, location, Rite, jurisdiction.
- Verify ownership claims.
- Submit a new business in ~30 seconds via an Amity-powered
  one-click flow.
- Claim an existing business listing.
- Contact a Brother-owner directly through the site.

### Why everything is gated

Publishing a searchable list of Masonic-owned businesses to the open
internet would create several concrete harms we're unwilling to accept:

- It doxes Lodges and Temple Associations to anyone with ill intent.
- It doxes individual Brethren who own businesses, even in
  jurisdictions where Masonic membership is socially or politically
  risky.
- It gives hostile actors a convenient target list.
- It erodes trust with Grand Lodges whose cooperation we want.

The trust model is simple: **you must be a verified Brother to see any
Brother's business.** Amity is how we enforce that.

### What's already scaffolded in the repo
- Django 5 + PostGIS backend with spatial REST APIs.
- Preliminary models for Grand Lodges, local bodies (Craft Lodges, RA
  Chapters, Cryptic Councils, Commanderies, Scottish Rite Valleys,
  Shrine Temples, OES Chapters, etc.), Temple Associations, Brethren,
  and Businesses.
- Grappelli admin for curation.
- Designed from day one with an `AmityLink` table and an
  `businesses/services/amity.py` client waiting to be filled in.

### Scope notes
- **In scope:** Mainstream / Regular, Prince Hall Affiliated, and
  Liberal / Continental (e.g. Grand Orient style) bodies.
- **Out of scope for v1:** Co-Masonry. This is a product decision to
  match the comfort level of the Brethren we expect to serve first.
- **Launch geographies:** United States + United Kingdom, phased global
  expansion after.
- **In scope for bodies:** Craft / Blue Lodges, York Rite (Chapter /
  Council / Commandery), Scottish Rite (Valley / Consistory), Shrine,
  Order of the Eastern Star, allied bodies.

---

## 3. Why Amity, specifically

We considered three paths for Masonic identity verification and
rejected the other two:

| Option | Problem |
|---|---|
| Build our own vetting (send a picture of your dues card + Lodge officer attestation) | Slow, expensive, error-prone, and it duplicates work Amity already does. Brethren will abandon the flow. |
| Rely on Grand Lodge APIs directly | Most Grand Lodges don't have APIs. Those that do don't have compatible ones. Every jurisdiction would be a bespoke integration. |
| **Partner with Amity** | Already trusted. Already federated across jurisdictions. One integration, many jurisdictions covered. |

Amity is the only existing piece of infrastructure that solves the
"is this person actually a Mason" problem at scale and across
jurisdictions.

---

## 4. What the integration would look like (plain English)

From a Brother's perspective:

1. He visits the registry and clicks **"Sign in with Amity."**
2. Amity shows a standard "this site is asking to see your name, your
   home Lodge, and your membership in appendant bodies — allow / deny"
   consent screen.
3. He approves.
4. He lands back on the registry, already linked to the correct Grand
   Lodge, Lodge number, and any York Rite / Scottish Rite / Shrine
   bodies he belongs to.
5. He clicks **"Add my business,"** fills out business name, address,
   category, and clicks save. His ownership is pre-populated from the
   Amity data.
6. Other verified Brethren can now find his business.

From Amity's perspective: this is a standard OAuth2 integration with a
custom scope set relevant to Masonic data. Amity controls what the
registry can and cannot see. Consent is revocable.

---

## 5. Technical integration (for Jeremy)

### 5.1 Preferred auth model

OAuth 2.0 Authorization Code flow with PKCE. Standard for first-party
and third-party web apps in 2026 and well-supported by every mainstream
library we'd be using (`authlib` on the Django side).

```
Browser --> Registry            GET /amity/connect/
Registry --> Browser            302 to Amity /oauth/authorize?client_id=...&scope=...&code_challenge=...
Browser --> Amity               Consent screen
Amity    --> Browser            302 to Registry /amity/callback/?code=...
Registry --> Amity               POST /oauth/token  (code + verifier)
Amity    --> Registry            { access_token, refresh_token, expires_in }
Registry --> Amity               GET  /api/v1/me
Registry --> Amity               GET  /api/v1/me/memberships
Registry --> Registry DB         upsert Brother + BodyMembership rows
```

### 5.2 Scopes we'd like to request

We want to request as little as possible and ladder up:

| Scope | What it unlocks for us | Why we need it |
|---|---|---|
| `profile.basic` | Brother's display name, verified flag, preferred contact email | Required; without this we cannot authenticate. |
| `membership.home_lodge` | Grand Lodge, Lodge number, Lodge name, rank (EA/FC/MM/PM/WM/PGM etc.) | Lets us pre-fill ownership and route the Brother to his jurisdiction's listings. |
| `membership.appendant` | Bodies in York Rite, Scottish Rite, Shrine, OES, allied | Lets a Brother list a business owned by (say) his Shrine Temple without re-entering the Temple's data. |
| `directory.lookup` (optional) | Resolve another Brother's display name by Amity user id | Only used when confirming co-ownership claims between Brethren; can be deferred. |

Happy to split, rename, or collapse these however your scope taxonomy
prefers.

### 5.3 Data we store on our side after import

Per linked Brother, in an `AmityLink` row:
- Amity user id (stable identifier).
- Access token + refresh token (encrypted at rest, KMS-backed).
- Last sync timestamp.
- Scopes granted.

Per Brother, in our `Brother` row:
- Display name.
- Verified flag (mirrors Amity's).
- Home Lodge FK → our own `Body` table (matched on Grand Lodge + number).
- Rank.

Per Brother, rows in our `BodyMembership` table pointing at York Rite
Chapters, AASR Valleys, Shrine Temples, etc.

We would **not** cache any PII beyond what the Brother explicitly
consents to share at link time, and we would support a one-click
"disconnect from Amity" that deletes all Amity-sourced data on our side
and revokes our tokens.

### 5.4 Jurisdictional data matching

Open technical question: when Amity says a Brother belongs to
"Lodge #42, Grand Lodge of New York F&AM," how does our side reliably
match that to the same Lodge in our `Body` table?

Options, in order of our preference:

1. **Amity publishes stable ids for Grand Lodges and Lodges** and we
   store those ids on our `GoverningBody.amity_id` and `Body.amity_id`
   columns. One integer match, no fuzzy logic.
2. Amity returns a normalized `{jurisdiction_code, lodge_number}` tuple
   and we maintain the jurisdiction code mapping on our side.
3. Worst case: we match on string name + number and build a manual
   reconciliation UI for the long tail.

(1) is what we're hoping for. (2) is fine. (3) we'd rather avoid, but
it's workable.

### 5.5 Write-back (stretch goal, not v1)

It would be fantastic if, after a Brother lists a business on the
registry, we could *optionally* push a "owns: [business name]" flag
back to his Amity profile so that Brethren browsing Amity can see he's
a registered business owner there too. Strictly one-way, opt-in,
deletable. Absolutely not required for launch — floating it so you know
the shape we want to grow into.

### 5.6 Rate limits, webhooks, staleness

- **Rate limits:** we'd expect most Brethren to link once and sync on
  demand. Our baseline usage is "one `/me` and one `/memberships` call
  per login or explicit refresh." Happy to implement caching with any
  TTL you specify.
- **Staleness:** if a Brother is suspended or expelled in Amity, we
  should know. Two options: (a) Amity webhook to us on status change,
  (b) we re-check verification each time a Brother performs a
  trust-sensitive action (list a business, contact another Brother).
  Either works; we'd prefer (a) long-term.
- **Token refresh:** standard refresh_token flow, short access token
  TTL fine.

---

## 6. Privacy and trust

We take this seriously because the Craft takes it seriously.

- **Everything Masonic is behind verified-Brother authentication.**
  Not just individual-Brother ownership — *all* ownership, including
  Lodges, Temple Associations, and Grand Lodges. An unauthenticated
  visitor sees the landing page and nothing else. Publishing a
  searchable list of Masonic real estate or Masonic-owned businesses
  to the open internet is a security risk to the Craft, full stop.
- **Brother opt-in for individual ownership visibility.** Even to
  other verified Brethren, a Brother can choose to list a business
  under his name or anonymously ("owned by a Brother in [jurisdiction]").
  His call.
- **Amity as source of truth for verification.** We don't try to
  compete with or shadow your verification. If Amity says a user is
  not a verified Brother, they see nothing.
- **Revocation respected.** If a Brother disconnects from Amity or is
  marked un-verified on Amity's side, his access flips off on the next
  trust-sensitive action, his individual ownership rows flip to
  anonymous, and we delete his Amity-sourced data within 30 days.
- **Data minimization.** We only store the fields listed in §5.3. We
  do not fan out Amity data to third parties.
- **No bulk exports.** There is no endpoint on our side that returns
  a list of Brethren, Lodges, or businesses in a scrapable form.
- **Per-jurisdiction redaction on request.** If a Grand Lodge asks us
  to suppress listings in its jurisdiction, we comply immediately
  while we discuss.
- **No search-engine indexing.** The authenticated surface is
  `noindex, nofollow`, excluded from `robots.txt`, and blocked at the
  CDN from indexable crawlers.

We're open to having these commitments codified in a written data
handling agreement with Amity, and separately with any Grand Lodge
that wants one.

---

## 7. Operating model (not commercial)

The registry is a **public service, not a company**. It is underwritten
by Siege Analytics and operated at cost. Concretely:

- **No paid tier, no freemium, no upsell.** Every feature is free for
  every verified Brother.
- **No ads. No affiliate links. No sponsored placements.**
- **No revenue share proposed to Amity.** We are not asking Amity to
  bless a money-making venture. We are asking Amity to help us run a
  trust layer for a free service to the Craft.
- **No sale of data, ever, to anyone, for any price.** Not aggregated,
  not anonymized, not in the event of an acquisition. Codified in the
  data handling agreement.
- **No acquisition exit on the table.** The registry is not a startup
  with a cap table.
- **Costs covered by Siege Analytics.** Hosting, storage, bandwidth,
  engineering, on-call. Budget set annually.
- **Co-branding is welcome.** A "Verified via Amity" badge on every
  Brother-owned listing, linking back to Amity, is something we'd
  encourage — it's recognition of where verification actually comes
  from.

If at any future point the economics change (for example, if scale
forces a sustainability model beyond what Siege can absorb), any shift
would be discussed openly with Amity and with participating Grand
Lodges first, before any user-facing change.

---

## 8. What we're asking Amity for, concretely

In order of importance:

1. **A conversation** about whether this partnership makes sense to
   you. Everything else follows from that.
2. **OAuth2 access** with the scopes in §5.2 (or your equivalent).
3. **Stable ids for Grand Lodges and Lodges** we can store as
   foreign keys (see §5.4).
4. **API docs** we can build against — sandbox credentials ideal.
5. **A point of contact** on your side for the integration build.
6. **Webhook support** for membership status changes (stretch).
7. **Write-back endpoint** for opt-in business ownership flags
   (stretch, post-v1).

---

## 9. Timeline we're targeting

| Phase | Target | Depends on Amity |
|---|---|---|
| Model + schema finalized | 2–3 weeks | No |
| Landing page + infrastructure + admin curation tools | ~6 weeks | No |
| Amity OAuth integration in staging | +2 weeks after sandbox access | **Yes** |
| Closed beta with a small cohort of verified Brethren, US + UK | +4 weeks after staging works | **Yes** |
| Public (authenticated) launch, US + UK | after beta feedback absorbed | **Yes** |
| PHA + Grand Orient coverage | +4 weeks | Soft yes (jurisdiction ids) |
| Global expansion | 2026 Q3–Q4 | Soft yes |

**Amity is now a hard dependency, not a "nice to have."** Because the
registry is entirely behind verified-Brother authentication, there is
no shippable v1 without an identity partner. We are betting on Amity.
We would rather delay launch than ship without verification.

---

## 10. Open questions for Jeremy

1. Does Amity have a public OAuth / API program today, or would this be
   the first external integration?
2. If it's the first, are you open to it, and on what timeline?
3. Given that **Amity becomes the sole identity gate** for a free
   public service to the Craft, are you comfortable with that level of
   dependency on your side? We want to be upfront about the stakes.
4. What's your preferred scope taxonomy — are we close in §5.2?
5. Stable jurisdiction / lodge ids: do they exist and are they exposed?
6. Is there a membership-status webhook we can subscribe to, or should
   we plan around polling? (Given the trust model, this matters more
   than in a typical integration.)
7. Any scopes or data classes you'd want to keep explicitly **off**
   limits? We'd rather know up front than discover it in review.
8. Is there interest in an `Amity for Business` surface — i.e. would
   Amity want to expose "this Brother owns a registered business" back
   into the Amity UX via a write-back API?
9. Because the registry is non-profit and entirely Siege-funded, there
   is no commercial ask on our side. Is there a non-commercial shape
   (co-branding, MOU, joint statement to Grand Lodges) that would be
   useful to Amity?

---

## 11. Next step

If any of the above is directionally interesting, a 30-minute call with
Jeremy + whoever on Amity's side would own the integration. We'll come
prepared to walk through a live demo of the registry scaffold, the
schema, and the OAuth callback wiring. No commitment required from
that call other than "yes, we want to keep talking" or "no, this isn't
for us."

Either answer is a fine answer. We'd just like one.

---

*Contact: [fill in]*
