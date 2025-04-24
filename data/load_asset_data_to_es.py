import json
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import RequestError, NotFoundError
import logging

# --- Configuration ---
# Default to 9200, adjust if needed (like your class uses 9201)
ELASTICSEARCH_HOST = os.getenv("ES_HOST", "http://localhost:9201")
INDEX_NAME = "assets_index"
DATA_FILE_PATH = "assets.json"  # Path to your JSON data file
# Set USE_PROVIDED_CLASS_FOR_TESTING to True if you want to run a test search
# using your class after loading. Make sure the class is importable.
USE_PROVIDED_CLASS_FOR_TESTING = True
# Adjust the import path based on your project structure if testing
# from your_package.elasticsearch_vector_store import EquipmentEntryElasticSearch

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Elasticsearch Mapping ---
# Define the mapping, specifically ensuring ASSETID.EQUIPMENTCODE is 'text'
# for fuzzy matching. Other fields will be dynamically mapped unless specified.
INDEX_MAPPING = {
    "properties": {
        "ASSETID": {
            "properties": {
                "EQUIPMENTCODE": {
                    "type": "text",
                    # Add keyword field for exact matches/aggregations if needed
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "DESCRIPTION": {"type": "text"},
                "ORGANIZATIONID": {
                    "properties": {
                        "ORGANIZATIONCODE": {
                            "type": "text",
                            "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
                        }
                        # other ORGANIZATIONID fields dynamically mapped
                    }
                }
                # other ASSETID fields dynamically mapped
            }
        },
        # Map based on python class names for clarity
        "equipmentdesc": {"type": "text"},
        "department": {"type": "keyword"},
        "eqtype": {"type": "keyword"},
        "organization": {"type": "keyword"},
        "assetstatus": {"type": "keyword"},
        "operationalstatus": {"type": "keyword"},
        "category": {"type": "keyword"},
        "class": {"type": "keyword"},
        # Handle potential date format
        "commissiondate": {"type": "date", "format": "epoch_millis||strict_date_optional_time"},
        # Add other known important fields or let them be dynamically mapped
        # Map fields referenced in the Python class explicitly if types matter
        "TYPE": {
            "properties": {
                "TYPECODE": {"type": "keyword"}
            }
        },
        "CLASSID": {
            "properties": {
                "CLASSCODE": {"type": "keyword"}
            }
        },
        "STATUS": {
            "properties": {
                "STATUSCODE": {"type": "keyword"}
            }
        },
        "DEPARTMENTID": {
            "properties": {
                "DEPARTMENTCODE": {"type": "keyword"}
            }
        },
        "CATEGORYID": {
            "properties": {
                "CATEGORYCODE": {"type": "keyword"}
            }
        }
        # ... map other fields as needed based on their expected type and usage
    }
    # Enable dynamic mapping for fields not explicitly defined
    # "dynamic": "true" # This is usually the default
}


def create_index_if_not_exists(client: Elasticsearch, index: str, mapping: dict):
    """Creates an index in Elasticsearch if it doesn't already exist."""
    try:
        if not client.indices.exists(index=index):
            logging.info(f"Index '{index}' not found. Creating...")
            client.indices.create(index=index, mappings=mapping)
            logging.info(f"Index '{index}' created successfully.")
        else:
            logging.info(f"Index '{index}' already exists.")
            # Optionally update mapping if needed (use with caution)
            # try:
            #     client.indices.put_mapping(index=index, properties=mapping['properties'])
            #     logging.info(f"Mapping updated for index '{index}'.")
            # except RequestError as e:
            #     logging.warning(f"Could not update mapping for index '{index}': {e.info['error']['reason']}")
    except RequestError as e:
        logging.error(f"Elasticsearch error creating index '{index}': {e}")
        raise
    except Exception as e:
        logging.error(
            f"An unexpected error occurred during index creation: {e}")
        raise


def generate_bulk_actions(filepath: str, index_name: str):
    """Reads the JSON file and yields actions for the Elasticsearch bulk helper."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: Data file not found at '{filepath}'")
        raise
    except json.JSONDecodeError:
        logging.error(f"Error: Could not decode JSON from file '{filepath}'")
        raise
    except Exception as e:
        logging.error(f"An error occurred reading the data file: {e}")
        raise

    if not isinstance(data, list):
        logging.error(
            f"Error: Expected a JSON list in '{filepath}', but got {type(data)}")
        raise ValueError("Invalid JSON format: Expected a list of objects.")

    logging.info(f"Preparing {len(data)} documents for bulk indexing.")
    count = 0
    skipped = 0
    for doc in data:
        try:
            # Use ASSETID.EQUIPMENTCODE as the document ID for idempotency
            # Handle potential missing keys gracefully
            asset_id_data = doc.get("ASSETID")
            if not asset_id_data or not isinstance(asset_id_data, dict):
                logging.warning(
                    f"Skipping record due to missing or invalid 'ASSETID': {doc.get('recordid', 'N/A')}")
                skipped += 1
                continue

            equipment_code = asset_id_data.get("EQUIPMENTCODE")
            if not equipment_code:
                logging.warning(
                    f"Skipping record due to missing 'ASSETID.EQUIPMENTCODE': {doc.get('recordid', 'N/A')}")
                skipped += 1
                continue

            # Clean up potential problematic fields before indexing if needed
            # For example, H3 requires specific date formats if mapped as date
            # Convert epoch millis in COMMISSIONDATE if present and mapping expects it
            if 'COMMISSIONDATE' in doc and isinstance(doc['COMMISSIONDATE'], dict) and 'YEAR' in doc['COMMISSIONDATE']:
                if isinstance(doc['COMMISSIONDATE']['YEAR'], (int, float)):
                   # Assuming 'YEAR' field actually holds epoch millis
                    doc['COMMISSIONDATE'] = int(doc['COMMISSIONDATE']['YEAR'])
                else:
                    # Handle cases where the date isn't epoch millis as expected
                    logging.warning(
                        f"Unexpected format for COMMISSIONDATE in doc id {equipment_code}, removing.")
                    del doc['COMMISSIONDATE']  # Or transform differently

            action = {
                "_index": index_name,
                "_id": equipment_code,  # Use equipment code as ID
                "_source": doc
            }
            yield action
            count += 1
        except Exception as e:
            logging.error(
                f"Error preparing document with equipment code '{equipment_code}': {e}. Skipping.")
            skipped += 1

    logging.info(f"Generated {count} actions, skipped {skipped} records.")


def load_data_to_es(client: Elasticsearch, index: str, filepath: str):
    """Loads data from the JSON file into the specified Elasticsearch index."""
    logging.info(f"Starting data load from '{filepath}' to index '{index}'...")
    try:
        success, failed = bulk(
            client=client,
            actions=generate_bulk_actions(filepath, index),
            chunk_size=500,  # Adjust chunk size based on document size and ES capacity
            request_timeout=60  # Increase timeout for large bulks
        )
        logging.info(
            f"Bulk indexing completed. Success: {success}, Failed: {failed}")
        if failed > 0:
            logging.warning(
                "Some documents failed to index. Check Elasticsearch logs for details.")
        # Explicitly refresh the index to make changes searchable immediately (optional)
        try:
            client.indices.refresh(index=index)
            logging.info(f"Index '{index}' refreshed.")
        except NotFoundError:
            logging.warning(
                f"Index '{index}' not found during refresh (might indicate previous failure).")

    except Exception as e:
        logging.error(f"An error occurred during bulk indexing: {e}")
        raise


# --- Main Execution ---
if __name__ == "__main__":
    logging.info("Script started.")
    logging.info(f"Connecting to Elasticsearch at {ELASTICSEARCH_HOST}")

    try:
        # Instantiate Elasticsearch client
        es_client = Elasticsearch(
            hosts=[ELASTICSEARCH_HOST],
            # Add authentication here if needed (e.g., basic_auth=('user', 'password'))
            # basic_auth=('elastic', 'changeme'), # Example basic auth
            verify_certs=False,  # Set to True if using HTTPS with valid certs
            ssl_show_warn=False  # Suppress SSL warnings if verify_certs=False
        )

        # Verify connection
        if not es_client.ping():
            raise ConnectionError(
                f"Could not connect to Elasticsearch at {ELASTICSEARCH_HOST}")
        logging.info("Successfully connected to Elasticsearch.")

        # 1. Create index with mapping (if it doesn't exist)
        create_index_if_not_exists(es_client, INDEX_NAME, INDEX_MAPPING)

        # 2. Load data using bulk API
        load_data_to_es(es_client, INDEX_NAME, DATA_FILE_PATH)

    except FileNotFoundError:
        logging.error(
            f"Fatal Error: Data file '{DATA_FILE_PATH}' not found. Exiting.")
    except ConnectionError as e:
        logging.error(
            f"Fatal Error: Could not establish connection to Elasticsearch. {e}. Exiting.")
    except Exception as e:
        logging.error(f"An unexpected fatal error occurred: {e}. Exiting.")
