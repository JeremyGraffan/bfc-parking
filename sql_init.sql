-- Adminer 4.8.1 PostgreSQL 16.1 (Debian 16.1-1.pgdg120+1) dump

\connect "bfc";

DROP TABLE IF EXISTS "authorization";
DROP SEQUENCE IF EXISTS authorization_id_seq;
CREATE SEQUENCE authorization_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."authorization" (
    "id" bigint DEFAULT nextval('authorization_id_seq') NOT NULL,
    "plate" character varying(255) NOT NULL,
    "expiration" date NOT NULL,
    "model" character varying(255),
    CONSTRAINT "authorization_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "verbalization";
DROP SEQUENCE IF EXISTS verbalization_id_seq;
CREATE SEQUENCE verbalization_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;

CREATE TABLE "public"."verbalization" (
    "id" bigint DEFAULT nextval('verbalization_id_seq') NOT NULL,
    "plate" character varying(255) NOT NULL,
    "image" text,
    "date" date NOT NULL,
    "reason" character varying(255),
    CONSTRAINT "verbalization_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


-- 2024-01-22 00:49:52.708685+00
