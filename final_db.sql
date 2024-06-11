/*
SQLyog Community Edition- MySQL GUI v7.01 
MySQL - 5.0.27-community-nt : Database - register
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

CREATE DATABASE /*!32312 IF NOT EXISTS*/`register` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `register`;

/*Table structure for table `pred_bird` */

DROP TABLE IF EXISTS `pred_bird`;

CREATE TABLE `pred_bird` (
  `predId` int(255) NOT NULL auto_increment,
  `username` varchar(255) default NULL,
  `birdName` varchar(255) default NULL,
  `filePath` longtext,
  PRIMARY KEY  (`predId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `pred_bird` */

insert  into `pred_bird`(`predId`,`username`,`birdName`,`filePath`) values (1,'asd','Ashy Prinia - Prinia socialis','static/image_data/_79.png');

/*Table structure for table `user` */

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `userid` int(255) NOT NULL auto_increment,
  `name` varchar(255) default NULL,
  `email` varchar(50) default NULL,
  `password` varchar(50) default NULL,
  UNIQUE KEY `userid` (`userid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `user` */

insert  into `user`(`userid`,`name`,`email`,`password`) values (1,'asd','a@gmail.com','a');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
