DROP DATABASE IF EXISTS `MyTicksTest`;

CREATE DATABASE `MyTicksTest`;
USE `MyTicksTest`;

CREATE TABLE `areas` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(65) NOT NULL,
	`parent_id` INT NOT NULL,
	`parent_name` VARCHAR(65) NOT NULL,
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

INSERT INTO areas(name,parent_id,parent_name,path,description,directions,elevation,lat,lng,area_type)
	VALUES
		('All Locations', 1, 'All Locations', '1/All Locations', 'This is the root area', 'Just find yourself', 0, 129.23245, -86.545398, 1),
        ('North America', 1, 'All Locations', '1/All Locations', 'This is NA', 'N of SA', 4500, 126.5543, -83.425423, 1),
        ('Asia', 1, 'All Locations', '1/All Locations', 'This is Asia', 'Most of Eurasia', 4500, 126.5543, -83.425423, 1),
        ('Europe', 1, 'All Locations', '1/All Locations', 'This is Europe', 'Left Eurasia', 4500, 126.5543, -83.425423, 1),
        ('Wyoming', 2, 'North America', '1/All Locations$2/North America', 'This is Wyoming', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('California', 2, 'North America', '1/All Locations$2/North America', 'This is California', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('Oregon', 2, 'North America', '1/All Locations$2/North America', 'This is Oregon', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('Washington', 2, 'North America', '1/All Locations$2/North America', 'This is Washington', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('Nevada', 2, 'North America', '1/All Locations$2/North America', 'This is Nevada', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('Utah', 2, 'North America', '1/All Locations$2/North America', 'This is Utah', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('Colorado', 2, 'North America', '1/All Locations$2/North America', 'This is Colorado', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1),
        ('Test Area', 2, 'North America', '1/All Locations$2/North America', 'This is A TEST', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 2),
        ('Thailand', 3, 'Asia', '1/All Locations$3/Asia', 'This is Thailand', 'Somewhere inside Asia', 6500, 120.425245, -45.52435, 1),
        ('Canada', 2, 'North America', '1/All Locations$2/North America', 'This is Canada', 'Somewhere inside NA', 6500, 120.425245, -45.52435, 1)
	;

CREATE TABLE danger (
  `id` INT NOT NULL,
  `movie` VARCHAR(5) NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO danger
	VALUES 
		(0,'G'),(1,'PG-13'),(2,'R'),(3,'X')
	;

CREATE TABLE route_types (
	`id` INT NOT NULL,
    `route_type` VARCHAR(10) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO route_types
	VALUES
		(0, 'boulder'), (1, 'sport'), (2, 'trad'), (3, 'dws'), (4, 'aid')
	;

CREATE TABLE `climbs` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(65) NOT NULL,
	`parent_id` INT NOT NULL,
	`parent_name` VARCHAR(65) NOT NULL,
	`climb_type` VARCHAR(10) NOT NULL,
	`position` INT NOT NULL DEFAULT 0,
	`quality` INT NOT NULL,
	`danger` INT NOT NULL,
	`height` INT,
	`fa` VARCHAR(50),
	`description` VARCHAR(1500),
	`pro` VARCHAR(100),
	`date_inserted` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (parent_id, parent_name) REFERENCES areas(id, name),
    FOREIGN KEY (danger) REFERENCES danger(id)
);


INSERT INTO climbs(name,parent_id,parent_name,climb_type,position,quality,danger,height,fa,description,pro)
	VALUES
		('Boulder One', 12, 'Test Area', 'boulder', 1, 3, 0, 12, 'Some rando', 'Its aight', 'Towel'),
        ('Boulder Two', 12, 'Test Area', 'boulder', 0, 1, 2, 32, Null, Null, 'pads'),
        ('Route One', 12, 'Test Area', 'route', 0, 4, 0, 89, 'Josh Lowy', 'The best', '3 Draws'),
        ('Route Two', 12, 'Test Area', 'route', 2, 3, 2, 120, 'Unknown', Null, Null)
	;


CREATE TABLE tags (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(20) NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO tags(title)
	VALUES
		('dirty'),
        ('reachy'),
        ('technical'),
        ('highball'),
        ('chossy'),
        ('bad landing'),
        ('warmup'),
        ('pinchy'),
        ('crimpy'),
        ('compstyle'),
        ('sandbagged'),
        ('huecos'),
        ('pockety'),
        ('dyno'),
        ('eliminate'),
        ('manufactured')
	;

CREATE TABLE tagClimb (
  `climb_id` INT NOT NULL,
  `tag_id` INT NOT NULL,
  FOREIGN KEY (climb_id) REFERENCES climbs(id),
  FOREIGN KEY (tag_id) REFERENCES tags(id)
);

INSERT INTO tagClimb
	VALUES
		(1,1),(1,5),(3,3)
	;

CREATE TABLE boulders (
  `id` INT NOT NULL,
  `grade` DECIMAL(10,3) NOT NULL,
  FOREIGN KEY (id) REFERENCES climbs(id)
);

INSERT INTO boulders
	VALUES
		(1, 8.6),
        (2, 10.2)
	;

CREATE TABLE routes (
  `id` INT NOT NULL,
  `route_type` INT NOT NULL,
  `grade` DECIMAL(10,3) NOT NULL,
  `aid_grade` VARCHAR(2),
  `pitches` INT NOT NULL,
  `committment` INT,
  FOREIGN KEY (id) REFERENCES climbs(id),
  FOREIGN KEY (route_type) REFERENCES route_types(id)
);

INSERT INTO routes
	VALUES
		(3, 2, 18.7,Null, 4, Null),
        (4, 3, 6.33,Null, 6, 1)
	;

CREATE TABLE boulder_grades (
  `lowVal` DECIMAL(4,2) NOT NULL,
  `highVal` DECIMAL(4,2) NOT NULL,
  `usa` VARCHAR(10) NOT NULL,
  `euro` VARCHAR(10) NOT NULL
);

INSERT INTO boulder_grades
	VALUES
		(-1, -0.66, 'VB', '3'),
		(-0.66, -0.34, 'V0-', '3+'),
		(-0.34, 0.34, 'V0', '4'),
		(0.34, 0.66, 'V0+', '4+'),
		(0.66, 1.34, 'V1', '5'),
		(1.34, 1.66, 'V1-2', '5+'),
		(1.66, 2.34, 'V2', '5+'),
		(2.34, 2.66, 'V2-3', '6A'),
		(2.66, 3.34, 'V3', '6A'),
		(3.34, 3.66, 'V3-4', '6A+'),
		(3.66, 4.34, 'V4', '6B'),
		(4.34, 4.66, 'V4-5', '6B+'),
		(4.66, 5.34, 'V5', '6C'),
		(5.34, 5.66, 'V5-6', '6C+'),
		(5.66, 6.34, 'V6', '7A'),
		(6.34, 6.66, 'V6-7', '7A/+'),
		(6.66, 7.34, 'V7', '7A+'),
		(7.34, 7.66, 'V7-8', '7A+/B'),
		(7.66, 8.34, 'V8', '7B'),
		(8.34, 8.66, 'V8-9', '7B+/C'),
		(8.66, 9.34, 'V9', '7C'),
		(9.34, 9.66, 'V9-10', '7C/+'),
		(9.66, 10.34, 'V10', '7C+'),
		(10.34, 10.66, 'V10-11', '7C+/8A'),
		(10.66, 11.34, 'V11', '8A'),
		(11.34, 11.66, 'V11-12', '8A/+'),
		(11.66, 12.34, 'V12', '8A+'),
		(12.34, 12.66, 'V12-13', '8A+/B'),
		(12.66, 13.34, 'V13', '8B'),
		(13.34, 13.66, 'V13-14', '8B/+'),
		(13.66, 14.34, 'V14', '8B+'),
        (14.34, 14.66, 'V14-15', '8C'),
        (14.66, 15.34, 'V15', '8C')
    ;

CREATE TABLE route_grades (
  `lowVal` DECIMAL(4,2) NOT NULL,
  `highVal` DECIMAL(4,2) NOT NULL,
  `usa` VARCHAR(10) NOT NULL,
  `euro` VARCHAR(10) NOT NULL
);

INSERT INTO route_grades
	VALUES
		(-1, -0.66, 'Easy 5th', '1'),
		(-0.66, -0.34, '5.4', '1'),
		(-0.34, 0.34, '5.4', '2'),
		(0.34, 1.34, '5.5', '3'),
		(1.34, 2.34, '5.6', '4'),
		(2.34, 3.34, '5.7', '4+'),
		(3.34, 4.34, '5.8', '5a'),
		(4.34, 5.34, '5.9', '5b'),
		(5.34, 5.66, '5.9+', '5b/+'),
		(5.66, 6.34, '5.10a', '6a'),
		(6.34, 6.66, '5.10b', '6a/+'),
		(6.66, 7.34, '5.10b', '6a+'),
		(7.34, 7.66, '5.10c', '6a+/b'),
		(7.66, 8.34, '5.10c', '6b'),
		(8.34, 8.66, '5.10d', '6b/+'),
		(8.66, 9.34, '5.10d', '6b+'),
		(9.34, 9.66, '5.11a', '6b+/c'),
		(9.66, 10.34, '5.11a', '6c'),
		(10.34, 10.66, '5.11b', '6c/+'),
		(10.66, 11.34, '5.11b', '6c+'),
		(11.34, 11.66, '5.11c', '6c+'),
		(11.66, 12.34, '5.11c', '6c+/7a'),
		(12.34, 13.34, '5.11d', '7a'),
		(13.34, 13.66, '5.12a', '7a/+'),
		(13.66, 14.34, '5.12a', '7a+'),
        (14.34, 14.66, '5.12b', '7a+/b'),
		(14.66, 15.34, '5.12b', '7b'),
		(15.34, 15.66, '5.12c', '7b/+'),
		(15.66, 16.34, '5.12c', '7b+'),
		(16.34, 16.66, '5.12d', '7b+/c'),
		(16.66, 17.34, '5.12d', '7c'),
		(17.34, 17.66, '5.13a', '7c/+'),
		(17.66, 18.34, '5.13a', '7c+'),
		(18.34, 18.66, '5.13b', '7c+/8a'),
		(18.66, 19.34, '5.13b', '8a'),
		(19.34, 19.66, '5.13c', '8a/+'),
		(19.66, 20.34, '5.13c', '8a+'),
		(20.34, 20.66, '5.13d', '8a+/b'),
		(20.66, 21.34, '5.13d', '8b'),
        (21.34, 21.66, '5.14a', '8b/+'),
        (21.66, 22.34, '5.14a', '8b+'),
        (22.34, 22.66, '5.14b', '8b+/c'),
        (22.66, 23.34, '5.14b', '8c'),
        (23.34, 23.66, '5.14c', '8c/+'),
        (23.66, 24.34, '5.14c', '8c+'),
		(24.34, 24.66, '5.14d', '8c+/9a'),
		(24.66, 25.34, '5.14d', '9a'),
        (25.34, 25.66, '5.15a', '9a/+'),
        (25.66, 26.34, '5.15a', '9a+'),
        (26.34, 99, 'Aid', 'Aid')
    ;


SELECT c.id,c.name,c.climb_type,c.position,c.quality,d.movie AS 'danger',c.height,c.fa,c.description,c.pro,COALESCE(bg.usa,rg.usa) AS 'grade',rt.route_type,r.pitches, t.title
	FROM climbs as c
	LEFT JOIN boulders as b ON b.id=c.id
    LEFT JOIN routes as r ON r.id=c.id
    JOIN danger as d ON d.id=c.danger
    LEFT JOIN boulder_grades as bg ON b.grade BETWEEN bg.lowVal AND bg.highVal
	LEFT JOIN route_grades as rg ON r.grade BETWEEN rg.lowVal AND rg.highVal
    LEFT JOIN tagClimb as tc ON tc.climb_id=c.id
    LEFT JOIN tags as t ON t.id = tc.tag_id
    LEFT JOIN route_types as rt ON rt.id = r.route_type
	WHERE c.parent_id = 3 AND c.parent_name = 'Wyoming'
    ORDER BY c.position
;

SELECT t.title
	FROM tags AS t
    JOIN tagClimb as tc ON tc.tag_id=t.id
    JOIN climbs as c ON c.id=tc.climb_id
    WHERE c.id = 13
;

SELECT c.climb_type, r.route_type
	FROM climbs AS c
    LEFT JOIN routes as r ON r.id = c.id
    WHERE c.parent_id = 3 AND c.parent_name = 'Wyoming'
;

SELECT * 
	FROM areas as a
    WHERE a.name LIKE '%wy%'
;

SELECT * FROM areas;

SELECT c.name, a.name
	FROM climbs as c
	JOIN areas as a ON a.id = c.parent_id
    WHERE c.name = 'Boulder One' AND a.name = 'Wyoming'
;