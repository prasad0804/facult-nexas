CREATE TABLE faculty_details (
  faculty_id VARCHAR(255) NOT NULL ,
  faculty_name VARCHAR(255) NOT NULL,
  faculty_email VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  PRIMARY KEY (faculty_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;