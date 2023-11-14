CREATE TABLE courses (
    course_id VARCHAR(255) PRIMARY KEY,
    course_name TEXT NOT NULL,
    course_description TEXT,
    course_credits INTEGER NOT NULL,
    course_start_date DATE NOT NULL,
    course_end_date DATE NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;