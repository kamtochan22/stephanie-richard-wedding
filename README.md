# Stephanie & Richard — Wedding 2027

One-page wedding invitation + photo site. Design system referenced from
YSL.com (Saint Laurent HK): ivory `#F8F7F5`, ink `#1A1A1A`, Cormorant
Garamond wordmark, Inter UI, hairline rules, frosted nav, restrained motion.

Deployable to Netlify by drag-and-drop (no build step).

---

## 1. Add your photos

Drop photos into `photos/` and edit the `PHOTOS` list at the top of the
`<script>` in `index.html`:

```js
{ src: "photos/01.jpg", span: 5, ar: "4/5", num: "01", cap: "The beginning" }
```

| field | meaning |
|-------|---------|
| `src` | file path inside `photos/` (jpg/png/webp) |
| `ar`  | aspect ratio — crop box. Default is **`9/16`** (portrait, phone photos fit perfectly). Other options: `4/5`, `3/4`, `1/1`, `3/2`, `16/9` |
| `span`| grid width out of 12: `3` (smallest) · `4` (default) · `5` · `6` (double-wide) |
| `cap` | caption shown under the photo |

Missing files render an elegant place-holder tile automatically — you can
drop photos in one by one and the layout stays intact.

- **Hero photo (first photo)**: replace the `.ph` block inside `#heroMedia` with
  `<img src="photos/hero.jpg" alt="Stephanie & Richard">` — **9:16 portrait**. On desktop it shows as a centered portrait column (YSL lookbook style); on mobile it fills the screen.
- **Story photos**: swap the `.ph` divs inside `.ed-media` (01 + 02).
- Compress large photos (≈2000px long edge, JPEG q80) before uploading.

## 2. Connect the RSVP form to Google Sheets

1. Go to `https://sheets.new` — a new spreadsheet opens.
2. Rename the tab from `Sheet1` to **`RSVP`**.
3. **Extensions → Apps Script** → delete placeholder code → paste the
   contents of `webhook.gs`.
4. **Deploy → New deployment → Web app**.
5. Execute as: **Me** · Who has access: **Anyone** → **Deploy**.
6. **Open the URL in a browser** (you should see `{"status":"RSVP webhook live"}`).
7. **Deploy again (new version)** — this second deploy is what makes POST
   work. Copy the final URL.
8. In `index.html`, replace `YOUR_APPS_SCRIPT_WEBHOOK_URL` with that URL
   (search for `WEBHOOK_URL`).

Each submission appends a row: Timestamp, Date, Name, Email, Attendance,
Guests, Dietary, Note.

### Pitfalls (the two that always bite)

- The FIRST deployed URL returns an HTML error on POST — the browser GET
  (step 6) + re-deploy (step 7) fixes it.
- POST must use `no-cors` + `text/plain` (already done in the form code).
  `application/json` triggers a CORS preflight Google rejects.

Verify with:

```bash
curl -X POST "https://script.google.com/macros/s/YOUR_ID/exec" \
  -H "Content-Type: text/plain;charset=utf-8" \
  -d '{"name":"Test","email":"t@t.com","attendance":"joyfully-accepts","guests":"2","source":"curl-test"}'
```

…then check the sheet for a new row.

## 3. Deploy

- **Netlify**: drag the whole folder (or just `index.html` + `photos/`)
  onto https://app.netlify.com/drop — done.
- Local preview: `python3 -m http.server 8000` in this folder, then open
  `http://localhost:8000`.

## 4. Background music

Track is in place at **`audio/bgm.mp3`** — 45.7s, 128 kbps stereo, extracted from the
supplied video (video track discarded), trailing silence trimmed, 0.3s fade-out,
loudness-normalised to −16 LUFS. The "Sound off" pill shows automatically because the
file exists (delete the file and the pill disappears).

Music cannot autoplay with sound (browser policy), so it starts on the visitor's
**first tap / click / keypress anywhere on the page** (the `pointerdown`/`touchstart`/
`keydown` listeners in the `BACKGROUND MUSIC` block). The bottom-left pill then works as
a mute / unmute control — tapping it to pause is remembered, so later taps won't restart
it. Replace `audio/bgm.mp3` with any other track you own/licensed — no code change
needed. Volume is set to 0.35 in the same block.

## 5. Envelope opener (intro)

On load the site is covered by an ivory envelope with a red wax seal. Tapping it opens
the flap, the card rises, then the veil lifts onto the hero — and that same tap is the
user gesture that starts the music with sound.

- Markup: `#opener` (right after `<body>`), styled by the `ENVELOPE OPENER` block.
- Timing: flap 1s → card rises from 0.5s → veil lifts at 1.7s → veil removed at 2.6s
  (see the `openInvitation()` function; adjust the two `setTimeout` values).
- Scroll is locked while it's open (`html.intro-locked`).
- To skip the intro entirely, delete the `#opener` div (nothing else references it).

## 6. Still to fill in (placeholders right now)

- Wedding date / venue / time / dress code — `#details` section
- RSVP deadline — `Kindly respond by — 2027` under `#rsvp`
- Contact email for guests — currently omits one; add if wanted
- Story copy (Chapter I / II quotes) — `#story` section
