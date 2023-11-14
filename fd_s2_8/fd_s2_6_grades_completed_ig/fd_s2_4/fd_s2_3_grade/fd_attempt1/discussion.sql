CREATE TABLE discussions (
    course_id VARCHAR(255) NOT NULL,
    faculty_id VARCHAR(255) NOT NULL,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (faculty_id(100),course_id(100),message(200)),
    FOREIGN KEY (faculty_id,course_id) REFERENCES faculty_course(faculty_id,course_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;