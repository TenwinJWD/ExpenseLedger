"""Write the Transaction List to a PDF (landscape A4, the heading row repeats on every page).

Uses the Nunito font shipped with the app, so names with accents or other scripts print correctly.
"""

from datetime import date
from pathlib import Path

from app.core import config, dates, money, paths
from app.core.models import Entry
from app.services import report_service as rs

HEADINGS = ("Date", "Owner", "Main Entry", "Sub-Head", "Name", "Particulars", "Debit", "Credit")
COLUMN_WIDTHS = (22, 24, 32, 38, 42, 66, 26, 26)  # millimetres; 276 fits the 297 mm page with 10 mm margins
FONT = "Nunito"
BODY_SIZE = 8


def export_pdf(path: Path, entries: list[Entry], main_entries, own_owner: str, today: date | None = None) -> None:
    """Write the entries in the order given, with the totals in the last row."""
    from fpdf import FPDF  # loaded here: the library takes about 0.4 s to import and is needed only when exporting
    from fpdf.fonts import FontFace

    today = today or date.today()
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(True, margin=12)
    pdf.add_font(FONT, "", str(paths.asset_file("fonts/Nunito-Regular.ttf")))
    pdf.add_font(FONT, "B", str(paths.asset_file("fonts/Nunito-Bold.ttf")))
    pdf.add_page()

    pdf.set_font(FONT, "B", 16)
    pdf.cell(0, 9, f"{config.APP_NAME} - Transaction List", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 9)
    debit, credit = rs.totals(entries)
    pdf.cell(0, 5, f"Created {dates.format_date(today)} by {own_owner or 'unknown'} - {len(entries)} entries", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    pdf.set_font(FONT, "", BODY_SIZE)
    with pdf.table(col_widths=COLUMN_WIDTHS, text_align=("LEFT",) * 6 + ("RIGHT", "RIGHT"), line_height=4.6, padding=1.2, repeat_headings=1) as table:
        table.row(HEADINGS)
        for entry in entries:
            table.row([
                dates.format_date(entry.entry_date),
                entry.owner or own_owner,
                main_entries.label(entry.main_head),
                entry.sub_head,
                entry.name,
                entry.particulars,
                money.format_amount(entry.debit),
                money.format_amount(entry.credit),
            ])
        total = table.row()
        for text in ("Total", "", "", "", "", "", money.format_amount(debit), money.format_amount(credit)):
            total.cell(text, style=FontFace(emphasis="BOLD"))
    pdf.output(str(path))
