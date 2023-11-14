CREATE TABLE scale (
    course_id VARCHAR(255) NOT NULL,
    faculty_id VARCHAR(255) NOT NULL,
    test_name VARCHAR(20) NOT NULL,
    weight float NOT NULL,
    PRIMARY KEY (course_id, faculty_id,test_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;