-- MySQL dump 10.13  Distrib 5.7.23, for Linux (x86_64)
--
-- Host: localhost    Database: wsit_event_db
-- ------------------------------------------------------
-- Server version	5.7.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `activity_history`
--

DROP TABLE IF EXISTS `activity_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `activity_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `activity_type` enum('update','delete','register','message','offline','check-in') COLLATE utf8_unicode_ci NOT NULL,
  `category` enum('event','session','question','travel','room','message','profile','push_notification','group','tag','package','checkpoint','photo','registration_group','rebate','order','order_item','credit_order','credit_usage','payment') COLLATE utf8_unicode_ci NOT NULL,
  `old_value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `new_value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `activity_message` longtext COLLATE utf8_unicode_ci,
  `admin_id` int(11) DEFAULT NULL,
  `attendee_id` int(11) NOT NULL,
  `checkpoint_id` int(11) DEFAULT NULL,
  `event_id` int(11) NOT NULL,
  `message_id` int(11) DEFAULT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `question_id` int(11) DEFAULT NULL,
  `registration_group_id` int(11) DEFAULT NULL,
  `room_id` int(11) DEFAULT NULL,
  `session_id` int(11) DEFAULT NULL,
  `travel_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `activity_history_156f41ed` (`admin_id`),
  KEY `activity_history_c50970ee` (`attendee_id`),
  KEY `activity_history_bef2d98a` (`checkpoint_id`),
  KEY `activity_history_4437cfac` (`event_id`),
  KEY `activity_history_4ccaa172` (`message_id`),
  KEY `activity_history_b4e75e23` (`photo_id`),
  KEY `activity_history_7aa0f6ee` (`question_id`),
  KEY `activity_history_b107eae0` (`registration_group_id`),
  KEY `activity_history_8273f993` (`room_id`),
  KEY `activity_history_7fc8ef54` (`session_id`),
  KEY `activity_history_46413c35` (`travel_id`),
  CONSTRAINT `D50c39852bb630a0ae7217e16abe3cc9` FOREIGN KEY (`registration_group_id`) REFERENCES `registration_groups` (`id`),
  CONSTRAINT `activity_histo_message_id_36a2d0aa0050561f_fk_message_history_id` FOREIGN KEY (`message_id`) REFERENCES `message_history` (`id`),
  CONSTRAINT `activity_history_admin_id_748582719b4b3d3d_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `activity_history_attendee_id_119be15223c0811_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `activity_history_checkpoint_id_36e24b3e5c3f7cd_fk_checkpoints_id` FOREIGN KEY (`checkpoint_id`) REFERENCES `checkpoints` (`id`),
  CONSTRAINT `activity_history_event_id_79920ca356876fae_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `activity_history_photo_id_4036d9dc93d84cf4_fk_photos_id` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`id`),
  CONSTRAINT `activity_history_question_id_4e93d0dbd9c922d2_fk_questions_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`),
  CONSTRAINT `activity_history_room_id_24132ddf3face727_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`),
  CONSTRAINT `activity_history_session_id_1900e774ec252592_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`),
  CONSTRAINT `activity_history_travel_id_1db355091b10f790_fk_travels_id` FOREIGN KEY (`travel_id`) REFERENCES `travels` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `activity_history`
--

LOCK TABLES `activity_history` WRITE;
/*!40000 ALTER TABLE `activity_history` DISABLE KEYS */;
INSERT INTO `activity_history` VALUES (1,'update','session','Not Answered','Attending','2018-11-30 10:30:23.327910',NULL,NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL,1,NULL),(2,'register','order','','','2018-11-30 10:30:23.745271','New order created with order id: 1 and order number: 1001',NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(3,'register','order_item','','','2018-11-30 10:30:23.846591','New order item Dinner added to order number: 1001',NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(4,'update','session','Not Answered','Attending','2018-11-30 10:30:57.497955',NULL,NULL,2,NULL,1,NULL,NULL,NULL,NULL,NULL,1,NULL),(5,'register','order','','','2018-11-30 10:30:57.856847','New order created with order id: 2 and order number: 1001',NULL,2,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(6,'register','order_item','','','2018-11-30 10:30:58.097823','New order item Dinner added to order number: 1001',NULL,2,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(7,'update','session','Attending','Not Attending','2018-11-30 10:30:58.384456',NULL,NULL,2,NULL,1,NULL,NULL,NULL,NULL,NULL,1,NULL),(8,'delete','order_item','','','2018-11-30 10:30:58.457974','Order Item Dinner is removed from order: 1001',NULL,2,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(9,'update','session','Not Answered','Attending','2018-11-30 10:31:44.678955',NULL,NULL,3,NULL,1,NULL,NULL,NULL,NULL,NULL,1,NULL),(10,'register','order','','','2018-11-30 10:31:44.806337','New order created with order id: 3 and order number: 1001',NULL,3,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(11,'register','order_item','','','2018-11-30 10:31:45.036998','New order item Dinner added to order number: 1001',NULL,3,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(12,'update','session','Attending','Not Attending','2018-11-30 10:31:45.499050',NULL,NULL,3,NULL,1,NULL,NULL,NULL,NULL,NULL,1,NULL),(13,'delete','order_item','','','2018-11-30 10:31:45.574167','Order Item Dinner is removed from order: 1001',NULL,3,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(14,'update','profile','','','2018-11-30 10:31:52.150440',NULL,NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(15,'update','profile','','','2018-11-30 10:31:52.311266',NULL,NULL,2,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(16,'update','profile','','','2018-11-30 10:31:52.403777',NULL,NULL,3,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(17,'message','message','','','2018-11-30 10:31:53.025791',NULL,1,1,NULL,1,1,NULL,NULL,NULL,NULL,NULL,NULL),(18,'update','registration_group','','as Order owner','2018-11-30 10:31:53.028643',NULL,NULL,1,NULL,1,NULL,NULL,NULL,1,NULL,NULL,NULL),(19,'update','registration_group','','as Attendee','2018-11-30 10:31:53.028697',NULL,NULL,2,NULL,1,NULL,NULL,NULL,1,NULL,NULL,NULL),(20,'update','registration_group','','as Attendee','2018-11-30 10:31:53.028734',NULL,NULL,3,NULL,1,NULL,NULL,NULL,1,NULL,NULL,NULL),(21,'update','profile','','','2018-11-30 10:39:48.662978',NULL,NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(22,'register','room','','','2018-11-30 10:39:48.674711',NULL,NULL,1,NULL,1,NULL,NULL,NULL,NULL,1,NULL,NULL),(23,'register','order_item','','','2018-11-30 10:39:48.814190','New order item Regency Hotel Double added to order number: 1001',NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(24,'update','photo','','','2018-11-30 10:41:08.507489',NULL,NULL,1,NULL,1,NULL,1,NULL,NULL,NULL,NULL,NULL),(25,'update','photo','','','2018-11-30 10:42:01.124933',NULL,NULL,1,NULL,1,NULL,2,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `activity_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `answers`
--

DROP TABLE IF EXISTS `answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `answers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `question_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `answers_7aa0f6ee` (`question_id`),
  KEY `answers_e8701ad4` (`user_id`),
  CONSTRAINT `answers_question_id_29262ce0deada2d9_fk_questions_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`),
  CONSTRAINT `answers_user_id_faae77289febd06_fk_attendees_id` FOREIGN KEY (`user_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `answers`
--

LOCK TABLES `answers` WRITE;
/*!40000 ALTER TABLE `answers` DISABLE KEYS */;
INSERT INTO `answers` VALUES (1,'Mahedi',1,1),(2,'Hasan',2,1),(3,'mahedi@workspaceit.com',3,1),(4,'01324566554554',4,1),(5,'test bio',5,1),(6,'BD',6,1),(7,'Zahed',1,2),(8,'Alam',2,2),(9,'zahed@workspaceit.com',3,2),(10,'02151154511',4,2),(11,'new bio',5,2),(12,'AU',6,2),(13,'Samiul',1,3),(14,'Alim',2,3),(15,'samiul@workspaceit.com',3,3),(16,'0146515155',4,3),(17,'my bio',5,3),(18,'AT',6,3);
/*!40000 ALTER TABLE `answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendee_groups`
--

DROP TABLE IF EXISTS `attendee_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendee_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attendee_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attendee_groups_attendee_id_68b0f0852e612e79_fk_attendees_id` (`attendee_id`),
  KEY `attendee_groups_0e939a4f` (`group_id`),
  CONSTRAINT `attendee_groups_attendee_id_68b0f0852e612e79_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `attendee_groups_group_id_2241d14a253b4f72_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendee_groups`
--

LOCK TABLES `attendee_groups` WRITE;
/*!40000 ALTER TABLE `attendee_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendee_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendee_password_reset_requests`
--

DROP TABLE IF EXISTS `attendee_password_reset_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendee_password_reset_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hash_code` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `expired_at` datetime(6) NOT NULL,
  `already_used` tinyint(1) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attendee_password_r_attendee_id_1cb4ec1a66e926f9_fk_attendees_id` (`attendee_id`),
  CONSTRAINT `attendee_password_r_attendee_id_1cb4ec1a66e926f9_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendee_password_reset_requests`
--

LOCK TABLES `attendee_password_reset_requests` WRITE;
/*!40000 ALTER TABLE `attendee_password_reset_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendee_password_reset_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendee_submit_button`
--

DROP TABLE IF EXISTS `attendee_submit_button`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendee_submit_button` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hit_count` int(11) NOT NULL,
  `attendee_id` int(11) DEFAULT NULL,
  `button_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attendee_submit_but_attendee_id_11722fff340a068e_fk_attendees_id` (`attendee_id`),
  KEY `attendee_submit_button_2e479f87` (`button_id`),
  CONSTRAINT `attendee_s_button_id_7b331dc79f1ba997_fk_plugin_submit_button_id` FOREIGN KEY (`button_id`) REFERENCES `plugin_submit_button` (`id`),
  CONSTRAINT `attendee_submit_but_attendee_id_11722fff340a068e_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendee_submit_button`
--

LOCK TABLES `attendee_submit_button` WRITE;
/*!40000 ALTER TABLE `attendee_submit_button` DISABLE KEYS */;
INSERT INTO `attendee_submit_button` VALUES (1,1,1,3),(2,1,1,2);
/*!40000 ALTER TABLE `attendee_submit_button` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendee_tags`
--

DROP TABLE IF EXISTS `attendee_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendee_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attendee_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attendee_tags_attendee_id_5a3bb400b1140856_fk_attendees_id` (`attendee_id`),
  KEY `attendee_tags_76f094bc` (`tag_id`),
  CONSTRAINT `attendee_tags_attendee_id_5a3bb400b1140856_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `attendee_tags_tag_id_1513a67b9c6f134d_fk_tags_id` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendee_tags`
--

LOCK TABLES `attendee_tags` WRITE;
/*!40000 ALTER TABLE `attendee_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendee_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendees`
--

DROP TABLE IF EXISTS `attendees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `lastname` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `company` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `phonenumber` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `type` enum('user','guest') COLLATE utf8_unicode_ci NOT NULL,
  `tag` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `checksum` longtext COLLATE utf8_unicode_ci,
  `checksum_flag` tinyint(1) NOT NULL,
  `status` enum('canceled','registered','pending') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `avatar` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `secret_key` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bid` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `push_notification_status` tinyint(1) NOT NULL,
  `event_id` int(11) NOT NULL,
  `language_id` int(11) NOT NULL,
  `registration_group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `secret_key` (`secret_key`),
  UNIQUE KEY `bid` (`bid`),
  KEY `attendees_4437cfac` (`event_id`),
  KEY `attendees_468679bd` (`language_id`),
  KEY `attendees_b107eae0` (`registration_group_id`),
  CONSTRAINT `D6bdcd326535eebe9395aa863d2455bf` FOREIGN KEY (`registration_group_id`) REFERENCES `registration_groups` (`id`),
  CONSTRAINT `attendees_event_id_1db1ccccc7eceb1a_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `attendees_language_id_4327fbac7f3d2124_fk_presets_id` FOREIGN KEY (`language_id`) REFERENCES `presets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendees`
--

LOCK TABLES `attendees` WRITE;
/*!40000 ALTER TABLE `attendees` DISABLE KEYS */;
INSERT INTO `attendees` VALUES (1,'Mahedi','Hasan','','mahedi@workspaceit.com','pbkdf2_sha256$20000$xcTk1AkllrIK$CoBpmhsNUAvPX3H/khT7OTI/hK/oGD0dAbqoyQ0jSIg=','01324566554554','user','',NULL,0,'registered','2018-11-30 10:29:18.486229','2018-11-30 10:39:48.662096','','wN1lrlUurUX3in8x','VG6N0AtGVNXNvh6F',1,1,6,NULL),(2,'Zahed','Alam','','zahed@workspaceit.com','pbkdf2_sha256$20000$RVRLhHelvoeE$DyE+QQWSyYlNIZACRMJEvNsyztBVOGv/5Vc5FmkelBI=','02151154511','user','',NULL,0,'registered','2018-11-30 10:29:18.486924','2018-11-30 10:31:52.624546','','gvtrCnUPC1LiKXcL','zU1EZtwXyd7gnHV0',1,1,6,1),(3,'Samiul','Alim','','samiul@workspaceit.com','pbkdf2_sha256$20000$yieGNnsWhpEv$2CsrGr+aSsNctatJYeweMoeMuTuB+DjQdn8IKx7Fl4Q=','0146515155','user','',NULL,0,'registered','2018-11-30 10:29:34.546118','2018-11-30 10:31:52.652389','','ir2vVmAxoAoSnXJh','kmeqE8enNcR3SDiz',1,1,6,1);
/*!40000 ALTER TABLE `attendees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group__permission_id_6e81fdfb82ce13ec_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_group__permission_id_6e81fdfb82ce13ec_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permission_group_id_1cb6930b2345f82a_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  CONSTRAINT `auth__content_type_id_28f54e2107663547_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=310 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can add permission',2,'add_permission'),(5,'Can change permission',2,'change_permission'),(6,'Can delete permission',2,'delete_permission'),(7,'Can add group',3,'add_group'),(8,'Can change group',3,'change_group'),(9,'Can delete group',3,'delete_group'),(10,'Can add user',4,'add_user'),(11,'Can change user',4,'change_user'),(12,'Can delete user',4,'delete_user'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add users',7,'add_users'),(20,'Can change users',7,'change_users'),(21,'Can delete users',7,'delete_users'),(22,'Can add events',8,'add_events'),(23,'Can change events',8,'change_events'),(24,'Can delete events',8,'delete_events'),(25,'Can add group',9,'add_group'),(26,'Can change group',9,'change_group'),(27,'Can delete group',9,'delete_group'),(28,'Can add locations',10,'add_locations'),(29,'Can change locations',10,'change_locations'),(30,'Can delete locations',10,'delete_locations'),(31,'Can add seminars',11,'add_seminars'),(32,'Can change seminars',11,'change_seminars'),(33,'Can delete seminars',11,'delete_seminars'),(34,'Can add presets',12,'add_presets'),(35,'Can change presets',12,'change_presets'),(36,'Can delete presets',12,'delete_presets'),(37,'Can add registration groups',13,'add_registrationgroups'),(38,'Can change registration groups',13,'change_registrationgroups'),(39,'Can delete registration groups',13,'delete_registrationgroups'),(40,'Can add attendee',14,'add_attendee'),(41,'Can change attendee',14,'change_attendee'),(42,'Can delete attendee',14,'delete_attendee'),(43,'Can add registration group owner',15,'add_registrationgroupowner'),(44,'Can change registration group owner',15,'change_registrationgroupowner'),(45,'Can delete registration group owner',15,'delete_registrationgroupowner'),(46,'Can add event admin',16,'add_eventadmin'),(47,'Can change event admin',16,'change_eventadmin'),(48,'Can delete event admin',16,'delete_eventadmin'),(49,'Can add questions',17,'add_questions'),(50,'Can change questions',17,'change_questions'),(51,'Can delete questions',17,'delete_questions'),(52,'Can add answers',18,'add_answers'),(53,'Can change answers',18,'change_answers'),(54,'Can delete answers',18,'delete_answers'),(55,'Can add tag',19,'add_tag'),(56,'Can change tag',19,'change_tag'),(57,'Can delete tag',19,'delete_tag'),(58,'Can add export state',20,'add_exportstate'),(59,'Can change export state',20,'change_exportstate'),(60,'Can delete export state',20,'delete_exportstate'),(61,'Can add attendee tag',21,'add_attendeetag'),(62,'Can change attendee tag',21,'change_attendeetag'),(63,'Can delete attendee tag',21,'delete_attendeetag'),(64,'Can add hotel',22,'add_hotel'),(65,'Can change hotel',22,'change_hotel'),(66,'Can delete hotel',22,'delete_hotel'),(67,'Can add room',23,'add_room'),(68,'Can change room',23,'change_room'),(69,'Can delete room',23,'delete_room'),(70,'Can add room allotment',24,'add_roomallotment'),(71,'Can change room allotment',24,'change_roomallotment'),(72,'Can delete room allotment',24,'delete_roomallotment'),(73,'Can add session',25,'add_session'),(74,'Can change session',25,'change_session'),(75,'Can delete session',25,'delete_session'),(76,'Can add seminar speakers',26,'add_seminarspeakers'),(77,'Can change seminar speakers',26,'change_seminarspeakers'),(78,'Can delete seminar speakers',26,'delete_seminarspeakers'),(79,'Can add travel',27,'add_travel'),(80,'Can change travel',27,'change_travel'),(81,'Can delete travel',27,'delete_travel'),(82,'Can add travel bound relation',28,'add_travelboundrelation'),(83,'Can change travel bound relation',28,'change_travelboundrelation'),(84,'Can delete travel bound relation',28,'delete_travelboundrelation'),(85,'Can add seminars users',29,'add_seminarsusers'),(86,'Can change seminars users',29,'change_seminarsusers'),(87,'Can delete seminars users',29,'delete_seminarsusers'),(88,'Can add travel attendee',30,'add_travelattendee'),(89,'Can change travel attendee',30,'change_travelattendee'),(90,'Can delete travel attendee',30,'delete_travelattendee'),(91,'Can add booking',31,'add_booking'),(92,'Can change booking',31,'change_booking'),(93,'Can delete booking',31,'delete_booking'),(94,'Can add requested buddy',32,'add_requestedbuddy'),(95,'Can change requested buddy',32,'change_requestedbuddy'),(96,'Can delete requested buddy',32,'delete_requestedbuddy'),(97,'Can add match',33,'add_match'),(98,'Can change match',33,'change_match'),(99,'Can delete match',33,'delete_match'),(100,'Can add match line',34,'add_matchline'),(101,'Can change match line',34,'change_matchline'),(102,'Can delete match line',34,'delete_matchline'),(103,'Can add rule set',35,'add_ruleset'),(104,'Can change rule set',35,'change_ruleset'),(105,'Can delete rule set',35,'delete_ruleset'),(106,'Can add used rule',36,'add_usedrule'),(107,'Can change used rule',36,'change_usedrule'),(108,'Can delete used rule',36,'delete_usedrule'),(109,'Can add option',37,'add_option'),(110,'Can change option',37,'change_option'),(111,'Can delete option',37,'delete_option'),(112,'Can add message contents',38,'add_messagecontents'),(113,'Can change message contents',38,'change_messagecontents'),(114,'Can delete message contents',38,'delete_messagecontents'),(115,'Can add message language contents',39,'add_messagelanguagecontents'),(116,'Can change message language contents',39,'change_messagelanguagecontents'),(117,'Can delete message language contents',39,'delete_messagelanguagecontents'),(118,'Can add notification',40,'add_notification'),(119,'Can change notification',40,'change_notification'),(120,'Can delete notification',40,'delete_notification'),(121,'Can add setting',41,'add_setting'),(122,'Can change setting',41,'change_setting'),(123,'Can delete setting',41,'delete_setting'),(124,'Can add general tag',42,'add_generaltag'),(125,'Can change general tag',42,'change_generaltag'),(126,'Can delete general tag',42,'delete_generaltag'),(127,'Can add session tags',43,'add_sessiontags'),(128,'Can change session tags',43,'change_sessiontags'),(129,'Can delete session tags',43,'delete_sessiontags'),(130,'Can add travel tag',44,'add_traveltag'),(131,'Can change travel tag',44,'change_traveltag'),(132,'Can delete travel tag',44,'delete_traveltag'),(133,'Can add checkpoint',45,'add_checkpoint'),(134,'Can change checkpoint',45,'change_checkpoint'),(135,'Can delete checkpoint',45,'delete_checkpoint'),(136,'Can add scan',46,'add_scan'),(137,'Can change scan',46,'change_scan'),(138,'Can delete scan',46,'delete_scan'),(139,'Can add session rating',47,'add_sessionrating'),(140,'Can change session rating',47,'change_sessionrating'),(141,'Can delete session rating',47,'delete_sessionrating'),(142,'Can add export rule',48,'add_exportrule'),(143,'Can change export rule',48,'change_exportrule'),(144,'Can delete export rule',48,'delete_exportrule'),(145,'Can add message history',49,'add_messagehistory'),(146,'Can change message history',49,'change_messagehistory'),(147,'Can delete message history',49,'delete_messagehistory'),(148,'Can add email templates',50,'add_emailtemplates'),(149,'Can change email templates',50,'change_emailtemplates'),(150,'Can delete email templates',50,'delete_emailtemplates'),(151,'Can add page content',51,'add_pagecontent'),(152,'Can change page content',51,'change_pagecontent'),(153,'Can delete page content',51,'delete_pagecontent'),(154,'Can add page image',52,'add_pageimage'),(155,'Can change page image',52,'change_pageimage'),(156,'Can delete page image',52,'delete_pageimage'),(157,'Can add menu item',53,'add_menuitem'),(158,'Can change menu item',53,'change_menuitem'),(159,'Can delete menu item',53,'delete_menuitem'),(160,'Can add menu permission',54,'add_menupermission'),(161,'Can change menu permission',54,'change_menupermission'),(162,'Can delete menu permission',54,'delete_menupermission'),(163,'Can add page permission',55,'add_pagepermission'),(164,'Can change page permission',55,'change_pagepermission'),(165,'Can delete page permission',55,'delete_pagepermission'),(166,'Can add photo group',56,'add_photogroup'),(167,'Can change photo group',56,'change_photogroup'),(168,'Can delete photo group',56,'delete_photogroup'),(169,'Can add photo',57,'add_photo'),(170,'Can change photo',57,'change_photo'),(171,'Can delete photo',57,'delete_photo'),(172,'Can add activity history',58,'add_activityhistory'),(173,'Can change activity history',58,'change_activityhistory'),(174,'Can delete activity history',58,'delete_activityhistory'),(175,'Can add group permission',59,'add_grouppermission'),(176,'Can change group permission',59,'change_grouppermission'),(177,'Can delete group permission',59,'delete_grouppermission'),(178,'Can add content permission',60,'add_contentpermission'),(179,'Can change content permission',60,'change_contentpermission'),(180,'Can delete content permission',60,'delete_contentpermission'),(181,'Can add question pre requisite',61,'add_questionprerequisite'),(182,'Can change question pre requisite',61,'change_questionprerequisite'),(183,'Can delete question pre requisite',61,'delete_questionprerequisite'),(184,'Can add export notification',62,'add_exportnotification'),(185,'Can change export notification',62,'change_exportnotification'),(186,'Can delete export notification',62,'delete_exportnotification'),(187,'Can add import change request',63,'add_importchangerequest'),(188,'Can change import change request',63,'change_importchangerequest'),(189,'Can delete import change request',63,'delete_importchangerequest'),(190,'Can add import change status',64,'add_importchangestatus'),(191,'Can change import change status',64,'change_importchangestatus'),(192,'Can delete import change status',64,'delete_importchangestatus'),(193,'Can add elements',65,'add_elements'),(194,'Can change elements',65,'change_elements'),(195,'Can delete elements',65,'delete_elements'),(196,'Can add device token',66,'add_devicetoken'),(197,'Can change device token',66,'change_devicetoken'),(198,'Can delete device token',66,'delete_devicetoken'),(199,'Can add style sheet',67,'add_stylesheet'),(200,'Can change style sheet',67,'change_stylesheet'),(201,'Can delete style sheet',67,'delete_stylesheet'),(202,'Can add current event',68,'add_currentevent'),(203,'Can change current event',68,'change_currentevent'),(204,'Can delete current event',68,'delete_currentevent'),(205,'Can add current filter',69,'add_currentfilter'),(206,'Can change current filter',69,'change_currentfilter'),(207,'Can delete current filter',69,'delete_currentfilter'),(208,'Can add visible columns',70,'add_visiblecolumns'),(209,'Can change visible columns',70,'change_visiblecolumns'),(210,'Can delete visible columns',70,'delete_visiblecolumns'),(211,'Can add email contents',71,'add_emailcontents'),(212,'Can change email contents',71,'change_emailcontents'),(213,'Can delete email contents',71,'delete_emailcontents'),(214,'Can add email language contents',72,'add_emaillanguagecontents'),(215,'Can change email language contents',72,'change_emaillanguagecontents'),(216,'Can delete email language contents',72,'delete_emaillanguagecontents'),(217,'Can add email receivers',73,'add_emailreceivers'),(218,'Can change email receivers',73,'change_emailreceivers'),(219,'Can delete email receivers',73,'delete_emailreceivers'),(220,'Can add message receivers',74,'add_messagereceivers'),(221,'Can change message receivers',74,'change_messagereceivers'),(222,'Can delete message receivers',74,'delete_messagereceivers'),(223,'Can add email receivers history',75,'add_emailreceivershistory'),(224,'Can change email receivers history',75,'change_emailreceivershistory'),(225,'Can delete email receivers history',75,'delete_emailreceivershistory'),(226,'Can add message receivers history',76,'add_messagereceivershistory'),(227,'Can change message receivers history',76,'change_messagereceivershistory'),(228,'Can delete message receivers history',76,'delete_messagereceivershistory'),(229,'Can add password reset request',77,'add_passwordresetrequest'),(230,'Can change password reset request',77,'change_passwordresetrequest'),(231,'Can delete password reset request',77,'delete_passwordresetrequest'),(232,'Can add elements questions',78,'add_elementsquestions'),(233,'Can change elements questions',78,'change_elementsquestions'),(234,'Can delete elements questions',78,'delete_elementsquestions'),(235,'Can add elements answers',79,'add_elementsanswers'),(236,'Can change elements answers',79,'change_elementsanswers'),(237,'Can delete elements answers',79,'delete_elementsanswers'),(238,'Can add element default lang',80,'add_elementdefaultlang'),(239,'Can change element default lang',80,'change_elementdefaultlang'),(240,'Can delete element default lang',80,'delete_elementdefaultlang'),(241,'Can add element preset lang',81,'add_elementpresetlang'),(242,'Can change element preset lang',81,'change_elementpresetlang'),(243,'Can delete element preset lang',81,'delete_elementpresetlang'),(244,'Can add preset event',82,'add_presetevent'),(245,'Can change preset event',82,'change_presetevent'),(246,'Can delete preset event',82,'delete_presetevent'),(247,'Can add attendee groups',83,'add_attendeegroups'),(248,'Can change attendee groups',83,'change_attendeegroups'),(249,'Can delete attendee groups',83,'delete_attendeegroups'),(250,'Can add custom classes',84,'add_customclasses'),(251,'Can change custom classes',84,'change_customclasses'),(252,'Can delete custom classes',84,'delete_customclasses'),(253,'Can add page content classes',85,'add_pagecontentclasses'),(254,'Can change page content classes',85,'change_pagecontentclasses'),(255,'Can delete page content classes',85,'delete_pagecontentclasses'),(256,'Can add deleted attendee',86,'add_deletedattendee'),(257,'Can change deleted attendee',86,'change_deletedattendee'),(258,'Can delete deleted attendee',86,'delete_deletedattendee'),(259,'Can add deleted history',87,'add_deletedhistory'),(260,'Can change deleted history',87,'change_deletedhistory'),(261,'Can delete deleted history',87,'delete_deletedhistory'),(262,'Can add cookie',88,'add_cookie'),(263,'Can change cookie',88,'change_cookie'),(264,'Can delete cookie',88,'delete_cookie'),(265,'Can add cookie page',89,'add_cookiepage'),(266,'Can change cookie page',89,'change_cookiepage'),(267,'Can delete cookie page',89,'delete_cookiepage'),(268,'Can add dashboard plugin',90,'add_dashboardplugin'),(269,'Can change dashboard plugin',90,'change_dashboardplugin'),(270,'Can delete dashboard plugin',90,'delete_dashboardplugin'),(271,'Can add plugin submit button',91,'add_pluginsubmitbutton'),(272,'Can change plugin submit button',91,'change_pluginsubmitbutton'),(273,'Can delete plugin submit button',91,'delete_pluginsubmitbutton'),(274,'Can add plugin pdf button',92,'add_pluginpdfbutton'),(275,'Can change plugin pdf button',92,'change_pluginpdfbutton'),(276,'Can delete plugin pdf button',92,'delete_pluginpdfbutton'),(277,'Can add attendee submit button',93,'add_attendeesubmitbutton'),(278,'Can change attendee submit button',93,'change_attendeesubmitbutton'),(279,'Can delete attendee submit button',93,'delete_attendeesubmitbutton'),(280,'Can add attendee password reset request',94,'add_attendeepasswordresetrequest'),(281,'Can change attendee password reset request',94,'change_attendeepasswordresetrequest'),(282,'Can delete attendee password reset request',94,'delete_attendeepasswordresetrequest'),(283,'Can add element html',95,'add_elementhtml'),(284,'Can change element html',95,'change_elementhtml'),(285,'Can delete element html',95,'delete_elementhtml'),(286,'Can add orders',96,'add_orders'),(287,'Can change orders',96,'change_orders'),(288,'Can delete orders',96,'delete_orders'),(289,'Can add rebates',97,'add_rebates'),(290,'Can change rebates',97,'change_rebates'),(291,'Can delete rebates',97,'delete_rebates'),(292,'Can add order items',98,'add_orderitems'),(293,'Can change order items',98,'change_orderitems'),(294,'Can delete order items',98,'delete_orderitems'),(295,'Can add credit orders',99,'add_creditorders'),(296,'Can change credit orders',99,'change_creditorders'),(297,'Can delete credit orders',99,'delete_creditorders'),(298,'Can add payments',100,'add_payments'),(299,'Can change payments',100,'change_payments'),(300,'Can delete payments',100,'delete_payments'),(301,'Can add credit usages',101,'add_creditusages'),(302,'Can change credit usages',101,'change_creditusages'),(303,'Can delete credit usages',101,'delete_creditusages'),(304,'Can add session classes',102,'add_sessionclasses'),(305,'Can change session classes',102,'change_sessionclasses'),(306,'Can delete session classes',102,'delete_sessionclasses'),(307,'Can add payment settings',103,'add_paymentsettings'),(308,'Can change payment settings',103,'change_paymentsettings'),(309,'Can delete payment settings',103,'delete_paymentsettings');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `first_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `last_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_657e7dac00037b1c_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_657e7dac00037b1c_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_7cd6b15811f33ef3_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_u_permission_id_1ec43523f5440221_fk_auth_permission_id` (`permission_id`),
  CONSTRAINT `auth_user_u_permission_id_1ec43523f5440221_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissi_user_id_5f4162fc9dc1dd8c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bookings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `check_in` date NOT NULL,
  `check_out` date NOT NULL,
  `broken_up` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bookings_attendee_id_5b3335aca2fd0935_fk_attendees_id` (`attendee_id`),
  KEY `bookings_8273f993` (`room_id`),
  CONSTRAINT `bookings_attendee_id_5b3335aca2fd0935_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `bookings_room_id_7257b3322a79c9cd_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
INSERT INTO `bookings` VALUES (1,'2018-12-08','2018-12-11',0,'2018-11-30 10:39:48.674144','2018-11-30 10:39:48.674163',1,1);
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `checkpoints`
--

DROP TABLE IF EXISTS `checkpoints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `checkpoints` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `questions` longtext COLLATE utf8_unicode_ci NOT NULL,
  `defaults` longtext COLLATE utf8_unicode_ci,
  `allow_re_entry` tinyint(1) NOT NULL,
  `is_hide` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `filter_id` int(11) DEFAULT NULL,
  `session_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `checkpoints_e93cb7eb` (`created_by_id`),
  KEY `checkpoints_4437cfac` (`event_id`),
  KEY `checkpoints_0a317463` (`filter_id`),
  KEY `checkpoints_7fc8ef54` (`session_id`),
  CONSTRAINT `checkpoints_created_by_id_723288c990f427ee_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `checkpoints_event_id_5375aef372eb0c9c_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `checkpoints_filter_id_757f7dbeba585af_fk_rule_set_id` FOREIGN KEY (`filter_id`) REFERENCES `rule_set` (`id`),
  CONSTRAINT `checkpoints_session_id_7b61e53ae71df75c_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checkpoints`
--

LOCK TABLES `checkpoints` WRITE;
/*!40000 ALTER TABLE `checkpoints` DISABLE KEYS */;
INSERT INTO `checkpoints` VALUES (1,'Dinner','',NULL,0,0,'2018-11-30 09:44:54.662959',1,1,NULL,1);
/*!40000 ALTER TABLE `checkpoints` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `content_permissions`
--

DROP TABLE IF EXISTS `content_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `content_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` enum('event','attendee','deleted_attendee','session','question','travel','location','hotel','page','menu','template','css','filter','export_filter','photo_reel','message','file_browser','checkpoints','language','economy','setting','assign_session','assign_travel','assign_hotel','group_registration') COLLATE utf8_unicode_ci NOT NULL,
  `access_level` enum('read','write','none') COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `content_permissions_156f41ed` (`admin_id`),
  KEY `content_permissions_4437cfac` (`event_id`),
  CONSTRAINT `content_permissions_admin_id_4f8e170a03bc554b_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `content_permissions_event_id_46e1f3b5f40e57a0_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `content_permissions`
--

LOCK TABLES `content_permissions` WRITE;
/*!40000 ALTER TABLE `content_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `content_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cookie`
--

DROP TABLE IF EXISTS `cookie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cookie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cookie_key` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cookie`
--

LOCK TABLES `cookie` WRITE;
/*!40000 ALTER TABLE `cookie` DISABLE KEYS */;
INSERT INTO `cookie` VALUES (1,'d40659f5-79ca-4a73-a2e3-bd0337d3966a','2018-11-30 06:06:47.520455');
/*!40000 ALTER TABLE `cookie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cookie_page`
--

DROP TABLE IF EXISTS `cookie_page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cookie_page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `visit_count` int(11) NOT NULL,
  `visit_date` date NOT NULL,
  `cookie_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cookie_page_cookie_id_3ce78ee7f57f9203_fk_cookie_id` (`cookie_id`),
  KEY `cookie_page_1a63c800` (`page_id`),
  CONSTRAINT `cookie_page_cookie_id_3ce78ee7f57f9203_fk_cookie_id` FOREIGN KEY (`cookie_id`) REFERENCES `cookie` (`id`),
  CONSTRAINT `cookie_page_page_id_33e8f9d164cb3023_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cookie_page`
--

LOCK TABLES `cookie_page` WRITE;
/*!40000 ALTER TABLE `cookie_page` DISABLE KEYS */;
INSERT INTO `cookie_page` VALUES (1,4,'2018-11-30',1,1),(2,1,'2018-11-30',1,3),(3,1,'2018-11-30',1,34),(4,6,'2018-11-30',1,2),(5,1,'2018-11-30',1,8),(6,1,'2018-11-30',1,32),(7,1,'2018-11-30',1,30),(8,1,'2018-11-30',1,29),(9,4,'2018-11-30',1,28),(10,3,'2018-11-30',1,31),(11,3,'2018-11-30',1,33);
/*!40000 ALTER TABLE `cookie_page` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_orders`
--

DROP TABLE IF EXISTS `credit_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `credit_orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `cost_excluding_vat` double NOT NULL,
  `cost_including_vat` double NOT NULL,
  `type` enum('session','hotel','travel','rebate','adjustment') COLLATE utf8_unicode_ci NOT NULL,
  `item_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status` enum('open','pending','paid','cancelled') COLLATE utf8_unicode_ci NOT NULL,
  `invoice_ref` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `order_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_orders_e93cb7eb` (`created_by_id`),
  KEY `credit_orders_69dfcb07` (`order_id`),
  CONSTRAINT `credit_orders_created_by_id_131b338dec17184b_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `credit_orders_order_id_1710a9aa7a0451ee_fk_orders_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_orders`
--

LOCK TABLES `credit_orders` WRITE;
/*!40000 ALTER TABLE `credit_orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `credit_usages`
--

DROP TABLE IF EXISTS `credit_usages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `credit_usages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `cost` double NOT NULL,
  `created_at` date NOT NULL,
  `credit_order_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `credit_usag_credit_order_id_3be3f50d43d155d8_fk_credit_orders_id` (`credit_order_id`),
  CONSTRAINT `credit_usag_credit_order_id_3be3f50d43d155d8_fk_credit_orders_id` FOREIGN KEY (`credit_order_id`) REFERENCES `credit_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `credit_usages`
--

LOCK TABLES `credit_usages` WRITE;
/*!40000 ALTER TABLE `credit_usages` DISABLE KEYS */;
/*!40000 ALTER TABLE `credit_usages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `current_event`
--

DROP TABLE IF EXISTS `current_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `current_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `current_event_156f41ed` (`admin_id`),
  KEY `current_event_4437cfac` (`event_id`),
  CONSTRAINT `current_event_admin_id_4a86b2e95ef6d025_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `current_event_event_id_2c6a51b5c59af3a_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `current_event`
--

LOCK TABLES `current_event` WRITE;
/*!40000 ALTER TABLE `current_event` DISABLE KEYS */;
INSERT INTO `current_event` VALUES (1,1,1);
/*!40000 ALTER TABLE `current_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `current_filter`
--

DROP TABLE IF EXISTS `current_filter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `current_filter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `visible_columns` longtext COLLATE utf8_unicode_ci,
  `show_rows` int(11) DEFAULT NULL,
  `table_type` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `sorted_column` int(11) DEFAULT NULL,
  `sorting_order` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `filter_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `current_filter_156f41ed` (`admin_id`),
  KEY `current_filter_4437cfac` (`event_id`),
  KEY `current_filter_0a317463` (`filter_id`),
  CONSTRAINT `current_filter_admin_id_1ce46ab8e6a3b835_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `current_filter_event_id_4e9383c40c0d516_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `current_filter_filter_id_c07ab405cb48bfd_fk_rule_set_id` FOREIGN KEY (`filter_id`) REFERENCES `rule_set` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `current_filter`
--

LOCK TABLES `current_filter` WRITE;
/*!40000 ALTER TABLE `current_filter` DISABLE KEYS */;
INSERT INTO `current_filter` VALUES (1,'[0, 1, 4, 11, 12, 13, 14]',10,'attendee',1,'asc',1,1,NULL);
/*!40000 ALTER TABLE `current_filter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_classes`
--

DROP TABLE IF EXISTS `custom_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classname` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `custom_classes_e93cb7eb` (`created_by_id`),
  KEY `custom_classes_4437cfac` (`event_id`),
  CONSTRAINT `custom_classes_created_by_id_d099257a61102bd_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `custom_classes_event_id_528754dd926058bf_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_classes`
--

LOCK TABLES `custom_classes` WRITE;
/*!40000 ALTER TABLE `custom_classes` DISABLE KEYS */;
/*!40000 ALTER TABLE `custom_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dashboard_plugin`
--

DROP TABLE IF EXISTS `dashboard_plugin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dashboard_plugin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `setting_data` longtext COLLATE utf8_unicode_ci NOT NULL,
  `modified_at` datetime(6) NOT NULL,
  `event_id` int(11) NOT NULL,
  `modified_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dashboard_plugin_4437cfac` (`event_id`),
  KEY `dashboard_plugin_b3da0983` (`modified_by_id`),
  CONSTRAINT `dashboard_plugin_event_id_41a09582bbc215b4_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `dashboard_plugin_modified_by_id_5691901531287061_fk_users_id` FOREIGN KEY (`modified_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dashboard_plugin`
--

LOCK TABLES `dashboard_plugin` WRITE;
/*!40000 ALTER TABLE `dashboard_plugin` DISABLE KEYS */;
INSERT INTO `dashboard_plugin` VALUES (1,'{\"message_statistic\": {\"start_time\": \"2018-10-23\", \"end_time\": \"2018-11-22\"}, \"session_statistic\": \"6\", \"filter_statistic\": \"2\", \"pagehit_statistic\": {\"start_time\": \"2018-10-23\", \"end_time\": \"2018-11-22\"}, \"reg_statistic\": {\"start_time\": \"2018-10-23\", \"end_time\": \"2018-11-22\"}}','2018-11-22 13:29:18.417085',1,1);
/*!40000 ALTER TABLE `dashboard_plugin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deleted_attendees`
--

DROP TABLE IF EXISTS `deleted_attendees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deleted_attendees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `lastname` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `phonenumber` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `deleted_at` datetime(6) NOT NULL,
  `deleted_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `deleted_attendees_d19ec81d` (`deleted_by_id`),
  KEY `deleted_attendees_4437cfac` (`event_id`),
  CONSTRAINT `deleted_attendees_deleted_by_id_255a52068df09b3d_fk_users_id` FOREIGN KEY (`deleted_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `deleted_attendees_event_id_cad9b2eb76fd2e4_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deleted_attendees`
--

LOCK TABLES `deleted_attendees` WRITE;
/*!40000 ALTER TABLE `deleted_attendees` DISABLE KEYS */;
/*!40000 ALTER TABLE `deleted_attendees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `deleted_history`
--

DROP TABLE IF EXISTS `deleted_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `deleted_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `activity_type` enum('update','delete','register','message','offline','check-in') COLLATE utf8_unicode_ci NOT NULL,
  `category` enum('event','session','question','travel','room','message','profile','push_notification','group','tag','package','checkpoint','photo','registration_group','rebate','order','order_item','credit_order','credit_usage','payment') COLLATE utf8_unicode_ci NOT NULL,
  `old_value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `new_value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `activity_message` longtext COLLATE utf8_unicode_ci,
  `admin_id` int(11) DEFAULT NULL,
  `attendee_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `message_id` int(11) DEFAULT NULL,
  `photo_id` int(11) DEFAULT NULL,
  `question_id` int(11) DEFAULT NULL,
  `registration_group_id` int(11) DEFAULT NULL,
  `room_id` int(11) DEFAULT NULL,
  `session_id` int(11) DEFAULT NULL,
  `travel_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `deleted_history_156f41ed` (`admin_id`),
  KEY `deleted_history_c50970ee` (`attendee_id`),
  KEY `deleted_history_4437cfac` (`event_id`),
  KEY `deleted_history_4ccaa172` (`message_id`),
  KEY `deleted_history_b4e75e23` (`photo_id`),
  KEY `deleted_history_7aa0f6ee` (`question_id`),
  KEY `deleted_history_b107eae0` (`registration_group_id`),
  KEY `deleted_history_8273f993` (`room_id`),
  KEY `deleted_history_7fc8ef54` (`session_id`),
  KEY `deleted_history_46413c35` (`travel_id`),
  CONSTRAINT `deleted_his_attendee_id_20e76b0b3d1a6467_fk_deleted_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `deleted_attendees` (`id`),
  CONSTRAINT `deleted_history_admin_id_78300a2eb5ae04f5_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `deleted_history_event_id_19c58de74ef177aa_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `deleted_history_message_id_b34a917937a79c9_fk_message_history_id` FOREIGN KEY (`message_id`) REFERENCES `message_history` (`id`),
  CONSTRAINT `deleted_history_photo_id_4c4448ea51b3b07c_fk_photos_id` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`id`),
  CONSTRAINT `deleted_history_question_id_cc9975c66017d6_fk_questions_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`),
  CONSTRAINT `deleted_history_room_id_10c18c419da006af_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`),
  CONSTRAINT `deleted_history_session_id_73952cbcb8f2b0ea_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`),
  CONSTRAINT `deleted_history_travel_id_563d30e60574af78_fk_travels_id` FOREIGN KEY (`travel_id`) REFERENCES `travels` (`id`),
  CONSTRAINT `faa72317da97e2cfc9739a21623dadb7` FOREIGN KEY (`registration_group_id`) REFERENCES `registration_groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `deleted_history`
--

LOCK TABLES `deleted_history` WRITE;
/*!40000 ALTER TABLE `deleted_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `deleted_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices_token`
--

DROP TABLE IF EXISTS `devices_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devices_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_unique_id` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `token` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `os_type` enum('1','2') COLLATE utf8_unicode_ci NOT NULL,
  `arn_enpoint` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `is_enable` tinyint(1) NOT NULL,
  `offline_pakage_status` tinyint(1) NOT NULL,
  `package_download_count` int(11) NOT NULL,
  `package_created_at` datetime(6) DEFAULT NULL,
  `package_version` int(11) NOT NULL,
  `attendee_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `devices_token_attendee_id_3f6d29f0f8fc9ae7_fk_attendees_id` (`attendee_id`),
  CONSTRAINT `devices_token_attendee_id_3f6d29f0f8fc9ae7_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices_token`
--

LOCK TABLES `devices_token` WRITE;
/*!40000 ALTER TABLE `devices_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `devices_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext COLLATE utf8_unicode_ci NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `djang_content_type_id_50f93280bc745f13_fk_django_content_type_id` (`content_type_id`),
  KEY `django_admin_log_user_id_6d2774cbc497d3c2_fk_auth_user_id` (`user_id`),
  CONSTRAINT `djang_content_type_id_50f93280bc745f13_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_6d2774cbc497d3c2_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_198be3e2317f2d31_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(58,'app','activityhistory'),(18,'app','answers'),(14,'app','attendee'),(83,'app','attendeegroups'),(94,'app','attendeepasswordresetrequest'),(93,'app','attendeesubmitbutton'),(21,'app','attendeetag'),(31,'app','booking'),(45,'app','checkpoint'),(60,'app','contentpermission'),(88,'app','cookie'),(89,'app','cookiepage'),(99,'app','creditorders'),(101,'app','creditusages'),(68,'app','currentevent'),(69,'app','currentfilter'),(84,'app','customclasses'),(90,'app','dashboardplugin'),(86,'app','deletedattendee'),(87,'app','deletedhistory'),(66,'app','devicetoken'),(80,'app','elementdefaultlang'),(95,'app','elementhtml'),(81,'app','elementpresetlang'),(65,'app','elements'),(79,'app','elementsanswers'),(78,'app','elementsquestions'),(71,'app','emailcontents'),(72,'app','emaillanguagecontents'),(73,'app','emailreceivers'),(75,'app','emailreceivershistory'),(50,'app','emailtemplates'),(16,'app','eventadmin'),(8,'app','events'),(62,'app','exportnotification'),(48,'app','exportrule'),(20,'app','exportstate'),(42,'app','generaltag'),(9,'app','group'),(59,'app','grouppermission'),(22,'app','hotel'),(63,'app','importchangerequest'),(64,'app','importchangestatus'),(10,'app','locations'),(33,'app','match'),(34,'app','matchline'),(53,'app','menuitem'),(54,'app','menupermission'),(38,'app','messagecontents'),(49,'app','messagehistory'),(39,'app','messagelanguagecontents'),(74,'app','messagereceivers'),(76,'app','messagereceivershistory'),(40,'app','notification'),(37,'app','option'),(98,'app','orderitems'),(96,'app','orders'),(51,'app','pagecontent'),(85,'app','pagecontentclasses'),(52,'app','pageimage'),(55,'app','pagepermission'),(77,'app','passwordresetrequest'),(100,'app','payments'),(103,'app','paymentsettings'),(57,'app','photo'),(56,'app','photogroup'),(92,'app','pluginpdfbutton'),(91,'app','pluginsubmitbutton'),(82,'app','presetevent'),(12,'app','presets'),(61,'app','questionprerequisite'),(17,'app','questions'),(97,'app','rebates'),(15,'app','registrationgroupowner'),(13,'app','registrationgroups'),(32,'app','requestedbuddy'),(23,'app','room'),(24,'app','roomallotment'),(35,'app','ruleset'),(46,'app','scan'),(11,'app','seminars'),(26,'app','seminarspeakers'),(29,'app','seminarsusers'),(25,'app','session'),(102,'app','sessionclasses'),(47,'app','sessionrating'),(43,'app','sessiontags'),(41,'app','setting'),(67,'app','stylesheet'),(19,'app','tag'),(27,'app','travel'),(30,'app','travelattendee'),(28,'app','travelboundrelation'),(44,'app','traveltag'),(36,'app','usedrule'),(7,'app','users'),(70,'app','visiblecolumns'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2018-11-22 12:04:58.672519'),(2,'auth','0001_initial','2018-11-22 12:05:08.580566'),(3,'admin','0001_initial','2018-11-22 12:05:11.078788'),(4,'app','0001_initial','2018-11-22 12:12:54.532907'),(5,'contenttypes','0002_remove_content_type_name','2018-11-22 12:12:56.430865'),(6,'auth','0002_alter_permission_name_max_length','2018-11-22 12:12:57.516703'),(7,'auth','0003_alter_user_email_max_length','2018-11-22 12:12:59.602667'),(8,'auth','0004_alter_user_username_opts','2018-11-22 12:12:59.688201'),(9,'auth','0005_alter_user_last_login_null','2018-11-22 12:13:00.405874'),(10,'auth','0006_require_contenttypes_0002','2018-11-22 12:13:00.454898'),(11,'sessions','0001_initial','2018-11-22 12:13:01.299054');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_de54fa62` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('gtdawyomoyum7xeembdp3dw9finf9ms4','ZDhjYzA1YzYzZmYyMzhhODU5OTU5YjFkNzQ0NzU4ZGI3NWZjZDVjZDp7ImlzX2xvZ2luIjp0cnVlLCJjb29raWVfZXhwaXJlIjoiODY0MDAwIiwiZXZlbnRfYXV0aF91c2VyIjp7ImV2ZW50X25hbWUiOiJEZWZhdWx0IFByb2plY3QiLCJuYW1lIjoiYWRtaW4gYWRtaW4iLCJpc19hdHRlbmRlZSI6ZmFsc2UsImVtYWlsIjoiYWRtaW5Ad3NpdC5jb20iLCJldmVudF91cmwiOiJkZWZhdWx0LXByb2plY3QiLCJ0eXBlIjoic3VwZXJfYWRtaW4iLCJldmVudF9pZCI6MSwiaWQiOjEsImJhc2VfdXJsIjoiaHR0cDovLzEyNy4wLjAuMTo4MDAwL2RlZmF1bHQtcHJvamVjdCJ9LCJhZG1pbl9wZXJtaXNzaW9uIjp7ImV2ZW50X3Blcm1pc3Npb24iOltdLCJjb250ZW50X3Blcm1pc3Npb24iOnt9LCJncm91cF9wZXJtaXNzaW9uIjpbXX19','2018-12-02 13:47:38.373014'),('idg00f7ixtg48669fdbeqc1ettg0phwq','MTBhYjVjYmNmMmFiM2RmZGM3MDBiMDE3NDc1NjUzYzJjNjczNWViZDp7ImV2ZW50X3VybCI6ImRlZmF1bHQtcHJvamVjdCIsImJhc2VfdXJsIjoiaHR0cDovLzEyNy4wLjAuMTo4MDAzL2RlZmF1bHQtcHJvamVjdCIsInNvY2tldF91cmwiOiJ3czovLzEyNy4wLjAuMSIsIndlYmNhbF91cmwiOiJ3ZWJjYWw6Ly8xMjcuMC4wLjEvZGVmYXVsdC1wcm9qZWN0IiwiY3VycmVudF91cmwiOiJsb2NhdGlvbi1saXN0IiwiY29va2llX2V4cGlyZSI6Ijg2NDAwMCIsImV2ZW50X2F1dGhfdXNlciI6eyJpZCI6MSwibmFtZSI6ImFkbWluIGFkbWluIiwiZW1haWwiOiJhZG1pbkB3c2l0LmNvbSIsInR5cGUiOiJzdXBlcl9hZG1pbiIsImV2ZW50X2lkIjoxLCJldmVudF9uYW1lIjoiRGVmYXVsdCBQcm9qZWN0IiwiZXZlbnRfdXJsIjoiZGVmYXVsdC1wcm9qZWN0IiwiYmFzZV91cmwiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDMvZGVmYXVsdC1wcm9qZWN0IiwiaXNfYXR0ZW5kZWUiOmZhbHNlfSwiaXNfbG9naW4iOnRydWUsImFkbWluX3Blcm1pc3Npb24iOnsiZXZlbnRfcGVybWlzc2lvbiI6W10sImNvbnRlbnRfcGVybWlzc2lvbiI6e30sImdyb3VwX3Blcm1pc3Npb24iOltdfSwiZXZlbnRfaWQiOjEsImxhbmd1YWdlX2lkIjo2LCJldmVudF91c2VyIjp7ImlkIjoxLCJuYW1lIjoiTWFoZWRpIEhhc2FuIiwiZW1haWwiOiJtYWhlZGlAd29ya3NwYWNlaXQuY29tIiwidHlwZSI6InVzZXIiLCJhdHRlbmRpbmciOiJZZXMiLCJhdmF0YXIiOiIiLCJzZWNyZXRfa2V5Ijoid04xbHJsVXVyVVgzaW44eCIsImV2ZW50X2lkIjoxLCJuZXdfc2Vzc2lvbnNfZmluaXNoZWQiOltdLCJuZXdfc2Vzc2lvbnNfbmV4dF91cCI6W119LCJpc191c2VyX2xvZ2luIjp0cnVlfQ==','2018-12-10 10:52:37.107069'),('rc6evad1tczzd63chphwydcp5taczcx9','MmMzMDcxZmI0N2Q3ZWYyMzg5MmU0OTE3ZmYxYjE3MTc0ZWMyNDdhNDp7ImlzX2xvZ2luIjp0cnVlLCJjb29raWVfZXhwaXJlIjoiODY0MDAwIiwiZXZlbnRfYXV0aF91c2VyIjp7ImV2ZW50X25hbWUiOiJEZWZhdWx0IFByb2plY3QiLCJldmVudF91cmwiOiJkZWZhdWx0LXByb2plY3QiLCJpc19hdHRlbmRlZSI6ZmFsc2UsImVtYWlsIjoiYWRtaW5Ad3NpdC5jb20iLCJuYW1lIjoiYWRtaW4gYWRtaW4iLCJ0eXBlIjoic3VwZXJfYWRtaW4iLCJldmVudF9pZCI6MSwiaWQiOjEsImJhc2VfdXJsIjoiaHR0cDovLzEyNy4wLjAuMTo4MDAwL2RlZmF1bHQtcHJvamVjdCJ9LCJhZG1pbl9wZXJtaXNzaW9uIjp7ImV2ZW50X3Blcm1pc3Npb24iOltdLCJjb250ZW50X3Blcm1pc3Npb24iOnt9LCJncm91cF9wZXJtaXNzaW9uIjpbXX19','2018-12-02 13:44:26.638894'),('y0wzdk3wa4ig2s7f3edq7dl74kqgy07x','Y2NjMzIxNWU0ZmQyMjAyYTNiODY0Nzk3MDRkOTdjZjRjYmYyODkwNDp7ImlzX2xvZ2luIjp0cnVlLCJhZG1pbl9wZXJtaXNzaW9uIjp7ImV2ZW50X3Blcm1pc3Npb24iOltdLCJjb250ZW50X3Blcm1pc3Npb24iOnt9LCJncm91cF9wZXJtaXNzaW9uIjpbXX0sImNvb2tpZV9leHBpcmUiOiI4NjQwMDAiLCJldmVudF9hdXRoX3VzZXIiOnsiZXZlbnRfbmFtZSI6IkRlZmF1bHQgUHJvamVjdCIsIm5hbWUiOiJhZG1pbiBhZG1pbiIsImlzX2F0dGVuZGVlIjpmYWxzZSwiZW1haWwiOiJhZG1pbkB3c2l0LmNvbSIsImV2ZW50X3VybCI6ImRlZmF1bHQtcHJvamVjdCIsInR5cGUiOiJzdXBlcl9hZG1pbiIsImV2ZW50X2lkIjoxLCJpZCI6MSwiYmFzZV91cmwiOiJodHRwOi8vMTI3LjAuMC4xOjgwMDAvZGVmYXVsdC1wcm9qZWN0In0sImV2ZW50X2lkIjoxfQ==','2018-12-02 14:08:29.166587');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `element_default_lang`
--

DROP TABLE IF EXISTS `element_default_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `element_default_lang` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('text','item_text','button','notification','validation_text') COLLATE utf8_unicode_ci NOT NULL,
  `lang_key` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `default_value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `element_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `element_default_lang_7057e840` (`element_id`),
  CONSTRAINT `element_default_lang_element_id_41ee8b42c407e2ef_fk_elements_id` FOREIGN KEY (`element_id`) REFERENCES `elements` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=387 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `element_default_lang`
--

LOCK TABLES `element_default_lang` WRITE;
/*!40000 ALTER TABLE `element_default_lang` DISABLE KEYS */;
INSERT INTO `element_default_lang` VALUES (1,'notification','notify_clash_session','You have a clash with previously selected session','You have a clash with previously selected session',26),(2,'notification','notify_registered_session','You are registered for this session','You are registered for this session',26),(3,'notification','notify_queue_session','You are in Queue for this session','You are in Queue for this session',26),(4,'notification','notify_unregistered_session','You have unregistered for this session','You have unregistered for this session',26),(5,'notification','notify_session_full','This sessions Capacity Full','This sessions Capacity Full',26),(6,'text','evaluation_txt_title','Title','Evaluation',15),(7,'button','evaluation_btn_send','Send','Send Evaluation',15),(8,'notification','evaluation_notify_session_success','All session are successfully rated.','All session are successfully rated.',15),(9,'text','messages_txt_title','Title','Messages',16),(10,'button','messages_btn_read_archived','Read Archived message','Read Archived message',16),(11,'button','messages_btn_mark_all_read','Mark all as read','Mark all as read',16),(12,'notification','messages_notify_read_success','All message read successfully','All message read successfully',16),(13,'notification','messages_notify_archived_success','message archived successfully','message archived successfully',16),(14,'text','nextup_txt_title','Title','Next up',17),(15,'text','locationlist_txt_title','Title','Location list',18),(16,'text','locationlist_txt_map_location','Map to location','Map to location',18),(17,'text','locationlist_txt_address','address','address',18),(18,'text','locationlist_txt_contact','contact','contact',18),(19,'text','sessionradiobutton_txt_title','Title','Session Radio button',19),(28,'text','sessioncheckbox_txt_title','Title','Session Checkbox',20),(59,'text','hotelreservation_txt_session_status','Session Status','Session Status',22),(60,'text','hotelreservation_txt_checkin','Check-in','Check-in',22),(61,'text','hotelreservation_txt_checkout','Check-out','Check-out',22),(62,'text','hotelreservation_txt_name','Name','Name',22),(63,'text','hotelreservation_txt_description','Description','Description',22),(64,'text','hotelreservation_txt_location','Location','Location',22),(65,'text','hotelreservation_txt_room_buddy','Room buddy','Room buddy',22),(66,'button','hotelreservation_btn_add_stay','Add a stay','Add a stay',22),(67,'button','hotelreservation_btn_remove_stay','Remove a stay','Remove a stay',22),(68,'text','th_hotel_name','Hotel name','Hotel name',27),(69,'text','th_hotel_room_description','Room Description','Room Description',27),(70,'text','th_hotel_beds','Beds','Beds',27),(71,'text','th_hotel_check_out','Check-out','Check-out',27),(72,'text','th_hotel_check_in','Check-in','Check-in',27),(73,'text','th_hotel_requested_room_buddy','Requested room buddy','Requested room buddy',27),(74,'text','th_hotel_actual_room_buddy','Actual room buddy','Actual room buddy',27),(75,'text','th_hotel_location','Location','Location',27),(76,'text','th_session_session_name','Session','Session',29),(77,'text','th_session_session_group','Group','Group',29),(78,'text','th_session_description','Description','Description',29),(79,'text','th_session_start','Start','Start',29),(80,'text','th_session_end','End','End',29),(81,'text','th_session_location','Location','Location',29),(82,'text','th_session_speakers','Speakers','Speakers',29),(83,'text','th_session_tags','Tags','Tags',29),(84,'text','th_session_status','Status','Status',29),(85,'text','th_travel_name','Travel name','Travel name',28),(86,'text','th_travel_group','Group','Group',28),(87,'text','th_travel_departure_city','Departure city','Departure city',28),(88,'text','th_travel_arrival_city','Arrival city','Arrival city',28),(89,'text','th_travel_departure_time','Departure time & date','Departure time & date',28),(90,'text','th_travel_arrival_time','Arrival time & date','Arrival time & date',28),(91,'text','th_travel_location','Location','Location',28),(92,'text','th_travel_description','Description','Description',28),(93,'text','th_question_name','Question','Question',30),(94,'text','th_question_answer','Answer','Answer',30),(95,'text','th_question_registration_date','Registration date','Registration date',30),(96,'text','th_question_last_update_date','Last update date','Last update date',30),(97,'text','th_question_attendee_groups','Attendee groups','Attendee groups',30),(98,'text','th_question_tags','Tags','Tags',30),(99,'text','request_login_txt_email','Your email address','Your email address',25),(100,'button','request_login_btn_request','Request','Request',25),(101,'text','request_login_notify_request','Validation failed','Validation failed',25),(102,'text','login_form_txt_email','Email address','Email address',23),(103,'text','login_form_txt_password','Password','Password',23),(104,'text','login_form_txt_forgot_password','Forgotten your password?','Forgotten your password?',23),(105,'button','login_form_btn_login','Login','Login',23),(106,'validation_text','login_form_notify_valid_failed','Validation failed','Validation failed',23),(107,'validation_text','hotelreservation_notify_validation_fail','Validation failed','Validation failed',22),(108,'validation_text','sessioncheckbox_notify_validation_fail','Validation failed','Validation failed',20),(109,'text','th_hotel_group','Group','Group',27),(110,'notification','evaluation_notify_socket','You have a session end','You have a new session to evaluate',15),(111,'notification','nextup_notify_socket_session_will_start','Session will start','Session {session_name} will be start on {remain_time} minutes',17),(112,'notification','messages_notify_session_clash','A seat has become available to an activity you\"re queueing for but has a time conflict with your previous choice. Would you like to switch to <strong>{session1}</strong> or keep your current choice <strong>{session2}</strong>?','A seat has become available to an activity you\"re queueing for but has a time conflict with your previous choice. Would you like to switch to <strong>{session1}</strong> or keep your current choice <strong>{session2}</strong>?',16),(113,'notification','messages_notify_session_attend','The session <strong>{session}</strong> has been added to your agenda.','The session <strong>{session}</strong> has been added to your agenda.',16),(114,'text','messages_txt_organizer','Organizer','Organizer',16),(115,'text','message_txt_session_conflict','Session Conflict','Session Conflict',16),(116,'button','messages_btn_session_conflict_yes','Switch','Switch',16),(117,'button','messages_btn_session_conflict_no','Keep','Keep',16),(118,'text','messages_txt_countdown','If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.','If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.',16),(119,'notification','messages_notify_socket_session','You have new Notification','You have new Notification',16),(120,'notification','nextup_notify_socket_session_started','Session is started','Session {session_name} is already started',17),(121,'notification','login_form_notify_successfull','Login Successfull','Login Successfull',23),(122,'notification','submit_button_notify_success','Submit success','Submit Successfull',24),(123,'validation_text','submit_button_notify_error','Submit Error','An Error occurred ',24),(124,'notification','request_login_notify_success','Request Login Activation Url','An Email sent to you with activation url',25),(125,'text','reset_password_txt_email','Email address','Email address',31),(126,'button','reset_password_btn_send','Send reset instructions','Send reset instructions',31),(127,'validation_text','reset_password_notify_validation','Validation failed','Validation failed',31),(128,'text','new_password_txt_password','New password','New password',32),(129,'text','new_password_txt_repeat_password','Repeat new password','Repeat new password',32),(130,'button','new_password_btn_change','Change password','Change password',32),(131,'validation_text','new_password_notify_validation','Validation failed','Validation failed',32),(132,'notification','submit_button_notify_registration_success','Attendee Registration Successfully','Attendee Registration Successfully',24),(133,'validation_text','submit_button_notify_er_registration_email','Email already exists','Email already exists',24),(134,'validation_text','submit_button_notify_er_registration_failed','Something went wrong','Something went wrong {error}',24),(135,'notification','new_password_notify_changed','Password Changed Successfully','Password Changed Successfully',32),(136,'notification','reset_password_notify_email_send','An recovery email has been sent to email','An recovery email has been sent to email',31),(137,'text','attendee_list_txt_title','Attendee list intro','Attendee list intro',33),(138,'button','attendee_list_btn_download_spreadsheet','Download spreadsheet','Download spreadsheet',33),(139,'notification','attendee_list_notify_spreadsheet_download','Spreadsheet Downloaded','Spreadsheet Downloaded',33),(140,'text','sessiondetails_txt_session_details','Session Details','Session Details',34),(141,'text','sessiondetails_txt_attending','Attending','Attending',34),(142,'text','sessiondetails_txt_starts','starts','starts',34),(143,'text','sessiondetails_txt_ends','ends','ends',34),(144,'text','sessiondetails_txt_rsvp','Rsvp','Rsvp',34),(145,'text','sessiondetails_txt_speakers','Speakers','Speakers',34),(146,'text','sessiondetails_txt_tags','Tags','Tags',34),(147,'text','sessiondetails_txt_session_group','Session Group','Session Group',34),(148,'text','sessiondetails_txt_seat_availability','Seats Availability','Seats Availability',34),(149,'text','sessiondetails_txt_location','Location','Location',34),(155,'text','evaluation_txt_empty','Empty','Evaluation is Empty',15),(156,'text','messages_txt_empty','Empty','Message is Empty',16),(157,'text','nextup_txt_empty','Empty','Next up is Empty',17),(158,'text','locationlist_txt_placeholder_search','Placeholder Search','Search',18),(159,'text','attendee_list_txt_placeholder_search','Placeholder Search','Search',33),(160,'notification','notify_title_success','Notification Title Success','Success!',26),(161,'notification','notify_title_warning','Notification Title Warning','Warning!',26),(162,'notification','notify_title_error','Notification Title Error','Error!',26),(163,'text','sessiondetails_txt_seat_availability_good','Seats Availability Good','Good',34),(164,'text','sessiondetails_txt_seat_availability_x_of_y','X of Y Seats Available','{X} of {Y} seats available',34),(165,'text','sessiondetails_txt_seats_available','Seats Available','seats available',34),(166,'text','sessiondetails_txt_no_seats_available','No Seats Available','No seats available',34),(167,'text','sessiondetails_txt_few_seats_available','Few Seats Available','Few seats available',34),(168,'text','sessiondetails_txt_seats_available_queue_is_open','Queue is Open','queue is open',34),(169,'text','hotelreservation_txt_room_buddy_placeholder','Room Buddy Placeholder','Select a room buddy',22),(170,'notification','attendee_list_notify_download_processing','Your request is processing, file will be download within few moment','Your request is processing, file will be download within few moment',33),(171,'text','attendee_list_txt_x_y_of_z','X - Y of Z items','{X} - {Y} of {Z} items',33),(172,'text','archive_message_txt_intro','Archive Messages Intro','Archived Messages',35),(173,'text','archive_message_txt_organizer','Organizer','Organizer',35),(174,'text','archive_message_txt_empty','Empty','Message is Empty',35),(175,'notification','notify_session_queue_not_open','This sessions Capacity Full and Queue is not Open','This sessions Capacity Full and Queue is not Open',26),(176,'notification','notify_session_already_attend','You Have Already Attend in this Session','You Have Already Attend in this Session',26),(177,'notification','notify_session_already_queue','You Have Already in Queue in this Session','You Have Already in Queue in this Session',26),(178,'notification','notify_session_not_available','This Session Is not Available','This Session Is not Available',26),(184,'text','archive_message_txt_session_conflict','Session Conflict','Session Conflict',35),(185,'button','archive_messages_btn_session_conflict_yes','Yes','Yes',35),(186,'button','archive_messages_btn_session_conflict_no','No','No',35),(187,'text','archive_messages_txt_countdown','If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.','If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.',35),(188,'text','locationlist_txt_empty','Empty','Location is Empty',18),(189,'text','sessionradiobutton_txt_empty','Empty','Session radio is Empty',19),(190,'text','sessioncheckbox_txt_empty','Empty','Session checkbox is Empty',20),(191,'text','evaluation_txt_misconfigured','Misconfigured','Evaluation settings are misconfigured.',15),(192,'text','messages_txt_misconfigured','Misconfigured','Message settings are misconfigured.',16),(193,'text','nextup_txt_misconfigured','Misconfigured','Next Up settings are misconfigured.',17),(194,'text','locationlist_txt_misconfigured','Misconfigured','Location settings are misconfigured.',18),(195,'text','sessionradiobutton_txt_misconfigured','Misconfigured','Session radio settings are misconfigured.',19),(196,'text','sessioncheckbox_txt_misconfigured','Misconfigured','Session checkbox settings are misconfigured.',20),(198,'text','hotelreservation_txt_misconfigured','Misconfigured','Hotel reservation settings are misconfigured.',22),(199,'text','login_form_txt_misconfigured','Misconfigured','Login form settings are misconfigured.',23),(200,'text','submit_button_txt_misconfigured','Misconfigured','Submit button settings are misconfigured.',24),(201,'text','request_login_txt_misconfigured','Misconfigured','Request login settings are misconfigured.',25),(202,'text','reset_password_txt_misconfigured','Misconfigured','Reset password settings are misconfigured.',31),(203,'text','new_password_txt_misconfigured','Misconfigured','New password settings are misconfigured.',32),(204,'text','attendee_list_txt_misconfigured','Misconfigured','Attendee list settings are misconfigured.',33),(205,'text','hotelreservation_txt_empty','Empty','Hotel reservation is Empty',22),(206,'text','attendee_list_txt_empty','Empty','Attendee list is Empty',33),(207,'text','photo_upload_comment_label','Photo comment label','Comment',36),(208,'text','photo_upload_comment_placeholder','Photo comment placeholder','add comment',36),(209,'button','photo_upload_button','Photo Upload Button','Upload Photo',36),(210,'notification','photo_upload_notification_success','Photo Upload Success','Photo Uploaded Successfully',36),(211,'validation_text','photo_upload_notification_error_large','Photo Upload Large Image Error','The image you are trying to upload is too large.',36),(212,'validation_text','photo_upload_notification_error_small','Photo Upload Small Image Error','The image you are trying to upload is too small.',36),(213,'validation_text','photo_upload_notification_error_general','Photo Upload General Error','Something went wrong. Please try again.',36),(214,'text','photo_upload_txt_misconfigured','Misconfigured','Photo Upload settings are misconfigured.',36),(215,'text','photo_gallery_txt_misconfigured','Misconfigured','Photo Gallery settings are misconfigured.',37),(216,'text','hotelreservation_txt_select_room_buddy','Select room buddy','Select a room buddy',22),(217,'text','hotelreservation_txt_no_data_found','No data found','No data found',22),(218,'validation_text','hotelreservation_notify_fix_date','Fix date','Fix date',22),(219,'validation_text','hotelreservation_notify_match_previous_date','Match previous date','Match previous date',22),(220,'validation_text','hotelreservation_notify_require_room_selection','Require room selection','Require room selection',22),(221,'validation_text','hotelreservation_notify_require_room_buddy','Require room buddy','Require room buddy',22),(222,'validation_text','hotelreservation_notify_max_stay_reach','Max stay reached','Max stay reached',22),(223,'validation_text','hotelreservation_notify_date_clash','Date clash','Date clash',22),(224,'validation_text','hotelreservation_date_not_set','Date is not set','Date is not set',22),(225,'text','th_question_select_ur_ques','Please select your {question}','Please select your {question}',30),(226,'button','photo_upload_photo_choose','Photo Choose Button','Upload',36),(227,'text','photo_upload_filename','Photo File Name Label','Filename:',36),(228,'text','th_question_select_option','Select option text','Select',30),(229,'text','photo_gallery_pagination_text','Photo gallery pagination text','Showing {X} to {Y} of {Z} photos',37),(230,'text','logout_message_text','Logout message text','You\'ve been logged out. Click here to go to the start page',38),(231,'button','logout_back_button','Logout back button','Go To Start Page',38),(232,'text','photo_gallery_comment_text','Comment label text','Comment',37),(233,'text','photo_gallery_uploader_text','Uploader label text','Uploader',37),(234,'text','photo_gallery_no_photo_exist_text','No Photo exist text','No Photo exist',37),(235,'text','photo_gallery_previous_text','Text for pagination Previous','Previous',37),(236,'text','photo_gallery_next_text','Text for pagination Next','Next',37),(237,'validation_text','hotelreservation_notify_room_validation_msg','Room validation message','Room is not available.',22),(238,'notification','submit_button_notify_update_success','Attendee update success message','Attendee Updated Successfully.',24),(239,'validation_text','submit_button_notify_update_fail','Attendee update fail message','Attendee Update Failed.',24),(240,'validation_text','messages_notify_validation_failed','Message Archive failed','Message Archive failed',16),(241,'validation_text','evaluation_notify_validation_failed','Session rated failed.','Session rated failed.',15),(242,'validation_text','sessionradiobutton_notify_validation_fail','Validation failed','Validation failed',19),(243,'button','multiple_registration_add_attendee_test','Test','Test',39),(244,'text','multiple_registration_current_no_of_attendees','Current number of attendees Text','Current number of attendees',39),(245,'button','multiple_registration_edit_button','Edit Button','Edit',39),(246,'button','multiple_registration_delete_button','Delete Button','Delete',39),(247,'text','multiple_registration_not_yet_registered','Not yet registered Text','Not yet registered',39),(248,'button','multiple_registration_add_attendee','Add attendee Button','Add an attendee',39),(249,'text','multiple_registration_misconfigured','Misconfigured Text','Multiple registration settings are Misconfigured',39),(250,'validation_text','multiple_registration_validation_fail','Validation failed','Validation failed',39),(251,'notification','notify_attendee_registration_time_expire','Attendee registration time expire notification','Your temporary session has been expired.',26),(252,'validation_text','multiple_registration_failed','Error','Something Went wrong. Please try again',39),(253,'notification','multiple_registration_success','Success','All attendee Register successfully',39),(254,'text','multiple_registration_group_column','Column Attendee group','Attendee group',39),(255,'text','multiple_registration_actions_column','Column Attendee Actions','Actions',39),(256,'text','multiple_registration_text_order_owner','Order Owner','Order Owner',39),(257,'text','multiple_registration_text_attendee','Attendee','Attendee',39),(258,'text','sessiondetails_txt_session_cost','Session Cost','Cost',34),(259,'text','sessiondetails_txt_session_cost_excl_vat','Session Cost Excluding Vat','(excl. vat {X})',34),(260,'text','sessiondetails_txt_session_cost_incl_vat','Session Cost Including Vat','(incl. vat {X})',34),(270,'text','economy_txt_order_table','Economy Order Table','Order Table',41),(271,'text','economy_txt_order_number','Economy Order Number','Order Number',41),(272,'text','economy_txt_status','Economy Status','Status',41),(273,'text','economy_txt_due_date','Economy Due Date','Due',41),(274,'text','economy_txt_cost_excl_vat','Economy Cost Excluding VAT','Cost excl. VAT',41),(275,'text','economy_txt_cost_incl_vat','Economy Cost Including VAT','Cost incl. VAT',41),(276,'text','economy_txt_rebate_amount','Economy Rebate Amount','Rebate Amount',41),(277,'text','economy_txt_amount','Economy Amount','Amount',41),(278,'text','economy_txt_vat','Economy VAT','VAT',41),(279,'text','economy_txt_amount','Economy Amount','Amount',41),(280,'text','economy_txt_grand_total','Economy Grand Total','Grand Total',41),(281,'text','economy_txt_balance_table','Economy Balance Table','Balance Table',41),(282,'text','economy_txt_data_and_time','Economy Date & time','Date & time',41),(283,'text','economy_txt_link_to_invoice_or_receipt','Economy Link to Invoice / Receipt','Link to Invoice / Receipt',41),(284,'button','economy_txt_invoice_download_button','Economy Invoice Download Button','Download',41),(285,'text','economy_txt_invoice_created','Economy Invoice created','Invoice created',41),(286,'text','economy_txt_invoice_settled','Economy Invoice settled','Invoice settled',41),(287,'text','economy_txt_credit_invoice','Economy Credit invoice','Credit invoice',41),(288,'text','economy_txt_order_balance','Economy Order balance','Order balance',41),(289,'text','economy_txt_misconfigured','Economy Misconfigured','Economy settings are Misconfigured',41),(290,'validation_text','economy_notify_validation_fail','Validation failed','Validation failed',41),(291,'text','economy_txt_status_open','Economy Status Open','Open',41),(292,'text','economy_txt_status_pending','Economy Status Pending','Pending',41),(293,'text','economy_txt_status_paid','Economy Status Paid','Open',41),(294,'text','economy_txt_status_cancelled','Economy Status Cancelled','Cancelled',41),(295,'button','economy_txt_place_order_button','Economy Place Order Button','Place Order',41),(296,'text','economy_txt_empty','Economy Empty','Economy settings are Empty',41),(297,'notification','economy_notify_order_status_change','Order status change message','Order status is changed Open to Pending successfully',41),(298,'text','session_agenda_txt_title','Title','Session Agenda',42),(299,'text','session_agenda_txt_show_my_sess','Show my sessions','Show my sessions only',42),(310,'button','session_agenda_btn_today','Today Button','Today',42),(311,'button','session_agenda_btn_subscribe_sessions','Subscribe to my sessions','Subscribe to my sessions',42),(319,'text','session_agenda_txt_misconfigured','Misconfigured','Session Agenda settings are misconfigured.',42),(320,'text','session_agenda_txt_column_session_group','Column Session Group','Session Group',42),(321,'text','session_agenda_txt_column_date','Column Date','Date',42),(322,'text','session_agenda_txt_column_time','Column Time','Time',42),(323,'text','session_agenda_txt_column_event','Column Event','Event',42),(324,'text','session_agenda_txt_placeholder_search','Placeholder Search','Search',42),(330,'validation_text','session_agenda_notify_track','You need to have at least one track selected','You need to have at least one track selected',42),(331,'button','session_agenda_btn_prev','Prev Button','Prev',42),(332,'button','session_agenda_btn_next','Next Button','Next',42),(333,'text','session_agenda_txt_empty','Empty','Nothing to display',42),(334,'text','locationlist_txt_location_details','Location Details','Location Details',18),(335,'text','th_question_attendee_details','Attendee Details','Attendee Details',30),(336,'text','sessiondetails_txt_status_attending','Session Details Status Attending','Attending',34),(337,'text','sessiondetails_txt_status_in_queue','Session Details Status In Queue','In Queue',34),(338,'text','sessiondetails_txt_status_time_conflict','Session Details Status Time Conflict','Time Conflict',34),(339,'text','sessiondetails_txt_status_full','Session Details Status Full','Full',34),(340,'text','sessiondetails_txt_status_not_attending','Session Details Status Not Attending','Not Attending',34),(341,'text','sessiondetails_txt_status_deciding','Session Details Status Deciding','Deciding',34),(342,'text','sessiondetails_txt_status_rsvp_passed','RSVP deadline passed','RSVP deadline passed',34),(343,'text','sessiondetails_txt_status_queue_open','Queue Open','Queue Open',34),(344,'text','sessiondetails_txt_status_queue_close','Queue Close','Queue Close',34),(345,'text','economy_txt_currency','Currency','SEK',41),(346,'button','economy_btn_settle_order','Settle Order','Settle Order',41),(347,'button','economy_btn_change_order_status','Change order status','Change order status',41),(348,'text','economy_txt_attendee','Attendee text for group order','Attendee:',41),(349,'text','economy_txt_date_of_transaction','Date Of Transaction','Date Of Transaction',41),(350,'text','economy_txt_card_number','Card Number','Card Number',41),(351,'text','economy_txt_transaction_id','Transaction Id','Transaction Id',41),(352,'text','economy_txt_payment_information','Payment Information','Payment Information',41),(353,'text','economy_txt_amount_due','Amount Due in order table','Amount Due',41),(354,'text','economy_txt_order_table_costs','Costs in order table','Costs',41),(355,'text','economy_txt_balance_table_activities','Activities in balance table','Activities',41),(356,'text','economy_txt_order_table_total_vat','Total Vat','Total',41),(357,'text','economy_txt_grand_total_invoice','Economy Grand Total - Invoice','Grand Total',41),(358,'text','economy_txt_grand_total_credit_invoice','Economy Grand Total - Credit Invoice','Grand Total',41),(360,'text','attendee_list_txt_counting_column_header','Counting column header','Sl.',33),(361,'text','pdf_button_txt_misconfigured','Misconfigured','Pdf button settings are misconfigured.',43),(362,'text','attendee_logout_txt_button','Attendee Logout Button Text','Log out',44),(363,'text','hotelreservation_txt_cost_excl_vat','Cost Excluding VAT','Cost excl. VAT',22),(364,'text','hotelreservation_txt_cost_incl_vat','Cost Including VAT','Cost incl. VAT',22),(365,'text','hotelreservation_txt_vat_percentage','VAT %','VAT %',22),(366,'text','hotelreservation_txt_vat_amount','VAT Amount','VAT Amount',22),(367,'text','hotelreservation_txt_no_hotel_text','No hotel text','no hotel',22),(368,'text','hotelreservation_txt_max_buddy_selected','Max buddy selected text','You can only select {X} item',22),(369,'text','hotelreservation_txt_input_too_short','Input is too short in room-buddy textbox','Please enter 1 or more characters',22),(370,'notification','notify_session_expire','Session Expire Notification','You have been idle for too long and have been logged out. Click Okay to reload the page.',26),(371,'button','economy_invoice_download_button_next_settle_order','Economy Invoice Download Button Next to Settle Order Button','Download Invoice',41),(372,'button','economy_receipt_download_button_next_settle_order','Economy Receipt Download Button Next to Settle Order Button','Download Receipt',41),(373,'text','attendee_list_txt_total_attendee_count','Total Attendee Text','Total',33),(374,'notification','notify_title_notify','Notification Title Notify','Notification!',26),(375,'text','photo_gallery_image_details_text','Image details text','Image Details',37),(376,'text','economy_order_empty','Economy Orders Empty','You do not have an order associated with you or your order is handled by someone else.',41),(377,'text','economy_txt_rebate_with','Economy Rebate Text With','With',41),(378,'text','economy_txt_rebate_rebate','Economy Rebate Text Rebate','rebate',41),(379,'text','sessiondetails_txt_session_detail_link','Session Details Link','Read more',34),(380,'text','reset_password_txt_header','Resest password header','Retrieve Password',31),(381,'text','reset_password_txt_message','Resest password message','There are multiple instances of your email, please select one below',31),(382,'text','reset_password_txt_th_first_name','Resest password Column First name','First name',31),(383,'text','reset_password_txt_th_last_name','Resest password Column Last name','Last name',31),(384,'text','reset_password_txt_th_event','Resest password Column Event','Event',31),(385,'text','reset_password_txt_th_select','Resest password Column Select','Select',31),(386,'button','reset_password_btn_select_event','Resest password Select Event','Select',31);
/*!40000 ALTER TABLE `element_default_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `element_html`
--

DROP TABLE IF EXISTS `element_html`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `element_html` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `box_id` int(11) NOT NULL,
  `compiled` longtext COLLATE utf8_unicode_ci NOT NULL,
  `uncompiled` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `language_id` int(11) DEFAULT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `element_html_e93cb7eb` (`created_by_id`),
  KEY `element_html_468679bd` (`language_id`),
  KEY `element_html_1a63c800` (`page_id`),
  CONSTRAINT `element_html_created_by_id_73b4e69e5f32873b_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `element_html_language_id_59bf2c53fb13e659_fk_presets_id` FOREIGN KEY (`language_id`) REFERENCES `presets` (`id`),
  CONSTRAINT `element_html_page_id_52dadedcf4c3fbf0_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `element_html`
--

LOCK TABLES `element_html` WRITE;
/*!40000 ALTER TABLE `element_html` DISABLE KEYS */;
INSERT INTO `element_html` VALUES (1,4,'<h2>Welcome to Default Project</h2>','<h2>Welcome to Default Project</h2>','2018-11-22 14:00:59.957459','2018-11-22 14:00:59.957487',1,6,1),(2,4,'<h2>Welcome {first_name} {last_name}</h2>','<h2>Welcome {first_name} {last_name}</h2>','2018-11-22 14:01:27.512136','2018-11-22 14:01:27.512161',1,6,2),(3,4,'<h2>Sign In</h2>','<h2>Sign In</h2>','2018-11-22 14:01:54.740147','2018-11-22 14:01:54.740181',1,6,3),(4,4,'<h2>Request Login</h2>','<h2>Request Login</h2>','2018-11-22 14:02:37.303152','2018-11-22 14:02:37.303180',1,6,4),(5,4,'<h2>Reset Password</h2>','<h2>Reset Password</h2>','2018-11-22 14:03:23.110963','2018-11-22 14:03:23.110990',1,6,5),(6,4,'<h2>New Password</h2>','<h2>New Password</h2>','2018-11-22 14:04:10.449913','2018-11-22 14:04:10.449938',1,6,6),(7,4,'<h2>Messages</h2>','<h2>Messages</h2>','2018-11-22 14:04:52.603836','2018-11-22 14:04:52.603860',1,6,7),(8,4,'<h2>404</h2><h3 style=\"text-align: center;\">Page Not Found</h3>','<h2>404</h2><h3 style=\"text-align: center;\">Page Not Found</h3>','2018-11-22 14:07:04.340180','2018-11-22 14:07:04.340203',1,6,11),(9,4,'<h2>403</h2><h3 style=\"text-align: center;\">Not Authorized</h3>','<h2>403</h2><h3 style=\"text-align: center;\">Not Authorized</h3>','2018-11-22 14:08:05.110288','2018-11-22 14:08:05.110317',1,6,12),(10,4,'<h2>403</h2><h3 style=\"text-align: center;\">Not Authorized</h3>','<h2>403</h2><h3 style=\"text-align: center;\">Not Authorized</h3>','2018-11-22 14:08:32.250800','2018-11-22 14:08:32.250823',1,6,13),(12,4,'<h2>Photo Upload</h2>','<h2>Photo Upload</h2>','2018-11-30 09:50:19.849863','2018-11-30 09:50:19.849883',1,6,28),(13,5,'<h2>Gallery</h2>','<h2>Gallery</h2>','2018-11-30 09:50:32.871007','2018-11-30 09:50:32.871027',1,6,28),(14,4,'<h2>Session Agenda</h2>','<h2>Session Agenda</h2>','2018-11-30 09:53:28.261036','2018-11-30 09:53:28.261059',1,6,29),(15,4,'<h2>Hotel Reservation</h2>','<h2>Hotel Reservation</h2>','2018-11-30 09:59:05.991440','2018-11-30 09:59:05.991458',1,6,30),(16,5,'<h2>Locations</h2>','<h2>Locations</h2>','2018-11-30 10:12:17.699099','2018-11-30 10:12:17.699124',1,6,33),(17,4,'<h2>Registration</h2>','<h2>Registration</h2>','2018-11-30 10:15:05.051340','2018-11-30 10:15:05.051375',1,6,34);
/*!40000 ALTER TABLE `element_html` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `element_preset_lang`
--

DROP TABLE IF EXISTS `element_preset_lang`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `element_preset_lang` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `value` longtext COLLATE utf8_unicode_ci NOT NULL,
  `element_default_lang_id` int(11) NOT NULL,
  `preset_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `f11edaeb4efbb92eb5be980c9c1351f6` (`element_default_lang_id`),
  KEY `element_preset_lang_cf933d7f` (`preset_id`),
  CONSTRAINT `element_preset_lang_preset_id_7e4a541db007a726_fk_presets_id` FOREIGN KEY (`preset_id`) REFERENCES `presets` (`id`),
  CONSTRAINT `f11edaeb4efbb92eb5be980c9c1351f6` FOREIGN KEY (`element_default_lang_id`) REFERENCES `element_default_lang` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=611 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `element_preset_lang`
--

LOCK TABLES `element_preset_lang` WRITE;
/*!40000 ALTER TABLE `element_preset_lang` DISABLE KEYS */;
INSERT INTO `element_preset_lang` VALUES (1,'You have a clash with previously selected session',1,6),(2,'You are registered for this session',2,6),(3,'You are in Queue for this session',3,6),(4,'You have unregistered for this session',4,6),(5,'This sessions Capacity Full',5,6),(6,'Evaluation',6,6),(7,'Send Evaluation',7,6),(8,'All session are successfully rated.',8,6),(9,'Messages',9,6),(10,'Read Archived message',10,6),(11,'Mark all as read',11,6),(12,'All message read successfully',12,6),(13,'message archived successfully',13,6),(14,'Next up',14,6),(15,'Location list',15,6),(16,'Map to location',16,6),(17,'address',17,6),(18,'contact',18,6),(19,'Session Radio button',19,6),(20,'Session Checkbox',28,6),(21,'Session Status',59,6),(22,'Check-in',60,6),(23,'Check-out',61,6),(24,'Name',62,6),(25,'Description',63,6),(26,'Location',64,6),(27,'Room buddy',65,6),(28,'Add a stay',66,6),(29,'Remove a stay',67,6),(30,'Hotel name',68,6),(31,'Room Description',69,6),(32,'Beds',70,6),(33,'Check-out',71,6),(34,'Check-in',72,6),(35,'Requested room buddy',73,6),(36,'Actual room buddy',74,6),(37,'Location',75,6),(38,'Session',76,6),(39,'Group',77,6),(40,'Description',78,6),(41,'Start',79,6),(42,'End',80,6),(43,'Location',81,6),(44,'Speakers',82,6),(45,'Tags',83,6),(46,'Status',84,6),(47,'Travel name',85,6),(48,'Group',86,6),(49,'Departure city',87,6),(50,'Arrival city',88,6),(51,'Departure time & date',89,6),(52,'Arrival time & date',90,6),(53,'Location',91,6),(54,'Description',92,6),(55,'Question',93,6),(56,'Answer',94,6),(57,'Registration date',95,6),(58,'Last update date',96,6),(59,'Attendee groups',97,6),(60,'Tags',98,6),(61,'Your email address',99,6),(62,'Request',100,6),(63,'Validation failed',101,6),(64,'Email address',102,6),(65,'Password',103,6),(66,'Forgotten your password?',104,6),(67,'Login',105,6),(68,'Validation failed',106,6),(69,'Validation failed',107,6),(70,'Validation failed',108,6),(71,'Group',109,6),(72,'You have a new session to evaluate',110,6),(73,'Session {session_name} will be start on {remain_time} minutes',111,6),(74,'A seat has become available to an activity you\"re queueing for but has a time conflict with your previous choice. Would you like to switch to <strong>{session1}</strong> or keep your current choice <strong>{session2}</strong>?',112,6),(75,'The session <strong>{session}</strong> has been added to your agenda.',113,6),(76,'Organizer',114,6),(77,'Session Conflict',115,6),(78,'Switch',116,6),(79,'Keep',117,6),(80,'If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.',118,6),(81,'You have new Notification',119,6),(82,'Session {session_name} is already started',120,6),(83,'Login Successfull',121,6),(84,'Submit Successfull',122,6),(85,'An Error occurred ',123,6),(86,'An Email sent to you with activation url',124,6),(87,'Email address',125,6),(88,'Send reset instructions',126,6),(89,'Validation failed',127,6),(90,'New password',128,6),(91,'Repeat new password',129,6),(92,'Change password',130,6),(93,'Validation failed',131,6),(94,'Attendee Registration Successfully',132,6),(95,'Email already exists',133,6),(96,'Something went wrong {error}',134,6),(97,'Password Changed Successfully',135,6),(98,'An recovery email has been sent to email',136,6),(99,'Attendee list intro',137,6),(100,'Download spreadsheet',138,6),(101,'Spreadsheet Downloaded',139,6),(102,'Session Details',140,6),(103,'Attending',141,6),(104,'starts',142,6),(105,'ends',143,6),(106,'Rsvp',144,6),(107,'Speakers',145,6),(108,'Tags',146,6),(109,'Session Group',147,6),(110,'Seats Availability',148,6),(111,'Location',149,6),(112,'Evaluation is Empty',155,6),(113,'Message is Empty',156,6),(114,'Next up is Empty',157,6),(115,'Search',158,6),(116,'Search',159,6),(117,'Success!',160,6),(118,'Warning!',161,6),(119,'Error!',162,6),(120,'Good',163,6),(121,'{X} of {Y} seats available',164,6),(122,'seats available',165,6),(123,'No seats available',166,6),(124,'Few seats available',167,6),(125,'queue is open',168,6),(126,'Select a room buddy',169,6),(127,'Your request is processing, file will be download within few moment',170,6),(128,'{X} - {Y} of {Z} items',171,6),(129,'Archived Messages',172,6),(130,'Organizer',173,6),(131,'Message is Empty',174,6),(132,'This sessions Capacity Full and Queue is not Open',175,6),(133,'You Have Already Attend in this Session',176,6),(134,'You Have Already in Queue in this Session',177,6),(135,'This Session Is not Available',178,6),(136,'Session Conflict',184,6),(137,'Yes',185,6),(138,'No',186,6),(139,'If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.',187,6),(140,'Location is Empty',188,6),(141,'Session radio is Empty',189,6),(142,'Session checkbox is Empty',190,6),(143,'Evaluation settings are misconfigured.',191,6),(144,'Message settings are misconfigured.',192,6),(145,'Next Up settings are misconfigured.',193,6),(146,'Location settings are misconfigured.',194,6),(147,'Session radio settings are misconfigured.',195,6),(148,'Session checkbox settings are misconfigured.',196,6),(149,'Hotel reservation settings are misconfigured.',198,6),(150,'Login form settings are misconfigured.',199,6),(151,'Submit button settings are misconfigured.',200,6),(152,'Request login settings are misconfigured.',201,6),(153,'Reset password settings are misconfigured.',202,6),(154,'New password settings are misconfigured.',203,6),(155,'Attendee list settings are misconfigured.',204,6),(156,'Hotel reservation is Empty',205,6),(157,'Attendee list is Empty',206,6),(158,'Comment',207,6),(159,'add comment',208,6),(160,'Upload Photo',209,6),(161,'Photo Uploaded Successfully',210,6),(162,'The image you are trying to upload is too large.',211,6),(163,'The image you are trying to upload is too small.',212,6),(164,'Something went wrong. Please try again.',213,6),(165,'Photo Upload settings are misconfigured.',214,6),(166,'Photo Gallery settings are misconfigured.',215,6),(167,'Select a room buddy',216,6),(168,'No data found',217,6),(169,'Fix date',218,6),(170,'Match previous date',219,6),(171,'Require room selection',220,6),(172,'Require room buddy',221,6),(173,'Max stay reached',222,6),(174,'Date clash',223,6),(175,'Date is not set',224,6),(176,'Please select your {question}',225,6),(177,'Upload',226,6),(178,'Filename:',227,6),(179,'Select',228,6),(180,'Showing {X} to {Y} of {Z} photos',229,6),(181,'You\'ve been logged out. Click here to go to the start page',230,6),(182,'Go To Start Page',231,6),(183,'Comment',232,6),(184,'Uploader',233,6),(185,'No Photo exist',234,6),(186,'Previous',235,6),(187,'Next',236,6),(188,'Room is not available.',237,6),(189,'Attendee Updated Successfully.',238,6),(190,'Attendee Update Failed.',239,6),(191,'Message Archive failed',240,6),(192,'Session rated failed.',241,6),(193,'Validation failed',242,6),(194,'Test',243,6),(195,'Current number of attendees',244,6),(196,'Edit',245,6),(197,'Delete',246,6),(198,'Not yet registered',247,6),(199,'Add an attendee',248,6),(200,'Multiple registration settings are Misconfigured',249,6),(201,'Validation failed',250,6),(202,'Your temporary session has been expired.',251,6),(203,'Something Went wrong. Please try again',252,6),(204,'All attendee Register successfully',253,6),(205,'Attendee group',254,6),(206,'Actions',255,6),(207,'Order Owner',256,6),(208,'Attendee',257,6),(209,'Cost',258,6),(210,'(excl. vat {X})',259,6),(211,'(incl. vat {X})',260,6),(212,'Order Table',270,6),(213,'Order Number',271,6),(214,'Status',272,6),(215,'Due',273,6),(216,'Cost excl. VAT',274,6),(217,'Cost incl. VAT',275,6),(218,'Rebate Amount',276,6),(219,'Amount',277,6),(220,'VAT',278,6),(221,'Amount',279,6),(222,'Grand Total',280,6),(223,'Balance Table',281,6),(224,'Date & time',282,6),(225,'Link to Invoice / Receipt',283,6),(226,'Download',284,6),(227,'Invoice created',285,6),(228,'Invoice settled',286,6),(229,'Credit invoice',287,6),(230,'Order balance',288,6),(231,'Economy settings are Misconfigured',289,6),(232,'Validation failed',290,6),(233,'Open',291,6),(234,'Pending',292,6),(235,'Open',293,6),(236,'Cancelled',294,6),(237,'Place Order',295,6),(238,'Economy settings are Empty',296,6),(239,'Order status is changed Open to Pending successfully',297,6),(240,'Session Agenda',298,6),(241,'Show my sessions only',299,6),(242,'Today',310,6),(243,'Subscribe to my sessions',311,6),(244,'Session Agenda settings are misconfigured.',319,6),(245,'Session Group',320,6),(246,'Date',321,6),(247,'Time',322,6),(248,'Event',323,6),(249,'Search',324,6),(250,'You need to have at least one track selected',330,6),(251,'Prev',331,6),(252,'Next',332,6),(253,'Nothing to display',333,6),(254,'Location Details',334,6),(255,'Attendee Details',335,6),(256,'Attending',336,6),(257,'In Queue',337,6),(258,'Time Conflict',338,6),(259,'Full',339,6),(260,'Not Attending',340,6),(261,'Deciding',341,6),(262,'RSVP deadline passed',342,6),(263,'Queue Open',343,6),(264,'Queue Close',344,6),(265,'SEK',345,6),(266,'Settle Order',346,6),(267,'Change order status',347,6),(268,'Attendee:',348,6),(269,'Date Of Transaction',349,6),(270,'Card Number',350,6),(271,'Transaction Id',351,6),(272,'Payment Information',352,6),(273,'Amount Due',353,6),(274,'Costs',354,6),(275,'Activities',355,6),(276,'Total',356,6),(277,'Grand Total',357,6),(278,'Grand Total',358,6),(279,'Sl.',360,6),(280,'Pdf button settings are misconfigured.',361,6),(281,'Log out',362,6),(282,'Cost excl. VAT',363,6),(283,'Cost incl. VAT',364,6),(284,'VAT %',365,6),(285,'VAT Amount',366,6),(286,'no hotel',367,6),(287,'You can only select {X} item',368,6),(288,'Please enter 1 or more characters',369,6),(289,'You have been idle for too long and have been logged out. Click Okay to reload the page.',370,6),(290,'Download Invoice',371,6),(291,'Download Receipt',372,6),(292,'Total',373,6),(293,'Notification!',374,6),(294,'Image Details',375,6),(295,'You do not have an order associated with you or your order is handled by someone else.',376,6),(296,'With',377,6),(297,'rebate',378,6),(298,'Read more',379,6),(299,'Retrieve Password',380,6),(300,'There are multiple instances of your email, please select one below',381,6),(301,'First name',382,6),(302,'Last name',383,6),(303,'Event',384,6),(304,'Select',385,6),(305,'Select',386,6),(306,'You have a clash with previously selected session',1,7),(307,'You are registered for this session',2,7),(308,'You are in Queue for this session',3,7),(309,'You have unregistered for this session',4,7),(310,'This sessions Capacity Full',5,7),(311,'Evaluation',6,7),(312,'Send Evaluation',7,7),(313,'All session are successfully rated.',8,7),(314,'Messages',9,7),(315,'Read Archived message',10,7),(316,'Mark all as read',11,7),(317,'All message read successfully',12,7),(318,'message archived successfully',13,7),(319,'Next up',14,7),(320,'Location list',15,7),(321,'Map to location',16,7),(322,'address',17,7),(323,'contact',18,7),(324,'Session Radio button',19,7),(325,'Session Checkbox',28,7),(326,'Session Status',59,7),(327,'Check-in',60,7),(328,'Check-out',61,7),(329,'Name',62,7),(330,'Description',63,7),(331,'Location',64,7),(332,'Room buddy',65,7),(333,'Add a stay',66,7),(334,'Remove a stay',67,7),(335,'Hotel name',68,7),(336,'Room Description',69,7),(337,'Beds',70,7),(338,'Check-out',71,7),(339,'Check-in',72,7),(340,'Requested room buddy',73,7),(341,'Actual room buddy',74,7),(342,'Location',75,7),(343,'Session',76,7),(344,'Group',77,7),(345,'Description',78,7),(346,'Start',79,7),(347,'End',80,7),(348,'Location',81,7),(349,'Speakers',82,7),(350,'Tags',83,7),(351,'Status',84,7),(352,'Travel name',85,7),(353,'Group',86,7),(354,'Departure city',87,7),(355,'Arrival city',88,7),(356,'Departure time & date',89,7),(357,'Arrival time & date',90,7),(358,'Location',91,7),(359,'Description',92,7),(360,'Question',93,7),(361,'Answer',94,7),(362,'Registration date',95,7),(363,'Last update date',96,7),(364,'Attendee groups',97,7),(365,'Tags',98,7),(366,'Your email address',99,7),(367,'Request',100,7),(368,'Validation failed',101,7),(369,'Email address',102,7),(370,'Password',103,7),(371,'Forgotten your password?',104,7),(372,'Login',105,7),(373,'Validation failed',106,7),(374,'Validation failed',107,7),(375,'Validation failed',108,7),(376,'Group',109,7),(377,'You have a new session to evaluate',110,7),(378,'Session {session_name} will be start on {remain_time} minutes',111,7),(379,'A seat has become available to an activity you\"re queueing for but has a time conflict with your previous choice. Would you like to switch to <strong>{session1}</strong> or keep your current choice <strong>{session2}</strong>?',112,7),(380,'The session <strong>{session}</strong> has been added to your agenda.',113,7),(381,'Organizer',114,7),(382,'Session Conflict',115,7),(383,'Switch',116,7),(384,'Keep',117,7),(385,'If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.',118,7),(386,'You have new Notification',119,7),(387,'Session {session_name} is already started',120,7),(388,'Login Successfull',121,7),(389,'Submit Successfull',122,7),(390,'An Error occurred ',123,7),(391,'An Email sent to you with activation url',124,7),(392,'Email address',125,7),(393,'Send reset instructions',126,7),(394,'Validation failed',127,7),(395,'New password',128,7),(396,'Repeat new password',129,7),(397,'Change password',130,7),(398,'Validation failed',131,7),(399,'Attendee Registration Successfully',132,7),(400,'Email already exists',133,7),(401,'Something went wrong {error}',134,7),(402,'Password Changed Successfully',135,7),(403,'An recovery email has been sent to email',136,7),(404,'Attendee list intro',137,7),(405,'Download spreadsheet',138,7),(406,'Spreadsheet Downloaded',139,7),(407,'Session Details',140,7),(408,'Attending',141,7),(409,'starts',142,7),(410,'ends',143,7),(411,'Rsvp',144,7),(412,'Speakers',145,7),(413,'Tags',146,7),(414,'Session Group',147,7),(415,'Seats Availability',148,7),(416,'Location',149,7),(417,'Evaluation is Empty',155,7),(418,'Message is Empty',156,7),(419,'Next up is Empty',157,7),(420,'Search',158,7),(421,'Search',159,7),(422,'Success!',160,7),(423,'Warning!',161,7),(424,'Error!',162,7),(425,'Good',163,7),(426,'{X} of {Y} seats available',164,7),(427,'seats available',165,7),(428,'No seats available',166,7),(429,'Few seats available',167,7),(430,'queue is open',168,7),(431,'Select a room buddy',169,7),(432,'Your request is processing, file will be download within few moment',170,7),(433,'{X} - {Y} of {Z} items',171,7),(434,'Archived Messages',172,7),(435,'Organizer',173,7),(436,'Message is Empty',174,7),(437,'This sessions Capacity Full and Queue is not Open',175,7),(438,'You Have Already Attend in this Session',176,7),(439,'You Have Already in Queue in this Session',177,7),(440,'This Session Is not Available',178,7),(441,'Session Conflict',184,7),(442,'Yes',185,7),(443,'No',186,7),(444,'If no answer is received within the next {countdown} the seat is given to the next attendee in Queue.',187,7),(445,'Location is Empty',188,7),(446,'Session radio is Empty',189,7),(447,'Session checkbox is Empty',190,7),(448,'Evaluation settings are misconfigured.',191,7),(449,'Message settings are misconfigured.',192,7),(450,'Next Up settings are misconfigured.',193,7),(451,'Location settings are misconfigured.',194,7),(452,'Session radio settings are misconfigured.',195,7),(453,'Session checkbox settings are misconfigured.',196,7),(454,'Hotel reservation settings are misconfigured.',198,7),(455,'Login form settings are misconfigured.',199,7),(456,'Submit button settings are misconfigured.',200,7),(457,'Request login settings are misconfigured.',201,7),(458,'Reset password settings are misconfigured.',202,7),(459,'New password settings are misconfigured.',203,7),(460,'Attendee list settings are misconfigured.',204,7),(461,'Hotel reservation is Empty',205,7),(462,'Attendee list is Empty',206,7),(463,'Comment',207,7),(464,'add comment',208,7),(465,'Upload Photo',209,7),(466,'Photo Uploaded Successfully',210,7),(467,'The image you are trying to upload is too large.',211,7),(468,'The image you are trying to upload is too small.',212,7),(469,'Something went wrong. Please try again.',213,7),(470,'Photo Upload settings are misconfigured.',214,7),(471,'Photo Gallery settings are misconfigured.',215,7),(472,'Select a room buddy',216,7),(473,'No data found',217,7),(474,'Fix date',218,7),(475,'Match previous date',219,7),(476,'Require room selection',220,7),(477,'Require room buddy',221,7),(478,'Max stay reached',222,7),(479,'Date clash',223,7),(480,'Date is not set',224,7),(481,'Please select your {question}',225,7),(482,'Upload',226,7),(483,'Filename:',227,7),(484,'Select',228,7),(485,'Showing {X} to {Y} of {Z} photos',229,7),(486,'You\'ve been logged out. Click here to go to the start page',230,7),(487,'Go To Start Page',231,7),(488,'Comment',232,7),(489,'Uploader',233,7),(490,'No Photo exist',234,7),(491,'Previous',235,7),(492,'Next',236,7),(493,'Room is not available.',237,7),(494,'Attendee Updated Successfully.',238,7),(495,'Attendee Update Failed.',239,7),(496,'Message Archive failed',240,7),(497,'Session rated failed.',241,7),(498,'Validation failed',242,7),(499,'Test',243,7),(500,'Current number of attendees',244,7),(501,'Edit',245,7),(502,'Delete',246,7),(503,'Not yet registered',247,7),(504,'Add an attendee',248,7),(505,'Multiple registration settings are Misconfigured',249,7),(506,'Validation failed',250,7),(507,'Your temporary session has been expired.',251,7),(508,'Something Went wrong. Please try again',252,7),(509,'All attendee Register successfully',253,7),(510,'Attendee group',254,7),(511,'Actions',255,7),(512,'Order Owner',256,7),(513,'Attendee',257,7),(514,'Cost',258,7),(515,'(excl. vat {X})',259,7),(516,'(incl. vat {X})',260,7),(517,'Order Table',270,7),(518,'Order Number',271,7),(519,'Status',272,7),(520,'Due',273,7),(521,'Cost excl. VAT',274,7),(522,'Cost incl. VAT',275,7),(523,'Rebate Amount',276,7),(524,'Amount',277,7),(525,'VAT',278,7),(526,'Amount',279,7),(527,'Grand Total',280,7),(528,'Balance Table',281,7),(529,'Date & time',282,7),(530,'Link to Invoice / Receipt',283,7),(531,'Download',284,7),(532,'Invoice created',285,7),(533,'Invoice settled',286,7),(534,'Credit invoice',287,7),(535,'Order balance',288,7),(536,'Economy settings are Misconfigured',289,7),(537,'Validation failed',290,7),(538,'Open',291,7),(539,'Pending',292,7),(540,'Open',293,7),(541,'Cancelled',294,7),(542,'Place Order',295,7),(543,'Economy settings are Empty',296,7),(544,'Order status is changed Open to Pending successfully',297,7),(545,'Session Agenda',298,7),(546,'Show my sessions only',299,7),(547,'Today',310,7),(548,'Subscribe to my sessions',311,7),(549,'Session Agenda settings are misconfigured.',319,7),(550,'Session Group',320,7),(551,'Date',321,7),(552,'Time',322,7),(553,'Event',323,7),(554,'Search',324,7),(555,'You need to have at least one track selected',330,7),(556,'Prev',331,7),(557,'Next',332,7),(558,'Nothing to display',333,7),(559,'Location Details',334,7),(560,'Attendee Details',335,7),(561,'Attending',336,7),(562,'In Queue',337,7),(563,'Time Conflict',338,7),(564,'Full',339,7),(565,'Not Attending',340,7),(566,'Deciding',341,7),(567,'RSVP deadline passed',342,7),(568,'Queue Open',343,7),(569,'Queue Close',344,7),(570,'SEK',345,7),(571,'Settle Order',346,7),(572,'Change order status',347,7),(573,'Attendee:',348,7),(574,'Date Of Transaction',349,7),(575,'Card Number',350,7),(576,'Transaction Id',351,7),(577,'Payment Information',352,7),(578,'Amount Due',353,7),(579,'Costs',354,7),(580,'Activities',355,7),(581,'Total',356,7),(582,'Grand Total',357,7),(583,'Grand Total',358,7),(584,'Sl.',360,7),(585,'Pdf button settings are misconfigured.',361,7),(586,'Log out',362,7),(587,'Cost excl. VAT',363,7),(588,'Cost incl. VAT',364,7),(589,'VAT %',365,7),(590,'VAT Amount',366,7),(591,'no hotel',367,7),(592,'You can only select {X} item',368,7),(593,'Please enter 1 or more characters',369,7),(594,'You have been idle for too long and have been logged out. Click Okay to reload the page.',370,7),(595,'Download Invoice',371,7),(596,'Download Receipt',372,7),(597,'Total',373,7),(598,'Notification!',374,7),(599,'Image Details',375,7),(600,'You do not have an order associated with you or your order is handled by someone else.',376,7),(601,'With',377,7),(602,'rebate',378,7),(603,'Read more',379,7),(604,'Retrieve Password',380,7),(605,'There are multiple instances of your email, please select one below',381,7),(606,'First name',382,7),(607,'Last name',383,7),(608,'Event',384,7),(609,'Select',385,7),(610,'Select',386,7);
/*!40000 ALTER TABLE `element_preset_lang` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elements`
--

DROP TABLE IF EXISTS `elements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `elements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `slug` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `type` enum('plugin','public_notification','default_plugin') COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `elements_e93cb7eb` (`created_by_id`),
  KEY `elements_49fa5cc1` (`last_updated_by_id`),
  CONSTRAINT `elements_created_by_id_1a16ea69686b75cb_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `elements_last_updated_by_id_1f9ee0b297317257_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elements`
--

LOCK TABLES `elements` WRITE;
/*!40000 ALTER TABLE `elements` DISABLE KEYS */;
INSERT INTO `elements` VALUES (15,'Evaluations','evaluations','plugin','2016-07-21 00:00:00.000000','2016-07-21 00:00:00.000000',1,1),(16,'Messages','messages','plugin','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000',1,1),(17,'Next-Up','next-up','plugin','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000',1,1),(18,'Location-list','location-list','plugin','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000',1,1),(19,'Session-radio-button','session-radio-button','plugin','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000',1,1),(20,'Session-checkbox','session-checkbox','plugin','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000',1,1),(22,'Hotel Reservation','hotel-reservation','plugin','2016-09-15 00:00:00.000000','2016-09-08 00:00:00.000000',1,1),(23,'Login Form','login-form','plugin','2016-09-27 00:00:00.000000','2016-09-27 00:00:00.000000',1,1),(24,'Submit Button','submit-button','plugin','2016-09-26 00:00:00.000000','2016-09-26 00:00:00.000000',1,1),(25,'Request-Login','request-login','plugin','2016-09-26 00:00:00.000000','2016-09-26 00:00:00.000000',1,1),(26,'Notification','notification','public_notification','2016-09-15 00:00:00.000000','2016-09-08 00:00:00.000000',1,1),(27,'Hotels','hotels','public_notification','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(28,'Travels','travels','public_notification','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(29,'Sessions','sessions','public_notification','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(30,'Questions','questions','public_notification','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(31,'Reset Password','reset-password','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(32,'New Password','new-password','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(33,'Attendee List','attendee-list','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(34,'Session Details','session-details','default_plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(35,'Archive Messages','archive-messages','default_plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(36,'Photo Upload','photo-upload','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(37,'Photo Gallery','photo-gallery','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(38,'Logout','logout','default_plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(39,'Multiple Registration','multiple-registration','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(40,'Rebate','rebate','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(41,'Economy','economy','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(42,'Session Agenda','session-agenda','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(43,'PDF Button','pdf-button','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1),(44,'Log Out','log-out','plugin','2016-10-31 11:00:00.000000','2016-10-31 11:00:00.000000',1,1);
/*!40000 ALTER TABLE `elements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elements_answers`
--

DROP TABLE IF EXISTS `elements_answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `elements_answers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `answer` longtext COLLATE utf8_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8_unicode_ci NOT NULL,
  `box_id` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `element_question_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `elements_answers_e93cb7eb` (`created_by_id`),
  KEY `elements_answers_aeb6aad9` (`element_question_id`),
  KEY `elements_answers_49fa5cc1` (`last_updated_by_id`),
  KEY `elements_answers_1a63c800` (`page_id`),
  CONSTRAINT `el_element_question_id_77d2ce32f1e1421d_fk_elements_questions_id` FOREIGN KEY (`element_question_id`) REFERENCES `elements_questions` (`id`),
  CONSTRAINT `elements_answers_created_by_id_55e0049e16a47587_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `elements_answers_last_updated_by_id_7aab865b0ab31aa5_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `elements_answers_page_id_5d7c2ab5ccc5d376_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=282 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elements_answers`
--

LOCK TABLES `elements_answers` WRITE;
/*!40000 ALTER TABLE `elements_answers` DISABLE KEYS */;
INSERT INTO `elements_answers` VALUES (1,'True','',5,'2018-11-22 14:02:19.374149','2018-11-22 14:02:19.374185',1,68,1,3),(2,'2','',5,'2018-11-22 14:03:06.524653','2018-11-22 14:03:06.524677',1,73,1,4),(3,'3','',5,'2018-11-22 14:03:57.104235','2018-11-22 14:03:57.104277',1,78,1,5),(4,'{\"6\": \"Submit\"}','',11,'2018-11-30 09:39:29.713526','2018-11-30 09:39:29.713550',1,69,1,27),(5,'registration-button','',11,'2018-11-30 09:39:29.783636','2018-11-30 09:39:29.783697',1,70,1,27),(6,'','',11,'2018-11-30 09:39:29.901339','2018-11-30 09:39:29.901360',1,366,1,27),(7,'False','',11,'2018-11-30 09:39:30.093208','2018-11-30 09:39:30.093230',1,372,1,27),(8,'False','',11,'2018-11-30 09:39:30.143037','2018-11-30 09:39:30.143059',1,208,1,27),(9,'False','',11,'2018-11-30 09:39:30.193163','2018-11-30 09:39:30.193184',1,222,1,27),(10,'False','',11,'2018-11-30 09:39:30.243263','2018-11-30 09:39:30.243285',1,298,1,27),(11,'[{\"state\":1,\"data\":\"\"}]','',11,'2018-11-30 09:39:30.293602','2018-11-30 09:39:30.293626',1,74,1,27),(12,'[{\"state\":1,\"data\":\"\"}]','',11,'2018-11-30 09:39:30.343825','2018-11-30 09:39:30.343850',1,371,1,27),(13,'[{\"state\":1,\"data\":\"\"}]','',11,'2018-11-30 09:39:30.393407','2018-11-30 09:39:30.393429',1,75,1,27),(14,'True','',12,'2018-11-30 09:49:33.916127','2018-11-30 09:49:33.916151',1,31,1,27),(15,'True','',12,'2018-11-30 09:49:33.972420','2018-11-30 09:49:33.972442',1,33,1,27),(16,'True','',12,'2018-11-30 09:49:34.022843','2018-11-30 09:49:34.022865',1,308,1,27),(17,'True','',12,'2018-11-30 09:49:34.122879','2018-11-30 09:49:34.122902',1,34,1,27),(18,'True','',12,'2018-11-30 09:49:34.222845','2018-11-30 09:49:34.222868',1,35,1,27),(19,'True','',12,'2018-11-30 09:49:34.273066','2018-11-30 09:49:34.273089',1,36,1,27),(20,'True','',12,'2018-11-30 09:49:34.322919','2018-11-30 09:49:34.322942',1,37,1,27),(21,'True','',12,'2018-11-30 09:49:34.373133','2018-11-30 09:49:34.373156',1,38,1,27),(22,'True','',12,'2018-11-30 09:49:34.422660','2018-11-30 09:49:34.422680',1,39,1,27),(23,'True','',12,'2018-11-30 09:49:34.473170','2018-11-30 09:49:34.473192',1,223,1,27),(24,'True','',12,'2018-11-30 09:49:34.522723','2018-11-30 09:49:34.522742',1,224,1,27),(25,'True','',12,'2018-11-30 09:49:34.573488','2018-11-30 09:49:34.573513',1,40,1,27),(26,'True','',12,'2018-11-30 09:49:34.623563','2018-11-30 09:49:34.623597',1,41,1,27),(27,'True','',12,'2018-11-30 09:49:34.674642','2018-11-30 09:49:34.674675',1,42,1,27),(28,'True','',12,'2018-11-30 09:49:34.724327','2018-11-30 09:49:34.724352',1,43,1,27),(29,'True','',12,'2018-11-30 09:49:34.773655','2018-11-30 09:49:34.773677',1,44,1,27),(30,'True','',12,'2018-11-30 09:49:34.823996','2018-11-30 09:49:34.824019',1,45,1,27),(31,'True','',12,'2018-11-30 09:49:34.873534','2018-11-30 09:49:34.873553',1,307,1,27),(32,'True','',12,'2018-11-30 09:49:34.923685','2018-11-30 09:49:34.923708',1,310,1,27),(33,'True','',12,'2018-11-30 09:49:34.974064','2018-11-30 09:49:34.974087',1,311,1,27),(34,'True','',12,'2018-11-30 09:49:35.058201','2018-11-30 09:49:35.058224',1,312,1,27),(35,'True','',12,'2018-11-30 09:49:35.109642','2018-11-30 09:49:35.109674',1,313,1,27),(36,'True','',12,'2018-11-30 09:49:35.157303','2018-11-30 09:49:35.157326',1,314,1,27),(37,'True','',12,'2018-11-30 09:49:35.207454','2018-11-30 09:49:35.207477',1,315,1,27),(38,'True','',12,'2018-11-30 09:49:35.257569','2018-11-30 09:49:35.257594',1,322,1,27),(39,'True','',12,'2018-11-30 09:49:35.307242','2018-11-30 09:49:35.307263',1,323,1,27),(40,'True','',12,'2018-11-30 09:49:35.357670','2018-11-30 09:49:35.357691',1,316,1,27),(41,'True','',12,'2018-11-30 09:49:35.407308','2018-11-30 09:49:35.407347',1,317,1,27),(42,'True','',12,'2018-11-30 09:49:35.458430','2018-11-30 09:49:35.458452',1,318,1,27),(43,'True','',12,'2018-11-30 09:49:35.507783','2018-11-30 09:49:35.507806',1,319,1,27),(44,'True','',12,'2018-11-30 09:49:35.557792','2018-11-30 09:49:35.557820',1,320,1,27),(45,'True','',12,'2018-11-30 09:49:35.607439','2018-11-30 09:49:35.607460',1,321,1,27),(46,'False','',12,'2018-11-30 09:49:35.657908','2018-11-30 09:49:35.657930',1,172,1,27),(47,'False','',12,'2018-11-30 09:49:35.708133','2018-11-30 09:49:35.708157',1,151,1,27),(48,'True','',12,'2018-11-30 09:49:35.758375','2018-11-30 09:49:35.758400',1,152,1,27),(49,'True','',12,'2018-11-30 09:49:35.808321','2018-11-30 09:49:35.808345',1,153,1,27),(50,'True','',12,'2018-11-30 09:49:35.857961','2018-11-30 09:49:35.857982',1,154,1,27),(51,'True','',12,'2018-11-30 09:49:35.908579','2018-11-30 09:49:35.908604',1,155,1,27),(52,'True','',12,'2018-11-30 09:49:35.957979','2018-11-30 09:49:35.957999',1,156,1,27),(53,'True','',12,'2018-11-30 09:49:36.008390','2018-11-30 09:49:36.008412',1,157,1,27),(54,'x','',12,'2018-11-30 09:49:36.058196','2018-11-30 09:49:36.058216',1,46,1,27),(55,'','',12,'2018-11-30 09:49:36.108902','2018-11-30 09:49:36.108927',1,81,1,27),(56,'\"{\\\"question\\\":[{\\\"id\\\":\\\"\\\"}]}\"','',12,'2018-11-30 09:49:36.159873','2018-11-30 09:49:36.159963',1,173,1,27),(57,'[\"6\"]','',12,'2018-11-30 09:49:36.208852','2018-11-30 09:49:36.208875',1,32,1,27),(58,'True','',13,'2018-11-30 09:50:01.148668','2018-11-30 09:50:01.148692',1,49,1,27),(59,'False','',13,'2018-11-30 09:50:01.210198','2018-11-30 09:50:01.210222',1,368,1,27),(60,'0','',13,'2018-11-30 09:50:01.268005','2018-11-30 09:50:01.268027',1,51,1,27),(61,'0','',13,'2018-11-30 09:50:01.325693','2018-11-30 09:50:01.325714',1,52,1,27),(62,'True','',13,'2018-11-30 09:50:01.384582','2018-11-30 09:50:01.384604',1,367,1,27),(63,'True','',13,'2018-11-30 09:50:01.443295','2018-11-30 09:50:01.443317',1,369,1,27),(64,'True','',13,'2018-11-30 09:50:01.501226','2018-11-30 09:50:01.501249',1,325,1,27),(65,'True','',13,'2018-11-30 09:50:01.559836','2018-11-30 09:50:01.559859',1,53,1,27),(66,'True','',13,'2018-11-30 09:50:01.676814','2018-11-30 09:50:01.676836',1,54,1,27),(67,'True','',13,'2018-11-30 09:50:01.793252','2018-11-30 09:50:01.793275',1,55,1,27),(68,'True','',13,'2018-11-30 09:50:01.851763','2018-11-30 09:50:01.851785',1,56,1,27),(69,'True','',13,'2018-11-30 09:50:01.910243','2018-11-30 09:50:01.910265',1,57,1,27),(70,'True','',13,'2018-11-30 09:50:01.968739','2018-11-30 09:50:01.968762',1,58,1,27),(71,'True','',13,'2018-11-30 09:50:02.027020','2018-11-30 09:50:02.027043',1,225,1,27),(72,'True','',13,'2018-11-30 09:50:02.085464','2018-11-30 09:50:02.085488',1,226,1,27),(73,'True','',13,'2018-11-30 09:50:02.143496','2018-11-30 09:50:02.143517',1,59,1,27),(74,'True','',13,'2018-11-30 09:50:02.202172','2018-11-30 09:50:02.202194',1,60,1,27),(75,'True','',13,'2018-11-30 09:50:02.261202','2018-11-30 09:50:02.261225',1,61,1,27),(76,'True','',13,'2018-11-30 09:50:02.318668','2018-11-30 09:50:02.318689',1,62,1,27),(77,'True','',13,'2018-11-30 09:50:02.377545','2018-11-30 09:50:02.377570',1,63,1,27),(78,'True','',13,'2018-11-30 09:50:02.437666','2018-11-30 09:50:02.437694',1,64,1,27),(79,'True','',13,'2018-11-30 09:50:02.493967','2018-11-30 09:50:02.493989',1,324,1,27),(80,'True','',13,'2018-11-30 09:50:02.552491','2018-11-30 09:50:02.552538',1,327,1,27),(81,'True','',13,'2018-11-30 09:50:02.610617','2018-11-30 09:50:02.610653',1,328,1,27),(82,'True','',13,'2018-11-30 09:50:02.670628','2018-11-30 09:50:02.670670',1,329,1,27),(83,'True','',13,'2018-11-30 09:50:02.727771','2018-11-30 09:50:02.727794',1,330,1,27),(84,'True','',13,'2018-11-30 09:50:02.787787','2018-11-30 09:50:02.787820',1,331,1,27),(85,'True','',13,'2018-11-30 09:50:02.839885','2018-11-30 09:50:02.839916',1,332,1,27),(86,'True','',13,'2018-11-30 09:50:02.888351','2018-11-30 09:50:02.888397',1,339,1,27),(87,'True','',13,'2018-11-30 09:50:02.937316','2018-11-30 09:50:02.937339',1,340,1,27),(88,'True','',13,'2018-11-30 09:50:02.987657','2018-11-30 09:50:02.987680',1,333,1,27),(89,'True','',13,'2018-11-30 09:50:03.037289','2018-11-30 09:50:03.037309',1,334,1,27),(90,'True','',13,'2018-11-30 09:50:03.088491','2018-11-30 09:50:03.088517',1,335,1,27),(91,'True','',13,'2018-11-30 09:50:03.137830','2018-11-30 09:50:03.137853',1,336,1,27),(92,'True','',13,'2018-11-30 09:50:03.187938','2018-11-30 09:50:03.187961',1,337,1,27),(93,'True','',13,'2018-11-30 09:50:03.238194','2018-11-30 09:50:03.238217',1,338,1,27),(94,'False','',13,'2018-11-30 09:50:03.287848','2018-11-30 09:50:03.287870',1,174,1,27),(95,'False','',13,'2018-11-30 09:50:03.367353','2018-11-30 09:50:03.367376',1,158,1,27),(96,'True','',13,'2018-11-30 09:50:03.430005','2018-11-30 09:50:03.430027',1,159,1,27),(97,'True','',13,'2018-11-30 09:50:03.479461','2018-11-30 09:50:03.479482',1,160,1,27),(98,'True','',13,'2018-11-30 09:50:03.529958','2018-11-30 09:50:03.529981',1,161,1,27),(99,'True','',13,'2018-11-30 09:50:03.579419','2018-11-30 09:50:03.579439',1,162,1,27),(100,'True','',13,'2018-11-30 09:50:03.630358','2018-11-30 09:50:03.630383',1,163,1,27),(101,'True','',13,'2018-11-30 09:50:03.679785','2018-11-30 09:50:03.679807',1,164,1,27),(102,'x','',13,'2018-11-30 09:50:03.730468','2018-11-30 09:50:03.730490',1,65,1,27),(103,'','',13,'2018-11-30 09:50:03.780235','2018-11-30 09:50:03.780258',1,370,1,27),(104,'[]','',13,'2018-11-30 09:50:03.830375','2018-11-30 09:50:03.830399',1,82,1,27),(105,'\"{\\\"question\\\":[{\\\"id\\\":\\\"\\\"}]}\"','',13,'2018-11-30 09:50:03.997574','2018-11-30 09:50:03.997597',1,175,1,27),(106,'[\"6\"]','',13,'2018-11-30 09:50:04.097215','2018-11-30 09:50:04.097237',1,50,1,27),(107,'photos-photo-group','',6,'2018-11-30 09:52:46.959376','2018-11-30 09:52:46.959401',1,187,1,28),(108,'','',6,'2018-11-30 09:52:47.014622','2018-11-30 09:52:47.014656',1,189,1,28),(109,'','',6,'2018-11-30 09:52:47.065027','2018-11-30 09:52:47.065061',1,190,1,28),(110,'','',6,'2018-11-30 09:52:47.114844','2018-11-30 09:52:47.114874',1,191,1,28),(111,'','',6,'2018-11-30 09:52:47.165407','2018-11-30 09:52:47.165434',1,192,1,28),(112,'256','',6,'2018-11-30 09:52:47.214821','2018-11-30 09:52:47.214845',1,193,1,28),(113,'256','',6,'2018-11-30 09:52:47.266098','2018-11-30 09:52:47.266127',1,194,1,28),(114,'','',6,'2018-11-30 09:52:47.315200','2018-11-30 09:52:47.315226',1,195,1,28),(115,'','',6,'2018-11-30 09:52:47.364591','2018-11-30 09:52:47.364612',1,196,1,28),(116,'True','',6,'2018-11-30 09:52:47.415269','2018-11-30 09:52:47.415291',1,197,1,28),(117,'True','',6,'2018-11-30 09:52:47.464694','2018-11-30 09:52:47.464716',1,198,1,28),(118,'False','',6,'2018-11-30 09:52:47.517516','2018-11-30 09:52:47.517537',1,199,1,28),(119,'12','',7,'2018-11-30 09:52:57.189868','2018-11-30 09:52:57.189886',1,202,1,28),(120,'True','',7,'2018-11-30 09:52:57.300524','2018-11-30 09:52:57.300546',1,203,1,28),(121,'False','',7,'2018-11-30 09:52:57.400726','2018-11-30 09:52:57.400751',1,204,1,28),(122,'full-size','',7,'2018-11-30 09:52:57.460266','2018-11-30 09:52:57.460296',1,205,1,28),(123,'full-size','',7,'2018-11-30 09:52:57.517382','2018-11-30 09:52:57.517403',1,206,1,28),(124,'[\"1\"]','',7,'2018-11-30 09:52:57.575831','2018-11-30 09:52:57.575853',1,201,1,28),(125,'True','',5,'2018-11-30 09:54:30.420051','2018-11-30 09:54:30.420088',1,238,1,29),(126,'True','',5,'2018-11-30 09:54:30.472780','2018-11-30 09:54:30.472805',1,295,1,29),(127,'True','',5,'2018-11-30 09:54:30.521072','2018-11-30 09:54:30.521098',1,297,1,29),(128,'12/7/2018','',5,'2018-11-30 09:54:30.570448','2018-11-30 09:54:30.570468',1,355,1,29),(129,'12/14/2018','',5,'2018-11-30 09:54:30.620621','2018-11-30 09:54:30.620643',1,356,1,29),(130,'12/8/2018','',5,'2018-11-30 09:54:30.670430','2018-11-30 09:54:30.670450',1,240,1,29),(131,'False','',5,'2018-11-30 09:54:30.720863','2018-11-30 09:54:30.720886',1,373,1,29),(132,'True','',5,'2018-11-30 09:54:30.771446','2018-11-30 09:54:30.771469',1,243,1,29),(133,'True','',5,'2018-11-30 09:54:30.820890','2018-11-30 09:54:30.820912',1,244,1,29),(134,'True','',5,'2018-11-30 09:54:30.871249','2018-11-30 09:54:30.871272',1,246,1,29),(135,'True','',5,'2018-11-30 09:54:30.920929','2018-11-30 09:54:30.920950',1,247,1,29),(136,'True','',5,'2018-11-30 09:54:31.196587','2018-11-30 09:54:31.196612',1,248,1,29),(137,'True','',5,'2018-11-30 09:54:31.254942','2018-11-30 09:54:31.254965',1,249,1,29),(138,'True','',5,'2018-11-30 09:54:31.314151','2018-11-30 09:54:31.314176',1,250,1,29),(139,'True','',5,'2018-11-30 09:54:31.371596','2018-11-30 09:54:31.371618',1,251,1,29),(140,'True','',5,'2018-11-30 09:54:31.430147','2018-11-30 09:54:31.430169',1,252,1,29),(141,'[\'time\',\'group\',\'name\']','',5,'2018-11-30 09:54:31.488540','2018-11-30 09:54:31.488561',1,253,1,29),(142,'True','',5,'2018-11-30 09:54:31.549061','2018-11-30 09:54:31.549099',1,254,1,29),(143,'True','',5,'2018-11-30 09:54:31.605309','2018-11-30 09:54:31.605331',1,255,1,29),(144,'True','',5,'2018-11-30 09:54:31.663523','2018-11-30 09:54:31.663546',1,256,1,29),(145,'True','',5,'2018-11-30 09:54:31.722268','2018-11-30 09:54:31.722291',1,257,1,29),(146,'True','',5,'2018-11-30 09:54:31.780533','2018-11-30 09:54:31.780556',1,258,1,29),(147,'True','',5,'2018-11-30 09:54:31.838811','2018-11-30 09:54:31.838834',1,265,1,29),(148,'True','',5,'2018-11-30 09:54:31.897362','2018-11-30 09:54:31.897385',1,266,1,29),(149,'True','',5,'2018-11-30 09:54:31.955851','2018-11-30 09:54:31.955875',1,259,1,29),(150,'True','',5,'2018-11-30 09:54:32.123163','2018-11-30 09:54:32.123186',1,260,1,29),(151,'True','',5,'2018-11-30 09:54:32.214898','2018-11-30 09:54:32.214922',1,261,1,29),(152,'True','',5,'2018-11-30 09:54:32.273070','2018-11-30 09:54:32.273095',1,262,1,29),(153,'True','',5,'2018-11-30 09:54:32.331466','2018-11-30 09:54:32.331489',1,263,1,29),(154,'True','',5,'2018-11-30 09:54:32.389567','2018-11-30 09:54:32.389591',1,264,1,29),(155,'True','',5,'2018-11-30 09:54:32.449705','2018-11-30 09:54:32.449727',1,267,1,29),(156,'True','',5,'2018-11-30 09:54:32.506328','2018-11-30 09:54:32.506351',1,268,1,29),(157,'True','',5,'2018-11-30 09:54:32.564794','2018-11-30 09:54:32.564817',1,269,1,29),(158,'True','',5,'2018-11-30 09:54:32.623083','2018-11-30 09:54:32.623106',1,270,1,29),(159,'True','',5,'2018-11-30 09:54:32.685430','2018-11-30 09:54:32.685477',1,271,1,29),(160,'True','',5,'2018-11-30 09:54:32.749141','2018-11-30 09:54:32.749177',1,272,1,29),(161,'True','',5,'2018-11-30 09:54:32.806238','2018-11-30 09:54:32.806257',1,279,1,29),(162,'True','',5,'2018-11-30 09:54:32.865006','2018-11-30 09:54:32.865028',1,280,1,29),(163,'True','',5,'2018-11-30 09:54:32.922977','2018-11-30 09:54:32.922996',1,273,1,29),(164,'True','',5,'2018-11-30 09:54:32.981999','2018-11-30 09:54:32.982022',1,274,1,29),(165,'True','',5,'2018-11-30 09:54:33.157145','2018-11-30 09:54:33.157168',1,275,1,29),(166,'True','',5,'2018-11-30 09:54:33.215481','2018-11-30 09:54:33.215503',1,276,1,29),(167,'True','',5,'2018-11-30 09:54:33.273632','2018-11-30 09:54:33.273653',1,277,1,29),(168,'True','',5,'2018-11-30 09:54:33.332262','2018-11-30 09:54:33.332285',1,278,1,29),(169,'False','',5,'2018-11-30 09:54:33.390887','2018-11-30 09:54:33.390910',1,293,1,29),(170,'False','',5,'2018-11-30 09:54:33.516467','2018-11-30 09:54:33.516492',1,286,1,29),(171,'True','',5,'2018-11-30 09:54:33.574126','2018-11-30 09:54:33.574148',1,287,1,29),(172,'True','',5,'2018-11-30 09:54:33.634066','2018-11-30 09:54:33.634129',1,288,1,29),(173,'True','',5,'2018-11-30 09:54:33.682755','2018-11-30 09:54:33.682778',1,289,1,29),(174,'True','',5,'2018-11-30 09:54:33.732602','2018-11-30 09:54:33.732623',1,290,1,29),(175,'True','',5,'2018-11-30 09:54:33.782757','2018-11-30 09:54:33.782779',1,291,1,29),(176,'True','',5,'2018-11-30 09:54:33.833153','2018-11-30 09:54:33.833176',1,292,1,29),(177,'x','',5,'2018-11-30 09:54:33.883060','2018-11-30 09:54:33.883084',1,281,1,29),(178,'\"{\\\"question\\\":[{\\\"id\\\":\\\"\\\"}]}\"','',5,'2018-11-30 09:54:33.932931','2018-11-30 09:54:33.932954',1,294,1,29),(179,'[\"6\"]','',5,'2018-11-30 09:54:33.983392','2018-11-30 09:54:33.983417',1,239,1,29),(180,'[\"group_name\",\"name\",\"tag\",\"description\",\"speaker\"]','',5,'2018-11-30 09:54:34.149692','2018-11-30 09:54:34.149714',1,296,1,29),(181,'True','',5,'2018-11-30 09:57:21.803447','2018-11-30 09:57:21.803468',1,235,1,2),(182,'True','',5,'2018-11-30 09:57:21.871225','2018-11-30 09:57:21.871247',1,299,1,2),(183,'True','',5,'2018-11-30 09:57:21.930093','2018-11-30 09:57:21.930118',1,300,1,2),(184,'True','',5,'2018-11-30 09:57:21.988279','2018-11-30 09:57:21.988304',1,301,1,2),(185,'True','',5,'2018-11-30 09:57:22.046095','2018-11-30 09:57:22.046111',1,302,1,2),(186,'True','',5,'2018-11-30 09:57:22.104904','2018-11-30 09:57:22.104926',1,303,1,2),(187,'True','',5,'2018-11-30 09:57:22.163479','2018-11-30 09:57:22.163502',1,304,1,2),(188,'True','',5,'2018-11-30 09:57:22.252794','2018-11-30 09:57:22.252815',1,234,1,2),(189,'True','',5,'2018-11-30 09:57:22.321762','2018-11-30 09:57:22.321784',1,305,1,2),(190,'True','',5,'2018-11-30 09:57:22.381663','2018-11-30 09:57:22.381735',1,306,1,2),(191,'True','',5,'2018-11-30 09:57:22.439836','2018-11-30 09:57:22.439865',1,357,1,2),(192,'True','',5,'2018-11-30 09:57:22.497583','2018-11-30 09:57:22.497609',1,358,1,2),(193,'True','',5,'2018-11-30 09:57:22.555704','2018-11-30 09:57:22.555729',1,359,1,2),(194,'12/8/2018','',6,'2018-11-30 10:00:37.244903','2018-11-30 10:00:37.244964',1,138,1,30),(195,'12/12/2018','',6,'2018-11-30 10:00:37.303324','2018-11-30 10:00:37.303367',1,139,1,30),(196,'False','',6,'2018-11-30 10:00:37.353009','2018-11-30 10:00:37.353051',1,140,1,30),(197,'False','',6,'2018-11-30 10:00:37.402133','2018-11-30 10:00:37.402155',1,141,1,30),(198,'False','',6,'2018-11-30 10:00:37.451914','2018-11-30 10:00:37.451936',1,142,1,30),(199,'do-not-force','',6,'2018-11-30 10:00:37.502415','2018-11-30 10:00:37.502439',1,143,1,30),(200,'1','',6,'2018-11-30 10:00:37.552020','2018-11-30 10:00:37.552053',1,144,1,30),(201,'True','',6,'2018-11-30 10:00:37.602274','2018-11-30 10:00:37.602295',1,347,1,30),(202,'True','',6,'2018-11-30 10:00:37.652167','2018-11-30 10:00:37.652190',1,348,1,30),(203,'True','',6,'2018-11-30 10:00:37.702314','2018-11-30 10:00:37.702337',1,349,1,30),(204,'True','',6,'2018-11-30 10:00:37.802287','2018-11-30 10:00:37.802309',1,350,1,30),(205,'True','',6,'2018-11-30 10:00:37.853158','2018-11-30 10:00:37.853186',1,351,1,30),(206,'True','',6,'2018-11-30 10:00:37.902877','2018-11-30 10:00:37.902900',1,352,1,30),(207,'True','',6,'2018-11-30 10:00:37.953277','2018-11-30 10:00:37.953305',1,353,1,30),(208,'[\"7\"]','',6,'2018-11-30 10:00:38.004088','2018-11-30 10:00:38.004111',1,137,1,30),(209,'{\"6\": \"Submit\"}','',7,'2018-11-30 10:01:12.059867','2018-11-30 10:01:12.059892',1,69,1,30),(210,'hotel-button','',7,'2018-11-30 10:01:12.129791','2018-11-30 10:01:12.129815',1,70,1,30),(211,'','',7,'2018-11-30 10:01:12.187154','2018-11-30 10:01:12.187175',1,366,1,30),(212,'False','',7,'2018-11-30 10:01:12.246539','2018-11-30 10:01:12.246563',1,372,1,30),(213,'False','',7,'2018-11-30 10:01:12.303868','2018-11-30 10:01:12.303890',1,208,1,30),(214,'False','',7,'2018-11-30 10:01:12.362657','2018-11-30 10:01:12.362679',1,222,1,30),(215,'False','',7,'2018-11-30 10:01:12.420850','2018-11-30 10:01:12.420884',1,298,1,30),(216,'[{\"state\":2,\"data\":{\"page_id\":\"2\"}}]','',7,'2018-11-30 10:01:12.479040','2018-11-30 10:01:12.479062',1,74,1,30),(217,'[{\"state\":1,\"data\":\"\"}]','',7,'2018-11-30 10:01:12.537793','2018-11-30 10:01:12.537817',1,371,1,30),(218,'[{\"state\":1,\"data\":\"\"}]','',7,'2018-11-30 10:01:12.596052','2018-11-30 10:01:12.596088',1,75,1,30),(219,'0','',15,'2018-11-30 10:03:46.845189','2018-11-30 10:03:46.845214',1,3,1,31),(220,'True','',15,'2018-11-30 10:03:46.903592','2018-11-30 10:03:46.903620',1,364,1,31),(221,'True','',16,'2018-11-30 10:03:50.209129','2018-11-30 10:03:50.209150',1,6,1,31),(222,'True','',16,'2018-11-30 10:03:50.270069','2018-11-30 10:03:50.270090',1,7,1,31),(223,'True','',16,'2018-11-30 10:03:50.328648','2018-11-30 10:03:50.328672',1,8,1,31),(224,'True','',16,'2018-11-30 10:03:50.387588','2018-11-30 10:03:50.387633',1,363,1,31),(225,'60','',17,'2018-11-30 10:03:56.245489','2018-11-30 10:03:56.245529',1,11,1,31),(226,'0','',17,'2018-11-30 10:03:56.346912','2018-11-30 10:03:56.346936',1,12,1,31),(227,'True','',17,'2018-11-30 10:03:56.404589','2018-11-30 10:03:56.404611',1,365,1,31),(228,'True','',17,'2018-11-30 10:03:56.579565','2018-11-30 10:03:56.579609',1,13,1,31),(229,'True','',17,'2018-11-30 10:03:56.638135','2018-11-30 10:03:56.638158',1,14,1,31),(230,'True','',17,'2018-11-30 10:03:56.696550','2018-11-30 10:03:56.696573',1,15,1,31),(231,'True','',17,'2018-11-30 10:03:56.754558','2018-11-30 10:03:56.754580',1,16,1,31),(232,'True','',17,'2018-11-30 10:03:56.813239','2018-11-30 10:03:56.813262',1,17,1,31),(233,'True','',17,'2018-11-30 10:03:56.872045','2018-11-30 10:03:56.872068',1,18,1,31),(234,'False','',17,'2018-11-30 10:03:56.933815','2018-11-30 10:03:56.933838',1,185,1,31),(235,'False','',17,'2018-11-30 10:03:57.007799','2018-11-30 10:03:57.007830',1,178,1,31),(236,'True','',17,'2018-11-30 10:03:57.063762','2018-11-30 10:03:57.063784',1,179,1,31),(237,'True','',17,'2018-11-30 10:03:57.121801','2018-11-30 10:03:57.121822',1,180,1,31),(238,'True','',17,'2018-11-30 10:03:57.180318','2018-11-30 10:03:57.180341',1,181,1,31),(239,'True','',17,'2018-11-30 10:03:57.238944','2018-11-30 10:03:57.238966',1,182,1,31),(240,'True','',17,'2018-11-30 10:03:57.288592','2018-11-30 10:03:57.288615',1,183,1,31),(241,'True','',17,'2018-11-30 10:03:57.339044','2018-11-30 10:03:57.339069',1,184,1,31),(242,'\"{\\\"question\\\":[{\\\"id\\\":\\\"\\\"}]}\"','',17,'2018-11-30 10:03:57.388572','2018-11-30 10:03:57.388593',1,186,1,31),(243,'1','',1,'2018-11-30 10:10:42.563816','2018-11-30 10:10:42.563839',1,342,1,32),(244,'True','',1,'2018-11-30 10:10:42.614836','2018-11-30 10:10:42.614858',1,85,1,32),(245,'True','',1,'2018-11-30 10:10:42.663438','2018-11-30 10:10:42.663461',1,86,1,32),(246,'True','',1,'2018-11-30 10:10:42.713395','2018-11-30 10:10:42.713418',1,341,1,32),(247,'True','',1,'2018-11-30 10:10:42.763767','2018-11-30 10:10:42.763792',1,360,1,32),(248,'True','',1,'2018-11-30 10:10:42.813048','2018-11-30 10:10:42.813067',1,361,1,32),(249,'10','',1,'2018-11-30 10:10:42.863542','2018-11-30 10:10:42.863565',1,362,1,32),(250,'True','',1,'2018-11-30 10:12:38.243862','2018-11-30 10:12:38.243887',1,21,1,33),(251,'True','',1,'2018-11-30 10:12:38.307080','2018-11-30 10:12:38.307154',1,23,1,33),(252,'True','',1,'2018-11-30 10:12:38.357587','2018-11-30 10:12:38.357618',1,24,1,33),(253,'True','',1,'2018-11-30 10:12:38.409669','2018-11-30 10:12:38.409708',1,25,1,33),(254,'True','',1,'2018-11-30 10:12:38.508054','2018-11-30 10:12:38.508082',1,26,1,33),(255,'True','',1,'2018-11-30 10:12:38.607336','2018-11-30 10:12:38.607358',1,27,1,33),(256,'True','',1,'2018-11-30 10:12:38.656942','2018-11-30 10:12:38.656960',1,28,1,33),(257,'[\"10\"]','',1,'2018-11-30 10:12:38.707435','2018-11-30 10:12:38.707457',1,22,1,33),(258,'{\"6\": \"Download PDF\"}','',6,'2018-11-30 10:14:02.085355','2018-11-30 10:14:02.085382',1,343,1,33),(259,'locations-pdf-button','',6,'2018-11-30 10:14:02.138344','2018-11-30 10:14:02.138367',1,344,1,33),(260,'6','',6,'2018-11-30 10:14:02.188802','2018-11-30 10:14:02.188826',1,345,1,33),(261,'1','',5,'2018-11-30 10:15:44.680946','2018-11-30 10:15:44.681004',1,210,1,34),(262,'5','',5,'2018-11-30 10:15:44.743898','2018-11-30 10:15:44.743923',1,211,1,34),(263,'1','',5,'2018-11-30 10:15:44.810079','2018-11-30 10:15:44.810103',1,212,1,34),(264,'inline','',5,'2018-11-30 10:15:44.868219','2018-11-30 10:15:44.868241',1,213,1,34),(265,'27','',5,'2018-11-30 10:15:44.926676','2018-11-30 10:15:44.926698',1,214,1,34),(266,'27','',5,'2018-11-30 10:15:44.985308','2018-11-30 10:15:44.985332',1,215,1,34),(267,'send-to-order-owner','',5,'2018-11-30 10:15:45.043482','2018-11-30 10:15:45.043504',1,220,1,34),(268,'include-owner','',5,'2018-11-30 10:15:45.109705','2018-11-30 10:15:45.109724',1,221,1,34),(269,'[]','',5,'2018-11-30 10:15:45.218649','2018-11-30 10:15:45.218671',1,216,1,34),(270,'[]','',5,'2018-11-30 10:15:45.310655','2018-11-30 10:15:45.310677',1,217,1,34),(271,'\"{\\\"question\\\":[{\\\"id\\\":\\\"\\\"}]}\"','',5,'2018-11-30 10:15:45.368740','2018-11-30 10:15:45.368762',1,219,1,34),(272,'{\"6\": \"Submit\"}','',6,'2018-11-30 10:16:16.652977','2018-11-30 10:16:16.653005',1,69,1,34),(273,'inline-registration-button','',6,'2018-11-30 10:16:16.721059','2018-11-30 10:16:16.721081',1,70,1,34),(274,'','',6,'2018-11-30 10:16:16.771331','2018-11-30 10:16:16.771352',1,366,1,34),(275,'False','',6,'2018-11-30 10:16:16.821222','2018-11-30 10:16:16.821241',1,372,1,34),(276,'True','',6,'2018-11-30 10:16:16.871410','2018-11-30 10:16:16.871431',1,208,1,34),(277,'False','',6,'2018-11-30 10:16:16.921534','2018-11-30 10:16:16.921556',1,222,1,34),(278,'False','',6,'2018-11-30 10:16:16.971677','2018-11-30 10:16:16.971699',1,298,1,34),(279,'[{\"state\":2,\"data\":{\"page_id\":\"2\"}}]','',6,'2018-11-30 10:16:17.021828','2018-11-30 10:16:17.021850',1,74,1,34),(280,'[{\"state\":1,\"data\":\"\"}]','',6,'2018-11-30 10:16:17.071206','2018-11-30 10:16:17.071225',1,371,1,34),(281,'[{\"state\":2,\"data\":{\"email_id\":\"1\"}}]','',6,'2018-11-30 10:16:17.121887','2018-11-30 10:16:17.121909',1,75,1,34);
/*!40000 ALTER TABLE `elements_answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elements_questions`
--

DROP TABLE IF EXISTS `elements_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `elements_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `question_key` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `elements_questions_e93cb7eb` (`created_by_id`),
  KEY `elements_questions_0e939a4f` (`group_id`),
  KEY `elements_questions_49fa5cc1` (`last_updated_by_id`),
  CONSTRAINT `elements_question_last_updated_by_id_541c6144c786fba_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `elements_questions_created_by_id_242c68eeb5552c76_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `elements_questions_group_id_52d4ec95af4247c2_fk_elements_id` FOREIGN KEY (`group_id`) REFERENCES `elements` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=374 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elements_questions`
--

LOCK TABLES `elements_questions` WRITE;
/*!40000 ALTER TABLE `elements_questions` DISABLE KEYS */;
INSERT INTO `elements_questions` VALUES (1,'Evaluation Title','2016-07-26 00:00:00.000000','2016-07-26 00:00:00.000000','evaluation_title',1,15,1),(2,'Evaluation Message','2016-07-26 00:00:00.000000','2016-07-26 00:00:00.000000','evaluation_message',1,15,1),(3,'When will the session evaluation appear','2016-07-26 00:00:00.000000','2016-07-26 00:00:00.000000','evaluation_appear',1,15,1),(4,'Messages Title','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000','message_title',1,16,1),(5,'Messages message','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000','message_message',1,16,1),(6,'Allow attendees to archive messages','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000','message_allow_archive',1,16,1),(7,'Display \"Read archived messages\" button','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000','message_archive_button',1,16,1),(8,'Display \"Mark all as read\" button','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000','message_read_button',1,16,1),(9,'Next up Title','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_title',1,17,1),(10,'Next up Message','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_message',1,17,1),(11,'When will the session appear in Next Up','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_appear',1,17,1),(12,'When will the session no no longer be displayed in Next Up','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_disappear',1,17,1),(13,'Start time','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_start_time',1,17,1),(14,'Start date','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_start_date',1,17,1),(15,'Location','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_location',1,17,1),(16,'Link to location details','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_link_location',1,17,1),(17,'Speaker','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_speaker',1,17,1),(18,'Link to speaker details','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_link_speaker',1,17,1),(19,'Location Title','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_title',1,18,1),(20,'Location Message','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_message',1,18,1),(21,'Make list searchable','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_list_searchable',1,18,1),(22,'location groups','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_location_groups',1,18,1),(23,'Title','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_list_title',1,18,1),(24,'Link to location details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_link_location_details',1,18,1),(25,'Description','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_description',1,18,1),(26,'Link to map','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_link_map',1,18,1),(27,'Address details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_address_details',1,18,1),(28,'Contact details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','location_contact_details',1,18,1),(29,'Session Radio Title','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_title',1,19,1),(30,'Session Radio Message','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_message',1,19,1),(31,'Session selection is enabled','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_session_enable',1,19,1),(32,'Session groups','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_session_groups',1,19,1),(33,'Attendee must choose a session','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_session_choose',1,19,1),(34,'Description','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_description',1,19,1),(35,'Start time','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_start_time',1,19,1),(36,'Start date','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_start_date',1,19,1),(37,'End time','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_end_time',1,19,1),(38,'End date','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_end_date',1,19,1),(39,'RVSP date','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_rvsp_date',1,19,1),(40,'Speaker','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_speaker',1,19,1),(41,'Link to speaker details','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_link_speaker',1,19,1),(42,'Tags','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_tags',1,19,1),(43,'Session group','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_session_group',1,19,1),(44,'Location','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_location',1,19,1),(45,'Link to location details','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_link_location',1,19,1),(46,'Show session availability options','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_session_available',1,19,1),(47,'Session Title','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_title',1,20,1),(48,'Session Message','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_message',1,20,1),(49,'Session selection is enabled','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_session_seletion_enabled',1,20,1),(50,'Session groups','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_session_groups',1,20,1),(51,'Attendee must choose at least','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_session_choose_at_least',1,20,1),(52,'Attendee can\'t choose more than','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_session_choose_more_than',1,20,1),(53,'Description','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_description',1,20,1),(54,'Start time','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_start_time',1,20,1),(55,'Start date','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_start_date',1,20,1),(56,'End time','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_end_time',1,20,1),(57,'End date','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_end_date',1,20,1),(58,'RVSP date','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_rvsp_date',1,20,1),(59,'Speaker','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_speaker',1,20,1),(60,'Link to speaker details','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_link_speaker',1,20,1),(61,'Tags','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_tags',1,20,1),(62,'Session group','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_session_group',1,20,1),(63,'Location','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_location',1,20,1),(64,'Link to location details','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_link_location',1,20,1),(65,'Show session availability options','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_session_available',1,20,1),(66,'Login Form Title','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','login_form_title',1,23,1),(67,'Login Form Message','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','login_form_message',1,23,1),(68,'Show reset password link','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','login_form_password_link',1,23,1),(69,'Submit Button Title','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','submit_button_title',1,24,1),(70,'Submit Button Name','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','submit_button_name',1,24,1),(71,'Request Login Title','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','request_login_title',1,25,1),(72,'Request Login Message','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','request_login_message',1,25,1),(73,'Request Login Email to send','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','request_login_email_send',1,25,1),(74,'Submit Button redirect page','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','submit_button_redirect_page',1,24,1),(75,'Submit Button email send','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','submit_button_email_send',1,24,1),(76,'Reset Password Title','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','reset_password_title',1,31,1),(77,'Reset Password Message','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','reset_password_message',1,31,1),(78,'Reset Password Email to send','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','reset_password_email_send',1,31,1),(79,'New Password Title','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','new_password_title',1,32,1),(80,'New Password Message','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','new_password_message',1,32,1),(81,'Session Preselected','2017-01-13 00:00:00.000000','2017-01-13 00:00:00.000000','session_radio_preselected',1,19,1),(82,'Attendee List Title','2017-01-13 00:00:00.000000','2017-01-13 00:00:00.000000','session_checkbox_preselected',1,20,1),(83,'Attendee List Title','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_title',1,33,1),(84,'Attendee List Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_message',1,33,1),(85,'Attendee Allow Excel export','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_allow_excel_export',1,33,1),(86,'Attendee Show search field','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_show_search_field',1,33,1),(87,'Attendee Filter','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_filter_id',1,33,1),(88,'Attendee Selected Columns','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_selected_columns',1,33,1),(137,'Hotel Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_hotel_groups',1,22,1),(138,'Default Check in Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_default_check_in_date',1,22,1),(139,'Default Check out Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_default_check_out_date',1,22,1),(140,'Force the Default Dates','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_force_default_dates',1,22,1),(141,'Require a Room Buddy Request','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_require_room_buddy',1,22,1),(142,'Require a Room Selection','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_require_room_selection',1,22,1),(143,'Force Hotel Room Type','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_force_hotel_room_type',1,22,1),(144,'Allow for Partial Stays','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_allow_partial_stays',1,22,1),(145,'Hotel Reservation Title','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_title',1,22,1),(146,'Hotel Reservation Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_message',1,22,1),(149,'Archive Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','archive_messages_message',1,35,1),(151,'Use Cutom Location Settings','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_custom_location_settings',1,19,1),(152,'Title','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_location_list_title',1,19,1),(153,'Link to location details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_location_link_location_details',1,19,1),(154,'Description','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_location_description',1,19,1),(155,'Link to map','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_location_link_map',1,19,1),(156,'Address details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_location_address_details',1,19,1),(157,'Contact details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_location_contact_details',1,19,1),(158,'Use Custom Location Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_custom_location_settings',1,20,1),(159,'Title','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_location_list_title',1,20,1),(160,'Link to location details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_location_link_location_details',1,20,1),(161,'Description','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_location_description',1,20,1),(162,'Link to map','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_location_link_map',1,20,1),(163,'Address details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_location_address_details',1,20,1),(164,'Contact details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_location_contact_details',1,20,1),(172,'Use Custom Attendee Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_custom_attendee_settings',1,19,1),(173,'Attendee Selected Columns','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_attendee_selected_columns',1,19,1),(174,'Use Custom Attendee Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_custom_attendee_settings',1,20,1),(175,'Attendee Selected Columns','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_attendee_selected_columns',1,20,1),(178,'Use Custom Location Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','next_up_custom_location_settings',1,17,1),(179,'Title','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','next_up_location_list_title',1,17,1),(180,'Link to location details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','next_up_location_link_location_details',1,17,1),(181,'Description','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','next_up_location_description',1,17,1),(182,'Link to map','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','next_up_location_link_map',1,17,1),(183,'Address details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','next_up_location_address_details',1,17,1),(184,'Contact details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','next_up_location_contact_details',1,17,1),(185,'Use Custom Attendee Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','next_up_custom_attendee_settings',1,17,1),(186,'Attendee Selected Columns','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','next_up_attendee_selected_columns',1,17,1),(187,'Photo Group name','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_group_name',1,36,1),(188,'Photo Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_message',1,36,1),(189,'Photo Max Height','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_max_height',1,36,1),(190,'Photo Max Width','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_max_width',1,36,1),(191,'Photo Min Height','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_min_height',1,36,1),(192,'Photo Min Width','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_min_width',1,36,1),(193,'Photo Thumbnail Height','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_thumbnail_height',1,36,1),(194,'Photo Thumbnail Width','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_thumbnail_width',1,36,1),(195,'Photo Rescal Height','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_rescal_height',1,36,1),(196,'Photo Rescal Width','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_rescal_width',1,36,1),(197,'Photo Add Comment','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_add_comment',1,36,1),(198,'Photo Auto Publish','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_auto_publish',1,36,1),(199,'Photo Overwrite','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_upload_overwrite',1,36,1),(200,'Photo Gallery Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_message',1,37,1),(201,'Photo Gallery Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_groups',1,37,1),(202,'Photo Gallery Photo per Page','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_photo_per_page',1,37,1),(203,'Photo Gallery Full Size Photo','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_full_size_photo',1,37,1),(204,'Photo Gallery Show only User Photos','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_only_my_photos',1,37,1),(205,'Photo Gallery Show Comment','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_show_comment',1,37,1),(206,'Photo Gallery Show Submitter Name','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','photo_gallery_show_submitter_name',1,37,1),(207,'Logout Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','logout_message',1,38,1),(208,'Finish multiple registration loop','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','submit_button_finish_multiple_registration_loop',1,24,1),(209,'Multiple Registration Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_message',1,39,1),(210,'Multiple Registration Min Attendees','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_min_attendees',1,39,1),(211,'Multiple Registration Max Attendees','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_max_attendees',1,39,1),(212,'Multiple Registration Default Attendees','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_default_attendees',1,39,1),(213,'Multiple Registration Form','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_form',1,39,1),(214,'Multiple Registration Order Owner Page','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_order_owner_page',1,39,1),(215,'Multiple Registration Attendee Page','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_attendee_page',1,39,1),(216,'Multiple Registration Order Owner Group','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_order_owner_group',1,39,1),(217,'Multiple Registration Attendee Group','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_attendee_group',1,39,1),(218,'Multiple Registration Table Questions','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_table_questions',1,39,1),(219,'Multiple Registration Inherit Answers','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_inherit_answers',1,39,1),(220,'Multiple Registration Confirmation','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_confirmations',1,39,1),(221,'Multiple Registration Attendee Numbers','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','multiple_registration_attendee_numbers',1,39,1),(222,'Send Order','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','submit_button_open_to_pending_order',1,24,1),(223,'Cost','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_cost',1,19,1),(224,'Including Vat','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_incl_vat',1,19,1),(225,'Cost','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_cost',1,20,1),(226,'Including Vat','2016-08-19 00:00:00.000000','2016-08-19 00:00:00.000000','session_checkbox_incl_vat',1,20,1),(231,'Rebate Apply','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','rebate_apply',1,40,1),(232,'Economy Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_message',1,41,1),(233,'Economy Order As','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_as',1,41,1),(234,'Economy Include Balance Table','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_include_balance_table',1,41,1),(235,'Economy Include Order Table','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_include_order_table',1,41,1),(236,'Session Agenda Title','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_title',1,42,1),(237,'Session Agenda Message','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_message',1,42,1),(238,'Session Selection is enabled','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_enable',1,42,1),(239,'Session Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_groups',1,42,1),(240,'Default Browse Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_default_browse_date',1,42,1),(241,'Day Starts at','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_day_starts_at',1,42,1),(242,'Day Ends at','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_day_ends_at',1,42,1),(243,'Show Toolbar Today Button','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_toolbar_today_button',1,42,1),(244,'Show Toolbar Currently Selected Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_toolbar_currently_selected_date',1,42,1),(245,'Show Toolbar Change Browse Mode Buttons','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_toolbar_change_browse_mode_buttons',1,42,1),(246,'Show Toolbar Move Day Forward or Backwards Buttons','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_toolbar_move_day_forward_or_backwards_buttons',1,42,1),(247,'Show All or My sessions toggle','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_all_or_my_sessions',1,42,1),(248,'Show Subscribe to calender','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_subscribe_to_calender',1,42,1),(249,'Show Session Group toggle','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_show_session_group_toggle',1,42,1),(250,'Column Session Group available in Agenda view','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_column_session_group_available_in_agenda_view',1,42,1),(251,'Column Date available in Agenda view','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_column_date_available_in_agenda_view',1,42,1),(252,'Column Time available in Agenda view','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_column_time_available_in_agenda_view',1,42,1),(253,'In Agenda view sort on','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_view_sort_on',1,42,1),(254,'Session Start Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_start_time',1,42,1),(255,'Session Start Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_start_date',1,42,1),(256,'Session End Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_end_time',1,42,1),(257,'Session End Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_end_date',1,42,1),(258,'Session RVSP Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_rvsp_date',1,42,1),(259,'Session Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_speaker',1,42,1),(260,'Session Link to Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_link_speaker',1,42,1),(261,'Session Tags','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_tags',1,42,1),(262,'Session Session Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_session_groups',1,42,1),(263,'Session Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_location',1,42,1),(264,'Session Link to Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_limk_location',1,42,1),(265,'Session Cost','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_session_cost',1,42,1),(266,'Session Including Vat','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_session_incl_vat',1,42,1),(267,'Session Details Description','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_description',1,42,1),(268,'Session Details Start Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_start_time',1,42,1),(269,'Session Details Start Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_start_date',1,42,1),(270,'Session Details End Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_end_time',1,42,1),(271,'Session Details End Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_end_date',1,42,1),(272,'Session Details RVSP Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_rvsp_date',1,42,1),(273,'Session Details Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_speaker',1,42,1),(274,'Session Details Link to Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_link_speaker',1,42,1),(275,'Session Details Tags','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_tags',1,42,1),(276,'Session Details Session Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_session_groups',1,42,1),(277,'Session Details Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_location',1,42,1),(278,'Session Details Link to Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_details_limk_location',1,42,1),(279,'Session Details Cost','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_session_details_cost',1,42,1),(280,'Session Details Including Vat','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_session_details_incl_vat',1,42,1),(281,'Show Session Availability Options','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_available',1,42,1),(282,'Scheduler Width','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_width',1,42,1),(283,'Session Width','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_session_width',1,42,1),(284,'One Hour Height','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_one_hour_height',1,42,1),(285,'Disable Grouping','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_disable_grouping',1,42,1),(286,'Use Custom Location Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_custom_location_settings',1,42,1),(287,'Title','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_location_list_title',1,42,1),(288,'Link to location details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_location_link_location_details',1,42,1),(289,'Description','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_location_description',1,42,1),(290,'Link to map','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_location_link_map',1,42,1),(291,'Address details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_location_address_details',1,42,1),(292,'Contact details','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_agenda_location_contact_details',1,42,1),(293,'Use Custom Attendee Settings','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_custom_attendee_settings',1,42,1),(294,'Attendee Selected Columns','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_attendee_selected_columns',1,42,1),(295,'Make Session Searchable','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_searchable',1,42,1),(296,'Session Searchable Property','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_searchable_property',1,42,1),(297,'Display todays date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_display_today',1,42,1),(298,'Download Invoice','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','submit_button_download_invoice',1,24,1),(299,'Item name','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_table_item_name',1,41,1),(300,'Cost excl. VAT','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_table_cost_excl_vat',1,41,1),(301,'Rebate amount','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_table_rebate_amount',1,41,1),(302,'VAT amount','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_table_vat_amount',1,41,1),(303,'VAT rate','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_table_vat_rate',1,41,1),(304,'Cost incl. VAT','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_order_table_cost_incl_vat',1,41,1),(305,'Setting to display group order in one order table','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','display_group_order_in_one_order_table',1,41,1),(306,'Download invoice when changing order status','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_download_invoice_changing_status',1,41,1),(307,'Show link to session details','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_show_link_to_session_details',1,19,1),(308,'Only count status attending','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_only_count_status_attending',1,19,1),(309,'automatically remove previous session if there is a time conflict','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_radio_remove_previous_session_time_conflict',1,19,1),(310,'Session Details Description','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_description',1,19,1),(311,'Session Details Start Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_start_time',1,19,1),(312,'Session Details Start Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_start_date',1,19,1),(313,'Session Details End Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_end_time',1,19,1),(314,'Session Details End Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_end_date',1,19,1),(315,'Session Details RVSP Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_rvsp_date',1,19,1),(316,'Session Details Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_speaker',1,19,1),(317,'Session Details Link to Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_link_speaker',1,19,1),(318,'Session Details Tags','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_tags',1,19,1),(319,'Session Details Session Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_session_groups',1,19,1),(320,'Session Details Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_location',1,19,1),(321,'Session Details Link to Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_radio_session_details_limk_location',1,19,1),(322,'Session Details Cost','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_session_details_cost',1,19,1),(323,'Session Details Including Vat','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_radio_session_details_incl_vat',1,19,1),(324,'Show link to session details','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_show_link_to_session_details',1,20,1),(325,'Only count status attending','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_only_count_status_attending',1,20,1),(326,'automatically remove previous session if there is a time conflict','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_remove_previous_session_time_conflict',1,20,1),(327,'Session Details Description','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_description',1,20,1),(328,'Session Details Start Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_start_time',1,20,1),(329,'Session Details Start Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_start_date',1,20,1),(330,'Session Details End Time','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_end_time',1,20,1),(331,'Session Details End Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_end_date',1,20,1),(332,'Session Details RVSP Date','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_rvsp_date',1,20,1),(333,'Session Details Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_speaker',1,20,1),(334,'Session Details Link to Speaker','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_link_speaker',1,20,1),(335,'Session Details Tags','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_tags',1,20,1),(336,'Session Details Session Groups','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_session_groups',1,20,1),(337,'Session Details Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_location',1,20,1),(338,'Session Details Link to Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_checkbox_session_details_limk_location',1,20,1),(339,'Session Details Cost','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_session_details_cost',1,20,1),(340,'Session Details Including Vat','2016-08-03 00:00:00.000000','2016-08-03 00:00:00.000000','session_checkbox_session_details_incl_vat',1,20,1),(341,'Show Counting Column','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_show_counting_column',1,33,1),(342,'Attendee Exported List','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_export_list',1,33,1),(343,'PDF Button Title','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','pdf_button_title',1,43,1),(344,'PDF Button Name','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','pdf_button_name',1,43,1),(345,'PDF Button Template','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','pdf_button_template',1,43,1),(346,'Manual Logout Button','2016-12-28 00:00:00.000000','2016-12-28 00:00:00.000000','attendee_logout_button',1,44,1),(347,'Hotel Reservation Optional Field Name','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_name',1,22,1),(348,'Hotel Reservation Optional Field Description','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_description',1,22,1),(349,'Hotel Reservation Optional Field Location','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_location',1,22,1),(350,'Hotel Reservation Optional Field Cost excl VAT','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_cost_excl_vat',1,22,1),(351,'Hotel Reservation Optional Field Cost incl VAT','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_cost_incl_vat',1,22,1),(352,'Hotel Reservation Optional Field VAT Percentage','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_vat_percent',1,22,1),(353,'Hotel Reservation Optional Field VAT Amount','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_optional_field_vat_amount',1,22,1),(354,'Hotel Reservation Pay Whole Hotel Amount','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','hotel_reservation_pay_whole_hotel_amount',1,22,1),(355,'Session agenda date range start','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_date_range_start',1,42,1),(356,'Session agenda date range end','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_date_range_end',1,42,1),(357,'Display Pay by Card Button','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_pay_by_card_button_status',1,41,1),(358,'Display Last Generate PDF Button','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_generate_last_pdf_button_status',1,41,1),(359,'Display PDF Button in Balance Table','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','economy_balance_table_pdf_button_status',1,41,1),(360,'Display Total Number of Attendees','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_show_total_attendees',1,33,1),(361,'Display Table','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_show_attendee_table',1,33,1),(362,'Attendees Per Page','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','attendee_list_attendee_per_page',1,33,1),(363,'Link session name to session details','2016-08-01 00:00:00.000000','2016-08-01 00:00:00.000000','message_session_details_link',1,16,1),(364,'Title link to session details','2016-07-26 00:00:00.000000','2016-07-26 00:00:00.000000','evaluation_session_details_link',1,15,1),(365,'Title link to session details','2016-08-02 00:00:00.000000','2016-08-02 00:00:00.000000','next_up_session_details_link',1,17,1),(366,'Submit Button custom value','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','submit_button_custom_value',1,24,1),(367,'Attendee must choose a session','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_session_must_choose',1,20,1),(368,'Session Checkbox Act like a radio button','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_act_like_radio_button',1,20,1),(369,'Automatically remove previous session if there is a time conflict','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_radio_remove_conflict_session',1,20,1),(370,'Session Checkbox radio preselect','2016-08-05 00:00:00.000000','2016-08-05 00:00:00.000000','session_checkbox_radio_preselected',1,20,1),(371,'Submit Button Auto Add Session','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','submit_button_add_session',1,24,1),(372,'Submit Button remove conflict session','2017-01-02 00:00:00.000000','2017-01-02 00:00:00.000000','submit_button_remove_conflict_session',1,24,1),(373,'Session Agenda Only display attendees sessions','2017-02-01 00:00:00.000000','2017-02-01 00:00:00.000000','session_agenda_only_display_attendees_sessions',1,42,1);
/*!40000 ALTER TABLE `elements_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_contents`
--

DROP TABLE IF EXISTS `email_contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_contents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` longtext COLLATE utf8_unicode_ci NOT NULL,
  `subject_lang` longtext COLLATE utf8_unicode_ci,
  `content` longtext COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `sender_email` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  `template_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_contents_e93cb7eb` (`created_by_id`),
  KEY `email_contents_49fa5cc1` (`last_updated_by_id`),
  KEY `email_contents_74f53564` (`template_id`),
  CONSTRAINT `email_content_template_id_197476d742efaaad_fk_email_templates_id` FOREIGN KEY (`template_id`) REFERENCES `email_templates` (`id`),
  CONSTRAINT `email_contents_created_by_id_186499a0033dd456_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `email_contents_last_updated_by_id_40655a653368d79a_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_contents`
--

LOCK TABLES `email_contents` WRITE;
/*!40000 ALTER TABLE `email_contents` DISABLE KEYS */;
INSERT INTO `email_contents` VALUES (1,'Registration',NULL,'','default-email-confirmation','mahedi@workspaceit.com','2017-03-14 10:23:37.000000','2017-03-14 10:23:37.000000',1,1,1,1),(2,'Login Info',NULL,'','request-login-confirmation','mahedi@workspaceit.com','2017-03-14 10:23:37.000000','2017-03-14 10:23:37.000000',1,1,1,1),(3,'Reset Password',NULL,'','reset-password-confirmation','mahedi@workspaceit.com','2017-03-14 10:23:37.000000','2017-03-14 10:23:37.000000',1,1,1,1),(4,'Session Conflict',NULL,'','session-conflict-email-confirmation','mahedi@workspaceit.com','2017-11-17 06:35:22.000000','2017-11-17 06:35:22.000000',1,1,1,1),(5,'Session Attend',NULL,'','session-no-conflict-email-confirmation','mahedi@workspaceit.com','2017-11-17 06:36:00.000000','2017-11-17 06:36:00.000000',1,1,1,1);
/*!40000 ALTER TABLE `email_contents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_language_contents`
--

DROP TABLE IF EXISTS `email_language_contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_language_contents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext COLLATE utf8_unicode_ci NOT NULL,
  `email_content_id` int(11) NOT NULL,
  `language_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_lan_email_content_id_5da2f6b4d947baa2_fk_email_contents_id` (`email_content_id`),
  KEY `email_language_contents_468679bd` (`language_id`),
  CONSTRAINT `email_lan_email_content_id_5da2f6b4d947baa2_fk_email_contents_id` FOREIGN KEY (`email_content_id`) REFERENCES `email_contents` (`id`),
  CONSTRAINT `email_language_conten_language_id_74223b51ab361319_fk_presets_id` FOREIGN KEY (`language_id`) REFERENCES `presets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_language_contents`
--

LOCK TABLES `email_language_contents` WRITE;
/*!40000 ALTER TABLE `email_language_contents` DISABLE KEYS */;
INSERT INTO `email_language_contents` VALUES (1,'<h1>Confirmation</h1>\n<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur ac mattis erat. Cras sodales purus vitae neque auctor, vel sollicitudin velit molestie. Integer venenatis diam quis massa tincidunt convallis. Aliquam ullamcorper nunc at rutrum luctus.</p>\n\n<p><a class=\"button\" data-mce-href=\"{uid_link}\" href=\"{uid_link}\">Your personal page</a></p>\n\n<h2>Your details</h2>\n\n<p>{\"questions\"}\n	<br>{\"sessions\"}\n	<br>{\"hotels\"}\n	<br>{\"travels\"}</p>\n\n<h1>&nbsp;</h1>',1,6),(2,'<p>As this clashes with another Session you’re booked onto ({session_name}), please follow <a data-mce-href=\"{messages_link}\" href=\"{messages_link}\">THIS LINK</a> to confirm whether you’d like to take your place in the new Session or stick with your current choice.</p>\n\n',4,6),(3,'<p>A space has opened up in the following Session: {session_name}</p>\n\n<p>You’ve been moved from the waiting list and the Session has been added to your personal agenda for the day.</p>\n\n',5,6);
/*!40000 ALTER TABLE `email_language_contents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_receivers`
--

DROP TABLE IF EXISTS `email_receivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_receivers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lastname` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status` enum('sent','not_sent') COLLATE utf8_unicode_ci NOT NULL,
  `last_received` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `added_by_id` int(11) NOT NULL,
  `attendee_id` int(11) DEFAULT NULL,
  `email_content_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_receivers_0c5d7d4e` (`added_by_id`),
  KEY `email_receivers_c50970ee` (`attendee_id`),
  KEY `email_receivers_a4ae2b14` (`email_content_id`),
  CONSTRAINT `email_rece_email_content_id_f61f6456cefdd1c_fk_email_contents_id` FOREIGN KEY (`email_content_id`) REFERENCES `email_contents` (`id`),
  CONSTRAINT `email_receivers_added_by_id_5ce205a9ea2aff24_fk_users_id` FOREIGN KEY (`added_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `email_receivers_attendee_id_128ffb1d07cc80e_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_receivers`
--

LOCK TABLES `email_receivers` WRITE;
/*!40000 ALTER TABLE `email_receivers` DISABLE KEYS */;
INSERT INTO `email_receivers` VALUES (1,'Mahedi','Hasan','mahedi@workspaceit.com','sent','2018-11-30 10:31:53.024223',1,1,1,1);
/*!40000 ALTER TABLE `email_receivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_receivers_history`
--

DROP TABLE IF EXISTS `email_receivers_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_receivers_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sending_at` datetime(6) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_receive_receiver_id_1d16af327a6bccbf_fk_email_receivers_id` (`receiver_id`),
  CONSTRAINT `email_receive_receiver_id_1d16af327a6bccbf_fk_email_receivers_id` FOREIGN KEY (`receiver_id`) REFERENCES `email_receivers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_receivers_history`
--

LOCK TABLES `email_receivers_history` WRITE;
/*!40000 ALTER TABLE `email_receivers_history` DISABLE KEYS */;
INSERT INTO `email_receivers_history` VALUES (1,'2018-11-30 10:31:53.024677',1);
/*!40000 ALTER TABLE `email_receivers_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_templates`
--

DROP TABLE IF EXISTS `email_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_templates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8_unicode_ci NOT NULL,
  `category` enum('web_pages','email_templates','invoices','pdf') COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_templates_e93cb7eb` (`created_by_id`),
  KEY `email_templates_4437cfac` (`event_id`),
  KEY `email_templates_49fa5cc1` (`last_updated_by_id`),
  CONSTRAINT `email_templates_created_by_id_6851773627784a75_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `email_templates_event_id_738f85f7d1d058ff_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `email_templates_last_updated_by_id_9b4dc80ac08eaa1_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_templates`
--

LOCK TABLES `email_templates` WRITE;
/*!40000 ALTER TABLE `email_templates` DISABLE KEYS */;
INSERT INTO `email_templates` VALUES (1,'default-email-template','<!DOCTYPE html>\n<html lang=\"en\">\n	<head>\n		<meta charset=\"utf-8\">\n		<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">\n		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n		<style>\n			html,\n			body {\n				height: 100%;\n				margin: 0;\n			}\n			\n			body {\n				font-family: sans-serif;\n				font-size: 16px;\n			}\n			\n			h1,\n			h2,\n			h3,\n			h4,\n			h5,\n			h6 {\n				color: #AE6686;\n				margin-top: 0;\n			}\n			\n			p {\n				line-height: 145%;\n			}\n			\n			a {\n				color: #AE6686;\n			}\n			\n			table {\n				border-spacing: 0;\n				border-collapse: collapse;\n			}\n			\n			td {\n				vertical-align: top;\n				padding: 0;\n			}\n			\n			#wrapper {\n				height: 100%;\n				width: 100%;\n				background-color: #E9E7D7;\n				background: url(\"http://springconf.com/temp/ed-mail/bg.png\") #F2F0E4 no-repeat center top;\n				background-size: contain;\n				text-align: center;\n			}\n			\n			#content {\n				margin: 0 auto;\n				width: 600px;\n				text-align: left;\n			}\n			\n			#content #header td {\n				padding: 50px 0 25px 0;\n			}\n			\n			#content #header img {\n				width: 150px;\n			}\n			\n			#content .section td {\n				background-color: white;\n				padding: 20px;\n				box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.1);\n			}\n			\n			#content .section td *:last-child {\n				margin-bottom: 0;\n			}\n			\n			#content .spacer td {\n				height: 20px;\n			}\n			\n			#content .footer td {\n				background-color: #7C5578;\n				color: white;\n				padding: 20px;\n				box-shadow: 0px 2px 2px rgba(0, 0, 0, 0.1);\n			}\n			\n			#content .footer td a {\n				color: white;\n			}\n			\n			.button {\n				color: #ffffff;\n				text-decoration: none;\n				border-radius: 2px;\n				background-color: #AE6686;\n				border-top: 12px solid #AE6686;\n				border-bottom: 12px solid #AE6686;\n				border-right: 18px solid #AE6686;\n				border-left: 18px solid #AE6686;\n				display: inline-block;\n				text-align: center;\n			}\n			\n			.button:hover {\n				background-color: #7C5578;\n				border-top: 12px solid #7C5578;\n				border-bottom: 12px solid #7C5578;\n				border-right: 18px solid #7C5578;\n				border-left: 18px solid #7C5578;\n			}\n			\n			#content .confirmation-table {\n				width: 100%;\n			}\n			\n			#content .confirmation-table th,\n			#content .confirmation-table td {\n				padding: 7px;\n				font-size: 12px;\n			}\n			\n			#content .confirmation-table th {\n				font-weight: bold;\n				text-align: left;\n				background-color: #AE6686;\n				color: white;\n			}\n			\n			#content .confirmation-table td {\n				border: 1px solid #B7B0A9;\n			}\n\n		</style>\n		<link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.4.0/css/font-awesome.min.css\">\n	</head>\n	<body>\n\n		<table id=\"wrapper\">\n			<tbody>\n				<tr>\n					<td>\n\n						<table id=\"content\">\n							<tbody>\n								<tr id=\"header\">\n									<td><img src=\"https://www.workspaceit.com/wsit_images/logo.png\" width=\"150\" class=\"fr-fic fr-dii\"></td>\n								</tr>\n								<tr class=\"section\">\n									<td>{content}</td>\n								</tr>\n								<tr class=\"spacer\">\n									<td>\n										<br>\n									</td>\n								</tr>\n								<tr class=\"footer\">\n									<td>If you have any questions, please contact <a href=\"mailto:someone@domain.com\">someone@domain.com</a></td>\n								</tr>\n								<tr class=\"spacer\">\n									<td>\n										<br>\n									</td>\n								</tr>\n							</tbody>\n						</table>\n					</td>\n				</tr>\n			</tbody>\n		</table>\n	</body>\n</html>','email_templates','2017-03-14 10:23:37.000000','2017-03-14 10:23:37.000000',1,1,1,1),(2,'default-web-template','<!DOCTYPE html>\n<html>\n	<head>\n		<meta charset=\"utf-8\">\n		<meta content=\"IE=edge\" http-equiv=\"X-UA-Compatible\">\n		<meta content=\"width=device-width, initial-scale=1\" name=\"viewport\">\n		<link href=\"[[css]]\" rel=\"stylesheet\" type=\"text/css\">\n		<title>\n			Default Project\n		</title>\n	</head>\n	<body>\n		<div class=\"section header\">\n			<div class=\"row\">\n				<div class=\"col span-12\">\n					<a href=\"#\" target=\"_blank\"><img class=\"logo fr-fic fr-dii\" src=\"https://www.workspaceit.com/wsit_images/logo.png\"></a> {menu} {language}</div>\n			</div>\n		</div>\n		{content}\n	</body>\n</html>','web_pages','2017-03-14 10:23:37.000000','2017-03-14 10:23:37.000000',1,1,1,1),(3,'default-invoice-template','<!DOCTYPE html>\n<html lang=\"sv-se\">\n	<head>\n		<meta charset=\"utf-8\">\n		<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge,chrome=1\">\n		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n		<style>\n		</style>\n	</head>\n	<body>\n		{content}\n	</body>\n</html>\n','invoices','2017-09-14 10:01:19.000000','2017-09-14 10:01:19.000000',1,1,1,1),(4,'default-credit-invoice-template','<!DOCTYPE html>\n<html lang=\"sv-se\">\n	<head>\n		<meta charset=\"utf-8\">\n		<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge,chrome=1\">\n		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n		<style>\n		</style>\n	</head>\n	<body>\n		{content}\n	</body>\n</html>\n','invoices','2017-09-14 10:01:43.000000','2017-09-14 10:01:43.000000',1,1,1,1),(5,'default-receipt-template','<!DOCTYPE html>\n<html lang=\"sv-se\">\n	<head>\n		<meta charset=\"utf-8\">\n		<meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge,chrome=1\">\n		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n		<style>\n		</style>\n	</head>\n	<body>\n		{content}\n	</body>\n</html>\n','invoices','2017-09-14 10:01:58.000000','2017-09-14 10:01:58.000000',1,1,1,1),(6,'pdf-1','<!DOCTYPE html>\n                        <html lang=sv-se>\n                            <head>\n                                <meta charset=utf-8>\n                                <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge,chrome=1\">\n                                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n                                <link rel=\"stylesheet\" type=\"text/css\" href=\"[[css]]\" />\n                                <style>\n                                </style>\n                            </head>\n                            <body>\n                                <div class=\"section header\">\n                                </div>\n                                {content}\n                                <div class=\"section footer\">\n                                </div>\n                            </body>\n                        </html>','pdf','2018-11-30 10:13:21.214172','2018-11-30 10:13:21.214198',1,1,1,1);
/*!40000 ALTER TABLE `email_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_admins`
--

DROP TABLE IF EXISTS `event_admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event_admins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `updated_at` datetime(6) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `event_admins_156f41ed` (`admin_id`),
  KEY `event_admins_4437cfac` (`event_id`),
  CONSTRAINT `event_admins_admin_id_768bdac2ef9709cc_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `event_admins_event_id_7f6801314e4805cf_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_admins`
--

LOCK TABLES `event_admins` WRITE;
/*!40000 ALTER TABLE `event_admins` DISABLE KEYS */;
/*!40000 ALTER TABLE `event_admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_stylesheets`
--

DROP TABLE IF EXISTS `event_stylesheets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `event_stylesheets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `style` longtext COLLATE utf8_unicode_ci NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `version` int(11) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `event_stylesheets_e93cb7eb` (`created_by_id`),
  KEY `event_stylesheets_4437cfac` (`event_id`),
  CONSTRAINT `event_stylesheets_created_by_id_c1fd3ec4b15d21b_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `event_stylesheets_event_id_297eb24190b06b31_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_stylesheets`
--

LOCK TABLES `event_stylesheets` WRITE;
/*!40000 ALTER TABLE `event_stylesheets` DISABLE KEYS */;
INSERT INTO `event_stylesheets` VALUES (1,'@charset \"UTF-8\";\n@import url(\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css\");\n@import url(\"https://fonts.googleapis.com/css?family=Roboto\");\n\n\n@media screen and (min-width: 769px) {\n    .fixed-footer {\n        padding-bottom: 0;\n    }\n}\n\n*, *:after, *:before {\n    box-sizing: border-box;\n}\n\n.add-outer-padding {\n    padding: 1.6em;\n}\n\n.add-inner-padding {\n    padding: 0.75em;\n}\n\n.add-outer-margin {\n    margin: 1.6em;\n}\n\n.add-inner-margin {\n    margin: 0.75em;\n}\n\n.no-margin {\n    margin: 0;\n}\n\n.no-padding-bottom {\n    padding-bottom: 0px !important;\n}\n\n.table-no-padding-top-left td {\n    padding-top: 0px !important;\n    padding-left: 0px !important;\n}\n\n.scroll-x {\n    overflow-x: auto;\n}\n\n.only-small-screens {\n    display: none;\n}\n\n@media screen and (max-width: 768px) {\n    .only-small-screens {\n        display: inherit;\n    }\n}\n\n.only-large-screens {\n    display: inherit;\n}\n\n@media screen and (max-width: 768px) {\n    .only-large-screens {\n        display: none;\n    }\n}\n\n.bg-none {\n    background: none !important;\n}\n\n.rounded-corners {\n    border-radius: 8px;\n}\n\nhtml {\n    min-height: 100%;\n    position: relative;\n}\n\nbody {\n    min-height: 100%;\n    color: #6A6A6A;\n    font-size: 16px;\n    font-family: \'Roboto\', sans-serif;\n    font-weight: 300;\n    background: #E9E7D7;\n    margin: 0;\n}\n\n@media screen and (max-width: 768px) {\n    body {\n        font-size: 10px;\n    }\n}\n\n:selection {\n    background: #D8A479;\n    color: white;\n}\n\n:-moz-selection {\n    background: #D8A479;\n    color: white;\n}\n\n@media screen and (max-width: 1280px) {\n    .section {\n        border-radius: 0 !important;\n    }\n}\n\n#dialoge {\n    height: 100%;\n    width: 100%;\n    background: rgba(0, 0, 0, 0.5);\n    position: fixed;\n    z-index: 1005;\n    overflow-y: auto;\n    display: none;\n    top: 0;\n}\n\n#dialoge.visible {\n    display: block;\n}\n\n#dialoge .close-dialouge {\n    position: absolute;\n    top: 0;\n    right: 0;\n    padding: 0.75em;\n    padding: 0.75em;\n    background: #d43c3c;\n    color: white;\n    cursor: pointer;\n    z-index: 1;\n}\n\n#dialoge .close-dialouge:after {\n    display: inline-block;\n    content: \"\\f00d\";\n    font-family: FontAwesome;\n}\n\n#dialoge .close-dialouge:hover {\n    background: #a75757;\n    color: white;\n}\n\n#dialoge .dialogue-content {\n    margin: 0 auto;\n    margin-top: 1.6em;\n    overflow: hidden;\n    box-shadow: 0px 15px 30px rgba(0, 0, 0, 0.5);\n    background: white;\n    position: relative;\n}\n\n@media screen and (max-width: 768px) {\n    #dialoge .dialogue-content {\n        width: 100%;\n        margin: 0;\n        position: fixed;\n        overflow-y: auto;\n        max-height: 100%;\n    }\n\n    #dialoge .dialogue-content .dialoge-menu {\n        position: fixed;\n        top: 0;\n        z-index: 1;\n    }\n\n    #dialoge .dialogue-content .section {\n        margin-top: 2.75em;\n    }\n}\n\n@media screen and (min-width: 769px) {\n    #dialoge .dialogue-content {\n        max-width: 791.04px;\n    }\n}\n\n#dialoge .dialogue-content .dialoge-menu {\n    width: 100%;\n    margin-bottom: 0;\n    list-style: none;\n    padding: 0;\n    white-space: nowrap;\n    font-size: 0;\n    overflow-x: auto;\n    -webkit-touch-callout: none;\n    -webkit-user-select: none;\n    -khtml-user-select: none;\n    -moz-user-select: none;\n    -ms-user-select: none;\n    user-select: none;\n    background: #0a8e76;\n    margin-right: 2.5em !important;\n}\n\n#dialoge .dialogue-content .dialoge-menu li {\n    display: inline-block;\n    font-size: 16px;\n    border-right: 2px solid #0a8e76;\n    cursor: pointer;\n}\n\n#dialoge .dialogue-content .dialoge-menu li a {\n    display: inline-block;\n    padding: 0.75em 1.125em;\n    color: white;\n    background: #0a8e76;\n}\n\n#dialoge .dialogue-content .dialoge-menu li a:hover {\n    background-color: #1e5239;\n    color: white;\n}\n\n#dialoge .dialogue-content .dialoge-menu li:last-child {\n    margin-right: 2.5em;\n}\n\n#dialoge .dialogue-content .dialoge-menu li.active a, #dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button, #dialoge .dialogue-content .dialoge-menu li.active a:hover, #dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button:hover {\n    background: white;\n    color: #6A6A6A;\n}\n\n#dialoge .dialogue-content .dialoge-menu li.active a:after, #dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button:after, #dialoge .dialogue-content .dialoge-menu li.active a:hover:after, #dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button:hover:after {\n    color: #6A6A6A;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button {\n    display: inline-block;\n    padding: 0.75em;\n    color: white;\n    background: #0a8e76;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button:hover {\n    background-color: #1e5239;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button:after {\n    display: inline-block;\n    content: \"\\f00d\";\n    font-family: FontAwesome;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button:hover:after {\n    color: white;\n}\n\n#dialoge .dialogue-content .section {\n    padding: 1.6em;\n    border-radius: 0;\n    margin-bottom: 0;\n}\n\n#dialoge .dialogue-content .section *:last-child {\n    margin-bottom: 0;\n}\n\n.section {\n    background: white;\n    border-radius: 0;\n    width: 100%;\n    max-width: 100%;\n    margin: 0 auto 1.6em auto;\n    margin-left: 0px;\n    margin-right: 0px;\n}\n\n.section.fixed-header {\n    width: 100%;\n    position: fixed;\n    top: 0;\n    left: 0;\n    max-width: 100%;\n    margin-bottom: 1.6em;\n    border-radius: 0;\n    z-index: 996;\n}\n\n.section.fixed-header .section {\n    margin-bottom: 0;\n    background: none;\n}\n\n.section.full-width {\n    width: 100%;\n    max-width: 100%;\n    border-radius: 0;\n}\n\n.section.full-width .section {\n    margin-bottom: 0;\n    background: none;\n}\n\n.section.fixed-footer {\n    position: absolute;\n    left: 0;\n    bottom: 0;\n    height: auto;\n    margin: 0;\n    z-index: 995;\n}\n\n.section.fixed-footer .section {\n    margin-bottom: 0;\n    background: none;\n}\n\n.section section {\n    margin-bottom: 1.6em;\n}\n\n.section h1, .section h2, .section h3, .section h4, .section h5, .section h6 {\n    font-family: \'Roboto\', sans-serif;\n    font-weight: bold;\n    margin-top: 0;\n}\n\n.section h1, .section h2 {\n    font-family: \'Roboto\', sans-serif !important;\n    font-weight: 800;\n    text-align: center;\n    display: block;\n    border-bottom: 6px double #8dbeb5;\n    line-height: 1em;\n    padding: 0.75em;\n    padding-top: 0.5em;\n    margin-bottom: 0.35em !important;\n}\n\n.section h1 {\n    font-size: 4.2087269129em;\n    margin-bottom: 1em;\n}\n\n.section h2 {\n    font-size: 3.1573345183em;\n    margin-bottom: 1em;\n}\n\n.section h3 {\n    font-size: 2.368593037em;\n    margin-bottom: 1em;\n}\n\n.section h4 {\n    font-size: 1.776889em;\n    margin-bottom: 1em;\n}\n\n.section h5 {\n    font-size: 1.333em;\n    margin-bottom: 1em;\n}\n\n.section h6 {\n    font-size: 1em;\n    margin-bottom: 1em;\n}\n\n.section p {\n    margin-top: 0;\n    margin-bottom: 1.6em;\n    font-weight: 300;\n    line-height: 1.5;\n}\n\n.section .font-size-xxs {\n    font-size: 9.6837519013px;\n}\n\n.section .font-size-xs {\n    font-size: 11.2616293333px;\n}\n\n.section .font-size-s {\n    font-size: 12.4453333333px;\n}\n\n.section .font-size-l {\n    font-size: 19.5546666667px;\n}\n\n.section .font-size-xl {\n    font-size: 20.7383706667px;\n}\n\n.section .font-size-xxl {\n    font-size: 22.3162480987px;\n}\n\n.section h1 {\n    font-size: raise(1.333, 5);\n    margin-bottom: 1em;\n}\n\n.section h2 {\n    font-size: raise(1.333, 4);\n    margin-bottom: 1em;\n}\n\n.section h3 {\n    font-size: raise(1.333, 3);\n    margin-bottom: 1em;\n}\n\n.section h4 {\n    font-size: raise(1.333, 2);\n    margin-bottom: 1em;\n}\n\n.section h5 {\n    font-size: raise(1.333, 1);\n    margin-bottom: 1em;\n}\n\n.section h6 {\n    font-size: raise(1.333, 0);\n    margin-bottom: 1em;\n}\n\n.section #mobile-menu-trigger {\n    display: none;\n}\n\n/*@media screen and (min-width: 769px) {*/\n    /*.section ul.menu {*/\n        /*list-style: none;*/\n        /*padding: 0;*/\n        /*font-size: 0;*/\n        /*border: 2px solid #0a8e76;*/\n        /*display: inline-block;*/\n        /*border-radius: 0px;*/\n        /*overflow: hidden;*/\n        /*white-space: nowrap;*/\n        /*text-align: left;*/\n    /*}*/\n\n    /*.section ul.menu li {*/\n        /*display: inline-block;*/\n    /*}*/\n\n    /*.section ul.menu li a {*/\n        /*background: linear-gradient(#0a8e76, #1e5239);*/\n        /*color: white;*/\n        /*font-weight: bold;*/\n        /*font-size: 1rem;*/\n        /*padding: 0.75em 1.125em;*/\n        /*display: block;*/\n        /*border-right: 2px solid #0a8e76;*/\n    /*}*/\n\n    /*.section ul.menu li a.has-submenu:after {*/\n        /*content: \"\\f107\";*/\n        /*margin-left: 0.75em;*/\n        /*font-family: FontAwesome;*/\n    /*}*/\n\n    /*.section ul.menu li:hover > a, .section ul.menu li a.active {*/\n        /*text-decoration: none;*/\n        /*background: #1e5239;*/\n        /*color: white;*/\n    /*}*/\n\n    /*.section ul.menu li:last-child a {*/\n        /*border-right: none;*/\n    /*}*/\n\n    /*.section ul.menu li ul {*/\n        /*display: none;*/\n        /*position: absolute;*/\n        /*border: 2px solid #d4d4d4;*/\n        /*border-bottom-left-radius: 8px;*/\n        /*border-bottom-right-radius: 8px;*/\n        /*overflow: hidden;*/\n        /*padding: 0;*/\n        /*background-color: white;*/\n    /*}*/\n\n    /*.section ul.menu li ul li {*/\n        /*display: block;*/\n    /*}*/\n\n    /*.section ul.menu li ul li a {*/\n        /*background: white;*/\n        /*color: #6A6A6A;*/\n        /*width: 100%;*/\n        /*border: none;*/\n        /*padding: 0.75em 3.2em 0.75em 1.6em;*/\n    /*}*/\n\n    /*.section ul.menu li ul li:hover > a, .section ul.menu li ul li a.active {*/\n        /*background-color: #5894a8;*/\n        /*color: white;*/\n    /*}*/\n\n    /*.section ul.menu li:hover > ul {*/\n        /*display: block;*/\n    /*}*/\n/*}*/\n\n/*@media screen and (max-width: 768px) {*/\n    /*.section ul.menu {*/\n        /*display: none;*/\n        /*text-align: left;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger-label {*/\n        /*-webkit-touch-callout: none;*/\n        /*-webkit-user-select: none;*/\n        /*-khtml-user-select: none;*/\n        /*-moz-user-select: none;*/\n        /*-ms-user-select: none;*/\n        /*user-select: none;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger:checked + #mobile-menu-trigger-label + ul.menu {*/\n        /*transform: translate(0, 0);*/\n        /*transition: transform 0.25s ease-out;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu {*/\n        /*transform: translate(100%, 0);*/\n        /*transition: transform 0.25s ease-in;*/\n        /*list-style: none;*/\n        /*padding: 0;*/\n        /*margin: 0;*/\n        /*display: block;*/\n        /*overflow-y: auto;*/\n        /*overflow-x: hidden;*/\n        /*position: fixed;*/\n        /*top: 0;*/\n        /*right: 0;*/\n        /*height: 100%;*/\n        /*background: #0a8e76;*/\n        /*width: 300px;*/\n        /*max-width: 100%;*/\n        /*z-index: 997;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu:before {*/\n        /*content: \"Main menu\";*/\n        /*font-family: \'Roboto\', sans-serif;*/\n        /*font-size: 1.5em;*/\n        /*height: 3.3333333333em;*/\n        /*line-height: 3.3333333333em;*/\n        /*display: block;*/\n        /*padding-left: 1.125em;*/\n        /*color: white;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li {*/\n        /*display: inline-block;*/\n        /*display: block;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li a {*/\n        /*background: #0a8e76;*/\n        /*color: white;*/\n        /*padding: 0.75em 1.125em;*/\n        /*display: block;*/\n        /*text-decoration: none;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li:hover > a, .section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li a.active {*/\n        /*text-decoration: none;*/\n        /*background-color: #1e5239;*/\n        /*color: white;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li ul {*/\n        /*padding: 0;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li ul li a {*/\n        /*background: #0a8e76;*/\n        /*color: white;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li ul li a:before {*/\n        /*content: \"-\";*/\n        /*padding-right: 1.125em;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li ul li:hover > a, .section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu li ul li a.active {*/\n        /*text-decoration: none;*/\n        /*background-color: #352433;*/\n        /*color: white;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger + #mobile-menu-trigger-label + ul.menu #mobile-menu-trigger {*/\n        /*display: none;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger:checked + #mobile-menu-trigger-label {*/\n        /*background: white;*/\n        /*color: #0a8e76;*/\n        /*transition: background 0.25s linear;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger:checked + #mobile-menu-trigger-label:after {*/\n        /*content: \"\\f00d\";*/\n        /*font-family: FontAwesome;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger-label {*/\n        /*user-select: none;*/\n        /*background: #0a8e76;*/\n        /*width: 3em;*/\n        /*height: 3em;*/\n        /*line-height: 3em;*/\n        /*background: #0a8e76;*/\n        /*cursor: pointer;*/\n        /*color: white;*/\n        /*text-align: center;*/\n        /*display: inline-block;*/\n        /*position: fixed;*/\n        /*top: 1em;*/\n        /*right: 1em;*/\n        /*z-index: 998;*/\n        /*border-radius: 1.5em;*/\n        /*transition: background 0.25s linear;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger-label:after {*/\n        /*content: \"\\f0c9\";*/\n        /*height: 100%;*/\n        /*font-family: FontAwesome;*/\n        /*font-size: 1.5em;*/\n    /*}*/\n\n    /*.section #mobile-menu-trigger-label:hover {*/\n        /*background: #0a8e76;*/\n    /*}*/\n/*}*/\n\n.section a {\n    color: #0a8e76;\n    text-decoration: none;\n}\n\n.section a:hover {\n    text-decoration: underline;\n}\n\n.section .label {\n    display: inline-block;\n    padding: 0.1875em 0.375em;\n    color: white;\n    background: #0a8e76;\n    border-radius: 8px;\n    font-size: 0.9em;\n}\n\n.section a.label {\n    color: white;\n    background: #0a8e76;\n    font-weight: normal;\n    text-decoration: none;\n    cursor: pointer;\n}\n\n.section a.label:hover {\n    color: white;\n    background: #0a8e76;\n}\n\n.section .btn, .section button, .section .event-plugin .event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button, .section .dialoge-button-row .event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button, #dialoge .dialogue-content .section .dialoge-button-row button {\n    font-family: \"Merriweather\", serif;\n    color: white;\n    background: #0a8e76;\n    display: inline-block;\n    font-size: 1em;\n    padding: 8px 12px;\n    border: 2px solid #0a8e76;\n}\n\n.section .btn:hover, .section button:hover, .section .event-plugin .event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button:hover, .section .dialoge-button-row .event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button:hover, #dialoge .dialogue-content .section .dialoge-button-row button:hover {\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #1e5239;\n    text-decoration: none;\n    cursor: pointer;\n}\n\n.section .btn.round, .section button.round, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button, .section #dialoge .dialogue-content .dialoge-button-row button, #dialoge .dialogue-content .section .dialoge-button-row button, .section .event-plugin .event-plugin-button, .section .dialoge-button-row .event-plugin-button {\n    border-radius: 2.8em;\n}\n\n.section .btn.rounded, .section button.rounded, .section .event-plugin .rounded.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.rounded, .section .dialoge-button-row .rounded.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.rounded, #dialoge .dialogue-content .section .dialoge-button-row button.rounded {\n    border-radius: 8px;\n}\n\n.section .btn.btn-gradient, .section button.btn-gradient, .section .event-plugin .btn-gradient.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient, .section .dialoge-button-row .btn-gradient.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient {\n    color: white;\n    background: linear-gradient(#996b95 0%, #0a8e76 100%);\n    border: 2px solid #0a8e76;\n}\n\n.section .btn.btn-gradient:hover, .section button.btn-gradient:hover, .section .event-plugin .btn-gradient.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient:hover, .section .dialoge-button-row .btn-gradient.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient:hover {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #1e5239 100%);\n    border: 2px solid #1e5239;\n}\n\n.section .btn.extra-small, .section button.extra-small, .section .event-plugin .extra-small.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.extra-small, .section .dialoge-button-row .extra-small.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.extra-small, #dialoge .dialogue-content .section .dialoge-button-row button.extra-small {\n    padding: 0.3em 0.45em;\n    font-size: 0.6em;\n}\n\n.section .btn.small, .section button.small, .section .event-plugin .small.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.small, .section .dialoge-button-row .small.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.small, #dialoge .dialogue-content .section .dialoge-button-row button.small {\n    padding: 0.4em 0.6em;\n    font-size: 0.8em;\n}\n\n.section .btn.large, .section button.large, .section .event-plugin .large.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.large, .section .dialoge-button-row .large.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.large, #dialoge .dialogue-content .section .dialoge-button-row button.large {\n    padding: 0.6em 0.9em;\n    font-size: 1.2em;\n}\n\n.section .btn.extra-large, .section button.extra-large, .section .event-plugin .extra-large.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.extra-large, .section .dialoge-button-row .extra-large.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.extra-large, #dialoge .dialogue-content .section .dialoge-button-row button.extra-large {\n    padding: 0.7em 1.05em;\n    font-size: 1.4em;\n}\n\n.section hr {\n    border: 0;\n    height: 2px;\n    background: #8dbeb5;\n    margin-bottom: 1.6em;\n}\n\n.section table {\n    border-spacing: 0;\n    border-collapse: collapse;\n    /*margin: 0 0 1.6em 0;*/\n\n}\n\n.section table thead {\n    border-bottom: 2px solid #8dbeb5;\n    text-align: left;\n}\n\n.section table th, .section table td {\n    padding: 0.5625em;\n    vertical-align: top;\n    text-align: left;\n}\n\n.section table tfoot {\n    border-top: 2px solid #8dbeb5;\n}\n\n.section table.strapped th, .section table.strapped tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #0a8e76;\n}\n\n.section table.strapped td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes th, .section table.polka-stripes tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes tbody td:first-child {\n    border-left: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes tbody td:last-child {\n    border-right: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes tbody tr:last-child td {\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes tbody tr:nth-child(even) td {\n    background: #d5c2d3;\n    color: #6A6A6A;\n}\n\n.section fieldset {\n    border: 1px solid #0a8e76;\n    border-radius: 8px;\n    margin-bottom: 1.6em;\n}\n\n.section fieldset legend {\n    font-size: 1.1em;\n    font-weight: bold;\n}\n\n.section .event-question {\n    margin-bottom: 1.6em;\n}\n\n.section .event-question-label {\n    font-weight: bold;\n    display: inline-block;\n    padding-bottom: 0.8em;\n}\n\n.section .event-question-label .event-question-label-description {\n    font-weight: normal;\n    font-style: italic;\n    display: block;\n}\n\n.section input, .section select, .section textarea {\n    outline: none;\n    font-family: \"Merriweather\", serif;\n}\n\n.section textarea {\n    height: 100px;\n}\n\n.section input[type=\"text\"]:not(.k-input):not(.event-plugin-search), .section textarea, .section .search {\n    width: 100%;\n    border: 2px solid #8dbeb5;\n    padding: 0.625em;\n    display: block;\n    font-size: 1em;\n    border-radius: 8px;\n    margin: 0;\n}\n\n.section input[type=\"text\"]:not(.k-input):not(.event-plugin-search):hover, .section textarea:hover, .section .search:hover {\n    border-color: #a2beb4;\n}\n\n.section input[type=\"text\"]:not(.k-input):not(.event-plugin-search):focus, .section textarea:focus, .section .search:focus {\n    border-color: #0a8e76;\n}\n\n.section input[type=\"text\"]:not(.k-input):not(.event-plugin-search):disabled, .section textarea:disabled, .section .search:disabled {\n    background: #dcdcdc;\n    border: 2px solid #b7b7b7;\n}\n\n.section select {\n    width: 100%;\n}\n\n.section .switch-wrapper {\n    overflow: hidden;\n    margin: 0.8em 0;\n}\n\n.section .switch-wrapper .switch {\n    position: relative;\n    display: inline-block;\n    float: left;\n    width: 4.5em;\n    height: 2.5em;\n    margin-right: 0.75em;\n}\n\n.section .switch-wrapper .switch input {\n    display: none;\n}\n\n.section .switch-wrapper .slider {\n    position: absolute;\n    cursor: pointer;\n    top: 0;\n    left: 0;\n    right: 0;\n    bottom: 0;\n    background-color: #dcdcdc;\n    -webkit-transition: background-color .4s, left .4s;\n    transition: background-color .4s, transform .4s;\n}\n\n.section .switch-wrapper .slider:before {\n    position: absolute;\n    content: \"\";\n    height: 2em;\n    width: 2em;\n    left: 0.25em;\n    bottom: 0.25em;\n    background-color: white;\n    -webkit-transition: background-color .4s, left .4s;\n    transition: background-color .4s, transform .4s;\n}\n\n.section .switch-wrapper .slider.round, .section .switch-wrapper .event-plugin .slider.event-plugin-button, .section .event-plugin .switch-wrapper .slider.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .switch-wrapper .event-plugin button.slider, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin .switch-wrapper button.slider, .section .switch-wrapper .dialoge-button-row .slider.event-plugin-button, .section .dialoge-button-row .switch-wrapper .slider.event-plugin-button, .section .switch-wrapper #dialoge .dialogue-content .dialoge-button-row button.slider, .section #dialoge .dialogue-content .dialoge-button-row .switch-wrapper button.slider, #dialoge .dialogue-content .section .switch-wrapper .dialoge-button-row button.slider, #dialoge .dialogue-content .section .dialoge-button-row .switch-wrapper button.slider {\n    border-radius: 34px;\n}\n\n.section .switch-wrapper .slider.round:before, .section .switch-wrapper .event-plugin .slider.event-plugin-button:before, .section .event-plugin .switch-wrapper .slider.event-plugin-button:before, #dialoge .dialogue-content .dialoge-button-row .section .switch-wrapper .event-plugin button.slider:before, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin .switch-wrapper button.slider:before, .section .switch-wrapper .dialoge-button-row .slider.event-plugin-button:before, .section .dialoge-button-row .switch-wrapper .slider.event-plugin-button:before, .section .switch-wrapper #dialoge .dialogue-content .dialoge-button-row button.slider:before, .section #dialoge .dialogue-content .dialoge-button-row .switch-wrapper button.slider:before, #dialoge .dialogue-content .section .switch-wrapper .dialoge-button-row button.slider:before, #dialoge .dialogue-content .section .dialoge-button-row .switch-wrapper button.slider:before {\n    border-radius: 50%;\n}\n\n.section .switch-wrapper input:checked + .slider {\n    background-color: #0a8e76;\n}\n\n.section .switch-wrapper input:focus + .slider {\n    box-shadow: 0 0 1px #0a8e76;\n}\n\n.section .switch-wrapper input:checked + .slider:before {\n    -webkit-transform: translateX(2em);\n    -ms-transform: translateX(2em);\n    transform: translateX(2em);\n}\n\n.section .switch-wrapper .toggle-label {\n    font-size: 1.2em;\n    padding-top: 0.4em;\n    display: inline-block;\n    cursor: pointer;\n}\n\n.section .checkbox-wrapper, .section .radio-wrapper {\n    margin-bottom: 0.8em;\n}\n\n.section .error-on-validate {\n    display: none;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) input[type=\"text\"], .section .validation-failed:not(.event-plugin-hotel-reservation) textarea {\n    margin: 0;\n    border: 2px solid #d43c3c;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) input[type=\"text\"]:focus, .section .validation-failed:not(.event-plugin-hotel-reservation) textarea:focus {\n    border: 2px solid #d43c3c;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .error-on-validate {\n    margin: 0 8px;\n    display: inline-block;\n    background: #d43c3c;\n    color: white;\n    padding: 0.75em;\n    border-bottom-left-radius: 8px;\n    border-bottom-right-radius: 8px;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-select, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-checkbox, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-radio {\n    border-radius: 8px;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-select {\n    border: 2px solid #d43c3c;\n    padding: 0.75em;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-checkbox, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-select, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-radio {\n    border: 2px solid #d43c3c;\n    padding: 0.75em;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-checkbox .checkbox-wrapper:last-child, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-checkbox .radio-wrapper:last-child, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-select .checkbox-wrapper:last-child, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-select .radio-wrapper:last-child, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-radio .checkbox-wrapper:last-child, .section .validation-failed:not(.event-plugin-hotel-reservation) .event-question-radio .radio-wrapper:last-child {\n    margin-bottom: 0;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .event-plugin-item {\n    border-top: 2px solid #d43c3c !important;\n    border-left: 2px solid #d43c3c !important;\n    border-right: 2px solid #d43c3c !important;\n}\n\n.section .validation-failed:not(.event-plugin-hotel-reservation) .event-plugin-item:last-child {\n    border-bottom: 2px solid #d43c3c !important;\n}\n\n.section .validation-failed.event-plugin-hotel-reservation .error-on-validate {\n    margin: 0 8px;\n    display: inline-block;\n    background: #d43c3c;\n    color: white;\n    padding: 0.75em;\n    border-bottom-left-radius: 8px;\n    border-bottom-right-radius: 8px;\n}\n\n.section .validation-failed.event-plugin-hotel-reservation .event-plugin-item {\n    border-top: 2px solid #d43c3c !important;\n    border-left: 2px solid #d43c3c !important;\n    border-right: 2px solid #d43c3c !important;\n}\n\n.section .validation-failed.event-plugin-hotel-reservation .event-plugin-item:last-of-type {\n    border-bottom: 2px solid #d43c3c !important;\n}\n\n.section .event-plugin a, .section .dialoge-button-row a {\n    color: #0a8e76;\n}\n\n.section .event-plugin .event-plugin-intro, .section .dialoge-button-row .event-plugin-intro {\n    margin-bottom: 0.75em;\n}\n\n.section .event-plugin .event-plugin-intro:empty, .section .dialoge-button-row .event-plugin-intro:empty {\n    margin-bottom: 0;\n}\n\n.section .event-plugin .checkbox-input-large input, .section .dialoge-button-row.checkbox-input-large input {\n    display: none;\n}\n\n.section .event-plugin .checkbox-input-large input + label, .section .dialoge-button-row.checkbox-input-large input + label {\n    margin-top: 0.05em;\n    position: relative;\n    border: 4px solid #8dbeb5;\n    color: white;\n    height: 1em;\n    width: 1em;\n    border-radius: 4px;\n    display: inline-block;\n    color: rgba(121, 169, 185, 0);\n    font-size: 2em;\n    -webkit-transition: color .15s;\n    transition: color .15s;\n    cursor: pointer;\n}\n\n.section .event-plugin .checkbox-input-large input + label:after, .section .dialoge-button-row.checkbox-input-large input + label:after {\n    font-family: FontAwesome;\n    content: \"\\f00c\";\n    bottom: -0.125em;\n    left: -0.125em;\n    position: absolute;\n    font-size: 1.2em;\n}\n\n.section .event-plugin .checkbox-input-large input + label:hover, .section .dialoge-button-row.checkbox-input-large input + label:hover {\n    -webkit-transition: color .15s;\n    transition: color .15s;\n    color: rgba(121, 169, 185, 0.5);\n}\n\n.section .event-plugin .checkbox-input-large input + label:hover:after, .section .dialoge-button-row.checkbox-input-large input + label:hover:after {\n    font-family: FontAwesome;\n    content: \"\\f00c\";\n    bottom: -0.125em;\n    left: -0.125em;\n    position: absolute;\n    font-size: 1.2em;\n}\n\n.section .event-plugin .checkbox-input-large input:checked + label, .section .dialoge-button-row.checkbox-input-large input:checked + label {\n    -webkit-transition: color .15s;\n    transition: color .15s;\n    color: #0a8e76;\n}\n\n.section .event-plugin .radiobutton-input-large input, .section .dialoge-button-row.radiobutton-input-large input {\n    display: none;\n}\n\n.section .event-plugin .radiobutton-input-large input + label, .section .dialoge-button-row.radiobutton-input-large input + label {\n    margin-top: 0.05em;\n    position: relative;\n    border: 4px solid #8dbeb5;\n    color: white;\n    height: 1em;\n    width: 1em;\n    border-radius: 1em;\n    display: inline-block;\n    background: rgba(121, 169, 185, 0);\n    font-size: 2em;\n    cursor: pointer;\n}\n\n.section .event-plugin .radiobutton-input-large input + label:before, .section .dialoge-button-row.radiobutton-input-large input + label:before {\n    width: 0.5em;\n    height: 0.5em;\n    border-radius: 0.25em;\n    background: rgba(255, 255, 255, 0);\n    content: \"\";\n    display: inline-block;\n    position: absolute;\n    top: 0.125em;\n    left: 0.125em;\n    -webkit-transition: background .15s;\n    transition: background .15s;\n}\n\n.section .event-plugin .radiobutton-input-large input + label:hover:before, .section .dialoge-button-row.radiobutton-input-large input + label:hover:before {\n    width: 0.5em;\n    height: 0.5em;\n    border-radius: 0.25em;\n    background: rgba(121, 169, 185, 0.5);\n    content: \"\";\n    display: inline-block;\n    position: absolute;\n    top: 0.125em;\n    left: 0.125em;\n    -webkit-transition: background .15s;\n    transition: background .15s;\n}\n\n.section .event-plugin .radiobutton-input-large input:checked + label:before, .section .dialoge-button-row.radiobutton-input-large input:checked + label:before {\n    width: 0.5em;\n    height: 0.5em;\n    border-radius: 0.25em;\n    background: #0a8e76;\n    display: inline-block;\n    position: absolute;\n    top: 0.125em;\n    left: 0.125em;\n    content: \"\";\n    -webkit-transition: background .2s;\n    transition: background .2s;\n}\n\n.section .event-plugin .event-plugin-list, .section .dialoge-button-row .event-plugin-list {\n    overflow: hidden;\n    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);\n    border-radius: 8px;\n}\n\n.section .event-plugin .event-plugin-item, .section .dialoge-button-row .event-plugin-item {\n    color: #6A6A6A;\n    padding: 0.75em;\n    border-top: 2px solid #8dbeb5;\n    border-left: 2px solid #8dbeb5;\n    border-right: 2px solid #8dbeb5;\n    background: white;\n    overflow: hidden;\n}\n\n.section .event-plugin .event-plugin-item:first-child, .section .dialoge-button-row .event-plugin-item:first-child {\n    border-top-left-radius: 8px;\n    border-top-right-radius: 8px;\n}\n\n.section .event-plugin .event-plugin-item:last-child, .section .dialoge-button-row .event-plugin-item:last-child {\n    border-bottom: 2px solid #8dbeb5;\n    border-bottom-left-radius: 8px;\n    border-bottom-right-radius: 8px;\n}\n\n.section .event-plugin .event-plugin-item *:last-child, .section .dialoge-button-row .event-plugin-item *:last-child {\n    margin-bottom: 0;\n}\n\n.section .event-plugin .event-plugin-title, .section .dialoge-button-row .event-plugin-title {\n    margin: 0;\n    padding: 0;\n    font-weight: bold;\n}\n\n.section .event-plugin .event-plugin-title-date, .section .dialoge-button-row .event-plugin-title-date {\n    font-size: 1em;\n    font-weight: normal;\n    font-style: italic;\n    margin-bottom: 0.1875em;\n}\n\n.section .event-plugin .event-plugin-scroll-wrapper, .section .dialoge-button-row .event-plugin-scroll-wrapper {\n    width: 100%;\n    overflow-x: auto;\n}\n\n.section .event-plugin .event-plugin-text, .section .dialoge-button-row .event-plugin-text {\n    line-height: 150%;\n    font-size: 1.15em;\n}\n\n.section .event-plugin .event-plugin-table, .section .dialoge-button-row .event-plugin-table {\n    width: 100%;\n}\n\n.section .event-plugin .event-plugin-table th, .section .dialoge-button-row .event-plugin-table th {\n    white-space: nowrap;\n}\n\n.section .event-plugin .event-plugin-table th, .section .event-plugin .event-plugin-table tfoot td, .section .dialoge-button-row .event-plugin-table th, .section .dialoge-button-row .event-plugin-table tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #1e5239;\n}\n\n.section .event-plugin .event-plugin-table .time, .section .dialoge-button-row .event-plugin-table .time {\n    font-weight: bold;\n}\n\n.section .event-plugin .event-plugin-tags-list, .section .dialoge-button-row .event-plugin-tags-list {\n    display: inline-block;\n}\n\n.section .event-plugin .event-plugin-tags-list .event-plugin-tag, .section .event-plugin.event-plugin-session-scheduler .event-plugin-tags-list .session .event-plugin-tag, .section .event-plugin.event-plugin-session-scheduler .session .event-plugin-tags-list .event-plugin-tag, .section .event-plugin .event-plugin-tags-list .dialoge-button-row.event-plugin-session-scheduler .session .event-plugin-tag, .section .dialoge-button-row.event-plugin-session-scheduler .session .event-plugin .event-plugin-tags-list .event-plugin-tag, .section .dialoge-button-row .event-plugin-tags-list .event-plugin-tag, .section .dialoge-button-row .event-plugin-tags-list .event-plugin.event-plugin-session-scheduler .session .event-plugin-tag, .section .event-plugin.event-plugin-session-scheduler .session .dialoge-button-row .event-plugin-tags-list .event-plugin-tag, .section .dialoge-button-row.event-plugin-session-scheduler .event-plugin-tags-list .session .event-plugin-tag, .section .dialoge-button-row.event-plugin-session-scheduler .session .event-plugin-tags-list .event-plugin-tag {\n    font-size: 0.8em;\n    display: inline-block;\n    color: #ffffff;\n    background: #0a8e76;\n    border-radius: 4px;\n    padding: 0.25em 0.375em;\n}\n\n.section .event-plugin .event-plugin-button, .section .event-plugin #dialoge .dialogue-content .dialoge-button-row button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button, .section .dialoge-button-row .event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button, #dialoge .dialogue-content .section .dialoge-button-row button {\n    margin-top: 0.75em;\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #5793a7;\n}\n\n.section .event-plugin .event-plugin-button:hover, .section .event-plugin #dialoge .dialogue-content .dialoge-button-row button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button:hover, .section .dialoge-button-row .event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button:hover, #dialoge .dialogue-content .section .dialoge-button-row button:hover {\n    color: white;\n    background: #5793a7;\n    border: 2px solid #457585;\n}\n\n.section .event-plugin .event-plugin-button.top, .section .event-plugin #dialoge .dialogue-content .dialoge-button-row button.top, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.top, .section .dialoge-button-row .event-plugin-button.top, .section #dialoge .dialogue-content .dialoge-button-row button.top, #dialoge .dialogue-content .section .dialoge-button-row button.top {\n    margin-top: 0;\n    margin-bottom: 0.75em;\n}\n\n.section .event-plugin .event-plugin-button.close-button:before, .section .event-plugin #dialoge .dialogue-content .dialoge-button-row button.close-button:before, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.close-button:before, .section .dialoge-button-row .event-plugin-button.close-button:before, .section #dialoge .dialogue-content .dialoge-button-row button.close-button:before, #dialoge .dialogue-content .section .dialoge-button-row button.close-button:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin .event-plugin-search-label, .section .dialoge-button-row .event-plugin-search-label {\n    position: relative;\n}\n\n.section .event-plugin .event-plugin-search-label:before, .section .dialoge-button-row .event-plugin-search-label:before {\n    position: absolute;\n    top: 0;\n    left: 0;\n    content: \"?\";\n    font-size: 1.3em;\n    font-family: FontAwesome;\n    padding: 0.75em;\n    color: #0a8e76;\n}\n\n.section .event-plugin .event-plugin-search-wrapper, .section .dialoge-button-row .event-plugin-search-wrapper {\n    position: relative;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search {\n    width: 100%;\n    border: 2px solid #8dbeb5;\n    padding: 0.625em 0.625em 0.625em 1.25em;\n    display: block;\n    font-size: 1em;\n    border-radius: 1.625em;\n    margin: 0 0 0.75em 0 !important;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search:hover, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:hover {\n    border-color: #a2beb4;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search:focus, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:focus {\n    border-color: #0a8e76;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search:disabled, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:disabled {\n    background: #dcdcdc;\n    border: 2px solid #b7b7b7;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-clear-search, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-clear-search {\n    display: none;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search:focus + .event-plugin-clear-search, .section .event-plugin .event-plugin-search-wrapper .event-plugin-search:hover + .event-plugin-clear-search, .section .event-plugin .event-plugin-search-wrapper .event-plugin-clear-search:hover, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:focus + .event-plugin-clear-search, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:hover + .event-plugin-clear-search, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-clear-search:hover {\n    display: block;\n    position: absolute;\n    top: 0.75em;\n    right: 0.75em;\n    font-size: 16px;\n    cursor: pointer;\n    color: #666666;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search:focus + .event-plugin-clear-search:after, .section .event-plugin .event-plugin-search-wrapper .event-plugin-search:hover + .event-plugin-clear-search:after, .section .event-plugin .event-plugin-search-wrapper .event-plugin-clear-search:hover:after, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:focus + .event-plugin-clear-search:after, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:hover + .event-plugin-clear-search:after, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-clear-search:hover:after {\n    line-height: 16px;\n    content: \"\\f057\";\n    font-family: FontAwesome;\n}\n\n.section .event-plugin .event-plugin-search-wrapper .event-plugin-search:focus + .event-plugin-clear-search:hover, .section .event-plugin .event-plugin-search-wrapper .event-plugin-search:hover + .event-plugin-clear-search:hover, .section .event-plugin .event-plugin-search-wrapper .event-plugin-clear-search:hover:hover, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:focus + .event-plugin-clear-search:hover, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-search:hover + .event-plugin-clear-search:hover, .section .dialoge-button-row .event-plugin-search-wrapper .event-plugin-clear-search:hover:hover {\n    color: #7e746a;\n}\n\n.section .event-plugin .event-plugin-label, .section .dialoge-button-row .event-plugin-label {\n    font-weight: bold;\n}\n\n.section .event-plugin.event-plugin-attendee-list .dataTables_scrollHead table th, .section .dialoge-button-row.event-plugin-attendee-list table th {\n    white-space: nowrap;\n    padding-right: 1em;\n    cursor: pointer;\n}\n\n.section .event-plugin.event-plugin-attendee-list .dataTables_scrollHead  table th:after, .section .dialoge-button-row.event-plugin-attendee-list table th:after {\n    content: \"\\f0dc\";\n    font-family: FontAwesome;\n    margin-left: 0.75em;\n}\n\n.section .event-plugin.event-plugin-attendee-list .dataTables_scrollHead  table th.desc:after, .section .dialoge-button-row.event-plugin-attendee-list table th.desc:after {\n    content: \"\\f0dd\";\n    font-family: FontAwesome;\n    margin-left: 0.75em;\n}\n\n.section .event-plugin.event-plugin-attendee-list .dataTables_scrollHead  table th.asc:after, .section .dialoge-button-row.event-plugin-attendee-list table th.asc:after {\n    content: \"\\f0de\";\n    font-family: FontAwesome;\n    margin-left: 0.75em;\n}\n\n.section .event-plugin.event-plugin-evaluations .evaluation-send-button:before, .section .dialoge-button-row.event-plugin-evaluations .evaluation-send-button:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating, .section .dialoge-button-row.event-plugin-evaluations .star-rating {\n    white-space: nowrap;\n    font-size: 0;\n    unicode-bidi: bidi-override;\n    direction: rtl;\n    font-family: FontAwesome;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating *, .section .dialoge-button-row.event-plugin-evaluations .star-rating * {\n    font-size: 1.875rem;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating > input, .section .dialoge-button-row.event-plugin-evaluations .star-rating > input {\n    display: none;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating > input + label, .section .dialoge-button-row.event-plugin-evaluations .star-rating > input + label {\n    display: inline-block;\n    overflow: hidden;\n    text-indent: 9999px;\n    width: 1.2em;\n    white-space: nowrap;\n    cursor: pointer;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating > input + label:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating > input + label:before {\n    display: inline-block;\n    text-indent: -9999px;\n    content: \"?\";\n    color: #dcdcdc;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating > input:checked ~ label:before, .section .event-plugin.event-plugin-evaluations .star-rating > input + label:hover ~ label:before, .section .event-plugin.event-plugin-evaluations .star-rating > input + label:hover:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating > input:checked ~ label:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating > input + label:hover ~ label:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating > input + label:hover:before {\n    content: \"?\";\n    color: #0a8e76;\n    text-shadow: 0 0 1px #0a8e76;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating > .star-rating-clear + label, .section .dialoge-button-row.event-plugin-evaluations .star-rating > .star-rating-clear + label {\n    text-indent: -9999px;\n    width: 0.5em;\n    margin-left: -0.5em;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating > .star-rating-clear + label:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating > .star-rating-clear + label:before {\n    width: 0.5em;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating:hover > input + label:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating:hover > input + label:before {\n    content: \"?\";\n    color: #dcdcdc;\n    text-shadow: none;\n}\n\n.section .event-plugin.event-plugin-evaluations .star-rating:hover > input + label:hover ~ label:before, .section .event-plugin.event-plugin-evaluations .star-rating:hover > input + label:hover:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating:hover > input + label:hover ~ label:before, .section .dialoge-button-row.event-plugin-evaluations .star-rating:hover > input + label:hover:before {\n    content: \"?\";\n    color: #0a8e76;\n    text-shadow: 0 0 1px #0a8e76;\n}\n\n.section .event-plugin.event-plugin-messages .messages-clear, .section .dialoge-button-row.event-plugin-messages .messages-clear {\n    cursor: pointer;\n}\n\n.section .event-plugin.event-plugin-messages .messages-clear:before, .section .dialoge-button-row.event-plugin-messages .messages-clear:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin: 0 0 0.75em 0.75em;\n    float: right;\n    font-size: 1.3em;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-messages .messages-clear:hover:before, .section .dialoge-button-row.event-plugin-messages .messages-clear:hover:before {\n    color: #7e746a;\n}\n\n.section .event-plugin.event-plugin-messages .btn-read-archive-message:before, .section .dialoge-button-row.event-plugin-messages .btn-read-archive-message:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-messages .btn-mark-all-message:before, .section .dialoge-button-row.event-plugin-messages .messages-mark-all-button:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-next-up .next-up-time-and-date-icon:before, .section .dialoge-button-row.event-plugin-next-up .next-up-time-and-date-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-next-up .next-up-location-icon:before, .section .dialoge-button-row.event-plugin-next-up .next-up-location-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-next-up .next-up-speaker-icon:before, .section .dialoge-button-row.event-plugin-next-up .next-up-speaker-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-location-list .location-list-map-icon:before, .section .dialoge-button-row.event-plugin-location-list .location-list-map-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-location-list .location-list-address-icon:before, .section .dialoge-button-row.event-plugin-location-list .location-list-address-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-location-list .location-list-speaker-icon:before, .section .dialoge-button-row.event-plugin-location-list .location-list-speaker-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-attendee-list .attendee-list-download-button:before, .section .dialoge-button-row.event-plugin-attendee-list .attendee-list-download-button:before {\n    content: \"\\f1c3\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin .session-time-and-date-icon:before, .section .dialoge-button-row .session-time-and-date-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin .session-rsvp-deadline-icon:before, .section .dialoge-button-row .session-rsvp-deadline-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin .session-speaker-icon:before, .section .dialoge-button-row .session-speaker-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin .session-tags-icon:before, .section .dialoge-button-row .session-tags-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin .session-group-icon:before, .section .dialoge-button-row .session-group-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin .session-seats-available-icon:before, .section .dialoge-button-row .session-seats-available-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin .session-location-icon:before, .section .dialoge-button-row .session-location-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    color: #666666;\n}\n\n.section .event-plugin.event-plugin-session-radio .event-plugin-title label, .section .dialoge-button-row.event-plugin-session-radio .event-plugin-title label {\n    cursor: pointer;\n}\n\n.section .event-plugin.event-plugin-session-checkbox .event-plugin-title label, .section .dialoge-button-row.event-plugin-session-checkbox .event-plugin-title label {\n    cursor: pointer;\n}\n\n.section .event-plugin.event-plugin-session-checkbox table td:first-child, .section .dialoge-button-row.event-plugin-session-checkbox table td:first-child {\n    width: 1%;\n    padding-left: 0;\n    text-align: center;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation .hotel-reservation-calendar, .section .event-plugin.event-plugin-hotel-reservation .hotel-room-buddy, .section .dialoge-button-row.event-plugin-hotel-reservation .hotel-reservation-calendar, .section .dialoge-button-row.event-plugin-hotel-reservation .hotel-room-buddy {\n    width: 100%;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation label, .section .dialoge-button-row.event-plugin-hotel-reservation label {\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation .row, .section .dialoge-button-row.event-plugin-hotel-reservation .row {\n    margin-bottom: 0.75em;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation .row:last-child, .section .dialoge-button-row.event-plugin-hotel-reservation .row:last-child {\n    margin-bottom: 0;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table, .section .dialoge-button-row.event-plugin-hotel-reservation table {\n    width: 100%;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table tr.sold-out, .section .dialoge-button-row.event-plugin-hotel-reservation table tr.sold-out {\n    text-decoration: line-through;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table tr.sold-out input, .section .dialoge-button-row.event-plugin-hotel-reservation table tr.sold-out input {\n    display: none;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table td, .section .event-plugin.event-plugin-hotel-reservation table th, .section .dialoge-button-row.event-plugin-hotel-reservation table td, .section .dialoge-button-row.event-plugin-hotel-reservation table th {\n    border-left: none;\n    border-right: none;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table td:first-child, .section .dialoge-button-row.event-plugin-hotel-reservation table td:first-child {\n    padding-left: 0;\n    text-align: center;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table td:first-child, .section .event-plugin.event-plugin-hotel-reservation table th:first-child, .section .dialoge-button-row.event-plugin-hotel-reservation table td:first-child, .section .dialoge-button-row.event-plugin-hotel-reservation table th:first-child {\n    width: 1%;\n    padding-left: 0.75em;\n    border-left: 2px solid #8dbeb5;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation table td:last-child, .section .event-plugin.event-plugin-hotel-reservation table th:last-child, .section .dialoge-button-row.event-plugin-hotel-reservation table td:last-child, .section .dialoge-button-row.event-plugin-hotel-reservation table th:last-child {\n    border-right: 2px solid #8dbeb5;\n}\n\n@media screen and (max-width: 768px) {\n    .section .event-plugin.event-plugin-hotel-reservation .hotel-reservation-calendar, .section .event-plugin.event-plugin-hotel-reservation .hotel-room-buddy, .section .dialoge-button-row.event-plugin-hotel-reservation .hotel-reservation-calendar, .section .dialoge-button-row.event-plugin-hotel-reservation .hotel-room-buddy {\n        float: right;\n    }\n\n    .section .event-plugin.event-plugin-hotel-reservation .row:last-child, .section .dialoge-button-row.event-plugin-hotel-reservation .row:last-child {\n        margin-bottom: 0;\n    }\n\n    .section .event-plugin.event-plugin-hotel-reservation .col, .section .dialoge-button-row.event-plugin-hotel-reservation .col {\n        margin-bottom: 0.75em;\n    }\n\n    .section .event-plugin.event-plugin-hotel-reservation .col:last-child, .section .dialoge-button-row.event-plugin-hotel-reservation .col:last-child {\n        margin-bottom: 0;\n    }\n}\n\n.section .event-plugin.event-plugin-hotel-reservation .hotel-reservation-add-button:before, .section .dialoge-button-row.event-plugin-hotel-reservation .hotel-reservation-add-button:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-hotel-reservation .hotel-reservation-remove-button:before, .section .dialoge-button-row.event-plugin-hotel-reservation .hotel-reservation-remove-button:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-travel-reservation .event-plugin-table tbody td:first-child, .section .dialoge-button-row.event-plugin-travel-reservation .event-plugin-table tbody td:first-child {\n    width: 1%;\n}\n\n.section .event-plugin.event-plugin-travel-reservation .event-plugin-table .outbound th, .section .event-plugin.event-plugin-travel-reservation .event-plugin-table .homebound th, .section .dialoge-button-row.event-plugin-travel-reservation .event-plugin-table .outbound th, .section .dialoge-button-row.event-plugin-travel-reservation .event-plugin-table .homebound th {\n    background: #1e5239;\n    color: white;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-subscribe-to-calendar-icon:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-subscribe-to-calendar-icon:before {\n    content: \"?\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item, .section .dialoge-button-row.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item {\n    display: inline-block;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input, .section .dialoge-button-row.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input {\n    display: none;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item label, .section .dialoge-button-row.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item label {\n    cursor: pointer;\n    border: 2px solid #0a8e76;\n    color: #0a8e76;\n    padding: 0.5em;\n    display: inline-block;\n    border-radius: 8px;\n    margin-bottom: 0.375em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input + label:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input + label:before {\n    content: \"\\f070\";\n    font-family: FontAwesome;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input:checked + label, .section .dialoge-button-row.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input:checked + label {\n    color: white;\n    background: #0a8e76;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input:checked + label:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-group-toggle-list .session-group-toggle-list-item input:checked + label:before {\n    content: \"\\f06e\";\n    font-family: FontAwesome;\n}\n\n.section .event-plugin.event-plugin-session-scheduler ul, .section .dialoge-button-row.event-plugin-session-scheduler ul {\n    list-style: none;\n    padding: 0;\n    margin: 0;\n}\n\n.section .event-plugin.event-plugin-session-scheduler ul li, .section .dialoge-button-row.event-plugin-session-scheduler ul li {\n    padding-left: 0;\n    text-indent: 0;\n}\n\n.section .event-plugin.event-plugin-session-scheduler ul li:before, .section .dialoge-button-row.event-plugin-session-scheduler ul li:before {\n    content: \"\";\n    margin-right: 0;\n}\n\n.section .event-plugin.event-plugin-session-scheduler ul li ul, .section .event-plugin.event-plugin-session-scheduler ul li ol, .section .dialoge-button-row.event-plugin-session-scheduler ul li ul, .section .dialoge-button-row.event-plugin-session-scheduler ul li ol {\n    margin-bottom: 0;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session, .section .dialoge-button-row.event-plugin-session-scheduler .session {\n    border-radius: 8px;\n    cursor: pointer;\n    background: white;\n    box-shadow: 0px 2px 0px #cccccc;\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session .status:before {\n    content: \"?\";\n    font-family: FontAwesome;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session .session-title {\n    padding: 0.375em;\n    font-weight: bold;\n    font-size: 1em;\n    color: #009FE2;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session .session-section {\n    padding: 0.375em;\n    font-size: 0.75em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .session-section .session-section-item, .section .dialoge-button-row.event-plugin-session-scheduler .session .session-section .session-section-item {\n    display: inline-block;\n    margin-right: 0.375em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session .session-section .session-section-item *:before {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session .session-section .session-section-item a {\n    color: #6A6A6A;\n    text-decoration: underline;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session .status, .section .dialoge-button-row.event-plugin-session-scheduler .session .status {\n    font-weight: 300;\n    white-space: nowrap;\n    font-size: 0.75em;\n    padding: 0 0.375em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full, .section .dialoge-button-row.event-plugin-session-scheduler .session.full {\n    background: #dcdcdc;\n    color: #6A6A6A;\n    box-shadow: 0px 2px 0px darkgray;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full .status .queue-open, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .status .queue-open {\n    font-size: 0.8em;\n    display: inline-block;\n    color: #6A6A6A;\n    background: #0a8e76;\n    border-radius: 4px;\n    padding: 0.25em 0.375em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .status:before {\n    content: \"?\";\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full .session-section, .section .event-plugin.event-plugin-session-scheduler .session.full .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .session-title {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full .session-section .session-section-item *:before, .section .event-plugin.event-plugin-session-scheduler .session.full .session-title .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .session-title .session-section-item *:before {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full .session-section .session-section-item a, .section .event-plugin.event-plugin-session-scheduler .session.full .session-title .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.full .session-title .session-section-item a {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full-queue-open, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open {\n    background: #dcdcdc;\n    color: #6A6A6A;\n    box-shadow: 0px 2px 0px darkgray;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .status .queue-open, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .status .queue-open {\n    font-size: 0.8em;\n    display: inline-block;\n    color: #6A6A6A;\n    background: #0a8e76;\n    border-radius: 4px;\n    padding: 0.25em 0.375em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .status:before {\n    content: \"?\";\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .session-section, .section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .session-title {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .session-section .session-section-item *:before, .section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .session-title .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .session-title .session-section-item *:before {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .session-section .session-section-item a, .section .event-plugin.event-plugin-session-scheduler .session.full-queue-open .session-title .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.full-queue-open .session-title .session-section-item a {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.attending, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending {\n    background: #0a8e76;\n    color: white;\n    box-shadow: 0px 2px 0px #668646;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.attending .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .status:before {\n    content: \"?\";\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.attending .session-section, .section .event-plugin.event-plugin-session-scheduler .session.attending .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .session-title {\n    color: white;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.attending .session-section .session-section-item *:before, .section .event-plugin.event-plugin-session-scheduler .session.attending .session-title .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .session-title .session-section-item *:before {\n    color: white;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.attending .session-section .session-section-item a, .section .event-plugin.event-plugin-session-scheduler .session.attending .session-title .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.attending .session-title .session-section-item a {\n    color: white;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.in-queue, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue {\n    background: #0a8e76;\n    color: #6A6A6A;\n    box-shadow: 0px 2px 0px #d9c44e;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.in-queue .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .status:before {\n    content: \"?\";\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.in-queue .session-section, .section .event-plugin.event-plugin-session-scheduler .session.in-queue .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .session-title {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.in-queue .session-section .session-section-item *:before, .section .event-plugin.event-plugin-session-scheduler .session.in-queue .session-title .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .session-title .session-section-item *:before {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.in-queue .session-section .session-section-item a, .section .event-plugin.event-plugin-session-scheduler .session.in-queue .session-title .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.in-queue .session-title .session-section-item a {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended {\n    background: #dcdcdc;\n    color: #6A6A6A;\n    box-shadow: 0px 2px 0px darkgray;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .status:before {\n    content: \"?\";\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .session-section, .section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .session-title {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .session-section .session-section-item *:before, .section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .session-title .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .session-title .session-section-item *:before {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .session-section .session-section-item a, .section .event-plugin.event-plugin-session-scheduler .session.rsvp-ended .session-title .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.rsvp-ended .session-title .session-section-item a {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.time-conflict, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict {\n    background: #dcdcdc;\n    color: #6A6A6A;\n    box-shadow: 0px 2px 0px darkgray;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.time-conflict .status:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .status:before {\n    content: \"?\";\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.time-conflict .session-section, .section .event-plugin.event-plugin-session-scheduler .session.time-conflict .session-title, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .session-section, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .session-title {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.time-conflict .session-section .session-section-item *:before, .section .event-plugin.event-plugin-session-scheduler .session.time-conflict .session-title .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .session-section .session-section-item *:before, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .session-title .session-section-item *:before {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session.time-conflict .session-section .session-section-item a, .section .event-plugin.event-plugin-session-scheduler .session.time-conflict .session-title .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .session-section .session-section-item a, .section .dialoge-button-row.event-plugin-session-scheduler .session.time-conflict .session-title .session-section-item a {\n    color: #6A6A6A;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .session-description, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .session-description {\n    margin: 0.8em 0;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .status.full:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .status.full:before {\n    content: \"?\";\n    font-family: FontAwesome;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .status.rsvp-deadline:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .status.rsvp-deadline:before {\n    content: \"?\";\n    font-family: FontAwesome;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .status.time-conflict:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .status.time-conflict:before {\n    content: \"?\";\n    font-family: FontAwesome;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .session-detail-title, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .session-detail-title {\n    margin-bottom: 0;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .switch, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .switch {\n    position: relative;\n    display: inline-block;\n    float: left;\n    width: 4.5em;\n    height: 2.5em;\n    margin-right: 0.75em;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .switch input, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .switch input {\n    display: none;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .disabled .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .disabled .slider {\n    cursor: not-allowed;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .attending input:checked + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .attending input:checked + .slider {\n    background-color: #0a8e76;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .attending input:focus + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .attending input:focus + .slider {\n    box-shadow: 0 0 1px #0a8e76;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .in-queue input:checked + .slider, .section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .full-queue-open input:checked + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .in-queue input:checked + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .full-queue-open input:checked + .slider {\n    background-color: #0a8e76;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .in-queue input:focus + .slider, .section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .full-queue-open input:focus + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .in-queue input:focus + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .full-queue-open input:focus + .slider {\n    box-shadow: 0 0 1px #0a8e76;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .disabled input:checked + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .disabled input:checked + .slider {\n    background-color: #dcdcdc;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .disabled .slider:before, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .disabled .slider:before {\n    background-color: #f4f4f4;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .disabled input:focus + .slider, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .disabled input:focus + .slider {\n    box-shadow: 0 0 1px #dcdcdc;\n}\n\n.section .event-plugin.event-plugin-session-scheduler .session-details .switch-wrapper .session-slider-label, .section .dialoge-button-row.event-plugin-session-scheduler .session-details .switch-wrapper .session-slider-label {\n    font-size: 1.5em;\n    padding-top: 0.25em;\n    display: inline-block;\n    cursor: pointer;\n}\n\n.section .event-plugin.event-plugin-request-login .event-question, .section .dialoge-button-row.event-plugin-request-login .event-question {\n    margin-bottom: 0;\n}\n\n.section .event-plugin.event-plugin-email-password-verification .email-password-verification-password-label, .section .dialoge-button-row.event-plugin-email-password-verification .email-password-verification-password-label {\n    margin-top: 0.5em;\n}\n\n.section .event-plugin.event-plugin-email-password-verification .event-question:last-of-type, .section .dialoge-button-row.event-plugin-email-password-verification .event-question:last-of-type {\n    margin-bottom: 0;\n}\n\n.section .bg-color1, .section #agenda .shared-agenda, #agenda .section .shared-agenda {\n    background: #0a8e76;\n    color: white;\n}\n\n.section .bg-gradient-color1 {\n    background: linear-gradient(#996b95 0%, #0a8e76 100%);\n    color: white;\n}\n\n.section .text-color1 {\n    color: #0a8e76;\n}\n\n.section label.bg-color1, .section #agenda label.shared-agenda, #agenda .section label.shared-agenda {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-color1, .section #agenda a.label.shared-agenda, #agenda .section a.label.shared-agenda {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-color1:hover, .section #agenda a.label.shared-agenda:hover, #agenda .section a.label.shared-agenda:hover {\n    color: white;\n    background: #0a8e76;\n}\n\n.section .btn.btn-color1, .section button.btn-color1, .section .event-plugin .btn-color1.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color1, .section .dialoge-button-row .btn-color1.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color1, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color1 {\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #0a8e76;\n}\n\n.section .btn.btn-color1:hover, .section button.btn-color1:hover, .section .event-plugin .btn-color1.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color1:hover, .section .dialoge-button-row .btn-color1.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color1:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color1:hover {\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #1e5239;\n}\n\n.section .btn.btn-gradient-color1, .section button.btn-gradient-color1, .section .event-plugin .btn-gradient-color1.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color1, .section .dialoge-button-row .btn-gradient-color1.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color1, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color1 {\n    color: white;\n    background: linear-gradient(#996b95 0%, #0a8e76 100%);\n    border: 2px solid #0a8e76;\n}\n\n.section .btn.btn-gradient-color1:hover, .section button.btn-gradient-color1:hover, .section .event-plugin .btn-gradient-color1.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color1:hover, .section .dialoge-button-row .btn-gradient-color1.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color1:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color1:hover {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #1e5239 100%);\n    border: 2px solid #1e5239;\n}\n\n.section ul.list-color1 li:before, .section ol.list-color1 li:before {\n    color: #0a8e76;\n}\n\n.section table.table-color1 thead {\n    color: #0a8e76;\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.table-color1 tfoot {\n    border-top: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-color1 th, .section table.strapped.table-color1 tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-color1 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color1 th, .section table.polka-stripes.table-color1 tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes.table-color1 tbody td:first-child {\n    border-left: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes.table-color1 tbody td:last-child {\n    border-right: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes.table-color1 tbody tr:last-child td {\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.polka-stripes.table-color1 tbody tr:nth-child(even) td {\n    background: #d5c2d3;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color1 {\n    border: 2px solid #0a8e76;\n}\n\n.section select:focus {\n    border-color: #0a8e76;\n}\n\n.section select {\n    background: transparent;\n    padding: 10px;\n    border-radius: 8px;\n}\n\n.section .bg-color2 {\n    background: #1e5239;\n    color: white;\n}\n\n.section .bg-gradient-color2 {\n    background: linear-gradient(#bc809b 0%, #1e5239 100%);\n    color: white;\n}\n\n.section .text-color2 {\n    color: #0a8e76;\n}\n\n.section label.bg-color2 {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-color2 {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-color2:hover {\n    color: white;\n    background: #1e5239;\n}\n\n.section .btn.btn-color2, .section button.btn-color2, .section .event-plugin .btn-color2.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color2, .section .dialoge-button-row .btn-color2.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color2, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color2 {\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #1e5239;\n}\n\n.section .btn.btn-color2:hover, .section button.btn-color2:hover, .section .event-plugin .btn-color2.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color2:hover, .section .dialoge-button-row .btn-color2.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color2:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color2:hover {\n    color: white;\n    background: #1e5239;\n    border: 2px solid #378e76;\n}\n\n.section .btn.btn-gradient-color2, .section button.btn-gradient-color2, .section .event-plugin .btn-gradient-color2.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color2, .section .dialoge-button-row .btn-gradient-color2.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color2, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color2 {\n    color: white;\n    background: linear-gradient(#bc809b 0%, #1e5239 100%);\n    border: 2px solid #1e5239;\n}\n\n.section .btn.btn-gradient-color2:hover, .section button.btn-gradient-color2:hover, .section .event-plugin .btn-gradient-color2.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color2:hover, .section .dialoge-button-row .btn-gradient-color2.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color2:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color2:hover {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #773f58 100%);\n    border: 2px solid #773f58;\n}\n\n.section ul.list-color2 li:before, .section ol.list-color2 li:before {\n    color: #0a8e76;\n}\n\n.section table.table-color2 thead {\n    color: #0a8e76;\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.table-color2 tfoot {\n    border-top: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-color2 th, .section table.strapped.table-color2 tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #1e5239;\n}\n\n.section table.strapped.table-color2 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color2 th, .section table.polka-stripes.table-color2 tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #1e5239;\n}\n\n.section table.polka-stripes.table-color2 tbody td:first-child {\n    border-left: 2px solid #1e5239;\n}\n\n.section table.polka-stripes.table-color2 tbody td:last-child {\n    border-right: 2px solid #1e5239;\n}\n\n.section table.polka-stripes.table-color2 tbody tr:last-child td {\n    border-bottom: 2px solid #1e5239;\n}\n\n.section table.polka-stripes.table-color2 tbody tr:nth-child(even) td {\n    background: #e3cbd6;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color2 {\n    border: 2px solid #0a8e76;\n}\n\n.section .bg-color3 {\n    background: #D8A479;\n    color: #6A6A6A;\n}\n\n.section .bg-gradient-color3 {\n    background: linear-gradient(#dfb390 0%, #cb864d 100%);\n    color: #6A6A6A;\n}\n\n.section .text-color3 {\n    color: #D8A479;\n}\n\n.section label.bg-color3 {\n    color: #6A6A6A;\n    background: #D8A479;\n}\n\n.section a.label.bg-color3 {\n    color: #6A6A6A;\n    background: #D8A479;\n}\n\n.section a.label.bg-color3:hover {\n    color: white;\n    background: #cb864d;\n}\n\n.section .btn.btn-color3, .section button.btn-color3, .section .event-plugin .btn-color3.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color3, .section .dialoge-button-row .btn-color3.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color3, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color3 {\n    color: #6A6A6A;\n    background: #D8A479;\n    border: 2px solid #cb864d;\n}\n\n.section .btn.btn-color3:hover, .section button.btn-color3:hover, .section .event-plugin .btn-color3.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color3:hover, .section .dialoge-button-row .btn-color3.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color3:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color3:hover {\n    color: white;\n    background: #cb864d;\n    border: 2px solid #ac6932;\n}\n\n.section .btn.btn-gradient-color3, .section button.btn-gradient-color3, .section .event-plugin .btn-gradient-color3.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color3, .section .dialoge-button-row .btn-gradient-color3.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color3, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color3 {\n    color: #6A6A6A;\n    background: linear-gradient(#dfb390 0%, #cb864d 100%);\n    border: 2px solid #cb864d;\n}\n\n.section .btn.btn-gradient-color3:hover, .section button.btn-gradient-color3:hover, .section .event-plugin .btn-gradient-color3.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color3:hover, .section .dialoge-button-row .btn-gradient-color3.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color3:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color3:hover {\n    color: white;\n    background: linear-gradient(#D8A479 0%, #ac6932 100%);\n    border: 2px solid #ac6932;\n}\n\n.section ul.list-color3 li:before, .section ol.list-color3 li:before {\n    color: #D8A479;\n}\n\n.section table.table-color3 thead {\n    color: #D8A479;\n    border-bottom: 2px solid #D8A479;\n}\n\n.section table.table-color3 tfoot {\n    border-top: 2px solid #D8A479;\n}\n\n.section table.strapped.table-color3 th, .section table.strapped.table-color3 tfoot td {\n    background: #D8A479;\n    color: #6A6A6A;\n    border: 2px solid #cb864d;\n}\n\n.section table.strapped.table-color3 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color3 th, .section table.polka-stripes.table-color3 tfoot td {\n    background: #D8A479;\n    color: #6A6A6A;\n    border: 2px solid #cb864d;\n}\n\n.section table.polka-stripes.table-color3 tbody td:first-child {\n    border-left: 2px solid #cb864d;\n}\n\n.section table.polka-stripes.table-color3 tbody td:last-child {\n    border-right: 2px solid #cb864d;\n}\n\n.section table.polka-stripes.table-color3 tbody tr:last-child td {\n    border-bottom: 2px solid #cb864d;\n}\n\n.section table.polka-stripes.table-color3 tbody tr:nth-child(even) td {\n    background: #f2e0d1;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color3 {\n    border: 2px solid #D8A479;\n}\n\n.section .bg-color4 {\n    background: #0a8e76;\n    color: #6A6A6A;\n}\n\n.section .bg-gradient-color4 {\n    background: linear-gradient(#eee5b2 0%, #dfcd6a 100%);\n    color: #6A6A6A;\n}\n\n.section .text-color4 {\n    color: #0a8e76;\n}\n\n.section label.bg-color4 {\n    color: #6A6A6A;\n    background: #0a8e76;\n}\n\n.section a.label.bg-color4 {\n    color: #6A6A6A;\n    background: #0a8e76;\n}\n\n.section a.label.bg-color4:hover {\n    color: white;\n    background: #dfcd6a;\n}\n\n.section .btn.btn-color4, .section button.btn-color4, .section .event-plugin .btn-color4.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color4, .section .dialoge-button-row .btn-color4.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color4, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color4 {\n    color: #6A6A6A;\n    background: #0a8e76;\n    border: 2px solid #dfcd6a;\n}\n\n.section .btn.btn-color4:hover, .section button.btn-color4:hover, .section .event-plugin .btn-color4.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color4:hover, .section .dialoge-button-row .btn-color4.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color4:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color4:hover {\n    color: white;\n    background: #dfcd6a;\n    border: 2px solid #d3bb33;\n}\n\n.section .btn.btn-gradient-color4, .section button.btn-gradient-color4, .section .event-plugin .btn-gradient-color4.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color4, .section .dialoge-button-row .btn-gradient-color4.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color4, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color4 {\n    color: #6A6A6A;\n    background: linear-gradient(#eee5b2 0%, #dfcd6a 100%);\n    border: 2px solid #dfcd6a;\n}\n\n.section .btn.btn-gradient-color4:hover, .section button.btn-gradient-color4:hover, .section .event-plugin .btn-gradient-color4.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color4:hover, .section .dialoge-button-row .btn-gradient-color4.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color4:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color4:hover {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #d3bb33 100%);\n    border: 2px solid #d3bb33;\n}\n\n.section ul.list-color4 li:before, .section ol.list-color4 li:before {\n    color: #0a8e76;\n}\n\n.section table.table-color4 thead {\n    color: #0a8e76;\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.table-color4 tfoot {\n    border-top: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-color4 th, .section table.strapped.table-color4 tfoot td {\n    background: #0a8e76;\n    color: #6A6A6A;\n    border: 2px solid #dfcd6a;\n}\n\n.section table.strapped.table-color4 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color4 th, .section table.polka-stripes.table-color4 tfoot td {\n    background: #0a8e76;\n    color: #6A6A6A;\n    border: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-color4 tbody td:first-child {\n    border-left: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-color4 tbody td:last-child {\n    border-right: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-color4 tbody tr:last-child td {\n    border-bottom: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-color4 tbody tr:nth-child(even) td {\n    background: #f8f4df;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color4 {\n    border: 2px solid #0a8e76;\n}\n\n.section .bg-color5 {\n    background: #666666;\n    color: #6A6A6A;\n}\n\n.section .bg-gradient-color5 {\n    background: linear-gradient(#c3bdb8 0%, #9c9288 100%);\n    color: #6A6A6A;\n}\n\n.section .text-color5 {\n    color: #666666;\n}\n\n.section label.bg-color5 {\n    color: #6A6A6A;\n    background: #666666;\n}\n\n.section a.label.bg-color5 {\n    color: #6A6A6A;\n    background: #666666;\n}\n\n.section a.label.bg-color5:hover {\n    color: white;\n    background: #9c9288;\n}\n\n.section .btn.btn-color5, .section button.btn-color5, .section .event-plugin .btn-color5.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color5, .section .dialoge-button-row .btn-color5.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color5, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color5 {\n    color: #6A6A6A;\n    background: #666666;\n    border: 2px solid #9c9288;\n}\n\n.section .btn.btn-color5:hover, .section button.btn-color5:hover, .section .event-plugin .btn-color5.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color5:hover, .section .dialoge-button-row .btn-color5.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color5:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color5:hover {\n    color: white;\n    background: #9c9288;\n    border: 2px solid #7e746a;\n}\n\n.section .btn.btn-gradient-color5, .section button.btn-gradient-color5, .section .event-plugin .btn-gradient-color5.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color5, .section .dialoge-button-row .btn-gradient-color5.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color5, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color5 {\n    color: #6A6A6A;\n    background: linear-gradient(#c3bdb8 0%, #9c9288 100%);\n    border: 2px solid #9c9288;\n}\n\n.section .btn.btn-gradient-color5:hover, .section button.btn-gradient-color5:hover, .section .event-plugin .btn-gradient-color5.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color5:hover, .section .dialoge-button-row .btn-gradient-color5.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color5:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color5:hover {\n    color: white;\n    background: linear-gradient(#666666 0%, #7e746a 100%);\n    border: 2px solid #7e746a;\n}\n\n.section ul.list-color5 li:before, .section ol.list-color5 li:before {\n    color: #666666;\n}\n\n.section table.table-color5 thead {\n    color: #666666;\n    border-bottom: 2px solid #666666;\n}\n\n.section table.table-color5 tfoot {\n    border-top: 2px solid #666666;\n}\n\n.section table.strapped.table-color5 th, .section table.strapped.table-color5 tfoot td {\n    background: #666666;\n    color: #6A6A6A;\n    border: 2px solid #9c9288;\n}\n\n.section table.strapped.table-color5 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color5 th, .section table.polka-stripes.table-color5 tfoot td {\n    background: #666666;\n    color: #6A6A6A;\n    border: 2px solid #9c9288;\n}\n\n.section table.polka-stripes.table-color5 tbody td:first-child {\n    border-left: 2px solid #9c9288;\n}\n\n.section table.polka-stripes.table-color5 tbody td:last-child {\n    border-right: 2px solid #9c9288;\n}\n\n.section table.polka-stripes.table-color5 tbody tr:last-child td {\n    border-bottom: 2px solid #9c9288;\n}\n\n.section table.polka-stripes.table-color5 tbody tr:nth-child(even) td {\n    background: #e7e4e2;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color5 {\n    border: 2px solid #666666;\n}\n\n.section .bg-color6 {\n    background: #E9E7D7;\n    color: #6A6A6A;\n}\n\n.section .bg-gradient-color6 {\n    background: linear-gradient(#edebde 0%, #cecaa6 100%);\n    color: #6A6A6A;\n}\n\n.section .text-color6 {\n    color: #E9E7D7;\n}\n\n.section label.bg-color6 {\n    color: #6A6A6A;\n    background: #E9E7D7;\n}\n\n.section a.label.bg-color6 {\n    color: #6A6A6A;\n    background: #E9E7D7;\n}\n\n.section a.label.bg-color6:hover {\n    color: #6A6A6A;\n    background: #cecaa6;\n}\n\n.section .btn.btn-color6, .section button.btn-color6, .section .event-plugin .btn-color6.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color6, .section .dialoge-button-row .btn-color6.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color6, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color6 {\n    color: #6A6A6A;\n    background: #E9E7D7;\n    border: 2px solid #cecaa6;\n}\n\n.section .btn.btn-color6:hover, .section button.btn-color6:hover, .section .event-plugin .btn-color6.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color6:hover, .section .dialoge-button-row .btn-color6.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color6:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color6:hover {\n    color: #6A6A6A;\n    background: #cecaa6;\n    border: 2px solid #b3ac75;\n}\n\n.section .btn.btn-gradient-color6, .section button.btn-gradient-color6, .section .event-plugin .btn-gradient-color6.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color6, .section .dialoge-button-row .btn-gradient-color6.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color6, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color6 {\n    color: #6A6A6A;\n    background: linear-gradient(#edebde 0%, #cecaa6 100%);\n    border: 2px solid #cecaa6;\n}\n\n.section .btn.btn-gradient-color6:hover, .section button.btn-gradient-color6:hover, .section .event-plugin .btn-gradient-color6.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color6:hover, .section .dialoge-button-row .btn-gradient-color6.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color6:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color6:hover {\n    color: white;\n    background: linear-gradient(#E9E7D7 0%, #b3ac75 100%);\n    border: 2px solid #b3ac75;\n}\n\n.section ul.list-color6 li:before, .section ol.list-color6 li:before {\n    color: #E9E7D7;\n}\n\n.section table.table-color6 thead {\n    color: #E9E7D7;\n    border-bottom: 2px solid #E9E7D7;\n}\n\n.section table.table-color6 tfoot {\n    border-top: 2px solid #E9E7D7;\n}\n\n.section table.strapped.table-color6 th, .section table.strapped.table-color6 tfoot td {\n    background: #E9E7D7;\n    color: #6A6A6A;\n    border: 2px solid #cecaa6;\n}\n\n.section table.strapped.table-color6 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color6 th, .section table.polka-stripes.table-color6 tfoot td {\n    background: #E9E7D7;\n    color: #6A6A6A;\n    border: 2px solid #cecaa6;\n}\n\n.section table.polka-stripes.table-color6 tbody td:first-child {\n    border-left: 2px solid #cecaa6;\n}\n\n.section table.polka-stripes.table-color6 tbody td:last-child {\n    border-right: 2px solid #cecaa6;\n}\n\n.section table.polka-stripes.table-color6 tbody tr:last-child td {\n    border-bottom: 2px solid #cecaa6;\n}\n\n.section table.polka-stripes.table-color6 tbody tr:nth-child(even) td {\n    background: #f8f7f1;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color6 {\n    border: 2px solid #E9E7D7;\n}\n\n.section .bg-color7 {\n    background: #F8FAF4;\n    color: #6A6A6A;\n}\n\n.section .bg-gradient-color7 {\n    background: linear-gradient(#f9fbf6 0%, #d3e0ba 100%);\n    color: #6A6A6A;\n}\n\n.section .text-color7 {\n    color: #F8FAF4;\n}\n\n.section label.bg-color7 {\n    color: #6A6A6A;\n    background: #F8FAF4;\n}\n\n.section a.label.bg-color7 {\n    color: #6A6A6A;\n    background: #F8FAF4;\n}\n\n.section a.label.bg-color7:hover {\n    color: #6A6A6A;\n    background: #d3e0ba;\n}\n\n.section .btn.btn-color7, .section button.btn-color7, .section .event-plugin .btn-color7.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color7, .section .dialoge-button-row .btn-color7.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color7, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color7 {\n    color: #6A6A6A;\n    background: #F8FAF4;\n    border: 2px solid #d3e0ba;\n}\n\n.section .btn.btn-color7:hover, .section button.btn-color7:hover, .section .event-plugin .btn-color7.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color7:hover, .section .dialoge-button-row .btn-color7.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color7:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color7:hover {\n    color: #6A6A6A;\n    background: #d3e0ba;\n    border: 2px solid #afc681;\n}\n\n.section .btn.btn-gradient-color7, .section button.btn-gradient-color7, .section .event-plugin .btn-gradient-color7.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color7, .section .dialoge-button-row .btn-gradient-color7.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color7, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color7 {\n    color: #6A6A6A;\n    background: linear-gradient(#f9fbf6 0%, #d3e0ba 100%);\n    border: 2px solid #d3e0ba;\n}\n\n.section .btn.btn-gradient-color7:hover, .section button.btn-gradient-color7:hover, .section .event-plugin .btn-gradient-color7.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color7:hover, .section .dialoge-button-row .btn-gradient-color7.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color7:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color7:hover {\n    color: white;\n    background: linear-gradient(#F8FAF4 0%, #afc681 100%);\n    border: 2px solid #afc681;\n}\n\n.section ul.list-color7 li:before, .section ol.list-color7 li:before {\n    color: #F8FAF4;\n}\n\n.section table.table-color7 thead {\n    color: #F8FAF4;\n    border-bottom: 2px solid #F8FAF4;\n}\n\n.section table.table-color7 tfoot {\n    border-top: 2px solid #F8FAF4;\n}\n\n.section table.strapped.table-color7 th, .section table.strapped.table-color7 tfoot td {\n    background: #F8FAF4;\n    color: #6A6A6A;\n    border: 2px solid #d3e0ba;\n}\n\n.section table.strapped.table-color7 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color7 th, .section table.polka-stripes.table-color7 tfoot td {\n    background: #F8FAF4;\n    color: #6A6A6A;\n    border: 2px solid #d3e0ba;\n}\n\n.section table.polka-stripes.table-color7 tbody td:first-child {\n    border-left: 2px solid #d3e0ba;\n}\n\n.section table.polka-stripes.table-color7 tbody td:last-child {\n    border-right: 2px solid #d3e0ba;\n}\n\n.section table.polka-stripes.table-color7 tbody tr:last-child td {\n    border-bottom: 2px solid #d3e0ba;\n}\n\n.section table.polka-stripes.table-color7 tbody tr:nth-child(even) td {\n    background: #fdfdfb;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color7 {\n    border: 2px solid #F8FAF4;\n}\n\n.section .bg-color8 {\n    background: #948B82;\n    color: white;\n}\n\n.section .bg-gradient-color8 {\n    background: linear-gradient(#a69f97 0%, #7c736a 100%);\n    color: white;\n}\n\n.section .text-color8 {\n    color: #948B82;\n}\n\n.section label.bg-color8 {\n    color: white;\n    background: #948B82;\n}\n\n.section a.label.bg-color8 {\n    color: white;\n    background: #948B82;\n}\n\n.section a.label.bg-color8:hover {\n    color: white;\n    background: #7c736a;\n}\n\n.section .btn.btn-color8, .section button.btn-color8, .section .event-plugin .btn-color8.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color8, .section .dialoge-button-row .btn-color8.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color8, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color8 {\n    color: white;\n    background: #948B82;\n    border: 2px solid #7c736a;\n}\n\n.section .btn.btn-color8:hover, .section button.btn-color8:hover, .section .event-plugin .btn-color8.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-color8:hover, .section .dialoge-button-row .btn-color8.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-color8:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-color8:hover {\n    color: white;\n    background: #7c736a;\n    border: 2px solid #635c55;\n}\n\n.section .btn.btn-gradient-color8, .section button.btn-gradient-color8, .section .event-plugin .btn-gradient-color8.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color8, .section .dialoge-button-row .btn-gradient-color8.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color8, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color8 {\n    color: white;\n    background: linear-gradient(#a69f97 0%, #7c736a 100%);\n    border: 2px solid #7c736a;\n}\n\n.section .btn.btn-gradient-color8:hover, .section button.btn-gradient-color8:hover, .section .event-plugin .btn-gradient-color8.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-color8:hover, .section .dialoge-button-row .btn-gradient-color8.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-color8:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-color8:hover {\n    color: white;\n    background: linear-gradient(#948B82 0%, #635c55 100%);\n    border: 2px solid #635c55;\n}\n\n.section ul.list-color8 li:before, .section ol.list-color8 li:before {\n    color: #948B82;\n}\n\n.section table.table-color8 thead {\n    color: #948B82;\n    border-bottom: 2px solid #948B82;\n}\n\n.section table.table-color8 tfoot {\n    border-top: 2px solid #948B82;\n}\n\n.section table.strapped.table-color8 th, .section table.strapped.table-color8 tfoot td {\n    background: #948B82;\n    color: white;\n    border: 2px solid #7c736a;\n}\n\n.section table.strapped.table-color8 td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-color8 th, .section table.polka-stripes.table-color8 tfoot td {\n    background: #948B82;\n    color: white;\n    border: 2px solid #7c736a;\n}\n\n.section table.polka-stripes.table-color8 tbody td:first-child {\n    border-left: 2px solid #7c736a;\n}\n\n.section table.polka-stripes.table-color8 tbody td:last-child {\n    border-right: 2px solid #7c736a;\n}\n\n.section table.polka-stripes.table-color8 tbody tr:last-child td {\n    border-bottom: 2px solid #7c736a;\n}\n\n.section table.polka-stripes.table-color8 tbody tr:nth-child(even) td {\n    background: #dbd8d5;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-color8 {\n    border: 2px solid #948B82;\n}\n\n.section .bg-info {\n    background: #0a8e76;\n    color: white;\n}\n\n.section .bg-gradient-info {\n    background: linear-gradient(#90b8c5 0%, #5793a7 100%);\n    color: white;\n}\n\n.section .text-info {\n    color: #0a8e76;\n}\n\n.section label.bg-info {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-info {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-info:hover {\n    color: white;\n    background: #5793a7;\n}\n\n.section .btn.btn-info, .section button.btn-info, .section .event-plugin .btn-info.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-info, .section .dialoge-button-row .btn-info.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-info, #dialoge .dialogue-content .section .dialoge-button-row button.btn-info {\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #5793a7;\n}\n\n.section .btn.btn-info:hover, .section button.btn-info:hover, .section .event-plugin .btn-info.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-info:hover, .section .dialoge-button-row .btn-info.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-info:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-info:hover {\n    color: white;\n    background: #5793a7;\n    border: 2px solid #457585;\n}\n\n.section .btn.btn-gradient-info, .section button.btn-gradient-info, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button, .section #dialoge .dialogue-content .dialoge-button-row button, #dialoge .dialogue-content .section .dialoge-button-row button, .section .event-plugin .event-plugin-button, .section .dialoge-button-row .event-plugin-button {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #1e5239 100%);\n    border: 2px solid #1e5239;\n}\n\n.section .btn.btn-gradient-info:hover, .section button.btn-gradient-info:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button:hover, .section #dialoge .dialogue-content .dialoge-button-row button:hover, #dialoge .dialogue-content .section .dialoge-button-row button:hover, .section .event-plugin .event-plugin-button:hover, .section .dialoge-button-row .event-plugin-button:hover {\n    color: #265035;\n    background: #fff;\n    border: 2px solid #265035;\n}\n\n.section ul.list-info li:before, .section ol.list-info li:before {\n    color: #0a8e76;\n}\n\n.section table.table-info thead {\n    color: #0a8e76;\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.table-info tfoot {\n    border-top: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-info th, .section table.strapped.table-info tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #5793a7;\n}\n\n.section table.strapped.table-info td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-info th, .section table.polka-stripes.table-info tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #5793a7;\n}\n\n.section table.polka-stripes.table-info tbody td:first-child {\n    border-left: 2px solid #5793a7;\n}\n\n.section table.polka-stripes.table-info tbody td:last-child {\n    border-right: 2px solid #5793a7;\n}\n\n.section table.polka-stripes.table-info tbody tr:last-child td {\n    border-bottom: 2px solid #5793a7;\n}\n\n.section table.polka-stripes.table-info tbody tr:nth-child(even) td {\n    background: #d1e2e7;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-info {\n    border: 2px solid #0a8e76;\n}\n\n.section .bg-success {\n    background: #0a8e76;\n    color: white;\n}\n\n.section .bg-gradient-success {\n    background: linear-gradient(#aac590 0%, #7fa757 100%);\n    color: white;\n}\n\n.section .text-success {\n    color: #0a8e76;\n}\n\n.section label.bg-success {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-success {\n    color: white;\n    background: #0a8e76;\n}\n\n.section a.label.bg-success:hover {\n    color: white;\n    background: #7fa757;\n}\n\n.section .btn.btn-success, .section button.btn-success, .section .event-plugin .btn-success.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-success, .section .dialoge-button-row .btn-success.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-success, #dialoge .dialogue-content .section .dialoge-button-row button.btn-success {\n    color: white;\n    background: #0a8e76;\n    border: 2px solid #7fa757;\n}\n\n.section .btn.btn-success:hover, .section button.btn-success:hover, .section .event-plugin .btn-success.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-success:hover, .section .dialoge-button-row .btn-success.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-success:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-success:hover {\n    color: white;\n    background: #7fa757;\n    border: 2px solid #658545;\n}\n\n.section .btn.btn-gradient-success, .section button.btn-gradient-success, .section .event-plugin .btn-gradient-success.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-success, .section .dialoge-button-row .btn-gradient-success.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-success, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-success {\n    color: white;\n    background: linear-gradient(#aac590 0%, #7fa757 100%);\n    border: 2px solid #7fa757;\n}\n\n.section .btn.btn-gradient-success:hover, .section button.btn-gradient-success:hover, .section .event-plugin .btn-gradient-success.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-success:hover, .section .dialoge-button-row .btn-gradient-success.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-success:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-success:hover {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #658545 100%);\n    border: 2px solid #658545;\n}\n\n.section ul.list-success li:before, .section ol.list-success li:before {\n    color: #0a8e76;\n}\n\n.section table.table-success thead {\n    color: #0a8e76;\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.table-success tfoot {\n    border-top: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-success th, .section table.strapped.table-success tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #7fa757;\n}\n\n.section table.strapped.table-success td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-success th, .section table.polka-stripes.table-success tfoot td {\n    background: #0a8e76;\n    color: white;\n    border: 2px solid #7fa757;\n}\n\n.section table.polka-stripes.table-success tbody td:first-child {\n    border-left: 2px solid #7fa757;\n}\n\n.section table.polka-stripes.table-success tbody td:last-child {\n    border-right: 2px solid #7fa757;\n}\n\n.section table.polka-stripes.table-success tbody tr:last-child td {\n    border-bottom: 2px solid #7fa757;\n}\n\n.section table.polka-stripes.table-success tbody tr:nth-child(even) td {\n    background: #dce7d1;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-success {\n    border: 2px solid #0a8e76;\n}\n\n.section .bg-warning {\n    background: #0a8e76;\n    color: #6A6A6A;\n}\n\n.section .bg-gradient-warning {\n    background: linear-gradient(#eee5b2 0%, #dfcd6a 100%);\n    color: #6A6A6A;\n}\n\n.section .text-warning {\n    color: #0a8e76;\n}\n\n.section label.bg-warning {\n    color: #6A6A6A;\n    background: #0a8e76;\n}\n\n.section a.label.bg-warning {\n    color: #6A6A6A;\n    background: #0a8e76;\n}\n\n.section a.label.bg-warning:hover {\n    color: white;\n    background: #dfcd6a;\n}\n\n.section .btn.btn-warning, .section button.btn-warning, .section .event-plugin .btn-warning.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-warning, .section .dialoge-button-row .btn-warning.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-warning, #dialoge .dialogue-content .section .dialoge-button-row button.btn-warning {\n    color: #6A6A6A;\n    background: #0a8e76;\n    border: 2px solid #dfcd6a;\n}\n\n.section .btn.btn-warning:hover, .section button.btn-warning:hover, .section .event-plugin .btn-warning.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-warning:hover, .section .dialoge-button-row .btn-warning.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-warning:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-warning:hover {\n    color: white;\n    background: #dfcd6a;\n    border: 2px solid #d3bb33;\n}\n\n.section .btn.btn-gradient-warning, .section button.btn-gradient-warning, .section .event-plugin .btn-gradient-warning.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-warning, .section .dialoge-button-row .btn-gradient-warning.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-warning, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-warning {\n    color: #6A6A6A;\n    background: linear-gradient(#eee5b2 0%, #dfcd6a 100%);\n    border: 2px solid #dfcd6a;\n}\n\n.section .btn.btn-gradient-warning:hover, .section button.btn-gradient-warning:hover, .section .event-plugin .btn-gradient-warning.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-warning:hover, .section .dialoge-button-row .btn-gradient-warning.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-warning:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-warning:hover {\n    color: white;\n    background: linear-gradient(#0a8e76 0%, #d3bb33 100%);\n    border: 2px solid #d3bb33;\n}\n\n.section ul.list-warning li:before, .section ol.list-warning li:before {\n    color: #0a8e76;\n}\n\n.section table.table-warning thead {\n    color: #0a8e76;\n    border-bottom: 2px solid #0a8e76;\n}\n\n.section table.table-warning tfoot {\n    border-top: 2px solid #0a8e76;\n}\n\n.section table.strapped.table-warning th, .section table.strapped.table-warning tfoot td {\n    background: #0a8e76;\n    color: #6A6A6A;\n    border: 2px solid #dfcd6a;\n}\n\n.section table.strapped.table-warning td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-warning th, .section table.polka-stripes.table-warning tfoot td {\n    background: #0a8e76;\n    color: #6A6A6A;\n    border: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-warning tbody td:first-child {\n    border-left: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-warning tbody td:last-child {\n    border-right: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-warning tbody tr:last-child td {\n    border-bottom: 2px solid #dfcd6a;\n}\n\n.section table.polka-stripes.table-warning tbody tr:nth-child(even) td {\n    background: #f8f4df;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-warning {\n    border: 2px solid #0a8e76;\n}\n\n.section .bg-danger {\n    background: #d43c3c;\n    color: white;\n}\n\n.section .bg-gradient-danger {\n    background: linear-gradient(#c59090 0%, #a75757 100%);\n    color: white;\n}\n\n.section .text-danger {\n    color: #d43c3c;\n}\n\n.section label.bg-danger {\n    color: white;\n    background: #d43c3c;\n}\n\n.section a.label.bg-danger {\n    color: white;\n    background: #d43c3c;\n}\n\n.section a.label.bg-danger:hover {\n    color: white;\n    background: #a75757;\n}\n\n.section .btn.btn-danger, .section button.btn-danger, .section .event-plugin .btn-danger.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-danger, .section .dialoge-button-row .btn-danger.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-danger, #dialoge .dialogue-content .section .dialoge-button-row button.btn-danger {\n    color: white;\n    background: #d43c3c;\n    border: 2px solid #a75757;\n}\n\n.section .btn.btn-danger:hover, .section button.btn-danger:hover, .section .event-plugin .btn-danger.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-danger:hover, .section .dialoge-button-row .btn-danger.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-danger:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-danger:hover {\n    color: white;\n    background: #a75757;\n    border: 2px solid #854545;\n}\n\n.section .btn.btn-gradient-danger, .section button.btn-gradient-danger, .section .event-plugin .btn-gradient-danger.event-plugin-button, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-danger, .section .dialoge-button-row .btn-gradient-danger.event-plugin-button, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-danger, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-danger {\n    color: white;\n    background: linear-gradient(#c59090 0%, #a75757 100%);\n    border: 2px solid #a75757;\n}\n\n.section .btn.btn-gradient-danger:hover, .section button.btn-gradient-danger:hover, .section .event-plugin .btn-gradient-danger.event-plugin-button:hover, #dialoge .dialogue-content .dialoge-button-row .section .event-plugin button.btn-gradient-danger:hover, .section .dialoge-button-row .btn-gradient-danger.event-plugin-button:hover, .section #dialoge .dialogue-content .dialoge-button-row button.btn-gradient-danger:hover, #dialoge .dialogue-content .section .dialoge-button-row button.btn-gradient-danger:hover {\n    color: white;\n    background: linear-gradient(#d43c3c 0%, #854545 100%);\n    border: 2px solid #854545;\n}\n\n.section ul.list-danger li:before, .section ol.list-danger li:before {\n    color: #d43c3c;\n}\n\n.section table.table-danger thead {\n    color: #d43c3c;\n    border-bottom: 2px solid #d43c3c;\n}\n\n.section table.table-danger tfoot {\n    border-top: 2px solid #d43c3c;\n}\n\n.section table.strapped.table-danger th, .section table.strapped.table-danger tfoot td {\n    background: #d43c3c;\n    color: white;\n    border: 2px solid #a75757;\n}\n\n.section table.strapped.table-danger td {\n    border: 2px solid #8dbeb5;\n}\n\n.section table.polka-stripes.table-danger th, .section table.polka-stripes.table-danger tfoot td {\n    background: #d43c3c;\n    color: white;\n    border: 2px solid #a75757;\n}\n\n.section table.polka-stripes.table-danger tbody td:first-child {\n    border-left: 2px solid #a75757;\n}\n\n.section table.polka-stripes.table-danger tbody td:last-child {\n    border-right: 2px solid #a75757;\n}\n\n.section table.polka-stripes.table-danger tbody tr:last-child td {\n    border-bottom: 2px solid #a75757;\n}\n\n.section table.polka-stripes.table-danger tbody tr:nth-child(even) td {\n    background: #e7d1d1;\n    color: #6A6A6A;\n}\n\n.section fieldset.fieldset-danger {\n    border: 2px solid #d43c3c;\n}\n\n.bg-color1, #agenda .shared-agenda {\n    background: #0a8e76;\n    color: white;\n}\n\n.bg-gradient-color1 {\n    background: linear-gradient(#996b95 0%, #0a8e76 100%);\n    color: white;\n}\n\n.bg-color2 {\n    background: #0a8e76;\n    color: white;\n}\n\n.bg-gradient-color2 {\n    background: linear-gradient(#bc809b 0%, #1e5239 100%);\n    color: white;\n}\n\n.bg-color3 {\n    background: #D8A479;\n    color: #6A6A6A;\n}\n\n.bg-gradient-color3 {\n    background: linear-gradient(#dfb390 0%, #cb864d 100%);\n    color: #6A6A6A;\n}\n\n.bg-color4 {\n    background: #0a8e76;\n    color: #6A6A6A;\n}\n\n.bg-gradient-color4 {\n    background: linear-gradient(#eee5b2 0%, #dfcd6a 100%);\n    color: #6A6A6A;\n}\n\n.bg-color5 {\n    background: #666666;\n    color: #6A6A6A;\n}\n\n.bg-gradient-color5 {\n    background: linear-gradient(#c3bdb8 0%, #9c9288 100%);\n    color: #6A6A6A;\n}\n\n.bg-color6 {\n    background: #E9E7D7;\n    color: #6A6A6A;\n}\n\n.bg-gradient-color6 {\n    background: linear-gradient(#edebde 0%, #cecaa6 100%);\n    color: #6A6A6A;\n}\n\n.bg-color7 {\n    background: #F8FAF4;\n    color: #6A6A6A;\n}\n\n.bg-gradient-color7 {\n    background: linear-gradient(#f9fbf6 0%, #d3e0ba 100%);\n    color: #6A6A6A;\n}\n\n.bg-color8 {\n    background: #948B82;\n    color: white;\n}\n\n.bg-gradient-color8 {\n    background: linear-gradient(#a69f97 0%, #7c736a 100%);\n    color: white;\n}\n\n.bg-info {\n    background: #0a8e76;\n    color: white;\n}\n\n.bg-gradient-info {\n    background: linear-gradient(#90b8c5 0%, #5793a7 100%);\n    color: white;\n}\n\n.bg-success {\n    background: #0a8e76;\n    color: white;\n}\n\n.bg-gradient-success {\n    background: linear-gradient(#aac590 0%, #7fa757 100%);\n    color: white;\n}\n\n.bg-warning {\n    background: #0a8e76;\n    color: #6A6A6A;\n}\n\n.bg-gradient-warning {\n    background: linear-gradient(#eee5b2 0%, #dfcd6a 100%);\n    color: #6A6A6A;\n}\n\n.bg-danger {\n    background: #d43c3c;\n    color: white;\n}\n\n.bg-gradient-danger {\n    background: linear-gradient(#c59090 0%, #a75757 100%);\n    color: white;\n}\n\n.row.outer-gutter {\n    padding: 1.5em;\n}\n\n.row.outer-gutter .col:last-child *:last-child {\n    margin-bottom: 0;\n}\n\n@media screen and (min-width: 769px) {\n    .row.outer-gutter .col *:last-child {\n        margin-bottom: 0;\n    }\n}\n\n.row:after {\n    content: \"\";\n    display: table;\n    clear: both;\n}\n\n.col {\n    float: left;\n}\n\n.col.align-right {\n    text-align: right;\n}\n\n.col.align-center {\n    text-align: center;\n}\n\n.row.inner-gutter {\n    margin-left: -1.5em;\n}\n\n.row.inner-gutter .col {\n    padding-left: 1.5em;\n}\n\n.element {\n    margin-bottom: 1.6em;\n}\n\n.col.span-1 {\n    width: 8.3333333333%;\n}\n\n.col.span-2 {\n    width: 16.6666666667%;\n}\n\n.col.span-3 {\n    width: 25%;\n}\n\n.col.span-4 {\n    width: 33.3333333333%;\n}\n\n.col.span-5 {\n    width: 41.6666666667%;\n}\n\n.col.span-6 {\n    width: 50%;\n}\n\n.col.span-7 {\n    width: 58.3333333333%;\n}\n\n.col.span-8 {\n    width: 66.6666666667%;\n}\n\n.col.span-9 {\n    width: 75%;\n}\n\n.col.span-10 {\n    width: 83.3333333333%;\n}\n\n.col.span-11 {\n    width: 91.6666666667%;\n}\n\n.col.span-12 {\n    width: 100%;\n}\n\n@media screen and (max-width: 768px) {\n    .element {\n        margin-bottom: 1.6em;\n    }\n\n    .row:not(.unbreakable) > .col[class*=\'span-\'] {\n        width: 100%;\n    }\n\n    .row.mobile-2-col .col[class*=\'span-\'] {\n        width: 50%;\n    }\n\n    .row.mobile-3-col .col[class*=\'span-\'] {\n        width: 33.3333333333%;\n    }\n\n    .row.mobile-4-col .col[class*=\'span-\'] {\n        width: 25%;\n    }\n}\n\ninput, select, textarea {\n    outline: none;\n}\n\n.page-area .element {\n    background: white;\n    border: 2px solid #8dbeb5;\n    border-top: 6px double #8dbeb5;\n    text-align: center;\n    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);\n}\n\n.page-area .element h3 {\n    padding: 0.75em;\n    margin: 0;\n    margin-top: -0.2em;\n    font-size: 2em;\n    padding-bottom: 0;\n}\n\n.page-area .element p {\n    padding: 0.75em;\n}\n\n.page-area .element img {\n    margin-top: -2em;\n    width: 4em;\n    padding-bottom: 0;\n}\n\n.page-area .element a.full-width {\n    display: block;\n    margin: 0.75em;\n}\n\n#index {\n    background-image: url(\"../non-essential-images/start-bg.jpg\");\n    background-size: cover;\n    background-position: center bottom;\n    background-attachment: fixed;\n}\n\n#hotel-img-1 {\n    background-image: url(\"../non-essential-images/Clarion-Hotel-Stockholm-Single-room.jpg\");\n    background-size: cover;\n    background-position: center bottom;\n}\n\n#hotel-img-2 {\n    background-image: url(\"../non-essential-images/Clarion-Hotel-Stockholm-Double-room.jpg\");\n    background-size: cover;\n    background-position: center bottom;\n}\n\n#hotel-img-3 {\n    background-image: url(\"../non-essential-images/Haymarket-By-Scandic-Single-room.jpg\");\n    background-size: cover;\n    background-position: center bottom;\n}\n\n.element.equal-height2 {\n    position: relative;\n    padding-bottom: 1em !important;\n}\n\n.element.equal-height2 p {\n    position: relative;\n}\n\n.same-position {\n    position: absolute;\n    bottom: 0;\n    left: 0;\n    width: 100%;\n    border-radius: 0 !important;\n}\n\n#agenda {\n    min-width: 800px;\n}\n\n#agenda td {\n    width: 22.5%;\n}\n\n#agenda td:first-child {\n    width: 10.0%;\n}\n\n#agenda td .label {\n    margin-top: 0.375em;\n}\n\n#agenda tbody tr {\n    border-bottom: 2px solid #8dbeb5;\n}\n\n.bg-palette {\n    font-size: 0;\n}\n\nh2.element-document-headline {\n    background: #265035;\n    color: white;\n    padding: 0.5rem;\n    font-weight: normal;\n    text-transform: uppercase;\n}\n\nh3.element-document-headline {\n    background: #e3e7ea;\n    padding: 0.5rem;\n    font-weight: normal;\n}\n\n.background-colors > .demo, .background-gradients > .demo {\n    width: 200px;\n    height: 200px;\n    padding: 10px;\n    display: inline-block;\n    text-align: center;\n    overflow: hidden;\n}\n\n.module {\n    border: 1px solid silver;\n    padding: 0.5rem;\n}\n\n#elements .session {\n    margin-bottom: 1em;\n}\n\n#elements .session-details {\n    border: 1px solid silver;\n    margin-bottom: 1em;\n    padding: 0 1em;\n}\n\n.event-plugin-item > .session-table > tbody > tr > td:first-child {\n    border-right: 2px dotted #8dbeb5;\n    padding-right: 0.75em;\n}\n\n.menu-bar {\n    list-style: none;\n    padding: 0;\n    font-size: 0;\n    border: 2px solid #0a8e76;\n    display: inline-block;\n    border-radius: 30px;\n    overflow: hidden;\n}\n\n.menu-bar li {\n    display: inline-block;\n}\n\n.menu-bar li a {\n    font-weight: bold;\n    font-size: 1rem;\n    padding: 0.75em 1.125em;\n    display: block;\n    border-right: 2px solid #0a8e76;\n    background: #0a8e76;\n    color: white;\n}\n\n.menu-bar li:hover > a, .menu-bar li a.active {\n    text-decoration: none;\n    background: #1e5239;\n    color: white;\n}\n\n.menu-bar li:last-child a {\n    border-right: none;\n}\n\n.event-plugin-location-list .event-plugin-table {\n    width: auto !important;\n}\n\n.event-plugin-location-list .event-plugin-description .img {\n    width: 40%;\n    height: 18em;\n    margin-left: 1em;\n    margin-bottom: 1em;\n    float: right;\n    background-size: cover;\n    background-position: center;\n}\n\n.event-plugin-location-list .event-plugin-description .img.oaxen {\n    background-image: url(\"../non-essential-images/oaxen.jpeg\");\n}\n\n.event-plugin-location-list .event-plugin-description .img.omakase {\n    background-image: url(\"../non-essential-images/omakase.jpg\");\n}\n\n.contact-details {\n    border: 2px solid #d7e2bf;\n    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);\n    margin-bottom: 0;\n}\n\n.payment-method i {\n    width: 1em;\n}\n\n#welcome {\n    background: url(\"../non-essential-images/start-bg.jpg\");\n    background-size: cover;\n    background-position: center -17em;\n}\n\n.welcome {\n    background: 0;\n    width: 100%;\n}\n\n.welcome p span {\n    color: black;\n    font-size: 1.5em;\n    font-weight: bold;\n    text-shadow: 1px 1px 0px white;\n    margin-bottom: 0.75em;\n    display: inline-block;\n}\n\n.welcome p a {\n    font-weight: bold;\n    font-size: 2em !important;\n}\n\n.welcome .headline-wrapper {\n    text-align: center;\n    width: 100%;\n}\n\n.welcome h1, .welcome h2 {\n    border-bottom: none;\n    margin-bottom: 0;\n    padding: 0.25em 0.5em;\n    background: rgba(0, 0, 0, 0.65);\n    color: white;\n    display: inline-block;\n    border-radius: 0.125em;\n    text-align: center;\n}\n\n.welcome h1 {\n    -ms-transform: rotate(-3deg);\n    -webkit-transform: rotate(-3deg);\n    transform: rotate(-3deg);\n    font-size: 8em;\n    margin-bottom: 0;\n}\n\n.welcome h2 {\n    margin-top: -1em;\n    -ms-transform: rotate(3deg);\n    -webkit-transform: rotate(3deg);\n    transform: rotate(3deg);\n    background: #0a8e76;\n    font-size: 4.2em;\n    margin-right: -2em;\n}\n\n/*Mahedi 25-09-2018*/\n\n/* Plugin - Photo Gallery*/\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item {\n    border: none;\n    border-radius: 0;\n    margin: 0;\n    background-size: cover !important;\n    background-position: center;\n    cursor: pointer;\n    height: 30vw;\n    position: relative;\n    display: block;\n    float: left;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item img {\n    display: none !important;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item .photo-submitter {\n    position: absolute;\n    left: 0;\n    bottom: 0;\n    background: rgba(0, 0, 0, 0.7);\n    color: white;\n    padding: 0.5em 0.5em;\n    font-size: 0.7em;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item .photo-submitter label {\n    display: none;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(1) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(2) {\n    width: 66.66667%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(3) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(4) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(5) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(6) {\n    width: 66.66667%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(7) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(8) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(9) {\n    width: 66.66667%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(10) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(11) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item:nth-child(12) {\n    width: 33.33333%;\n}\n\n.event-plugin-photo-gallery .event-plugin-list .event-plugin-item .event-plugin-description .photo-comment {\n    display: none;\n}\n\n.event-plugin-photo-upload .event-plugin-photo-upload-file-select-button {\n    display: inline-block;\n}\n\n.event-plugin-photo-upload .event-plugin-photo-upload-file-select-button::after {\n    font-family: \"Font Awesome 5 Pro\";\n    font-weight: 500;\n    content: \"ï€¾\";\n}\n\n.event-plugin-photo-upload .event-plugin-photo-upload-file-select-button input {\n    display: none;\n}\n\n.event-plugin-photo-upload .event-plugin-photo-upload-comment-label {\n    display: none;\n}\n\n.event-plugin-photo-upload .event-plugin-photo-upload-button::after {\n    font-family: \"Font Awesome 5 Pro\";\n    font-weight: 500;\n    content: \"ïƒ®\";\n}\n\n.event-plugin-table.event-plugin-economy-order-table,\n.early-bird-table.event-plugin-economy-order-table,\ntable.event-plugin-economy-order-table {\n    width: 100%;\n}\n\n.event-plugin-table.event-plugin-economy-order-table tr:last-child td,\n.early-bird-table.event-plugin-economy-order-table tr:last-child td,\ntable.event-plugin-economy-order-table tr:last-child td {\n    background: #2b4e30;\n    border: none;\n    color: white;\n}\n\n.event-plugin-table.event-plugin-economy-balance-table td:last-child,\n.early-bird-table.event-plugin-economy-balance-table td:last-child,\ntable.event-plugin-economy-balance-table td:last-child {\n    vertical-align: middle;\n    text-align: center;\n}\n\n.event-plugin-table.event-plugin-economy-balance-table tr:last-child td,\n.early-bird-table.event-plugin-economy-balance-table tr:last-child td,\ntable.event-plugin-economy-balance-table tr:last-child td {\n    background: #2b4e30;\n    border: none;\n    color: white;\n}\n\n.event-plugin-table.event-plugin-economy-vat-table tr:last-child td,\n.early-bird-table.event-plugin-economy-vat-table tr:last-child td,\ntable.event-plugin-economy-vat-table tr:last-child td {\n    background: #2b4e30;\n    border: none;\n    color: white;\n}\n\n.economy-order-number, .economy-status, .economy-due-date, .economy-amount-due {\n    font-family: \"AvenirNext-DemiBold\", sans-serif;\n}\n\n.economy-order-number span, .economy-status span, .economy-due-date span,\n.economy-amount-due span {\n    font-family: \"AvenirNext-Regular\", sans-serif;\n}\n\n.section .event-plugin-attendee-list td {\n    border: 1px solid #378e76;\n}\n\n/*Copied from old*/\n\n#content.loading-page {\n    text-align: center;\n}\n\n#content.loading-page * {\n    display: none;\n}\n\n#content.loading-page:before {\n    display: block;\n    content: \'\';\n    box-sizing: border-box;\n    width: 2em;\n    height: 2em;\n    margin: 0 auto;\n    border-radius: 50%;\n    border: 5px solid white;\n    border-top-color: #40ABDE;\n    animation: loading 0.6s linear infinite;\n    margin-top: 2em;\n    margin-bottom: 2em;\n}\n\n@keyframes loading {\n    to {\n        transform: rotate(360deg);\n    }\n}\n\n/*#header-wrapper {*/\n/*width: 100%;*/\n/*background: #BE9E56;*/\n/*position: fixed;*/\n/*top: 0;*/\n/*z-index: 999;*/\n/*height: 3.2em;*/\n/*}*/\n\n/*#header-wrapper #header {*/\n/*margin: 0 auto;*/\n/*max-width: 960px;*/\n/*padding: 0.5em 2em;*/\n/*}*/\n\n/*#header-wrapper #header #logo {*/\n/*height: 2.2em;*/\n/*float: left;*/\n/*}*/\n\n*, *:before, *:after {\n    box-sizing: border-box;\n}\n\nimg {\n    display: block;\n}\n\n[data-req=\"1\"] .event-question-label-title:after {\n    content: \"*\";\n    margin-left: 0.25em;\n    color: #D0021B;\n}\n\ninput:focus, select:focus, textarea:focus, button:focus {\n    outline: none;\n}\n\nbody, html {\n    width: 100%;\n    padding-top: 20px;\n    font-family: \'AvenirNext-Regular\', sans-serif;\n    font-family: \'Quicksand\', sans-serif;\n    font-size: 16px;\n}\n\n/*body {*/\n/*margin: 0;*/\n/*font-size: 16px;*/\n/*background: #262928;*/\n/*color: #666;*/\n/*}*/\n\n@media screen and (max-width: 768px) {\n    body {\n        font-size: 13px !important;\n    }\n}\n\n@media screen and (min-width: 1280px) {\n    body {\n        font-size: 20px !important;\n    }\n}\n\n.only-small-screens {\n    display: none;\n}\n\n@media screen and (max-width: 960px) {\n    .only-small-screens {\n        display: inherit;\n    }\n}\n\n.only-large-screens {\n    display: inherit;\n}\n\n@media screen and (max-width: 960px) {\n    .only-large-screens {\n        display: none;\n    }\n}\n\n.scroll-x {\n    max-width: 100%;\n    overflow-x: auto;\n    margin-bottom: 1em;\n}\n\n.scroll-x::-webkit-scrollbar {\n    -webkit-appearance: none;\n    width: 14px;\n    height: 14px;\n}\n\n.scroll-x::-webkit-scrollbar-thumb {\n    border-radius: 8px;\n    border: 3px solid #262928;\n    background-color: #40ABDE;\n}\n\n.event-plugin-session-checkbox .event-plugin-title label,\n.event-plugin-session-radio-button .event-plugin-title label {\n    cursor: pointer;\n}\n\n.event-plugin-submit-button .form-submit-button {\n    margin-top: 1em;\n}\n\n.event-plugin-multiple-registration .event-plugin-multiple-registration-current-count {\n    display: inline-block;\n    font-weight: normal;\n    color: white;\n    border-radius: 1em;\n}\n\n.event-plugin-multiple-registration .event-plugin-list .event-plugin-item {\n    margin-bottom: 1em;\n}\n\n.event-plugin-multiple-registration .event-plugin-list .event-plugin-item:last-child {\n    margin-bottom: 0;\n}\n\n.event-plugin-multiple-registration .event-plugin-list .event-plugin-item .section {\n    padding: 1em 0;\n}\n\n.event-plugin-multiple-registration .event-plugin-list .event-plugin-item .event-plugin-item-information {\n    background: #262928;\n    position: relative;\n}\n\n\n.event-plugin-multiple-registration .event-plugin-list .event-plugin-item .event-plugin-item-information .event-plugin-multiple-registration-delete-attendee-button-from-inline {\n    position: absolute;\n    padding: 0.5em 1em;\n    top: 0;\n    right: 0;\n    z-index: 1;\n    color: white;\n    border-radius: 0;\n    margin: 0;\n    border: 0;\n    font-size: 0.75em;\n}\n\n#dialoge {\nheight: 100%;\nwidth: 100%;\nbackground: rgba(0, 0, 0, 0.5);\nposition: fixed;\nz-index: 1005;\noverflow-y: auto;\ndisplay: none;\ntop: 0;\n}\n\n#dialoge.visible {\ndisplay: block;\n}\n\n#dialoge .close-dialouge {\nposition: absolute;\ntop: 0;\nright: 0;\npadding: 0.75em;\npadding: 0.75em;\nbackground: #B97979;\ncolor: white;\ncursor: pointer;\nz-index: 1;\n}\n\n#dialoge .close-dialouge:after {\ndisplay: inline-block;\ncontent: \"?\";\nfont-family: FontAwesome;\n}\n\n#dialoge .close-dialouge:hover {\nbackground: #a75757;\ncolor: white;\n}\n\n#dialoge .dialogue-content {\nmargin: 0 auto;\nmargin-top: 1.6em;\noverflow: hidden;\nbox-shadow: 0px 15px 30px rgba(0, 0, 0, 0.5);\nbackground: white;\nposition: relative;\n}\n\n@media screen and (max-width: 768px) {\n#dialoge .dialogue-content {\nwidth: 100%;\nmargin: 0;\nposition: fixed;\noverflow-y: auto;\nmax-height: 100%;\n}\n\n#dialoge .dialogue-content .dialoge-menu {\nposition: fixed;\ntop: 0;\nz-index: 1;\n}\n\n#dialoge .dialogue-content .section {\nmargin-top: 2.75em;\n}\n}\n\n@media screen and (min-width: 769px) {\n#dialoge .dialogue-content {\nmax-width: 791.04px;\n}\n}\n\n#dialoge .dialogue-content .dialoge-menu {\nwidth: 100%;\nmargin-bottom: 0;\nlist-style: none;\npadding: 0;\nwhite-space: nowrap;\nfont-size: 0;\noverflow-x: auto;\n-webkit-touch-callout: none;\n-webkit-user-select: none;\n-khtml-user-select: none;\n-moz-user-select: none;\n-ms-user-select: none;\nuser-select: none;\nbackground: #0a8e76;\nmargin-right: 2.5em !important;\n}\n\n#dialoge .dialogue-content .dialoge-menu li {\ndisplay: inline-block;\nfont-size: 16px;\nborder-right: 2px solid #0a8e76;\ncursor: pointer;\n}\n\n#dialoge .dialogue-content .dialoge-menu li a {\ndisplay: inline-block;\npadding: 0.75em 1.125em;\ncolor: white;\nbackground: #7C5578;\n}\n\n#dialoge .dialogue-content .dialoge-menu li a:hover {\nbackground-color: #3f2c3d;\ncolor: white;\n}\n\n#dialoge .dialogue-content .dialoge-menu li:last-child {\nmargin-right: 2.5em;\n}\n\n#dialoge .dialogue-content .dialoge-menu li.active a,\n#dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button,\n#dialoge .dialogue-content .dialoge-menu li.active a:hover,\n#dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button:hover {\nbackground: white;\ncolor: #6A6A6A;\n}\n\n#dialoge .dialogue-content .dialoge-menu li.active a:after,\n#dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button:after,\n#dialoge .dialogue-content .dialoge-menu li.active a:hover:after,\n#dialoge .dialogue-content .dialoge-menu li.active .dialoge-menu-close-button:hover:after {\ncolor: #6A6A6A;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button {\ndisplay: inline-block;\npadding: 0.75em;\ncolor: white;\nbackground: #7C5578;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button:hover {\nbackground-color: #3f2c3d;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button:after {\ndisplay: inline-block;\ncontent: \"?\";\nfont-family: FontAwesome;\n}\n\n#dialoge .dialogue-content .dialoge-menu li .dialoge-menu-close-button:hover:after {\ncolor: white;\n}\n\n#dialoge .dialogue-content .section {\npadding: 1.6em;\nborder-radius: 0;\nmargin-bottom: 0;\n}\n\n#dialoge .dialogue-content .section *:last-child {\nmargin-bottom: 0;\n}\n\n.row {\n    display: flex;\n    margin-bottom: 0;\n    max-width: 1280px;\n    margin: 0 auto;\n}\n\n.row:last-child {\n    margin-bottom: 0;\n}\n\n.row.row-margin {\n    margin: 0 2em;\n}\n\n.row.row-gutter .col {\n    margin: 0 1em;\n}\n\n.row.row-gutter .col:last-child {\n    margin: 0 0 0 1em;\n}\n\n.row.row-gutter .col:first-child {\n    margin: 0 1em 0 0;\n}\n\n.row .col {\n    flex: 1;\n    padding: 0 2em 0 2em;\n}\n\n.row.no-col-padding .col {\n    padding: 0;\n    border: 2px solid green;\n}\n\n#content .row:last-child .col:last-child {\n    padding-bottom: 0;\n}\n\n@media only screen and (min-width: 0px) and (max-width: 960px) {\n    .button:not(.dropdown-toggle),\n    .event-plugin-button:not(.event-plugin-multiple-registration-delete-attendee-button-from-inline),\n    .form-submit-button, ul.information, ul.information li a, ul.information a {\n        width: 100%;\n        display: inline-block;\n        text-align: center;\n    }\n\n    .row:not(.unbreakable) {\n        flex-wrap: wrap;\n    }\n\n    .row:not(.unbreakable) .col {\n        flex-basis: 100%;\n        max-width: 100%;\n        word-wrap: break-word;\n    }\n\n    .row.row-gutter {\n        flex-wrap: wrap;\n    }\n\n    .row.row-gutter .col, .row.row-gutter .col:last-child,\n    .row.row-gutter .col:first-child {\n        margin-left: 0;\n        margin-right: 0;\n    }\n}\n\n.settle-order-button {\n    margin: 0 0 1em 0;\n}\n\n.order-info {\n    display: inline-block;\n    padding: 0.5em;\n    border: 1px solid white;\n    margin-bottom: 1em;\n}\n\ntr.cost label.event-plugin-label {\n    display: none;\n}\n\n.economy-order-number, .economy-status, .economy-due-date, .economy-amount-due {\n    font-family: \'Quicksand\', sans-serif;\n    font-weight: 500;\n}\n\n.economy-order-number span, .economy-status span, .economy-due-date span,\n.economy-amount-due span {\n    font-family: \'Quicksand\', sans-serif;\n}\n\n.event-plugin-logout span {\n    display: block;\n    margin-bottom: 1em;\n}\n\ninput[type=\"checkbox\"] {\n    margin-right: 0.5em;\n}\n\n#logout-button {\n    float: right;\n    padding: 0.6em 1em;\n    border-radius: 0px;\n    color: white;\n    background: #40ABDE;\n    border: none;\n    transition: background 100ms ease-in-out;\n    cursor: pointer;\n    font-size: 0.85em;\n    display: inline-block;\n    font-family: \'Quicksand\', sans-serif;\n    text-transform: uppercase;\n    margin: 0;\n    top: 0;\n}\n\n#logout-button:hover {\n    background: #2393c8;\n    color: white;\n    text-decoration: none;\n    transition: background 100ms ease-in-out;\n}\n\nhr {\n    border: none;\n    margin: 2em 0;\n    height: 2px;\n    background: #BE9E56;\n}\n\n.event-plugin-pdf-button {\n    text-align: center;\n}\n\n.event-plugin-archive-messages .event-plugin-item {\n    padding: 0.5em;\n    margin-bottom: 0.5em;\n    color: black;\n}\n\ntr.session {\n    cursor: pointer;\n}\n\na.attendee-details, a.location-details {\n    cursor: pointer;\n}\n\nLogo\n.section.header {\nbackground-color: #7c5578;\nposition: fixed;\ntop: 0;\nwidth: 100%;\nz-index: 998;\n}\n\n.section.header .logo {\n    height: 2.5em;\n    width: auto;\n    margin: 1.25em 0;\n    display: block;\n}\n\n/*Menu*/\n\n.section.header .row {\n    position: relative;\n}\n\n/*Language select*/\n#language-select {\n    list-style: none;\n    position: absolute;\n    height: 2.5em;\n    right: 2.5em;\n    margin: 0;\n    display: flex;\n    justify-content: center;\n}\n\n@media only screen and (min-width: 0px) and (max-width: 45em) {\n    #language-select {\n        margin-right: 2.5em;\n    }\n}\n\n#language-select .current:before {\n    -webkit-font-smoothing: antialiased;\n    content: \"\\f0ac\";\n    font-family: \"FontAwesome\";\n    margin-right: 0.625em;\n}\n#language-select li {\n    display: block;\n    padding: 0;\n    position: relative;\n    display: flex;\n    justify-content: center;\n}\n\n#language-select li:hover > ul {\n    display: block;\n}\n\n#language-select li a {\n    padding: 2.5em 0;\n    color: white;\n    text-decoration: none;\n    display: flex;\n    align-items: center;\n}\n\n#language-select li ul {\n    display: none;\n    position: absolute;\n    top: 4.375em;\n    left: 50%;\n    transform: translateX(-50%);\n    background: #FFFFFF;\n    padding: 0;\n    border: 1px solid #BCBEC0;\n    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);\n}\n\n#language-select li ul:after, #language-select li ul:before {\n    bottom: 100%;\n    left: 50%;\n    border: solid transparent;\n    content: \" \";\n    height: 0;\n    width: 0;\n    position: absolute;\n    cursor: pointer;\n}\n\n#language-select li ul:after {\n    border-color: rgba(255, 255, 255, 0);\n    border-bottom-color: #FFFFFF;\n    border-width: 10px;\n    margin-left: -10px;\n}\n\n#language-select li ul:before {\n    border-color: rgba(194, 225, 245, 0);\n    border-bottom-color: #BCBEC0;\n    border-width: 11px;\n    margin-left: -11px;\n}\n\n#language-select li ul li {\n    list-style: none;\n    margin: 0;\n    display: block;\n    padding: 0;\n}\n\n#language-select li ul li a {\n    text-align: left;\n    color: black;\n    padding: 0.625em 1.25em;\n    width: 100%;\n    white-space: nowrap;\n    transition: color 0.2s ease;\n    font-family: \'Quicksand\', sans-serif;\n    transition: background 0.2s ease, color 0.2s ease;\n}\n\n#language-select li ul li a:hover, #language-select li ul li a.active {\n    border-bottom: none;\n    background: #ae6686;\n    transition: background 0.2s ease, color 0.2s ease;\n    color: #FFFFFF;\n}\n\n.session-detail-link {\n    font-size: 14px;\n    float: left;\n    padding: 5px;\n    background: #4542c5;\n    color: #fff;\n    margin-right: 5px;\n}\n\n.status.attending {\n    font-size: 14px;\n    float: left;\n    padding: 5px;\n    background: #4542c5;\n    color: #fff;\n    margin-right: 5px;\n}\n\n.event-plugin-description {\n    font-size: 14px;\n    float: left;\n    padding: 5px;\n    background: #4542c5;\n    color: #fff;\n    margin-right: 5px;\n}\n\n.event-plugin-description p {\n    margin-bottom: 0px;\n}\n\n.status.rsvp-ended {\n    font-size: 14px;\n    float: left;\n    padding: 5px;\n    background: #4542c5;\n    color: #fff;\n    margin-right: 5px;\n}\n\n\n/*Menu*/\n\n@media only screen and (min-width: 0px) and (max-width: 45em) {\n    .section.header input {\n        display: none;\n    }\n\n    .section.header label {\n        position: absolute;\n        top: 0;\n        right: 1.25em;\n        z-index: 1001;\n        -webkit-user-select: none;\n        -khtml-user-select: none;\n        -moz-user-select: none;\n        -ms-user-select: none;\n        user-select: none;\n        cursor: pointer;\n        font-size: 1.5em;\n        color: white;\n        transition: color 0.25s ease;\n        height: 2.5em;\n        width: 2.5em;\n        text-align: center;\n        margin-top: -0.25em;\n    }\n\n    .section.header label:hover {\n        transition: color 0.25s ease;\n        color: #B97979;\n    }\n\n    .section.header label:before {\n        content: \"ïƒ‰\";\n        font-family: \"FontAwesome\";\n    }\n\n    .section.header input:checked + label:before {\n        content: \"ï€\";\n        font-family: \"FontAwesome\";\n    }\n\n    .section.header ul.menu {\n        z-index: 1000;\n        display: block;\n        left: 0;\n        width: 100%;\n        background: #000000;\n        margin: 0;\n        position: fixed;\n        padding-left: 0;\n        padding-bottom: 0;\n        transition: padding-bottom 0.25s ease;\n    }\n\n    .section.header ul.menu a {\n        width: 100%;\n        text-align: left;\n        display: block;\n        color: #000000;\n        text-decoration: none;\n        font-size: 1.25em;\n        padding-left: 2.5em;\n        padding-top: 0em;\n        background: white;\n        border-bottom: none;\n        height: 0;\n        overflow: hidden;\n        transition: height 0.25s ease, color 0.25s ease;\n    }\n\n    .section.header ul.menu li:hover a, .section.header ul.menu li.current a,\n    .section.header ul.menu li.selected a {\n        background: white;\n    }\n\n    .section.header input:checked + label + ul.menu {\n        padding-bottom: 4px;\n        transition: padding-bottom 0.25s ease;\n    }\n\n    .section.header input:checked + label + ul.menu a {\n        height: 3em;\n        transition: height 0.25s ease, color 0.25s ease;\n        overflow: auto;\n        padding-top: 0.65em;\n        border-bottom: 1px solid #EDEDED;\n    }\n\n    .section.header input:checked + label + ul.menu a:after {\n        content: \"ï”\";\n        font-family: \"FontAwesome\";\n        color: #BCBEC0;\n        float: right;\n        margin-right: 2.5em;\n        transition: color 0.25s ease;\n    }\n\n    .section.header input:checked + label + ul.menu a:hover {\n        color: red;\n    }\n\n    .section.header input:checked + label + ul.menu a:hover:after {\n        color: red;\n        transition: color 0.25s ease;\n    }\n}\n\n\n@media only screen and (min-width: 45em) {\n    .section.header .col.span-12 {\n        display: flex;\n        justify-content: space-between;\n    }\n\n    .section.header input {\n        display: none;\n    }\n\n    .section.header ul.menu {\n        list-style: none;\n        width: 100%;\n        padding: 0;\n        text-align: center;\n        left: 0;\n        top: 0;\n        width: 100%;\n        margin: 0;\n        display: flex;\n        justify-content: center;\n        align-items: stretch;\n    }\n\n    .section.header ul.menu li:hover > ul {\n        display: block;\n    }\n\n    .section.header ul.menu li:hover > a {\n        color: #ebe0a2;\n        transition: color 0.2s ease;\n    }\n\n    .section.header ul.menu li {\n        margin: 0 0.625em;\n        transition: border-bottom 0.1s ease, color 0.1s ease;\n        position: relative;\n        display: flex;\n    }\n\n    .section.header ul.menu li a {\n        text-decoration: none;\n        color: #FFFFFF;\n        transition: color 0.2s ease;\n        font-size: 16px;\n        display: flex;\n        align-items: center;\n    }\n\n    .section.header ul.menu li ul {\n        display: none;\n        position: absolute;\n        top: 4.375em;\n        left: 50%;\n        transform: translateX(-50%);\n        background: #FFFFFF;\n        padding: 0;\n        border: 0px solid #685f80;\n        box-shadow: 2px 2px 10px rgba(66, 58, 58, 0.95);\n    }\n\n    .section.header ul.menu li ul:after, .section.header ul.menu li ul:before {\n        bottom: 100%;\n        left: 50%;\n        border: solid transparent;\n        content: \" \";\n        height: 0;\n        width: 0;\n        position: absolute;\n        cursor: pointer;\n    }\n\n    .section.header ul.menu li ul:after {\n        border-color: rgba(255, 255, 255, 0);\n        border-bottom-color: #FFFFFF;\n        border-width: 10px;\n        margin-left: -10px;\n    }\n\n    .section.header ul.menu li ul:before {\n        border-color: rgba(194, 225, 245, 0);\n        border-bottom-color: #BCBEC0;\n        border-width: 11px;\n        margin-left: -11px;\n    }\n\n    .section.header ul.menu li ul li {\n        list-style: none;\n        margin: 0;\n        display: block;\n        padding: 0;\n    }\n\n    .section.header ul.menu li ul li a {\n        text-align: left;\n        color: black;\n        padding: 0.625em 1.25em;\n        width: 100%;\n        white-space: nowrap;\n        transition: color 0.2s ease;\n        transition: background 0.2s ease, color 0.2s ease;\n    }\n\n    .section.header ul.menu li ul li a:hover, .section.header ul.menu li ul li a.active {\n        border-bottom: none;\n        background: #498e76;\n        transition: background 0.2s ease, color 0.2s ease;\n        color: #FFFFFF;\n    }\n    .section.header ul.menu input:checked + label + ul.menu {\n        right: 0;\n        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);\n        transition: right 0.15s ease;\n    }\n}\n.section.header {\n    background: #378e76;\n    margin: 0px;\n    margin-bottom: 10px;\n    border-radius: 0px;\n}\n.section.header ul.menu li ul li ul:before{\n    display: none;\n    content: unset;\n}\n.section.header ul.menu li ul li ul {\n    right: -131px;\n    top: 10px;\n    left: auto;\n}\n.section.header ul.menu li ul li {\n    position: relative;\n}','2018-11-14 00:00:00.000000','2018-11-14 00:00:00.000000',2,1,1);
/*!40000 ALTER TABLE `event_stylesheets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `start` date NOT NULL,
  `end` date NOT NULL,
  `description` longtext COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `address` longtext COLLATE utf8_unicode_ci,
  `is_show` tinyint(1) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `admin_id` int(11) DEFAULT NULL,
  `created_by_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `events_156f41ed` (`admin_id`),
  KEY `events_e93cb7eb` (`created_by_id`),
  KEY `events_49fa5cc1` (`last_updated_by_id`),
  CONSTRAINT `events_admin_id_449667661a29db75_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `events_created_by_id_83e1552a4a91862_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `events_last_updated_by_id_71a84ba95642f72_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (1,'Default Project','2017-03-14 10:23:37.000000','2017-03-01','2019-01-01','default project','default-project','Dhaka,Bangladesh',1,'2017-03-14 10:23:37.000000',1,1,1);
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `export_notification`
--

DROP TABLE IF EXISTS `export_notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `export_notification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status` smallint(6) NOT NULL,
  `request_time` datetime(6) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `file_name` (`file_name`),
  KEY `export_notification_156f41ed` (`admin_id`),
  KEY `export_notification_4437cfac` (`event_id`),
  CONSTRAINT `export_notification_admin_id_26dc3bcc2aca54ee_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `export_notification_event_id_338b661209ad3403_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `export_notification`
--

LOCK TABLES `export_notification` WRITE;
/*!40000 ALTER TABLE `export_notification` DISABLE KEYS */;
/*!40000 ALTER TABLE `export_notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `export_rules`
--

DROP TABLE IF EXISTS `export_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `export_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `preset` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created_at` date NOT NULL,
  `modified_at` date NOT NULL,
  `export_order` int(11) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `export_rules_e93cb7eb` (`created_by_id`),
  KEY `export_rules_0e939a4f` (`group_id`),
  CONSTRAINT `export_rules_created_by_id_6f72ffcc48bb750f_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `export_rules_group_id_2c5e18cc00af4fc3_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `export_rules`
--

LOCK TABLES `export_rules` WRITE;
/*!40000 ALTER TABLE `export_rules` DISABLE KEYS */;
INSERT INTO `export_rules` VALUES (1,'All Attendees','{\"questions\": \"1,2,3,4,6\", \"sessions\": \"\", \"rule_id\": \"2\", \"uid\": false, \"rdate\": false, \"udate\": false, \"secret\": false, \"bid\": false, \"attGroup\": false, \"attTag\": false, \"hotel\": false, \"flight\": false, \"export_type\": \"attendee_edit\", \"hotel_columns\": \"\", \"economy_columns\": \"\", \"include_import_header\": false}','2018-11-30','2018-11-30',1,1,9);
/*!40000 ALTER TABLE `export_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `export_state`
--

DROP TABLE IF EXISTS `export_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `export_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status` int(11) NOT NULL,
  `created` datetime(6) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `export_state_156f41ed` (`admin_id`),
  KEY `export_state_4437cfac` (`event_id`),
  CONSTRAINT `export_state_admin_id_1ffe4f9266102e05_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `export_state_event_id_2fde97754aba4750_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `export_state`
--

LOCK TABLES `export_state` WRITE;
/*!40000 ALTER TABLE `export_state` DISABLE KEYS */;
INSERT INTO `export_state` VALUES (1,'exported_files/Default Project/All_Attendees_2018_11_30_16_10_12.xlsx',0,'2018-11-30 10:10:14.340066',1,1);
/*!40000 ALTER TABLE `export_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `general_tags`
--

DROP TABLE IF EXISTS `general_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `general_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `category` enum('session','hotel','room','travel') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `general_tags_event_id_16dfb25dceb8ca9c_fk_events_id` (`event_id`),
  CONSTRAINT `general_tags_event_id_16dfb25dceb8ca9c_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `general_tags`
--

LOCK TABLES `general_tags` WRITE;
/*!40000 ALTER TABLE `general_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `general_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group_permissions`
--

DROP TABLE IF EXISTS `group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `access_level` enum('read','write','none') COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `group_permissions_156f41ed` (`admin_id`),
  KEY `group_permissions_0e939a4f` (`group_id`),
  CONSTRAINT `group_permissions_admin_id_5aa133bb2186e660_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `group_permissions_group_id_34895b6e06b175f5_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group_permissions`
--

LOCK TABLES `group_permissions` WRITE;
/*!40000 ALTER TABLE `group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name_lang` longtext COLLATE utf8_unicode_ci,
  `type` enum('attendee','session','hotel','filter','payment','question','location','travel','export_filter','menu','email') COLLATE utf8_unicode_ci NOT NULL,
  `color` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `group_order` int(11) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `is_searchable` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `groups_event_id_561af8750dacedc8_fk_events_id` (`event_id`),
  CONSTRAINT `groups_event_id_561af8750dacedc8_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'Default',NULL,'question',NULL,1,1,0,'2017-04-04 06:23:45.000000','2017-04-04 06:24:02.000000',1),(2,'temporary-filter',NULL,'filter',NULL,1,1,0,'2017-04-04 06:23:45.000000','2017-04-04 06:24:02.000000',1),(3,'Attending',NULL,'attendee',NULL,1,1,0,'2017-04-04 06:23:45.000000','2017-04-04 06:24:02.000000',1),(4,'Not Attending',NULL,'attendee',NULL,2,1,0,'2017-04-04 06:23:45.000000','2017-04-04 06:24:02.000000',1),(5,'Default Menu Group',NULL,'menu',NULL,1,1,1,'2017-04-25 15:26:54.000000','2017-04-25 15:26:54.000000',1),(6,'Default Session Group',NULL,'session',NULL,1,1,1,'2017-04-25 15:27:06.000000','2017-04-25 15:27:06.000000',1),(7,'Default Hotel Group',NULL,'hotel',NULL,1,1,1,'2017-04-25 15:27:15.000000','2017-04-25 15:27:15.000000',1),(8,'Default Filter Group',NULL,'filter',NULL,2,1,1,'2017-04-25 15:27:25.000000','2017-04-25 15:27:25.000000',1),(9,'Default Export Group',NULL,'export_filter',NULL,1,1,1,'2017-04-25 15:27:41.000000','2017-04-25 15:27:41.000000',1),(10,'Default Location Group',NULL,'location',NULL,1,1,1,'2017-04-25 15:28:08.000000','2017-04-25 15:28:08.000000',1),(11,'Default Travel Group',NULL,'travel',NULL,1,1,1,'2017-04-25 15:28:19.000000','2017-04-25 15:28:19.000000',1),(12,'*',NULL,'email',NULL,1,1,1,'2017-04-25 15:28:43.000000','2017-04-25 15:28:43.000000',1),(13,'25',NULL,'payment',NULL,1,1,1,'2017-12-06 08:39:05.000000','2017-12-06 08:39:05.000000',1),(14,'Questions',NULL,'question',NULL,2,1,1,'2018-01-15 13:19:30.000000','2018-01-15 13:19:30.000000',1);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hotels`
--

DROP TABLE IF EXISTS `hotels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hotels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name_lang` longtext COLLATE utf8_unicode_ci,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `group_id` int(11) NOT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hotels_group_id_7d896cb9ba65315_fk_groups_id` (`group_id`),
  KEY `hotels_e274a5da` (`location_id`),
  CONSTRAINT `hotels_group_id_7d896cb9ba65315_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`),
  CONSTRAINT `hotels_location_id_65a17b30d1a36e96_fk_locations_id` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hotels`
--

LOCK TABLES `hotels` WRITE;
/*!40000 ALTER TABLE `hotels` DISABLE KEYS */;
INSERT INTO `hotels` VALUES (1,'Regency Hotel','{\"6\": \"Regency Hotel\"}','2018-11-30 09:46:18.088394','2018-11-30 09:46:18.088434',7,1);
/*!40000 ALTER TABLE `hotels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `import_change_request`
--

DROP TABLE IF EXISTS `import_change_request`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `import_change_request` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `changed_data` longtext COLLATE utf8_unicode_ci NOT NULL,
  `status` smallint(6) NOT NULL,
  `type` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) DEFAULT NULL,
  `approved_by_id` int(11) DEFAULT NULL,
  `event_id` int(11) NOT NULL,
  `imported_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `import_change_request_471c3cd5` (`approved_by_id`),
  KEY `import_change_request_4437cfac` (`event_id`),
  KEY `import_change_request_1ba9c431` (`imported_by_id`),
  CONSTRAINT `import_change_reques_approved_by_id_4fb01134a527d9ec_fk_users_id` FOREIGN KEY (`approved_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `import_change_reques_imported_by_id_137f6c53899139bc_fk_users_id` FOREIGN KEY (`imported_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `import_change_request_event_id_3107267811b7599c_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `import_change_request`
--

LOCK TABLES `import_change_request` WRITE;
/*!40000 ALTER TABLE `import_change_request` DISABLE KEYS */;
/*!40000 ALTER TABLE `import_change_request` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `import_change_status`
--

DROP TABLE IF EXISTS `import_change_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `import_change_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` longtext COLLATE utf8_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8_unicode_ci,
  `duplicate_attendees` longtext COLLATE utf8_unicode_ci,
  `status` smallint(6) NOT NULL,
  `import_change_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `im_import_change_id_738ac94bffb13527_fk_import_change_request_id` (`import_change_id`),
  CONSTRAINT `im_import_change_id_738ac94bffb13527_fk_import_change_request_id` FOREIGN KEY (`import_change_id`) REFERENCES `import_change_request` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `import_change_status`
--

LOCK TABLES `import_change_status` WRITE;
/*!40000 ALTER TABLE `import_change_status` DISABLE KEYS */;
/*!40000 ALTER TABLE `import_change_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `locations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `name_lang` longtext COLLATE utf8_unicode_ci,
  `description` longtext COLLATE utf8_unicode_ci,
  `description_lang` longtext COLLATE utf8_unicode_ci,
  `address` longtext COLLATE utf8_unicode_ci,
  `address_lang` longtext COLLATE utf8_unicode_ci,
  `latitude` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `longitude` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `map_highlight` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `contact_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `contact_name_lang` longtext COLLATE utf8_unicode_ci,
  `contact_web` longtext COLLATE utf8_unicode_ci,
  `contact_email` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `contact_phone` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `location_order` int(11) NOT NULL,
  `show_map_highlight` tinyint(1) NOT NULL,
  `show_contact_name` tinyint(1) NOT NULL,
  `show_contact_web` tinyint(1) NOT NULL,
  `show_contact_email` tinyint(1) NOT NULL,
  `show_contact_phone` tinyint(1) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `locations_group_id_1652dafa49a8085c_fk_groups_id` (`group_id`),
  CONSTRAINT `locations_group_id_1652dafa49a8085c_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locations`
--

LOCK TABLES `locations` WRITE;
/*!40000 ALTER TABLE `locations` DISABLE KEYS */;
INSERT INTO `locations` VALUES (1,'Le meridien','{\"6\": \"Le meridien\"}','<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>','{\"6\": \"<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>\"}','','{\"6\": \"\"}','23.836337016546125','90.41770577430725','','Name','{\"6\": \"Name\"}','https://www.marriott.com','name@domain.com','0135451515',1,0,1,1,1,1,10);
/*!40000 ALTER TABLE `locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `match_line`
--

DROP TABLE IF EXISTS `match_line`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `match_line` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `match_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `match_line_booking_id_6bd55623f05dfb80_fk_bookings_id` (`booking_id`),
  KEY `match_line_match_id_3c64e6cb2877fdb3_fk_matches_id` (`match_id`),
  CONSTRAINT `match_line_booking_id_6bd55623f05dfb80_fk_bookings_id` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`),
  CONSTRAINT `match_line_match_id_3c64e6cb2877fdb3_fk_matches_id` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `match_line`
--

LOCK TABLES `match_line` WRITE;
/*!40000 ALTER TABLE `match_line` DISABLE KEYS */;
/*!40000 ALTER TABLE `match_line` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matches`
--

DROP TABLE IF EXISTS `matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `all_dates` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `room_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `matches_8273f993` (`room_id`),
  CONSTRAINT `matches_room_id_596e0d0eb421e204_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matches`
--

LOCK TABLES `matches` WRITE;
/*!40000 ALTER TABLE `matches` DISABLE KEYS */;
/*!40000 ALTER TABLE `matches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `title_lang` longtext COLLATE utf8_unicode_ci,
  `url` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `uid_include` tinyint(1) NOT NULL,
  `accept_login` tinyint(1) NOT NULL,
  `only_speaker` tinyint(1) NOT NULL,
  `level` int(11) NOT NULL,
  `rank` int(11) NOT NULL,
  `start_time` datetime(6) NOT NULL,
  `end_time` datetime(6) NOT NULL,
  `is_visible` tinyint(1) NOT NULL,
  `available_offline` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `allow_unregistered` tinyint(1) NOT NULL,
  `content_id` int(11) DEFAULT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) DEFAULT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `menu_items_e14f02ad` (`content_id`),
  KEY `menu_items_e93cb7eb` (`created_by_id`),
  KEY `menu_items_4437cfac` (`event_id`),
  KEY `menu_items_49fa5cc1` (`last_updated_by_id`),
  KEY `menu_items_6be37982` (`parent_id`),
  CONSTRAINT `menu_items_content_id_27478cf03f6dfcc4_fk_page_contents_id` FOREIGN KEY (`content_id`) REFERENCES `page_contents` (`id`),
  CONSTRAINT `menu_items_created_by_id_e59ca4f2eb90b81_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `menu_items_event_id_1d449481b705757d_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `menu_items_last_updated_by_id_2f521fd5eb87ecab_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `menu_items_parent_id_54445d8cc462488a_fk_menu_items_id` FOREIGN KEY (`parent_id`) REFERENCES `menu_items` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
INSERT INTO `menu_items` VALUES (1,'Start','{\"6\": \"Start\"}','start',0,0,0,1,1,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:23:21.368868','2018-11-30 10:23:21.368888',1,1,1,1,1,NULL),(2,'Start','{\"6\": \"Start\"}','logged-in',0,0,0,1,2,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:23:58.155361','2018-11-30 10:23:58.155376',0,2,1,1,1,NULL),(3,'Registration','{\"6\": \"Registration\"}','inline-registration',0,0,0,1,4,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:24:38.279835','2018-11-30 10:24:38.279852',1,34,1,1,1,NULL),(4,'Login','{\"6\": \"Login\"}','default-login-page',0,0,0,1,3,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:25:42.998811','2018-11-30 10:25:42.998830',1,3,1,1,1,NULL),(5,'Logout','{\"6\": \"Logout\"}','logout',0,0,0,1,6,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:25:57.724275','2018-11-30 10:25:57.724295',0,8,1,1,1,NULL),(6,'Plugins','{\"6\": \"Plugins\"}','https://www.workspaceit.com',0,0,0,1,5,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:26:56.164438','2018-11-30 10:26:56.164453',0,NULL,1,1,1,NULL),(7,'Attendees','{\"6\": \"Attendees\"}','attendees',0,0,0,2,1,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:27:11.992147','2018-11-30 10:27:11.992174',0,32,1,1,1,6),(8,'Hotel','{\"6\": \"Hotel\"}','hotel',0,0,0,2,2,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:27:27.266097','2018-11-30 10:27:27.266115',0,30,1,1,1,6),(9,'Agenda','{\"6\": \"Agenda\"}','session-agenda',0,0,0,2,3,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:27:48.187349','2018-11-30 10:27:48.187369',0,29,1,1,1,6),(10,'photos','{\"6\": \"photos\"}','photos',0,0,0,2,4,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:28:04.848873','2018-11-30 10:28:04.848893',0,28,1,1,1,6),(11,'Locations','{\"6\": \"Locations\"}','location-list',0,0,0,2,5,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:28:24.336368','2018-11-30 10:28:24.336385',0,33,1,1,1,6),(12,'Evaluations','{\"6\": \"Evaluations\"}','evaluation',0,0,0,2,6,'2018-11-30 00:00:00.000000','2019-01-02 23:59:00.000000',1,0,'2018-11-30 10:28:40.012184','2018-11-30 10:28:40.012204',0,31,1,1,1,6);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu_permission`
--

DROP TABLE IF EXISTS `menu_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `menu_id` int(11) NOT NULL,
  `rule_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `menu_permission_menu_id_6de23db3cec3b21e_fk_menu_items_id` (`menu_id`),
  KEY `menu_permission_e1150e65` (`rule_id`),
  CONSTRAINT `menu_permission_menu_id_6de23db3cec3b21e_fk_menu_items_id` FOREIGN KEY (`menu_id`) REFERENCES `menu_items` (`id`),
  CONSTRAINT `menu_permission_rule_id_4389635811fbbdef_fk_rule_set_id` FOREIGN KEY (`rule_id`) REFERENCES `rule_set` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_permission`
--

LOCK TABLES `menu_permission` WRITE;
/*!40000 ALTER TABLE `menu_permission` DISABLE KEYS */;
INSERT INTO `menu_permission` VALUES (2,2,NULL),(5,5,NULL),(7,6,NULL),(8,7,NULL),(9,8,NULL),(10,9,NULL),(11,10,NULL),(12,11,NULL),(13,12,NULL),(14,1,3),(15,4,3),(16,3,3);
/*!40000 ALTER TABLE `menu_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_contents`
--

DROP TABLE IF EXISTS `message_contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_contents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `content` longtext COLLATE utf8_unicode_ci NOT NULL,
  `sender_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `type` enum('push_or_sms','sms_and_push','sms','push','plugin_message') COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `message_contents_e93cb7eb` (`created_by_id`),
  KEY `message_contents_4437cfac` (`event_id`),
  KEY `message_contents_49fa5cc1` (`last_updated_by_id`),
  CONSTRAINT `message_contents_created_by_id_24f724a664fb09bb_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `message_contents_event_id_61a18f867769e647_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `message_contents_last_updated_by_id_53675914bad529e7_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_contents`
--

LOCK TABLES `message_contents` WRITE;
/*!40000 ALTER TABLE `message_contents` DISABLE KEYS */;
/*!40000 ALTER TABLE `message_contents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_history`
--

DROP TABLE IF EXISTS `message_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8_unicode_ci NOT NULL,
  `type` enum('sms','push','mail') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `admin_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `message_history_156f41ed` (`admin_id`),
  CONSTRAINT `message_history_admin_id_5582244f51ccf50b_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_history`
--

LOCK TABLES `message_history` WRITE;
/*!40000 ALTER TABLE `message_history` DISABLE KEYS */;
INSERT INTO `message_history` VALUES (1,'Registration','N/A','mail','2018-11-30 10:31:53.025208',1);
/*!40000 ALTER TABLE `message_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_language_contents`
--

DROP TABLE IF EXISTS `message_language_contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_language_contents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext COLLATE utf8_unicode_ci NOT NULL,
  `language_id` int(11) NOT NULL,
  `message_content_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `message_language_contents_468679bd` (`language_id`),
  KEY `message_language_contents_1384ed9e` (`message_content_id`),
  CONSTRAINT `messag_message_content_id_7ccb41a7b299d7f_fk_message_contents_id` FOREIGN KEY (`message_content_id`) REFERENCES `message_contents` (`id`),
  CONSTRAINT `message_language_conte_language_id_3853e156836a273_fk_presets_id` FOREIGN KEY (`language_id`) REFERENCES `presets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_language_contents`
--

LOCK TABLES `message_language_contents` WRITE;
/*!40000 ALTER TABLE `message_language_contents` DISABLE KEYS */;
/*!40000 ALTER TABLE `message_language_contents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_receivers`
--

DROP TABLE IF EXISTS `message_receivers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_receivers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lastname` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `mobile_phone` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `status` enum('sent','not_sent') COLLATE utf8_unicode_ci NOT NULL,
  `last_received` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `push` tinyint(1) NOT NULL,
  `added_by_id` int(11) NOT NULL,
  `attendee_id` int(11) DEFAULT NULL,
  `message_content_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `message_receivers_0c5d7d4e` (`added_by_id`),
  KEY `message_receivers_c50970ee` (`attendee_id`),
  KEY `message_receivers_1384ed9e` (`message_content_id`),
  CONSTRAINT `messa_message_content_id_7e8c8f8aacc27df5_fk_message_contents_id` FOREIGN KEY (`message_content_id`) REFERENCES `message_contents` (`id`),
  CONSTRAINT `message_receivers_added_by_id_455361e767882d4c_fk_users_id` FOREIGN KEY (`added_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `message_receivers_attendee_id_4a456eb5ad046f22_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_receivers`
--

LOCK TABLES `message_receivers` WRITE;
/*!40000 ALTER TABLE `message_receivers` DISABLE KEYS */;
/*!40000 ALTER TABLE `message_receivers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_receivers_history`
--

DROP TABLE IF EXISTS `message_receivers_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message_receivers_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('sms','push') COLLATE utf8_unicode_ci NOT NULL,
  `sending_at` datetime(6) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `message_rec_receiver_id_2395535d1a545395_fk_message_receivers_id` (`receiver_id`),
  CONSTRAINT `message_rec_receiver_id_2395535d1a545395_fk_message_receivers_id` FOREIGN KEY (`receiver_id`) REFERENCES `message_receivers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_receivers_history`
--

LOCK TABLES `message_receivers_history` WRITE;
/*!40000 ALTER TABLE `message_receivers_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `message_receivers_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` enum('session','admin','attendee','group','session_attend','filter_message') COLLATE utf8_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8_unicode_ci NOT NULL,
  `status` tinyint(1) NOT NULL,
  `status_socket_message` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `clash_session_id` int(11) DEFAULT NULL,
  `message_content_id` int(11) DEFAULT NULL,
  `new_session_id` int(11) DEFAULT NULL,
  `sender_attendee_id` int(11) DEFAULT NULL,
  `to_attendee_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_94e7c6ee` (`clash_session_id`),
  KEY `notifications_1384ed9e` (`message_content_id`),
  KEY `notifications_a73d4f01` (`new_session_id`),
  KEY `notifications_3f9aaff2` (`sender_attendee_id`),
  KEY `notifications_c2cf5734` (`to_attendee_id`),
  CONSTRAINT `notifi_message_content_id_406142ca0e95039_fk_message_contents_id` FOREIGN KEY (`message_content_id`) REFERENCES `message_contents` (`id`),
  CONSTRAINT `notification_sender_attendee_id_413644279e20e68b_fk_attendees_id` FOREIGN KEY (`sender_attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `notifications_clash_session_id_90ccacdd022dad3_fk_sessions_id` FOREIGN KEY (`clash_session_id`) REFERENCES `sessions` (`id`),
  CONSTRAINT `notifications_new_session_id_7e87dce6e96195ec_fk_sessions_id` FOREIGN KEY (`new_session_id`) REFERENCES `sessions` (`id`),
  CONSTRAINT `notifications_to_attendee_id_263daa7330728ff9_fk_attendees_id` FOREIGN KEY (`to_attendee_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `options`
--

DROP TABLE IF EXISTS `options`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `options` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `option` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `option_lang` longtext COLLATE utf8_unicode_ci,
  `option_order` int(11) NOT NULL,
  `default_value` tinyint(1) NOT NULL,
  `question_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `options_7aa0f6ee` (`question_id`),
  CONSTRAINT `options_question_id_37b828b366ff5385_fk_questions_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `options`
--

LOCK TABLES `options` WRITE;
/*!40000 ALTER TABLE `options` DISABLE KEYS */;
/*!40000 ALTER TABLE `options` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `item_type` enum('session','hotel','travel','rebate','adjustment') COLLATE utf8_unicode_ci NOT NULL,
  `item_id` int(11) NOT NULL,
  `cost` double NOT NULL,
  `rebate_amount` double NOT NULL,
  `rebate_for_item_id` int(11) DEFAULT NULL,
  `vat_rate` double DEFAULT NULL,
  `rebate_for_item_type` enum('session','hotel','travel','rebate','adjustment') COLLATE utf8_unicode_ci DEFAULT NULL,
  `applied_on_open_order` tinyint(1) NOT NULL,
  `rebate_is_deleted` tinyint(1) NOT NULL,
  `item_booking_id` int(11) DEFAULT NULL,
  `effected_day_count` int(11) DEFAULT NULL,
  `booking_check_in` date DEFAULT NULL,
  `booking_check_out` date DEFAULT NULL,
  `order_id` int(11) NOT NULL,
  `rebate_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `order_items_69dfcb07` (`order_id`),
  KEY `order_items_10d0c6eb` (`rebate_id`),
  CONSTRAINT `order_items_order_id_254d4de87484faa7_fk_orders_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  CONSTRAINT `order_items_rebate_id_75c786d4e49e51de_fk_rebates_id` FOREIGN KEY (`rebate_id`) REFERENCES `rebates` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,'session',1,1000,0,1,25,NULL,1,0,NULL,1,NULL,NULL,1,NULL),(4,'hotel',1,15000,0,1,25,NULL,1,0,1,3,NULL,NULL,1,NULL);
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `cost` double NOT NULL,
  `rebate_amount` double NOT NULL,
  `vat_amount` double NOT NULL,
  `due_date` datetime(6) DEFAULT NULL,
  `status` enum('open','pending','paid','cancelled') COLLATE utf8_unicode_ci NOT NULL,
  `invoice_ref` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `invoice_date` datetime(6) DEFAULT NULL,
  `is_preselected` tinyint(1) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `orders_attendee_id_b795052318849b_fk_attendees_id` (`attendee_id`),
  KEY `orders_e93cb7eb` (`created_by_id`),
  CONSTRAINT `orders_attendee_id_b795052318849b_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `orders_created_by_id_27e10372dc592c56_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'1001',16000,0,4000,NULL,'open',NULL,'2018-11-30 10:30:23.744586','2018-11-30 10:39:48.682454',NULL,0,1,NULL);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_content_classes`
--

DROP TABLE IF EXISTS `page_content_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_content_classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `box_id` int(11) NOT NULL,
  `classname_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `page_content__classname_id_13d2410af6a74cc2_fk_custom_classes_id` (`classname_id`),
  KEY `page_content_classe_page_id_3719b1c0ba1a6d9c_fk_page_contents_id` (`page_id`),
  CONSTRAINT `page_content__classname_id_13d2410af6a74cc2_fk_custom_classes_id` FOREIGN KEY (`classname_id`) REFERENCES `custom_classes` (`id`),
  CONSTRAINT `page_content_classe_page_id_3719b1c0ba1a6d9c_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_content_classes`
--

LOCK TABLES `page_content_classes` WRITE;
/*!40000 ALTER TABLE `page_content_classes` DISABLE KEYS */;
/*!40000 ALTER TABLE `page_content_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_contents`
--

DROP TABLE IF EXISTS `page_contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_contents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `content` longtext COLLATE utf8_unicode_ci NOT NULL,
  `login_required` tinyint(1) NOT NULL,
  `filter` longtext COLLATE utf8_unicode_ci,
  `element_filter` longtext COLLATE utf8_unicode_ci,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `disallow_logged_in` tinyint(1) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  `template_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `page_contents_e93cb7eb` (`created_by_id`),
  KEY `page_contents_4437cfac` (`event_id`),
  KEY `page_contents_49fa5cc1` (`last_updated_by_id`),
  KEY `page_contents_74f53564` (`template_id`),
  CONSTRAINT `page_contents_created_by_id_66e702b97c1b57bd_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `page_contents_event_id_2e33604e149a2c41_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `page_contents_last_updated_by_id_7610d2c9ba05c161_fk_users_id` FOREIGN KEY (`last_updated_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `page_contents_template_id_3bb2a958d929fe00_fk_email_templates_id` FOREIGN KEY (`template_id`) REFERENCES `email_templates` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_contents`
--

LOCK TABLES `page_contents` WRITE;
/*!40000 ALTER TABLE `page_contents` DISABLE KEYS */;
INSERT INTO `page_contents` VALUES (1,'start','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{end_div}{end_div}{end_div}',0,'[]','[]','2017-03-14 10:23:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(2,'logged-in',' {section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:economy,box:5}{end_div}{end_div}{end_div} ',1,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"41\"}]','2017-03-14 10:23:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(3,'default-login-page','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:login-form,box:5}{end_div}{end_div}{end_div}',0,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"23\"}]','2017-03-14 10:23:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(4,'request-login-page','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:request-login,box:5}{end_div}{end_div}{end_div}',0,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"25\"}]','2017-03-14 10:23:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(5,'reset-password-page','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:reset-password,box:5}{end_div}{end_div}{end_div}',0,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"31\"}]','2017-03-14 10:23:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(6,'new-password-page','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:new-password,box:5}{end_div}{end_div}{end_div}',0,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"32\"}]','2017-03-14 10:23:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(7,'messages',' {section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:archive-messages,box:5}{end_div}{end_div}{end_div} ',1,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"35\"}]','2017-03-24 11:49:37.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(8,'logout','',1,NULL,NULL,'2017-05-25 04:40:30.000000','2017-11-27 07:31:13.000000',1,0,1,1,1,2),(9,'payment-success','',1,NULL,NULL,'2018-01-30 11:16:40.000000','2018-01-30 11:16:40.000000',1,0,1,1,1,2),(10,'payment-cancel','',1,NULL,NULL,'2018-01-30 11:16:54.000000','2018-01-30 11:16:54.000000',1,0,1,1,1,2),(11,'404-not-found','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{end_div}{end_div}{end_div}',0,'[]','[]','2018-03-14 11:16:09.000000','2018-03-14 11:16:09.000000',1,0,1,1,1,2),(12,'403-forbidden-registered','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{end_div}{end_div}{end_div}',0,'[]','[]','2018-03-14 11:16:22.000000','2018-03-14 11:16:22.000000',1,0,1,1,1,2),(13,'403-forbidden-unregistered','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{end_div}{end_div}{end_div}',0,'[]','[]','2018-03-14 11:16:33.000000','2018-03-14 11:16:33.000000',1,0,1,1,1,2),(27,'registration',' {section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{questionid:1,box:5}{questionid:2,box:6}{questionid:3,box:7}{questionid:4,box:8}{questionid:5,box:9}{questionid:6,box:10}{element:session-radio-button,box:12}{element:session-checkbox,box:13}{element:submit-button,box:11,button_id:1}{end_div}{end_div}{end_div} ',0,'[{\"box_id\":\"box-12\",\"filter_id\":1,\"action\":\"1\"},{\"box_id\":\"box-13\",\"filter_id\":1,\"action\":\"0\"}]','[{\"box_id\":\"box-12\",\"element_id\":\"19\"},{\"box_id\":\"box-13\",\"element_id\":\"20\"},{\"box_id\":\"box-11\",\"element_id\":\"24\",\"button_id\":\"1\"}]','2018-11-30 09:34:09.636184','2018-11-30 09:34:09.636201',1,0,1,1,1,2),(28,'photos',' {section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:photo-upload,box:6,button_id:1}{editor:html,box:5}{element:photo-gallery,box:7}{end_div}{end_div}{end_div} ',1,'[]','[{\"box_id\":\"box-6\",\"element_id\":\"36\",\"button_id\":\"1\"},{\"box_id\":\"box-7\",\"element_id\":\"37\"}]','2018-11-30 09:47:05.682918','2018-11-30 09:47:05.682951',1,0,1,1,1,2),(29,'session-agenda','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:session-agenda,box:5}{end_div}{end_div}{end_div}',1,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"42\"}]','2018-11-30 09:47:25.432918','2018-11-30 09:47:25.432942',1,0,1,1,1,2),(30,'hotel','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:hotel-reservation,box:6}{element:submit-button,box:7,button_id:2}{end_div}{end_div}{end_div}',1,'[]','[{\"box_id\":\"box-6\",\"element_id\":\"22\"},{\"box_id\":\"box-7\",\"element_id\":\"24\",\"button_id\":\"2\"}]','2018-11-30 09:58:57.859643','2018-11-30 09:58:57.859663',1,0,1,1,1,2),(31,'evaluation','<div class=\"section-box box \" id=\"box-1\">{row:,box:2}{col:span-4,box:3}{end_div}{col:span-4,box:4}{end_div}{col:span-4,box:5}{end_div}{end_div}</div>{section:temporary,box:7}{row:,box:11}{col:span-4,box:12}{element:evaluations,box:15}{end_div}{col:span-4,box:13}{element:messages,box:16}{end_div}{col:span-4,box:14}{element:next-up,box:17}{end_div}{end_div}{end_div}',1,'[]','[{\"box_id\":\"box-15\",\"element_id\":\"15\"},{\"box_id\":\"box-16\",\"element_id\":\"16\"},{\"box_id\":\"box-17\",\"element_id\":\"17\"}]','2018-11-30 10:01:32.502957','2018-11-30 10:01:32.502980',1,0,1,1,1,2),(32,'attendees',' {section:temporary,box:2}{row:,box:3}{col:span-12,box:4}{element:attendee-list,box:1}{end_div}{end_div}{end_div} ',1,'[]','[{\"box_id\":\"box-1\",\"element_id\":\"33\"}]','2018-11-30 10:06:38.443383','2018-11-30 10:06:38.443403',1,0,1,1,1,2),(33,'location-list',' {section:temporary,box:2}{row:,box:3}{col:span-12,box:4}{editor:html,box:5}{element:location-list,box:1}{element:pdf-button,box:6,button_id:1}{end_div}{end_div}{end_div} ',1,'[]','[{\"box_id\":\"box-1\",\"element_id\":\"18\"},{\"box_id\":\"box-6\",\"element_id\":\"43\",\"button_id\":\"1\"}]','2018-11-30 10:12:03.879838','2018-11-30 10:12:03.879857',1,0,1,1,1,2),(34,'inline-registration','{section:temporary,box:1}{row:,box:2}{col:span-12,box:3}{editor:html,box:4}{element:multiple-registration,box:5}{element:submit-button,box:6,button_id:3}{end_div}{end_div}{end_div}',0,'[]','[{\"box_id\":\"box-5\",\"element_id\":\"39\"},{\"box_id\":\"box-6\",\"element_id\":\"24\",\"button_id\":\"3\"}]','2018-11-30 10:14:54.649301','2018-11-30 10:14:54.649326',1,0,1,1,1,2);
/*!40000 ALTER TABLE `page_contents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_images`
--

DROP TABLE IF EXISTS `page_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `path` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `is_shown` tinyint(1) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `page_images_e93cb7eb` (`created_by_id`),
  KEY `page_images_4437cfac` (`event_id`),
  KEY `page_images_1a63c800` (`page_id`),
  CONSTRAINT `page_images_created_by_id_73b85ac17b023b48_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `page_images_event_id_3dbd5c4a27e7d75a_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `page_images_page_id_1e3e290f020aefcd_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_images`
--

LOCK TABLES `page_images` WRITE;
/*!40000 ALTER TABLE `page_images` DISABLE KEYS */;
/*!40000 ALTER TABLE `page_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `page_permission`
--

DROP TABLE IF EXISTS `page_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `page_id` int(11) NOT NULL,
  `rule_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `page_permission_page_id_69a2e35b6b615fff_fk_page_contents_id` (`page_id`),
  KEY `page_permission_e1150e65` (`rule_id`),
  CONSTRAINT `page_permission_page_id_69a2e35b6b615fff_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`),
  CONSTRAINT `page_permission_rule_id_2f03bdca6b841913_fk_rule_set_id` FOREIGN KEY (`rule_id`) REFERENCES `rule_set` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `page_permission`
--

LOCK TABLES `page_permission` WRITE;
/*!40000 ALTER TABLE `page_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `page_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `password_reset_requests`
--

DROP TABLE IF EXISTS `password_reset_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `password_reset_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hash_code` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `expired_at` datetime(6) NOT NULL,
  `already_used` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `password_reset_requests_e8701ad4` (`user_id`),
  CONSTRAINT `password_reset_requests_user_id_4170ff0886c75ebb_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `password_reset_requests`
--

LOCK TABLES `password_reset_requests` WRITE;
/*!40000 ALTER TABLE `password_reset_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_reset_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment_settings`
--

DROP TABLE IF EXISTS `payment_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payment_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `currency` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `merchant_id` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `payment_types` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `key1` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `key2` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `payment_settings_e93cb7eb` (`created_by_id`),
  KEY `payment_settings_4437cfac` (`event_id`),
  CONSTRAINT `payment_settings_created_by_id_1afb49a30e6ad3f5_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `payment_settings_event_id_44938bd9e1722097_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment_settings`
--

LOCK TABLES `payment_settings` WRITE;
/*!40000 ALTER TABLE `payment_settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_number` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `method` enum('dibs','admin') COLLATE utf8_unicode_ci NOT NULL,
  `amount` double NOT NULL,
  `details` longtext COLLATE utf8_unicode_ci NOT NULL,
  `currency` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `transaction` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `invoice_ref` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `payments_e93cb7eb` (`created_by_id`),
  CONSTRAINT `payments_created_by_id_5ff5a78275bdf14a_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photo_group`
--

DROP TABLE IF EXISTS `photo_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photo_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `photo_group_e93cb7eb` (`created_by_id`),
  KEY `photo_group_1a63c800` (`page_id`),
  CONSTRAINT `photo_group_created_by_id_62ed1c4b7bea51e1_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `photo_group_page_id_79a2f9c2a03e15de_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photo_group`
--

LOCK TABLES `photo_group` WRITE;
/*!40000 ALTER TABLE `photo_group` DISABLE KEYS */;
INSERT INTO `photo_group` VALUES (1,'photos-photo-group','2018-11-30 09:50:43.588518',1,28);
/*!40000 ALTER TABLE `photo_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos`
--

DROP TABLE IF EXISTS `photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `photo` varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
  `is_approved` int(11) NOT NULL,
  `thumb_image` varchar(1000) COLLATE utf8_unicode_ci DEFAULT NULL,
  `comment` longtext COLLATE utf8_unicode_ci,
  `uploaded_at` datetime(6) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `photos_attendee_id_5b9fe90ca3698acb_fk_attendees_id` (`attendee_id`),
  KEY `photos_0e939a4f` (`group_id`),
  CONSTRAINT `photos_attendee_id_5b9fe90ca3698acb_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `photos_group_id_7b2d40384f4f6eee_fk_photo_group_id` FOREIGN KEY (`group_id`) REFERENCES `photo_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos`
--

LOCK TABLES `photos` WRITE;
/*!40000 ALTER TABLE `photos` DISABLE KEYS */;
INSERT INTO `photos` VALUES (1,'public/default-project/photo-reel/15435744641.JPEG',1,'public/default-project/photo-reel/15435744661_thumb.JPEG','','2018-11-30 10:41:08.440570',1,1),(2,'public/default-project/photo-reel/15435745171.JPEG',1,'public/default-project/photo-reel/15435745191_thumb.JPEG','','2018-11-30 10:42:01.023379',1,1);
/*!40000 ALTER TABLE `photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plugin_pdf_button`
--

DROP TABLE IF EXISTS `plugin_pdf_button`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_pdf_button` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `plugin_pdf_button_e93cb7eb` (`created_by_id`),
  KEY `plugin_pdf_button_1a63c800` (`page_id`),
  CONSTRAINT `plugin_pdf_button_created_by_id_70f942b4f0da74e4_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `plugin_pdf_button_page_id_52b31993cef92999_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plugin_pdf_button`
--

LOCK TABLES `plugin_pdf_button` WRITE;
/*!40000 ALTER TABLE `plugin_pdf_button` DISABLE KEYS */;
INSERT INTO `plugin_pdf_button` VALUES (1,'locations-pdf-button','2018-11-30 10:12:45.698787',1,33);
/*!40000 ALTER TABLE `plugin_pdf_button` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plugin_submit_button`
--

DROP TABLE IF EXISTS `plugin_submit_button`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `plugin_submit_button` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `page_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `plugin_submit_button_e93cb7eb` (`created_by_id`),
  KEY `plugin_submit_button_1a63c800` (`page_id`),
  CONSTRAINT `plugin_submit_butto_page_id_18badf75877c364a_fk_page_contents_id` FOREIGN KEY (`page_id`) REFERENCES `page_contents` (`id`),
  CONSTRAINT `plugin_submit_button_created_by_id_2d497d9868a25439_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plugin_submit_button`
--

LOCK TABLES `plugin_submit_button` WRITE;
/*!40000 ALTER TABLE `plugin_submit_button` DISABLE KEYS */;
INSERT INTO `plugin_submit_button` VALUES (1,'registration-button','2018-11-30 09:38:46.269355',1,27),(2,'hotel-button','2018-11-30 10:00:59.111270',1,30),(3,'inline-registration-button','2018-11-30 10:15:51.799023',1,34);
/*!40000 ALTER TABLE `plugin_submit_button` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `preset_event`
--

DROP TABLE IF EXISTS `preset_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `preset_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `event_id` int(11) NOT NULL,
  `preset_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `preset_event_event_id_f76acd084fb5bb0_fk_events_id` (`event_id`),
  KEY `preset_event_cf933d7f` (`preset_id`),
  CONSTRAINT `preset_event_event_id_f76acd084fb5bb0_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`),
  CONSTRAINT `preset_event_preset_id_51b04c4198944ca2_fk_presets_id` FOREIGN KEY (`preset_id`) REFERENCES `presets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preset_event`
--

LOCK TABLES `preset_event` WRITE;
/*!40000 ALTER TABLE `preset_event` DISABLE KEYS */;
INSERT INTO `preset_event` VALUES (1,1,6);
/*!40000 ALTER TABLE `preset_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `presets`
--

DROP TABLE IF EXISTS `presets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `presets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `preset_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `language_code` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `date_format` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `time_format` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `datetime_format` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `datetime_language` longtext COLLATE utf8_unicode_ci,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `presets_e93cb7eb` (`created_by_id`),
  KEY `presets_4437cfac` (`event_id`),
  CONSTRAINT `presets_created_by_id_f2a2fa0c307587_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `presets_event_id_76c066e0bf4c06fd_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `presets`
--

LOCK TABLES `presets` WRITE;
/*!40000 ALTER TABLE `presets` DISABLE KEYS */;
INSERT INTO `presets` VALUES (6,'English','2017-03-14 10:39:15.000000','en','Y-m-d','H:i','Y-m-d H:i',NULL,1,1),(7,'Bengali','2017-03-14 10:39:15.000000','en','Y-m-d','H:i','Y-m-d H:i',NULL,1,1);
/*!40000 ALTER TABLE `presets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `question_pre_requisite`
--

DROP TABLE IF EXISTS `question_pre_requisite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `question_pre_requisite` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` tinyint(1) NOT NULL,
  `pre_req_answer_id` int(11) NOT NULL,
  `pre_req_question_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `question_pre_re_pre_req_answer_id_7f4344b77c3d7018_fk_options_id` (`pre_req_answer_id`),
  KEY `question_pre_requisite_3553ff6d` (`pre_req_question_id`),
  KEY `question_pre_requisite_7aa0f6ee` (`question_id`),
  CONSTRAINT `question_pr_pre_req_question_id_1d782020253b6c8c_fk_questions_id` FOREIGN KEY (`pre_req_question_id`) REFERENCES `questions` (`id`),
  CONSTRAINT `question_pre_re_pre_req_answer_id_7f4344b77c3d7018_fk_options_id` FOREIGN KEY (`pre_req_answer_id`) REFERENCES `options` (`id`),
  CONSTRAINT `question_pre_requis_question_id_1217f83a95b05c00_fk_questions_id` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `question_pre_requisite`
--

LOCK TABLES `question_pre_requisite` WRITE;
/*!40000 ALTER TABLE `question_pre_requisite` DISABLE KEYS */;
/*!40000 ALTER TABLE `question_pre_requisite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `title_lang` longtext COLLATE utf8_unicode_ci,
  `type` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8_unicode_ci,
  `description_lang` longtext COLLATE utf8_unicode_ci,
  `min_character` int(11) DEFAULT NULL,
  `max_character` int(11) DEFAULT NULL,
  `regular_expression` longtext COLLATE utf8_unicode_ci,
  `default_answer` longtext COLLATE utf8_unicode_ci,
  `default_answer_status` enum('set','leave','empty') COLLATE utf8_unicode_ci NOT NULL,
  `question_class` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `required` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `question_order` int(11) NOT NULL,
  `actual_definition` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `show_description` tinyint(1) NOT NULL,
  `from_date` date DEFAULT NULL,
  `to_date` date DEFAULT NULL,
  `from_time` time(6) DEFAULT NULL,
  `to_time` time(6) DEFAULT NULL,
  `time_interval` varchar(2) COLLATE utf8_unicode_ci DEFAULT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `questions_group_id_8ed0e603c3c0b4f_fk_groups_id` (`group_id`),
  CONSTRAINT `questions_group_id_8ed0e603c3c0b4f_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (1,'First Name',NULL,'text','',NULL,NULL,NULL,NULL,NULL,'leave',NULL,1,'2017-03-14 10:23:37.000000',1,'firstname',0,NULL,NULL,NULL,NULL,NULL,1),(2,'Last Name',NULL,'text','',NULL,NULL,NULL,NULL,NULL,'leave',NULL,1,'2017-03-14 10:23:37.000000',2,'lastname',0,NULL,NULL,NULL,NULL,NULL,1),(3,'Email',NULL,'text','',NULL,NULL,NULL,NULL,NULL,'leave',NULL,1,'2017-03-14 10:23:37.000000',3,'email',0,NULL,NULL,NULL,NULL,NULL,1),(4,'Mobile phone',NULL,'text','',NULL,NULL,NULL,NULL,NULL,'leave',NULL,1,'2017-03-14 10:23:37.000000',4,'phone',0,NULL,NULL,NULL,NULL,NULL,1),(5,'Bio','{\"6\": \"Bio\"}','textarea','About yourself','{\"6\": \"About yourself\"}',NULL,NULL,NULL,NULL,'leave',NULL,0,'2018-11-30 09:33:26.986466',1,NULL,1,NULL,NULL,NULL,NULL,'5',14),(6,'Country','{\"6\": \"Country\"}','country','','{\"6\": \"\"}',NULL,NULL,NULL,'BD','leave',NULL,1,'2018-11-30 09:33:51.130808',2,NULL,0,NULL,NULL,NULL,NULL,NULL,14);
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rebates`
--

DROP TABLE IF EXISTS `rebates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rebates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `type_id` longtext COLLATE utf8_unicode_ci,
  `rebate_type` enum('percentage','fixed') COLLATE utf8_unicode_ci NOT NULL,
  `value` double NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` int(11) NOT NULL,
  `event_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rebates_e93cb7eb` (`created_by_id`),
  KEY `rebates_4437cfac` (`event_id`),
  CONSTRAINT `rebates_created_by_id_37689e1c9500f924_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `rebates_event_id_51ebf2e2f76330ae_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rebates`
--

LOCK TABLES `rebates` WRITE;
/*!40000 ALTER TABLE `rebates` DISABLE KEYS */;
/*!40000 ALTER TABLE `rebates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_group_owner`
--

DROP TABLE IF EXISTS `registration_group_owner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registration_group_owner` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `registration_group_owner_0e939a4f` (`group_id`),
  KEY `registration_group_owner_5e7b1936` (`owner_id`),
  CONSTRAINT `registration__group_id_7c7957e62c98d55_fk_registration_groups_id` FOREIGN KEY (`group_id`) REFERENCES `registration_groups` (`id`),
  CONSTRAINT `registration_group_own_owner_id_5ac82ae684968e59_fk_attendees_id` FOREIGN KEY (`owner_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_group_owner`
--

LOCK TABLES `registration_group_owner` WRITE;
/*!40000 ALTER TABLE `registration_group_owner` DISABLE KEYS */;
INSERT INTO `registration_group_owner` VALUES (1,1,1);
/*!40000 ALTER TABLE `registration_group_owner` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_groups`
--

DROP TABLE IF EXISTS `registration_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registration_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_show` tinyint(1) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `registration_groups_event_id_fc8b99e2639e243_fk_events_id` (`event_id`),
  CONSTRAINT `registration_groups_event_id_fc8b99e2639e243_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_groups`
--

LOCK TABLES `registration_groups` WRITE;
/*!40000 ALTER TABLE `registration_groups` DISABLE KEYS */;
INSERT INTO `registration_groups` VALUES (1,'Registration-group-1','2018-11-30 10:31:52.562101',1,1);
/*!40000 ALTER TABLE `registration_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `requested_buddies`
--

DROP TABLE IF EXISTS `requested_buddies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `requested_buddies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exists` tinyint(1) NOT NULL,
  `email` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `buddy_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `requested_buddies_booking_id_28e0b5741fc3fb6a_fk_bookings_id` (`booking_id`),
  KEY `requested_buddies_buddy_id_5b93216b53d3c3ff_fk_attendees_id` (`buddy_id`),
  CONSTRAINT `requested_buddies_booking_id_28e0b5741fc3fb6a_fk_bookings_id` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`),
  CONSTRAINT `requested_buddies_buddy_id_5b93216b53d3c3ff_fk_attendees_id` FOREIGN KEY (`buddy_id`) REFERENCES `attendees` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `requested_buddies`
--

LOCK TABLES `requested_buddies` WRITE;
/*!40000 ALTER TABLE `requested_buddies` DISABLE KEYS */;
/*!40000 ALTER TABLE `requested_buddies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room_allotments`
--

DROP TABLE IF EXISTS `room_allotments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `room_allotments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `allotments` int(11) NOT NULL,
  `available_date` date NOT NULL,
  `cost` double DEFAULT NULL,
  `vat` double DEFAULT NULL,
  `room_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `room_allotments_room_id_4434eb024aae215d_fk_rooms_id` (`room_id`),
  CONSTRAINT `room_allotments_room_id_4434eb024aae215d_fk_rooms_id` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room_allotments`
--

LOCK TABLES `room_allotments` WRITE;
/*!40000 ALTER TABLE `room_allotments` DISABLE KEYS */;
INSERT INTO `room_allotments` VALUES (1,10,'2018-12-08',0,NULL,1),(2,10,'2018-12-09',0,NULL,1),(3,10,'2018-12-10',0,NULL,1),(4,10,'2018-12-11',0,NULL,1);
/*!40000 ALTER TABLE `room_allotments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rooms`
--

DROP TABLE IF EXISTS `rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description_lang` longtext COLLATE utf8_unicode_ci,
  `cost` double DEFAULT NULL,
  `beds` int(11) NOT NULL,
  `vat` double DEFAULT NULL,
  `room_order` int(11) NOT NULL,
  `keep_hotel` tinyint(1) NOT NULL,
  `pay_whole_amount` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `hotel_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rooms_hotel_id_2be7f88f4e810155_fk_hotels_id` (`hotel_id`),
  CONSTRAINT `rooms_hotel_id_2be7f88f4e810155_fk_hotels_id` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rooms`
--

LOCK TABLES `rooms` WRITE;
/*!40000 ALTER TABLE `rooms` DISABLE KEYS */;
INSERT INTO `rooms` VALUES (1,'Double','{\"6\": \"Double\"}',10000,2,25,1,1,0,'2018-11-30 09:46:18.092199','2018-11-30 09:46:18.092226',1);
/*!40000 ALTER TABLE `rooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rule_set`
--

DROP TABLE IF EXISTS `rule_set`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rule_set` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `preset` longtext COLLATE utf8_unicode_ci NOT NULL,
  `created_at` date NOT NULL,
  `modified_at` date NOT NULL,
  `rule_order` int(11) NOT NULL,
  `is_limit` tinyint(1) NOT NULL,
  `limit_amount` int(11) NOT NULL,
  `matchfor` varchar(1) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_by_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `rule_set_e93cb7eb` (`created_by_id`),
  KEY `rule_set_0e939a4f` (`group_id`),
  CONSTRAINT `rule_set_created_by_id_4ae87b9e4b7cacf8_fk_users_id` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`),
  CONSTRAINT `rule_set_group_id_7b58e5f0b1c3ebbc_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rule_set`
--

LOCK TABLES `rule_set` WRITE;
/*!40000 ALTER TABLE `rule_set` DISABLE KEYS */;
INSERT INTO `rule_set` VALUES (1,'filter 1','[[{\"field\":\"7\",\"type\":\"country\",\"condition\":\"6\",\"values\":[\"1\",\"BD\"],\"matchFor\":\"1\"}]]','2018-11-30','2018-11-30',1,0,0,'1',1,8),(2,'All Attendees','[[{\"field\":\"1\",\"condition\":\"3\",\"values\":[\"2018-11-01\"],\"matchFor\":\"1\"}]]','2018-11-30','2018-11-30',2,0,0,'1',1,8),(3,'not logged in','[[{\"field\":\"7\",\"condition\":\"3\",\"type\":\"text\",\"values\":[\"7\",null],\"matchFor\":\"1\"}]]','2018-11-30','2018-11-30',3,0,0,'1',1,8);
/*!40000 ALTER TABLE `rule_set` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scans`
--

DROP TABLE IF EXISTS `scans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scans` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` smallint(6) NOT NULL,
  `scan_time` datetime(6) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `checkpoint_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scans_attendee_id_6220689c166d69cb_fk_attendees_id` (`attendee_id`),
  KEY `scans_checkpoint_id_540bdd56f2bf74c1_fk_checkpoints_id` (`checkpoint_id`),
  CONSTRAINT `scans_attendee_id_6220689c166d69cb_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `scans_checkpoint_id_540bdd56f2bf74c1_fk_checkpoints_id` FOREIGN KEY (`checkpoint_id`) REFERENCES `checkpoints` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scans`
--

LOCK TABLES `scans` WRITE;
/*!40000 ALTER TABLE `scans` DISABLE KEYS */;
/*!40000 ALTER TABLE `scans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seminars`
--

DROP TABLE IF EXISTS `seminars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seminars` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `date` datetime(6) NOT NULL,
  `created` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seminars`
--

LOCK TABLES `seminars` WRITE;
/*!40000 ALTER TABLE `seminars` DISABLE KEYS */;
/*!40000 ALTER TABLE `seminars` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seminars_has_speakers`
--

DROP TABLE IF EXISTS `seminars_has_speakers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seminars_has_speakers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `session_id` int(11) NOT NULL,
  `speaker_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `seminars_has_speakers_7fc8ef54` (`session_id`),
  KEY `seminars_has_speakers_c5267933` (`speaker_id`),
  CONSTRAINT `seminars_has_speaker_speaker_id_709252ebed1271c4_fk_attendees_id` FOREIGN KEY (`speaker_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `seminars_has_speakers_session_id_4556291355edc6c2_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seminars_has_speakers`
--

LOCK TABLES `seminars_has_speakers` WRITE;
/*!40000 ALTER TABLE `seminars_has_speakers` DISABLE KEYS */;
/*!40000 ALTER TABLE `seminars_has_speakers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seminars_has_users`
--

DROP TABLE IF EXISTS `seminars_has_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seminars_has_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` enum('attending','in-queue','not-attending','deciding') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `queue_order` int(11) NOT NULL,
  `status_socket_nextup` tinyint(1) NOT NULL,
  `status_socket_evaluation` tinyint(1) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `seminars_has_users_attendee_id_74129055200c33f2_fk_attendees_id` (`attendee_id`),
  KEY `seminars_has_users_7fc8ef54` (`session_id`),
  CONSTRAINT `seminars_has_users_attendee_id_74129055200c33f2_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `seminars_has_users_session_id_2669264161db3fd5_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seminars_has_users`
--

LOCK TABLES `seminars_has_users` WRITE;
/*!40000 ALTER TABLE `seminars_has_users` DISABLE KEYS */;
INSERT INTO `seminars_has_users` VALUES (1,'attending','2018-11-30 10:30:23.671177','2018-11-30 10:30:23.671200',1,0,0,1,1),(2,'not-attending','2018-11-30 10:30:57.623632','2018-11-30 10:30:57.623655',1,0,0,2,1),(3,'not-attending','2018-11-30 10:31:44.738750','2018-11-30 10:31:44.738775',1,0,0,3,1);
/*!40000 ALTER TABLE `seminars_has_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_has_classes`
--

DROP TABLE IF EXISTS `session_has_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_has_classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classname_id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `session_has_c_classname_id_74bf23e8add84a77_fk_custom_classes_id` (`classname_id`),
  KEY `session_has_classes_session_id_ee6f2ae2eaf2684_fk_sessions_id` (`session_id`),
  CONSTRAINT `session_has_c_classname_id_74bf23e8add84a77_fk_custom_classes_id` FOREIGN KEY (`classname_id`) REFERENCES `custom_classes` (`id`),
  CONSTRAINT `session_has_classes_session_id_ee6f2ae2eaf2684_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_has_classes`
--

LOCK TABLES `session_has_classes` WRITE;
/*!40000 ALTER TABLE `session_has_classes` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_has_classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_has_tags`
--

DROP TABLE IF EXISTS `session_has_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_has_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `session_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `session_has_tags_session_id_2a23d6590e57d3a9_fk_sessions_id` (`session_id`),
  KEY `session_has_tags_tag_id_4eb16afd8e732a43_fk_general_tags_id` (`tag_id`),
  CONSTRAINT `session_has_tags_session_id_2a23d6590e57d3a9_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`),
  CONSTRAINT `session_has_tags_tag_id_4eb16afd8e732a43_fk_general_tags_id` FOREIGN KEY (`tag_id`) REFERENCES `general_tags` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_has_tags`
--

LOCK TABLES `session_has_tags` WRITE;
/*!40000 ALTER TABLE `session_has_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_has_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session_ratings`
--

DROP TABLE IF EXISTS `session_ratings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `session_ratings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rating` int(11) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `session_ratings_attendee_id_150a5d5c84f70234_fk_attendees_id` (`attendee_id`),
  KEY `session_ratings_session_id_5172bc42c21d0d63_fk_sessions_id` (`session_id`),
  CONSTRAINT `session_ratings_attendee_id_150a5d5c84f70234_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `session_ratings_session_id_5172bc42c21d0d63_fk_sessions_id` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session_ratings`
--

LOCK TABLES `session_ratings` WRITE;
/*!40000 ALTER TABLE `session_ratings` DISABLE KEYS */;
/*!40000 ALTER TABLE `session_ratings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name_lang` longtext COLLATE utf8_unicode_ci,
  `description` longtext COLLATE utf8_unicode_ci NOT NULL,
  `description_lang` longtext COLLATE utf8_unicode_ci,
  `start` datetime(6) NOT NULL,
  `end` datetime(6) NOT NULL,
  `reg_between_start` date NOT NULL,
  `reg_between_end` date NOT NULL,
  `max_attendees` int(11) DEFAULT NULL,
  `allow_attendees_queue` tinyint(1) NOT NULL,
  `speakers` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  `has_time` tinyint(1) NOT NULL,
  `receive_answer` tinyint(1) NOT NULL,
  `show_on_evaluation` tinyint(1) NOT NULL,
  `show_on_next_up` tinyint(1) NOT NULL,
  `allow_overlapping` tinyint(1) NOT NULL,
  `all_day` tinyint(1) NOT NULL,
  `session_order` int(11) NOT NULL,
  `default_answer` enum('attending','in-queue','not-attending','deciding') COLLATE utf8_unicode_ci NOT NULL,
  `default_answer_status` enum('set','leave','empty') COLLATE utf8_unicode_ci NOT NULL,
  `cost` double DEFAULT NULL,
  `vat` double DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `group_id` int(11) NOT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sessions_group_id_6ca08d70194be4ed_fk_groups_id` (`group_id`),
  KEY `sessions_location_id_7960de0e3de0dd8_fk_locations_id` (`location_id`),
  CONSTRAINT `sessions_group_id_6ca08d70194be4ed_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`),
  CONSTRAINT `sessions_location_id_7960de0e3de0dd8_fk_locations_id` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
INSERT INTO `sessions` VALUES (1,'Dinner','{\"6\": \"Dinner\"}','<p>Dinner Party</p>','{\"6\": \"<p>Dinner Party</p>\"}','2018-12-09 19:15:00.000000','2018-12-09 22:30:00.000000','2018-11-30','2019-01-01',100,0,'',1,0,1,1,0,0,1,'attending','leave',1000,25,'2018-11-30 09:44:54.596790','2018-11-30 09:44:54.596805',6,1);
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `settings_event_id_66a2d27ebf079e85_fk_events_id` (`event_id`),
  CONSTRAINT `settings_event_id_66a2d27ebf079e85_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES (1,'attendee_add_confirmation','1',1),(2,'attendee_edit_confirmation','1',1),(3,'notification_timeout','8:00',1),(4,'timezone','Asia/Dhaka',1),(5,'cookie_expire','864000',1),(6,'appear_next_up_setting','1:00',1),(7,'disappear_next_up_setting','0:15',1),(8,'appear_evaluation_setting','0:10',1),(9,'disappear_evaluation_setting','1:00',1),(10,'sender_email','mahedi@workspaceit.com',1),(11,'photo_slider_duration','',1),(12,'default_tag','[]',1),(13,'week_start_day','mon',1),(14,'plugin_language','en',1),(15,'session_global_settings','[]',1),(16,'location_global_settings','[]',1),(17,'attendee_global_settings','\"{\\\"question\\\":[{\\\"id\\\":\\\"\\\"}]}\"',1),(18,'uid_length','16',1),(19,'default_date_format','{\"kendo\":\"yyyy-MM-dd\",\"python\":\"Y-m-d\"}',1),(20,'temporary_attendee_expire_time','1800000',1),(21,'default_project','default-project',1),(22,'due_date','30',1),(23,'start_order_number','1000',1),(24,'current_invoice_ref','1000697',1),(25,'economy_order_table_global_settings','[]',1);
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tags_event_id_93a3bdf58af64a5_fk_events_id` (`event_id`),
  CONSTRAINT `tags_event_id_93a3bdf58af64a5_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `travel_bound_relation`
--

DROP TABLE IF EXISTS `travel_bound_relation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `travel_bound_relation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `travel_homebound_id` int(11) NOT NULL,
  `travel_outbound_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `travel_bound__travel_homebound_id_162cb88496689f4e_fk_travels_id` (`travel_homebound_id`),
  KEY `travel_bound_re_travel_outbound_id_d11c7d90b719fdb_fk_travels_id` (`travel_outbound_id`),
  CONSTRAINT `travel_bound__travel_homebound_id_162cb88496689f4e_fk_travels_id` FOREIGN KEY (`travel_homebound_id`) REFERENCES `travels` (`id`),
  CONSTRAINT `travel_bound_re_travel_outbound_id_d11c7d90b719fdb_fk_travels_id` FOREIGN KEY (`travel_outbound_id`) REFERENCES `travels` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `travel_bound_relation`
--

LOCK TABLES `travel_bound_relation` WRITE;
/*!40000 ALTER TABLE `travel_bound_relation` DISABLE KEYS */;
/*!40000 ALTER TABLE `travel_bound_relation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `travel_has_attendees`
--

DROP TABLE IF EXISTS `travel_has_attendees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `travel_has_attendees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` enum('attending','in-queue','not-attending','deciding') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `queue_order` int(11) NOT NULL,
  `attendee_id` int(11) NOT NULL,
  `travel_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `travel_has_attendee_attendee_id_780fa3adbe1d17ff_fk_attendees_id` (`attendee_id`),
  KEY `travel_has_attendees_travel_id_4f30d6397edd37d2_fk_travels_id` (`travel_id`),
  CONSTRAINT `travel_has_attendee_attendee_id_780fa3adbe1d17ff_fk_attendees_id` FOREIGN KEY (`attendee_id`) REFERENCES `attendees` (`id`),
  CONSTRAINT `travel_has_attendees_travel_id_4f30d6397edd37d2_fk_travels_id` FOREIGN KEY (`travel_id`) REFERENCES `travels` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `travel_has_attendees`
--

LOCK TABLES `travel_has_attendees` WRITE;
/*!40000 ALTER TABLE `travel_has_attendees` DISABLE KEYS */;
/*!40000 ALTER TABLE `travel_has_attendees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `travel_has_tags`
--

DROP TABLE IF EXISTS `travel_has_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `travel_has_tags` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tag_id` int(11) NOT NULL,
  `travel_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `travel_has_tags_tag_id_67f3e728601f2f02_fk_general_tags_id` (`tag_id`),
  KEY `travel_has_tags_travel_id_60c6a17efd8f8966_fk_travels_id` (`travel_id`),
  CONSTRAINT `travel_has_tags_tag_id_67f3e728601f2f02_fk_general_tags_id` FOREIGN KEY (`tag_id`) REFERENCES `general_tags` (`id`),
  CONSTRAINT `travel_has_tags_travel_id_60c6a17efd8f8966_fk_travels_id` FOREIGN KEY (`travel_id`) REFERENCES `travels` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `travel_has_tags`
--

LOCK TABLES `travel_has_tags` WRITE;
/*!40000 ALTER TABLE `travel_has_tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `travel_has_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `travels`
--

DROP TABLE IF EXISTS `travels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `travels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name_lang` longtext COLLATE utf8_unicode_ci,
  `description` longtext COLLATE utf8_unicode_ci NOT NULL,
  `description_lang` longtext COLLATE utf8_unicode_ci,
  `departure_city` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `arrival_city` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `departure` datetime(6) NOT NULL,
  `arrival` datetime(6) NOT NULL,
  `reg_between_start` date NOT NULL,
  `reg_between_end` date NOT NULL,
  `travel_bound` enum('homebound','outbound') COLLATE utf8_unicode_ci NOT NULL,
  `max_attendees` int(11) NOT NULL,
  `allow_attendees_queue` tinyint(1) NOT NULL,
  `travel_order` int(11) NOT NULL,
  `default_answer` enum('attending','in-queue','not-attending','deciding') COLLATE utf8_unicode_ci NOT NULL,
  `default_answer_status` enum('set','leave','empty') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `group_id` int(11) NOT NULL,
  `location_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `travels_group_id_1b9acef02665de03_fk_groups_id` (`group_id`),
  KEY `travels_location_id_2f4c11cd8d9c98b8_fk_locations_id` (`location_id`),
  CONSTRAINT `travels_group_id_1b9acef02665de03_fk_groups_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`),
  CONSTRAINT `travels_location_id_2f4c11cd8d9c98b8_fk_locations_id` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `travels`
--

LOCK TABLES `travels` WRITE;
/*!40000 ALTER TABLE `travels` DISABLE KEYS */;
/*!40000 ALTER TABLE `travels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `used_rule`
--

DROP TABLE IF EXISTS `used_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `used_rule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` date NOT NULL,
  `rule_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `used_rule_rule_id_3b4e25be0f6cabab_fk_rule_set_id` (`rule_id`),
  KEY `used_rule_e8701ad4` (`user_id`),
  CONSTRAINT `used_rule_rule_id_3b4e25be0f6cabab_fk_rule_set_id` FOREIGN KEY (`rule_id`) REFERENCES `rule_set` (`id`),
  CONSTRAINT `used_rule_user_id_780aa4e99a79a7d1_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `used_rule`
--

LOCK TABLES `used_rule` WRITE;
/*!40000 ALTER TABLE `used_rule` DISABLE KEYS */;
/*!40000 ALTER TABLE `used_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `firstname` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `lastname` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `company` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(150) COLLATE utf8_unicode_ci NOT NULL,
  `phonenumber` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
  `role` enum('student','participant','speaker','vip') COLLATE utf8_unicode_ci NOT NULL,
  `type` enum('super_admin','admin','third_party_admin') COLLATE utf8_unicode_ci NOT NULL,
  `status` enum('active','inactive') COLLATE utf8_unicode_ci NOT NULL,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin','wsit','admin@wsit.com','pbkdf2_sha256$20000$VpovRyU14W6o$cxLXNiZ5hfIgY/NqYDa0UggTYcs6loYrCSnriLKiw80=','123456789','vip','super_admin','active','2015-09-18 14:42:38.000000','2015-09-18 14:42:38.000000');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `visible_columns`
--

DROP TABLE IF EXISTS `visible_columns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visible_columns` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `visible_columns` longtext COLLATE utf8_unicode_ci,
  `type` enum('session','hotel') COLLATE utf8_unicode_ci NOT NULL,
  `admin_id` int(11) NOT NULL,
  `event_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `visible_columns_admin_id_4919e7286e33ca0b_fk_users_id` (`admin_id`),
  KEY `visible_columns_event_id_4497e4abf1885756_fk_events_id` (`event_id`),
  CONSTRAINT `visible_columns_admin_id_4919e7286e33ca0b_fk_users_id` FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  CONSTRAINT `visible_columns_event_id_4497e4abf1885756_fk_events_id` FOREIGN KEY (`event_id`) REFERENCES `events` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `visible_columns`
--

LOCK TABLES `visible_columns` WRITE;
/*!40000 ALTER TABLE `visible_columns` DISABLE KEYS */;
INSERT INTO `visible_columns` VALUES (1,'[0, 1, 12, 13]','session',1,1);
/*!40000 ALTER TABLE `visible_columns` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-11-30 11:04:40
