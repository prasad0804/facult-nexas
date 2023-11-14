CREATE TABLE final_grades (
    student_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    course_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    faculty_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    final_grade VARCHAR(10),
    PRIMARY KEY (student_id, course_id,faculty_id),
    FOREIGN KEY (student_id, course_id,faculty_id) REFERENCES student_course(student_id, course_id,faculty_id)
);
