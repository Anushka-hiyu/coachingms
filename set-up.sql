CREATE DATABASE IF NOT EXISTS coachingms;
USE coachingms;
CREATE TABLE IF NOT EXISTS users(
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  password VARCHAR(100) NOT NULL
);

INSERT INTO users(username, user_password) 
VALUES('admin12', 'royaldev');

CREATE TABLE IF NOT EXISTS students(
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100),
  phone VARCHAR(15),
  date_of_joining DATE,
  batch_id INT,
  fee_status ENUM('Paid', 'Unpaid') DEFAULT 'Unpaid'
);

CREATE TABLE IF NOT EXISTS teachers(
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  subject VARCHAR(100),
  email VARCHAR(100),
  availability VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS batches(
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  subject VARCHAR(100),
  teacher_id INT,
  days VARCHAR(100),
  timing VARCHAR(100),
  capacity INT,
  FOREIGN KEY(teacher_id) REFERENCES teachers(id)
);


CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    message TEXT,
    seen BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

SELECT * FROM students;
SELECT * FROM teachers;
SELECT * FROM batches;

UPDATE notifications SET seen = TRUE WHERE id = 5 AND teacher_id = 2;
ALTER TABLE notifications ADD COLUMN title VARCHAR(255) AFTER teacher_id;
UPDATE notifications SET seen = TRUE WHERE teacher_id = 4;
SELECT * FROM notifications WHERE teacher_id = 4 AND seen = FALSE ORDER BY created_at DESC;

CREATE TABLE IF NOT EXISTS messages(
  id INT PRIMARY KEY AUTO_INCREMENT,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  message TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_teacher_sender BOOLEAN
);


SELECT * FROM teachers;
SELECT * FROM messages;



