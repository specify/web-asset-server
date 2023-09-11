# removes all records added in the selected time window(in this case last 20 days), order matters
# as certain tables external keys
DELETE FROM collectionobjectattachment WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM attachment WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM determination WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM collectionobject WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM collector WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM collectingevent WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM locality WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM agent WHERE TimestampCreated  > (now() - interval 20 day);


# Deletes leaf nodes from taxon tree: this may need to be run twice to remove multiple layers of new hierarchy
# operates using a temporary table to select leaf nodes with no children added within time window.
# deletes lowest level of taxa first, then can repeat the process, deleting newly added taxa,
# with children recently deleted
CREATE TEMPORARY TABLE temp_leaf_nodes AS SELECT TaxonID FROM casbotany.taxon WHERE TaxonID
                       NOT IN (SELECT DISTINCT ParentID FROM casbotany.taxon
                       WHERE ParentID IS NOT NULL) AND TimestampCreated >= (now() - interval 20 day);

DELETE FROM casbotany.taxon WHERE TaxonID IN (SELECT TaxonID FROM temp_leaf_nodes);


DROP TEMPORARY TABLE IF EXISTS temp_leaf_nodes;

ALTER USER 'user'@'%' ACCOUNT UNLOCK;


# unlock command in case a script fails mid execution and fails to unlock database.
UPDATE mysql.user
SET account_locked = 'n'
WHERE user != 'user' AND host = '%';

# commands used to kill multiple processes, used to deal with conflicts between open connections to sql db.
#
# show processlist;
#
# kill *;