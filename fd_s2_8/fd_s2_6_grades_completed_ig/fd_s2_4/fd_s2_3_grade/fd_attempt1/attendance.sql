CREATE TABLE attendance (
    student_id VARCHAR(255) NOT NULL,
    course_id VARCHAR(255) NOT NULL,
    faculty_id VARCHAR(255) NOT NULL,
    date_ DATE NOT NULL,
    hour_ INTEGER NOT NULL,
    status_ VARCHAR(11),
    PRIMARY KEY (student_id, course_id, faculty_id,date_, hour_),
    FOREIGN KEY (student_id, course_id,faculty_id) REFERENCES student_course(student_id, course_id,faculty_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;