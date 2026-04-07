import os
import sqlite3
import base64
import smtplib
from io import BytesIO
from pathlib import Path
from email.message import EmailMessage
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from dotenv import load_dotenv

load_dotenv()

def get_sales_data():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE sales (region TEXT, revenue INTEGER, target INTEGER)')

    sample_data = [
        ('North America', 120000, 100000),
        ('Europe', 85000, 90000),
        ('Asia-Pacific', 150000, 130000),
        ('South America', 40000, 50000) 
    ]
    cursor.executemany('INSERT INTO sales VALUES (?, ?, ?)', sample_data)
    cursor.execute('SELECT * FROM sales')
    data = cursor.fetchall()
    conn.close()
    return data

def generate_chart(data):
    regions = [row[0] for row in data]
    revenue = [row[1] for row in data]

    plt.figure(figsize=(7, 4))
    plt.bar(regions, revenue, color='#4CAF50')
    plt.title('Monthly Revenue by Region')
    plt.ylabel('Revenue ($)')
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return image_base64

def render_html(data,chart_base64):
    declining_regions = [row[0] for row in data if row[1] < row[2]]
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report.html')

    return template.render(
        data=data, 
        declining_regions=declining_regions, 
        chart=chart_base64
    )
    

def send_email_with_attachment(pdf_path, recipient_email):
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD")
    
    msg = EmailMessage()
    msg['Subject'] = 'Automated Monthly Sales & Performance Report'
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(
        "Hello Team,\n\n"
        "Please find attached the automated sales and performance report for this month.\n\n"
        "Best regards,\n Automated System"
    )
    try:
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read() 
        msg.add_attachment(
            pdf_data, 
            maintype='application', 
            subtype='pdf', 
            filename=pdf_path.name
        )
    except FileNotFoundError:
        print(f"Error: Could not find the PDF at {pdf_path}")
        return
    try:
        print(f"Connecting to email server to send to {recipient_email}")

        with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
            smtp.login(SENDER_EMAIL,SENDER_APP_PASSWORD)
            smtp.send_message(msg)  
        print("Email successfully sent!")
        
    except Exception as e:
        print(f"Failed to send email Error: {e}")

def main():
    sales_data = get_sales_data()
    
    chart_b64 = generate_chart(sales_data)

    rendered_html = render_html(sales_data, chart_b64)

    output_path = Path("monthly_report.pdf")
    HTML(string=rendered_html).write_pdf(output_path)
    print(f"PDF successfully generated ")

    target_email = "2200032294cseh@gmail.com" 
    send_email_with_attachment(output_path,target_email)

if __name__ == "__main__":
    main()