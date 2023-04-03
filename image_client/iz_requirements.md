At the bottom are the requested file paths to various images for EXIF field mapping/decoding.

-   IZ has additional images of types, original specimen labels etc. located on "hydra" 
    here: N:\izg\SpecifyAttachments. SpecifyAttachments folder is the location we'd planned to save images 
    ready to be uploaded to Specify.

-   Images contained in  SpecifyAttachments are individually or with containing folder named with CASIZ XXXXXX or CASIZ_XXXXXX.   FYI Redundancy: McFadden files are also saved on the I drive (pegasus) among the files ready for the corresponding EXIF templates (text files) to be applied, AND also are in IZ Images.  
-   Label scan image files in the SpecifyAttachments folder are named by CASIZ no., however file names lack "CASIZ" acronym. Label scans were manually attached in Specify before we knew not to do this. You'll be dumping attached versions.

-   Request: Frequently, but not always, a © symbol or the word copyright/s/ed in file or folder name indicates externally held copyright. If there is a means to "flag" these files for manual checking the category this would be most useful. I think you had a column in your sheet for copyright[?]. There were no column names so I couldn't be sure.   In other cases required image "acknowledgements" or "credit" may be in the file/folder name, which is something else we'll eventually need to add to the Credit Line EXIF metadata field.

-   You likely have this covered but just in case you've missed formats that I encountered today, the most common formats for CASIZ nos. in file names are below, leading zeros are inconsistently applied and caps vary:

-   CASIZXXXXXX
-   CASIZ XXXXXX
-   CASIZ_XXXXXX
-   CASIZ# XXXXXX
-   CASIZ XXXXXX or CASIZ XXXXXX
-   CASIZ XXXXXX or XXXXXX
-   same as above but with "and" not "or"
-   same as above but >2 numbers in file name
-   other characters may precede "CASIZ"
-   CAT or other characters between CASIZ and # (i.e. CASIZ_CAT_XXXXX)
-   see above for Label scan files, which lack the CASIZ acronym

-   File paths to example images with the CASIZ no. stored in 3 different EXIF fields:

-   N:\izg\IZ Images\Verde Island Passage Expeditions 2014-2016 annotated metadata\Piotrowski VIP2015\CP VIP 2015 SPECIMEN IMAGES BATCH 1 WITH METADATA\CP-0010 Phyllodocidae  (all images in folder)

-   N:\izg\IZ Images\Hearst Expedition Philippines images 2011\Gosliner Hearst Expedition 2011_metadata includes CASIZ no\ST 104 Murals  (see file: Hypselodoris maridadlus_2148)

-   N:\izg\IZ Images\CASIZ TYPE SPECIMENS_Markello and others to July 2021\Crustacea copied to Specify Attachments    (see file: CASIZ 107403 Tetraclita barnesorum holotype)  You won't find many of these now but this is the format we're moving towards now so there will be many eventually.

Examples to test with. note that all should match, but some should only have minimal match groups,
e.g.:
casiz 208715 150822 150822 loch nevis 052.tif
should match only "casiz 208715"


casiz12345.tif
casiz 12345.tif
casiz_12345.tif
casiz# 12345.tif
casiz 12345 or casiz 12345.tif
casiz 12345 and 12345.tif
cas 12345 233 4523 5345.tif
casiz 208715 150822 150822 loch nevis 052.tif
casiz cat 12345 and 12345 and 472678 garbage garbage.tif
cas 12345 and 23145 garbage garbage.tif
casiz_cat_12345.tif
12345.tif
cas12345.tif

2casiz12345.tif
123casiz 12345.tif
45casiz_12345.tif
dlias casiz# 12345.tif
casiz 12345 or casiz 12345.tif
casiz 12345 and 12345.tif
casiz 12345 and 12345 and 472678.tif
casiz 182301 thuridilla gracilis © t.m. gosliner _3804.tif
casiz 182301 thuridilla gracilis © t.m. gosliner _3804.tif



------

Just to confirm the plan, will you also be writing the info to EXIF image fields and Specify Attachment 
fields as we'd discussed? These are templates I'd saved on Pegasus here: 
I:\izg\IZ\for Joe_modify metadata_all Hearst-VIP-CRRF, for example see the template pasted below.
Thanks! 
[IPTC Core field (metadata): text to be entered]
Copyright Status:  Copyrighted
Copyright Notice:  © Terrence M. Gosliner licensed under Creative Commons BY-NC-SA
Creator: Terrence M. Gosliner
Credit Line: Terrence M. Gosliner, California Academy of Sciences
Rights Usage Terms: Creative Commons Attribution-NonCommercial-ShareAlike - CC BY-NC-SA
Title: CASIZ number (if feasible)
File Properties:Notes:  False
File Properties:Label:  StillImage
Attributes:Label:  Live

[Specify Attachments field data to be entered]
CopyrightHolder: © Terrence M. Gosliner licensed under Creative Commons BY-NC-SA
Creator: Terrence M. Gosliner
Credit: Terrence M. Gosliner, California Academy of Sciences
License: Creative Commons Attribution-NonCommercial-ShareAlike - CC BY-NC-SA
Title: CASIZ number
NotPublic: False
Type: StillImage
subType: Live 
