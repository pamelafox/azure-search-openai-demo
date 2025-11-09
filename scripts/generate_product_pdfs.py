"""Create a PDF per product from the flattened product catalog."""

from __future__ import annotations

# ruff: noqa: I001

import argparse
import importlib
import json
import textwrap
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path("data/product_data_flat.json")
DEFAULT_IMAGES_DIR = Path("data/images")
DEFAULT_OUTPUT_DIR = Path("data/product_pdfs")
MARGIN = 72  # one inch
MAX_WRAP_WIDTH = 88
_REPORTLAB_MODULES: tuple[Any, Any, Any] | None = None


@dataclass
class Product:
    """Simple container for the product fields used when rendering PDFs."""

    name: str
    sku: str
    price: str
    description: str
    image_path: Path | None
    categories: str


def _coerce_price(raw_price: Any) -> str:
    """Format the price value as a dollar string."""

    if isinstance(raw_price, (int, float, Decimal)):
        return f"${raw_price:,.2f}"

    try:
        parsed = Decimal(str(raw_price))
    except Exception:  # pragma: no cover - relies on external data
        return str(raw_price)

    return f"${parsed:,.2f}"


def _coerce_product(entry: dict[str, Any], images_dir: Path) -> Product:
    """Convert a raw dictionary into a Product instance with derived fields."""

    categories = entry.get("categories", [])
    category_label = " > ".join(str(cat) for cat in categories if cat) or "Uncategorized"

    image_path_value = entry.get("image_path")
    image_path = images_dir / image_path_value if image_path_value else None
    if image_path and not image_path.exists():
        image_path = None

    return Product(
        name=str(entry.get("name", "Unnamed Product")),
        sku=str(entry.get("sku", "UNKNOWN")),
        price=_coerce_price(entry.get("price")),
        description=str(entry.get("description", "")),
        image_path=image_path,
        categories=category_label,
    )


def _load_products(path: Path, images_dir: Path) -> list[Product]:
    """Load Product instances from the supplied JSON file."""

    with path.open("r", encoding="utf-8") as source:
        data = json.load(source)

    if not isinstance(data, list):
        raise ValueError("Input JSON must contain a top-level array of products")

    products: list[Product] = []
    for entry in data:
        if not isinstance(entry, dict):
            continue

        products.append(_coerce_product(entry, images_dir))

    return products


def _ensure_reportlab() -> tuple[Any, Any, Any]:
    """Import reportlab modules lazily and cache the result."""

    global _REPORTLAB_MODULES

    if _REPORTLAB_MODULES is None:
        try:
            pagesizes = importlib.import_module("reportlab.lib.pagesizes")
            utils = importlib.import_module("reportlab.lib.utils")
            pdfgen_canvas = importlib.import_module("reportlab.pdfgen.canvas")
        except ImportError as exc:  # pragma: no cover - dependency missing path
            raise SystemExit(
                "The generate_product_pdfs script requires the 'reportlab' package. "
                "Install it with 'pip install reportlab' and try again."
            ) from exc

        _REPORTLAB_MODULES = (
            getattr(pagesizes, "letter"),
            getattr(utils, "ImageReader"),
            pdfgen_canvas,
        )

    return _REPORTLAB_MODULES


def _render_product(product: Product, output_path: Path) -> None:
    """Render a single product PDF into output_path."""

    letter, ImageReader, canvas_module = _ensure_reportlab()
    pdf_canvas = canvas_module.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    max_width = width - 2 * MARGIN
    y_position = height - MARGIN

    pdf_canvas.setTitle(product.name)

    pdf_canvas.setFont("Helvetica-Bold", 18)
    pdf_canvas.drawString(MARGIN, y_position, product.name)
    y_position -= 28

    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(MARGIN, y_position, f"SKU: {product.sku}")
    y_position -= 18

    pdf_canvas.drawString(MARGIN, y_position, f"Price: {product.price}")
    y_position -= 18

    pdf_canvas.drawString(MARGIN, y_position, f"Category: {product.categories}")
    y_position -= 24

    if product.image_path:
        image_reader = ImageReader(str(product.image_path))
        img_width, img_height = image_reader.getSize()
        scale = min(max_width / img_width, (height / 3) / img_height, 1.0)
        draw_width = img_width * scale
        draw_height = img_height * scale
        image_y = y_position - draw_height
        pdf_canvas.drawImage(
            image_reader,
            MARGIN,
            image_y,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=True,
            mask="auto",
        )
        y_position = image_y - 24

    wrapped_description = textwrap.wrap(product.description, width=MAX_WRAP_WIDTH)
    if wrapped_description:
        text_obj = pdf_canvas.beginText(MARGIN, y_position)
        text_obj.setFont("Helvetica", 12)
        text_obj.setLeading(16)
        for line in wrapped_description:
            text_obj.textLine(line)
        pdf_canvas.drawText(text_obj)

    pdf_canvas.showPage()
    pdf_canvas.save()


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the PDF generator."""

    parser = argparse.ArgumentParser(
        description="Generate a PDF per product using the flattened JSON dataset.",
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to product JSON (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=DEFAULT_IMAGES_DIR,
        help=f"Directory containing product images (default: {DEFAULT_IMAGES_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write PDFs (default: {DEFAULT_OUTPUT_DIR})",
    )

    return parser.parse_args()


def main() -> None:
    """Entrypoint for generating product PDFs."""

    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    products = list(_load_products(args.input, args.images_dir))
    if not products:
        raise SystemExit("No products found to render.")

    for product in products:
        output_path = args.output_dir / f"{product.sku}.pdf"
        _render_product(product, output_path)

    print(f"Wrote {len(products)} PDFs to {args.output_dir}")


if __name__ == "__main__":
    main()
