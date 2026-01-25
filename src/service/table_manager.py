"""Менеджер таблицы."""

import gspread
from gspread import Client
from google.oauth2.service_account import Credentials

from src.models import HorizontalProductLine, InputBatchProduct


class TableManager:
    AUTH_URLS = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    def __init__(self, credentials: str, spreadsheet_id: str, sheet_name: str):
        self.credentials = credentials
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.client = self._get_client()
        self.sheet = self._read_sheet()
        self.products_and_indexes = list[HorizontalProductLine]

    def write_to_cell(self, row, col, value):
        self.sheet.update_cell(row, col, value)

    def batch_update(self, data: InputBatchProduct):
        prepared_data = data.model_dump()["insert_data"]
        self.sheet.batch_update(prepared_data)

    def get_empty_column_letter(self) -> int:
        row_values = self.sheet.get("2:2")
        len_row = len(row_values[0]) + 1
        return len_row

    def get_product_names_and_indexes(
        self, max_empty=10
    ) -> list[HorizontalProductLine]:
        col_values = self.sheet.get(f"A1:A{self.sheet.row_count}")  # один запрос
        result = []
        empty_count = 0
        for i, row in enumerate(col_values, start=1):
            val = row[0] if row else ""
            if val and val.strip():
                result.append(HorizontalProductLine(product_name=val, index=i))
                empty_count = 0
            else:
                empty_count += 1
                if empty_count >= max_empty:
                    break

        return result

    def _read_sheet(self) -> gspread.Worksheet:
        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        return spreadsheet.worksheet(self.sheet_name)

    def _get_client(self) -> Client:
        return gspread.authorize(
            Credentials.from_service_account_file(
                filename=self.credentials,
                scopes=self.AUTH_URLS,
            )
        )
