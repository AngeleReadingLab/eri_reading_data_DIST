library(tidyverse)

fixation_data <- read_tsv("results_output.txt") %>%
  filter(Category == "Fixation") %>%
  mutate(x = as.numeric(`Fixation Position X [px]`), 
         y = as.numeric(`Fixation Position Y [px]`),
         start = as.numeric(`Event Start Trial Time [ms]`),
         stop = as.numeric(`Event End Trial Time [ms]`),
         # for subject, get only digits from the Participant string
         subject = as.numeric(str_extract(Participant, "\\d+")),
         trial_id = "output") %>%
  # round all to 0 decimal places
  mutate(across(c(x, y, start, stop), ~ round(., 0))) %>%
                
  select(x, y, start, stop, subject, trial_id)

write_csv(fixation_data, "fixation_data.csv")
