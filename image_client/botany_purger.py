import logging
from specify_db import SpecifyDb
from attachment_utils import AttachmentUtils
import botany_importer_config
from image_client import ImageClient


class BotanyPurger():
    def __init__(self):
        self.logger = logging.getLogger('Client.purger')
        self.specify_db = SpecifyDb(botany_importer_config)
        self.attachment_utils = AttachmentUtils(self.specify_db)
        self.logger.debug(f"BotanyPurger setup complete")
        self.image_client = ImageClient()

    def purge(self):

        # import csv
        # with open('doomed.csv') as csv_file:
        #     csv_reader = csv.reader(csv_file, delimiter=',')
        #     line_count = 0
        #     for row in csv_reader:
        #         collection_object_id = row[0]
        #         collecting_event_id = row[1]
        #         print(f"Deleting {collecting_event_id}, {collection_object_id}")
        #         sql = f"delete from collectionobject where CollectionObjectID={collection_object_id}"
        #         self.specify_db.execute(sql)
        #
        #         sql = f"delete from collectingevent where CollectingEventID={collecting_event_id}"
        #         self.specify_db.execute(sql)

        self.purge_attachments_from_image_server()
        self.purge_skeletons()

        self.logger.debug(f"Remove collection object attachments")
        sql = f"delete from collectionobjectattachment"
        self.specify_db.execute(sql)

        self.logger.debug(f"Remove attachments")
        sql = f"delete from attachment"
        self.specify_db.execute(sql)

    def purge_attachments_from_image_server(self):
        self.logger.debug("Pulling image records from image server")

        sql = f"""select AttachmentLocation from attachment"""
        attachment_locations = self.specify_db.get_records(sql)
        for attachment_location in attachment_locations:
            self.image_client.delete_from_image_server(attachment_location[0],
                                                       botany_importer_config.COLLECTION_NAME)

    def purge_skeletons(self):
        sql = (f"""
             select collectionobjectattachment.CollectionObjectID,
                    determination.DeterminationID,
                    determination.TaxonID,
                    collectionobject.CatalogNumber,
                    collectionobjectattachment.AttachmentID,
                    collectionobjectattachment.CollectionObjectAttachmentID,
                    collectionobject.CollectingEventID,
                    attachmentlocation,
                    attachment.origFilename
    
    
             from casbotany.collectionobjectattachment
                      INNER join casbotany.attachment ON attachment.AttachmentID = collectionobjectattachment.AttachmentID
                      INNER join casbotany.collectionobject
                                 ON collectionobject.CollectionObjectID = collectionobjectattachment.CollectionObjectID
                      left join casbotany.determination
                                on casbotany.collectionobject.CollectionObjectID = casbotany.determination.CollectionObjectID
             where determination.DeterminationID is NULL and collectionobject.version = 0;        
         """)
        specify_list = self.specify_db.get_records(sql)
        for remove_record in specify_list:
            collecting_event_id = remove_record[6]
            collection_object_id = remove_record[0]
            barcode = remove_record[3]
            self.logger.debug(f"Purging bardocde: {barcode}")
            self.logger.debug(f"Removing collecting event ID: {collecting_event_id}")

            self.logger.debug(f"Find and remove attachments from collection object {collection_object_id}")

            self.logger.debug(f"Removing collecting object ID: {collection_object_id}")
            sql = f"delete from collectionobject where CollectionObjectID={collection_object_id}"
            self.specify_db.execute(sql)

            sql = f"delete from collectingevent where CollectingEventID={collecting_event_id}"
            self.specify_db.execute(sql)

        # query_skeletons = [int(item[3]) for item in specify_list]
