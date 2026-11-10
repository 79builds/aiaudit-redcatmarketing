# Brief: Build and deploy aiaudit.redcatmarketing.ca

## Goal

Turn the approved Red Cat Marketing "AI Visibility Audit" landing page into a static, upload-ready website, and deploy it to the subdomain **aiaudit.redcatmarketing.ca** on Rebel.ca hosting (Plesk).

The design and copy are approved. **Do not rewrite copy or redesign.** Reproduce the page faithfully as plain HTML/CSS/JS.

## What's in this folder

```
BRIEF.md                         this file
source/landing-page.dc.html      the approved page (design-tool format, see below)
source/assets/red-cat-logo.png   logo (used in header and footer)
source/assets/hero-phone.jpg     hero background photo
source/assets/audit-report.jpg   photo of the printed sample report
```

### How to read the source file

`landing-page.dc.html` is a "Design Component" file from a design tool, not a browser-ready page. Convert it like this:

| In the source | In the output |
|---|---|
| `<script src="./support.js">`, `<x-dc>`, `</x-dc>` | Remove |
| `<helmet>…</helmet>` (font link + `<style>`) | Move into `<head>` |
| `{{accent}}` | Replace with `#CF202E` everywhere |
| `{{menuClass}}`, `{{ariaExpanded}}`, `{{toggleLabel}}`, `onClick="{{…}}"`, `<sc-if>` | Replace with a small vanilla JS mobile menu (see Requirements) |
| `<script type="text/x-dc" data-dc-script …>` | Remove (logic is reimplemented in vanilla JS) |
| `/_blob/a352247ed3e7de09f2bf2f9d72dc8c1c` | `assets/red-cat-logo.png` |
| `/_blob/79fcdec79d7568266ce7f08752ee20aa` | `assets/hero-phone.jpg` |
| `/_blob/2cb7e659b8b9c7aed230ce7f52887982` | `assets/audit-report.jpg` |

Inline styles can stay inline, or be moved into a stylesheet if that's cleaner. Either way the rendered page must match the source at desktop (1440px) and phone (390px) widths.

## Deliverables

```
dist/
  index.html
  thank-you.html          simple branded confirmation page
  send.php                form handler (unless a CRM form is used instead)
  assets/                 the three images, optimized (WebP + JPG fallback is fine)
  favicon.png / .ico      from the red slash or logo
  robots.txt
  sitemap.xml
```

## Requirements

### Brand
- Fonts: **Playfair Display** (headings) and **Figtree** (body), both from Google Fonts.
- Colors: ink `#111111`, white `#FFFFFF`, warm grey `#F6F4F0`, border `#E6E2DC`, and **one accent only: red `#CF202E`**. Do not introduce other accent colors.
- No em dashes anywhere in the copy.

### Behavior (keep all of this)
- Sticky header with shadow; smooth scroll to sections; sections offset so headings aren't hidden under the header (`scroll-margin-top`).
- **Mobile menu (≤760px only):** logo + hamburger button. Tapping opens the links as a stacked list with 44px+ tap targets and a full-width "Get your audit" button. Icon switches to an X. Tapping any link closes the menu. Use a real `<button>` with `aria-expanded` and `aria-controls`.
- "What AI answers" rows shrink on phones (≤600px), as in the source CSS.
- FAQ questions and answers always visible (not an accordion).
- Hero photo: dark left-to-right gradient on desktop, even dark overlay on phones (see `.hero-bg` in the source).

### Form
Fields (keep labels exactly as in the source): First name, Last name, Work email, Company website, "What geo-area do you serve?" (Global / National / Regional / Local radio buttons), "Help us make the audit more accurate, type in your main location(s):", "Your top 3 competitors' URLs", "Is there anything else you want us to know?", submit button "Get my AI Visibility Audit ($997)".

- Required: first name, last name, work email, company website. Add `required` and sensible `type`/`autocomplete` attributes.
- **Handler:** default to `send.php` that:
  - accepts POST only, validates and sanitizes every field, rejects header injection;
  - includes a hidden honeypot field and drops submissions that fill it;
  - emails a readable summary to **[RECIPIENT EMAIL, ask Caleb]** with Reply-To set to the submitter's email;
  - redirects to `thank-you.html` on success and back to the form with a visible error on failure.
- If Red Cat uses a CRM (HubSpot, Mailchimp, etc.), **ask before building `send.php`**. The CRM's form or API may replace it.

### SEO / AI search (this is an AEO offer, so the page should practice it)
- `<title>`: "AI Visibility Audit | Red Cat Marketing"
- Meta description (≤155 chars) based on the hero subhead.
- Canonical: `https://aiaudit.redcatmarketing.ca/`
- Open Graph + Twitter card tags, using `audit-report.jpg` as the share image.
- JSON-LD in `<head>`:
  - `Organization` for Red Cat Marketing (url `https://www.redcatmarketing.ca`, logo, sameAs LinkedIn `https://www.linkedin.com/company/redcatmarketing/`)
  - `Service` for "AI Visibility Audit" (provider Red Cat Marketing, offers price 997, priceCurrency CAD, areaServed Canada)
  - `FAQPage` built from the four FAQ questions and answers exactly as written on the page
- `robots.txt` allows all crawlers **including AI crawlers** (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) and points to the sitemap.
- One `<h1>` only; keep the heading order logical.

### Performance and accessibility
- Images compressed and sized; `width`/`height` set; hero image preloaded; other images `loading="lazy"`.
- Text contrast at least 4.5:1; visible focus styles (the source uses a red outline); every input has a label.
- No horizontal scroll at 360px wide.

## Deployment on Rebel (Plesk)

1. Log in to Rebel → **Products** → **Domains** → purple **Control Panel** button next to the hosting package (opens Plesk).
2. Select **redcatmarketing.ca** → **Add Subdomain** → enter `aiaudit` → **OK**.
3. **DNS:** if redcatmarketing.ca's nameservers are Rebel's, Plesk creates the record automatically. If DNS is managed elsewhere (where the main site lives), add an **A record**: host `aiaudit`, value = the hosting IP shown in Plesk under Websites & Domains. Check with `dig aiaudit.redcatmarketing.ca +short`.
4. In the subdomain's **SSL/TLS Certificates**, install a free **Let's Encrypt** certificate and turn on the HTTP → HTTPS redirect.
5. Upload the contents of `dist/` to the subdomain's document root via Plesk **File Manager** or FTP (Plesk shows FTP credentials under the subdomain's settings).
6. Confirm PHP is enabled for the subdomain (Plesk → Hosting & DNS → Hosting) if using `send.php`.

Reference: https://support.rebel.ca/hc/en-us/articles/49242394254235-How-do-I-add-a-subdomain-to-my-hosting-package

## QA checklist (before calling it done)

- [ ] Page matches the source visually at 1440px, 768px, 390px and 360px.
- [ ] Mobile menu opens, closes, and closes on link tap; keyboard works (Tab, Enter, Esc closes).
- [ ] All anchor links land with the heading visible below the sticky header.
- [ ] Form: required fields enforced; test submission arrives at the recipient inbox; honeypot blocks a filled test; thank-you page loads.
- [ ] HTTPS works with no mixed-content warnings.
- [ ] JSON-LD passes Google's Rich Results Test and validator.schema.org.
- [ ] Lighthouse: Performance, Accessibility, Best Practices and SEO all 90+ on mobile.
- [ ] `robots.txt` and `sitemap.xml` load at the subdomain root.

## Open questions for Caleb

1. Where should form submissions go: which email address, or which CRM?
2. Any analytics to add (GA4, Google Tag Manager, Meta pixel, LinkedIn Insight)?
3. Is the $997 price final? (It appears in the form intro, checklist, submit button, FAQ and the `Service` schema.)
4. Should the "[Tracker link]" in the sample audit deck point to a file hosted on this subdomain (for example `/ai-visibility-tracker.xlsx`)?
