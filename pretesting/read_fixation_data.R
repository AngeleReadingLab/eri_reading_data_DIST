library(tidyverse)

fixation_data <- read_tsv("pretesting/fix_data_cond3.txt") %>%
  filter(Category == "Fixation") %>%
  mutate(
    x = as.numeric(`Fixation Position X [px]`),
    y = as.numeric(`Fixation Position Y [px]`),
    start = as.numeric(`Event Start Trial Time [ms]`),
    stop = as.numeric(`Event End Trial Time [ms]`),
    duration = stop - start,
    # for subject, get only digits from the Participant string
    subject = as.numeric(str_extract(Participant, "\\d+")),
    # for trial_id, get only digits from the Stimulus string
    trial_id = as.numeric(str_extract(Stimulus, "\\d+"))
  ) %>%
  # round all to 0 decimal places
  mutate(across(c(x, y, start, stop), ~ round(., 0))) %>%
  
  select(x, y, start, stop, subject, trial_id)

write_csv(fixation_data %>% filter(trial_id == 30), "pretesting/fixation_data_pretesting_30.csv")

          