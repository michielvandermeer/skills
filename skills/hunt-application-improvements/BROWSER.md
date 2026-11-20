# Driving the browser

Hunters drive Playwright's agent CLI, `playwright cli`. Each Hunter that uses a browser gets its own named session, so all of them run side by side. The search crawler uses `curl` and no browser.

## Check

1. Find the command. From the repo root, run `npx --no-install playwright --version`. When it prints a version, the command is `npx --no-install playwright`. Otherwise run `playwright --version`. When that prints one, the command is `playwright`. With neither, stop and tell the user to install Playwright, in the repo with `npm install --save-dev playwright` or as their system's package, then run the skill again.
2. Run `<command> cli --help`. When it fails, this Playwright predates the agent CLI: stop and tell the user to upgrade it.
3. Write one config per browser Hunter, `<subfolder>/cli.json`, so that its snapshots and logs land in its own subfolder rather than the repo root:

   ```json
   { "outputDir": "<subfolder>", "browser": { "browserName": "chromium", "contextOptions": { "viewport": { "width": 1440, "height": 900 } } } }
   ```

   Two Hunters change `contextOptions`:
   - **Keyboard user**: `"viewport": { "width": 720, "height": 450 }, "deviceScaleFactor": 2`. That is a 1440 by 900 window at 200% zoom: the page lays out at 720 CSS pixels and its width media queries fire.
   - **Breaker**: add `"timezoneId": "<zone>"`, a zone at least eight hours from the machine's own (`date +%Z`), such as `Pacific/Auckland` for a machine on European time.
4. Open and close a test session: `<command> cli -s=<stamp>-check open --config=<any Hunter's subfolder>/cli.json`, then `<command> cli -s=<stamp>-check close`. When `open` fails on a missing browser and `command -v chromium` prints a path, add `"launchOptions": { "executablePath": "<that path>" }` under `browser` in every config and try once more. When it still fails, stop with the install command its error names.

Done: the test session opened and closed.

## Commands for each Hunter

The session name is `<stamp>-<slug>`, the scratch folder's stamp and the Hunter's slug, so two runs on one machine never share a browser. Every command starts `<command> cli -s=<session>`.

- **Open**: `open --config=<subfolder>/cli.json`.
- **Slow 3G**, for the slow-connection user only, right after Open and before the first page: `run-code "async page => { const s = await page.context().newCDPSession(page); await s.send('Network.emulateNetworkConditions', { offline: false, latency: 2000, downloadThroughput: 50000, uploadThroughput: 50000 }); }"`. These are Chromium's slow 3G numbers, and they hold across later page loads.
- **Go to the app**: `goto <url>`.
- **See the page**: `screenshot --filename <subfolder>/<NN>.png` shows what your person sees. `snapshot` lists the page's elements with refs such as `e21`, which the actions below take.
- **Act**: `click <ref>`, `dblclick <ref>`, `fill <ref> "<text>"`, `type "<text>"`, `press Enter`, `press Tab`, `select <ref> <value>`, `check <ref>`, `go-back`, `reload`.
- **Upload**, for the breaker: make the file in your subfolder, such as `head -c 52428800 /dev/zero > <subfolder>/50mb.bin` for 50 MB, click the file input so the file chooser opens, then `upload <absolute path>`.
- **Offline**, for the breaker: `network-state-set offline`, then `network-state-set online` to come back.
- **Network log**, for the attacker and the privacy reviewer: `requests --static --all` lists every request of the session with a number, including scripts, fonts, and the page itself. `request <n>` shows one request's headers and response headers. `response-body <n>` prints its body: the page's own request gives the page source, a script's gives the JavaScript bundle.
- **Read the page**, for the keyboard user: `eval "document.activeElement.outerHTML"` names the element that has focus.
- **Close**: `close`.

`<command> cli --help` lists every other command, and `<command> cli --help <command>` explains one.
