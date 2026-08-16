import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from ruten_exporter import (
    Product,
    build_parser,
    detail_quantity_from_html,
    export_excel,
    parse_price,
    parse_quantity,
    products_from_json,
    store_list_url,
    validate_store_url,
)


ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_price_and_quantity_example(self):
        text = "\u3010\u7f85\u52c3\u5c0f\u8216\u3011\u904a\u6232\u738b DBWS-JP023 \u8ced\u4e0a\u9748\u9b42! (\u4eae\u9762) NT$80 \u51711\u4ef6"
        self.assertEqual(parse_price(text), 80)
        self.assertEqual(parse_quantity(text), 1)

    def test_json_product(self):
        payload = {
            "items": [{
                "itemId": "22612345678901",
                "itemName": "\u3010\u7f85\u52c3\u5c0f\u8216\u3011\u6e2c\u8a66\u5546\u54c1",
                "price": 80,
                "stockQuantity": 3,
            }]
        }
        products = products_from_json(payload, "test")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].quantity, 3)
        self.assertEqual(products[0].price, 80)

    def test_detail_html(self):
        html = '<html><script type="application/ld+json">{"@type":"Product","name":"\u6e2c\u8a66\u5546\u54c1\u540d\u7a31","offers":{"price":80,"url":"https://www.ruten.com.tw/item/show?22612345678901","inventoryLevel":{"value":7}}}</script></html>'
        self.assertEqual(detail_quantity_from_html(html, "test"), 7)

    def test_store_root_is_changed_to_full_list(self):
        self.assertEqual(
            store_list_url("https://www.ruten.com.tw/store/qzecrvyn/"),
            "https://www.ruten.com.tw/store/qzecrvyn/list",
        )

    def test_store_url_is_required_and_validated(self):
        url = "https://www.ruten.com.tw/store/example_seller/"
        args = build_parser().parse_args(["--store-url", url, "--demo"])
        self.assertEqual(args.store_url, url)
        self.assertEqual(validate_store_url(f'"{url}"'), url)

    def test_run_batch_prompts_for_store_url(self):
        batch = (ROOT / "run.bat").read_text(encoding="utf-8")
        self.assertIn("Enter or paste the Ruten store URL", batch)
        self.assertIn('--store-url "%STORE_URL%"', batch)
        self.assertNotIn('call :run_python "ruten_exporter.py"\n', batch)


class ExcelTests(unittest.TestCase):
    def test_excel_has_requested_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.xlsx"
            export_excel([
                Product("\u3010\u7f85\u52c3\u5c0f\u8216\u3011\u904a\u6232\u738b DBWS-JP023 \u8ced\u4e0a\u9748\u9b42! (\u4eae\u9762)", 80, 1)
            ], output, "https://www.ruten.com.tw/store/qzecrvyn/")
            workbook = load_workbook(output, data_only=False)
            sheet = workbook["Products"]
            self.assertEqual(
                [sheet.cell(1, col).value for col in range(1, 4)],
                ["Product Name", "Quantity", "Price"],
            )
            self.assertEqual(sheet["A2"].value, "\u3010\u7f85\u52c3\u5c0f\u8216\u3011\u904a\u6232\u738b DBWS-JP023 \u8ced\u4e0a\u9748\u9b42! (\u4eae\u9762)")
            self.assertEqual(sheet["B2"].value, 1)
            self.assertEqual(sheet["C2"].value, 80)


if __name__ == "__main__":
    unittest.main()
