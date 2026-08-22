# Ruten to Kapaipai Workflow

This package combines the Ruten exporter, Kapaipai preview generator, and Kapaipai uploader into one folder with one menu-based batch file.

## Setup

1. Install Python 3.11 or later and enable `Add python.exe to PATH`.
2. Open Command Prompt in this folder.
3. Run:

   ```bat
   py -m pip install -r requirements.txt
   ```

4. Double-click `run.bat`.

## Menu

- Case 1 asks for a Ruten store URL, then exports all public products from that store to `ruten_products_YYYYMMDD.xlsx`.
- Case 2 reads a Ruten workbook and creates the Kapaipai preview and skipped-items report.
- Case 3 reads a Ruten workbook and uploads products to Kapaipai.

Case 3 uses the following listing sequence:

1. Open the matched card page.
2. Click the add-product control to create the default listing.
3. Wait for and open the full-edit panel, or reuse an inline editor that Kapaipai opened automatically.
4. Set Product Price, Listed Quantity, and Product Note.
5. Verify the entered values and save the changes.

If an existing listing is detected, the workflow reuses its full-edit action or active inline editor instead of creating a duplicate. Newly created products continue through Full Edit even when Kapaipai also displays inline controls. A card that is not found is recorded and skipped. Any error after a card is found, including product creation, full edit, field entry, or saving, stops the entire upload immediately, writes diagnostic files, returns an error code, and leaves the batch window paused.

Cases 2 and 3 create one shared `*_kapaipai_skipped.xlsx` report. Preview-validation failures, products that require manual listing, mismatched search results, and cards that cannot be found are all recorded there instead of duplicating a `Skipped Items` worksheet inside the preview workbook. The report contains the source row, card code, product name, skip type, reason, quantity, price, source URL, and time. It is refreshed after every status change, keeps only the latest status for each source row, and removes a product after a later retry lists it successfully. Close the report in Excel while an upload is running so Windows can replace it; a locked report produces a warning but does not stop the upload.

Kapaipai may keep an existing listing's inline editor open after Save Changes succeeds. In that state, the workflow verifies the saved price, listed quantity, and note, and accepts the update only when the Save Changes control has become inactive. This avoids reporting a successful existing-listing update as a submission failure while still rejecting an enabled, unverified save state.

After a card page opens, the workflow waits for either Full Edit or Add Product. This handles the short reload period after consecutive rows reference the same card: a delayed existing listing is reused instead of being misreported as a missing add-product control.

Some cards have a zero quick-listing price when Kapaipai has no market price. Because Kapaipai silently ignores Add Product at zero price, the workflow initializes only a confirmed `$0` price with the Excel target price before creating the product. If that price update exposes an existing listing's inline editor, the workflow raises total stock when necessary, updates the price and listed quantity, adds the note through Add Note when needed, and saves the listing directly. If the quick price cannot be identified, it is left unchanged and product creation continues. The final Product Price, Listed Quantity, and Product Note are still verified before saving.

Kapaipai may replace a button in the DOM immediately after a successful click. For Add Product, Full Edit, and Save Changes, the workflow verifies the expected resulting UI state before deciding whether the action failed. This prevents a successful action from being reported as a timeout while preserving the immediate stop behavior for unverified upload errors.

Category selection and card search are verified together and retried up to three times. The result matcher accepts both normal card codes such as `AGOV-JP002` and Kapaipai catalog-qualified codes such as `AGOV(1202)-JP002`. Only three failed verification rounds stop the workflow.

Every processable card must contain a set code and card number connected by a hyphen. Official Japanese variants such as `BLZD-JPS06`, `20CP-JPC04`, `15AX-JPY52`, `DS14-JPL28`, `NCF1-JPP01`, `DUEA-JA045`, and legacy numeric forms such as `EE3-147` and `RB-60` are supported. Merchandise without a hyphenated card code is excluded. Card-number sections beginning with `AE` are treated as Asian English, and sections beginning with `EN` are treated as American English even when the title does not state the edition. Unnumbered, non-Japanese, and unsupported-language cards are written to the skipped-items report with short user-facing English reasons.

Duplicate DOM labels for the same visible card code, rarity, and artwork are collapsed before version selection. Zero quick-listing prices are detected from either an input value or the visible price stepper, so text-only `$0` controls are initialized before Add Product is clicked.

When the Excel title resolves to a known rarity, the Kapaipai result must match it exactly. For example, an Excel rarity of `N` cannot use an `SR` search result even when `SR` is the only result; the card is recorded as not found and skipped. The single-result fallback is used only when the source rarity is unresolved.

Before every card search, the configured game category is actively reselected even when the label already appears correct. Search-history card codes are excluded from rarity detection, and an empty result must remain stable before it is accepted. This prevents delayed category resets from turning search-history chips into false card results.

Game-filter options rendered by a virtualized dropdown use layered click recovery: normal click, scroll plus forced click, then a DOM click. The selected category is still verified afterward, so an off-screen option no longer stops the workflow as an unexpected error.

Search-result rarity labels may begin with digits, including `20SER` and `25SER`. Numeric product identifiers and card codes remain excluded, so they cannot be mistaken for rarities.

For Cases 2 and 3, paste or drag an Excel path into the prompt. Press Enter without a path to use the latest `ruten_products_*.xlsx` file in the package folder.

For Case 1, paste the complete Ruten store URL when prompted, for example `https://www.ruten.com.tw/store/example_seller/`. The exporter does not contain a default seller URL. When running the Python file directly, `--store-url` is required.

Ruten store pagination is updated dynamically without a full browser reload. After clicking Next Page, the exporter treats newly received product IDs from Ruten's API as the primary success signal and uses displayed page changes only as a fallback. It then allows an additional three seconds for the page to settle. A failed page change is retried up to three times instead of treating the first duplicated page as the end of the store. The additional delay can be changed with `--page-delay` when running the exporter directly.

## Files

- `run.bat`: the only batch entry point.
- `ruten_exporter.py`: exports Ruten store products.
- `kapaipai_uploader.py`: generates previews and creates Kapaipai listings.
- `kapaipai_rules.json`: rarity, consignor, score, and game-filter configuration.
- `requirements.txt`: Python dependencies.

The Python source, batch menu, logs, diagnostic labels, generated filenames, and workbook layout use English. Chinese strings that remain in `kapaipai_rules.json` or escaped text constants are required data for matching Ruten product titles and Kapaipai's Traditional Chinese interface.

## Generated files

- `ruten_products_YYYYMMDD.xlsx`
- `*_kapaipai_preview.xlsx`
- `*_kapaipai_upload.log`
- `*_kapaipai_progress.json`
- `*_kapaipai_skipped.xlsx`
- `kapaipai_diagnostics\` when a browser interaction fails

The browser login profile is created locally in `.kapaipai_chrome_profile` during Case 3. It is intentionally not included in this package.
