DELETE FROM casbotany.collectionobjectattachment WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.attachment WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.determination WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.collectionobject WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.collector WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.collectingevent WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.locality WHERE TimestampCreated  > (now() - interval 20 day);
DELETE FROM casbotany.agent WHERE TimestampCreated  > (now() - interval 20 day);
# DELETE FROM casbotany.taxon WHERE TimestampCreated > (now() - interval 20 day);


CREATE TEMPORARY TABLE temp_leaf_nodes AS SELECT TaxonID FROM casbotany.taxon WHERE TaxonID
                    NOT IN (SELECT DISTINCT ParentID FROM casbotany.taxon);

    -- Step 2: Delete leaf nodes from temporary table
DELETE FROM casbotany.taxon WHERE TaxonID IN (SELECT TaxonID FROM temp_leaf_nodes) AND TimestampCreated > (now() - interval 20 day);


DROP TEMPORARY TABLE IF EXISTS temp_leaf_nodes;
