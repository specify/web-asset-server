test files for picturae project:

testing_tools.py: tools to create fake data and generate unique ids for them to avoid file naming overlap.

test classes:
    pic_csv_test_class.py: the test class of CsvCreatePicturae, with reduced init method for use in unittests.
    pic_importer_test_class.py: the test class of PicturaeImporter, with reduced init method for use in unittests.

tests for picturae_create_csv file:
    test_pic_dir.py : runs unittests for the functions : file_present
    test_pic_merge.py : runs unittests for the functions : csv_read_path, and csv_merge
    test_taxon_concat_tnrs.py : runs unittests for the functions: taxon_concat, check_taxon_real (which uses tnrs)
    test_check_record.py : runs unittests for the functions: barcode_has_record, image_has_record, check_barcode_match

tests for picturae_importer file:
    test_agent_list.py: runs unittests on create_agent_list function.
    test_populate_fields.py: runs unittests on populate_fields function.
    test_file_hide.py: runs unittests on hide_unwanted_files and unhide_files



