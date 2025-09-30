from PIL import Image, ImageDraw, ImageFont
import csv
import textwrap
import os


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
    trial_id="trial_1",
):
    """
    Generates a PNG image from a text file (with a title) and a CSV with character coordinates.

    Args:
        text_file: Path to the input text file.
        output_image_path: Path to save the output PNG image.
        output_csv_path: Path to save the output CSV file.
        title: The title text to be displayed (default: "Title").
        resolution: Tuple (width, height) of the output image.
        font_size: Font size for the paragraph text.
        title_font_size: Font size for the title.
        line_spacing: Line spacing multiplier.
        margin: Margin around the text in pixels.
        font_path: Path to a TrueType font file.
        trial_id: A string identifier for the trial (e.g., "trial_1").
    """

    try:
        # Load fonts
        font = ImageFont.truetype(font_path, font_size)
        title_font = ImageFont.truetype(font_path, title_font_size)
    except IOError:
        print(f"Error: Could not load font from {font_path}. Please ensure the path is correct.")
        return

    # Read text from file
    try:
        with open(text_file, "r") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Text file not found at {text_file}")
        return

    # Calculate line height
    line_height = int(font_size * line_spacing)
    title_line_height = int(title_font_size * line_spacing)

    # Estimate text width and wrap paragraph text
    avg_char_width = sum(font.getlength(c) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") / 52
    chars_per_line = int((resolution[0] - 2 * margin) / avg_char_width)
    wrapped_lines = textwrap.wrap(text, width=chars_per_line)

    # Calculate total text height (including title)
    total_text_height = len(wrapped_lines) * line_height + title_line_height + margin

    # Check if text fits
    if total_text_height + margin > resolution[1]:
        print(
            "Warning: Text may not fit within the specified image height. "
            "Consider increasing the image height, reducing font size, or decreasing line spacing."
        )

    # Create image
    image = Image.new("RGB", resolution, "white")
    draw = ImageDraw.Draw(image)

    # --- Draw title (centered) ---
    title_width = title_font.getlength(title)
    title_x = (resolution[0] - title_width) / 2
    title_y = margin
    draw.text((title_x, title_y), title, font=title_font, fill="black")

    # --- Draw paragraph text and record coordinates ---
    y = title_y + title_line_height + margin / 2  # Start below the title

    coordinates = []
    line_counter = 0  # Initialize line counter
    for line in wrapped_lines:
        x = margin
        assigned_line = line_counter + 1  # assigned line starts from 1
        for char in line:
            char_width = font.getlength(char)

            # Draw the character *before* getting the bounding box.
            draw.text((x, y), char, font=font, fill="black")

            # Calculate the bounding box.  getbbox is relative to the drawn text,
            # so we need to offset by x and y.
            bbox = draw.textbbox((x, y), char, font=font)

            # char,char_x_center,char_y_center,char_xmax,char_xmin,char_ymax,char_ymin,trial_id,assigned_line
            coordinates.append([
                char,
                (bbox[0] + bbox[2]) / 2,  # char_x_center
                (bbox[1] + bbox[3]) / 2,  # char_y_center
                bbox[2],  # char_xmax
                bbox[0],  # char_xmin
                bbox[3],  # char_ymax
                bbox[1],  # char_ymin
                trial_id,  # trial_id
                assigned_line,  # assigned line
            ])
            x += char_width  # Increment x by the *actual* width of the character
        y += line_height
        line_counter += 1  # Increment line counter after each line

    # --- Title Coordinates ---
    x_title = title_x
    assigned_line = 0  # Title is always line 0
    for char in title:
        char_width = title_font.getlength(char)

        # Draw the character *before* getting the bounding box
        draw.text((x_title, title_y), char, font=title_font, fill="black")

        bbox = draw.textbbox((x_title, title_y), char, font=title_font)

        coordinates.append([
            char,
            (bbox[0] + bbox[2]) / 2,  # char_x_center
            (bbox[1] + bbox[3]) / 2,  # char_y_center
            bbox[2],  # char_xmax
            bbox[0],  # char_xmin
            bbox[3],  # char_ymax
            bbox[1],  # char_ymin
            trial_id,  # trial_id
            assigned_line,  # assigned line
        ])
        x_title += char_width

    # Save image
    image.save(output_image_path)

    # Save coordinates to CSV
    with open(output_csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "char",
            "char_x_center",
            "char_y_center",
            "char_xmax",
            "char_xmin",
            "char_ymax",
            "char_ymin",
            "trial_id",
            "assigned_line",
        ])
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
    font_path="./LiberationMono-Regular.ttf",  # Ensure this font is in the current directory
    trial_id="trial_001",
)
