library(tidyverse)

fixation_data <- read_tsv("Fixations in paragraph_two subjects.txt") %>%
  filter(Category == "Fixation") %>%
  mutate(x = as.numeric(`Fixation Position X [px]`), 
         y = as.numeric(`Fixation Position Y [px]`),
         start = as.numeric(`Event Start Trial Time [ms]`),
         end = as.numeric(`Event End Trial Time [ms]`),
         # for subject, get only digits from the Participant string
         subject = as.numeric(str_extract(Participant, "\\d+")),
         trial_id = 1) %>%
  # round all to 0 decimal places
  mutate(across(c(x, y, start, end), ~ round(., 0))) %>%
                
  select(x, y, start, end, subject, trial_id)

write_csv(fixation_data, "fixation_data.csv")
