-- ==============================================================
-- Diabetes Risk Classification System - Database Schema
-- Database Management System: MySQL 8.0+
-- Database Name: diabetes_db
-- ==============================================================

-- 1. Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS diabetes_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE diabetes_db;

-- 2. Create the Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Create the Prediction History table
CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pregnancies INT NOT NULL,
    glucose FLOAT NOT NULL,
    blood_pressure FLOAT NOT NULL,
    skin_thickness FLOAT NOT NULL,
    insulin FLOAT NOT NULL,
    bmi FLOAT NOT NULL,
    diabetes_pedigree_function FLOAT NOT NULL,
    age INT NOT NULL,
    predicted_outcome TINYINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prediction_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
