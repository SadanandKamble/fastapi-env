
SELECT * FROM students;


SELECT * FROM students WHERE score > 80;

UPDATE students
SET score = 95, result = 'Pass'
WHERE id = 1;

SELECT * FROM students;

SELECT * FROM students WHERE result = 'Pass';

SELECT * FROM students WHERE result = 'Fail';

SELECT * FROM students WHERE score > 80;


SELECT * FROM students ORDER BY score DESC LIMIT 1;

SELECT AVG(score) AS average_score FROM students;

UPDATE students
SET score = 95, result = 'Pass'
WHERE id = 4;  -- e.g., David retook the exam


DELETE FROM students
WHERE id = 10; -- e.g., Jane
