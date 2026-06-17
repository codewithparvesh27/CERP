CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS correction_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_number TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING_USER_CORRECTION',
    original_request TEXT NOT NULL,
    original_response TEXT NOT NULL,
    revised_request TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS correction_work_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES correction_sessions(id) ON DELETE CASCADE,
    condition_code TEXT NOT NULL,
    severity_code TEXT,
    disposition_type_code TEXT,
    narrative_text TEXT,
    scope TEXT,
    view_name TEXT,
    section_name TEXT,
    ui_field_name TEXT,
    ui_label TEXT,
    record_id TEXT,
    request_line_number INTEGER,
    request_line_no TEXT,
    field_name TEXT,
    field_start INTEGER,
    field_end INTEGER,
    current_value TEXT,
    corrected_value TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    raw_response_context JSONB NOT NULL DEFAULT '[]'::jsonb,
    raw_response_condition JSONB NOT NULL DEFAULT '{}'::jsonb,
    validation JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES correction_sessions(id) ON DELETE CASCADE,
    work_item_id UUID REFERENCES correction_work_items(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
