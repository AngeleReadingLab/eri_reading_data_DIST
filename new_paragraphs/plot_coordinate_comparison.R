library(ggplot2)
library(dplyr)
library(png) # For reading PNG images

library(ggimage)
# Read the image
img <- readPNG("output.png")

# Read the CSV files
df1 <- read.csv("output_v3.csv") # Replace "file1.csv" with the actual filename
df2 <- read.csv("coordinates.csv") # Replace "file2.csv" with the actual filename

# Function to convert coordinates for df2 to be compatible with df1. Assumes df2 coordinates are relative.
convert_coordinates <- function(df2, image_width = 1920, image_height = 1080) {
  df2_converted <- df2 %>%
    mutate(
      X_Start = char_xmin,
      Y_Start = image_height - char_ymin,
      X_End = char_xmax,
      Y_End = image_height - char_ymax
    ) %>%
    mutate(
      X_Start = ifelse(X_Start < 0, 0, X_Start), # Clamp to image boundaries
      Y_Start = ifelse(Y_Start < 0, 0, Y_Start),
      X_End = ifelse(X_End > image_width, image_width, X_End),
      Y_End = ifelse(Y_End > image_height, image_height, Y_End)

    ) %>%
    select(char, X_Start, Y_Start, X_End, Y_End, everything()) #Keep all other columns
  return(df2_converted)
}

df2_converted <- convert_coordinates(df2)

# Create the plot
ggplot() +
  # Display the image as a background
  # Display the image as a background - CORRECTED
  # Display the image as a background - CORRECTED (Finally!)
 geom_image(image = "output.png", aes(x = 0, y = 0)) +
              xlim(0, 1920) +
              ylim(1080, 0)
  
  # Plot rectangles and characters from df1
  geom_rect(data = df1, aes(xmin = X_Start, ymin = Y_Start, xmax = X_End, ymax = Y_End),
            color = "blue", fill = NA, linewidth = 1, alpha = .3) +
  geom_text(data = df1, aes(x = (X_Start + X_End) / 2, y = (Y_Start + Y_End) / 2, label = Character),
            color = "blue", size = 3, alpha = .3) +
  
  # Plot rectangles and characters from df2
  geom_rect(data = df2_converted, aes(xmin = X_Start, ymin = Y_Start, xmax = X_End, ymax = Y_End),
            color = "red", fill = NA, linewidth = 1, alpha = .3) +
  geom_text(data = df2_converted, aes(x = (X_Start + X_End) / 2, y = (Y_Start + Y_End) / 2, label = char),
            color = "red", size = 3, alpha = .3) +
  
  # Set plot limits to image dimensions
 + # Note the reversed y-axis for image coordinates
  coord_fixed() + #Maintain aspect ratio
  labs(title = "Character Coordinates Comparison", x = "X-axis", y = "Y-axis") +
  theme_minimal()  # Clean theme
# Convert to raster object
img_grob <- rasterGrob(image = rgb(img[,,1], img[,,2], img[,,3]), 
                       width = unit(1,"npc"), height = unit(1,"npc"), interpolate = TRUE)

ggplot() +
  annotation_custom(img_grob, xmin = 0, xmax = 1920, ymin = 0, ymax = 1080) +
  xlim(0, 1920) +
  ylim(1080, 0) +
  coord_fixed()

