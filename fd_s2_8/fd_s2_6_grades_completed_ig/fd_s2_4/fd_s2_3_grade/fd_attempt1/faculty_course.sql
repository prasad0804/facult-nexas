CREATE TABLE faculty_course (
    faculty_id VARCHAR(255) NOT NULL,
    course_id VARCHAR(255) NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (faculty_id, course_id),
    FOREIGN KEY (faculty_id) REFERENCES faculty_details(faculty_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
