library(tidyverse)
library(taxize)
library(reticulate)
library(TNRS)
library(taxize)
library(httr)
library(jsonlite)

sink("output.txt")

process_taxon_resolve <- function(tax_frame){
  
  today_date <- format(Sys.Date(), "%Y-%m-%d")
  
  setwd("/Users/mdelaroca/specify-sandbox/web-asset-server/image_client")
  
  # base TNRS api 
  url_tn = "https://tnrsapi.xyz/tnrs_api.php"
  
  taxon_frame = tax_frame
  
  ncol_t = nrow(taxon_frame)
  #test_taxon = read_csv("test_csv.csv")

  
  headers = list('Accept' = 'application/json', 
                 'Content-Type'='application/json', 'charset'='UTF-8')
  
  data_json = jsonlite::toJSON(unname(taxon_frame))
  
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
  
  # to better compare the output fields
  results.t <- as.data.frame( t( results[,1:ncol(results)] ) )
  results.t[,ncol_t,drop =FALSE]
  
  # Display just the main results fields
  results$match.score <- format(round(as.numeric(results $Overall_score),2), nsmall=2)

  
  results[ 1:10, c('Name_submitted', 'match.score', 'Name_matched', 'Taxonomic_status', 
                   'Accepted_name', 'Unmatched_terms', 'Accepted_name_author')]
  
  results = results %>% rename('fullname'='Name_submitted', 
                               'name_matched' = 'Name_matched',
                               'taxonomic_status' = 'Taxonomic_status',
                               'accepted_name'= 'Accepted_name',
                               'unmatched_terms'= 'Unmatched_terms',
                               'overall_score' = 'Overall_score',
                               'accepted_author' = 'Accepted_name_author')
  

  hand_check_match = results %>% filter(overall_score < .985) %>% 
                     select('fullname', 'name_matched', 
                            'overall_score', 'unmatched_terms')
  
 hand_check_match = left_join(taxon_frame, hand_check_match, by='fullname')
 
 hand_check_match = hand_check_match %>% filter(!is.na(overall_score))


 if(nrow(hand_check_match)>0){
    
    print("writing spelling/mismatch error csv")
   
    filename = paste0('unmatch_and_typo_', today_date, '.csv')
    
    write_csv(hand_check_match,file = file.path('taxon_check','unmatched_taxa',filename))
    }
  
  
  
  results = results %>% filter(overall_score > .99) %>% 
            select('fullname', 'name_matched', 'accepted_author','overall_score')
  
  return(results)
}


resolved_taxa = process_taxon_resolve(tax_frame = r_dataframe_taxon)

sink()

# test_taxon = list(barcodes = c(1234),
               # fullname = c('Abies sibirica subsp. semenovii'))

# test_frame = do.call(data.frame, test_taxon)

# returnti = process_taxon_resolve(tax_frame = test_frame)


# test_taxon = list(barcodes= c(999999984), fullname = c('Abies sibirica'))

# test_frame = do.call(data.frame, test_taxon)

# returnti = process_taxon_resolve(tax_frame = test_frame)






