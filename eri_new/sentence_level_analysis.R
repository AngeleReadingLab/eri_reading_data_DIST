library(tidyverse)

sentences_words <- read_csv("eri_new/sentences_words_page_18.csv")

corrected_fixations <- read_csv("eri_new/corrected_fixations_data.csv")

# Join the sentences_words and corrected_fixations data frames
sentence_level_data <- sentences_words %>%
  left_join(corrected_fixations, by = c("overall_word_nr" = "on_word_number_Wisdom_of_Crowds")) %>%
  mutate(
   max_sentence = cummax(sentence_nr))  
