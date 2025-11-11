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
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
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


def enhance_email_with_ai(main_idea: str, tone: str = "professional", recipient_name: str = "") -> dict:
    """
    Enhance a short main idea into a professional email using Gemini AI
    Returns dict with 'subject', 'body', 'greeting', 'closing'
    """
    greeting_instruction = ""
    if recipient_name:
        greeting_instruction = f"\nRecipient name: {recipient_name}\nUse a personalized greeting with their name (e.g., 'Dear {recipient_name},' or 'Hi {recipient_name},')"
    
    prompt = f"""You are a professional email writing assistant. Given a short main idea, create a polished, concise, and natural-sounding email.

Main idea: {main_idea}
Tone: {tone}{greeting_instruction}

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
        if not GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        model = genai.GenerativeModel('gemini-2.5-flash')
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
        # Fallback to basic enhancement with error info
        return {
            "subject": f"Update: {main_idea[:50]}",
            "greeting": "Hello,",
            "body": f"I wanted to reach out regarding: {main_idea}\n\nPlease let me know if you have any questions.",
            "closing": "Best regards"
        }


def send_email(to_email: str, subject: str, body: str, 
               cc: Optional[List[str]] = None, 
               bcc: Optional[List[str]] = None,
               attachments: Optional[List[str]] = None) -> dict:
    """
    Send an email via SMTP with optional attachments
    Returns dict with status and message
    """
    try:
        attached_files = []
        missing_files = []
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ', '.join(cc)
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach files
        if attachments:
            for file_path in attachments:
                if not os.path.isfile(file_path):
                    missing_files.append(file_path)
                    continue
                
                # Guess MIME type
                ctype, encoding = mimetypes.guess_type(file_path)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                
                maintype, subtype = ctype.split('/', 1)
                
                with open(file_path, 'rb') as f:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', 
                               filename=os.path.basename(file_path))
                msg.attach(part)
                attached_files.append(os.path.basename(file_path))
        
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
        
        message = f"Email sent to {to_email}"
        if attached_files:
            message += f" (Attached: {', '.join(attached_files)})"
        if missing_files:
            message += f" (Missing files: {', '.join([os.path.basename(f) for f in missing_files])})"
        
        return {"status": "success", "message": message, "attached": attached_files, "missing": missing_files}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send to {to_email}: {str(e)}"}


@mcp.tool()
def send_professional_email(
    main_idea: str,
    recipients: str,
    tone: str = "professional",
    cc: str = "",
    bcc: str = "",
    attachments: str = "",
    recipient_names: str = ""
) -> str:
    """Send professional emails to multiple recipients with optional attachments. Provide a short main idea and list of email addresses - the AI automatically enhances it into a polished email with proper subject, greeting, and sign-off.

    PERSONALIZED GREETINGS:
    - Use recipient_names parameter to personalize each email
    - Format: "John Doe, Sarah Smith" (comma-separated, same order as recipients)
    - Example: recipients="john@co.com, sarah@co.com", recipient_names="John, Sarah"
    - Each person gets their own email with personalized greeting
    - If names not provided, uses generic greeting

    ATTACHMENTS WORKFLOW - When user uploads a file:
    
    STEP 1: Save the uploaded file first
    - Call save_temp_file(filename, content, is_base64) tool
    - For text files: is_base64=False, pass raw text content
    - For binary files (PDF, images, etc): is_base64=True, pass base64 encoded content
    - You'll get back a path like "d:/mcp_claude/temp_attachments/filename.ext"
    
    STEP 2: Then call this email tool
    - Use the path returned from save_temp_file in the attachments parameter
    - Example: attachments="d:/mcp_claude/temp_attachments/report.pdf"
    
    COMPLETE WORKFLOW EXAMPLE:
    User: "Send this file to john@example.com"
    1. You call: save_temp_file("document.pdf", "<base64_content>", True)
    2. Tool returns: "d:/mcp_claude/temp_attachments/document.pdf"
    3. You call: send_professional_email(
         main_idea="Please find attached document",
         recipients="john@example.com",
         attachments="d:/mcp_claude/temp_attachments/document.pdf"
       )
    
    For multiple attachments, separate paths with commas.

    Args:
        main_idea: Short description of what you want to communicate
        recipients: Comma-separated list of recipient email addresses
        tone: Email tone - professional (default), friendly, or formal
        cc: Optional comma-separated CC recipients
        bcc: Optional comma-separated BCC recipients
        attachments: Comma-separated file paths (use paths from save_temp_file tool)
    """
    # Parse recipients, names, and attachments
    recipient_list = [email.strip() for email in recipients.split(",") if email.strip()]
    name_list = [name.strip() for name in recipient_names.split(",") if name.strip()] if recipient_names else []
    cc_list = [email.strip() for email in cc.split(",") if email.strip()] if cc else None
    bcc_list = [email.strip() for email in bcc.split(",") if email.strip()] if bcc else None
    
    # Pad name_list with empty strings if fewer names than recipients
    while len(name_list) < len(recipient_list):
        name_list.append("")
    
    # Handle attachment paths - convert relative to absolute
    attachment_list = []
    if attachments:
        for path in attachments.split(","):
            path = path.strip()
            if not path:
                continue
            # If relative path, make it relative to workspace
            if not os.path.isabs(path):
                path = os.path.join(os.path.dirname(__file__), path)
            attachment_list.append(path)
    
    attachment_list = attachment_list if attachment_list else None
    
    if not recipient_list:
        return "Error: No valid recipients provided"
    
    if not main_idea:
        return "Error: No main idea provided"
    
    # Check SMTP configuration
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return "Error: SMTP credentials not configured. Please set SMTP_EMAIL and SMTP_PASSWORD in .env file"
    
    # Send emails to each recipient individually with personalized greeting
    results = []
    email_contents = []
    
    for recipient, recipient_name in zip(recipient_list, name_list):
        # Enhance email with AI (personalized for each recipient)
        try:
            enhanced = enhance_email_with_ai(main_idea, tone, recipient_name)
            subject = enhanced["subject"]
            greeting = enhanced["greeting"]
            body_text = enhanced["body"]
            closing = enhanced["closing"]
            
            # Format full email body
            full_body = f"{greeting}\n\n{body_text}\n\n{closing},\n{SENDER_NAME}"
            
            # Send email
            result = send_email(recipient, subject, full_body, cc_list, bcc_list, attachment_list)
            results.append(result)
            email_contents.append({"recipient": recipient, "subject": subject, "body": full_body})
            
        except Exception as e:
            results.append({"status": "error", "message": f"Error for {recipient}: {str(e)}"})
            email_contents.append({"recipient": recipient, "subject": "Error", "body": str(e)})
    
    # Format response
    success_count = sum(1 for r in results if r["status"] == "success")
    failed_count = len(results) - success_count
    
    # Collect attachment info
    all_attached = []
    all_missing = []
    for r in results:
        if "attached" in r and r["attached"]:
            all_attached.extend(r["attached"])
        if "missing" in r and r["missing"]:
            all_missing.extend(r["missing"])
    
    # Remove duplicates
    all_attached = list(set(all_attached))
    all_missing = list(set(all_missing))
    
    # Get first email content for display (all have same subject)
    first_content = email_contents[0] if email_contents else {"subject": "N/A", "body": "N/A"}
    
    response = f"""✓ Email Sent Successfully

Subject: {first_content['subject']}
Recipients: {len(recipient_list)} ({success_count} sent, {failed_count} failed)

--- Sample Email Content (first recipient) ---
{first_content['body']}
--------------------

Delivery Status:
"""
    
    for i, (recipient, result) in enumerate(zip(recipient_list, results)):
        status_icon = "✓" if result["status"] == "success" else "✗"
        name_info = f" ({name_list[i]})" if i < len(name_list) and name_list[i] else ""
        response += f"\n{status_icon} {recipient}{name_info}: {result['message']}"
        response += f"{status_icon} {recipient}: {result['message']}\n"
    
    if cc_list:
        response += f"\nCC: {', '.join(cc_list)}"
    if bcc_list:
        response += f"\nBCC: {', '.join(bcc_list)}"
    
    if all_attached:
        response += f"\n\n✓ Attachments Sent: {', '.join(all_attached)}"
    
    if all_missing:
        response += f"\n\n✗ Missing Files (not attached): {', '.join(all_missing)}"
        response += f"\n   Please check file paths. Use 'list_attachments' tool to browse available files."
    
    return response


@mcp.tool()
def list_attachments(directory: str = "") -> str:
    """List available files that can be attached to emails. Helps users find files to attach.

    Args:
        directory: Optional directory path to search (default: workspace root d:/mcp_claude/)
                  Common options: "d:/documents", "d:/downloads", "d:/desktop", etc.
    
    Returns:
        List of files with their full paths for easy copying into attachment parameter
    """
    if not directory:
        directory = os.path.dirname(__file__)
    
    if not os.path.isdir(directory):
        return f"Error: Directory not found: {directory}"
    
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                size_str = f"{size:,} bytes" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                files.append(f"File: {item} ({size_str})\n   Path: {item_path}")
        
        if not files:
            return f"No files found in: {directory}"
        
        result = f"Files in {directory}:\n\n"
        result += "\n\n".join(files[:20])  # Limit to 20 files
        
        if len(files) > 20:
            result += f"\n\n... and {len(files) - 20} more files"
        
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
def save_temp_file(filename: str, content: str, is_base64: bool = False) -> str:
    """Save content to a temporary file in workspace for email attachment.
    
    WORKFLOW: When user uploads a file to Claude chat:
    1. User uploads file to chat
    2. Claude reads the file content
    3. Call this tool with filename and content
    4. Use returned path in send_professional_email
    
    Args:
        filename: Name for the file (e.g., "document.txt", "report.pdf", "image.png")
        content: The file content (text or base64 encoded for binary files)
        is_base64: Set to True if content is base64 encoded (for PDFs, images, etc.)
    
    Returns:
        Full path to saved file, ready to use in send_professional_email attachments parameter
    
    Example:
        User uploads "report.pdf" to chat
        → save_temp_file("report.pdf", "<base64_content>", is_base64=True)
        → Returns path like "d:/mcp_claude/temp_attachments/report.pdf"
        → Use in email: attachments="d:/mcp_claude/temp_attachments/report.pdf"
    """
    try:
        import base64
        
        workspace_dir = os.path.dirname(__file__)
        temp_dir = os.path.join(workspace_dir, "temp_attachments")
        
        # Create temp directory if it doesn't exist
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        file_path = os.path.join(temp_dir, filename)
        
        # Save file based on type
        if is_base64:
            # Decode base64 and save as binary
            file_data = base64.b64decode(content)
            with open(file_path, 'wb') as f:
                f.write(file_data)
        else:
            # Save as text
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        file_size = os.path.getsize(file_path)
        size_str = f"{file_size:,} bytes" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f} MB"
        
        return f"""✓ File saved successfully!

File: {filename}
Size: {size_str}
Path: {file_path}

To attach this file to an email, use:
attachments="{file_path}"

Example:
send_professional_email(
    main_idea="Please review the attached document",
    recipients="user@example.com",
    attachments="{file_path}"
)"""
    except Exception as e:
        return f"Error saving file: {str(e)}"


if __name__ == "__main__":
    import sys
    import logging
    
    # Suppress all logging to stdout/stderr except critical errors
    logging.getLogger().setLevel(logging.CRITICAL)
    logging.getLogger('google').setLevel(logging.CRITICAL)
    logging.getLogger('googleapiclient').setLevel(logging.CRITICAL)
    
    # Ensure proper stdio encoding for Windows
    if sys.platform == "win32":
        import io
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)
    
    mcp.run(transport="stdio")
