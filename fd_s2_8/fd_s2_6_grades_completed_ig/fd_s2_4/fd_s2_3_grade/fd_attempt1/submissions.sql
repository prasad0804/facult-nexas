CREATE TABLE submissions(
  student_id VARCHAR(100),
  course_id VARCHAR(100),
  faculty_id VARCHAR(100),
  assignment_name VARCHAR(25),
  submitted_date DATE NOT NULL,
  student_submission VARCHAR(255),
  PRIMARY KEY (student_id(100), course_id(100), faculty_id(100), assignment_name(20)),
  FOREIGN KEY (student_id, course_id, faculty_id,assignment_name) REFERENCES assignment(student_id, course_id, faculty_id,assignment_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;