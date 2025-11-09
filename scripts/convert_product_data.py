"""Utility for flattening the product data JSON file used in the demo app."""

from __future__ import annotations

# ruff: noqa: I001

import argparse
import json
import pathlib


EXCLUDED_FIELDS = {"image_embedding", "description_embedding"}


def flatten_products(nested_data: dict[str, object]) -> list[dict[str, object]]:
    """Convert the nested product catalog into a flat list of product records.

    The input structure is expected to match the layout found in
    ``data/product_data.json`` where products are grouped under main and sub
    categories. The returned product dictionaries omit embedding fields and add
    a ``categories`` key that contains the category path.
    """

    main_categories = nested_data.get("main_categories")
    if not isinstance(main_categories, dict):
        raise ValueError("Expected 'main_categories' mapping in input data")

    flattened: list[dict[str, object]] = []

    for main_category, group in main_categories.items():
        if not isinstance(group, dict):
            continue

        for subcategory, items in group.items():
            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                product = {key: value for key, value in item.items() if key not in EXCLUDED_FIELDS}
                product["categories"] = [main_category, subcategory]
                flattened.append(product)

    return flattened


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the converter."""

    parser = argparse.ArgumentParser(
        description="Flatten product_data.json into a top-level product array",
    )
    parser.add_argument(
        "--input",
        type=pathlib.Path,
        default=pathlib.Path("data/product_data.json"),
        help="Path to the source JSON file (default: data/product_data.json)",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("data/product_data_flat.json"),
        help="Destination path for the flattened JSON output (default: data/product_data_flat.json)",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point for converting the nested product catalog."""

    args = parse_args()

    with args.input.open("r", encoding="utf-8") as src:
        nested_data = json.load(src)

    products = flatten_products(nested_data)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as dst:
        json.dump(products, dst, indent=2)
        dst.write("\n")

    print(f"Wrote {len(products)} products to {args.output}")


if __name__ == "__main__":
    main()
