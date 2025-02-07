import pytesseract
from PIL import Image
import pandas as pd

def image_to_csv_with_lines_and_words(image_path, csv_path, tesseract_cmd=None, language='spa'):
    """
    Extracts text from an image using pytesseract and saves detailed character
    information to a CSV file.

    The CSV includes coordinates (start, end, center), line number, word number,
    and character number within the word.  Spaces are included and associated
    with the preceding word.

    Args:
        image_path: Path to the input image.
        csv_path: Path to the output CSV file.
        tesseract_cmd: (Optional) Path to the tesseract executable.
        language: (Optional) Tesseract language code (default: 'spa').
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise Exception(f"Error opening image: {e}")

    # OCR and get data
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.STRING, config='--psm 6', lang=language)

    # Parse TSV data
    lines = data.splitlines()
    header = lines[0].split('\t')
    data_rows = [line.split('\t') for line in lines[1:]]
    df = pd.DataFrame(data_rows, columns=header)

    # Convert to numeric and clean data
    numeric_cols = ['left', 'top', 'width', 'height', 'conf', 'line_num', 'word_num']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['text'], inplace=True)
    df = df[df['conf'] != -1]

    # --- Character-Level Processing with Word Association ---
    char_data = []
    word_number = 0  # Initialize word counter
    for _, row in df.iterrows():
        text = row['text']
        x_start = row['left']
        y_start = row['top']
        width = row['width']
        height = row['height']
        line_num = int(row['line_num'])  # Ensure integer

        if text.strip() != "":  # If not just whitespace, increment word number
              word_number = int(row['word_num'])

        char_width = width / len(text)
        for i, char in enumerate(text):
            x_end = x_start + char_width
            y_end = y_start + height
            x_center = (x_start + x_end) / 2
            y_center = (y_start + y_end) / 2
            char_num_in_word = i + 1 # character number in the current word.

            char_data.append([
                char,
                x_start,
                y_start,
                x_end,
                y_end,
                line_num,
                word_number,
                char_num_in_word,
                x_center,
                y_center
            ])
            x_start = x_end  # Update x_start for the next character


    # Create character DataFrame
    char_df = pd.DataFrame(char_data, columns=[
        'Character', 'X_Start', 'Y_Start', 'X_End', 'Y_End',
        'Line_Number', 'Word_Number', 'Char_Number_in_Word', 'X_Center', 'Y_Center'
    ])

    # --- Save to CSV ---
    char_df.to_csv(csv_path, index=False)
    print(f"Character data saved to: {csv_path}")


# Example Usage
try:
    image_to_csv_with_lines_and_words("pagina_1.png", "output.csv", language='spa')
    # image_to_csv_with_lines_and_words("image.png", "output.csv", r'C:\Program Files\Tesseract-OCR\tesseract.exe', 'spa')
except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
