CREATE TABLE student_course (
  student_id VARCHAR(255),
  course_id VARCHAR(255),
  faculty_id VARCHAR(255),
  PRIMARY KEY (student_id, course_id,faculty_id),
  FOREIGN KEY (student_id) REFERENCES students (student_id),
  FOREIGN KEY (course_id) REFERENCES courses (course_id),
  FOREIGN KEY (faculty_id) REFERENCES faculty_details (faculty_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
