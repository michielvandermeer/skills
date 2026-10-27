# Driving the browser

First users drive Playwright's agent CLI, `playwright cli`. Each First user gets its own named browser session, so all five run side by side.

## Check

1. Find the command. From the repo root, run `npx --no-install playwright --version`. When it prints a version, the command is `npx --no-install playwright`. Otherwise run `playwright --version`. When that prints one, the command is `playwright`. With neither, stop and tell the user to install Playwright, in the repo with `npm install --save-dev playwright` or as their system's package, then run the skill again.
2. Run `<command> cli --help`. When it fails, this Playwright predates the agent CLI: stop and tell the user to upgrade it.
3. Write one config per First user, `<subfolder>/cli.json`, so that its snapshots and logs land in its own subfolder rather than the repo root:

   ```json
   { "outputDir": "<subfolder>", "browser": { "browserName": "chromium" } }
   ```

4. Open and close a test session: `<command> cli -s=<stamp>-check open --config=<subfolder 1>/cli.json`, then `<command> cli -s=<stamp>-check close`. When `open` fails on a missing browser and `command -v chromium` prints a path, add `"launchOptions": { "executablePath": "<that path>" }` under `browser` in every config and try once more. When it still fails, stop with the install command its error names.

Done: the test session opened and closed.

## Commands for each First user

The session name is `<stamp>-<n>`, the scratch folder's stamp and the First user's number, so two runs on one machine never share a browser. Every command starts `<command> cli -s=<session>`.

- **Open**: `open --config=<subfolder>/cli.json`. The mobile user adds `--device "iPhone SE (3rd gen)"`, a 375px screen.
- **Slow 3G**, for the mobile user only, right after Open and before the first page: `run-code "async page => { const s = await page.context().newCDPSession(page); await s.send('Network.emulateNetworkConditions', { offline: false, latency: 2000, downloadThroughput: 50000, uploadThroughput: 50000 }); }"`. These are Chromium's slow 3G numbers, and they hold across later page loads.
- **Go to the app**: `goto <url>`.
- **See the page**: `screenshot --filename <subfolder>/<NN>.png` shows what your person sees. `snapshot` lists the page's elements with refs such as `e21`, which the actions below take.
- **Act**: `click <ref>`, `dblclick <ref>`, `fill <ref> "<text>"`, `type "<text>"`, `press Enter`, `select <ref> <value>`, `check <ref>`, `go-back`, `reload`.
- **Close**: `close`.

`<command> cli --help` lists every other command.
