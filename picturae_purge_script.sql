DELETE FROM casbotany.collectionobjectattachment WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.attachment WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.collectionobject WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.collectingevent WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.locality WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.agent WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.collectionobjectattachment WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);
DELETE FROM casbotany.collectionobject WHERE TimestampCreated > (NOW() - INTERVAL 1 DAY);

