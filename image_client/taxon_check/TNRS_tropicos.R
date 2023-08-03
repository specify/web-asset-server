library(tidyverse)
library(taxize)
library(reticulate)
library(TNRS)
library(httr)
library(jsonlite)
# reading in taxon_list from python
use_python("python3.10.9")
#Sys.setenv(TROPICOS_KEY = "ad2063c0-b19a-4349-b8c3-c00ef7e2cc0b")

today_date <- format(Sys.Date(), "%Y%m%d")

tp_key = getkey(service="tropicos")

# taxon_frame = py$input_frame


test_taxon = list(barcodes = c(1234, 1235, 1236, 1237),
                    full_name = c('Castilleja miniata var. dixonii', 
                                   'Clidemia almedae', 
                                   'Wrongus Wrongica', 
                                   'Eschscholzia californica var. stricta'))

taxon_frame = do.call(data.frame, test_taxon)


input_list <- as.list(taxon_frame$full_name)


# resolving names to tropicos
# 165 for tropicos 11 for gbif backbone

# checking names against tropicos , resolving names

mynames = resolve(sci=input_list, db='gnr')

mynames = as.data.frame(mynames)

# filtering data to tolerance of 0.53

mynames_valid = mynames %>% filter('gnr.score' > 0.60 & 
                gnr.data_source_title == "Tropicos - Missouri Botanical Garden")

# renaming columns for merge
mynames_valid = mynames_valid %>% rename("full_name"= "gnr.user_supplied_name",
                                         "matched_name"= "gnr.matched_name") %>%
                select("full_name", "matched_name")

# making a matched_name list to plug into tropicos
mynames_list =  as.list(mynames_valid$matched_name)

# merging barcode back into valid names list, 
full_name_bar = left_join(taxon_frame, mynames_valid, by ="full_name")

#no_match_list , and writing to csv

no_match = full_name_bar %>% filter(is.na(matched_name))

current_date <- Sys.Date()

#formatted_date <- format(current_date, "%Y-%m-%d")

file_name = paste("no_match_", today_date, ".csv", sep = "")

if (nrow(no_match)>0) {
print("writing csv for no matches")
write_csv(no_match, file = file.path("unmatched_taxa", "no_tropicos_match", file_name))}

# removing empty rows 

full_name_bar = full_name_bar %>% filter(is.na(matched_name) == FALSE)

# entering the spell checked names to get names
# with and without author

base_names = gnr_resolve(sci = mynames_list, data_source_ids = c(165),
                         fields="all", 
                         with_canonical_ranks = TRUE, 
                         best_match_only = TRUE, highestscore = TRUE
                         )


# remerging tropicos id back into name corrected frame

base_names = base_names %>% select(taxon_id, submitted_name, matched_name2)

base_names = base_names %>% rename('tropicos_id' ='taxon_id', 
                                   'matched_name' = 'submitted_name', 
                                   'corrected_name' = 'matched_name2')

full_names_auth = left_join(full_name_bar, base_names, by='matched_name')


# filtering out mistmatches between subtaxa var and subsp

except_data <- full_names_auth %>% filter((grepl("var\\.", full_name) & 
                                               grepl("subsp\\.", corrected_name)) |
                                              (grepl("subsp\\.", full_name) & 
                                                 grepl("var\\.", corrected_name)))




filtered_data <- full_names_auth %>% filter(!((grepl("var\\.", full_name) & 
                                                 grepl("subsp\\.", corrected_name)) |
                                          (grepl("subsp\\.", full_name) & 
                                             grepl("var\\.", corrected_name)))
  )



# filtering and writing file for subtaxa mismatch 
# to prevent duplicates between files


barcode_common = as.list(filtered_data$barcodes)

except_data = except_data %>% filter(!(barcodes %in% barcode_common))

file_name = paste("subtaxa_", today_date, ".csv", sep = "")

if(nrow(except_data)>0){
  
  print("writing subtaxa error csv")
  
  write.csv(except_data, 
            file = file.path("unmatched_taxa", "subtaxa_mismatch", file_name))}


  


# sorting invalid names into handcheck list

# saving new error csv and omit list


