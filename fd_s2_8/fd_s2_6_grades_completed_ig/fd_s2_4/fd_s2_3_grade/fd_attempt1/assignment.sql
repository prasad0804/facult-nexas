CREATE TABLE assignment(
  student_id VARCHAR(255),
  course_id VARCHAR(255),
  faculty_id VARCHAR(255),
  assignment_name VARCHAR(50),
  due_date DATE NOT NULL,
  instructions VARCHAR(255),
  PRIMARY KEY (student_id(100), course_id(100), faculty_id(100), assignment_name),
  FOREIGN KEY (student_id, course_id, faculty_id) REFERENCES student_course(student_id, course_id, faculty_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;