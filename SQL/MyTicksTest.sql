DROP DATABASE IF EXISTS `MyTicksTest`;

CREATE DATABASE `MyTicksTest`;
USE `MyTicksTest`;

CREATE TABLE `cars` (
	`id` INT(4) NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(12) NOT NULL,
    `model` VARCHAR(20) NOT NULL,
    `doors` INT(1) NOT NULL,
    PRIMARY KEY (`id`)
);

SELECT * FROM `cars`
