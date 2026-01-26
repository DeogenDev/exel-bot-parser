"""Задача на парсинг сообщений."""

import logging
import asyncio

from gspread.utils import rowcol_to_a1

from src.shared import conf
from src.celery_app import app
from src.models import BatchData, InputBatchProduct, ExtractMessage
from src.utils import send_telegram_message


logger = logging.getLogger(__name__)


COMPRATOR_TEXT_ERROR = (
    "🚫 Произошла ошибка при сравнивании для товара: - {product_name}."
)


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


async def send_log_message(
    original_text: str,
    extract_message_text: ExtractMessage,
    message_input_products: InputBatchProduct,
) -> None:
    parsed_products = "\n".join(
        f"{product.name} - {product.count}" for product in extract_message_text.products
    )

    inserted_products = "\n".join(
        f"{product.values[0][0]} => {product.range}"
        for product in message_input_products.insert_data
    )

    text = (
        "=======Сообщение========\n"
        f"{original_text}\n"
        "=======Определено=======\n"
        f"Заказчик - {extract_message_text.buyer_name}\n"
        f"{parsed_products}\n"
        "=======Вставлено========\n"
        f"{inserted_products}"
    )

    await send_telegram_message(
        chat_id=conf.bot.parse_channel_id,
        text=text,
        thread_id=conf.bot.logs_topic_id,
    )


@app.task(name="transfer_message_task", bind=True, queue="transfer")
def transfer_message_task(self, messages: list[str], output_user_id: int) -> None:
    from src.utils.message_extractor import messages_extractor
    from src.utils import table_manager
    from src.service import CharComparator

    if not messages:
        logger.warning("transfer_message_task called with empty messages list")
        return

    char_comparator = CharComparator()
    messages_count = len(messages)

    logger.info("Extracting %s messages", messages_count)

    try:
        extracted_messages = [
            messages_extractor.extract_message(message) for message in messages
        ]
    except Exception:
        logger.exception("Failed to extract messages")
        return

    try:
        base_texts = table_manager.get_product_names_and_indexes()
        current_column = table_manager.get_empty_column_letter()
    except Exception:
        logger.exception("Failed to initialize table state")
        return

    inserted_messages_count = 0
    processed_products_count = 0
    failed_messages_count = 0

    for original_text, extracted in zip(messages, extracted_messages):
        try:
            batch = InputBatchProduct(
                insert_data=[
                    BatchData(
                        range=rowcol_to_a1(2, current_column),
                        values=[[extracted.buyer_name]],
                    )
                ]
            )

            for product in extracted.products or ():
                try:
                    comparator_result = char_comparator.search_sim(
                        product.name,
                        base_texts,
                    )
                except Exception:
                    logger.exception(
                        "CharComparator failed for product '%s'",
                        product.name,
                    )
                    asyncio.run(
                        send_telegram_message(
                            chat_id=output_user_id,
                            thread_id=conf.bot.logs_topic_id,
                            text=COMPRATOR_TEXT_ERROR.format(product_name=product.name),
                        )
                    )
                    continue

                batch.insert_data.append(
                    BatchData(
                        range=rowcol_to_a1(
                            comparator_result.horiazontal_product_line,
                            current_column,
                        ),
                        values=[[product.count]],
                    )
                )

                product.name = comparator_result.similar_base_text
                processed_products_count += 1

            table_manager.batch_update(batch)
            inserted_messages_count += 1
            current_column += 1

            asyncio.run(
                send_log_message(
                    original_text=original_text,
                    extract_message_text=extracted,
                    message_input_products=batch,
                )
            )

        except Exception:
            failed_messages_count += 1
            logger.exception("Failed to process message: %s", original_text)
            continue

    result_text = get_send_result_text(
        messages_count,
        inserted_messages_count,
        sum(len(msg.products) for msg in extracted_messages if msg.products),
        processed_products_count,
    )

    asyncio.run(
        send_telegram_message(
            chat_id=output_user_id,
            text=result_text,
        )
    )

    logger.info(
        "Finished transfer_message_task: total=%s, inserted=%s, failed=%s",
        messages_count,
        inserted_messages_count,
        failed_messages_count,
    )
