import os
from PIL import Image, ImageDraw, ImageFont
import csv
import textwrap

def text_to_image_and_coordinates(
    text_file,
    output_image_path,
    output_csv_path,
    resolution=(3509, 2480),
    font_size=63,
    title_font_size=63,
    subtitle_font_size=63,
    line_spacing=2,
    margin_left=10,      
    margin_right=10,     
    margin_top=350,      
    margin_bottom=100,   
    font_path="C:/WINDOWS/Fonts/cour.ttf",
    title_font_path="C:/WINDOWS/Fonts/courbd.ttf",  # Fuente en negrita para título y subtítulo
    buffer=1  
):
    """
    Generates PNG and CSV with character coordinates, including spaces, with buffer for anti-aliasing.

    Args:
        text_file: Path to the input text file.
        output_image_path: Path to save the output PNG image.
        output_csv_path: Path to save the output CSV file.
        resolution: Tuple (width, height) of the output image.
        font_size: Font size for the paragraph text.
        title_font_size: Font size for the title.
        subtitle_font_size: Font size for the subtitle.
        line_spacing: Line spacing multiplier.
        margin_left: Left margin in pixels.
        margin_right: Right margin in pixels.
        margin_top: Top margin in pixels.
        margin_bottom: Bottom margin in pixels.
        font_path: Path to a TrueType font file.
        title_font_path: Path to a bold TrueType font file.
        buffer: Buffer (in pixels) to add to y_end to account for anti-aliasing.
    """

    try:
        font = ImageFont.truetype(font_path, font_size)  
        title_font = ImageFont.truetype(title_font_path, title_font_size)  # Fuente en negrita
        subtitle_font = ImageFont.truetype(title_font_path, subtitle_font_size)  # Fuente en negrita para subtítulo
    except IOError:
        print(f"Error: Could not load font from {font_path} or {title_font_path}.")
        return

    try:
        with open(text_file, "r", encoding="utf-8") as f:  
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Text file not found at {text_file}")
        return

    title, subtitle = None, None
    text_lines = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("##"):
            subtitle = stripped_line[2:].strip()
        elif stripped_line.startswith("#"):
            title = stripped_line[1:].strip()
        else:
            text_lines.append(stripped_line)

    y = margin_top  # Primera línea disponible

    image = Image.new("RGB", resolution, "white")
    draw = ImageDraw.Draw(image)
    coordinates = []

    # Dibujar título (si existe)
    if title:
        left, top, right, bottom = draw.textbbox((0, 0), title, font=title_font)
        title_width = right - left
        title_x = (resolution[0] - title_width) / 2  # Centrado
        draw.text((title_x, y), title, font=title_font, fill="black")

        # Guardar coordenadas del título
        x_pos = title_x
        for char_index, char in enumerate(title):
            char_left, char_top, char_right, char_bottom = draw.textbbox((x_pos, y), char, font=title_font)
            x_center = x_pos + (char_right - char_left) / 2
            y_center = y + (char_bottom - char_top) / 2
            coordinates.append([char, x_pos, y, char_right, char_bottom, 0, 0, char_index + 1, x_center, y_center])
            x_pos += (char_right - char_left)

        y += int(title_font_size * line_spacing)  # Pasar a la siguiente línea

    # Dibujar subtítulo (si existe)
    if subtitle:
        draw.text((margin_left, y), subtitle, font=subtitle_font, fill="black")

        # Guardar coordenadas del subtítulo
        x_pos = margin_left
        for char_index, char in enumerate(subtitle):
            char_left, char_top, char_right, char_bottom = draw.textbbox((x_pos, y), char, font=subtitle_font)
            x_center = x_pos + (char_right - char_left) / 2
            y_center = y + (char_bottom - char_top) / 2
            coordinates.append([char, x_pos, y, char_right, char_bottom, 0, 0, char_index + 1, x_center, y_center])
            x_pos += (char_right - char_left)

        y += int(subtitle_font_size * line_spacing)  # Pasar a la siguiente línea

    # Asegurar espacio correcto antes del texto normal si hay título y no subtítulo
    if title and not subtitle:
        y += int(font_size * line_spacing)  # Línea en blanco entre título y texto

    # Dibujar el texto normal
    line_number = 1
    word_number = 1
    avg_char_width = sum(font.getlength(c) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") / 52
    chars_per_line = int((resolution[0] - margin_left - margin_right) / avg_char_width)
    
    for paragraph in text_lines:
        wrapped_lines = textwrap.wrap(paragraph, width=chars_per_line)

        for line in wrapped_lines:
            x = margin_left
            words_in_line = line.split()

            for word_index, word in enumerate(words_in_line):
                for char_index, char in enumerate(word):
                    char_left, char_top, char_right, char_bottom = draw.textbbox((x, y), char, font=font)
                    x_center = x + (char_right - char_left) / 2
                    y_center = y + (char_bottom - char_top) / 2
                    draw.text((x, y), char, font=font, fill="black")
                    coordinates.append([char, x, y, char_right, char_bottom, line_number, word_number, char_index + 1, x_center, y_center])
                    x += (char_right - char_left)

                # Añadir espacio entre palabras
                if word_index < len(words_in_line) - 1:
                    space_left, space_top, space_right, space_bottom = draw.textbbox((x, y), " ", font=font)
                    space_x_center = x + (space_right - space_left) / 2
                    space_y_center = y + (space_bottom - space_top) / 2
                    coordinates.append([' ', x, y, space_right, space_bottom, line_number, word_number, 0, space_x_center, space_y_center])
                    x += (space_right - space_left)

                word_number += 1

            y += int(font_size * line_spacing)
            line_number += 1

    image.save(output_image_path)

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:  
        writer = csv.writer(csvfile)
        writer.writerow(["Character", "X_Start", "Y_Start", "X_End", "Y_End", "Line_Number", "Word_Number", "Char_Number_in_Word", "X_Center", "Y_Center"])
        writer.writerows(coordinates)

    print(f"Image saved to {output_image_path}")
    print(f"Character coordinates saved to {output_csv_path}")


# Ruta de la carpeta que contiene los archivos de texto
input_folder = r"C:\Users\Mario\Desktop\code_for_new_paragraphs\input"
output_folder = r"C:\Users\Mario\Desktop\code_for_new_paragraphs\output"

# Procesar todos los archivos .txt en la carpeta
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        text_file = os.path.join(input_folder, filename)
        output_image_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.png")
        output_csv_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.csv")
        
        # Llamar a la función para procesar cada archivo .txt
        text_to_image_and_coordinates(
            text_file,
            output_image_path,
            output_csv_path,
            resolution=(3509, 2480),
            font_size=63,
            title_font_size=63,
            subtitle_font_size=63,
            line_spacing=2,
            margin_left=10,
            margin_right=10,
            margin_top=350,
            margin_bottom=100,
            font_path="C:/WINDOWS/Fonts/cour.ttf",
            title_font_path="C:/WINDOWS/Fonts/courbd.ttf",  # Fuente en negrita
            buffer=2,
        )
