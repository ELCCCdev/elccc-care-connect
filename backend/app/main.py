"""Local-only fictional inquiries demo. Never store real patient information."""
from contextlib import closing, asynccontextmanager
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import sqlite3
from typing import Literal, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict, Field

BACKEND_DIR = Path(__file__).resolve().parent.parent
Category = Literal['individual', 'couples', 'family', 'general']
ContactMethod = Literal['email', 'phone']
Status = Literal['new', 'reviewing', 'closed']


class InquiryCreate(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    fictional_client_name: str = Field(min_length=2, max_length=80)
    category: Category
    preferred_contact_method: ContactMethod
    fictional_data_only: Literal[True] = Field(
        description='Confirm this submission contains only made-up demonstration data.'
    )


class Inquiry(BaseModel):
    inquiry_id: UUID
    fictional_client_name: str
    category: Category
    preferred_contact_method: ContactMethod
    status: Status
    created_at: datetime


PortalStatus = Literal['Not Sent', 'Sent', 'Activated']


class ConversionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    confirmed: Literal[True]


class PortalStatusUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    portal_status: PortalStatus


class HistoryEvent(BaseModel):
    action: str
    occurred_at: datetime
    detail: str


class ManagedInquiry(Inquiry):
    converted_at: Optional[datetime] = None
    portal_status: PortalStatus = 'Not Sent'
    history: list[HistoryEvent]

def create_app(db_path: Optional[Path] = None, *, seed: bool = True) -> FastAPI:
    """Factory allows tests to use disposable SQLite files."""
    database = Path(db_path) if db_path is not None else Path(
        os.environ.get('ELCCC_DB_PATH', str(BACKEND_DIR / 'data' / 'inquiries.sqlite3'))
    ).expanduser().resolve()

    def connect():
        connection = sqlite3.connect(database, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys = ON')
        return connection

    def insert(connection, name, category, contact, status='new'):
        record = {
            'inquiry_id': str(uuid4()), 'fictional_client_name': name,
            'category': category, 'preferred_contact_method': contact,
            'status': status, 'created_at': datetime.now(timezone.utc).isoformat(),
        }
        connection.execute(
            'INSERT INTO inquiries VALUES (:inquiry_id, :fictional_client_name, '
            ':category, :preferred_contact_method, :status, :created_at)', record
        )
        return record

    @asynccontextmanager
    async def lifespan(app):
        database.parent.mkdir(parents=True, exist_ok=True)
        with closing(connect()) as connection, connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS inquiries (
                inquiry_id TEXT PRIMARY KEY,
                fictional_client_name TEXT NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('individual','couples','family','general')),
                preferred_contact_method TEXT NOT NULL CHECK(preferred_contact_method IN ('email','phone')),
                status TEXT NOT NULL CHECK(status IN ('new','reviewing','closed')),
                created_at TEXT NOT NULL
            )''')
            connection.execute('PRAGMA foreign_keys = ON')
            connection.execute("""CREATE TABLE IF NOT EXISTS inquiry_management (
                inquiry_id TEXT PRIMARY KEY REFERENCES inquiries(inquiry_id),
                converted_at TEXT,
                portal_status TEXT NOT NULL DEFAULT 'Not Sent'
                  CHECK(portal_status IN ('Not Sent','Sent','Activated'))
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS inquiry_history (
                event_id INTEGER PRIMARY KEY,
                inquiry_id TEXT NOT NULL REFERENCES inquiries(inquiry_id),
                action TEXT NOT NULL, occurred_at TEXT NOT NULL, detail TEXT NOT NULL
            )""")
            # Seed once per database, even when an existing database is later emptied.
            connection.execute('CREATE TABLE IF NOT EXISTS demo_metadata (key TEXT PRIMARY KEY)')
            if seed and connection.execute(
                "SELECT key FROM demo_metadata WHERE key = 'samples_seeded'"
            ).fetchone() is None:
                for sample in [
                    ('Demo Avery Maple', 'individual', 'email', 'new'),
                    ('Demo Jordan Lantern', 'family', 'phone', 'reviewing'),
                    ('Demo Casey Meadow', 'general', 'email', 'closed'),
                ]:
                    insert(connection, *sample)
                connection.execute("INSERT INTO demo_metadata VALUES ('samples_seeded')")
        yield

    app = FastAPI(title='ELCCC Care Connect — DEVELOPMENT ONLY', lifespan=lifespan,
                  description='Local prototype for fictional data only. Not HIPAA-ready.')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://127.0.0.1:5500', 'http://localhost:5500'],
        allow_methods=['GET', 'POST'],
        allow_headers=['Content-Type'],
        allow_credentials=False,
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={
            'detail': 'Invalid inquiry. Use fictional data and the allowed field values.',
            'errors': [{'field': '.'.join(str(part) for part in error['loc']),
                        'message': error['msg']} for error in exc.errors()],
        })

    @app.exception_handler(sqlite3.Error)
    async def database_error(request: Request, exc: sqlite3.Error):
        logging.getLogger(__name__).error('SQLite operation failed (%s)', type(exc).__name__)
        return JSONResponse(status_code=503, content={
            'detail': 'Local database unavailable. Check the database path and file permissions, then retry.'
        })

    @app.get('/', include_in_schema=False)
    def home():
        return RedirectResponse('/demo')

    @app.get('/demo', include_in_schema=False)
    def demo():
        return FileResponse(BACKEND_DIR / 'app' / 'demo.html', media_type='text/html',
                            headers={'Cache-Control': 'no-store'})

    @app.get('/health')
    def health():
        with closing(connect()) as connection:
            connection.execute('SELECT 1 FROM inquiries LIMIT 1')
        return {'status': 'ok', 'database': 'ok', 'environment': 'local-development'}

    @app.post('/api/inquiries', response_model=Inquiry, status_code=201)
    def create_inquiry(payload: InquiryCreate):
        with closing(connect()) as connection, connection:
            return insert(connection, payload.fictional_client_name,
                          payload.category, payload.preferred_contact_method)

    @app.get('/api/inquiries', response_model=list[Inquiry])
    def list_inquiries():
        with closing(connect()) as connection:
            return [dict(row) for row in connection.execute(
                'SELECT * FROM inquiries ORDER BY created_at DESC, inquiry_id DESC'
            )]

    @app.get('/api/inquiries/{inquiry_id}', response_model=Inquiry)
    def get_inquiry(inquiry_id: UUID):
        with closing(connect()) as connection:
            record = connection.execute(
                'SELECT * FROM inquiries WHERE inquiry_id = ?', (str(inquiry_id),)
            ).fetchone()
        if record is None:
            raise HTTPException(status_code=404, detail='Inquiry not found. Check the inquiry ID.')
        return dict(record)

    def managed_record(connection, inquiry_id):
        row = connection.execute(
            """SELECT i.*, m.converted_at, COALESCE(m.portal_status, 'Not Sent') AS portal_status
               FROM inquiries i LEFT JOIN inquiry_management m USING(inquiry_id)
               WHERE i.inquiry_id = ?""", (str(inquiry_id),)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail='Inquiry not found. Check the inquiry ID.')
        record = dict(row)
        record['history'] = [dict(action='Inquiry created', occurred_at=record['created_at'],
                                  detail='Original fictional inquiry received.')] + [
            dict(event) for event in connection.execute(
                'SELECT action, occurred_at, detail FROM inquiry_history WHERE inquiry_id = ? ORDER BY event_id',
                (str(inquiry_id),))]
        return record

    def management_list(converted):
        with closing(connect()) as connection:
            ids = connection.execute(
                'SELECT i.inquiry_id FROM inquiries i LEFT JOIN inquiry_management m USING(inquiry_id) '
                + ('WHERE m.converted_at IS NOT NULL ' if converted else 'WHERE m.converted_at IS NULL ')
                + 'ORDER BY i.created_at DESC, i.inquiry_id DESC').fetchall()
            return [managed_record(connection, row['inquiry_id']) for row in ids]

    @app.get('/api/prospective-clients', response_model=list[ManagedInquiry])
    def prospective_clients():
        return management_list(False)

    @app.get('/api/clients', response_model=list[ManagedInquiry])
    def established_clients():
        return management_list(True)

    @app.get('/api/inquiries/{inquiry_id}/management', response_model=ManagedInquiry)
    def get_management(inquiry_id: UUID):
        with closing(connect()) as connection:
            return managed_record(connection, inquiry_id)

    @app.post('/api/inquiries/{inquiry_id}/convert', response_model=ManagedInquiry)
    def convert_to_client(inquiry_id: UUID, payload: ConversionRequest):
        with closing(connect()) as connection, connection:
            # Serialize state transitions, including competing requests from other tabs.
            connection.execute('BEGIN IMMEDIATE')
            record = managed_record(connection, inquiry_id)
            if record['converted_at'] is not None:
                raise HTTPException(status_code=409, detail='This inquiry is already an established client. Refresh the list.')
            timestamp = datetime.now(timezone.utc).isoformat()
            connection.execute(
                'INSERT INTO inquiry_management (inquiry_id, converted_at) VALUES (?, ?) '
                'ON CONFLICT(inquiry_id) DO UPDATE SET converted_at = excluded.converted_at',
                (str(inquiry_id), timestamp))
            connection.execute('INSERT INTO inquiry_history (inquiry_id, action, occurred_at, detail) VALUES (?, ?, ?, ?)',
                               (str(inquiry_id), 'Converted to client', timestamp,
                                'Confirmed fictional conversion in the ELCCC local workflow.'))
            return managed_record(connection, inquiry_id)

    @app.post('/api/inquiries/{inquiry_id}/portal-status', response_model=ManagedInquiry)
    def update_portal_status(inquiry_id: UUID, payload: PortalStatusUpdate):
        with closing(connect()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            record = managed_record(connection, inquiry_id)
            if record['portal_status'] != payload.portal_status:
                timestamp = datetime.now(timezone.utc).isoformat()
                connection.execute(
                    'INSERT INTO inquiry_management (inquiry_id, portal_status) VALUES (?, ?) '
                    'ON CONFLICT(inquiry_id) DO UPDATE SET portal_status = excluded.portal_status',
                    (str(inquiry_id), payload.portal_status))
                connection.execute('INSERT INTO inquiry_history (inquiry_id, action, occurred_at, detail) VALUES (?, ?, ?, ?)',
                                   (str(inquiry_id), 'MYIO tracking updated', timestamp,
                                    record['portal_status'] + ' → ' + payload.portal_status + '; tracking only, no invitation sent.'))
            return managed_record(connection, inquiry_id)

    return app


app = create_app()
