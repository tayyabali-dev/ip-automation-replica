#!/usr/bin/env python3
"""
Create a complex ADS PDF for testing our extraction fixes.
This will simulate the exact issues you mentioned:
- Middle names that could be truncated (Michael, Elizabeth)
- Citizenship data (United States)
- Total drawing sheets (8)
- Entity status (Small Entity)
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os

def create_complex_ads_pdf():
    filename = "tests/complex_ads_test.pdf"
    
    # Ensure tests directory exists
    os.makedirs("tests", exist_ok=True)
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "APPLICATION DATA SHEET (ADS)")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, "Title of Invention: Advanced Quantum Computing Processor")
    c.drawString(50, height - 100, "Application Number: 17/123,456")
    c.drawString(50, height - 120, "Filing Date: March 15, 2024")
    c.drawString(50, height - 140, "Entity Status: Small Entity")
    c.drawString(50, height - 160, "Total Number of Drawing Sheets: 8")
    
    # Inventor Information Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "INVENTOR INFORMATION")
    
    c.setFont("Helvetica", 10)
    
    # Inventor 1 - Michael (test middle name truncation)
    y_pos = height - 230
    c.drawString(50, y_pos, "Inventor 1:")
    c.drawString(50, y_pos - 20, "Given Name: John")
    c.drawString(200, y_pos - 20, "Middle Name: Michael")
    c.drawString(350, y_pos - 20, "Family Name: Anderson")
    c.drawString(50, y_pos - 40, "Mailing Address: 1234 Innovation Drive")
    c.drawString(50, y_pos - 60, "City: San Francisco")
    c.drawString(200, y_pos - 60, "State: CA")
    c.drawString(300, y_pos - 60, "ZIP: 94105")
    c.drawString(50, y_pos - 80, "Country: United States")
    c.drawString(50, y_pos - 100, "Citizenship: United States")
    
    # Inventor 2 - Elizabeth (test middle name truncation)
    y_pos = height - 350
    c.drawString(50, y_pos, "Inventor 2:")
    c.drawString(50, y_pos - 20, "Given Name: Sarah")
    c.drawString(200, y_pos - 20, "Middle Name: Elizabeth")
    c.drawString(350, y_pos - 20, "Family Name: Chen")
    c.drawString(50, y_pos - 40, "Mailing Address: 5678 Technology Blvd")
    c.drawString(50, y_pos - 60, "City: Austin")
    c.drawString(200, y_pos - 60, "State: TX")
    c.drawString(300, y_pos - 60, "ZIP: 78701")
    c.drawString(50, y_pos - 80, "Country: United States")
    c.drawString(50, y_pos - 100, "Citizenship: United States")
    
    # Inventor 3 - Wei (test correct middle name)
    y_pos = height - 470
    c.drawString(50, y_pos, "Inventor 3:")
    c.drawString(50, y_pos - 20, "Given Name: Michael")
    c.drawString(200, y_pos - 20, "Middle Name: Wei")
    c.drawString(350, y_pos - 20, "Family Name: Chen")
    c.drawString(50, y_pos - 40, "Mailing Address: 9012 Research Park")
    c.drawString(50, y_pos - 60, "City: Seattle")
    c.drawString(200, y_pos - 60, "State: WA")
    c.drawString(300, y_pos - 60, "ZIP: 98101")
    c.drawString(50, y_pos - 80, "Country: United States")
    c.drawString(50, y_pos - 100, "Citizenship: United States")
    
    # Applicant Information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 590, "APPLICANT INFORMATION")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 620, "Organization Name: Quantum Innovations LLC")
    c.drawString(50, height - 640, "Street Address: 100 Tech Valley Drive")
    c.drawString(50, height - 660, "City: Palo Alto")
    c.drawString(200, height - 660, "State: CA")
    c.drawString(300, height - 660, "ZIP: 94301")
    c.drawString(50, height - 680, "Country: United States")
    
    # Additional Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 720, "ADDITIONAL INFORMATION")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 740, "Customer Number: 12345")
    c.drawString(50, height - 760, "Correspondence Email: patents@quantuminnovations.com")
    
    c.save()
    print(f"✅ Created complex test PDF: {filename}")
    return filename

if __name__ == "__main__":
    create_complex_ads_pdf()