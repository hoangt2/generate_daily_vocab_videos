import google.generativeai as genai
from google.oauth2.service_account import Credentials
import gspread
# 🛠️ CORRECTED IMPORTS: Removed set_text_format, set_data_validation, get_default_format
from gspread_formatting import set_row_height, cellFormat, format_cell_range 
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Ensure GEMINI_MODEL is set or defaults to a good one
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash") 
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Daily Vocabulary")
# Update column index since 'Starting Date' is removed and 'Date Added' is now column 1 ('A')
FINNISH_WORD_COLUMN_INDEX = 2 # 'B' column for 'Finnish Word' in 1-based index
VOCAB_COUNT=int(os.getenv("VOCAB_COUNT", 10)) # Default to 10 words if not set

def setup_gemini():
    """Initialize Gemini API"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    return model

def setup_google_sheets():
    """
    Initialize Google Sheets connection and set up the sheet.
    This version ensures headers are always present and correct.
    """
    # 🆕 UPDATED HEADERS: Added 'Video Caption'
    headers = [
        'Date Added', 'Finnish Word', 'English Translation', 
        'Category', 'Level', 'Example Sentence', 'Video Prompt', 'Video Caption'
    ]
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials for service account
    creds = Credentials.from_service_account_file(
        GOOGLE_SHEETS_CREDENTIALS_FILE, 
        scopes=scope
    )
    client = gspread.authorize(creds)
    
    # Open or create spreadsheet
    try:
        # 1. Sheet exists: open it
        spreadsheet = client.open(SPREADSHEET_NAME)
        sheet = spreadsheet.sheet1
        print(f"Spreadsheet '{SPREADSHEET_NAME}' opened.")
        
    except gspread.SpreadsheetNotFound:
        # 2. Sheet does not exist: create it
        print(f"Spreadsheet '{SPREADSHEET_NAME}' not found. Creating a new one.")
        spreadsheet = client.create(SPREADSHEET_NAME)
        sheet = spreadsheet.sheet1
        
    
    # --- Check and set headers in the first row (A1 to H1) ---
    try:
        # Read the current first row's values
        current_headers = sheet.row_values(1)
    except IndexError:
        # Handles a completely empty sheet
        current_headers = []
        
    if current_headers != headers:
        print("Adding/Correcting headers in the first row.")
        
        # Use gspread's batch update to set headers in row 1
        cell_list = sheet.range(f'A1:{gspread.utils.rowcol_to_a1(1, len(headers))}')
        for i, val in enumerate(headers):
            cell_list[i].value = val
        sheet.update_cells(cell_list, value_input_option='USER_ENTERED')
        
        if len(current_headers) == 0:
              print("Spreadsheet created with correct headers.")
              
    # -----------------------------------------------------------
    
    return sheet

def get_existing_words(sheet):
    """Retrieves all existing Finnish words from the sheet to prevent duplicates."""
    try:
        # Get all values from the 'Finnish Word' column (column B, index 2)
        column_data = sheet.col_values(FINNISH_WORD_COLUMN_INDEX)
        # Skip the header row and return the set of existing words for fast lookups
        return set(word.strip().lower() for word in column_data[1:])
    except Exception as e:
        print(f"Could not retrieve existing words: {e}")
        # Return an empty set if an error occurs
        return set() 

def generate_finnish_vocabulary(model, existing_words, count=10):
    """Generate random Finnish words using Gemini, filtering out existing ones."""
    
    if existing_words:
        existing_list = list(existing_words)[:5]
        exclude_hint = f" Do NOT use any of these words: {', '.join(existing_list)}."
    else:
        exclude_hint = ""

    # UPDATED PROMPT: Requesting Level (A1-B1)
    prompt = f"""Generate {count} random Finnish vocabulary words suitable for daily learning between levels A1 to B1.
    {exclude_hint}
    For each word, provide:
    1. The Finnish word
    2. English translation
    3. Category (e.g., noun, verb, adjective, daily life, food, nature, etc.)
    4. **Level (A1, A2, or B1)**
    5. A simple example sentence in Finnish with English translation
    
    Format the response as JSON array with objects containing: 
    finnish_word, english_translation, category, **level**, example_finnish, example_english
    
    Make the words varied and useful for beginners to intermediate learners."""
    
    response = model.generate_content(prompt)
    
    # Parse the JSON response
    text = response.text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    
    try:
        vocabulary = json.loads(text.strip())
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from model response: {e}")
        print(f"Raw response text: {text[:200]}...")
        return []
    
    # POST-PROCESSING: Filter out duplicates and ensure data structure
    new_vocabulary = []
    for item in vocabulary:
        if 'finnish_word' not in item:
            print(" ⚠️ Skipping item due to missing 'finnish_word' key.")
            continue
            
        finnish_word = item['finnish_word'].strip().lower()
        if finnish_word not in existing_words:
            new_vocabulary.append(item)
            existing_words.add(finnish_word)
        else:
            print(f" ⚠️ Skipping duplicate word: {item['finnish_word']}")
            
    return new_vocabulary

def generate_video_prompt(model, word_data):
    """Generate a video generation prompt for the vocabulary word"""
    prompt = f"""
    You are a creative TikTok scriptwriter. Your task is to generate a video prompt for Finnish word of the day. 
    Create a simple scene to illustrate for the word: {word_data['finnish_word']} which means "{word_data['english_translation']}". 
    Characters speak clearly in Finnish and grammatically correct. 
    
    The short scene should be about common daily life situation and easy to illustrate.
    Make the conversation sounds natural. 
    The main word just need to appear once in the speech, no need to repeat it. 
    The conversation should begin right in the first second to get the audience attention.

    * Strictly no text or subtitles included in the video. 
    
    *Also Include the following details in your response:
    Scene Duration: 8 seconds

    Illustration style:
    Use a warm, modern flat-vector illustration style with soft pastel colors, clean lines, and simple but expressive facial features. 
    Think of a style that could be used in educational flashcards or language-learning apps—playful yet clear, conveying both the action and the meaning.

    Audio:
    Characters say their lines exactly as in the scene description and match with their actions and they speak Finnish in Helsinki region accent
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_video_caption(model, word_data):
    """Generate an engaging TikTok caption for the vocabulary word."""
    finnish_word = word_data['finnish_word']
    english_translation = word_data['english_translation']
    level = word_data['level']
    
    prompt = f"""
    You are a TikTok content strategist. 
    Create a short, engaging TikTok caption for a video teaching the Finnish word **{finnish_word}** (meaning "{english_translation}"). 
    The target audience is A1-{level} Finnish learners.

    Do not use JSON formatting. Just provide the raw caption text.
    
    Below is the example as template, put the whole post with proper format in a "caption".
    Make sure the Quick Tip feels fresh and varied each day (sometimes grammar endings, sometimes synonyms, related words, cultural notes, fun facts, etc.).

    ✨ Finnish Word of the Day ✨

    📖 **kirjasto** (noun) → library

    💬 Example:
    [fi]: "Mennään tänään kirjastoon."
    [en]: “Let’s go to the library today.”

    🔎 Quick Tip
    Finnish place endings change the meaning:
    - kirjastossa = in the library
    - kirjastoon = to the library
    - kirjastosta = from the library

    🎭 What’s the best thing you’ve borrowed from a library? 📚

    📌 #FinnishWordOfTheDay #LearnFinnish #suomi #suomenkieli  #LanguageTok #FinnishLanguage #kirjasto #LanguageLearning
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()


def save_to_sheets(sheet, vocabulary_data):
    """Save vocabulary data to Google Sheets, using a single 'Date Added' column."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    rows = []
    for item in vocabulary_data:
        example_sentence = f"{item.get('example_finnish', '')} ({item.get('example_english', '')})"
        
        row = [
            current_date, 
            item.get('finnish_word', ''),
            item.get('english_translation', ''),
            item.get('category', ''),
            item.get('level', ''), 
            example_sentence,
            item.get('video_prompt', ''),
            item.get('video_caption', '')
        ]
        rows.append(row)
    
    if rows:
        sheet.append_rows(rows)
        print(f"Successfully added {len(rows)} **new** vocabulary words to Google Sheets")
    else:
        print("No new vocabulary words to add.")

def apply_fixed_row_height(sheet, pixel_size=50):
    """
    Sets a fixed row height for all data rows (starting from row 2) 
    and ensures text wrapping is disabled.
    """
    
    # Set fixed row height (e.g., 50 pixels) for all rows from row 2 onwards
    print(f"Applying fixed row height of {pixel_size} pixels...")
    
    # Set row height for rows 2 to the current last row
    
    # Get the total number of rows currently in the sheet
    max_rows = sheet.row_count
    
    try:
        # Set a fixed height for all rows from 2 to the end
        set_row_height(sheet, f'2:{max_rows}', pixel_size)
        
        # Optionally, apply 'CLIP' text wrapping to prevent expansion
        # This is the key to stopping the row height changing with content
        clip_format = cellFormat(wrapText=False) 
        format_cell_range(sheet, f'A2:{gspread.utils.rowcol_to_a1(max_rows, len(sheet.row_values(1)))}', clip_format)

    except Exception as e:
        print(f"Error applying row height: {e}")

def main():
    """Main function to run the vocabulary generator"""
    
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set in environment variables/dotenv file.")
        return
        
    print("Initializing Gemini...")
    model = setup_gemini()
    
    print("Connecting to Google Sheets...")
    sheet = setup_google_sheets()
    
    print("Checking for existing vocabulary words to prevent duplicates...")
    existing_words = get_existing_words(sheet)
    print(f"Found {len(existing_words)} existing words in the sheet.")
    
    print("Generating Finnish vocabulary...")
    vocabulary = generate_finnish_vocabulary(model, existing_words, count=VOCAB_COUNT) 
    
    if not vocabulary:
        print("No new unique words were generated. Exiting.")
        return
        
    print(f"Generated {len(vocabulary)} unique words.")
    
    print("Generating video prompts and captions...") # 🔄 Updated status message
    for item in vocabulary:
        word = item.get('finnish_word', 'Unknown Word')
        print(f"  Processing prompt for: {word}")
        
        # 1. Generate Video Prompt (Original step)
        video_prompt = generate_video_prompt(model, item)
        item['video_prompt'] = video_prompt
        
        # 2. 🆕 Generate Video Caption (New step)
        print(f"  Processing caption for: {word}")
        video_caption = generate_video_caption(model, item)
        item['video_caption'] = video_caption # Store the new caption
        
    
    print("Saving to Google Sheets...")
    save_to_sheets(sheet, vocabulary)

    apply_fixed_row_height(sheet, pixel_size=50)
    
    print("\n🎉 **Complete!** Your Finnish vocabulary has been saved to Google Sheets.")
    print(f"Generated {len(vocabulary)} new, unique words with video prompts and captions.")

if __name__ == "__main__":
    main()