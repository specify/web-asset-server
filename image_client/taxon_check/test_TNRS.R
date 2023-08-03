library(tidyverse)
library(taxize)
library(reticulate)
library(TNRS)
library(taxize)
library(httr)
library(jsonlite)


# Sys.setenv(TROPICOS_KEY = "ad2063c0-b19a-4349-b8c3-c00ef7e2cc0b")

setwd("/Users/mdelaroca/specify-sandbox/web-asset-server/image_client/taxon_check")

tp_key = getkey(service="tropicos")
# base TNRS api 
url_tn = "https://tnrsapi.xyz/tnrs_api.php"

# source_frame = TNRS::TNRS_sources(skip_internet_check = TRUE)


test_taxon = list(barcodes = c(1234, 1235, 1236, 1237),
                  full_name = c('Castilleja mianata var. dixonii', 
                                'Aesculus californica', 
                                'Wrongus wrongica', 
                                'Eschschozia californica subsp. californica'))


#test_taxon = read_csv("test_csv.csv")

taxon_frame = do.call(data.frame, test_taxon)

test_taxon_id = list(index = c(range(length(taxon_frame$barcodes))), 
                     full_name = taxon_frame$full_name)

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

print(input_json)

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







