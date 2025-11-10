# 📧 Professional Email Sender MCP Server

Send professional emails to multiple recipients directly from Claude Desktop! Just provide a short idea and email addresses — AI automatically enhances it into a polished email with proper subject, greeting, and sign-off.

## ✨ Features

- **AI-Enhanced Emails**: Converts short ideas into professional, well-structured emails
- **Multiple Recipients**: Send to many people individually (no group exposure)
- **Powered by Gemini**: Uses Google's Gemini AI for natural language enhancement
- **SMTP Support**: Works with Gmail, Outlook, or any SMTP server
- **Customizable Tone**: Professional, friendly, or formal
- **CC/BCC Support**: Optional carbon copy recipients
- **Full Transparency**: Shows the enhanced email content before sending
- **Claude Desktop Integration**: Seamless MCP tool integration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **FastMCP** - Lightweight, modern MCP server framework
- **python-dotenv** - Environment variable management
- **google-generativeai** - Gemini AI for email enhancement

### 2. Configure SMTP Credentials

Edit the `.env` file with your email settings:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_NAME=Your Name
GEMINI_API_KEY=your-gemini-api-key
```

#### For Gmail:
1. Enable 2-factor authentication
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use the 16-character app password as `SMTP_PASSWORD`

#### For Gemini:
1. Get API key from: https://aistudio.google.com/app/apikey
2. Add it to your `.env` file as `GEMINI_API_KEY`

### 3. Test the Server

```bash
python main.py
```

The server will start and wait for MCP connections from Claude Desktop. If it starts without errors, it's working correctly!

### 4. Configure Claude Desktop

Add this to your Claude Desktop MCP settings file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "email-sender": {
      "command": "python",
      "args": ["d:\\mcp_claude\\main.py"]
    }
  }
}
```

### 5. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

## 💬 Usage Examples

### Basic Email
```
Send email to alice@company.com: We finished the report early with 3 key insights.
```

### Multiple Recipients
```
Send email to alice@company.com, bob@team.org, charlie@corp.com: The new dashboard is live and ready for testing.
```

### With CC/BCC
```
Send email to team@company.com with CC manager@company.com: Project milestone reached ahead of schedule.
```

### Different Tone
```
Send a friendly email to colleague@company.com: Thanks for the help on the presentation!
```

## 🔧 How It Works

1. **User provides**: Short main idea + recipient emails
2. **AI enhances**: Gemini generates professional subject, greeting, body, and closing
3. **Email sends**: Each recipient gets their own individual copy via SMTP
4. **Confirmation**: Shows the sent email content and delivery status

## 📋 Example Output

```
✓ Email Sent Successfully

Subject: Project Update - Report Completed Early

Recipients: 2 (2 sent, 0 failed)

--- Email Content ---
Hello,

I'm pleased to inform you that we've completed the quarterly report ahead of schedule. The analysis includes three key insights that will be valuable for our strategic planning. Please review the findings at your earliest convenience.

Best regards,
Your Name
--------------------

Delivery Status:
✓ alice@company.com: Email sent to alice@company.com
✓ bob@team.org: Email sent to bob@team.org
```

## 🛠️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server address | smtp.gmail.com |
| `SMTP_PORT` | SMTP port | 587 |
| `SMTP_EMAIL` | Your email address | Required |
| `SMTP_PASSWORD` | App password or SMTP password | Required |
| `SENDER_NAME` | Display name for sender | Professional Sender |
| `GEMINI_API_KEY` | Google Gemini API key | Required |

## 🔐 Security Notes

- Never commit `.env` file to version control
- Use app-specific passwords (not your main email password)
- `.env` is already in `.gitignore`
- Keep your API keys private

## 🐛 Troubleshooting

### "Error: SMTP credentials not configured"
- Check that `.env` file exists and contains valid credentials
- Verify `SMTP_EMAIL` and `SMTP_PASSWORD` are set

### "Authentication failed"
- For Gmail: Use app password, not regular password
- Enable 2-factor authentication first
- Generate new app password if needed

### "AI enhancement failed"
- Check `GEMINI_API_KEY` is valid
- Verify internet connection
- Server will use fallback enhancement if AI fails

### "No valid recipients"
- Use comma-separated email addresses
- Check email format: `user@domain.com`

## 📝 Requirements

- Python 3.8+
- Active SMTP email account (Gmail recommended)
- Google Gemini API key
- Claude Desktop

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Support

Issues? Check:
1. `.env` file is configured correctly
2. SMTP credentials are valid (test with email client)
3. Gemini API key is active
4. Claude Desktop MCP config is correct

---

**Ready to send professional emails with AI! 🚀**
