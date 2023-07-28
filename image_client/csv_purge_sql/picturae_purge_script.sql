DELETE FROM casbotany.collectionobjectattachment WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.attachment WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.determination WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.collectionobject WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.collector WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.collectingevent WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.locality WHERE TimestampCreated  > (now() - interval 10 day);
DELETE FROM casbotany.agent WHERE TimestampCreated  > (now() - interval 10 day);
