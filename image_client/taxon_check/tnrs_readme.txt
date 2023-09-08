Summary: This folder contains the R script R_TNRS, utilizing the Taxonomic Name Resolution Service.

files:
 R_TNRS: able to pass taxonomic names through the Taxanomic Name resolution service. Which checks that
         a taxon exists and is spelled correctly. Can be used to test either full taxon names or partial taxon names.
         R_TNRS can be called from python files using the r2py package.

         - the preferred data format to pass through R_TNRS is a two column dataframe containing taxon names,
           and a unique code or identifier such as barcode or MD5 to match on.

         - returned information includes: matching score, matched name, matched author, and unmatched terms.

         - limitations: R_TNRS, has a limited scope when it comes to checking hybrids, so many hybrids may not be recognized.
                        best practice may be to check just genus or higher taxon ranks for hybridized taxonomic names.

         - sources: IPNI- kew gardens,  https://www.ipni.org/,   other sources may be added in script if desired,
                    such as world flora online.

