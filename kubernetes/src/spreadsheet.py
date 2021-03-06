from typing import List
from googleapiclient.discovery import build

from certification import Certification, CertificationDeserializationError
from config import settings
from google_auth_helpers import getGoogleCredentials


class SpreadsheetDownloadFailed(Exception):
    pass


def downloadSpreadsheet() -> List[str]:
    creds = getGoogleCredentials()
    sheetsAPI = build("sheets", "v4", credentials=creds)
    # fmt: off
    result = sheetsAPI.spreadsheets().values().get(
        spreadsheetId   = settings.SPREADSHEET_ID,
        range           = settings.SHEET_NAME
    ).execute()
    # fmt: on

    rows = result.get("values")
    return rows


class SpreadsheetDeserializationFailed(Exception):
    pass


def parseSpreadsheetRows(rows) -> List[Certification]:
    parsingErrors = []
    certifications = []
    for row in rows[1:]:  # Ignoring header
        try:
            certifications.append(Certification(row))
        # We keep gathering errors until we have tried to parse all the rows
        # so that we know everything we have to fix and not just a single item
        except CertificationDeserializationError as e:
            parsingErrors.append(e)
    if parsingErrors:
        raise SpreadsheetDeserializationFailed(parsingErrors)
    return certifications
