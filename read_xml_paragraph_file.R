library(xml2)
library(tidyverse)

# Read the XML file
my_xml <- read_xml("P3_Word coordinates.xml") 

# Extract all DynamicAOI nodes with Group = "Word"
character_aois <- xml_find_all(my_xml, "//DynamicAOI[Group = 'Character']")

# Create an empty list to store the extracted data
character_data <- list()

# Loop through each Word AOI node
for (i in seq_along(character_aois)) {
  aoi <- character_aois[i]
  
  # Extract Name
  name <- xml_text(xml_find_first(aoi, "Name"))
  
  # Extract Points
  points <- xml_find_all(aoi, "Points/Point") 
  
  # Get X and Y coordinates of the first and last points
  x1 <- as.numeric(xml_text(xml_find_first(points[1], "X")))
  y1 <- as.numeric(xml_text(xml_find_first(points[1], "Y")))
  x2 <- as.numeric(xml_text(xml_find_first(points[length(points)], "X")))
  y2 <- as.numeric(xml_text(xml_find_first(points[length(points)], "Y")))
  
  # Store the extracted data in a list
  character_data[[i]] <- list(Name = name, 
                         X1 = x1, 
                         Y1 = y1, 
                         X2 = x2, 
                         Y2 = y2)
}

# Convert the list to a data frame
character_df <- do.call(rbind, lapply(character_data, as.data.frame)) %>%
  mutate(width = X2 - X1,
         height = Y2 - Y1)

# remove duplicates
word_df <- character_df[!duplicated(character_df),]

# split the Name column into Paragraph, Section, Word, Character, Region, Line, and string
# the format of the Name column is "__re_p1_s1_w1_c0_r0_l1_Hay"

word_df_with_region_info <- word_df %>%
  mutate(paragraph = str_extract(Name, "p\\d+"),
         section = str_extract(Name, "s\\d+"),
         word = str_extract(Name, "w\\d+"),
         character = str_extract(Name, "c\\d+"),
         region = str_extract(Name, "r\\d+"),
         line = str_extract(Name, "l\\d+"),
         # string is all the final characters after the underscore at the end of the string
         string = str_extract(Name, "_([^_]+)$")) %>%
  # remove the "p", "s", "w", "c", "r", "l" and "_" from the columns
  mutate(across(c(paragraph, section, word, character, region, line), ~ str_remove(., "[a-z]"))) %>%
  mutate(string = str_remove(string, "_")) %>%
  rename(char_xmin = X1, char_ymin = Y1, char_xmax = X2, char_ymax = Y2,
         letter = character,
         assigned_line = line,
         char = string)

# Assign the new column names to the data frame
colnames(word_df_with_region_info) <- new_colnames 

# add char_x_center and char_y_center columns
word_df_with_region_info <- word_df_with_region_info %>%
  mutate(char_x_center = (char_xmin + char_xmax) / 2,
         char_y_center = (char_ymin + char_ymax) / 2,
         trial_id = 1)

write_csv(word_df_with_region_info, "word_df_with_region_info.csv")
