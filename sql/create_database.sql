--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--CREATE TABLE authors(
--    id integer NOT NULL,
--    name text NOT NULL,
--    raw_name text NOT NULL
--);
--
--ALTER TABLE public.authors OWNER TO cakesbot;
--
--CREATE SEQUENCE authors_id_seq
--    START WITH 1
--    INCREMENT BY 1
--    NO MINVALUE
--    NO MAXVALUE
--    CACHE 1;
--
--ALTER TABLE public.authors_id_seq OWNER TO cakesbot;
--
--ALTER SEQUENCE authors_id_seq OWNED BY authors.id;
--
--ALTER TABLE ONLY authors ALTER COLUMN id SET DEFAULT nextval('authors_id_seq'::regclass);
--
--ALTER TABLE ONLY authors
--    ADD CONSTRAINT authors_pkey PRIMARY KEY (id);
--
-- Name: cakes; Type: TABLE; Schema: public; Owner: cakesbot; Tablespace: 
--

CREATE TABLE users (
    id integer NOT NULL UNIQUE,
    name text NOT NULL,
    joined timestamp without time zone NOT NULL,
    last_visit timestamp without time zone NOT NULL,
    subscribed boolean NOT NULL
);

CREATE FUNCTION update(uid integer, uname text)
    RETURNS boolean AS $$
DECLARE
USER_EXISTS boolean;
VISIT_DATE timestamp;
BEGIN
    SELECT EXISTS(SELECT id FROM users WHERE id = uid) INTO USER_EXISTS;
    SELECT NOW() INTO VISIT_DATE;

    IF USER_EXISTS THEN
        UPDATE users SET last_visit = VISIT_DATE, name = uname WHERE id = uid;
    ELSE
        INSERT INTO users (id, name, joined, last_visit, subscribed) values (uid, uname, VISIT_DATE, VISIT_DATE, TRUE);
    END IF;

    RETURN TRUE;
END; $$
LANGUAGE PLPGSQL; 

CREATE FUNCTION update(uid integer, uname text, subscribe boolean)
    RETURNS boolean AS $$
DECLARE
USER_EXISTS boolean;
VISIT_DATE timestamp;
BEGIN
    SELECT EXISTS(SELECT id FROM users WHERE id = uid) INTO USER_EXISTS;
    SELECT NOW() INTO VISIT_DATE;

    IF USER_EXISTS THEN
        UPDATE users SET last_visit = VISIT_DATE, name = uname, subscribed = subscribe WHERE id = uid;
    ELSE
        INSERT INTO users (id, name, joined, last_visit, subscribed) values (uid, uname, VISIT_DATE, VISIT_DATE, subscribe);
    END IF;

    RETURN TRUE;
END; $$
LANGUAGE PLPGSQL; 

ALTER TABLE public.users OWNER TO cakesbot;

CREATE TABLE cakes (
    id integer NOT NULL,
    post_id integer NOT NULL,
--    author_id integer references authors(id),
    poem boolean,
    text text NOT NULL,
    raw_text text NOT NULL,
    raw_author text NOT NULL,
    author text NOT NULL,
    date timestamp without time zone NOT NULL
);

ALTER TABLE public.cakes OWNER TO cakesbot;

--
-- Name: cakes_id_seq; Type: SEQUENCE; Schema: public; Owner: cakesbot
--

CREATE SEQUENCE cakes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cakes_id_seq OWNER TO cakesbot;

--
-- Name: cakes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cakesbot
--

ALTER SEQUENCE cakes_id_seq OWNED BY cakes.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: cakesbot
--

ALTER TABLE ONLY cakes ALTER COLUMN id SET DEFAULT nextval('cakes_id_seq'::regclass);


--
-- Name: cakes_pkey; Type: CONSTRAINT; Schema: public; Owner: cakesbot; Tablespace: 
--

ALTER TABLE ONLY cakes
    ADD CONSTRAINT cakes_pkey PRIMARY KEY (id);


--
-- Name: cakes_post_id_key; Type: CONSTRAINT; Schema: public; Owner: cakesbot; Tablespace: 
--

-- ALTER TABLE ONLY cakes
--    ADD CONSTRAINT cakes_post_id_key UNIQUE (post_id);
--

--
-- Name: cakes_idx; Type: INDEX; Schema: public; Owner: cakesbot; Tablespace: 
--

CREATE INDEX cakes_idx ON cakes USING gin (to_tsvector('russian'::regconfig, text));


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

