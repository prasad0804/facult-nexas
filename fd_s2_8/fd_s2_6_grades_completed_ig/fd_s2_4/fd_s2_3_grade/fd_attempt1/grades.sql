CREATE TABLE grades (
  student_id VARCHAR(255),
  course_id VARCHAR(255),
  faculty_id VARCHAR(255),
  test_name VARCHAR(20),
  test_score FLOAT,
  total_marks FLOAT,
  PRIMARY KEY (student_id(100), course_id(100), faculty_id(100), test_name),
  FOREIGN KEY (student_id, course_id, faculty_id) REFERENCES student_course(student_id, course_id, faculty_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;