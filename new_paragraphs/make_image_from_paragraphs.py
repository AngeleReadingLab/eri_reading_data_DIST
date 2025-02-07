from PIL import Image, ImageDraw, ImageFont
import csv
import textwrap

def text_to_image_and_coordinates(
    text_file,
    output_image_path,
    output_csv_path,
    title="Title",
    resolution=(600, 400),
    font_size=20,
    title_font_size=28,
    line_spacing=1.5,
    margin=20,
    font_path="arial.ttf",
    buffer=1  # Add a buffer for anti-aliasing
):
    """
    Generates PNG and CSV with character coordinates, with buffer for anti-aliasing.

    Args:
        text_file: Path to the input text file.
        output_image_path: Path to save the output PNG image.
        output_csv_path: Path to save the output CSV file.
        title: The title text.
        resolution: Tuple (width, height) of the output image.
        font_size: Font size for the paragraph text.
        title_font_size: Font size for the title.
        line_spacing: Line spacing multiplier.
        margin: Margin in pixels.
        font_path: Path to a TrueType font file.
        buffer: Buffer (in pixels) to add to y_end to account for anti-aliasing.
    """

    try:
        font = ImageFont.truetype(font_path, font_size)
        title_font = ImageFont.truetype(font_path, title_font_size)
    except IOError:
        print(f"Error: Could not load font from {font_path}.")
        return

    try:
        with open(text_file, "r") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Text file not found at {text_file}")
        return

    line_height = int(font_size * line_spacing)
    title_line_height = int(title_font_size * line_spacing)

    # Use textlength for wrapping
    avg_char_width = sum(font.getlength(c) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") / 52
    chars_per_line = int((resolution[0] - 2 * margin) / avg_char_width)
    wrapped_lines = textwrap.wrap(text, width=chars_per_line)

    # Calculate total text height
    max_line_width = 0
    for line in wrapped_lines:
      left, top, right, bottom = font.getbbox(line)
      line_width = right - left
      if line_width > max_line_width:
          max_line_width = line_width

    total_text_height = len(wrapped_lines) * line_height + title_line_height + margin
    if total_text_height + margin > resolution[1]:
        print("Warning: Text may not fit within the specified image height.")

    image = Image.new("RGB", resolution, "white")
    draw = ImageDraw.Draw(image)

    # --- Draw title (using textbbox) ---
    left, top, right, bottom = draw.textbbox((0,0), title, font=title_font)
    title_width = right - left
    title_x = (resolution[0] - title_width) / 2
    title_y = margin
    draw.text((title_x, title_y), title, font=title_font, fill="black")

    coordinates = []
    x_title = title_x
    for char_index, char in enumerate(title):
        char_left, char_top, char_right, char_bottom = draw.textbbox((x_title, title_y), char, font=title_font)
        x_center = x_title + (char_right - char_left) / 2
        y_center = title_y + (char_bottom - char_top) / 2
        coordinates.append([char, x_title, title_y, char_right, char_bottom, 0, 0, char_index + 1, x_center, y_center])
        x_title += (char_right - char_left)

    # --- Draw paragraph text (with uniform Y_End per line) ---
    y = title_y + title_line_height + margin / 2
    line_number = 1
    word_number = 1

    for line in wrapped_lines:
        x = margin
        words_in_line = line.split()

        # --- Find max descender depth for the line ---
        max_descent = 0
        for word in words_in_line:
            for char in word:
                _, _, _, char_bottom = draw.textbbox((0, 0), char, font=font)
                descent = char_bottom - y - font_size
                if descent > max_descent:
                    max_descent = descent

        # --- Draw characters on the line with adjusted y_end ---
        for word_index, word in enumerate(words_in_line):
            for char_index, char in enumerate(word):
                char_left, char_top, char_right, char_bottom = draw.textbbox((x, y), char, font=font)
                x_center = x + (char_right - char_left) / 2
                y_center = y + (char_bottom - char_top) / 2

                # Adjust y_end to account for max_descent and buffer
                y_end_adjusted = y + font_size + max_descent + buffer

                draw.text((x, y), char, font=font, fill="black")
                coordinates.append([char, x, y, char_right, y_end_adjusted, line_number, word_number, char_index + 1, x_center, y_center])

                x += (char_right - char_left)

            # Add space coordinates (with adjusted y_end)
            if word_index < len(words_in_line) - 1:
                space_left, space_top, space_right, space_bottom = draw.textbbox((x,y), " ", font=font)
                x_center = x + (space_right - space_left) / 2
                y_center = y + (space_bottom - space_top) / 2
                coordinates.append([" ", x, y, space_right, y + font_size + max_descent + buffer, line_number, word_number, char_index + 2, x_center, y_center])
                x += (space_right - space_left)

            word_number += 1

        y += line_height
        line_number += 1

    image.save(output_image_path)

    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Character", "X_Start", "Y_Start", "X_End", "Y_End", "Line_Number", "Word_Number", "Char_Number_in_Word", "X_Center", "Y_Center"])
        writer.writerows(coordinates)

    print(f"Image saved to {output_image_path}")
    print(f"Character coordinates saved to {output_csv_path}")

text_to_image_and_coordinates(
    "input.txt",
    "output.png",
    "coordinates.csv",
    title="La extinción de los neandertales",
    resolution=(1920, 1080),
    font_size=42,
    title_font_size=52,
    line_spacing=2,
    margin=40,
    font_path="./LiberationMono-Regular.ttf",  # Example path on macOS, now using Arial Bold
    buffer = 2,
)
