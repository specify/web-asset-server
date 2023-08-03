library(tidyverse)
library(taxize)
library(reticulate)
library(TNRS)
library(taxize)
library(httr)
library(jsonlite)

process_taxon_resolve <- function(r_dataframe_taxon){
  
  today_date <- format(Sys.Date(), "%Y-%m-%d")
  
  setwd("/Users/mdelaroca/specify-sandbox/web-asset-server/image_client/taxon_check")
  
  # base TNRS api 
  url_tn = "https://tnrsapi.xyz/tnrs_api.php"
  
  test_taxon = r_dataframe_taxon
  
  
  #test_taxon = read_csv("test_csv.csv")
  
  taxon_frame = do.call(data.frame, test_taxon)
  
  test_taxon_id = list(index = c(range(length(taxon_frame$barcodes))), 
                       fullname = taxon_frame$fullname)
  
  test_taxon_id = do.call(data.frame, test_taxon_id)
  
  
  headers = list('Accept' = 'application/json', 
                 'Content-Type'='application/json', 'charset'='UTF-8')
  
  data_json = jsonlite::toJSON(unname(test_taxon_id))
  
  sources <- "wcvp"
  class <- "wfo"
  mode <- "resolve"
  match <- "best"
  
  opts = data.frame(c(sources), c(class), c(mode), c(match))
  
  names(opts) <- c("sources", "class", "mode", "matches")
  
  opts_json = jsonlite::toJSON(opts)
  opts_json = gsub('\\[','',opts_json)
  opts_json = gsub('\\]','',opts_json)
  
  # Combine the options and data into single JSON object
  input_json <- paste0('{"opts":', opts_json, ',"data":', data_json, '}' )
  
  results_json <- POST(url = url_tn,
                       add_headers('Content-Type' = 'application/json'),
                       add_headers('Accept' = 'application/json'),
                       add_headers('charset' = 'UTF-8'),
                       body = input_json,
                       encode = "json")
  
  results_raw <- fromJSON(rawToChar(results_json$content))
  
  results <- as.data.frame(results_raw)
  
  
  # Inspect the results
  head(results, 10)
  
  
  # to better compare the output fields
  results.t <- as.data.frame( t( results[,1:ncol(results)] ) )
  results.t[,3,drop =FALSE]
  
  # Display just the main results fields
  results$match.score <- format(round(as.numeric(results $Overall_score),2), nsmall=2)
  
  results[ 1:10, c('Name_submitted', 'match.score', 'Name_matched', 'Taxonomic_status', 
                   'Accepted_name', 'Unmatched_terms')]
  
  hand_check_match = results %>% filter(Overall_score < .98) %>% 
                     select('Name_submitted', 'Name_matched', 
                            'Overall_score', 'Unmatched_terms') %>%
                      rename('fullname'='Name_submitted')
  
  
  
 hand_check_match = left_join(hand_check_match, taxon_frame, by='fullname')

  
 if(nrow(hand_check_match)>0){
    
    print("writing spell/mismatch error csv")
   
    filename = paste0('unmatch_and_typo_', today_date, '.csv')
    
    write_csv(hand_check_match,file = file.path('unmatched_taxa',filename))
    }
  
  
  
  # results = results %>% filter(Overall_score > .98) %>% select('Name_submitted', 'Name_matched')
  
  return(results)
}





