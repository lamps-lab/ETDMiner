SHOW databases;
USE test_db;
SHOW TABLES;
CREATE TABLE IF NOT EXISTS`test_db.pdfs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(1000) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `advisor` varchar(2500) DEFAULT NULL,
  `year` varchar(10) DEFAULT NULL,
  `abstract` mediumtext,
  `university` varchar(255) DEFAULT NULL,
  `degree` varchar(255) DEFAULT NULL,
  `URI` varchar(2000) DEFAULT NULL,
  `department` varchar(400) DEFAULT NULL,
  `discipline` varchar(400) DEFAULT NULL,
  `language` varchar(64) DEFAULT 'eng',
  `schooltype` varchar(40) DEFAULT NULL,
  `borndigital` int DEFAULT '0',
  `oadsclassifier` varchar(50) DEFAULT NULL,
  `pri_identifier` varchar(100) DEFAULT NULL,
  `second_identifier` varchar(100) DEFAULT NULL,
  `license` varchar(2000) DEFAULT NULL,
  `copyright` varchar(2000) DEFAULT NULL,
  `haspdf` tinyint DEFAULT NULL,
  `timestamp_metadata` timestamp NULL DEFAULT NULL,
  `timestamp_pdf` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=639376 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
