#!/usr/bin/env python3
# one time image fixer

from image_db import ImageDb

sql = "select id,original_filename from images where original_filename like '%-0.jpg'"
image_db = ImageDb()

cursor = image_db.get_cursor()
cursor.execute(sql)
record_list = []
broken_list = []
for (id, original_filename) in cursor:
    print(f"Broken: {id}: {original_filename}")
    broken_list.append([id,original_filename])
cursor.close()
# cas0288422-0.jpg
for id,original_filename in broken_list:
    good_filename = original_filename.split('-')
    good_filename = good_filename[0] + ".jpg"
    sql = f"update images set original_filename='{good_filename}'  where id = {id}"
    print (sql)
    image_db.execute(sql)



