from fpdf import FPDF
from datetime import datetime

def generate_pdf_report(image_filename, plate_text, original_image_path, processed_image_path, report_path):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Informe de la imagen {image_filename}", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    if "Texto final no válido" in plate_text:
        pdf.cell(0, 10, "No se ha podido detectar la placa en la imagen.", ln=True)
    else:
        pdf.cell(0, 10, f"Se ha detectado una placa no adulterada de número {plate_text}.", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, "Imagen Original:", ln=True, align='center')
    pdf.image(original_image_path, x=10, y=pdf.get_y(), w=90)
    pdf.ln(70)
    pdf.cell(0, 10, "Placa Procesada:", ln=True, align='center')
    pdf.image(processed_image_path, x=10, y=pdf.get_y(), w=90)

    pdf.ln(50)
    pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    pdf.output(report_path)
