"""Задача на парсинг сообщений."""

import logging

from gspread.utils import rowcol_to_a1


from src.celery_app import app
from src.models import BatchData, InputBatchProduct


logger = logging.getLogger(__name__)


@app.task(name="transfer_message_task", bind=True, queue="transfer")
def transfer_message_task(self, messages: list[str]):
    from src.utils.message_extractor import messages_extractor
    from src.utils import table_manager
    from src.service import CharComparator

    char_comparator = CharComparator()

    logger.info(f"Extracting {len(messages)} messages")
    extract_messages = [
        messages_extractor.extract_message(message) for message in messages
    ]
    base_texts_and_indexes = table_manager.get_product_names_and_indexes()
    first_empty_column_index = table_manager.get_empty_column_letter()
    current_column_index = first_empty_column_index
    for message in extract_messages:
        message_input_products = InputBatchProduct(
            insert_data=[
                BatchData(
                    range=rowcol_to_a1(2, current_column_index),
                    values=[[message.buyer_name]],
                )
            ]
        )
        for product in message.products:
            output_comparator = char_comparator.search_sim(
                product.name, base_texts_and_indexes
            )
            horizontal_index = output_comparator.horiazontal_product_line
            message_input_products.insert_data.append(
                BatchData(
                    range=rowcol_to_a1(horizontal_index, current_column_index),
                    values=[[product.count]],
                )
            )
        logger.info(message_input_products)
        table_manager.batch_update(message_input_products)
        current_column_index += 1

    logger.info(f"Extracted {len(extract_messages)} messages")
