DELETE FROM images WHERE datetime > (now() - interval 20 day );
