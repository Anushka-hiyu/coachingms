CREATE DATABASE coachingms;
USE coachingms;
CREATE TABLE IF NOT EXISTS users(
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(100) NOT NULL,
`password` VARCHAR(100) NOT NULL);

INSERT INTO users(username, `password`) 
VALUES('anushka', 'tungtungsahur');

SHOW DATABASES;
USE coachingms;
SHOW TABLES;
SELECT * FROM users;

CREATE TABLE IF NOT EXISTS students(
id INT AUTO_INCREMENT PRIMARY KEY,
`name` VARCHAR(100),
email VARCHAR(100),
phone VARCHAR(15),
date_of_joining DATE,
batch_id INT,
fee_status ENUM('Paid', 'Unpaid') DEFAULT 'Unpaid'
);


CREATE TABLE IF NOT EXISTS teachers(
id INT AUTO_INCREMENT PRIMARY KEY,
`name` VARCHAR(100),
`subject` VARCHAR(100),
email VARCHAR(100),
availability VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS batches(
id INT AUTO_INCREMENT PRIMARY KEY,
`name` VARCHAR(100),
`subject` VARCHAR(100),
teacher_id INT,
days VARCHAR(100),
timing VARCHAR(100),
capacity INT,
FOREIGN KEY(teacher_id) REFERENCES teachers(id)
);


SHOW TABLES;
DESCRIBE students;
SELECT * FROM students;