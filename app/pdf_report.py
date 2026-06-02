from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

from reportlab.lib.styles import getSampleStyleSheet

def generate_report():

    pdf = SimpleDocTemplate(
        "security_report.pdf"
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(
            "Cyber Security Report",
            styles["Title"]
        )
    ]

    pdf.build(elements)