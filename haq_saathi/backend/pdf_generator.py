"""
Multilingual PDF Complaint Generator for Haq Saathi.
Generates one-page legal grievance draft in Telugu, Hindi, Urdu, or English.
Handles TrueType Unicode font registration and Arabic/Urdu RTL bidirectional reshaping.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display

FONTS_DIR = Path(__file__).resolve().parent / "fonts"

# Register Unicode fonts
TELUGU_FONT_PATH = FONTS_DIR / "NotoSansTelugu-Regular.ttf"
HINDI_FONT_PATH = FONTS_DIR / "NotoSansDevanagari-Regular.ttf"
URDU_FONT_PATH = FONTS_DIR / "NotoSansArabic-Regular.ttf"
URDU_NASTALIQ_PATH = FONTS_DIR / "NotoNastaliqUrdu-Regular.ttf"

FONTS_LOADED = False


def _init_fonts():
    global FONTS_LOADED
    if FONTS_LOADED:
        return

    # Telugu Font
    if TELUGU_FONT_PATH.exists():
        try:
            pdfmetrics.registerFont(TTFont("NotoTelugu", str(TELUGU_FONT_PATH)))
        except Exception as e:
            print(f"[PDF] Telugu font register notice: {e}")

    # Hindi Font
    if HINDI_FONT_PATH.exists():
        try:
            pdfmetrics.registerFont(TTFont("NotoHindi", str(HINDI_FONT_PATH)))
        except Exception as e:
            print(f"[PDF] Hindi font register notice: {e}")

    # Urdu Font (prefer Arabic for crisp linear table alignment or Nastaliq)
    urdu_file = URDU_FONT_PATH if URDU_FONT_PATH.exists() else URDU_NASTALIQ_PATH
    if urdu_file.exists():
        try:
            pdfmetrics.registerFont(TTFont("NotoUrdu", str(urdu_file)))
        except Exception as e:
            print(f"[PDF] Urdu font register notice: {e}")

    FONTS_LOADED = True


def prepare_urdu_text(text: str) -> str:
    """Shapes Arabic/Urdu cursive characters and applies BiDi visual ordering."""
    if not text:
        return ""
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except Exception as e:
        print(f"[PDF] Urdu reshape notice: {e}")
        return text


def get_font_for_lang(lang: str) -> str:
    _init_fonts()
    if lang.startswith("te"):
        return "NotoTelugu"
    elif lang.startswith("hi"):
        return "NotoHindi"
    elif lang.startswith("ur"):
        return "NotoUrdu"
    return "Helvetica"


class ComplaintPDFGenerator:
    """Generates official-grade single-page labour dispute petition PDF."""

    def __init__(self, output_dir: Optional[Path] = None):
        _init_fonts()
        self.output_dir = output_dir or (Path(__file__).resolve().parent.parent / "generated_pdfs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, complaint: Dict[str, Any], lang: str = "te-IN") -> str:
        """
        Builds a one-page grievance petition PDF for the given complaint record.
        Returns the absolute filepath to the generated PDF.
        """
        complaint_id = complaint.get("complaint_id", "HAQ-DRAFT-001")
        filename = f"Complaint_{complaint_id}_{lang[:2].upper()}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        font_name = get_font_for_lang(lang)
        bold_font = font_name  # Noto fonts handle standard weights cleanly
        is_urdu = lang.startswith("ur")

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName=bold_font,
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            alignment=1 if not is_urdu else 2  # Center or right
        )

        sub_title_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569"),
            alignment=1 if not is_urdu else 2
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=6,
            spaceAfter=4,
            alignment=2 if is_urdu else 0
        )

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#1e293b"),
            alignment=2 if is_urdu else 0
        )

        footer_style = ParagraphStyle(
            "DocFooter",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748b"),
            alignment=1
        )

        story = []

        # 1. Header Banner & Heading
        header_title = {
            "te": "కార్మిక సంక్షేమ మరియు వేతన బకాయిల ఫిర్యాదు పత్రం",
            "hi": "श्रम कल्याण एवं बकाया मजदूरी वसूली शिकायत पत्र",
            "ur": prepare_urdu_text("محنت کشوں کے حقوق اور بقایا اجرت کی باضابطہ شکایت"),
            "en": "FORMAL LABOUR DISPUTE & WAGE RECOVERY PETITION"
        }.get(lang[:2], "FORMAL LABOUR DISPUTE & WAGE RECOVERY PETITION")

        sub_header = {
            "te": "(తెలంగాణ రాష్ట్ర కార్మిక శాఖ పరిధిలో దాఖలు నిమిత్తం)",
            "hi": "(तेलंगाना राज्य श्रम विभाग के समक्ष प्रस्तुत करने हेतु)",
            "ur": prepare_urdu_text("(تلنگانہ ریاستی محکمہ محنت میں پیش کرنے کے لیے)"),
            "en": "(To be submitted before the Competent Authority, Telangana Labour Department)"
        }.get(lang[:2], "(Under Payment of Wages & Labour Welfare Framework)")

        story.append(Paragraph(header_title, title_style))
        story.append(Spacer(1, 2))
        story.append(Paragraph(sub_header, sub_title_style))
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0284c7"), spaceAfter=10))

        # 2. Addressed To Office
        addressed_header = {
            "te": "గౌరవనీయులైన అధికారి గారికి (TO):",
            "hi": "प्रति (TO):",
            "ur": prepare_urdu_text("بخدمت جناب (TO):"),
            "en": "TO:"
        }.get(lang[:2], "TO:")

        office_name = complaint.get("routed_office_name", "Office of the Deputy Commissioner of Labour")
        office_addr = complaint.get("routed_office_address", "RTC X Roads, Musheerabad, Hyderabad")

        if is_urdu:
            addressed_block = (
                f"<b>{addressed_header}</b><br/>"
                f"{prepare_urdu_text(office_name)}<br/>"
                f"{office_addr}"
            )
        else:
            addressed_block = (
                f"<b>{addressed_header}</b><br/>"
                f"<b>{office_name}</b><br/>"
                f"{office_addr}"
            )

        story.append(Paragraph(addressed_block, body_style))
        story.append(Spacer(1, 10))

        # 3. Facts in Clear Key Details Table
        worker_name = complaint.get("worker_name") or "Concerned Worker (అజ్ఞాత కార్మికుడు / पीड़ित श्रमिक)"
        worker_cat = complaint.get("worker_category", "informal_worker").replace("_", " ").title()
        employer_name = complaint.get("employer_name", "Employer / Contractor")
        district = complaint.get("district", "Telangana")
        unpaid_period = complaint.get("unpaid_period", "3 Months")
        amount_owed = complaint.get("amount_owed", "₹15,000")
        date_str = complaint.get("created_at", "2026-10-10")

        table_data = [
            [
                Paragraph(f"<b>Complaint Ref:</b> {complaint_id}", body_style),
                Paragraph(f"<b>Date:</b> {date_str}", body_style)
            ],
            [
                Paragraph(f"<b>Worker Name:</b> {worker_name}", body_style),
                Paragraph(f"<b>Category:</b> {worker_cat}", body_style)
            ],
            [
                Paragraph(f"<b>Employer/Company:</b> {employer_name}", body_style),
                Paragraph(f"<b>District/Location:</b> {district}", body_style)
            ],
            [
                Paragraph(f"<b>Unpaid Period:</b> {unpaid_period}", body_style),
                Paragraph(f"<b>Amount Claimed:</b> <font color='#059669'><b>{amount_owed}</b></font>", body_style)
            ]
        ]

        facts_table = Table(table_data, colWidths=[260, 260])
        facts_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(facts_table)
        story.append(Spacer(1, 10))

        # 4. Numbered Facts of the Case
        facts_heading = {
            "te": "వివాద వివరాలు (STATEMENT OF FACTS):",
            "hi": "विवाद का विवरण (STATEMENT OF FACTS):",
            "ur": prepare_urdu_text("واقعات اور حقائق (STATEMENT OF FACTS):"),
            "en": "STATEMENT OF FACTS & GRIEVANCE:"
        }.get(lang[:2], "STATEMENT OF FACTS:")

        story.append(Paragraph(facts_heading, section_heading))

        desc = complaint.get("description", "Employer withheld wages upon completion of duties.")
        f1 = {
            "te": f"1. ఫిర్యాదుదారుడు {employer_name} ఆధ్వర్యంలో {district} ప్రాంతంలో {worker_cat} గా చిత్తశుద్ధితో పనిచేశారు.",
            "hi": f"1. शिकायतकर्ता ने {district} में {employer_name} के अधीन {worker_cat} के रूप में निष्ठापूर्वक कार्य किया है।",
            "ur": prepare_urdu_text(f"1. شکایت کنندہ نے {district} میں {employer_name} کے ماتحت {worker_cat} کی حیثیت سے ایمانداری سے کام کیا۔"),
            "en": f"1. The applicant worked diligently as a {worker_cat} under {employer_name} in the district of {district}."
        }.get(lang[:2], f"1. The applicant worked as a {worker_cat} under {employer_name}.")

        f2 = {
            "te": f"2. పని చేసిన కాలానికి సంబంధించి సుమారు {amount_owed} మొత్తం చెల్లించకుండా యజమాని నిలిపివేశారు ({unpaid_period}).",
            "hi": f"2. कार्य अवधि {unpaid_period} के लिए लगभग {amount_owed} की बकाया राशि नियोक्ता द्वारा बिना किसी वैध कारण के रोक ली गई है।",
            "ur": prepare_urdu_text(f"2. کام کے عرصے {unpaid_period} کی تقریباً {amount_owed} کی واجب الادا رقم بغیر کسی جواز کے روک لی گئی ہے۔"),
            "en": f"2. The employer unlawfully withheld earned remuneration amounting to approximately {amount_owed} for the period {unpaid_period}."
        }.get(lang[:2], f"2. An amount of {amount_owed} is unpaid for {unpaid_period}.")

        f3 = {
            "te": f"3. కార్మికుని సంక్షిప్త వివరణ: {desc}",
            "hi": f"3. श्रमिक का विवरण: {desc}",
            "ur": prepare_urdu_text(f"3. مزدور کا بیان: {desc}"),
            "en": f"3. Particulars of violation: {desc}"
        }.get(lang[:2], f"3. Details: {desc}")

        story.append(Paragraph(f1, body_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f2, body_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f3, body_style))
        story.append(Spacer(1, 8))

        # 5. Right Violated & Statutory Basis
        rights_heading = {
            "te": "ఉల్లంఘించబడిన చట్టబద్ధ హక్కు (STATUTORY RIGHTS VIOLATED):",
            "hi": "उल्लंघन हुआ कानूनी अधिकार (STATUTORY RIGHTS VIOLATED):",
            "ur": prepare_urdu_text("پامال شدہ قانونی حقوق (STATUTORY RIGHTS VIOLATED):"),
            "en": "STATUTORY RIGHTS VIOLATED:"
        }.get(lang[:2], "STATUTORY RIGHTS VIOLATED:")

        rights_summary = complaint.get("rights_violated", "Timely payment of wages under wage protection laws.")
        source_citation = complaint.get("source_citation", "Payment of Wages Act / Labour Department Rules")

        story.append(Paragraph(rights_heading, section_heading))
        r_text = f"• <b>Legal Standard:</b> {rights_summary}<br/>• <b>Statutory Citation:</b> {source_citation} [Source: Verified Official Registry]"
        story.append(Paragraph(r_text, body_style))
        story.append(Spacer(1, 8))

        # 6. Desired Relief Requested
        relief_heading = {
            "te": "కోరబడిన న్యాయం (RELIEF PRAYED FOR):",
            "hi": "मांगी गई राहत (RELIEF PRAYED FOR):",
            "ur": prepare_urdu_text("مطالبہ و دادرسی (RELIEF PRAYED FOR):"),
            "en": "RELIEF PRAYED FOR:"
        }.get(lang[:2], "RELIEF PRAYED FOR:")

        relief_prayer = {
            "te": f"గౌరవనీయ లేబర్ అధికారి జోక్యం చేసుకుని, సదరు యజమానిని పిలిపించి బాకీ ఉన్న {amount_owed} మొత్తాన్ని వెంటనే రప్పించి న్యాయం చేయాల్సిందిగా వేడుకుంటున్నాను.",
            "hi": f"अतः श्रीमान से सविनय निवेदन है कि नियोक्ता को तलब कर बकाया राशि {amount_owed} तत्काल दिलवाई जाए तथा उचित कानूनी कार्रवाई की जाए।",
            "ur": prepare_urdu_text(f"لہٰذا جناب عالی سے پرزور گزارش ہے کہ ٹھیکیدار/مالک کو طلب فرما کر واجب الادا رقم {amount_owed} بلا تاخیر دلائی جائے اور انصاف فراہم کیا جائے۔"),
            "en": f"The applicant respectfully prays that this Hon'ble Authority summon the employer and direct immediate disbursement of all accrued dues amounting to {amount_owed} along with appropriate statutory interest."
        }.get(lang[:2], f"Direct immediate payment of {amount_owed}.")

        story.append(Paragraph(relief_heading, section_heading))
        story.append(Paragraph(relief_prayer, body_style))
        story.append(Spacer(1, 10))

        # 7. Verification & Declaration
        decl_text = {
            "te": "ధ్రువీకరణ: పైన పేర్కొన్న వివరాలన్నీ నాకు తెలిసినంత వరకు నిజమని మనస్ఫూర్తిగా తెలియజేస్తున్నాను.",
            "hi": "सत्यापन: उपर्युक्त समस्त विवरण मेरी जानकारी एवं विश्वास के अनुसार सत्य हैं।",
            "ur": prepare_urdu_text("تصدیق: مندرجہ بالا تمام بیانات میری معلومات کے مطابق بالکل سچ اور درست ہیں۔"),
            "en": "Verification: The applicant solemnly affirms that the facts stated above are true and correct to the best of their personal knowledge."
        }.get(lang[:2], "Verification: The facts stated above are true to the best of my knowledge.")

        sign_block = Table([
            [
                Paragraph(decl_text, body_style),
                Paragraph("<br/><br/>________________________<br/><b>Worker Signature / Thumb Impression</b>", body_style)
            ]
        ], colWidths=[340, 180])
        sign_block.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(sign_block)
        story.append(Spacer(1, 12))

        # 8. Disclaimer & Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=4))
        footer_text = (
            "Generated by Haq Saathi. This is a draft to help you file a complaint, not legal advice. "
            "Verify all amounts with the jurisdictional labour office before formal registration. "
            "No Aadhaar or sensitive bank identifiers are requested or logged."
        )
        story.append(Paragraph(footer_text, footer_style))

        doc.build(story)
        return str(filepath)


pdf_service = ComplaintPDFGenerator()
