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

- Case 1 exports all public products from the configured Ruten store to `ruten_products_YYYYMMDD.xlsx`.
- Case 2 reads a Ruten workbook and creates `*_kapaipai_preview.xlsx`.
- Case 3 reads a Ruten workbook and starts the automatic Kapaipai upload workflow.

Case 3 uses the following listing sequence:

1. Open the matched card page.
2. Click the add-product control to create the default listing.
3. Wait for and open the full-edit panel.
4. Set Product Price, Listed Quantity, and Product Note.
5. Verify the entered values and save the changes.

If an existing listing is detected, the workflow reuses its full-edit action instead of creating a duplicate. A card that is not found is recorded and skipped. Any error after a card is found, including product creation, full edit, field entry, or saving, stops the entire upload immediately, writes diagnostic files, returns an error code, and leaves the batch window paused.

After a card page opens, the workflow waits for either Full Edit or Add Product. This handles the short reload period after consecutive rows reference the same card: a delayed existing listing is reused instead of being misreported as a missing add-product control.

Some cards have a zero quick-listing price when Kapaipai has no market price. Because Kapaipai silently ignores Add Product at zero price, the workflow initializes only a confirmed `$0` price with the Excel target price before creating the product. If the quick price cannot be identified, it is left unchanged and product creation continues. The full-edit panel still performs and verifies the final Product Price, Listed Quantity, and Product Note update.

Kapaipai may replace a button in the DOM immediately after a successful click. For Add Product, Full Edit, and Save Changes, the workflow verifies the expected resulting UI state before deciding whether the action failed. This prevents a successful action from being reported as a timeout while preserving the immediate stop behavior for unverified upload errors.

Category selection and card search are verified together and retried up to three times. The result matcher accepts both normal card codes such as `AGOV-JP002` and Kapaipai catalog-qualified codes such as `AGOV(1202)-JP002`. Only three failed verification rounds stop the workflow.

For Cases 2 and 3, paste or drag an Excel path into the prompt. Press Enter without a path to use the latest `ruten_products_*.xlsx` file in the package folder.

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
- `kapaipai_diagnostics\` when a browser interaction fails

The browser login profile is created locally in `.kapaipai_chrome_profile` during Case 3. It is intentionally not included in this package.
