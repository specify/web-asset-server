import time_utils
import db_utils
from db_utils import DatabaseInconsistentError
import logging

class AttachmentUtils:

    def __init__(self,db_utils):
        self.db_utils = db_utils

    def get_collectionobjectid_from_filename(self,attachment_location):
        sql = f"""
        select cat.CollectionObjectID
               from attachment as at
               , collectionobjectattachment as cat

               where at.AttachmentLocation='{attachment_location}'
        and cat.AttachmentId = at.AttachmentId
        """
        coid = self.db_utils.get_one_record(sql)
        logging.debug(f"Got collectionObjectId: {coid}")

        return coid

    def create_attachment(self, storename, original_filename, file_created_datetime, guid, image_type, url,agent_id):
        # image type example 'image/png'

        sql = (f"""
                INSERT INTO attachment (attachmentlocation, attachmentstorageconfig, capturedevice, copyrightdate,
                                          copyrightholder, credit, dateimaged, filecreateddate, guid, ispublic, license,
                                          licenselogourl, metadatatext, mimetype, origfilename, remarks, scopeid,
                                          scopetype, subjectorientation, subtype, tableid, timestampcreated,
                                          timestampmodified, title, type, version, visibility, AttachmentImageAttributeID,
                                          CreatedByAgentID, CreatorID, ModifiedByAgentID, VisibilitySetByID)
                VALUES ('{storename}', NULL, NULL, NULL, 
                        NULL, NULL, NULL,   '{time_utils.get_pst_date_time_from_datetime(time_utils.get_pst_time(file_created_datetime))}', '{guid}', TRUE, NULL, 
                        NULL, NULL, '{image_type}','{original_filename}', '{url}', 4, 
                        0, NULL, NULL, 41, '{time_utils.get_pst_time_now_string()}',
                        '{time_utils.get_pst_time_now_string()}', '{original_filename.split(".")[0]}', NULL, 0, NULL, NULL, 
                        {agent_id}, NULL, NULL, NULL)
        """)
        cursor = self.db_utils.get_cursor()
        cursor.execute(sql)
        self.db_utils.commit()
        cursor.close()

    def create_collection_object_attachment(self, attachment_id, collection_object_id, ordinal, agent_id):
        # 68835 Joe russack ich
        # 95728 Joe russack botany
        cursor = self.db_utils.get_cursor()

        sql = (f"""INSERT INTO collectionobjectattachment 
            (collectionmemberid, 
            ordinal, 
            remarks, 
            timestampcreated,
            timestampmodified, 
            version, 
            AttachmentID, 
            CollectionObjectID,
            CreatedByAgentID, 
            ModifiedByAgentID)
        VALUES (
            4, 
            {ordinal}, 
            NULL, 
            '{time_utils.get_pst_time_now_string()}', 
            '{time_utils.get_pst_time_now_string()}',
            0, 
            {attachment_id}, 
            {collection_object_id}, 
            {agent_id},
            NULL)""")
        cursor.execute(sql)
        self.db_utils.commit()
        cursor.close()

    def get_attachment_id(self, uuid):
        sql = f"select attachmentid from attachment where guid='{uuid}'"
        return self.db_utils.get_one_record(sql)


    def get_ordinal_for_collection_object_attachment(self, collection_object_id):
        sql = f"select max(ordinal) from collectionobjectattachment where CollectionObjectID={collection_object_id}"
        return self.db_utils.get_one_record(sql)

    def get_is_attachment_redacted(self, internal_id):
        sql = f"""
            select a.AttachmentID,a.ispublic  from attachment a 
            where AttachmentLocation='{internal_id}'
    
            """
        cursor = self.db_utils.get_cursor()

        cursor.execute(sql)
        retval = cursor.fetchone()
        cursor.close()
        if retval is None:
            print(f"Error fetching attchment internal id: {internal_id}\n sql:{sql}")
            raise db_utils.DatabaseInconsistentError()

        retval = retval[1]
        if retval is None:
            logging.warning(f"Warning: No results from: \n\n{sql}\n")
        else:
            if retval is False or retval == 0:
                return True
        return False

    def get_is_collection_object_redacted(self, collection_object_id):
        sql = f"""
        select co.YesNo1, co.YesNo2, ta.YesNo1, ta.YesNo2,ta.TaxonID
    from collectionobject as co,
         taxon as ta,
         determination as de
    where co.CollectionObjectID = {collection_object_id}
      and de.CollectionObjectID = co.CollectionObjectID
      and de.TaxonID = ta.TaxonID
      and de.isCurrent = 1
        """
        cursor = self.db_utils.get_cursor()

        cursor.execute(sql)
        retval = cursor.fetchone()
        cursor.close()
        if retval is None:
            logging.error(f"Error fetching collection object id: {collection_object_id}\n sql:{sql}")
            raise DatabaseInconsistentError()

        logging.debug(f"Taxonid {retval[-1]}")
        retval = retval[:4]
        if retval is None:
            logging.warning(f"Warning: No results from: \n\n{sql}\n")
        else:
            for val in retval:
                if val is True or val == 1:
                    return True
        return False