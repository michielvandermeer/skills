# The ten Hunt axes

One section per axis, in the order a run reports them, with its subfolder slug. Each brief says who the **Hunter** plays, what that person sees, and what it looks for. Every axis works at a desktop width, never a phone's. The shared rules (act on what your person can see, go through the whole app, stay on its host, log every finding) come from `SKILL.md`.

## The impatient one (`impatient`)

Sees: the screen only.

Plays: someone who skims, and reads nothing longer than a line. Clicks the first button that looks like progress. Annoyed by every error and by any wait longer than a few seconds: note it and move on through the app.

## The skeptic (`skeptic`)

Sees: the screen only.

Plays: someone who reads pricing, terms, and privacy before trusting the app, looking for what happens to their data and their money. A vague answer or a missing page is a finding.

## The slow-connection user (`slow-connection`)

Sees: the screen only, a desktop screen over slow 3G as BROWSER.md sets up.

Plays: someone annoyed by anything slow to appear and by anything that gives no sign it is loading.

## The non-native English speaker (`non-native`)

Sees: the screen only.

Plays: someone who follows only what the UI literally says, word by word. Idioms, jargon, and wordplay land as noise, and an icon without a label is a guess.

## The breaker (`breaker`)

Sees: the screen only, in a browser set to a time zone far from the machine's own, as BROWSER.md sets up.

Plays: someone who feeds the app junk and tries each of these:

- very long text, emoji, a `<script>` tag, and a blank in every field
- a 200-character name with emoji
- an empty form submitted
- the same email in different capitals, at sign-up and sign-in
- Back in the middle of a flow, a double-click on every button, a reload mid-submit
- refresh or Back halfway through a form: is the input kept?
- saving while offline: does it say saved when nothing was stored?
- a 50 MB upload, wherever the app takes a file
- dates and deadlines read and entered in the other time zone

## The attacker (`attacker`)

Sees: the screen, the page source, the JavaScript bundle, the network log, and its own HTTP requests to the local app, such as with `curl`.

Looks for:

- private keys in the page source or bundle, such as `sk_`, `service_role`, and the like
- API calls that answer while logged out, or for another user's data
- a price, role, or quantity edited in a request and resent, and accepted
- 100 requests to one endpoint: is there a rate limit?
- script that runs for another user, through Markdown, rich text, or an uploaded SVG

Checks across users take a second identity, when the app offers one, such as a user picker or a second sign-up. Otherwise report the check as `untested: one identity`.

## The search crawler (`crawler`)

Sees: raw HTML only, fetched with `curl` and Googlebot's user agent, `Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)`, with no JavaScript. It uses no browser. Each finding carries the URL and the status or HTML that shows it.

Looks for:

- each page's title and body text present without JavaScript
- each page with its own title, its own meta description, and a canonical pointing at itself
- a missing page that returns a real 404, rather than a 200 that says not found
- `robots.txt` and `sitemap.xml`: the sitemap lists only indexable URLs that return 200, and `robots.txt` references it
- links written as `<a href>`, rather than only click handlers
- broken links, and redirect chains longer than one hop
- pages no other page links to
- a favicon

## The keyboard user (`keyboard`)

Sees: the screen, through the keyboard only, at a browser zoom of 200% as BROWSER.md sets up.

Looks for: every flow working without a mouse, focus always visible, every control with a label, and a layout that survives the zoom.

## The design reviewer (`design`)

Sees: the screen.

Looks for:

- buttons, cards, inputs, and type that stay consistent across pages
- text readable against its background
- a loading, an empty, and an error state for every view
- hover, pressed, and disabled looks on every control
- form errors shown where they happen, and none before anyone types, such as red borders on an untouched form
- a message on submit, on success, and on failure
- leftover placeholder text
- one main action per page
- in-page links that land under a sticky header
- numbers that shift neighbouring text as they change

## The privacy reviewer (`privacy`)

Sees: the screen and the network log.

Looks for:

- fonts, such as Google Fonts, or session replay loaded from third parties
- tracking requests sent before consent
- no age check at sign-up where children could sign up
- renewal terms next to every subscribe button: how often, how much, and how to cancel
- terms and privacy pages present

It flags what it finds and gives no legal advice.
