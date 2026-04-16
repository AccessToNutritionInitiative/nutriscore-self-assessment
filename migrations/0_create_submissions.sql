CREATE TABLE IF NOT EXISTS submissions (
    submission_id TEXT PRIMARY KEY,
    submitted_at TEXT NOT NULL,
    answers TEXT NOT NULL
);
