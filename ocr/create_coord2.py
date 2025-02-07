import pytesseract
from PIL import Image
import pandas as pd
import re

def image_to_csv_with_lines(image_path, csv_path, tesseract_cmd=None, language='spa'):
    """
    Extracts text from an image using pytesseract and saves the results to a CSV file.

    The CSV file includes the x, y coordinates, width, height, text of each character,
    and the line number it belongs to.  Spaces are included as characters.

    Args:
        image_path: Path to the input image.
        csv_path: Path to the output CSV file.
        tesseract_cmd: (Optional) Path to the tesseract executable.  Only needed if
                       tesseract is not in your system's PATH.  Example:
                       r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        language: (Optional) The language of the text in the image. Defaults to 'spa' (Spanish).
                  Use the appropriate Tesseract language code (e.g., 'eng' for English, 'fra' for French).
    """

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise Exception(f"Error opening image: {e}")

    # Use pytesseract to get bounding box information, specifying the language.
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.STRING, config='--psm 6', lang=language)

    # Parse the TSV data
    lines = data.splitlines()
    header = lines[0].split('\t')
    data_rows = [line.split('\t') for line in lines[1:]]

    # Create a Pandas DataFrame
    df = pd.DataFrame(data_rows, columns=header)

    # Convert numeric columns
    numeric_cols = ['left', 'top', 'width', 'height', 'conf', 'line_num']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['text'], inplace=True)  # Remove rows with missing text (NaN)
    df = df[df['conf'] != -1] # Keep only confident characters

    # --- Character-Level Processing ---
    char_data = []
    for _, row in df.iterrows():
        text = row['text']
        x = row['left']
        y = row['top']
        width = row['width']
        height = row['height']
        line_num = row['line_num']

        #  Handle spaces and multi-character boxes.
        if len(text) >= 1:  # >= 1 now includes spaces and single chars.
            char_width = width / len(text)
            for i, char in enumerate(text):
                char_x = x + (i * char_width)
                char_data.append([char_x, y, char_width, height, char, line_num])


    # Create character DataFrame
    char_df = pd.DataFrame(char_data, columns=['left', 'top', 'width', 'height', 'text', 'line_num'])

    # --- Save to CSV ---
    char_df.to_csv(csv_path, index=False)
    print(f"Character data saved to: {csv_path}")



# Example Usage
try:
    image_to_csv_with_lines("pagina_1.png", "output.csv", language='spa')  # Specify Spanish
    # Example with custom tesseract path and language:
    # image_to_csv_with_lines("image.png", "output.csv", r'C:\Program Files\Tesseract-OCR\tesseract.exe', 'spa')
except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
