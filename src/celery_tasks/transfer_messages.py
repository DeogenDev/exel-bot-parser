"""Задача на парсинг сообщений."""

import logging
import asyncio

from gspread.utils import rowcol_to_a1

from src.shared import conf
from src.celery_app import app
from src.models import BatchData, InputBatchProduct


logger = logging.getLogger(__name__)


def get_send_result_text(
    total_messages: int,
    transfered_messages: int,
    total_products: int,
    inserted_products: int,
):
    return (
        f"✅ Перенос сообщений завершен.\n\n"
        f"💬 Перенесено сообщений: {transfered_messages}/{total_messages}\n"
        f"📦 Вставлено товаров: {inserted_products}/{total_products}"
    )


@app.task(name="transfer_message_task", bind=True, queue="transfer")
def transfer_message_task(self, messages: list[str], output_user_id: int):
    from src.utils.message_extractor import messages_extractor
    from src.utils import table_manager, send_telegram_message
    from src.service import CharComparator

    char_comparator = CharComparator()

    logger.info(f"Extracting {len(messages)} messages")
    extract_messages = [
        messages_extractor.extract_message(message) for message in messages
    ]
    total_products_count = [
        len(message.products) for message in extract_messages if message.products
    ]
    base_texts_and_indexes = table_manager.get_product_names_and_indexes()
    first_empty_column_index = table_manager.get_empty_column_letter()
    current_column_index = first_empty_column_index

    count_products = 0
    count_inseret_messages = 0

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
            count_products += 1
        logger.info(message_input_products)
        table_manager.batch_update(message_input_products)
        count_inseret_messages += 1
        current_column_index += 1
    text = get_send_result_text(
        len(messages),
        count_inseret_messages,
        sum(total_products_count),
        count_products,
    )

    asyncio.run(
        send_telegram_message(
            token=conf.bot.token,
            chat_id=output_user_id,
            text=text,
        )
    )
    logger.info(f"Extracted {len(extract_messages)} messages")
