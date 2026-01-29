"""Задача на парсинг сообщений."""

import logging
import asyncio

from gspread.utils import rowcol_to_a1

from src.shared import conf
from src.celery_app import app
from src.models import BatchData, InputBatchProduct, ExtractMessage
from src.shared import send_telegram_message


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


async def send_error_log_message(original_text: str, error_text: str) -> None:
    text = f"⛔️⛔️Ошибка при обработке сообщения⛔️⛔️\n======Сообщение======\n\n{original_text}\n======Причина======\n{error_text}"
    await send_telegram_message(
        chat_id=conf.bot.parse_channel_id,
        text=text,
        thread_id=conf.bot.logs_topic_id,
    )


async def extract_messages(
    messages: list[str],
) -> tuple[list[ExtractMessage], list[str]]:
    from src.utils.message_extractor import (
        messages_extractor,
        MessageExtractError,
        MessageExtractNoName,
    )

    extracted_messages: list[ExtractMessage] = []
    input_messages = []

    for message in messages:
        try:
            extracted = messages_extractor.extract_message(message)
            extracted_messages.append(extracted)
            input_messages.append(message)
            logger.info(extracted.errors_products)
            if extracted.errors_products:
                error_text = "Не удалось распознать товары:\n" + "\n".join(
                    extracted.errors_products
                )
                await send_error_log_message(
                    original_text=message,
                    error_text=error_text,
                )
        except MessageExtractNoName:
            logger.warning("Message %s has no buyer name", message)
            await send_error_log_message(
                original_text=message,
                error_text="Не удалось распознать покупателя.",
            )
        except MessageExtractError as e:
            await send_error_log_message(
                original_text=message,
                error_text=str(e),
            )
            logger.exception(
                "Failed to extract message ID %s (other extraction error)",
            )
            continue

    return extracted_messages, input_messages


def get_table_data(table_manager) -> tuple[list, int]:
    base_texts = table_manager.get_product_names_and_indexes()
    current_column = table_manager.get_empty_column_letter()

    if not base_texts:
        raise Exception("No product names in table")

    if not current_column:
        raise Exception("No empty column in table")

    return base_texts, current_column


@app.task(name="transfer_message_task", bind=True, queue="transfer")
def transfer_message_task(self, messages: list[str], output_user_id: int) -> None:
    from src.service import CharComparator
    from src.utils import table_manager

    char_comparator = CharComparator()

    if not messages:
        logger.warning("transfer_message_task called with empty messages list")
        return

    base_texts, current_column = get_table_data(table_manager)
    extracted_messages, input_messages = asyncio.run(extract_messages(messages))

    inserted_messages_count = 0
    processed_products_count = 0

    for original_text, extracted in zip(input_messages, extracted_messages):
        failed_products: list[str] = []
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
                        "CharComparator failed for product '%s'", product.name
                    )
                    failed_products.append(product.name)
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

        except Exception as e:
            logger.exception("Failed to process message (critical): %s", e)
            asyncio.run(
                send_error_log_message(
                    original_text=original_text,
                    error_text=str(e),
                )
            )
    result_text = get_send_result_text(
        len(messages),
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
