from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class NfcRepository:
    def __init__(self, db: Session):
        self._db = db

    def get_tag(self, tag_id: str):
        return self._db.execute(
            text(
                '''
                SELECT tag_id, patient_id, status, issued_at, deactivated_at
                FROM "nfc_tags"
                WHERE tag_id = :tag_id
                '''
            ),
            {"tag_id": tag_id},
        ).fetchone()

    def get_all_tags(
        self,
        limit: int,
        cursor: Optional[str],
        status: Optional[str],
        search: Optional[str],
    ):
        search_pattern = f"%{search}%" if search else None
        return self._db.execute(
            text(
                '''
                SELECT tag_id, patient_id, status, issued_at, deactivated_at
                FROM "nfc_tags"
                WHERE (:cursor IS NULL OR tag_id > :cursor)
                  AND (:status IS NULL OR status = :status)
                  AND (
                    :search IS NULL
                    OR tag_id ILIKE :search_pattern
                    OR CAST(patient_id AS text) ILIKE :search_pattern
                  )
                ORDER BY tag_id ASC
                LIMIT :limit
                '''
            ),
            {
                "limit": limit,
                "cursor": cursor,
                "status": status,
                "search": search,
                "search_pattern": search_pattern,
            },
        ).fetchall()

    def get_stats(self):
        return self._db.execute(
            text(
                '''
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active,
                    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) AS inactive
                FROM "nfc_tags"
                '''
            )
        ).fetchone()

    def get_patient(self, patient_id):
        return self._db.execute(
            text(
                '''
                SELECT id
                FROM "patients"
                WHERE id = :patient_id
                '''
            ),
            {"patient_id": patient_id},
        ).fetchone()

    def get_active_tag_for_patient(self, patient_id):
        return self._db.execute(
            text(
                '''
                SELECT tag_id
                FROM "nfc_tags"
                WHERE patient_id = :patient_id
                  AND status = 'active'
                '''
            ),
            {"patient_id": patient_id},
        ).fetchone()

    def get_tag_for_patient(self, patient_id):
        return self._db.execute(
            text(
                '''
                SELECT tag_id, patient_id, status, issued_at, deactivated_at
                FROM "nfc_tags"
                WHERE patient_id = :patient_id
                  AND status = 'active'
                '''
            ),
            {"patient_id": patient_id},
        ).fetchone()

    def upsert_tag(self, tag_id: str, patient_id):
        self._db.execute(
            text(
                '''
                INSERT INTO "nfc_tags" (tag_id, patient_id, status, issued_at, deactivated_at)
                VALUES (:tag_id, :patient_id, 'active', CURRENT_TIMESTAMP, NULL)
                ON CONFLICT (tag_id)
                DO UPDATE SET
                    patient_id = EXCLUDED.patient_id,
                    status = 'active',
                    issued_at = CURRENT_TIMESTAMP,
                    deactivated_at = NULL
                '''
            ),
            {
                "tag_id": tag_id,
                "patient_id": patient_id,
            },
        )

    def deactivate_tag(self, tag_id: str):
        return self._db.execute(
            text(
                '''
                UPDATE "nfc_tags"
                SET status = 'inactive',
                    deactivated_at = CURRENT_TIMESTAMP
                WHERE tag_id = :tag_id
                '''
            ),
            {"tag_id": tag_id},
        ).rowcount

    def deactivate_tags_for_patient(self, patient_id):
        return self._db.execute(
            text(
                '''
                UPDATE "nfc_tags"
                SET status = 'inactive',
                    deactivated_at = CURRENT_TIMESTAMP
                WHERE patient_id = :patient_id
                '''
            ),
            {"patient_id": patient_id},
        ).rowcount

    def deactivate_all_tags(self):
        return self._db.execute(
            text(
                '''
                UPDATE "nfc_tags"
                SET status = 'inactive',
                    deactivated_at = CURRENT_TIMESTAMP
                '''
            )
        ).rowcount

    def reactivate_tag(self, tag_id: str):
        return self._db.execute(
            text(
                '''
                UPDATE "nfc_tags"
                SET status = 'active',
                    deactivated_at = NULL
                WHERE tag_id = :tag_id
                '''
            ),
            {"tag_id": tag_id},
        ).rowcount

    def commit(self):
        self._db.commit()
