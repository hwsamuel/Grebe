CREATE DATABASE grebe;

USE grebe;

CREATE TABLE tweets (
  id VARCHAR(255) NOT NULL,
  tweet VARCHAR(255) NOT NULL,
  tweet_hash VARCHAR(50) UNIQUE DEFAULT NULL,
  longitude FLOAT DEFAULT NULL,
  latitude FLOAT DEFAULT NULL,
  created_at DATETIME DEFAULT NULL,
  collected_at DATETIME DEFAULT NULL,
  collection_type enum('stream','search') DEFAULT NULL,
  lang VARCHAR(10) DEFAULT NULL,
  place_name VARCHAR(255) DEFAULT NULL,
  country_code VARCHAR(5) DEFAULT NULL,
  cronjob_tag VARCHAR(255) DEFAULT NULL,
  user_id VARCHAR(255) DEFAULT NULL,
  user_name VARCHAR(20) DEFAULT NULL,
  user_geoenabled TINYINT(1) DEFAULT NULL,
  user_lang VARCHAR(10) DEFAULT NULL,
  user_location VARCHAR(255) DEFAULT NULL,
  user_timezone VARCHAR(100) DEFAULT NULL,
  user_verified TINYINT(1) DEFAULT NULL
);

CREATE INDEX idx_id ON tweets(id);
CREATE INDEX idx_tweet ON tweets(tweet);
CREATE INDEX idx_tweet_hash ON tweets(tweet_hash);
CREATE INDEX idx_created_at ON tweets(created_at);
CREATE INDEX idx_place_name ON tweets(place_name);
