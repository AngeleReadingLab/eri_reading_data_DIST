library(tidyverse)

filename = "eri_new/Condición 3_Todos los párrafos.txt"

fixation_data <- read_delim(filename, delim = "\t") %>%
  filter(Category == "Fixation") %>%
  mutate(x = as.numeric(`Fixation Position X [px]`), 
         y = as.numeric(`Fixation Position Y [px]`),
         start = as.numeric(`Event Start Trial Time [ms]`),
         stop = as.numeric(`Event End Trial Time [ms]`),
         # for subject, get only digits from the Participant string
         subject = Participant, #as.numeric(str_extract(Participant, "\\d+")),
         # strip ".png " from the end of the stimulus name and make numeric for trial id
         trial_id = Stimulus %>%
           str_remove("\\.png") %>%
           # add prefix "page"
           str_replace("^", "page") 
         ) %>%
  # round all to 0 decimal places
  mutate(across(c(x, y, start, stop), ~ round(., 0))) %>%
                
  select(x, y, start, stop, subject, trial_id) #%>%
  #filter(trial_id == "page30")

write_csv(fixation_data, "eri_new/fixation_data.csv")
# Check the first few rows of the fixation data
