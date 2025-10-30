-- schema.sql
CREATE DATABASE IF NOT EXISTS sciqus_intern;
USE sciqus_intern;

CREATE TABLE IF NOT EXISTS courses (
  course_id INT AUTO_INCREMENT PRIMARY KEY,
  course_name VARCHAR(255) NOT NULL,
  course_code VARCHAR(50) NOT NULL UNIQUE,
  course_duration INT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','student') NOT NULL DEFAULT 'student',
  course_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE SET NULL
);

-- sample admin
INSERT INTO users (name,email,password_hash,role) VALUES ('Admin','admin@example.com','$2b$12$examplehash','admin');
