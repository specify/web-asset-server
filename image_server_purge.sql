DELETE FROM images WHERE datetime  > (NOW() - INTERVAL 10 DAY);