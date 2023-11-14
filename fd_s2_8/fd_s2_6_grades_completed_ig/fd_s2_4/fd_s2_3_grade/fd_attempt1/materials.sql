CREATE TABLE materials(
  faculty_id VARCHAR(255),
  course_id VARCHAR(255),
  file_name VARCHAR(255),
  file_path VARCHAR(255),
  upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (faculty_id(100),course_id(100),file_name(100),file_path),
  FOREIGN KEY (faculty_id,course_id) REFERENCES faculty_course(faculty_id,course_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;