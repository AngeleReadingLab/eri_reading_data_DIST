import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches

# --- Settings ---
image_path = 'output.png'  # Replace with the path to your image file
csv_file_1_path = 'coordinates.csv'  # Replace with the path to your first CSV file
csv_file_2_path = 'df_word_chars.csv'  # Replace with the path to your second CSV file
output_image_path = 'output_plot_image.png' # Path to save the output image

# --- Load data from CSV file 1 ---
try:
    df1 = pd.read_csv(csv_file_1_path)
    print(f"Data from {csv_file_1_path} loaded successfully.")
except FileNotFoundError:
    print(f"Error: {csv_file_1_path} not found. Please make sure the file exists and the path is correct.")
    df1 = None

# --- Load data from CSV file 2 ---
try:
    df2 = pd.read_csv(csv_file_2_path)
    print(f"Data from {csv_file_2_path} loaded successfully.")
except FileNotFoundError:
    print(f"Error: {csv_file_2_path} not found. Please make sure the file exists and the path is correct.")
    df2 = None

# --- Load the image to get its size ---
try:
    img = mpimg.imread(image_path)
    print(f"Image from {image_path} loaded successfully.")
    image_height, image_width, _ = img.shape # Get image dimensions
except FileNotFoundError:
    print(f"Error: {image_path} not found. Please make sure the file exists and the path is correct.")
    img = None
    image_height, image_width = None, None

# --- Plotting and Saving ---
if img is not None and image_height is not None and image_width is not None:
    dpi = 100  # Define DPI for output image
    figsize_inches = image_width / dpi, image_height / dpi # Calculate figsize in inches

    fig, ax = plt.subplots(1, figsize=figsize_inches, dpi=dpi) # Set figsize and dpi for the figure
    ax.imshow(img)

    if df1 is not None:
        for index, row in df1.iterrows():
            char = row['char']
            x_min = row['char_xmin']
            y_min = row['char_ymin']
            x_max = row['char_xmax']
            y_max = row['char_ymax']
            char_x_center = row['char_x_center']
            char_y_center = row['char_y_center']

            rect_width = x_max - x_min
            rect_height = y_max - y_min
            rect = patches.Rectangle((x_min, y_min), rect_width, rect_height, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
            ax.text(char_x_center, char_y_center, char, color='blue', fontsize=12, ha='center', va='center')

    if df2 is not None:
        for index, row in df2.iterrows():
            char = row['Character']
            x_start = row['X_Start']
            y_start = row['Y_Start']
            x_end = row['X_End']
            y_end = row['Y_End']
            x_center = row['X_Center']
            y_center = row['Y_Center']

            rect_width = x_end - x_start
            rect_height = y_end - y_start
            rect = patches.Rectangle((x_start, y_start), rect_width, rect_height, linewidth=1, edgecolor='g', facecolor='none')
            ax.add_patch(rect)
            ax.text(x_center, y_center, char, color='cyan', fontsize=12, ha='center', va='center')

    ax.set_xlim(0, image_width) # Set x limits to image width
    ax.set_ylim(image_height, 0) # Set y limits to image height, inverting axis

    ax.set_xticks([]) # Remove x axis ticks
    ax.set_yticks([]) # Remove y axis ticks
    ax.axis('off') # Turn off axes

    plt.gca().set_position([0, 0, 1, 1]) # Remove whitespace around the plot
    plt.savefig(output_image_path, dpi=dpi, bbox_inches='tight', pad_inches=0) # Save the plot
    print(f"Plot saved as {output_image_path} with the same size as the original image.")
    plt.show() # Still show plot if you want to preview it
else:
    print("Image plotting and saving failed because image was not loaded or image dimensions could not be determined.")
