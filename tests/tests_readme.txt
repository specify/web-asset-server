test files for picturae project:
testing_tools.py: tools to create fake data and generate unique ids for them to avoid filenaming overlap.

tests for picturae_create_csv file:
    test_pic_dir.py : runs unittests for the functions : file_present
    test_pic_merge.py : runs unittests for the functions : csv_read_path, and csv_merge
    test_taxon_concat_tnrs.py : runs unittests for the functions: taxon_concat, check_taxon_real (which uses tnrs)
    test_check_record.py : runs unittests for the functions: barcode_has_record, image_has_record, test_pic_merge

tests for picturae_importer file:



