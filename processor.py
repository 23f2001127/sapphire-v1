from datetime import datetime
import pytesseract
from PIL import Image
import re
import os
from fpdf import FPDF

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class CarbonProcessor:
    def __init__(self):
        # Emission Factors (kgCO2e per unit)
        self.factors = {
            "ELECTRICITY": 0.82,  # India Grid Avg
            "DIESEL": 2.68,       # per Liter
            "PETROL": 2.31        # per Liter
        }

    def extract_data(self, image_path):
        # Perform OCR
        text = pytesseract.image_to_string(Image.open(image_path))
        
        # Simple Regex to find units (look for numbers near 'Units' or 'kWh')
        # This is where we'll eventually use LayoutLM for 100% accuracy
        units_pattern = re.findall(r'(?:Units|Consumption|kWh)\D*(\d+)', text, re.IGNORECASE)
        
        extracted_units = float(units_pattern[0]) if units_pattern else 0.0
        
        # Determine fuel type (simple keyword matching)
        fuel_type = "ELECTRICITY"
        if "diesel" in text.lower(): fuel_type = "DIESEL"
        
        return fuel_type, extracted_units

    def calculate_emissions(self, fuel_type, units):
        factor = self.factors.get(fuel_type, 0.82)
        emissions = units * factor
        return round(emissions, 2)
    
    def generate_pdf_report(self, data):
        pdf = FPDF()
        pdf.add_page()
        
        # Header - Brand Identity
        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(34, 139, 34) # Forest Green
        pdf.cell(200, 20, txt="SAPPHIRE GREENS", ln=True, align='C')
        
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(200, 10, txt="AI-Powered Carbon Intelligence for MSMEs", ln=True, align='C')
        pdf.ln(10)
        
        # Report Details
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt="Carbon Footprint Audit Summary", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=f"Report ID: SG-{datetime.now().strftime('%Y%m%d%H%M')}", ln=True)
        pdf.cell(200, 8, txt=f"Audit Date: {datetime.now().strftime('%d %b %Y')}", ln=True)
        pdf.ln(10)
        
        # Results Table
        pdf.set_fill_color(230, 245, 230) # Light Green Background
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(95, 12, "Category", 1, 0, 'C', True)
        pdf.cell(95, 12, "Details", 1, 1, 'C', True)
        
        pdf.set_font("Arial", size=12)
        items = [
            ("Source Type", data['fuel']),
            ("Consumption", f"{data['units']} Units"),
            ("Emission Factor", f"{self.factors.get(data['fuel'])} kgCO2e/unit"),
            ("Total Footprint", f"{data['co2']} kg CO2e")
        ]
        
        for label, val in items:
            pdf.cell(95, 12, label, 1)
            pdf.cell(95, 12, val, 1, 1)
            
        # Footer / Certification
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 10, txt="Compliance Statement:", ln=True)
        pdf.set_font("Arial", size=9)
        pdf.multi_cell(0, 5, "This audit is based on the GHG Protocol Corporate Standard (Scope 1 & 2). Data extracted via Sapphire AI Document Intelligence. This report is directional and prepared for MSME business development purposes.")
        
        filename = f"Sapphire_Report_{datetime.now().strftime('%H%M%S')}.pdf"
        output_path = os.path.join('uploads', filename)
        pdf.output(output_path)
        return filename