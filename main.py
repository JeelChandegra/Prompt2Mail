"""
Professional Email Sender MCP Server
Sends enhanced emails to multiple recipients via SMTP
"""
import os
from typing import List, Optional
from dotenv import load_dotenv
from fastmcp import FastMCP
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# SMTP Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_NAME = os.getenv("SENDER_NAME", "Professional Sender")

# Initialize FastMCP server
mcp = FastMCP("email-sender")


def enhance_email_with_ai(main_idea: str, tone: str = "professional") -> dict:
    """
    Enhance a short main idea into a professional email using Gemini AI
    Returns dict with 'subject', 'body', 'greeting', 'closing'
    """
    prompt = f"""You are a professional email writing assistant. Given a short main idea, create a polished, concise, and natural-sounding email.

Main idea: {main_idea}
Tone: {tone}

Generate a complete professional email with:
1. A clear, specific subject line (no "Subject:" prefix)
2. Appropriate greeting
3. Well-structured body (2-4 sentences, clear and concise)
4. Professional closing

Return ONLY a valid JSON object with these exact keys: "subject", "greeting", "body", "closing"

Example format:
{{"subject": "Project Update - Q4 Results", "greeting": "Hello,", "body": "I wanted to share some exciting news about our Q4 performance. Our team exceeded targets by 15% and secured three new major clients. The detailed report is attached for your review.", "closing": "Best regards"}}

Now generate the email:"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Extract JSON from potential markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(text)
        
        # Validate required keys
        required_keys = ["subject", "greeting", "body", "closing"]
        if not all(key in result for key in required_keys):
            raise ValueError("Missing required keys in AI response")
        
        return result
    except Exception as e:
        # Fallback to basic enhancement
        return {
            "subject": f"Update: {main_idea[:50]}",
            "greeting": "Hello,",
            "body": f"I wanted to reach out regarding: {main_idea}\n\nPlease let me know if you have any questions.",
            "closing": "Best regards"
        }


def send_email(to_email: str, subject: str, body: str, 
               cc: Optional[List[str]] = None, 
               bcc: Optional[List[str]] = None) -> dict:
    """
    Send an email via SMTP
    Returns dict with status and message
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            
            # Prepare recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send email
            server.sendmail(SMTP_EMAIL, recipients, msg.as_string())
        
        return {"status": "success", "message": f"Email sent to {to_email}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send to {to_email}: {str(e)}"}


@mcp.tool()
def send_professional_email(
    main_idea: str,
    recipients: str,
    tone: str = "professional",
    cc: str = "",
    bcc: str = ""
) -> str:
    """Send professional emails to multiple recipients. Provide a short main idea and list of email addresses - the AI automatically enhances it into a polished email with proper subject, greeting, and sign-off. Each recipient receives their own individual copy (no group exposure).

    Example usage: "Send email to alice@company.com, bob@team.org: We finished the report early with 3 key insights."

    Args:
        main_idea: Short description of what you want to communicate (e.g., "We launched the new dashboard")
        recipients: Comma-separated list of recipient email addresses
        tone: Email tone - professional (default), friendly, or formal
        cc: Optional comma-separated CC recipients
        bcc: Optional comma-separated BCC recipients
    """
    # Parse recipients
    recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]
    cc_list = [email.strip() for email in cc.split(",") if email.strip()] if cc else None
    bcc_list = [email.strip() for email in bcc.split(",") if email.strip()] if bcc else None
    
    if not recipient_list:
        return "Error: No valid recipients provided"
    
    if not main_idea:
        return "Error: No main idea provided"
    
    # Check SMTP configuration
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return "Error: SMTP credentials not configured. Please set SMTP_EMAIL and SMTP_PASSWORD in .env file"
    
    # Enhance email with AI
    try:
        enhanced = enhance_email_with_ai(main_idea, tone)
        subject = enhanced["subject"]
        greeting = enhanced["greeting"]
        body_text = enhanced["body"]
        closing = enhanced["closing"]
        
        # Format full email body
        full_body = f"{greeting}\n\n{body_text}\n\n{closing},\n{SENDER_NAME}"
        
    except Exception as e:
        return f"Error enhancing email: {str(e)}"
    
    # Send emails to each recipient individually
    results = []
    for recipient in recipient_list:
        result = send_email(recipient, subject, full_body, cc_list, bcc_list)
        results.append(result)
    
    # Format response
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count
    
    response = f"""✓ Email Sent Successfully

Subject: {subject}
Recipients: {len(recipient_list)} ({success_count} sent, {failed_count} failed)

--- Email Content ---
{full_body}
--------------------

Delivery Status:
"""
    
    for recipient, result in zip(recipient_list, results):
        status_icon = "✓" if result["status"] == "success" else "✗"
        response += f"{status_icon} {recipient}: {result['message']}\n"
    
    if cc_list:
        response += f"\nCC: {', '.join(cc_list)}"
    if bcc_list:
        response += f"\nBCC: {', '.join(bcc_list)}"
    
    return response


if __name__ == "__main__":
    print("🚀 Professional Email Sender MCP Server Starting...")
    print(f"📧 SMTP: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"👤 Sender: {SENDER_NAME} <{SMTP_EMAIL}>")
    print(f"🤖 AI: Gemini (Configured: {bool(GEMINI_API_KEY)})")
    print("Ready to send professional emails via Claude Desktop!\n")
    mcp.run()
