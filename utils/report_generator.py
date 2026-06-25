from fpdf import FPDF
import datetime
from io import BytesIO

def generate_pdf(data):
    """
    Generates a PDF report from grading data and returns it as BytesIO.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Title (No emojis to prevent encoding crashes)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 15, txt="EduGrader - Student Feedback Report", ln=1, align='C')
    pdf.ln(5)
    
    # Date & Time
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 5, txt=f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='R')
    pdf.ln(10)
    
    # Score
    pdf.set_font("Arial", "B", 14)
    pdf.cell(50, 10, txt=f"Total Score: {data.get('score', 'N/A')}", ln=1)
    pdf.ln(8)
    
    # ----- STRENGTHS -----
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, txt="Strengths:", ln=1)
    pdf.set_font("Arial", "", 11)
    for s in data.get('strengths', []):
        # 🔥 FIXED: Removed 'ln=1' from multi_cell()
        pdf.multi_cell(190, 8, txt=f"  - {s}")
    pdf.ln(5)
    
    # ----- WEAKNESSES -----
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, txt="Areas for Improvement:", ln=1)
    pdf.set_font("Arial", "", 11)
    for w in data.get('weaknesses', []):
        # 🔥 FIXED: Removed 'ln=1' from multi_cell()
        pdf.multi_cell(190, 8, txt=f"  - {w}")
    pdf.ln(5)
    
    # ----- ACTIONABLE FEEDBACK (NEXT STEPS) -----
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, txt="Actionable Next Steps:", ln=1)
    pdf.set_font("Arial", "", 11)
    for f in data.get('feedback', []):
        # 🔥 FIXED: Removed 'ln=1' from multi_cell()
        pdf.multi_cell(190, 8, txt=f"  - {f}")
    
    # Generate PDF as bytes (safe for Windows)
    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='ignore')
    return BytesIO(pdf_bytes)