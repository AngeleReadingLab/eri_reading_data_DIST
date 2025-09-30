import pytesseract
from PIL import Image, ImageDraw
import pandas as pd
import io
import csv
import os

def recognize_text(image_path, tesseract_config='--psm 6 -l spa'):
    """
    Performs OCR on an image and returns a DataFrame with character bounding boxes
    and associated information.

    Args:
        image_path: Path to the image file.
        tesseract_config: Configuration string for pytesseract (e.g., '--psm 6 -l spa').

    Returns:
        pandas.DataFrame: DataFrame containing character-level data (df_word_chars).
    """

    image = Image.open(image_path).convert('RGB')
    image_height = image.height

    # Extract filename for trial_id
    trial_id = os.path.splitext(os.path.basename(image_path))[0]

    # Use pytesseract to extract data for words and characters
    data_words = pytesseract.image_to_data(image, config=tesseract_config)
    data_chars = pytesseract.image_to_boxes(image, config=tesseract_config)

    df_words = pd.read_csv(io.StringIO(data_words), sep='\t', quoting=csv.QUOTE_NONE)
    df_chars = pd.read_csv(io.StringIO(data_chars), sep=' ', header=None, names=['char', 'left', 'top', 'right', 'bottom', 'unknown'])

    # Fix character coordinates
    for index, row in df_chars.iterrows():
        original_top = int(row['top'])
        original_bottom = int(row['bottom'])
        df_chars.at[index, 'top'] = image_height - original_bottom
        df_chars.at[index, 'bottom'] = image_height - original_top

    # Create DataFrame to store spaces
    df_spaces = pd.DataFrame(columns=['level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text'])

    # Group words by line, block, and paragraph
    grouped_lines = df_words.groupby(['block_num', 'par_num', 'line_num'])

    for (block_num, par_num, line_num), line_words_df in grouped_lines:
        sorted_words = line_words_df.sort_values(by='left')
        previous_word = None
        for index, current_word in sorted_words.iterrows():
            if previous_word is not None:
                space_left = int(previous_word['left']) + int(previous_word['width'])
                space_width = int(current_word['left']) - space_left
                if space_width > 0:
                    space_top = int(previous_word['top'])
                    space_height = int(previous_word['height'])
                    space_data = {
                        'level': 5,
                        'page_num': int(current_word['page_num']),
                        'block_num': int(current_word['block_num']),
                        'par_num': int(current_word['par_num']),
                        'line_num': int(current_word['line_num']),
                        'word_num': int(previous_word['word_num']),
                        'left': space_left,
                        'top': space_top,
                        'width': space_width,
                        'height': space_height,
                        'conf': 0,
                        'text': ' '
                    }
                    df_spaces = pd.concat([df_spaces, pd.DataFrame(space_data, index=[0])], ignore_index=True)
            previous_word = current_word

    # Create DataFrame for characters within words (and spaces)
    df_word_chars = pd.DataFrame(columns=['char', 'char_xmin', 'char_ymin', 'char_xmax', 'char_ymax',
                                         'block', 'paragraph', 'line_number',
                                         'word_nr', 'letter_nr', 'word',
                                         'char_x_center', 'char_y_center', 'assigned_line', 'trial_id'])


    for index_word, row_word in df_words.iterrows():
        if isinstance(row_word['text'], str) and row_word['text'].strip() and row_word['level'] == 5:
            word_left = int(row_word['left'])
            word_top = int(row_word['top'])
            word_width = int(row_word['width'])
            word_height = int(row_word['height'])
            word_right = word_left + word_width
            word_bottom = word_top + word_height
            word_text = row_word['text']

            char_index_in_word = 0
            relevant_chars = df_chars[
                (df_chars['left'] >= word_left) & (df_chars['right'] <= word_right) &
                (df_chars['top'] >= word_top) & (df_chars['bottom'] <= word_bottom)
            ]
            relevant_chars = relevant_chars.sort_values(by='left')
            previous_char_right = word_left

            for index_char, row_char in relevant_chars.iterrows():
                char_text = row_char['char']
                char_left = previous_char_right
                char_right = int(row_char['right'])
                char_right = min(char_right, word_right)
                if char_left > char_right:
                    char_right = int(row_char['right'])
                char_top = word_top
                char_bottom = word_bottom

                char_data = {
                    'char': char_text,
                    'char_xmin': int(round(char_left)),  # Round and convert to int
                    'char_ymin': int(round(char_top)),   # Round and convert to int
                    'char_xmax': int(round(char_right)),  # Round and convert to int
                    'char_ymax': int(round(char_bottom)), # Round and convert to int
                    'block': int(row_word['block_num']),
                    'paragraph': int(row_word['par_num']),
                    'line_number': int(row_word['line_num']),
                    'word_nr': int(row_word['word_num']),
                    'letter_nr': int(char_index_in_word), #already an int
                    'word': word_text,
                    'char_x_center': int(round((char_left + char_right) / 2)),  # Round and convert
                    'char_y_center': int(round((char_top + char_bottom) / 2)),  # Round and convert
                    'assigned_line': None,
                    'trial_id': trial_id
                }
                df_word_chars = pd.concat([df_word_chars, pd.DataFrame(char_data, index=[0])], ignore_index=True)
                char_index_in_word += 1
                previous_char_right = char_right

            spaces_following_word = df_spaces[
                (df_spaces['word_num'] == int(row_word['word_num'])) &
                (df_spaces['line_num'] == int(row_word['line_num'])) &
                (df_spaces['block_num'] == int(row_word['block_num'])) &
                (df_spaces['par_num'] == int(row_word['par_num']))
            ]

            for index_space, row_space in spaces_following_word.iterrows():
                space_data = {
                    'char': ' ',
                    'char_xmin': int(round(row_space['left'])),    # Round and convert
                    'char_ymin': int(round(row_space['top'])),     # Round and convert
                    'char_xmax': int(round(row_space['left'] + row_space['width'])),  # Round and convert
                    'char_ymax': int(round(row_space['top'] + row_space['height'])), # Round and convert
                    'block': int(row_space['block_num']),
                    'paragraph': int(row_space['par_num']),
                    'line_number': int(row_space['line_num']),
                    'word_nr': int(row_space['word_num']),
                    'letter_nr': int(char_index_in_word),  # Already int
                    'word': word_text,
                    'char_x_center': int(round((row_space['left'] + row_space['left'] + row_space['width']) / 2)), # Round
                    'char_y_center': int(round((row_space['top'] + row_space['top'] + row_space['height']) / 2)), # Round
                    'assigned_line': None,
                    'trial_id': trial_id
                }
                df_word_chars = pd.concat([df_word_chars, pd.DataFrame(space_data, index=[0])], ignore_index=True)
                char_index_in_word += 1

    # Create 'assigned_line' column
    df_word_chars['assigned_line'] = 0
    line_counter = 1
    for block_num in sorted(df_word_chars['block'].unique()):
        for par_num in sorted(df_word_chars.loc[df_word_chars['block'] == block_num, 'paragraph'].unique()):
            for line_num in sorted(df_word_chars.loc[(df_word_chars['block'] == block_num) & (df_word_chars['paragraph'] == par_num), 'line_number'].unique()):
                line_mask = (df_word_chars['line_number'] == line_num) & (df_word_chars['paragraph'] == par_num) & (df_word_chars['block'] == block_num)
                df_word_chars.loc[line_mask, 'assigned_line'] = line_counter
                line_counter += 1

    # Adjust Y_Start, Y_End, and char_y_center, converting to integers
    for assigned_line in df_word_chars['assigned_line'].unique():
        line_mask = (df_word_chars['assigned_line'] == assigned_line)
        min_top = df_word_chars.loc[line_mask, 'char_ymin'].min()
        max_bottom = df_word_chars.loc[line_mask, 'char_ymax'].max()
        new_y_center = (min_top + max_bottom) / 2
        df_word_chars.loc[line_mask, 'char_ymin'] = int(round(min_top))      # Round and convert
        df_word_chars.loc[line_mask, 'char_ymax'] = int(round(max_bottom))     # Round and convert
        df_word_chars.loc[line_mask, 'char_y_center'] = int(round(new_y_center)) # Round and convert

    # Convert relevant columns to integers
    int_columns = ['char_xmin', 'char_ymin', 'char_xmax', 'char_ymax', 'block', 'paragraph',
                   'line_number', 'word_nr', 'letter_nr', 'char_x_center', 'char_y_center', 'assigned_line']
    for col in int_columns:
        df_word_chars[col] = df_word_chars[col].astype(int)

    return df_word_chars


def draw_char_boxes(image_path, df_word_chars, output_path='output_boxes_combined.png'):
    """
    Draws bounding boxes around characters on the image.

    Args:
        image_path: Path to the image file.
        df_word_chars: DataFrame containing character bounding box data.
        output_path: Path to save the image with bounding boxes.  Defaults to 'output_boxes_combined.png'.
    """
    image = Image.open(image_path).convert('RGB')
    draw = ImageDraw.Draw(image)

    # Draw bounding boxes for characters (purple)
    for index, row in df_word_chars.iterrows():
        left = int(row['char_xmin'])
        top = int(row['char_ymin'])
        right = int(row['char_xmax'])
        bottom = int(row['char_ymax'])
        draw.rectangle([(left, top), (right, bottom)], outline='purple', width=1)

    # Display or save the image
    image.save(output_path)


# Example usage
if __name__ == '__main__':
    image_path = '10.png'
    # Example with default tesseract config
    df_chars = recognize_text(image_path)
    draw_char_boxes(image_path, df_chars)
    df_chars.to_csv('df_word_chars_10.csv', index=False)
    print("\nDataFrame of Characters within Words (df_word_chars) - Default Config:")
    print(df_chars)
