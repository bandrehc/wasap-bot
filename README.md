# Wasap Bot - Automated Message Sender

Automated WhatsApp message sender using Selenium WebDriver (SPANISH VERSION). Send personalized messages to multiple contacts from a CSV file with customizable message templates.

## Features

- 📨 Send personalized WhatsApp messages from CSV file
- 🎯 Multiple message templates support
- 🔄 Automatic retry mechanism for failed sends
- 📊 Detailed logging and statistics
- 🛡️ Robust error handling
- 🔧 Customizable and extensible message templates

## Requirements

- Python 3.7+
- Firefox browser
- Firefox profile with active WhatsApp Web session (recommended)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/wasap-bot.git
cd whatsapp-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Firefox WebDriver**

The script uses Firefox. Make sure you have Firefox installed on your system.

## Configuration

### Setting up Firefox Profile (Recommended)

To avoid scanning the QR code every time:

1. Create a dedicated Firefox profile:
   - Open Firefox
   - Type `about:profiles` in the address bar
   - Click "Create a New Profile"
   - Name it (e.g., "WhatsAppBot")
   - Note the profile path

2. Log into WhatsApp Web with this profile:
   - Launch Firefox with the new profile
   - Go to https://web.whatsapp.com
   - Scan the QR code
   - Close Firefox

3. Use the profile path when running the bot

## Usage

### Basic Usage

```bash
python wasapy.py contacts.csv
```

### With Custom Template

```bash
python wasapy.py contacts.csv --template promotional
```

### With Firefox Profile

```bash
python wasapy.py contacts.csv --profile "/path/to/firefox/profile"
```

### Combined Options

```bash
python wasapy.py contacts.csv -t event_invitation -p "/path/to/profile"
```

## CSV File Format

Create a CSV file with the following columns:

```csv
Numero,Nombre
+51987654321,Juan Pérez
+51912345678,María González
+51998765432,Carlos Rodríguez
```

**Important:**
- Column headers must be exactly: `Numero` and `Nombre`
- Include country code in phone numbers (e.g., +51 for Peru)
- Use UTF-8 encoding for the CSV file

## Message Templates

The bot includes several pre-built templates in `message_templates.py`:

### Available Templates

1. **default** - Event sponsorship invitation
2. **promotional** - Generic promotional message
3. **event_invitation** - Event invitation with details
4. **followup** - Follow-up on previous conversations
5. **thankyou** - Thank you message

### Creating Custom Templates

Edit `message_templates.py` and add your own template:

```python
def my_custom_template(**kwargs):
    nombre = kwargs.get('nombre', 'Estimado/a')
    # Add your custom variables
    custom_var = kwargs.get('custom_var', 'default value')
    
    return f"""Hello {nombre},
    
Your custom message here with {custom_var}

Best regards."""

# Register the template
AVAILABLE_TEMPLATES["my_custom"] = my_custom_template
```

Then use it:
```bash
python wasapy.py contacts.csv --template my_custom
```

## Command Line Arguments

```
usage: wasapy.py [-h] [--template TEMPLATE] [--profile PROFILE] csv_file

positional arguments:
  csv_file              Path to CSV file with Numero and Nombre columns

optional arguments:
  -h, --help            show this help message and exit
  --template TEMPLATE, -t TEMPLATE
                        Message template name (default: 'default')
  --profile PROFILE, -p PROFILE
                        Firefox profile path
```

## Logging

The bot creates a log file `wasapy.log` with detailed information about:
- Messages sent successfully
- Failed attempts and errors
- Retry mechanisms
- Final statistics

## Output Example

```
2025-10-04 10:30:15 - INFO - STARTING WhatsApp Bot
2025-10-04 10:30:15 - INFO - CSV File: contacts.csv
2025-10-04 10:30:15 - INFO - Message Template: default
2025-10-04 10:30:20 - INFO - Firefox started successfully
2025-10-04 10:30:25 - INFO - PROCESSING 1 - Number: +51987654321, Name: Juan Pérez
2025-10-04 10:30:35 - INFO - SUCCESS - Personalized message sent to Juan Pérez
2025-10-04 10:30:38 - INFO - CONTACT 1 COMPLETED - Success: 1/1
...
==================================================
FINAL SUMMARY
Total contacts processed: 50
Messages sent successfully: 48
Failed messages: 2
Success rate: 96.0%
PROCESS COMPLETED
==================================================
```

## Safety Features

- **Rate limiting**: 3-second delay between messages to avoid spam detection
- **Retry mechanism**: Automatic retry (up to 2 attempts) for failed sends
- **Error handling**: Comprehensive error catching and logging
- **State management**: Automatic reset between contacts

## Troubleshooting

### Common Issues

**QR Code appears every time**
- Solution: Use a Firefox profile with saved WhatsApp Web session

**Messages not sending**
- Check CSV file format and encoding (must be UTF-8)
- Verify phone numbers include country code
- Ensure WhatsApp Web is properly loaded

**Firefox profile not found**
- Verify the profile path is correct
- Use absolute path instead of relative path

**Contact not found**
- Ensure phone number format is correct
- Number must be registered on WhatsApp

### Debug Mode

For more detailed logs, edit `setup_logging()` in `wasapy.py`:
```python
level=logging.DEBUG  # Change from INFO to DEBUG
```

## Limitations

- Requires active internet connection
- WhatsApp Web must be accessible
- Subject to WhatsApp's usage policies and rate limits
- Recommended to send messages in small batches

## Legal Notice

**Important**: Use this tool responsibly and in compliance with:
- WhatsApp Terms of Service
- Local spam and privacy laws
- GDPR and data protection regulations

Do not use this tool for:
- Unsolicited marketing (spam)
- Harassment
- Any illegal activities

The authors are not responsible for misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Selenium WebDriver](https://www.selenium.dev/)
- Inspired by the need for efficient WhatsApp communication

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---


**Disclaimer**: This is an unofficial tool and is not affiliated with WhatsApp or Meta Platforms, Inc.
