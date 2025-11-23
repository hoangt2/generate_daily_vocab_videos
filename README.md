# Finnish Daily Vocabulary Video Generator

An automated tool that generates Finnish vocabulary words with AI-powered video prompts and TikTok captions for language learning content creation.

## Overview

This project uses Google's Gemini AI to generate daily Finnish vocabulary words (A1-B1 level) and automatically creates:
- **Video generation prompts** for 8-second TikTok-style educational videos
- **Engaging TikTok captions** with examples, tips, and hashtags
- **Organized Google Sheets** storage with all vocabulary data

Perfect for content creators, language teachers, or anyone building Finnish language learning materials.

## Features

- 🎯 **Smart Vocabulary Generation**: Generates random Finnish words at A1-B1 levels with English translations
- 🎬 **Video Prompt Creation**: AI-generated scene descriptions for visual learning content
- 📱 **TikTok-Ready Captions**: Engaging social media captions with examples and cultural tips
- 📊 **Google Sheets Integration**: Automatic storage and organization of all vocabulary data
- 🔄 **Duplicate Prevention**: Tracks existing words to avoid repetition
- 🎨 **Consistent Style**: Prompts follow a warm, modern flat-vector illustration style
- 📏 **Fixed Formatting**: Maintains consistent row heights and formatting in spreadsheets

## Prerequisites

- Python 3.7+
- Google Cloud Project with Sheets API enabled
- Google Gemini API key
- Service account credentials for Google Sheets

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd generate_daily_vocab_videos
   ```

2. **Set up a virtual environment (Recommended)**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install google-generativeai google-auth gspread gspread-formatting python-dotenv
   ```

4. **Set up Google Cloud credentials**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Create a service account and download `credentials.json`
   - Place `credentials.json` in the project root

5. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
   SPREADSHEET_NAME=Daily Vocabulary
   VOCAB_COUNT=10
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Google Gemini API key | *Required* |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash` |
| `GOOGLE_SHEETS_CREDENTIALS_FILE` | Path to service account credentials | `credentials.json` |
| `SPREADSHEET_NAME` | Name of the Google Sheets spreadsheet | `Daily Vocabulary` |
| `VOCAB_COUNT` | Number of words to generate per run | `10` |

## Usage

Run the script to generate vocabulary words:

```bash
python generate_daily_vocab_video_prompts.py
```

The script will:
1. Connect to Google Sheets (creates spreadsheet if it doesn't exist)
2. Check for existing words to prevent duplicates
3. Generate new Finnish vocabulary words with translations
4. Create video prompts for each word
5. Generate TikTok captions with examples and tips
6. Save everything to Google Sheets

## Google Sheets Structure

The generated spreadsheet contains the following columns:

| Column | Description |
|--------|-------------|
| Date Added | Date when the word was generated |
| Finnish Word | The Finnish vocabulary word |
| English Translation | English meaning |
| Category | Word category (noun, verb, daily life, etc.) |
| Level | Difficulty level (A1, A2, or B1) |
| Example Sentence | Finnish example with English translation |
| Video Prompt | AI-generated scene description for video creation |
| Video Caption | TikTok-ready caption with hashtags |

## Video Prompt Style

Generated video prompts follow these guidelines:
- **Duration**: 8-second scenes
- **Style**: Warm, modern flat-vector illustration with soft pastel colors
- **Audio**: Finnish dialogue with Helsinki region accent
- **Content**: Natural daily life situations
- **Length**: Under 3000 characters for compatibility

## Example Output

**Finnish Word**: kirjasto  
**Translation**: library  
**Level**: A2  
**Category**: noun  

**Video Prompt**: [8-second scene description with characters, dialogue, and visual style]

**Caption**:
```
✨ Finnish Word of the Day ✨

📖 **kirjasto** (noun) → library

💬 Example:
[fi]: "Mennään tänään kirjastoon."
[en]: "Let's go to the library today."

🔎 Quick Tip
Finnish place endings change the meaning:
- kirjastossa = in the library
- kirjastoon = to the library
- kirjastosta = from the library

📌 #FinnishWordOfTheDay #LearnFinnish #suomi
```

## Project Structure

```
generate_daily_vocab_videos/
├── generate_daily_vocab_video_prompts.py  # Main script
├── credentials.json                        # Google service account credentials
├── .env                                    # Environment variables
├── .gitignore                             # Git ignore rules
└── README.md                              # This file
```

## Troubleshooting

**"Spreadsheet not found" error**  
The script will automatically create a new spreadsheet if it doesn't exist.

**Duplicate words being generated**  
The script checks existing words, but if you want to reset, you can delete rows from the spreadsheet.

**API quota exceeded**  
Reduce `VOCAB_COUNT` in `.env` or wait for quota reset.

## License

This project is provided as-is for educational and content creation purposes.

## Contributing

Feel free to submit issues or pull requests for improvements!