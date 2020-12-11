-- MyTicksClimbs
DROP DATABASE IF EXISTS `MyTicksClimbs`;

CREATE DATABASE `MyTicksClimbs`;
USE `MyTicksClimbs`;

-- areas
	-- Areas hold other areas and/or routes/climbs
    -- parent column is computed/triggered
CREATE TABLE `areas` (
	`id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(35) NOT NULL,
    `parent_id` INT NOT NULL,
    `parent_name` VARCHAR(35) NOT NULL,
    `path` VARCHAR(150),
    `description` VARCHAR(500),
    `directions` VARCHAR(500),
    `elevation` INT,
    `lat` DOUBLE(9,6),
    `lng` DOUBLE(9,6),
    `area_type` INT DEFAULT 0,
    `date_inserted` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT PK_Area PRIMARY KEY (id,name),
    FOREIGN KEY (parent_id,parent_name) REFERENCES areas(id,name)
);
-- Initialize with 'All Locations'
INSERT INTO areas (name, parent_id, parent_name, path, area_type)
	VALUES ('All Locations',1,'All Locations', '1/All Locations', 1),
		('North America', 1, 'All Locations', '1/All Locations', 1),
        ('Wyoming', 2, 'North America', '1/All Locations$2/North America', 2);


-- Boulder Grades Reference Table
CREATE TABLE `boulder_grades` (
	`int_id` INT NOT NULL,
    `sherman` VARCHAR(3) NOT NULL,
    `font` VARCHAR(3) NOT NULL,
    PRIMARY KEY (int_id)
);
INSERT INTO boulder_grades (int_id,sherman,font)
	VALUES 
		(-1, 'VB', '3'),(0, 'V0', '4'),(1, 'V1', '5'),(2, 'V2', '5+'),(3, 'V3', '6A'),(4, 'V4', '6B'),(5, 'V5', '6C'),(6, 'V6', '7A'),
        (7, 'V7', '7A+'),(8, 'V8', '7B'),(9, 'V9', '7C'),(10, 'V10', '7C+'),(11, 'V11', '8A'),(12, 'V12', '8A+'),(13, 'V13', '8B'),
        (14, 'V14', '8B+')
	;
    
-- Route Grades Reference Table
CREATE TABLE `route_grades` (
	`int_id` INT NOT NULL,
    `yos` VARCHAR(10) NOT NULL,
    `french` VARCHAR(3) NOT NULL,
    PRIMARY KEY (int_id)
);
INSERT INTO route_grades 
	VALUES
		(-1, 'Easy 5th', '1'),(0, '5.4', '2'),(1, '5.5', '3'),(2,'5.6','4'),(3,'5.7','4+'),(4,'5.8','5a'),(5,'5.9','5b'),(6,'5.10a','6a'),
        (7,'5.10b','6a+'),(8,'5.10c','6b'),(9,'5.10d','6b+'),(10,'5.11a','6c'),(11,'5.11b','6c+'),(12,'5.11c','7a'),(13,'5.11d','7a'),
        (14,'5.12a','7a+'),(15,'5.12b','7b'),(16,'5.12c','7b+'),(17,'5.12d','7c'),(18,'5.13a','7c+'),(19,'5.13b','8a'),(20,'5.13c','8a+'),
        (21,'5.13d','8b'),(22,'5.14a','8b+'),(23,'5.14b','8c')
        ;
    
-- Danger Reference Table
CREATE TABLE `danger` (
	`int_id` INT NOT NULL,
    `movie` VARCHAR(5),
    PRIMARY KEY (int_id)
);
INSERT INTO danger
	VALUES 
		(0, 'G'), (1, 'PG-13'), (2, 'R'), (3, 'X')
	;

-- Boulders
CREATE TABLE `boulders` (
	`id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(35) NOT NULL,
    `parent_id` INT NOT NULL,
    `parent_name` VARCHAR(35) NOT NULL,
    `path` VARCHAR(150),
    `position` INT NOT NULL DEFAULT 0,
    `grade` INT NOT NULL,
    `quality` INT NOT NULL,
    `danger` INT NOT NULL,
    `height` INT,
    `fa` VARCHAR(50),
    `description` VARCHAR(500),
    `pro` VARCHAR(100),
    `climb_type` VARCHAR(10) NOT NULL DEFAULT 'boulder',
    `date_inserted` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id,name),
    FOREIGN KEY (parent_id,parent_name) REFERENCES areas(id,name),
    FOREIGN KEY (danger) REFERENCES danger(int_id)
);

-- Routes
CREATE TABLE `routes` (
	`id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(35) NOT NULL,
    `parent_id` INT NOT NULL,
    `parent_name` VARCHAR(35) NOT NULL,
    `path` VARCHAR(150),
    `position` INT NOT NULL DEFAULT 0,
    `grade` INT NOT NULL,
    `quality` INT NOT NULL,
    `danger` INT NOT NULL,
    `height` INT,
    `pitches` INT,
    `committment` VARCHAR(3),
    `fa` VARCHAR(50),
    `description` VARCHAR(500),
    `pro` VARCHAR(100),
    `climb_type` VARCHAR(10) NOT NULL DEFAULT 'route',
    `route_type` INT NOT NULL,
    `date_inserted` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id,name),
    FOREIGN KEY (parent_id,parent_name) REFERENCES areas(id,name),
    FOREIGN KEY (danger) REFERENCES danger(int_id)
);

CREATE TABLE `tags` (
	`id` INT NOT NULL AUTO_INCREMENT,
    `title` VARCHAR(20) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE `tagClimb` (
	`climb_id` INT NOT NULL,
    `tag_id` INT NOT NULL,
    FOREIGN KEY (climb_id) REFERENCES 
);


SELECT * FROM areas;