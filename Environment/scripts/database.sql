--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

-- Started on 2024-12-26 19:06:45

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 217 (class 1259 OID 24611)
-- Name: t_guest_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_guest_accounts (
    user_id integer NOT NULL,
    being_used boolean DEFAULT false NOT NULL,
    expiry_date date
);


--
-- TOC entry 218 (class 1259 OID 24620)
-- Name: t_user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_user_roles (
    id integer NOT NULL,
    name text
);


--
-- TOC entry 219 (class 1259 OID 24627)
-- Name: t_user_user_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_user_user_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


--
-- TOC entry 215 (class 1259 OID 16410)
-- Name: t_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.t_users (
    username text NOT NULL,
    password text NOT NULL,
    id integer NOT NULL,
    salt text NOT NULL,
    email text
);


--
-- TOC entry 4863 (class 0 OID 0)
-- Dependencies: 215
-- Name: COLUMN t_users.salt; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_users.salt IS 'Salt used during user authentication';


--
-- TOC entry 4864 (class 0 OID 0)
-- Dependencies: 215
-- Name: COLUMN t_users.email; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.t_users.email IS 'Address email used for password recovery';


--
-- TOC entry 216 (class 1259 OID 16419)
-- Name: t_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.t_users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.t_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 4855 (class 0 OID 24611)
-- Dependencies: 217
-- Data for Name: t_guest_accounts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.t_guest_accounts (user_id, being_used, expiry_date) FROM stdin;
10	f	\N
\.


--
-- TOC entry 4856 (class 0 OID 24620)
-- Dependencies: 218
-- Data for Name: t_user_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.t_user_roles (id, name) FROM stdin;
1	Player
2	Guest
\.


--
-- TOC entry 4857 (class 0 OID 24627)
-- Dependencies: 219
-- Data for Name: t_user_user_roles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.t_user_user_roles (user_id, role_id) FROM stdin;
10	1
10	2
\.


--
-- TOC entry 4853 (class 0 OID 16410)
-- Dependencies: 215
-- Data for Name: t_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.t_users (username, password, id, salt, email) FROM stdin;
tester	c3d363cf94e5aa04b474022280f15794a0c02058d5298fc08e358c64eb45ca5d	1	salt_test	tester@example.com
tester2	c4d1183f8d63d87d92171b8cb4e3812911a828118c0fe24a23cad196944dc753	2	zabka	tester2@example.com
guest#0001	0404245baf3815fd36c8b84e768d8414da5868f39e97d5469e0a9155aae2d5ec	3	O6v7z3ETa6	guest0001@exmple.com
\.


--
-- TOC entry 4865 (class 0 OID 0)
-- Dependencies: 216
-- Name: t_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.t_users_id_seq', 3, true);


--
-- TOC entry 4706 (class 2606 OID 24626)
-- Name: t_user_roles t_user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_user_roles
    ADD CONSTRAINT t_user_roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4702 (class 2606 OID 16416)
-- Name: t_users t_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_users
    ADD CONSTRAINT t_users_pkey PRIMARY KEY (id);


--
-- TOC entry 4704 (class 2606 OID 16418)
-- Name: t_users t_users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_users
    ADD CONSTRAINT t_users_username_key UNIQUE (username);


--
-- TOC entry 4708 (class 2606 OID 24635)
-- Name: t_user_user_roles role_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_user_user_roles
    ADD CONSTRAINT role_fk FOREIGN KEY (role_id) REFERENCES public.t_user_roles(id);


--
-- TOC entry 4709 (class 2606 OID 24630)
-- Name: t_user_user_roles user_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_user_user_roles
    ADD CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES public.t_users(id);


--
-- TOC entry 4707 (class 2606 OID 24615)
-- Name: t_guest_accounts user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.t_guest_accounts
    ADD CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES public.t_users(id);


-- Completed on 2024-12-26 19:06:45

--
-- PostgreSQL database dump complete
--

