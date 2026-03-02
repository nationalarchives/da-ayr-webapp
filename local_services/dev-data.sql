--
-- PostgreSQL database dump
--

\restrict 7gWCH43hGT7z9GcO102mxHiIE8qIghELLsPOZfSW2XWne7HDJflwy9NZvKzpbOE

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg13+2)
-- Dumped by pg_dump version 18.1 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tablefunc; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS tablefunc WITH SCHEMA public;


--
-- Name: EXTENSION tablefunc; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION tablefunc IS 'functions that manipulate whole tables, including crosstab';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: AVMetadata; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."AVMetadata" (
    "FileId" uuid NOT NULL,
    "AV-Software" text,
    "AV-SoftwareVersion" text
);


ALTER TABLE public."AVMetadata" OWNER TO local_db_user;

--
-- Name: Body; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."Body" (
    "BodyId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "Name" text NOT NULL,
    "Description" text
);


ALTER TABLE public."Body" OWNER TO local_db_user;

--
-- Name: Consignment; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."Consignment" (
    "ConsignmentId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "BodyId" uuid,
    "SeriesId" uuid,
    "ConsignmentReference" text,
    "ConsignmentType" text,
    "IncludeTopLevelFolder" boolean,
    "ContactName" text,
    "ContactEmail" text,
    "TransferStartDatetime" timestamp with time zone,
    "TransferCompleteDatetime" timestamp with time zone,
    "ExportDatetime" timestamp with time zone,
    "CreatedDatetime" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public."Consignment" OWNER TO local_db_user;

--
-- Name: FFIDMetadata; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."FFIDMetadata" (
    "FileId" uuid NOT NULL,
    "Extension" text,
    "PUID" text,
    "FormatName" text,
    "ExtensionMismatch" text,
    "FFID-Software" text,
    "FFID-SoftwareVersion" text,
    "FFID-BinarySignatureFileVersion" text,
    "FFID-ContainerSignatureFileVersion" text
);


ALTER TABLE public."FFIDMetadata" OWNER TO local_db_user;

--
-- Name: File; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."File" (
    "FileId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "ConsignmentId" uuid NOT NULL,
    "FileType" text NOT NULL,
    "FileName" text NOT NULL,
    "FilePath" text NOT NULL,
    "FileReference" text,
    "CiteableReference" text,
    "ParentReference" text,
    "OriginalFilePath" text,
    "Checksum" text,
    "CreatedDatetime" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public."File" OWNER TO local_db_user;

--
-- Name: FileMetadata; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."FileMetadata" (
    "MetadataId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "FileId" uuid,
    "PropertyName" text,
    "Value" text,
    "CreatedDatetime" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public."FileMetadata" OWNER TO local_db_user;

--
-- Name: Series; Type: TABLE; Schema: public; Owner: local_db_user
--

CREATE TABLE public."Series" (
    "SeriesId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "BodyId" uuid,
    "Name" text NOT NULL,
    "Description" text
);


ALTER TABLE public."Series" OWNER TO local_db_user;

--
-- Data for Name: AVMetadata; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."AVMetadata" ("FileId", "AV-Software", "AV-SoftwareVersion") FROM stdin;
5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	yara	4.3.1
5458dc04-8a9d-42c4-bb5e-8239b92eb120	yara	4.3.1
123e4567-e89b-12d3-a456-426614174000	yara	4.3.1
c382ad5b-c747-4214-9135-6061f61c4f75	yara	4.3.1
a0d5a464-7708-4eaa-beb2-057507632224	E2E tests software	E2E tests software version
dc34b1c5-f1dd-4278-86e1-dfe537c267ea	E2E tests software	E2E tests software version
6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	E2E tests software	E2E tests software version
f81c27c6-9451-4a45-bbd3-55dda8d626f6	E2E tests software	E2E tests software version
10dd553d-a6bf-4914-b837-8b2bd053e4d8	E2E tests software	E2E tests software version
568f3dcc-25d3-403c-ab4d-68a959cd1353	E2E tests software	E2E tests software version
ca79a23c-efd1-465d-9b7f-a12e35f36c2c	E2E tests software	E2E tests software version
2ab48274-7e14-4e60-980f-4d8e9d011d05	E2E tests software	E2E tests software version
859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	E2E tests software	E2E tests software version
3bc5628d-9587-49c4-9e94-d200f76d6497	yara	4.3.1
7ce919c0-9f2b-4133-b41f-f85bdecc6a52	yara	4.3.1
ced32116-5b57-4a45-83d0-7a372a6ab333	yara	4.3.1
3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	yara	4.3.1
0a31ffd6-f530-4464-9783-07e5717f1ab4	yara	4.3.1
ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	yara	4.3.1
cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	yara	4.3.1
6cba3e70-d635-42fa-9d4a-607047fd290c	yara	4.3.1
b2279f23-8d07-4fa5-b0af-94ec4123e21e	yara	4.3.1
8211c175-5331-4fba-a14b-24db8fdaf6a1	yara	4.3.1
0de5cb7e-baf6-4f9c-8a52-450dd117ae83	yara	4.3.1
405ea5a6-b71d-4ecd-be3c-43062af8e1e6	yara	4.3.1
cc3a458b-123d-4b01-b7e5-787a05dfd7a7	yara	4.3.1
8ecc93c8-dc96-4419-aeba-f79c84298cc8	yara	4.3.1
f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	yara	4.3.1
db7455e6-3b09-49c4-89c5-19ad2ce52aa5	yara	4.3.1
b9a8f847-ce98-4894-8c48-3986570dec7d	yara	4.3.1
100251bb-5b93-48a9-953f-ad5bd9abfbdc	yara	4.3.1
8ffacc5a-443a-4568-a5c9-c9741955b40f	E2E tests software	E2E tests software version
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	E2E tests software	E2E tests software version
47526ba9-88e5-4cc8-8bc1-d682a10fa270	E2E tests software	E2E tests software version
\.


--
-- Data for Name: Body; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."Body" ("BodyId", "Name", "Description") FROM stdin;
4654e9f9-335b-4ab1-acd8-edff54f908d4	AYR Test Data Department	AYR Test Data Department
8ccc8cd1-c0ee-431d-afad-70cf404ba337	Mock 1 Department	Mock 1 Department
c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	Testing A	Testing A
9ced8d31-ea58-4794-9582-4b4de1409d59	MOCK1 Department	MOCK1 Department
1dafba21-4ba1-4ad0-91e7-6de105dddb67	Test Transferring Body	Test Transferring Body Description
\.


--
-- Data for Name: Consignment; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."Consignment" ("ConsignmentId", "BodyId", "SeriesId", "ConsignmentReference", "ConsignmentType", "IncludeTopLevelFolder", "ContactName", "ContactEmail", "TransferStartDatetime", "TransferCompleteDatetime", "ExportDatetime", "CreatedDatetime") FROM stdin;
d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	4654e9f9-335b-4ab1-acd8-edff54f908d4	93ed0101-2318-45ab-8730-c681958ded7e	TDR-2025-ABCD	standard	f	Random First Name Random Last Name	random.email@example.com	2025-03-13 12:00:00+00	2025-03-13 12:15:00+00	2025-03-13 12:30:00+00	2025-03-13 12:45:00+00
b4a8379c-0767-4a9b-8537-181aed23e837	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JMQK	standard	f	Test First Name Test Last Name	e4dnuhvq@testsomething.com	2024-02-07 14:26:31+00	2024-02-07 14:26:42+00	2024-02-07 14:27:23+00	2024-02-20 10:06:04.777+00
8cb97d25-5607-477e-aa79-eaae89aa4dc5	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JQJV	standard	f	Test First Name Test Last Name	cnrs6ayg@testsomething.com	2024-02-12 11:27:00+00	2024-02-12 11:27:11+00	2024-02-12 11:27:55+00	2024-02-20 10:08:37.659+00
696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JMHS	standard	f	Test First Name Test Last Name	eipzkbx3@testsomething.com	2024-02-07 10:53:03+00	2024-02-07 10:53:11+00	2024-02-07 10:53:52+00	2024-02-20 10:14:59.722+00
64c30a21-d97d-45c7-ac77-1fe905f48add	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JMF6	standard	f	Test First Name Test Last Name	u7cxznnd@testsomething.com	2024-02-07 10:52:23+00	2024-02-07 10:52:56+00	2024-02-07 10:53:39+00	2024-02-20 10:16:26.092+00
df05b8b8-c222-47c3-903b-9b7f2a8aa1c6	9ced8d31-ea58-4794-9582-4b4de1409d59	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2023-MNJ	standard	f	Test First Name Test Last Name	ufcco8tw@testsomething.com	2023-07-28 09:32:34+00	2023-07-28 09:34:05+00	2023-07-28 09:34:45+00	2024-02-20 10:33:39.34+00
016031db-1398-4fe4-b743-630aa82ea32a	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2023-GXFH	standard	t	Paul Young	paul.young@something2.com	2023-11-30 15:32:58+00	2023-11-30 15:46:20+00	2023-11-30 15:47:09+00	2024-02-20 10:34:51.409+00
3184c737-fe10-4493-8025-77adc5062a84	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-J42R	standard	f	Test First Name Test Last Name	xzbu9vs0@testsomething.com	2024-02-19 08:32:59+00	2024-02-19 08:33:38+00	2024-02-19 08:34:20+00	2024-02-20 16:23:56.124+00
436d6273-fcdb-454e-a9a5-8f55fd064457	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2023-BV6	standard	f	Paul Young	paul.young@something2.com	2023-10-18 08:46:20+00	2023-10-18 09:44:07+00	2023-10-18 09:44:51+00	2024-02-20 16:44:57.314+00
2fd4e03e-5913-4c04-b4f2-5a823fafd430	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-KKX4	standard	f	Test First Name Test Last Name	vskf5utn@testsomething.com	2024-03-05 15:05:30+00	2024-03-05 15:05:38+00	2024-03-05 15:06:21+00	2024-03-06 10:43:30.509+00
369d0592-6554-4c6e-84e4-ae06e12bc52f	1dafba21-4ba1-4ad0-91e7-6de105dddb67	0c94b4be-80da-4c29-b03b-e8920689fa4f	AYR-2026-BIVA	Test	t	Test User	test@example.com	2026-03-02 01:56:48.810843+00	1992-03-05 19:54:42.579282+00	1997-08-16 19:54:57.846981+00	2026-03-02 01:56:48.810844+00
\.


--
-- Data for Name: FFIDMetadata; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."FFIDMetadata" ("FileId", "Extension", "PUID", "FormatName", "ExtensionMismatch", "FFID-Software", "FFID-SoftwareVersion", "FFID-BinarySignatureFileVersion", "FFID-ContainerSignatureFileVersion") FROM stdin;
5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	png	fmt/11	Portable Network Graphics (PNG)	    false	Droid	6.7.0	11	20230822
5458dc04-8a9d-42c4-bb5e-8239b92eb120	gif	fmt/3	Graphics Interchange Format (GIF)	false	Droid	6.7.0	111	20230822
123e4567-e89b-12d3-a456-426614174000	webp	fmt/567	WebP Image	false	Droid	6.7.0	111	20230822
c382ad5b-c747-4214-9135-6061f61c4f75	jpg	fmt/43	JPEG Image	false	Droid	6.7.0	111	20230822
04d6e1da-6542-4af9-88a1-a23821c6e2b4	doc	fmt/40	Microsoft Word Document	False	DROID	6.5	202	1
fa9939f4-a0af-4042-8386-a00fc573ef01	doc	fmt/40	Microsoft Word Document	False	DROID	6.5	202	1
a0d5a464-7708-4eaa-beb2-057507632224	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
dc34b1c5-f1dd-4278-86e1-dfe537c267ea	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
f81c27c6-9451-4a45-bbd3-55dda8d626f6	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
10dd553d-a6bf-4914-b837-8b2bd053e4d8	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
568f3dcc-25d3-403c-ab4d-68a959cd1353	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
ca79a23c-efd1-465d-9b7f-a12e35f36c2c	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
2ab48274-7e14-4e60-980f-4d8e9d011d05	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
3bc5628d-9587-49c4-9e94-d200f76d6497				false	Droid	6.7.0	116	20231127
7ce919c0-9f2b-4133-b41f-f85bdecc6a52			\N	\N	Droid	6.6.1	111	20230510
ced32116-5b57-4a45-83d0-7a372a6ab333	pdf	fmt/276	Acrobat PDF 1.7 - Portable Document Format	false	Droid	6.7.0	111	20230822
3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
0a31ffd6-f530-4464-9783-07e5717f1ab4	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	pdf	fmt/276	Acrobat PDF 1.7 - Portable Document Format	false	Droid	6.7.0	111	20230822
6cba3e70-d635-42fa-9d4a-607047fd290c	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
b2279f23-8d07-4fa5-b0af-94ec4123e21e	docx	fmt/276	Acrobat PDF 1.7 - Portable Document Format	true	Droid	6.7.0	111	20230822
8211c175-5331-4fba-a14b-24db8fdaf6a1	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
0de5cb7e-baf6-4f9c-8a52-450dd117ae83				false	Droid	6.7.0	116	20231127
405ea5a6-b71d-4ecd-be3c-43062af8e1e6	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
cc3a458b-123d-4b01-b7e5-787a05dfd7a7	pdf	fmt/276	Acrobat PDF 1.7 - Portable Document Format	false	Droid	6.7.0	111	20230822
8ecc93c8-dc96-4419-aeba-f79c84298cc8	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
db7455e6-3b09-49c4-89c5-19ad2ce52aa5	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
b9a8f847-ce98-4894-8c48-3986570dec7d	docx	fmt/276	Acrobat PDF 1.7 - Portable Document Format	true	Droid	6.7.0	111	20230822
100251bb-5b93-48a9-953f-ad5bd9abfbdc	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
8ffacc5a-443a-4568-a5c9-c9741955b40f	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
47526ba9-88e5-4cc8-8bc1-d682a10fa270	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
062da4a4-dc6f-4c62-895b-b257811a5cba	csv	x-fmt/18	Comma-Separated Values	true	Siegfried	FsURn	BcnUi	UlWyB
271e4cb8-9a68-436a-b5da-263cd26cb10f	doc	fmt/40	Microsoft Word Document	true	DROID	umdWV	IlsWY	elXoZ
935645a6-4abe-4387-b877-018377aefdac	docx	fmt/412	Microsoft Word Open XML Document	false	DROID	IqZgH	XGYfS	sTbpk
32081439-36c9-4f38-8bcb-a8d610f04b0f	epub	\N	Unknown	false	DROID	ZSEzV	IfJHO	ZMKiE
470e55b9-4758-4d68-8c3d-065413fa7d49	jpg	fmt/43	JPEG Image	false	DROID	nAOxg	kDldY	ClLwM
5add6a18-1dc6-4552-9bf8-c8266309ce80	odt	\N	Unknown	true	DROID	RyYjB	MUjGn	tJihR
a84f03f2-df66-40ba-b446-3e4c563c3f23	pdf	fmt/276	PDF	true	DROID	dUxSJ	fvpSV	MKsmt
e894c064-812e-4db1-896f-8c82c92f3d01	png	fmt/11	Portable Network Graphics	true	Siegfried	eppJj	SxflX	lOdhz
02ac3799-c40a-4274-8600-e19e052c6432	ppt	fmt/126	Microsoft PowerPoint Presentation	false	Siegfried	EdEbj	fBPKE	wRkau
092de09f-718a-4053-8d4b-a35dce9e76bd	pptx	fmt/215	Microsoft PowerPoint Open XML Presentation	true	Siegfried	osjBG	xPKwF	Yokju
84d189d1-695e-48c2-8eae-77301283c31e	rtf	fmt/50	Rich Text Format	true	Siegfried	gEqah	WfvWa	YDrrf
fa297160-2b1e-419c-b466-105f49b54d1e	tif	fmt/353	Tagged Image File Format	false	Siegfried	EwFMe	gpHFm	NlBzq
9f536ef7-0100-4e57-a155-6f3c4aff6098	txt	x-fmt/111	Plain Text	true	Siegfried	rbziu	nQYtI	lzcAR
16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	wk1	\N	Lotus 1-2-3 Spreadsheet	false	DROID	eVLCd	ZCZhZ	kBcnx
6c3aa753-1123-455b-aaeb-d5b22e917f79	wk4	x-fmt/116	Lotus 1-2-3 Spreadsheet	false	DROID	QlJkD	AkluQ	rUjPJ
e9cef0ab-e553-4c69-b81e-5676d1749999	wpd	\N	Unknown	false	DROID	wgaCl	oIQTl	XNCOk
451ef2a4-717c-4c5d-b27b-d3904628c3ef	xls	fmt/59	Microsoft Excel Spreadsheet	true	DROID	qHTbb	CHYYS	CCgiH
aa42b744-e64e-489c-95ac-a62927e5716c	xlsx	fmt/214	Microsoft Excel Open XML Spreadsheet	true	Siegfried	oRxNt	xaevO	aYXgI
f43b4d4d-569a-46b2-98d4-8dec2df46966	xml	\N	Unknown	true	Siegfried	jZegH	XwumS	BEIKl
\.


--
-- Data for Name: File; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."File" ("FileId", "ConsignmentId", "FileType", "FileName", "FilePath", "FileReference", "CiteableReference", "ParentReference", "OriginalFilePath", "Checksum", "CreatedDatetime") FROM stdin;
5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	File	Rose_with_Mantis.png	data/AYR_Test_Data/original/Rose_with_Mantis.png	AYR1000	AYR 1/AYR1000	AYR1000		d41d8cd98f00b204e9800998ecf8427e	2025-02-20 10:06:04.833+00
5458dc04-8a9d-42c4-bb5e-8239b92eb120	d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	File	Muybridge_race_horse_animated_184px.gif	data/AYR_Test_Data/original/Muybridge_race_horse_animated_184px.gif	AYR1001	AYR 1/AYR1001	AYR1001		g41d8cd98f00b204e9800998ecf8427e	2025-03-13 12:00:00+00
123e4567-e89b-12d3-a456-426614174000	d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	File	Mary_Ann_Jackson_-_The_Pictorial_Flora;_or_British_Botany_Delineated_-_images_17,_224,_737.webp	data/AYR_Test_Data/original/Mary_Ann_Jackson_-_The_Pictorial_Flora;_or_British_Botany_Delineated_-_images_17,_224,_737.webp	AYR1002	AYR 1/AYR1002	AYR1002		f41d8cd98f00b204e9800998ecf8427e	2025-03-13 12:00:00+00
c382ad5b-c747-4214-9135-6061f61c4f75	d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	File	tna_logo.jpg	data/AYR_Test_Data/original/tna_logo.jpg	AYR1004	AYR 1/AYR1004	AYR1004		e41d8cd98f00b204e9800998ecf8427e	2025-03-13 12:00:00+00
04d6e1da-6542-4af9-88a1-a23821c6e2b4	d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	File	Disposing-of-Digital-Debris-Information-Governance-Practice-and-Strategy - 97.doc	data/AYR_Test_Data/original/Disposing-of-Digital-Debris-Information-Governance-Practice-and-Strategy - 97.doc	AYR1005	AYR 1/AYR1005	AYR1005		342dd841c792a0049584346d1a5c506b	2025-07-18 10:00:00+00
fa9939f4-a0af-4042-8386-a00fc573ef01	d9f8e7c2-4b8d-4c9a-8b7e-1a2b3c4d5e6f	File	Disposing of Digital Debris - 97.doc	data/AYR_Test_Data/original/Disposing of Digital Debris - 97.doc	AYR1006	AYR 1/AYR1006	AYR1006		6862571502419d8f3c26440e7d7dbf55	2025-07-18 10:00:00+00
a0d5a464-7708-4eaa-beb2-057507632224	b4a8379c-0767-4a9b-8537-181aed23e837	File	path1	data/E2E_tests/original/path1	ZD6FVB	MOCK1 123/ZD6FVB	ZD6FVF		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:06:04.833+00
dc34b1c5-f1dd-4278-86e1-dfe537c267ea	b4a8379c-0767-4a9b-8537-181aed23e837	File	path2	data/E2E_tests/original/path2	ZD6FVD	MOCK1 123/ZD6FVD	ZD6FVF		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:06:04.905+00
c797d3a1-b467-4193-8143-5a189e3e3878	b4a8379c-0767-4a9b-8537-181aed23e837	Folder	original	data/E2E_tests/original	ZD6FVF	MOCK1 123/ZD6FVF	ZD6FVC		\N	2024-02-20 10:06:04.946+00
6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	b4a8379c-0767-4a9b-8537-181aed23e837	File	path0	data/E2E_tests/original/path0	ZD6FV9	MOCK1 123/ZD6FV9	ZD6FVF		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:06:04.979+00
aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	b4a8379c-0767-4a9b-8537-181aed23e837	Folder	E2E_tests	data/E2E_tests	ZD6FVC	MOCK1 123/ZD6FVC			\N	2024-02-20 10:06:05.031+00
f81c27c6-9451-4a45-bbd3-55dda8d626f6	8cb97d25-5607-477e-aa79-eaae89aa4dc5	File	path0	data/E2E_tests/original/path0	ZD6NDG	MOCK1 123/ZD6NDG	ZD6NDL		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:08:37.709+00
b723cb63-9589-417c-ba48-643f665f1463	8cb97d25-5607-477e-aa79-eaae89aa4dc5	Folder	original	data/E2E_tests/original	ZD6NDL	MOCK1 123/ZD6NDL	ZD6NDJ		\N	2024-02-20 10:08:37.739+00
10dd553d-a6bf-4914-b837-8b2bd053e4d8	8cb97d25-5607-477e-aa79-eaae89aa4dc5	File	path2	data/E2E_tests/original/path2	ZD6NDK	MOCK1 123/ZD6NDK	ZD6NDL		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:08:37.761+00
2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	8cb97d25-5607-477e-aa79-eaae89aa4dc5	Folder	E2E_tests	data/E2E_tests	ZD6NDJ	MOCK1 123/ZD6NDJ			\N	2024-02-20 10:08:37.792+00
568f3dcc-25d3-403c-ab4d-68a959cd1353	8cb97d25-5607-477e-aa79-eaae89aa4dc5	File	path1	data/E2E_tests/original/path1	ZD6NDH	MOCK1 123/ZD6NDH	ZD6NDL		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:08:37.813+00
ca79a23c-efd1-465d-9b7f-a12e35f36c2c	696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	File	path1	data/E2E_tests/original/path1	ZD6F85	MOCK1 123/ZD6F85	ZD6F88		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:14:59.765+00
2ab48274-7e14-4e60-980f-4d8e9d011d05	696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	File	path2	data/E2E_tests/original/path2	ZD6F87	MOCK1 123/ZD6F87	ZD6F88		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:14:59.816+00
a226a809-5379-4362-926c-3e6964f8bbae	696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	Folder	original	data/E2E_tests/original	ZD6F88	MOCK1 123/ZD6F88	ZD6F86		\N	2024-02-20 10:14:59.878+00
6e03818d-8fe2-4e9d-a378-39532160d7c4	696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	Folder	E2E_tests	data/E2E_tests	ZD6F86	MOCK1 123/ZD6F86			\N	2024-02-20 10:14:59.903+00
859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	File	path0	data/E2E_tests/original/path0	ZD6F84	MOCK1 123/ZD6F84	ZD6F88		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:14:59.936+00
3bc5628d-9587-49c4-9e94-d200f76d6497	64c30a21-d97d-45c7-ac77-1fe905f48add	File	testfile1	data/testfile1	ZD6F6R	MOCK1 123/ZD6F6R			e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:16:26.141+00
7ce919c0-9f2b-4133-b41f-f85bdecc6a52	df05b8b8-c222-47c3-903b-9b7f2a8aa1c6	File	testfile1	data/testfile1	\N	\N	\N		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 10:33:39.401+00
ced32116-5b57-4a45-83d0-7a372a6ab333	016031db-1398-4fe4-b743-630aa82ea32a	File	closed_file_R - Copy.pdf	data/content/redacted/closed_file_R - Copy.pdf	NBRPR	TSTA 1/NBRPR	NBRPW		f391065b47a36a06748720ad9c88545a16c95c3bd3e806fc1c10c68eeccfa328	2024-02-20 10:34:51.453+00
9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	016031db-1398-4fe4-b743-630aa82ea32a	Folder	mismatch	data/content/mismatch	NBRPK	TSTA 1/NBRPK	NBRPM		\N	2024-02-20 10:34:51.481+00
3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	016031db-1398-4fe4-b743-630aa82ea32a	File	file-b2.txt	data/content/folder-b/file-b2.txt	NBRPX	TSTA 1/NBRPX	NBRPS		b62a45f66bbc5d8f234f785b3f2342a07ef6db5fc9bcaf11273f6712a8629c05	2024-02-20 10:34:51.498+00
ed1b679e-805d-403b-b6cd-8fd073a0e832	016031db-1398-4fe4-b743-630aa82ea32a	Folder	content	data/content	NBRPM	TSTA 1/NBRPM			\N	2024-02-20 10:34:51.535+00
0a31ffd6-f530-4464-9783-07e5717f1ab4	016031db-1398-4fe4-b743-630aa82ea32a	File	file-b1.txt	data/content/folder-b/file-b1.txt	NBRPP	TSTA 1/NBRPP	NBRPS		1ac5612f744314f2a32c72e562b4b548ec587888249c23ceae9c19a9b566018c	2024-02-20 10:34:51.549+00
57824039-5538-4169-9136-1a44b7222776	016031db-1398-4fe4-b743-630aa82ea32a	Folder	folder-a	data/content/folder-a	NBRPV	TSTA 1/NBRPV	NBRPM		\N	2024-02-20 10:34:51.587+00
ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	016031db-1398-4fe4-b743-630aa82ea32a	File	closed_file.txt	data/content/redacted/closed_file.txt	NBRP2	TSTA 1/NBRP2	NBRPW		c92a8dc3329c85755f0896b91f690a93a8729eb084037e110db3bf1525b7917d	2024-02-20 10:34:51.613+00
cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	016031db-1398-4fe4-b743-630aa82ea32a	File	closed_file_R.pdf	data/content/redacted/closed_file_R.pdf	NBRPQ	TSTA 1/NBRPQ	NBRPW	data/content/redacted/closed_file.txt	f391065b47a36a06748720ad9c88545a16c95c3bd3e806fc1c10c68eeccfa328	2024-02-20 10:34:51.64+00
6cba3e70-d635-42fa-9d4a-607047fd290c	016031db-1398-4fe4-b743-630aa82ea32a	File	file-a1.txt	data/content/folder-a/file-a1.txt	NBRPN	TSTA 1/NBRPN	NBRPV		4ef13f1d2350fe1e9f79a88ec063031f65da834e8afdd0512e230544cca0a34b	2024-02-20 10:34:51.658+00
60b50686-1689-4aeb-9687-435e76a3b255	016031db-1398-4fe4-b743-630aa82ea32a	Folder	folder-b	data/content/folder-b	NBRPS	TSTA 1/NBRPS	NBRPM		\N	2024-02-20 10:34:51.677+00
63bbfa85-5799-4612-bf3f-0bb9dd3cb067	016031db-1398-4fe4-b743-630aa82ea32a	Folder	redacted	data/content/redacted	NBRPW	TSTA 1/NBRPW	NBRPM		\N	2024-02-20 10:34:51.69+00
b2279f23-8d07-4fa5-b0af-94ec4123e21e	016031db-1398-4fe4-b743-630aa82ea32a	File	mismatch.docx	data/content/mismatch/mismatch.docx	NBRPT	TSTA 1/NBRPT	NBRPK		f391065b47a36a06748720ad9c88545a16c95c3bd3e806fc1c10c68eeccfa328	2024-02-20 10:34:51.703+00
8211c175-5331-4fba-a14b-24db8fdaf6a1	016031db-1398-4fe4-b743-630aa82ea32a	File	file-a2.txt	data/content/folder-a/file-a2.txt	NBRPJ	TSTA 1/NBRPJ	NBRPV		5d11e11deb1705433b900a4b07a07cf6307b595f4121081342aa12f67989b8fa	2024-02-20 10:34:51.724+00
b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	016031db-1398-4fe4-b743-630aa82ea32a	File	file-a1,.txt	data/content/folder-a/file-a1,.txt	NBRPL	TSTA 1/NBRPL	NBRPV		4ef13f1d2350fe1e9f79a88ec063031f65da834e8afdd0512e230544cca0a34b	2024-02-20 10:34:51.742+00
0de5cb7e-baf6-4f9c-8a52-450dd117ae83	3184c737-fe10-4493-8025-77adc5062a84	File	testfile1	data/testfile1	ZD7KSG	MOCK1 123/ZD7KSG			e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-02-20 16:23:56.172+00
405ea5a6-b71d-4ecd-be3c-43062af8e1e6	436d6273-fcdb-454e-a9a5-8f55fd064457	File	closed_file.txt	data/content/redacted/closed_file.txt		\N	\N		53d7e0b4555e6fcbb72de20f962d7b56bf5905032f21beec9a9278b2fd2fa052	2024-02-20 16:44:57.384+00
cc3a458b-123d-4b01-b7e5-787a05dfd7a7	436d6273-fcdb-454e-a9a5-8f55fd064457	File	closed_file_R.pdf	data/content/redacted/closed_file_R.pdf		\N	\N	data/content/redacted/closed_file.txt	f391065b47a36a06748720ad9c88545a16c95c3bd3e806fc1c10c68eeccfa328	2024-02-20 16:44:57.453+00
8ecc93c8-dc96-4419-aeba-f79c84298cc8	436d6273-fcdb-454e-a9a5-8f55fd064457	File	file-a1.txt	data/content/folder-a/file-a1.txt		\N	\N		4ef13f1d2350fe1e9f79a88ec063031f65da834e8afdd0512e230544cca0a34b	2024-02-20 16:44:57.5+00
f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	436d6273-fcdb-454e-a9a5-8f55fd064457	File	file-b1.txt	data/content/folder-b/file-b1.txt		\N	\N		7378fd2184dc4d847ed1ac048658a3cfc2be93eb239da08a16cc09b1157739d1	2024-02-20 16:44:57.538+00
db7455e6-3b09-49c4-89c5-19ad2ce52aa5	436d6273-fcdb-454e-a9a5-8f55fd064457	File	file-b2.txt	data/content/folder-b/file-b2.txt		\N	\N		a0c5eee2309fb2f87d3e32c55b30b522be04665345464a672acf30eade9f088b	2024-02-20 16:44:57.584+00
a3e85444-fd76-4b51-8d91-5047821c7b61	436d6273-fcdb-454e-a9a5-8f55fd064457	Folder	folder-b	data/content/folder-b		\N	\N		\N	2024-02-20 16:44:57.627+00
f323a998-e9a5-42c3-bc8f-eda9efb102e8	436d6273-fcdb-454e-a9a5-8f55fd064457	Folder	folder-a	data/content/folder-a		\N	\N		\N	2024-02-20 16:44:57.652+00
d306fbf4-b3f5-4311-b2ae-b9bce9556c44	436d6273-fcdb-454e-a9a5-8f55fd064457	Folder	content	data/content		\N	\N		\N	2024-02-20 16:44:57.676+00
5d8c077b-5133-4409-9a76-73d91b376175	436d6273-fcdb-454e-a9a5-8f55fd064457	Folder	redacted	data/content/redacted		\N	\N		\N	2024-02-20 16:44:57.711+00
b9a8f847-ce98-4894-8c48-3986570dec7d	436d6273-fcdb-454e-a9a5-8f55fd064457	File	mismatch.docx	data/content/mismatch/mismatch.docx		\N	\N		f391065b47a36a06748720ad9c88545a16c95c3bd3e806fc1c10c68eeccfa328	2024-02-20 16:44:57.751+00
caf080fe-b365-46da-91f1-1aba7689c271	436d6273-fcdb-454e-a9a5-8f55fd064457	Folder	mismatch	data/content/mismatch		\N	\N		\N	2024-02-20 16:44:57.792+00
100251bb-5b93-48a9-953f-ad5bd9abfbdc	436d6273-fcdb-454e-a9a5-8f55fd064457	File	file-a2.txt	data/content/folder-a/file-a2.txt		\N	\N		fc26b66045a653650d483739572f47bac2ab0ef43e66981a5c1d0fb5c86bf14c	2024-02-20 16:44:57.826+00
b5cdde0f-93e8-4975-accf-93372d5774c3	2fd4e03e-5913-4c04-b4f2-5a823fafd430	Folder	original	data/E2E_tests/original	ZD8MCP	MOCK1 123/ZD8MCP	ZD8MCM		\N	2024-03-06 10:43:30.565+00
8ffacc5a-443a-4568-a5c9-c9741955b40f	2fd4e03e-5913-4c04-b4f2-5a823fafd430	File	path0	data/E2E_tests/original/path0	ZD8MCK	MOCK1 123/ZD8MCK	ZD8MCP		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-03-06 10:43:30.624+00
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	2fd4e03e-5913-4c04-b4f2-5a823fafd430	File	path2	data/E2E_tests/original/path2	ZD8MCN	MOCK1 123/ZD8MCN	ZD8MCP		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-03-06 10:43:30.685+00
7fb02107-17e3-4659-a644-69f854a6058d	2fd4e03e-5913-4c04-b4f2-5a823fafd430	Folder	E2E_tests	data/E2E_tests	ZD8MCM	MOCK1 123/ZD8MCM			\N	2024-03-06 10:43:30.768+00
47526ba9-88e5-4cc8-8bc1-d682a10fa270	2fd4e03e-5913-4c04-b4f2-5a823fafd430	File	path1	data/E2E_tests/original/path1	ZD8MCL	MOCK1 123/ZD8MCL	ZD8MCP		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-03-06 10:43:30.809+00
062da4a4-dc6f-4c62-895b-b257811a5cba	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_KTV6RM.csv	data/content/AYR 25_KTV6RM.csv	UJ1O	CITE-0001	\N	\N	xHoOUrgnGb	2026-03-02 01:56:48.927051+00
271e4cb8-9a68-436a-b5da-263cd26cb10f	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZFW6DB.doc	data/content/AYR 25_ZFW6DB.doc	YQVE	CITE-0002	\N	\N	sRNOYehzIC	2026-03-02 01:56:48.941755+00
935645a6-4abe-4387-b877-018377aefdac	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZDC8J4.docx	data/content/AYR 25_ZDC8J4.docx	2Z84	CITE-0003	\N	\N	MaasteOtVg	2026-03-02 01:56:49.001563+00
32081439-36c9-4f38-8bcb-a8d610f04b0f	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_LW73EO.epub	data/content/AYR 25_LW73EO.epub	NXD7	CITE-0004	\N	\N	aAghzVoFUv	2026-03-02 01:56:49.064166+00
470e55b9-4758-4d68-8c3d-065413fa7d49	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_6YTFTC.jpg	data/content/AYR 25_6YTFTC.jpg	62LZ	CITE-0005	\N	\N	bwjdmDJkNB	2026-03-02 01:56:49.130293+00
5add6a18-1dc6-4552-9bf8-c8266309ce80	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_Z9P4WW.odt	data/content/AYR 25_Z9P4WW.odt	SIOE	CITE-0006	\N	\N	GgqXLQgZaY	2026-03-02 01:56:49.2705+00
a84f03f2-df66-40ba-b446-3e4c563c3f23	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZDKL26.pdf	data/content/AYR 25_ZDKL26.pdf	8FYK	CITE-0007	\N	\N	hgxtVRQMel	2026-03-02 01:56:49.286316+00
e894c064-812e-4db1-896f-8c82c92f3d01	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_G85D3R.png	data/content/AYR 25_G85D3R.png	LPD4	CITE-0008	\N	\N	wkmCbEmAQA	2026-03-02 01:56:49.425724+00
02ac3799-c40a-4274-8600-e19e052c6432	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_Z95P37.ppt	data/content/AYR 25_Z95P37.ppt	HHVQ	CITE-0009	\N	\N	HOsjUVjFQZ	2026-03-02 01:56:49.446394+00
092de09f-718a-4053-8d4b-a35dce9e76bd	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZG8SKW.pptx	data/content/AYR 25_ZG8SKW.pptx	W3Y2	CITE-0010	\N	\N	INhAyumIpz	2026-03-02 01:56:49.461783+00
84d189d1-695e-48c2-8eae-77301283c31e	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZJ56LA.rtf	data/content/AYR 25_ZJ56LA.rtf	VGSP	CITE-0011	\N	\N	HgBxeaaZdh	2026-03-02 01:56:49.492164+00
fa297160-2b1e-419c-b466-105f49b54d1e	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_VCT56L.tif	data/content/AYR 25_VCT56L.tif	4ESR	CITE-0012	\N	\N	mtQtUwMMps	2026-03-02 01:56:49.508076+00
9f536ef7-0100-4e57-a155-6f3c4aff6098	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_DNI76K.txt	data/content/AYR 25_DNI76K.txt	ATT2	CITE-0013	\N	\N	tisBmuxTLv	2026-03-02 01:56:49.522843+00
16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZB33RH.wk1	data/content/AYR 25_ZB33RH.wk1	2CXN	CITE-0014	\N	\N	HcenXtssfW	2026-03-02 01:56:49.53779+00
6c3aa753-1123-455b-aaeb-d5b22e917f79	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_ZB33RK.wk4	data/content/AYR 25_ZB33RK.wk4	XGJB	CITE-0015	\N	\N	kEPPtCjAFz	2026-03-02 01:56:49.56211+00
e9cef0ab-e553-4c69-b81e-5676d1749999	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_Z9P523.wpd	data/content/AYR 25_Z9P523.wpd	YWCR	CITE-0016	\N	\N	OPgDeJvKev	2026-03-02 01:56:49.576822+00
451ef2a4-717c-4c5d-b27b-d3904628c3ef	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_VTC9WP.xls	data/content/AYR 25_VTC9WP.xls	RVFZ	CITE-0017	\N	\N	YWIIMmKJiS	2026-03-02 01:56:49.593002+00
aa42b744-e64e-489c-95ac-a62927e5716c	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_UYT6DV.xlsx	data/content/AYR 25_UYT6DV.xlsx	ZJ52	CITE-0018	\N	\N	CAnBaMDjGG	2026-03-02 01:56:49.609039+00
f43b4d4d-569a-46b2-98d4-8dec2df46966	369d0592-6554-4c6e-84e4-ae06e12bc52f	File	AYR 25_Z9P524.xml	data/content/AYR 25_Z9P524.xml	7W07	CITE-0019	\N	\N	xekGtRZVAm	2026-03-02 01:56:49.622988+00
\.


--
-- Data for Name: FileMetadata; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."FileMetadata" ("MetadataId", "FileId", "PropertyName", "Value", "CreatedDatetime") FROM stdin;
f47ac10b-58cc-4372-a567-0e02b2c3d479	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	file_name	Rose_with_Mantis.png	2025-02-20 10:06:04.845+00
effd1331-dffb-4e96-a391-efa9156481fd	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	file_type	File	2025-02-20 10:06:04.867+00
9d20a755-aa38-45dc-8a56-45207756af1a	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	file_size	1024	2025-02-20 10:06:04.87+00
1cadd30a-eded-471e-9afc-e5bf960655d4	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	rights_copyright	Crown Copyright	2025-02-20 10:06:04.874+00
b0656064-864b-4c74-8ccc-c3fd935b84ce	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	legal_status	Public Record(s)	2025-02-20 10:06:04.877+00
4e7cd23d-a8a9-429d-8181-5db7b38cf583	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	held_by	The National Archives, Kew	2025-02-20 10:06:04.88+00
7073972a-181e-479c-a0f5-8dbd8aae87fd	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	date_last_modified	2025-02-07T14:26:31	2025-02-20 10:06:04.883+00
f41d03da-eaaa-43a3-8316-20883a671ef8	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	closure_type	Open	2025-02-20 10:06:04.886+00
58a303d6-6864-464e-87bd-1309fe90b150	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	title_closed	false	2025-02-20 10:06:04.889+00
9a010aa2-d34f-4020-ac08-1ab25914185b	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	description_closed	false	2025-02-20 10:06:04.892+00
39489697-fc0d-49bd-9393-b5097b261d99	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	language	English	2025-02-20 10:06:04.894+00
4d6433ec-a860-428d-a5d2-1ecb40c7ae21	5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	evidence_provided_by	Evidence provided by test	2026-02-26 22:59:54.876329+00
efa981d2-0ce8-4116-9bc5-364917ed7b17	5458dc04-8a9d-42c4-bb5e-8239b92eb120	file_name	Muybridge_race_horse_animated_184px.gif	2025-03-13 12:00:00+00
a1553956-2d0d-4c81-9230-90dc4cd8c337	5458dc04-8a9d-42c4-bb5e-8239b92eb120	file_type	File	2025-03-13 12:00:00+00
e89e76f5-9a60-46ec-90dc-203909060b49	5458dc04-8a9d-42c4-bb5e-8239b92eb120	file_size	2048	2025-03-13 12:00:00+00
b8bcec67-2dc3-4bec-beb1-4bad392b36bf	5458dc04-8a9d-42c4-bb5e-8239b92eb120	rights_copyright	Crown Copyright	2025-03-13 12:00:00+00
2b425af8-4f12-45d3-b11a-48bf620adf63	5458dc04-8a9d-42c4-bb5e-8239b92eb120	legal_status	Public Record(s)	2025-03-13 12:00:00+00
49a1570b-aabc-4b5f-a558-476ed3a8e38f	5458dc04-8a9d-42c4-bb5e-8239b92eb120	held_by	The National Archives, Kew	2025-03-13 12:00:00+00
20fc4aa7-9eb6-4345-b6e7-db3d22a7723c	5458dc04-8a9d-42c4-bb5e-8239b92eb120	date_last_modified	2025-03-13T12:00:00	2025-03-13 12:00:00+00
32d74c57-4847-4431-9df5-edfd1bb0788e	5458dc04-8a9d-42c4-bb5e-8239b92eb120	closure_type	Open	2025-03-13 12:00:00+00
9652619d-7d7b-4dfc-b51b-2eaaeffd48ab	5458dc04-8a9d-42c4-bb5e-8239b92eb120	title_closed	false	2025-03-13 12:00:00+00
02bbff1c-0c09-43e0-90ad-5151cafd77ca	5458dc04-8a9d-42c4-bb5e-8239b92eb120	description_closed	false	2025-03-13 12:00:00+00
2f6732f2-829b-4e1e-a64e-ddd69f8cc1b4	5458dc04-8a9d-42c4-bb5e-8239b92eb120	language	English	2025-03-13 12:00:00+00
302bddca-9c26-47c3-9836-9c5c84010126	5458dc04-8a9d-42c4-bb5e-8239b92eb120	evidence_provided_by		2026-02-27 11:26:46.308337+00
e5878898-c705-487b-ad76-87e32cf9ae81	123e4567-e89b-12d3-a456-426614174000	file_name	Mary_Ann_Jackson_-_The_Pictorial_Flora;_or_British_Botany_Delineated_-_images_17,_224,_737.webp	2025-03-13 12:00:00+00
dd600d53-00f1-4a62-9b99-c81fbe54e00a	123e4567-e89b-12d3-a456-426614174000	file_type	File	2025-03-13 12:00:00+00
60a05cb5-6c88-4114-b906-8bc63d0e8892	123e4567-e89b-12d3-a456-426614174000	file_size	3072	2025-03-13 12:00:00+00
4a51ac61-12dd-4f97-9612-fce74120af28	123e4567-e89b-12d3-a456-426614174000	rights_copyright	Crown Copyright	2025-03-13 12:00:00+00
35245b26-b7d0-4915-876a-53141d655ba0	123e4567-e89b-12d3-a456-426614174000	legal_status	Public Record(s)	2025-03-13 12:00:00+00
135f48e5-677b-4541-830b-ffcdc99c3bfe	123e4567-e89b-12d3-a456-426614174000	held_by	The National Archives, Kew	2025-03-13 12:00:00+00
2d3b97c8-cde0-478e-a9c8-7024ad1715e5	123e4567-e89b-12d3-a456-426614174000	date_last_modified	2025-03-13T12:00:00	2025-03-13 12:00:00+00
f9c60b1c-b5ba-4a43-a5d4-d7991d6d4be9	123e4567-e89b-12d3-a456-426614174000	closure_type	Closed	2025-03-13 12:00:00+00
5a2bb3ee-7de8-489f-a4fb-344a9637fd23	123e4567-e89b-12d3-a456-426614174000	title_closed	false	2025-03-13 12:00:00+00
7002c133-f62c-465f-88e5-3e300bd2ab96	123e4567-e89b-12d3-a456-426614174000	description_closed	false	2025-03-13 12:00:00+00
de57153a-3cd6-4a04-b902-db6e0aa9a708	123e4567-e89b-12d3-a456-426614174000	language	English	2025-03-13 12:00:00+00
efd2218b-dc5e-4c6e-8058-dba906702924	123e4567-e89b-12d3-a456-426614174000	evidence_provided_by	Evidence provided by test	2026-02-26 23:22:22.716905+00
995459f1-c8c4-4650-a6b1-27baeaa0f0c3	c382ad5b-c747-4214-9135-6061f61c4f75	file_name	tna_logo.jpg	2025-03-13 12:00:00+00
12f66d04-0d41-4b85-97de-433b3f06e9cd	c382ad5b-c747-4214-9135-6061f61c4f75	file_type	File	2025-03-13 12:00:00+00
86c88268-e1cf-47c8-83a9-490bbdb3fdab	c382ad5b-c747-4214-9135-6061f61c4f75	file_size	1024	2025-03-13 12:00:00+00
ef901edc-7def-459a-b37e-899e1c16995e	c382ad5b-c747-4214-9135-6061f61c4f75	rights_copyright	Crown Copyright	2025-03-13 12:00:00+00
0756f180-e1fa-4f44-8999-912db94eef9d	c382ad5b-c747-4214-9135-6061f61c4f75	legal_status	Public Record(s)	2025-03-13 12:00:00+00
53a35cc8-d796-4a81-b2ca-d417af5677f8	c382ad5b-c747-4214-9135-6061f61c4f75	held_by	The National Archives, Kew	2025-03-13 12:00:00+00
29750bd9-cf49-4da1-a2f1-648c4f9027f8	c382ad5b-c747-4214-9135-6061f61c4f75	date_last_modified	2025-02-07T14:26:31	2025-02-20 10:06:04.883+00
eb7738fa-2e19-454e-9229-ca762a5951cd	c382ad5b-c747-4214-9135-6061f61c4f75	closure_type	Open	2025-02-20 10:06:04.886+00
417950ee-b122-4569-ac4b-15ffbd6687ea	c382ad5b-c747-4214-9135-6061f61c4f75	title_closed	false	2025-02-20 10:06:04.889+00
3cafcc1f-5446-4754-8293-b424b233c29c	c382ad5b-c747-4214-9135-6061f61c4f75	description_closed	false	2025-02-20 10:06:04.892+00
d9bd72e6-e859-406b-8ed7-227c397849c6	c382ad5b-c747-4214-9135-6061f61c4f75	language	English	2025-02-20 10:06:04.894+00
d1aa0600-1a9a-4cf6-a4a5-8a1f01e44501	04d6e1da-6542-4af9-88a1-a23821c6e2b4	file_name	Disposing-of-Digital-Debris-Information-Governance-Practice-and-Strategy - 97.doc	2025-02-20 10:06:04.845+00
6c6d6c20-8a35-405b-b1a2-3b6ce5f4c102	04d6e1da-6542-4af9-88a1-a23821c6e2b4	file_type	File	2025-07-18 10:06:04.845+00
b1cb246e-8ddf-41fa-8f4e-c4d2b99bc709	04d6e1da-6542-4af9-88a1-a23821c6e2b4	file_size	5474883	2025-07-18 10:06:04.845+00
06c60aa5-6f56-470c-8541-bf5f620b58a1	04d6e1da-6542-4af9-88a1-a23821c6e2b4	rights_copyright	Crown copyright	2025-07-18 10:06:04.845+00
2ee110af-b961-43a6-a31c-79d0c13b4350	04d6e1da-6542-4af9-88a1-a23821c6e2b4	legal_status	Public Record(s)	2025-07-18 10:06:04.845+00
af63226b-7e6a-429b-8124-2f61594e3583	04d6e1da-6542-4af9-88a1-a23821c6e2b4	held_by	The National Archives, Kew	2025-07-18 10:06:04.845+00
0d509ec7-53a4-4e37-a8bc-785c31f292b7	04d6e1da-6542-4af9-88a1-a23821c6e2b4	date_last_modified	2024-02-07T14:26:31	2025-07-18 10:06:04.845+00
d1c6c9b0-f86a-4a08-a58a-119d2d5e0171	04d6e1da-6542-4af9-88a1-a23821c6e2b4	closure_type	Open	2025-07-18 10:06:04.845+00
012e08c7-65ee-4907-8b4e-4b374e0bbd86	04d6e1da-6542-4af9-88a1-a23821c6e2b4	title_closed	false	2025-07-18 10:06:04.845+00
d3dfb084-607c-41db-8056-27d65b4700b6	04d6e1da-6542-4af9-88a1-a23821c6e2b4	description_closed	false	2025-07-18 10:06:04.845+00
e786be50-c7f2-4d1d-9393-57f9536f09a9	04d6e1da-6542-4af9-88a1-a23821c6e2b4	language	English	2025-07-18 10:06:04.845+00
d9b7260a-34e6-449c-8cd1-aa7bf0a7eb99	fa9939f4-a0af-4042-8386-a00fc573ef01	file_name	Disposing of Digital Debris - 97.doc	2025-02-20 10:06:04.845+00
681d032c-dba9-45ae-a98d-e31298bc8c25	fa9939f4-a0af-4042-8386-a00fc573ef01	file_type	File	2025-07-18 10:06:04.845+00
f7c6d3b4-78f1-41c3-9e1c-5f6a5c9ffecd	fa9939f4-a0af-4042-8386-a00fc573ef01	file_size	2677248	2025-07-18 10:06:04.845+00
a32a5052-4ec2-43d8-8788-2aeb7e249d83	fa9939f4-a0af-4042-8386-a00fc573ef01	rights_copyright	Crown Copyright	2025-07-18 10:06:04.845+00
c62e008c-7c0e-4ac4-9df9-6f308bdf174b	fa9939f4-a0af-4042-8386-a00fc573ef01	legal_status	Public Record(s)	2025-07-18 10:06:04.845+00
40d124ed-406e-4a62-b34b-9f61a317ad11	fa9939f4-a0af-4042-8386-a00fc573ef01	held_by	The National Archives, Kew 	2025-07-18 10:06:04.845+00
2af92d6b-6fe7-414c-b0ca-5baf5cb1619e	fa9939f4-a0af-4042-8386-a00fc573ef01	date_last_modified	2024-02-07T14:26:31	2025-07-18 10:06:04.845+00
8b59de54-dfb4-41de-8c3a-04230c2ce29d	fa9939f4-a0af-4042-8386-a00fc573ef01	closure_type	Open	2025-07-18 10:06:04.845+00
f05b4f0c-5f03-42a1-aec2-3c8ff1d38e2a	fa9939f4-a0af-4042-8386-a00fc573ef01	title_closed	false	2025-07-18 10:06:04.845+00
1113288a-8cd3-46cd-a142-8fd25cf02ec8	fa9939f4-a0af-4042-8386-a00fc573ef01	description_closed	false	2025-07-18 10:06:04.845+00
8ea139c4-7c7a-4c2c-9806-f87c5d9d676d	fa9939f4-a0af-4042-8386-a00fc573ef01	language	English	2025-07-18 10:06:04.845+00
9b818156-0e4d-4a15-8ac6-4fb536507c2b	a0d5a464-7708-4eaa-beb2-057507632224	file_name	path1	2024-02-20 10:06:04.845+00
04ab0605-fde0-476c-bbf1-576265824ab9	a0d5a464-7708-4eaa-beb2-057507632224	file_type	File	2024-02-20 10:06:04.867+00
0cd39341-a7a6-4b31-a078-5747d6e9a1d9	a0d5a464-7708-4eaa-beb2-057507632224	file_size	1024	2024-02-20 10:06:04.87+00
6aeff7bc-a8bf-4ccc-a64b-2bc30b010456	a0d5a464-7708-4eaa-beb2-057507632224	rights_copyright	Crown Copyright	2024-02-20 10:06:04.874+00
57b900f6-f04f-41cb-ada3-e78546e399d4	a0d5a464-7708-4eaa-beb2-057507632224	legal_status	Public Record(s)	2024-02-20 10:06:04.877+00
ba95b5db-f0cc-4bc8-a79a-deb0aedd2aae	a0d5a464-7708-4eaa-beb2-057507632224	held_by	The National Archives, Kew	2024-02-20 10:06:04.88+00
1a5bb0b2-939c-4a73-bee1-f768b55d7494	a0d5a464-7708-4eaa-beb2-057507632224	date_last_modified	2024-02-07T14:26:31	2024-02-20 10:06:04.883+00
4e5096cb-f4ee-4f87-ba1b-18bc1958af33	a0d5a464-7708-4eaa-beb2-057507632224	closure_type	Open	2024-02-20 10:06:04.886+00
9ae274b8-3bcb-41c1-a487-de7d1dc434a5	a0d5a464-7708-4eaa-beb2-057507632224	title_closed	false	2024-02-20 10:06:04.889+00
5d1d65c9-2e5a-4711-a9b5-222c5ccd44d9	a0d5a464-7708-4eaa-beb2-057507632224	description_closed	false	2024-02-20 10:06:04.892+00
fd0e1ac8-a831-4a17-b32e-1a7fabb60c1d	a0d5a464-7708-4eaa-beb2-057507632224	language	English	2024-02-20 10:06:04.894+00
88427675-5342-44dd-ae3c-910ae0a24b61	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	file_name	path2	2024-02-20 10:06:04.908+00
f50b472b-1e2d-40e0-ac1b-73345527f94c	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	file_type	File	2024-02-20 10:06:04.91+00
eeb41294-6dfe-4153-b419-786608af437f	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	file_size	1024	2024-02-20 10:06:04.918+00
4cc9e772-2435-4026-b7af-e48d1ff102fa	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	rights_copyright	Crown Copyright	2024-02-20 10:06:04.92+00
d2e1f029-c339-4797-9f14-d35102309af1	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	legal_status	Public Record(s)	2024-02-20 10:06:04.923+00
8f76b31c-3910-4cc9-8292-df9def2f50ba	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	held_by	The National Archives, Kew	2024-02-20 10:06:04.925+00
4951b5ca-80a1-408c-9afc-66dcac970ce8	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	date_last_modified	2024-02-07T14:26:31	2024-02-20 10:06:04.928+00
15104d3d-a140-4371-94c4-128a0a1cd3ea	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	closure_type	Open	2024-02-20 10:06:04.93+00
fd45689c-58a5-4798-afc8-4f356ed48b7a	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	title_closed	false	2024-02-20 10:06:04.933+00
77f81247-2290-4a36-a206-992b78cab54e	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	description_closed	false	2024-02-20 10:06:04.936+00
df9bd1e3-b636-4362-bd8f-7eb33e4e8013	dc34b1c5-f1dd-4278-86e1-dfe537c267ea	language	English	2024-02-20 10:06:04.938+00
4665f2eb-1a1b-4941-88f0-abb2a1258794	c797d3a1-b467-4193-8143-5a189e3e3878	file_name	original	2024-02-20 10:06:04.949+00
112c8e87-d98b-49ac-bdf7-4fecbe2499ee	c797d3a1-b467-4193-8143-5a189e3e3878	file_type	Folder	2024-02-20 10:06:04.951+00
78a2c589-d022-42d7-b38b-f334d17713c9	c797d3a1-b467-4193-8143-5a189e3e3878	rights_copyright	Crown Copyright	2024-02-20 10:06:04.954+00
d314aa20-ae70-4ec4-b88f-d650c3b5c5ec	c797d3a1-b467-4193-8143-5a189e3e3878	legal_status	Public Record(s)	2024-02-20 10:06:04.957+00
81d1f815-50fd-4b37-95ea-deb7ea724970	c797d3a1-b467-4193-8143-5a189e3e3878	held_by	The National Archives, Kew	2024-02-20 10:06:04.96+00
830ea566-df17-473d-a301-6b73d9781d72	c797d3a1-b467-4193-8143-5a189e3e3878	closure_type	Open	2024-02-20 10:06:04.962+00
49de9921-d6b9-43b3-83e5-551ca4c406ac	c797d3a1-b467-4193-8143-5a189e3e3878	title_closed	false	2024-02-20 10:06:04.965+00
28751fd1-2d5e-49f0-8640-56dce49055e1	c797d3a1-b467-4193-8143-5a189e3e3878	description_closed	false	2024-02-20 10:06:04.968+00
2e78cfb4-7c5c-40cd-9fe4-63ee9ae8caf5	c797d3a1-b467-4193-8143-5a189e3e3878	language	English	2024-02-20 10:06:04.974+00
672779a6-45fe-4c63-ad07-47fb32c7bcd6	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	file_name	path0	2024-02-20 10:06:04.983+00
62578b09-4710-4386-a11f-3caad43a0e4b	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	file_type	File	2024-02-20 10:06:04.986+00
a702c396-383d-40bf-8338-82d720fad82a	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	file_size	1024	2024-02-20 10:06:04.99+00
1a374f2f-d339-4c11-8745-c4e145c05ca1	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	rights_copyright	Crown Copyright	2024-02-20 10:06:04.992+00
ee68b025-b988-4efb-99d6-baa7b6f29baf	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	legal_status	Public Record(s)	2024-02-20 10:06:04.995+00
d3a5d6ad-b7e6-4268-9414-31abfe04c2eb	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	held_by	The National Archives, Kew	2024-02-20 10:06:04.998+00
3a173300-0899-4b6c-8c34-ff5e99e1973d	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	date_last_modified	2024-02-07T14:26:31	2024-02-20 10:06:05.002+00
3683ebe6-ec17-4a7e-88e3-150f5d2ab252	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	closure_type	Open	2024-02-20 10:06:05.008+00
86f4bfe3-66e8-49ac-a1b2-b52f58cd1d86	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	title_closed	false	2024-02-20 10:06:05.011+00
6f0ba1a8-de55-4721-8230-91968eee2b8f	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	description_closed	false	2024-02-20 10:06:05.014+00
69122141-5302-4376-881d-f61ed4ee90b9	6abda9e3-99d5-47ce-8b03-94e13c9d8e9a	language	English	2024-02-20 10:06:05.017+00
81189a8a-eba6-4234-b315-79dd1b0a8104	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	file_name	E2E_tests	2024-02-20 10:06:05.034+00
086feade-1ede-4897-a1d9-7dd5b677d30b	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	file_type	Folder	2024-02-20 10:06:05.036+00
477e50e7-89f0-42af-8d3f-eb2dfad9ddb9	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	rights_copyright	Crown Copyright	2024-02-20 10:06:05.039+00
df335fa2-7b39-41c0-a20d-d5be8f176864	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	legal_status	Public Record(s)	2024-02-20 10:06:05.042+00
6407ed47-c26b-4775-b85d-03045d286ccc	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	held_by	The National Archives, Kew	2024-02-20 10:06:05.044+00
6d39cadc-bbbc-4cbb-bf07-9f29cc9f6fc4	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	closure_type	Open	2024-02-20 10:06:05.047+00
c0f84ccf-f19c-40ce-804a-8d18c0a749ab	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	title_closed	false	2024-02-20 10:06:05.049+00
e495d622-9c18-428e-b300-b9515debcff8	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	description_closed	false	2024-02-20 10:06:05.052+00
994024ef-1cac-4769-a416-c2e57245ebe5	aca35e73-2784-4a2d-a58c-3b7bcb5f3f52	language	English	2024-02-20 10:06:05.055+00
7ed27910-30d4-402f-b596-5b2821dafede	f81c27c6-9451-4a45-bbd3-55dda8d626f6	file_name	path0	2024-02-20 10:08:37.713+00
783f1343-4ec6-47bb-9429-685f8f618472	f81c27c6-9451-4a45-bbd3-55dda8d626f6	file_type	File	2024-02-20 10:08:37.716+00
2f0a8572-dad1-4103-94d1-b1073aeefde3	f81c27c6-9451-4a45-bbd3-55dda8d626f6	file_size	1024	2024-02-20 10:08:37.718+00
8fe69f0c-abb0-4400-a11b-108d3ba81ef5	f81c27c6-9451-4a45-bbd3-55dda8d626f6	rights_copyright	Crown Copyright	2024-02-20 10:08:37.72+00
6cfd96ff-283f-40c1-9f7f-f3f247e0642b	f81c27c6-9451-4a45-bbd3-55dda8d626f6	legal_status	Public Record(s)	2024-02-20 10:08:37.722+00
59070004-62af-4e23-aa76-d8ec9fcfb16c	f81c27c6-9451-4a45-bbd3-55dda8d626f6	held_by	The National Archives, Kew	2024-02-20 10:08:37.724+00
5f9ec8c6-36af-45e9-b08a-0936bf77d6e7	f81c27c6-9451-4a45-bbd3-55dda8d626f6	date_last_modified	2024-02-12T11:27:00	2024-02-20 10:08:37.725+00
6b92fd49-3536-4c9d-963f-0826d58e896a	f81c27c6-9451-4a45-bbd3-55dda8d626f6	closure_type	Open	2024-02-20 10:08:37.727+00
9a1db8b1-d612-4dc4-9675-4fac760c22ac	f81c27c6-9451-4a45-bbd3-55dda8d626f6	title_closed	false	2024-02-20 10:08:37.73+00
0564a9a5-ad7a-43e1-a369-3421e029a126	f81c27c6-9451-4a45-bbd3-55dda8d626f6	description_closed	false	2024-02-20 10:08:37.732+00
e80496f2-52fc-46f2-968b-a6e1f94abd44	f81c27c6-9451-4a45-bbd3-55dda8d626f6	language	English	2024-02-20 10:08:37.733+00
7627216c-c862-47a3-bcd2-e7a99a823c6a	b723cb63-9589-417c-ba48-643f665f1463	file_name	original	2024-02-20 10:08:37.744+00
b3dd1f55-09b1-4b77-ae7e-8f04d8c508b9	b723cb63-9589-417c-ba48-643f665f1463	file_type	Folder	2024-02-20 10:08:37.746+00
00c25980-9fcd-4f29-bef7-c3e1734ec19a	b723cb63-9589-417c-ba48-643f665f1463	rights_copyright	Crown Copyright	2024-02-20 10:08:37.747+00
e30d7459-04fc-4c28-bc54-1df9c21dffae	b723cb63-9589-417c-ba48-643f665f1463	legal_status	Public Record(s)	2024-02-20 10:08:37.75+00
631c2962-d04c-412a-8a2a-0a1e1c1ea55f	b723cb63-9589-417c-ba48-643f665f1463	held_by	The National Archives, Kew	2024-02-20 10:08:37.752+00
f4f233be-a743-4d77-bb6c-4b552800c6c4	b723cb63-9589-417c-ba48-643f665f1463	closure_type	Open	2024-02-20 10:08:37.754+00
e2713761-055b-42f0-bc0e-f321ee4848b4	b723cb63-9589-417c-ba48-643f665f1463	title_closed	false	2024-02-20 10:08:37.756+00
f45aaa19-9357-40f4-becb-92b8a1e8b30a	b723cb63-9589-417c-ba48-643f665f1463	description_closed	false	2024-02-20 10:08:37.757+00
961e7f59-ddde-403c-929d-2eeeeddc9fec	b723cb63-9589-417c-ba48-643f665f1463	language	English	2024-02-20 10:08:37.759+00
0e03a201-a260-4e96-bdb2-116fc9406111	10dd553d-a6bf-4914-b837-8b2bd053e4d8	file_name	path2	2024-02-20 10:08:37.763+00
41abe5b9-19b8-4dcb-88ed-ead905359824	10dd553d-a6bf-4914-b837-8b2bd053e4d8	file_type	File	2024-02-20 10:08:37.765+00
f4836c71-8c51-484e-8c57-c04c9fde9d05	10dd553d-a6bf-4914-b837-8b2bd053e4d8	file_size	1024	2024-02-20 10:08:37.767+00
ef2a186c-81f0-4d57-997c-afbba5ba602c	10dd553d-a6bf-4914-b837-8b2bd053e4d8	rights_copyright	Crown Copyright	2024-02-20 10:08:37.768+00
009fddeb-c01a-4514-8c37-5bfae4ca8ed1	10dd553d-a6bf-4914-b837-8b2bd053e4d8	legal_status	Public Record(s)	2024-02-20 10:08:37.77+00
bd938fb9-74e0-4633-a1bf-a973bc9dafa5	10dd553d-a6bf-4914-b837-8b2bd053e4d8	held_by	The National Archives, Kew	2024-02-20 10:08:37.771+00
15bb18a2-1ed7-4584-a600-173cc927d517	10dd553d-a6bf-4914-b837-8b2bd053e4d8	date_last_modified	2024-02-12T11:27:00	2024-02-20 10:08:37.773+00
ed8ac2d3-c53b-409f-982c-404d34fa648f	10dd553d-a6bf-4914-b837-8b2bd053e4d8	closure_type	Open	2024-02-20 10:08:37.776+00
55e51ffa-2659-4b36-ad64-04176fbdee84	10dd553d-a6bf-4914-b837-8b2bd053e4d8	title_closed	false	2024-02-20 10:08:37.779+00
d3b8a61f-a7e7-42d5-8311-c11ebe601763	10dd553d-a6bf-4914-b837-8b2bd053e4d8	description_closed	false	2024-02-20 10:08:37.78+00
99d13666-f6b0-41fa-a250-7e04c612f0b3	10dd553d-a6bf-4914-b837-8b2bd053e4d8	language	English	2024-02-20 10:08:37.786+00
71ec0eb6-fd4f-4e5a-a35c-662fb591785f	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	file_name	E2E_tests	2024-02-20 10:08:37.794+00
e052670a-a729-4d0f-9994-3441518e1392	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	file_type	Folder	2024-02-20 10:08:37.796+00
04ffb7b8-f2f7-4eb8-9525-44d8f1bac6cf	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	rights_copyright	Crown Copyright	2024-02-20 10:08:37.797+00
b19ba5e3-2e6b-4f73-9521-63d177677ece	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	legal_status	Public Record(s)	2024-02-20 10:08:37.799+00
8f74ffd4-529b-4fcd-9c28-d369c0c4f646	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	held_by	The National Archives, Kew	2024-02-20 10:08:37.8+00
3a097166-db3e-4aeb-b2a6-0239dc9e57e2	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	closure_type	Open	2024-02-20 10:08:37.802+00
f26fb226-5932-4d73-a32a-2fd97edf0196	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	title_closed	false	2024-02-20 10:08:37.806+00
e59bedc1-640b-4af4-ab59-7f0b91f9682f	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	description_closed	false	2024-02-20 10:08:37.81+00
c07c4930-5e29-4d74-9599-8851e6ea62f6	2d5a2138-b66d-4be0-ba6d-6560ecc3e5d5	language	English	2024-02-20 10:08:37.811+00
cb168e7c-6fef-463c-926a-10d77afe81f9	568f3dcc-25d3-403c-ab4d-68a959cd1353	file_name	path1	2024-02-20 10:08:37.815+00
24c5aeca-0ade-44d9-8ea3-8dd82152d0da	568f3dcc-25d3-403c-ab4d-68a959cd1353	file_type	File	2024-02-20 10:08:37.817+00
ea87bdd6-5e65-46a3-8818-4c7f8a3e4f56	568f3dcc-25d3-403c-ab4d-68a959cd1353	file_size	1024	2024-02-20 10:08:37.819+00
397318b1-c09f-40b9-b17e-6b62f4738d2e	568f3dcc-25d3-403c-ab4d-68a959cd1353	rights_copyright	Crown Copyright	2024-02-20 10:08:37.82+00
6a32f326-e820-406d-a779-5aca5d474aca	568f3dcc-25d3-403c-ab4d-68a959cd1353	legal_status	Public Record(s)	2024-02-20 10:08:37.821+00
c9952ec3-9b43-4c12-80ab-85232fe6f471	568f3dcc-25d3-403c-ab4d-68a959cd1353	held_by	The National Archives, Kew	2024-02-20 10:08:37.823+00
2a4605a8-a041-4e20-ad6a-fd2ba4e27e7d	568f3dcc-25d3-403c-ab4d-68a959cd1353	date_last_modified	2024-02-12T11:27:00	2024-02-20 10:08:37.825+00
91d7fcf2-b71e-4c01-b136-99a705ee888a	568f3dcc-25d3-403c-ab4d-68a959cd1353	closure_type	Open	2024-02-20 10:08:37.826+00
260cdd18-f6b8-4ddd-bd9d-4432c55f1748	568f3dcc-25d3-403c-ab4d-68a959cd1353	title_closed	false	2024-02-20 10:08:37.829+00
ca9ffe4e-4c8e-4c8e-a2e2-f5879f0efc04	568f3dcc-25d3-403c-ab4d-68a959cd1353	description_closed	false	2024-02-20 10:08:37.835+00
86cd973f-f2d3-45f8-9b66-a4c4c3c4564d	568f3dcc-25d3-403c-ab4d-68a959cd1353	language	English	2024-02-20 10:08:37.836+00
225422ab-1565-483b-a932-0b9df4d2c677	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	file_name	path1	2024-02-20 10:14:59.773+00
dbb385eb-6804-454d-8e59-e7515013e747	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	file_type	File	2024-02-20 10:14:59.78+00
5b7d5403-0bd0-4d0d-a78d-6adc5797ef59	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	file_size	1024	2024-02-20 10:14:59.783+00
22e77b6b-5f9a-4a5a-a54c-e68456298cbf	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	rights_copyright	Crown Copyright	2024-02-20 10:14:59.786+00
711474c2-749e-4a29-9d76-c52bae7f3e2d	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	legal_status	Public Record(s)	2024-02-20 10:14:59.789+00
986ca03e-e777-4561-ac5d-0838d407777b	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	held_by	The National Archives, Kew	2024-02-20 10:14:59.792+00
6b7ab98f-2ea8-48f3-9df9-ae8627252623	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	date_last_modified	2024-02-07T10:53:04	2024-02-20 10:14:59.795+00
f46c9a1a-68e1-4163-9bca-e7cde538e5a1	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	closure_type	Open	2024-02-20 10:14:59.798+00
efc8cbf4-610b-4825-a1d3-969022e5f292	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	title_closed	false	2024-02-20 10:14:59.801+00
a390589e-fe2a-44b6-a628-d40726698d89	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	description_closed	false	2024-02-20 10:14:59.804+00
81eba4b2-3a11-40c7-959c-98211eace3ca	ca79a23c-efd1-465d-9b7f-a12e35f36c2c	language	English	2024-02-20 10:14:59.807+00
cc114ab5-6917-4c47-9e94-c2b3cd638921	2ab48274-7e14-4e60-980f-4d8e9d011d05	file_name	path2	2024-02-20 10:14:59.819+00
84cfb377-bde1-4f30-afb6-b23c8d876226	2ab48274-7e14-4e60-980f-4d8e9d011d05	file_type	File	2024-02-20 10:14:59.821+00
0c97c1dd-2bc6-4fd1-a8a9-edbae221ce0f	2ab48274-7e14-4e60-980f-4d8e9d011d05	file_size	1024	2024-02-20 10:14:59.83+00
032f9563-2489-4b7f-b91e-7362c9b84d42	2ab48274-7e14-4e60-980f-4d8e9d011d05	rights_copyright	Crown Copyright	2024-02-20 10:14:59.832+00
c5eb0be3-a8ba-4d63-a548-1af9518565d5	2ab48274-7e14-4e60-980f-4d8e9d011d05	legal_status	Public Record(s)	2024-02-20 10:14:59.835+00
32fffe1a-82ff-4166-bbf3-b12c2801bcac	2ab48274-7e14-4e60-980f-4d8e9d011d05	held_by	The National Archives, Kew	2024-02-20 10:14:59.838+00
f9079e5e-e6a3-4ac6-8b94-091bd2e23b2b	2ab48274-7e14-4e60-980f-4d8e9d011d05	date_last_modified	2024-02-07T10:53:04	2024-02-20 10:14:59.842+00
8806b60b-a62b-42d5-82f9-a82df5a7124c	2ab48274-7e14-4e60-980f-4d8e9d011d05	closure_type	Open	2024-02-20 10:14:59.847+00
0e4f0ba0-9339-403c-8396-c65e2996609d	2ab48274-7e14-4e60-980f-4d8e9d011d05	title_closed	false	2024-02-20 10:14:59.851+00
a546090e-e025-4a30-b84d-ba1b79796da7	2ab48274-7e14-4e60-980f-4d8e9d011d05	description_closed	false	2024-02-20 10:14:59.859+00
e08c471b-b5a8-4f98-9ab9-855ccbec0648	2ab48274-7e14-4e60-980f-4d8e9d011d05	language	English	2024-02-20 10:14:59.863+00
c6fd0991-b0a6-4334-b420-af81f87d1294	a226a809-5379-4362-926c-3e6964f8bbae	file_name	original	2024-02-20 10:14:59.881+00
1c05f947-465e-4808-9153-68f7309390d6	a226a809-5379-4362-926c-3e6964f8bbae	file_type	Folder	2024-02-20 10:14:59.884+00
ece05c50-52aa-4e55-94e1-3eed2c141ce3	a226a809-5379-4362-926c-3e6964f8bbae	rights_copyright	Crown Copyright	2024-02-20 10:14:59.886+00
257ee213-8bae-4253-b998-d5deef0e52d6	a226a809-5379-4362-926c-3e6964f8bbae	legal_status	Public Record(s)	2024-02-20 10:14:59.888+00
390db480-de94-4637-b455-0da99de419cc	a226a809-5379-4362-926c-3e6964f8bbae	held_by	The National Archives, Kew	2024-02-20 10:14:59.89+00
5c68e8da-15e5-4bb7-ab4c-506b14a4b396	a226a809-5379-4362-926c-3e6964f8bbae	closure_type	Open	2024-02-20 10:14:59.893+00
47112f51-7ca2-4568-a1a7-5a4d795e2c41	a226a809-5379-4362-926c-3e6964f8bbae	title_closed	false	2024-02-20 10:14:59.895+00
5f6d14fe-bbbd-4f43-a871-2c200c033095	a226a809-5379-4362-926c-3e6964f8bbae	description_closed	false	2024-02-20 10:14:59.897+00
7956f215-b353-4f72-926b-013cd21c571a	a226a809-5379-4362-926c-3e6964f8bbae	language	English	2024-02-20 10:14:59.899+00
6dcec231-e793-44e5-90ac-363ce30538f7	6e03818d-8fe2-4e9d-a378-39532160d7c4	file_name	E2E_tests	2024-02-20 10:14:59.906+00
b7f8d96b-ae6e-4c34-be32-a407c49d388d	6e03818d-8fe2-4e9d-a378-39532160d7c4	file_type	Folder	2024-02-20 10:14:59.908+00
24459535-b432-415a-a2c3-985d4b909f6d	6e03818d-8fe2-4e9d-a378-39532160d7c4	rights_copyright	Crown Copyright	2024-02-20 10:14:59.911+00
9242fc9c-97fa-4ac7-a4ba-7d1e7e2dc3a7	6e03818d-8fe2-4e9d-a378-39532160d7c4	legal_status	Public Record(s)	2024-02-20 10:14:59.914+00
e7ddfc3a-087e-4485-8589-0a4bdf485045	6e03818d-8fe2-4e9d-a378-39532160d7c4	held_by	The National Archives, Kew	2024-02-20 10:14:59.916+00
d01c5222-7601-4ff8-b99b-53e3f054f4dc	6e03818d-8fe2-4e9d-a378-39532160d7c4	closure_type	Open	2024-02-20 10:14:59.92+00
e68fc469-6083-4cca-b119-5a15822edc51	6e03818d-8fe2-4e9d-a378-39532160d7c4	title_closed	false	2024-02-20 10:14:59.925+00
c84fe219-9397-4d02-8101-e8fbc5a87381	6e03818d-8fe2-4e9d-a378-39532160d7c4	description_closed	false	2024-02-20 10:14:59.931+00
c55c8953-c471-4686-a44a-2b19d2307d62	6e03818d-8fe2-4e9d-a378-39532160d7c4	language	English	2024-02-20 10:14:59.934+00
b543d5af-b994-4660-ae91-c7bca1d87420	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	file_name	path0	2024-02-20 10:14:59.939+00
10b6c554-a91a-47eb-8df8-9fa699332006	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	file_type	File	2024-02-20 10:14:59.942+00
ba0041b3-b89b-490a-a01e-6b80eeb57414	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	file_size	1024	2024-02-20 10:14:59.951+00
bab0a1f8-b736-4416-9331-602382d97ccf	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	rights_copyright	Crown Copyright	2024-02-20 10:14:59.954+00
8b07747d-6e5a-4a11-9ce4-f08374ddef71	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	legal_status	Public Record(s)	2024-02-20 10:14:59.957+00
017e4ed7-24f3-4cd2-a3ad-6be6a64ee8d5	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	held_by	The National Archives, Kew	2024-02-20 10:14:59.96+00
b2129a57-0415-42cc-ae61-a7c5c785ab4e	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	date_last_modified	2024-02-07T10:53:04	2024-02-20 10:14:59.962+00
2248f742-cdbb-4d1d-9476-7a275f974ac7	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	closure_type	Open	2024-02-20 10:14:59.966+00
e2b7a928-b83d-46fd-a557-8102fda37428	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	title_closed	false	2024-02-20 10:14:59.971+00
2ac548ae-45c5-40f9-90f8-1b4d9dea4c74	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	description_closed	false	2024-02-20 10:14:59.974+00
12952670-0638-4b7c-aa9c-a7d9dd9f2bdc	859679b7-2e6d-4bc2-8fcb-e3ffb1e40209	language	English	2024-02-20 10:14:59.977+00
a7267378-a77f-46b2-9fc2-88306fd32a61	3bc5628d-9587-49c4-9e94-d200f76d6497	file_name	testfile1	2024-02-20 10:16:26.146+00
779babd4-52e2-4ebd-a1e9-2c6e1f85e422	3bc5628d-9587-49c4-9e94-d200f76d6497	file_type	File	2024-02-20 10:16:26.15+00
8a24b7be-93b9-411c-a279-6ff3979b1c3b	3bc5628d-9587-49c4-9e94-d200f76d6497	file_size	0	2024-02-20 10:16:26.151+00
ecda34c5-c1cc-43dc-812a-a8ca3016c1e3	3bc5628d-9587-49c4-9e94-d200f76d6497	rights_copyright	Crown Copyright	2024-02-20 10:16:26.154+00
8cf7501a-180d-4b8b-93f4-c287c942a440	3bc5628d-9587-49c4-9e94-d200f76d6497	legal_status	Public Record(s)	2024-02-20 10:16:26.155+00
d7f7d0bf-d5ea-4b22-89b4-2a51e4252a17	3bc5628d-9587-49c4-9e94-d200f76d6497	held_by	The National Archives, Kew	2024-02-20 10:16:26.163+00
a65245b5-3f1b-4b3b-b8a6-ed0b0b438b5c	3bc5628d-9587-49c4-9e94-d200f76d6497	date_last_modified	2024-02-07T10:51:15	2024-02-20 10:16:26.166+00
a0c1d7e0-f5d9-41c3-b22d-b7c99cf3bc7f	3bc5628d-9587-49c4-9e94-d200f76d6497	closure_type	Open	2024-02-20 10:16:26.168+00
d7951a8b-82fc-4dc9-be96-726ac16d7841	3bc5628d-9587-49c4-9e94-d200f76d6497	title_closed	false	2024-02-20 10:16:26.169+00
a4c2466d-e3c4-4c26-a339-ad46847bbe09	3bc5628d-9587-49c4-9e94-d200f76d6497	description_closed	false	2024-02-20 10:16:26.171+00
4c65686d-1beb-48a2-b3c6-e71cf99b963e	3bc5628d-9587-49c4-9e94-d200f76d6497	language	English	2024-02-20 10:16:26.172+00
f3e1e267-a03d-44a1-8904-518ebe6692a5	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	file_name	testfile1	2024-02-20 10:33:39.406+00
38bb1308-8dfe-42ae-b8c5-bea586d04ae4	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	file_type	File	2024-02-20 10:33:39.409+00
a45d02a1-4753-458e-8765-8415ed4ce0e6	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	file_size	0	2024-02-20 10:33:39.412+00
496015c7-5d5b-4946-8756-3c35d1498575	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	rights_copyright	Crown Copyright	2024-02-20 10:33:39.415+00
9c23ec16-2b53-4678-beb7-45fd2ccbf12f	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	legal_status	Public Record(s)	2024-02-20 10:33:39.417+00
1d2e100a-9c76-4963-a4e0-ba3c27cef08f	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	held_by	The National Archives, Kew	2024-02-20 10:33:39.421+00
b6fd2f58-7649-4320-b29c-9a75a5ce5da4	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	date_last_modified	2023-07-28T09:30:46	2024-02-20 10:33:39.428+00
6ea76d01-8fe9-4762-a485-6176dcca95d0	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	closure_type	Open	2024-02-20 10:33:39.433+00
a8cc7c9e-cd90-46e6-8206-bede7a8bffe6	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	title_closed	false	2024-02-20 10:33:39.435+00
9346f29a-f818-4499-85d6-35a55fe5ed3e	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	description_closed	false	2024-02-20 10:33:39.438+00
b2a67e10-5bab-4753-9013-eff29133dd41	7ce919c0-9f2b-4133-b41f-f85bdecc6a52	language	English	2024-02-20 10:33:39.44+00
e8ce0c09-9439-44cf-889f-e7c02f8a4c9f	ced32116-5b57-4a45-83d0-7a372a6ab333	file_name	closed_file_R - Copy.pdf	2024-02-20 10:34:51.456+00
ecbc15f0-9921-4173-b45c-d694b1228eba	ced32116-5b57-4a45-83d0-7a372a6ab333	file_type	File	2024-02-20 10:34:51.459+00
80390075-8f9a-49ad-8508-676c99753fed	ced32116-5b57-4a45-83d0-7a372a6ab333	file_size	6466	2024-02-20 10:34:51.461+00
75992140-ce4d-4425-8f5b-c7723db04250	ced32116-5b57-4a45-83d0-7a372a6ab333	rights_copyright	Crown Copyright	2024-02-20 10:34:51.463+00
436df0e1-1c85-4be1-b256-143eae4a497c	ced32116-5b57-4a45-83d0-7a372a6ab333	legal_status	Public Record(s)	2024-02-20 10:34:51.465+00
e457fdca-d4b6-4f22-a4c6-b375debea3ba	ced32116-5b57-4a45-83d0-7a372a6ab333	held_by	The National Archives, Kew	2024-02-20 10:34:51.467+00
1d095853-7a09-4d85-ac38-839d407f70ba	ced32116-5b57-4a45-83d0-7a372a6ab333	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.468+00
d604a224-ddad-4fbf-887c-70c89da850df	ced32116-5b57-4a45-83d0-7a372a6ab333	closure_type	Open	2024-02-20 10:34:51.47+00
2810bee3-a1a7-4444-912d-739456ab4fb8	ced32116-5b57-4a45-83d0-7a372a6ab333	title_closed	false	2024-02-20 10:34:51.471+00
6c939eab-b962-4cce-a327-de48fd023b80	ced32116-5b57-4a45-83d0-7a372a6ab333	description_closed	false	2024-02-20 10:34:51.473+00
6d70cf57-ba63-48d3-a9ef-faa42c1495ef	ced32116-5b57-4a45-83d0-7a372a6ab333	language	English	2024-02-20 10:34:51.474+00
b52f106a-01b5-4f4d-8aa8-a00642fc0f9c	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	file_name	mismatch	2024-02-20 10:34:51.482+00
745a0e56-df41-4df9-97a8-d940fd92fb25	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	file_type	Folder	2024-02-20 10:34:51.484+00
a5d6a315-75ca-4e97-b7ad-756a9778a45c	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	rights_copyright	Crown Copyright	2024-02-20 10:34:51.485+00
c7698c1b-bd5c-42a7-84ac-71cc56f231ce	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	legal_status	Public Record(s)	2024-02-20 10:34:51.487+00
55bc3375-9033-4ad7-bc77-a8f64c7b60e6	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	held_by	The National Archives, Kew	2024-02-20 10:34:51.488+00
128a6904-9836-44d6-89e8-cb40ffe838e9	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	closure_type	Open	2024-02-20 10:34:51.491+00
c7eff6b3-dd72-425d-a7f4-eae376519f2d	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	title_closed	false	2024-02-20 10:34:51.492+00
fe2f9dc8-2112-40b0-8f86-d2c4093f313d	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	description_closed	false	2024-02-20 10:34:51.494+00
27d84489-c6ad-4775-be1e-bd0f0aba46de	9819c4ee-93e0-4441-a0e8-4db1cdd85a6b	language	English	2024-02-20 10:34:51.495+00
71e416c2-5cad-4da9-b4ed-c7a0bb77f546	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	file_name	file-b2.txt	2024-02-20 10:34:51.5+00
8e4140aa-c8ff-4c38-99a0-7e62e40fc9bb	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	file_type	File	2024-02-20 10:34:51.506+00
b0f2cb58-34d7-4fed-ba9c-eb59a792f2f1	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	file_size	45	2024-02-20 10:34:51.508+00
caeeb23d-66ea-4a6f-949f-2522f377f2e2	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	rights_copyright	Crown Copyright	2024-02-20 10:34:51.51+00
8e34fb53-7bd3-48ca-bf31-03f39a548f83	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	legal_status	Public Record(s)	2024-02-20 10:34:51.512+00
47cfbfaf-fe6f-4719-8fb1-8feefad6a95b	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	held_by	The National Archives, Kew	2024-02-20 10:34:51.513+00
564e79d0-fe0c-41ee-9323-956cca759edc	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.515+00
7a17acb4-d5b5-43a3-9cc6-be82240055ff	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	closure_type	Open	2024-02-20 10:34:51.516+00
f1264905-0bbb-488e-b15e-0f706b37aab5	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	title_closed	false	2024-02-20 10:34:51.524+00
4afe02dc-e52b-4dc1-aba2-98d0608cc856	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	description_closed	false	2024-02-20 10:34:51.526+00
51378423-3814-4a9a-a603-7a98d75f0e06	3cb3163a-af1f-4aae-b4f4-b01e01f64ad3	language	English	2024-02-20 10:34:51.528+00
8e1691bd-6132-44b2-8725-a66e79962662	ed1b679e-805d-403b-b6cd-8fd073a0e832	file_name	content	2024-02-20 10:34:51.536+00
64f65f67-a485-4225-993d-d53b632b447f	ed1b679e-805d-403b-b6cd-8fd073a0e832	file_type	Folder	2024-02-20 10:34:51.538+00
eb36be6b-4290-4a8e-8389-827229986456	ed1b679e-805d-403b-b6cd-8fd073a0e832	rights_copyright	Crown Copyright	2024-02-20 10:34:51.54+00
857629f9-2151-4f8c-9051-835cfd2553ee	ed1b679e-805d-403b-b6cd-8fd073a0e832	legal_status	Public Record(s)	2024-02-20 10:34:51.541+00
99cf95b7-d7cc-462d-bf69-19ba74eca5a8	ed1b679e-805d-403b-b6cd-8fd073a0e832	held_by	The National Archives, Kew	2024-02-20 10:34:51.543+00
61cedc2e-4524-4f17-a952-b2fba29962d7	ed1b679e-805d-403b-b6cd-8fd073a0e832	closure_type	Open	2024-02-20 10:34:51.544+00
f685f436-f9a8-4097-9f97-417b4d7d84a1	ed1b679e-805d-403b-b6cd-8fd073a0e832	title_closed	false	2024-02-20 10:34:51.545+00
78a42b4a-d2c3-4228-9076-98e8f362d37e	ed1b679e-805d-403b-b6cd-8fd073a0e832	description_closed	false	2024-02-20 10:34:51.546+00
209173af-88f8-4094-95f1-7d31e11850e7	ed1b679e-805d-403b-b6cd-8fd073a0e832	language	English	2024-02-20 10:34:51.548+00
c0b4a2eb-5d4e-4b4e-88ca-3067085f21d8	0a31ffd6-f530-4464-9783-07e5717f1ab4	file_name	file-b1.txt	2024-02-20 10:34:51.551+00
081324d8-aedd-4d0a-8f94-f0c69fb8e16d	0a31ffd6-f530-4464-9783-07e5717f1ab4	file_type	File	2024-02-20 10:34:51.556+00
7ad6ea7f-c36a-4cec-a497-7e4db1da96ed	0a31ffd6-f530-4464-9783-07e5717f1ab4	file_size	45	2024-02-20 10:34:51.558+00
789c6f7a-3c59-4088-bbe9-fcde59b39099	0a31ffd6-f530-4464-9783-07e5717f1ab4	rights_copyright	Crown Copyright	2024-02-20 10:34:51.559+00
8ac748cd-545c-4348-a483-abfa017c4743	0a31ffd6-f530-4464-9783-07e5717f1ab4	legal_status	Public Record(s)	2024-02-20 10:34:51.561+00
498968bd-4db9-45ac-92de-14ad9ed2993b	0a31ffd6-f530-4464-9783-07e5717f1ab4	held_by	The National Archives, Kew	2024-02-20 10:34:51.564+00
b0a17c02-91e1-4992-97b9-28b23cbdc00d	0a31ffd6-f530-4464-9783-07e5717f1ab4	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.566+00
ef31f73b-7dca-4e5d-a542-35c3143bc881	0a31ffd6-f530-4464-9783-07e5717f1ab4	closure_type	Open	2024-02-20 10:34:51.57+00
334f141f-b709-4080-ab52-c6fda1d86e23	0a31ffd6-f530-4464-9783-07e5717f1ab4	title_closed	false	2024-02-20 10:34:51.573+00
5f6c5280-1cb4-4cb6-8386-8a53f128ae5b	0a31ffd6-f530-4464-9783-07e5717f1ab4	description_closed	false	2024-02-20 10:34:51.575+00
ab58f606-b2d9-426a-98d1-6ae266394fea	0a31ffd6-f530-4464-9783-07e5717f1ab4	language	English	2024-02-20 10:34:51.576+00
0cee3b3a-24a8-4442-a07f-e84c9f03f69e	57824039-5538-4169-9136-1a44b7222776	file_name	folder-a	2024-02-20 10:34:51.589+00
cd0aa433-3063-4a13-ae05-193e1c40d5c4	57824039-5538-4169-9136-1a44b7222776	file_type	Folder	2024-02-20 10:34:51.59+00
fa6cbaca-8e9a-4f32-af37-4ec91eafff94	57824039-5538-4169-9136-1a44b7222776	rights_copyright	Crown Copyright	2024-02-20 10:34:51.596+00
63a9636c-8714-4647-99be-42f645ba7291	57824039-5538-4169-9136-1a44b7222776	legal_status	Public Record(s)	2024-02-20 10:34:51.598+00
ac2cba23-4e7d-4b25-aa65-3ef0a98fc998	57824039-5538-4169-9136-1a44b7222776	held_by	The National Archives, Kew	2024-02-20 10:34:51.6+00
dc651dd9-d80a-4357-b95e-41b75cbe5f9e	57824039-5538-4169-9136-1a44b7222776	closure_type	Open	2024-02-20 10:34:51.602+00
67f85ad5-cd1a-4411-8796-2d725ad1ba28	57824039-5538-4169-9136-1a44b7222776	title_closed	false	2024-02-20 10:34:51.604+00
74345bee-cf2f-4c54-9b30-e44419396207	57824039-5538-4169-9136-1a44b7222776	description_closed	false	2024-02-20 10:34:51.609+00
6098f059-9200-4010-afa6-e777ad352b52	57824039-5538-4169-9136-1a44b7222776	language	English	2024-02-20 10:34:51.612+00
7b8cb640-8e10-4b3e-aeac-e25b1abbaa2f	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	file_name	closed_file.txt	2024-02-20 10:34:51.615+00
fe1cf559-e892-4454-83d9-ea985aad58af	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	file_type	File	2024-02-20 10:34:51.619+00
01ced285-3ead-46d3-b6d6-9d3e0755c86c	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	file_size	4	2024-02-20 10:34:51.62+00
0dfd4818-4d4e-4d86-977b-289db5a1af2a	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	rights_copyright	Crown Copyright	2024-02-20 10:34:51.622+00
ee090a2b-49a7-47c5-adbc-4b3f7a3952a2	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	legal_status	Public Record(s)	2024-02-20 10:34:51.623+00
cbe2c188-5f91-42b8-ba40-bef2e62c18f2	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	held_by	The National Archives, Kew	2024-02-20 10:34:51.625+00
9d736a4f-6c50-4a46-a9f4-39ace23ceea1	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.626+00
cc2d5c48-b0c1-4e8f-b075-82f010ffce5e	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	closure_type	Open	2024-02-20 10:34:51.628+00
09298c26-1660-4074-ba1a-e3612b78883e	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	title_closed	false	2024-02-20 10:34:51.633+00
9bc6988c-f2b1-4121-ba99-64b099cc3579	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	description_closed	false	2024-02-20 10:34:51.634+00
6b6e60c4-f3ce-4017-a330-c31cbf276d64	ea8a6ad6-5362-4346-a86d-22a52b9fc0c5	language	English	2024-02-20 10:34:51.636+00
a50ebfdc-95c1-4e47-bfef-6b314a2c2d53	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	file_name	closed_file_R.pdf	2024-02-20 10:34:51.641+00
f8fc038d-8690-4175-ada8-69dd7073fa29	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	file_type	File	2024-02-20 10:34:51.643+00
658db660-460a-4ae7-83d3-d35a07235ad7	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	file_size	6466	2024-02-20 10:34:51.644+00
ccc7e00b-9e54-4dba-ba0c-b283a7df9eef	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	rights_copyright	Crown Copyright	2024-02-20 10:34:51.645+00
93f3e193-3683-43ee-8b9a-090a8d69f67d	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	legal_status	Public Record(s)	2024-02-20 10:34:51.647+00
98de83d0-c6ea-41a2-b159-f5e66653e5ed	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	held_by	The National Archives, Kew	2024-02-20 10:34:51.648+00
78cda47e-5853-42b8-8d07-cf6462d8ece7	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.649+00
91e40b20-1d93-414f-aae7-29d66bbcf4a9	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	closure_type	Open	2024-02-20 10:34:51.65+00
84041653-c83b-4a94-8188-55e345f83809	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	title_closed	false	2024-02-20 10:34:51.651+00
42036522-58d5-4a7b-b3fc-92ff232029fd	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	description_closed	false	2024-02-20 10:34:51.653+00
8f899ec9-e9d8-47da-87c4-8926f8363151	cec194d0-2d90-4e70-b7ae-f7d2c3ff41d1	language	English	2024-02-20 10:34:51.654+00
e0f5e187-2057-4e56-b56a-094a23dae26d	6cba3e70-d635-42fa-9d4a-607047fd290c	file_name	file-a1.txt	2024-02-20 10:34:51.659+00
23e5c3cf-5631-431d-9622-2c01c1a6e30e	6cba3e70-d635-42fa-9d4a-607047fd290c	file_type	File	2024-02-20 10:34:51.661+00
1a165f9d-43f5-4be6-ae67-f22ea2c654f8	6cba3e70-d635-42fa-9d4a-607047fd290c	file_size	46	2024-02-20 10:34:51.663+00
0e0000c2-c272-407d-8557-f7a92db6ac04	6cba3e70-d635-42fa-9d4a-607047fd290c	rights_copyright	Crown Copyright	2024-02-20 10:34:51.665+00
d300d93b-ddde-4405-9526-1c8f391fcdad	6cba3e70-d635-42fa-9d4a-607047fd290c	legal_status	Public Record(s)	2024-02-20 10:34:51.666+00
f42de4cb-96ec-48f5-9195-03d7b55c1189	6cba3e70-d635-42fa-9d4a-607047fd290c	held_by	The National Archives, Kew	2024-02-20 10:34:51.667+00
8244508c-8f29-4b81-9a9f-1e4695c19465	6cba3e70-d635-42fa-9d4a-607047fd290c	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.668+00
d2e40929-97aa-4af4-97e2-e7c86af982a3	6cba3e70-d635-42fa-9d4a-607047fd290c	closure_type	Open	2024-02-20 10:34:51.669+00
355ba422-5f31-4748-96cd-6ce6e01b8511	6cba3e70-d635-42fa-9d4a-607047fd290c	title_closed	false	2024-02-20 10:34:51.671+00
ede31131-9b79-47c4-b991-c4e80c5e10c2	6cba3e70-d635-42fa-9d4a-607047fd290c	description_closed	false	2024-02-20 10:34:51.672+00
161c831e-83af-420c-8b2e-49f63a754a05	6cba3e70-d635-42fa-9d4a-607047fd290c	language	English	2024-02-20 10:34:51.673+00
73a55b72-61d3-49bb-9ae5-ba3d39e38135	60b50686-1689-4aeb-9687-435e76a3b255	file_name	folder-b	2024-02-20 10:34:51.678+00
0b5c0135-9b4d-433a-9937-164b2c0dc5c4	60b50686-1689-4aeb-9687-435e76a3b255	file_type	Folder	2024-02-20 10:34:51.679+00
44663a71-bec4-43ff-83e9-cc03e598299b	60b50686-1689-4aeb-9687-435e76a3b255	rights_copyright	Crown Copyright	2024-02-20 10:34:51.68+00
796c0e3c-c2f1-4b40-8028-3a34d6a9c82c	60b50686-1689-4aeb-9687-435e76a3b255	legal_status	Public Record(s)	2024-02-20 10:34:51.681+00
22e0653d-d5e4-417f-b160-7aabc5ff7571	60b50686-1689-4aeb-9687-435e76a3b255	held_by	The National Archives, Kew	2024-02-20 10:34:51.682+00
1991bdd8-3a8e-4365-91e0-12a15810557f	60b50686-1689-4aeb-9687-435e76a3b255	closure_type	Open	2024-02-20 10:34:51.684+00
49324773-651a-4f49-b367-6687624bb9d0	60b50686-1689-4aeb-9687-435e76a3b255	title_closed	false	2024-02-20 10:34:51.685+00
73cb5b91-7ede-42ec-92d9-e28f7ba89da3	60b50686-1689-4aeb-9687-435e76a3b255	description_closed	false	2024-02-20 10:34:51.686+00
412d620d-f5db-4538-b4a1-402b1e64f9cb	60b50686-1689-4aeb-9687-435e76a3b255	language	English	2024-02-20 10:34:51.689+00
12df0ed2-31ef-4a31-b4f9-835a7c6457e8	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	file_name	redacted	2024-02-20 10:34:51.691+00
846cfc5d-ab77-4bec-8aaa-65a0c0984883	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	file_type	Folder	2024-02-20 10:34:51.692+00
147e8ee3-3e81-4d11-ad7c-7714f8da3453	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	rights_copyright	Crown Copyright	2024-02-20 10:34:51.693+00
4ca3408b-689b-407d-80df-3ca745ee3b94	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	legal_status	Public Record(s)	2024-02-20 10:34:51.694+00
2b2dd2dd-46ba-4ff5-b0b0-0f4f08ef568c	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	held_by	The National Archives, Kew	2024-02-20 10:34:51.695+00
cb5cbfd7-1434-4ef7-aca5-ab17248c1702	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	closure_type	Open	2024-02-20 10:34:51.697+00
91626729-7465-4c9b-a639-5175a5f9c9f1	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	title_closed	false	2024-02-20 10:34:51.698+00
88d42ae9-2312-46fb-a678-48f9681e3ebf	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	description_closed	false	2024-02-20 10:34:51.699+00
176e47e0-e14f-4671-a132-1b6b8eec2601	63bbfa85-5799-4612-bf3f-0bb9dd3cb067	language	English	2024-02-20 10:34:51.7+00
65c3680f-ad91-4b6b-bb2e-dcbd7393cc82	b2279f23-8d07-4fa5-b0af-94ec4123e21e	file_name	mismatch.docx	2024-02-20 10:34:51.705+00
93081399-2ba5-445a-b9f2-3a8424a0001e	b2279f23-8d07-4fa5-b0af-94ec4123e21e	file_type	File	2024-02-20 10:34:51.707+00
f4a54d26-95af-4afd-ad4f-78278763ab97	b2279f23-8d07-4fa5-b0af-94ec4123e21e	file_size	6466	2024-02-20 10:34:51.708+00
def99ad5-a9a9-408b-8f2a-b60242f0196c	b2279f23-8d07-4fa5-b0af-94ec4123e21e	rights_copyright	Crown Copyright	2024-02-20 10:34:51.709+00
6ae11e85-2590-4c9e-9a97-703d62858f6b	b2279f23-8d07-4fa5-b0af-94ec4123e21e	legal_status	Public Record(s)	2024-02-20 10:34:51.71+00
f51f3354-9e55-4c12-a75d-54b2def90032	b2279f23-8d07-4fa5-b0af-94ec4123e21e	held_by	The National Archives, Kew	2024-02-20 10:34:51.712+00
0e6852a7-cea4-40fa-aac7-6de56eb8b429	b2279f23-8d07-4fa5-b0af-94ec4123e21e	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.714+00
dc112549-53c4-4d24-bcde-4f05603748c3	b2279f23-8d07-4fa5-b0af-94ec4123e21e	closure_type	Open	2024-02-20 10:34:51.715+00
afb3cf72-97a8-415c-b565-7198e38064d3	b2279f23-8d07-4fa5-b0af-94ec4123e21e	title_closed	false	2024-02-20 10:34:51.716+00
247a74ec-8dfe-4f0f-8b5e-008cdca5c6ec	b2279f23-8d07-4fa5-b0af-94ec4123e21e	description_closed	false	2024-02-20 10:34:51.717+00
a0f724e5-a10f-4157-98f5-3c7aad7d2387	b2279f23-8d07-4fa5-b0af-94ec4123e21e	language	English	2024-02-20 10:34:51.718+00
3d506151-ae02-4396-91e7-9644cf51d7ab	8211c175-5331-4fba-a14b-24db8fdaf6a1	file_name	file-a2.txt	2024-02-20 10:34:51.725+00
f920ec7a-1924-444b-8474-8f4fe170a596	8211c175-5331-4fba-a14b-24db8fdaf6a1	file_type	File	2024-02-20 10:34:51.728+00
11b2e584-d63c-4651-af46-ac95e29b7014	8211c175-5331-4fba-a14b-24db8fdaf6a1	file_size	45	2024-02-20 10:34:51.729+00
037b092c-f1ef-435c-9e59-8512b487936d	8211c175-5331-4fba-a14b-24db8fdaf6a1	rights_copyright	Crown Copyright	2024-02-20 10:34:51.731+00
b5dc6dba-fa8d-44ce-9057-01c7bf3b9814	8211c175-5331-4fba-a14b-24db8fdaf6a1	legal_status	Public Record(s)	2024-02-20 10:34:51.732+00
743f2961-563b-499b-b30f-be0beb952985	8211c175-5331-4fba-a14b-24db8fdaf6a1	held_by	The National Archives, Kew	2024-02-20 10:34:51.733+00
7b47bc20-416b-44d3-9539-9041f85a84f8	8211c175-5331-4fba-a14b-24db8fdaf6a1	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.734+00
b37ca5e8-0dba-4881-9b33-9e7221f5bbf4	8211c175-5331-4fba-a14b-24db8fdaf6a1	closure_type	Open	2024-02-20 10:34:51.735+00
d1b56210-aa32-4175-8988-e79fdad4e193	8211c175-5331-4fba-a14b-24db8fdaf6a1	title_closed	false	2024-02-20 10:34:51.736+00
7799ec61-b679-41af-801d-0c4d4c54436e	8211c175-5331-4fba-a14b-24db8fdaf6a1	description_closed	false	2024-02-20 10:34:51.738+00
049afb18-c538-46d4-a618-a4a1a043e8f3	8211c175-5331-4fba-a14b-24db8fdaf6a1	language	English	2024-02-20 10:34:51.739+00
9ed7f0cb-8921-4fd6-823a-fccc9d79f3c2	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	file_name	file-a1,.txt	2024-02-20 10:34:51.743+00
5dee1d43-7ea1-4a58-9cb6-744d8e82cd3d	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	file_type	File	2024-02-20 10:34:51.744+00
d6d137b3-9e10-4a13-a8a2-9bde6f4702d8	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	file_size	46	2024-02-20 10:34:51.746+00
55c3aaa4-a652-4180-9dd4-cb46ef8f41cc	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	rights_copyright	Crown Copyright	2024-02-20 10:34:51.748+00
66ddf7ba-a44b-4091-9552-339e4c5d98eb	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	legal_status	Public Record(s)	2024-02-20 10:34:51.755+00
a2910148-356e-4d4b-b7a7-db474de31a19	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	held_by	The National Archives, Kew	2024-02-20 10:34:51.757+00
de0856e7-132c-4757-bd75-9b5764048115	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	date_last_modified	2023-11-22T00:00:00	2024-02-20 10:34:51.758+00
e8c117c7-4bd6-4d15-ad64-30086bbe83c8	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	closure_type	Open	2024-02-20 10:34:51.759+00
ce1e7133-e377-4320-8439-5afa0d686a96	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	title_closed	false	2024-02-20 10:34:51.761+00
edec8999-a5bb-4d24-92f4-a002380a4912	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	description_closed	false	2024-02-20 10:34:51.763+00
d8679737-3278-4420-bfa4-9dabbfa88345	b43f2580-d1dd-4a15-ab9d-cddeb9cb56ec	language	English	2024-02-20 10:34:51.764+00
76b937fe-ac25-48fc-8494-98378a57caaa	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	file_name	testfile1	2024-02-20 16:23:56.177+00
efe75d00-c0bd-4984-9269-083f241bf868	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	file_type	File	2024-02-20 16:23:56.182+00
eb168a19-b8d4-46bc-9bf4-7631e2a5792f	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	file_size	0	2024-02-20 16:23:56.185+00
adc410bc-5866-4411-855c-59d55e817c3f	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	rights_copyright	Crown Copyright	2024-02-20 16:23:56.188+00
dd0c73a8-b1b5-4375-8bce-2c8cd068beea	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	legal_status	Public Record(s)	2024-02-20 16:23:56.191+00
6fb733e3-7df1-46b5-8788-2aa47b0883f8	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	held_by	The National Archives, Kew	2024-02-20 16:23:56.194+00
ecd2900c-0fbe-4fcb-8ab5-9f35977359d1	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	date_last_modified	2024-02-19T08:31:36	2024-02-20 16:23:56.197+00
e8f4233d-559b-4bf6-8b2c-08e29030df78	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	closure_type	Open	2024-02-20 16:23:56.201+00
060cfcd0-564b-4cf7-824d-2417e8e790ef	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	title_closed	false	2024-02-20 16:23:56.204+00
0a585144-259d-40da-b36e-b756c4c62f04	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	description_closed	false	2024-02-20 16:23:56.206+00
0adb6ff1-7cc3-4858-a885-a4521f9089f8	0de5cb7e-baf6-4f9c-8a52-450dd117ae83	language	English	2024-02-20 16:23:56.209+00
d8a511e9-ce6c-4149-a6bb-bdac14a7d3d9	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	file_name	closed_file.txt	2024-02-20 16:44:57.389+00
3fd689ba-3845-474c-8ec6-ba30247dca4e	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	file_type	File	2024-02-20 16:44:57.393+00
8e92086a-bd98-4f4d-a5b2-5ecc4b6297e4	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	file_size	4	2024-02-20 16:44:57.397+00
ac68f225-b1fc-491d-88db-adafa28b7c47	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	rights_copyright	Crown Copyright	2024-02-20 16:44:57.4+00
3ada9321-9c65-46f2-bd9d-ab67eeb3afb8	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	legal_status	Public Record(s)	2024-02-20 16:44:57.403+00
3eda5f4a-f464-497d-8cf5-c4bf0e30b6d7	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	held_by	The National Archives, Kew	2024-02-20 16:44:57.407+00
a0528595-ea65-4869-98d0-0dea0866b0e3	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	date_last_modified	2023-10-17T00:00:00	2024-02-20 16:44:57.411+00
62634411-626e-4028-8dbd-f98cf1163399	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	closure_type	Closed	2024-02-20 16:44:57.414+00
1888aeb3-d44c-47f8-855c-156ab8cfa245	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	opening_date	2048-10-18T00:00:00	2024-02-20 16:44:57.417+00
87d1013e-8c21-474f-9622-ac7a16f9bf52	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	closure_start_date	2023-10-17T00:00:00	2024-02-20 16:44:57.419+00
3ff001ac-5591-4266-97e9-f1a036b4b18c	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	closure_period	25	2024-02-20 16:44:57.422+00
adbbfd2b-a7d2-4541-ab0c-d00e2be9ea14	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	foi_exemption_code	40(2)	2024-02-20 16:44:57.426+00
964f9fde-3407-46f5-b0e3-1ede2d17f259	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	foi_exemption_asserted	2023-10-18T00:00:00	2024-02-20 16:44:57.429+00
4f31c94c-2de6-4a3b-913d-c3cebcbbb35f	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	title_closed	true	2024-02-20 16:44:57.433+00
51364bde-fc69-4ec7-af97-0b8c93f47296	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	title_alternate	redacted_file	2024-02-20 16:44:57.436+00
eb7072a0-9752-4b12-8726-f8b40e4aa96a	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	description_closed	false	2024-02-20 16:44:57.439+00
d6e86399-297b-4e47-ab7c-aadb7d887324	405ea5a6-b71d-4ecd-be3c-43062af8e1e6	language	English	2024-02-20 16:44:57.441+00
4e6b2046-48c2-44b0-b1dd-a071edc4f87f	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	file_name	closed_file_R.pdf	2024-02-20 16:44:57.456+00
a2cd7048-8280-4d75-9ae6-576b9bf79b79	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	file_type	File	2024-02-20 16:44:57.459+00
4784f505-d13d-43ef-b0aa-796c020df7c3	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	file_size	6466	2024-02-20 16:44:57.461+00
d46d0fbc-3db4-4150-b6a1-2d5970777582	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	rights_copyright	Crown Copyright	2024-02-20 16:44:57.464+00
07d82c1e-6d04-4351-ac8b-09ce44e468f6	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	legal_status	Public Record(s)	2024-02-20 16:44:57.467+00
921f2244-8934-43ed-a2e2-bd63fc1b93c9	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	held_by	The National Archives, Kew	2024-02-20 16:44:57.47+00
184c9832-b03c-4f0f-9faf-d1ba1fff0ad0	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	date_last_modified	2023-10-18T08:40:37	2024-02-20 16:44:57.473+00
cd0f4b7e-3262-4d98-a868-2dc0f6bf3077	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	closure_type	Open	2024-02-20 16:44:57.475+00
ce40967b-e9dc-48a4-9ea5-5ade7bde6026	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	title_closed	false	2024-02-20 16:44:57.485+00
ebfa1265-e1d7-4813-be29-407e63ac8191	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	description_closed	false	2024-02-20 16:44:57.488+00
77b97cbd-afa8-4e45-8c67-06f1c4e141b9	cc3a458b-123d-4b01-b7e5-787a05dfd7a7	language	English	2024-02-20 16:44:57.491+00
76c6919e-0d0d-4a80-8fbb-9331e1dfdf0a	8ecc93c8-dc96-4419-aeba-f79c84298cc8	file_name	file-a1.txt	2024-02-20 16:44:57.503+00
812dddb4-e347-42f6-8d8a-70a07c786c6a	8ecc93c8-dc96-4419-aeba-f79c84298cc8	file_type	File	2024-02-20 16:44:57.506+00
ff0ee35b-53d0-4a39-a124-526871c7f309	8ecc93c8-dc96-4419-aeba-f79c84298cc8	file_size	46	2024-02-20 16:44:57.508+00
745df4a2-5294-419d-880c-fcdbebf37616	8ecc93c8-dc96-4419-aeba-f79c84298cc8	rights_copyright	Crown Copyright	2024-02-20 16:44:57.512+00
334a0c5b-9b1c-4645-829a-2bc52f4a294f	8ecc93c8-dc96-4419-aeba-f79c84298cc8	legal_status	Public Record(s)	2024-02-20 16:44:57.514+00
1bda8895-1b63-483b-8f6c-5369c1f6d9f9	8ecc93c8-dc96-4419-aeba-f79c84298cc8	held_by	The National Archives, Kew	2024-02-20 16:44:57.518+00
15dceff4-d812-40b6-a011-ff7355bfb893	8ecc93c8-dc96-4419-aeba-f79c84298cc8	date_last_modified	2023-10-17T00:00:00	2024-02-20 16:44:57.52+00
0c11658f-9cbc-4022-8c3b-8533772ae3c6	8ecc93c8-dc96-4419-aeba-f79c84298cc8	closure_type	Open	2024-02-20 16:44:57.523+00
7a4bb85b-5ada-4cd6-875d-7018ad38dfa4	8ecc93c8-dc96-4419-aeba-f79c84298cc8	title_closed	false	2024-02-20 16:44:57.526+00
562e9143-1bad-4174-a940-27da023030f5	8ecc93c8-dc96-4419-aeba-f79c84298cc8	description_closed	false	2024-02-20 16:44:57.528+00
b244099a-5094-4782-8ebc-55a2e247f8a7	8ecc93c8-dc96-4419-aeba-f79c84298cc8	language	English	2024-02-20 16:44:57.531+00
9ad35fef-7fc7-4889-83f9-343f1fcb6b28	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	file_name	file-b1.txt	2024-02-20 16:44:57.542+00
60fdb254-5317-46cf-8a15-b91b60500b98	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	file_type	File	2024-02-20 16:44:57.544+00
c0050eb8-2dec-4691-bf7d-2cf71a74222b	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	file_size	45	2024-02-20 16:44:57.547+00
93a73e05-127c-4fd5-a3dc-9372fe332ce7	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	rights_copyright	Crown Copyright	2024-02-20 16:44:57.55+00
4b9d7af5-202e-4f3a-b68f-5aa34ab79dd3	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	legal_status	Public Record(s)	2024-02-20 16:44:57.552+00
0b5b98b1-074a-4d90-95a6-8956cbf026b6	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	held_by	The National Archives, Kew	2024-02-20 16:44:57.555+00
a659a716-4320-410b-a308-a6471b1f3f42	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	date_last_modified	2023-10-17T00:00:00	2024-02-20 16:44:57.56+00
ba267aab-931b-45c5-b9af-976776dfdee9	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	closure_type	Open	2024-02-20 16:44:57.563+00
7e44baef-5306-4896-b872-6bb32fd828ad	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	title_closed	false	2024-02-20 16:44:57.569+00
0f77c34d-3726-4def-802b-d34e50ca7efd	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	description_closed	false	2024-02-20 16:44:57.572+00
4b96082f-ba14-4b3c-be41-991ab8826375	f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	language	English	2024-02-20 16:44:57.575+00
f9f309e2-609a-476d-a3e0-e61d1f4ebb5f	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	file_name	file-b2.txt	2024-02-20 16:44:57.587+00
0ccd7ec4-24bf-42ea-b2ba-b4b87cd817af	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	file_type	File	2024-02-20 16:44:57.591+00
8e8dd4eb-f74a-4470-a0c8-e2a1abce2f2e	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	file_size	45	2024-02-20 16:44:57.594+00
f8c6a7c2-d347-4cfa-b1f7-abafaee6670c	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	rights_copyright	Crown Copyright	2024-02-20 16:44:57.596+00
63ef137b-72e5-4202-8289-b8a29bf69e0a	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	legal_status	Public Record(s)	2024-02-20 16:44:57.599+00
aee07a4b-3c8d-4eed-99d2-c3829c617ea9	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	held_by	The National Archives, Kew	2024-02-20 16:44:57.601+00
60b1918d-c367-44dc-a829-0647a99b5f6a	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	date_last_modified	2023-10-17T00:00:00	2024-02-20 16:44:57.604+00
68a8811b-5e71-4c3a-90ee-74f4fd4c49a4	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	closure_type	Open	2024-02-20 16:44:57.606+00
eeb8ae37-b7fb-40d1-b500-dbb419006406	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	title_closed	false	2024-02-20 16:44:57.608+00
93ce2713-40d0-49c3-b416-191c4ce4639c	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	description_closed	false	2024-02-20 16:44:57.615+00
7c35b59e-de98-438b-ba1a-018401365aac	db7455e6-3b09-49c4-89c5-19ad2ce52aa5	language	English	2024-02-20 16:44:57.618+00
ecb2fd07-0d7c-4f9d-bc27-65da79ceae8c	a3e85444-fd76-4b51-8d91-5047821c7b61	file_name	folder-b	2024-02-20 16:44:57.631+00
8ac6802d-3160-41a0-bcd6-fb8c4b646be0	a3e85444-fd76-4b51-8d91-5047821c7b61	file_type	Folder	2024-02-20 16:44:57.633+00
b5dafc20-3598-43e7-a345-57b38f6f91ac	a3e85444-fd76-4b51-8d91-5047821c7b61	rights_copyright	Crown Copyright	2024-02-20 16:44:57.636+00
e45d42a0-9be0-41c5-8f22-185230799063	a3e85444-fd76-4b51-8d91-5047821c7b61	legal_status	Public Record(s)	2024-02-20 16:44:57.639+00
7e640cbb-38fa-4a24-9c0b-a80f3454b377	a3e85444-fd76-4b51-8d91-5047821c7b61	held_by	The National Archives, Kew	2024-02-20 16:44:57.641+00
5670527a-934c-40ec-8949-5b64bccbe0be	a3e85444-fd76-4b51-8d91-5047821c7b61	closure_type	Open	2024-02-20 16:44:57.643+00
6ec28860-dacd-44d6-940b-604c50a20232	a3e85444-fd76-4b51-8d91-5047821c7b61	title_closed	false	2024-02-20 16:44:57.646+00
5ba0df49-4c3b-4296-a5fe-ce00346dc719	a3e85444-fd76-4b51-8d91-5047821c7b61	description_closed	false	2024-02-20 16:44:57.648+00
09a4c55e-f173-48ba-930b-7eead2b6ae1d	a3e85444-fd76-4b51-8d91-5047821c7b61	language	English	2024-02-20 16:44:57.65+00
3d550d09-069c-4d00-a96e-426ccbc27815	f323a998-e9a5-42c3-bc8f-eda9efb102e8	file_name	folder-a	2024-02-20 16:44:57.655+00
8a7b996c-9d03-46aa-8369-bf706fd8256d	f323a998-e9a5-42c3-bc8f-eda9efb102e8	file_type	Folder	2024-02-20 16:44:57.657+00
64aadc19-15ef-44c1-ba9d-53457cc83767	f323a998-e9a5-42c3-bc8f-eda9efb102e8	rights_copyright	Crown Copyright	2024-02-20 16:44:57.66+00
f6c0f5d0-7bcd-43f9-8735-c7f639335c11	f323a998-e9a5-42c3-bc8f-eda9efb102e8	legal_status	Public Record(s)	2024-02-20 16:44:57.662+00
80a8c605-f27c-48b0-a961-c2361aee2ced	f323a998-e9a5-42c3-bc8f-eda9efb102e8	held_by	The National Archives, Kew	2024-02-20 16:44:57.664+00
62bc9b44-5baf-43ab-b48f-f81527d9b3e6	f323a998-e9a5-42c3-bc8f-eda9efb102e8	closure_type	Open	2024-02-20 16:44:57.667+00
f46031e9-de92-4d8d-9e58-999fc8ff56df	f323a998-e9a5-42c3-bc8f-eda9efb102e8	title_closed	false	2024-02-20 16:44:57.669+00
b3592981-30f2-4b3c-bd23-68ac111b42bd	f323a998-e9a5-42c3-bc8f-eda9efb102e8	description_closed	false	2024-02-20 16:44:57.671+00
9a445480-6acc-4280-b349-fc467a249c5a	f323a998-e9a5-42c3-bc8f-eda9efb102e8	language	English	2024-02-20 16:44:57.673+00
0ff2d9a9-26fd-40c4-9313-ff20b593942a	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	file_name	content	2024-02-20 16:44:57.678+00
94d30f56-281b-4bff-b606-cc4fff5eb3cc	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	file_type	Folder	2024-02-20 16:44:57.682+00
3d7b7e26-c2bc-4f56-90bd-a767f4c3b5ae	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	rights_copyright	Crown Copyright	2024-02-20 16:44:57.689+00
2aef5958-7af9-4047-9335-3e10ec4cebf9	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	legal_status	Public Record(s)	2024-02-20 16:44:57.692+00
c0b0cfa0-f6ef-487f-a99c-cd795e97cf49	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	held_by	The National Archives, Kew	2024-02-20 16:44:57.695+00
e2dd5822-8971-44de-b2f5-0097661c828f	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	closure_type	Open	2024-02-20 16:44:57.697+00
752aa36b-7868-4e25-b0f8-e343b27f1af7	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	title_closed	false	2024-02-20 16:44:57.7+00
ca4c9625-65c3-44ee-bf79-2cc5d0a47f87	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	description_closed	false	2024-02-20 16:44:57.702+00
db2dd33b-7957-43b8-8314-370ff20fb26c	d306fbf4-b3f5-4311-b2ae-b9bce9556c44	language	English	2024-02-20 16:44:57.705+00
08e73f44-aff9-44df-8db8-6954f4362a63	5d8c077b-5133-4409-9a76-73d91b376175	file_name	redacted	2024-02-20 16:44:57.715+00
f7d44f6f-7fd2-4918-a609-6d61de04fee2	5d8c077b-5133-4409-9a76-73d91b376175	file_type	Folder	2024-02-20 16:44:57.718+00
0eeda88d-f898-4005-b277-8bb4c1c0cce5	5d8c077b-5133-4409-9a76-73d91b376175	rights_copyright	Crown Copyright	2024-02-20 16:44:57.723+00
519dd29b-b561-46e0-a8a2-c470233867d6	5d8c077b-5133-4409-9a76-73d91b376175	legal_status	Public Record(s)	2024-02-20 16:44:57.726+00
54c6205d-39a7-44d8-ad8d-7355a20e2eea	5d8c077b-5133-4409-9a76-73d91b376175	held_by	The National Archives, Kew	2024-02-20 16:44:57.733+00
2d0e1c0e-f8c9-4e4e-84c9-a4abc8c45235	5d8c077b-5133-4409-9a76-73d91b376175	closure_type	Open	2024-02-20 16:44:57.735+00
9eef5bf8-451e-495d-86df-4fa587b64333	5d8c077b-5133-4409-9a76-73d91b376175	title_closed	false	2024-02-20 16:44:57.74+00
33024513-ecb4-48c9-ba9f-6211fe6b86ee	5d8c077b-5133-4409-9a76-73d91b376175	description_closed	false	2024-02-20 16:44:57.744+00
4964843c-4148-48fe-9182-82fcc244cba6	5d8c077b-5133-4409-9a76-73d91b376175	language	English	2024-02-20 16:44:57.746+00
b7f223e5-611c-49f1-8791-729532d2d14b	b9a8f847-ce98-4894-8c48-3986570dec7d	file_name	mismatch.docx	2024-02-20 16:44:57.754+00
7ba9273b-cf11-46fb-8e4a-2afe286c4a4b	b9a8f847-ce98-4894-8c48-3986570dec7d	file_type	File	2024-02-20 16:44:57.757+00
d7c35ace-eea0-4050-8dfe-71e6c3611428	b9a8f847-ce98-4894-8c48-3986570dec7d	file_size	6466	2024-02-20 16:44:57.761+00
f68e3658-8720-4073-8a7f-89424c5ea861	b9a8f847-ce98-4894-8c48-3986570dec7d	rights_copyright	Crown Copyright	2024-02-20 16:44:57.764+00
7bde3424-ec3a-4447-a9ee-1f5dea3d303f	b9a8f847-ce98-4894-8c48-3986570dec7d	legal_status	Public Record(s)	2024-02-20 16:44:57.766+00
da4968bf-fc17-4378-ae81-c4be64009804	b9a8f847-ce98-4894-8c48-3986570dec7d	held_by	The National Archives, Kew	2024-02-20 16:44:57.769+00
9362b227-d45d-4a8d-934e-208395e29d4b	b9a8f847-ce98-4894-8c48-3986570dec7d	date_last_modified	2023-10-18T08:40:37	2024-02-20 16:44:57.771+00
1436ccef-1e9d-447e-bd7d-01859832d15b	b9a8f847-ce98-4894-8c48-3986570dec7d	closure_type	Open	2024-02-20 16:44:57.774+00
c5865c5e-b3d0-4d8e-a8b3-060b84e1a43f	b9a8f847-ce98-4894-8c48-3986570dec7d	title_closed	false	2024-02-20 16:44:57.776+00
25ef3c41-e35f-4896-aecd-eb1b8282e830	b9a8f847-ce98-4894-8c48-3986570dec7d	description_closed	false	2024-02-20 16:44:57.778+00
4c527b29-39a5-428f-b924-aa24eb3016c2	b9a8f847-ce98-4894-8c48-3986570dec7d	language	English	2024-02-20 16:44:57.781+00
45e31a5c-2fd2-45da-8461-d1ca773fcc65	caf080fe-b365-46da-91f1-1aba7689c271	file_name	mismatch	2024-02-20 16:44:57.795+00
9b913741-1087-40b7-8f68-2e52a9e37af3	caf080fe-b365-46da-91f1-1aba7689c271	file_type	Folder	2024-02-20 16:44:57.799+00
2379f6c9-160e-4f94-b5c4-8b4539fb0e34	caf080fe-b365-46da-91f1-1aba7689c271	rights_copyright	Crown Copyright	2024-02-20 16:44:57.802+00
34b2f327-47ca-44b1-b5ad-b5ba00eb9c1b	caf080fe-b365-46da-91f1-1aba7689c271	legal_status	Public Record(s)	2024-02-20 16:44:57.805+00
cb2e8396-ac37-48da-a19e-1683e8c536ce	caf080fe-b365-46da-91f1-1aba7689c271	held_by	The National Archives, Kew	2024-02-20 16:44:57.809+00
bb94043f-956a-4066-a73b-08cdb5eebbf2	caf080fe-b365-46da-91f1-1aba7689c271	closure_type	Open	2024-02-20 16:44:57.811+00
80957f12-0fe3-4da2-82ec-ba693425a8ec	caf080fe-b365-46da-91f1-1aba7689c271	title_closed	false	2024-02-20 16:44:57.817+00
3cc4d02e-bff0-4463-b28a-06f5f9698a04	caf080fe-b365-46da-91f1-1aba7689c271	description_closed	false	2024-02-20 16:44:57.82+00
e7fac949-278c-404b-9f47-7d26fb4f9a79	caf080fe-b365-46da-91f1-1aba7689c271	language	English	2024-02-20 16:44:57.823+00
21a028e8-d6df-4b33-bb81-1c51f8741843	100251bb-5b93-48a9-953f-ad5bd9abfbdc	file_name	file-a2.txt	2024-02-20 16:44:57.828+00
7297c69f-9ef8-41d3-95c8-fee6d6346e7f	100251bb-5b93-48a9-953f-ad5bd9abfbdc	file_type	File	2024-02-20 16:44:57.836+00
093ef63e-9d66-4420-b028-da83e290f667	100251bb-5b93-48a9-953f-ad5bd9abfbdc	file_size	45	2024-02-20 16:44:57.839+00
e2144504-a790-4b95-bc04-6f9fc41bc4dd	100251bb-5b93-48a9-953f-ad5bd9abfbdc	rights_copyright	Crown Copyright	2024-02-20 16:44:57.842+00
6da5b126-770f-4bed-a6ff-0d1d02838ace	100251bb-5b93-48a9-953f-ad5bd9abfbdc	legal_status	Public Record(s)	2024-02-20 16:44:57.844+00
ed35c498-2f78-4a18-9ef4-c62bf33cd6fb	100251bb-5b93-48a9-953f-ad5bd9abfbdc	held_by	The National Archives, Kew	2024-02-20 16:44:57.846+00
ac59c47e-716c-47d0-9143-ac8fe00a3184	100251bb-5b93-48a9-953f-ad5bd9abfbdc	date_last_modified	2023-10-17T00:00:00	2024-02-20 16:44:57.85+00
78299380-8504-4012-a74f-9e24ef03ab59	100251bb-5b93-48a9-953f-ad5bd9abfbdc	closure_type	Open	2024-02-20 16:44:57.852+00
f0cd6df6-b5ab-4961-8063-e2270f737dfd	100251bb-5b93-48a9-953f-ad5bd9abfbdc	title_closed	false	2024-02-20 16:44:57.854+00
df2875fe-b410-45ec-be37-1a5a179803c7	100251bb-5b93-48a9-953f-ad5bd9abfbdc	description_closed	false	2024-02-20 16:44:57.857+00
1478bae8-2d96-473f-bbb0-d29330ff433f	100251bb-5b93-48a9-953f-ad5bd9abfbdc	language	English	2024-02-20 16:44:57.859+00
1882cd87-ceaf-44f4-8319-f8932044eeda	b5cdde0f-93e8-4975-accf-93372d5774c3	file_name	original	2024-03-06 10:43:30.57+00
b3fc01f7-4b54-4cf1-a5d9-51fc7ba9edba	b5cdde0f-93e8-4975-accf-93372d5774c3	file_type	Folder	2024-03-06 10:43:30.575+00
2a84120a-531f-4a04-b4f5-5ea904c40e8e	b5cdde0f-93e8-4975-accf-93372d5774c3	rights_copyright	Crown Copyright	2024-03-06 10:43:30.59+00
ddfe0853-9b9a-48d6-a149-b6ba472d1074	b5cdde0f-93e8-4975-accf-93372d5774c3	legal_status	Public Record(s)	2024-03-06 10:43:30.596+00
2431c4d2-4cfb-4654-9276-184f3f156e26	b5cdde0f-93e8-4975-accf-93372d5774c3	held_by	The National Archives, Kew	2024-03-06 10:43:30.6+00
68b3cd57-d8b2-42c8-951d-14827abb57c8	b5cdde0f-93e8-4975-accf-93372d5774c3	closure_type	Open	2024-03-06 10:43:30.605+00
576b215b-da3f-4426-bfbb-a7a3ad069474	b5cdde0f-93e8-4975-accf-93372d5774c3	title_closed	false	2024-03-06 10:43:30.608+00
163bd52d-7f0a-45d9-a7c5-edd0032aca0a	b5cdde0f-93e8-4975-accf-93372d5774c3	description_closed	false	2024-03-06 10:43:30.614+00
b0828856-ffc8-4396-ac3b-366a2c2fd02d	b5cdde0f-93e8-4975-accf-93372d5774c3	language	English	2024-03-06 10:43:30.618+00
e3077613-0022-4102-86a4-659f6f38bd49	8ffacc5a-443a-4568-a5c9-c9741955b40f	file_name	path0	2024-03-06 10:43:30.631+00
ec117e9a-55c8-485c-b79b-162983039321	8ffacc5a-443a-4568-a5c9-c9741955b40f	file_type	File	2024-03-06 10:43:30.635+00
27c6cafa-065d-47db-915e-e8a295a11ca2	8ffacc5a-443a-4568-a5c9-c9741955b40f	file_size	1024	2024-03-06 10:43:30.639+00
fd86040d-4318-4b57-aece-e7d44dc8cf47	8ffacc5a-443a-4568-a5c9-c9741955b40f	rights_copyright	Crown Copyright	2024-03-06 10:43:30.646+00
258fa98c-487f-4ed8-a444-a672eb668189	8ffacc5a-443a-4568-a5c9-c9741955b40f	legal_status	Public Record(s)	2024-03-06 10:43:30.651+00
70360e9e-1a45-4380-9cef-ba380005ceaa	8ffacc5a-443a-4568-a5c9-c9741955b40f	held_by	The National Archives, Kew	2024-03-06 10:43:30.654+00
5ac8d021-f608-47a2-a8ca-8f783bdfa9fa	8ffacc5a-443a-4568-a5c9-c9741955b40f	date_last_modified	2024-03-05T15:05:31	2024-03-06 10:43:30.656+00
d5763a77-706b-4d0b-9579-96fd642dff1b	8ffacc5a-443a-4568-a5c9-c9741955b40f	closure_type	Open	2024-03-06 10:43:30.659+00
5789f74e-6848-4360-b1f0-c1f0dd9200d1	8ffacc5a-443a-4568-a5c9-c9741955b40f	title_closed	false	2024-03-06 10:43:30.662+00
f104718f-4b8c-4ba0-8d55-cda169daaaac	8ffacc5a-443a-4568-a5c9-c9741955b40f	description_closed	false	2024-03-06 10:43:30.67+00
227857f3-bbe3-4309-8433-465d87767472	8ffacc5a-443a-4568-a5c9-c9741955b40f	language	English	2024-03-06 10:43:30.674+00
1a433506-3184-4cda-9e78-831080ac89fb	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	file_name	path2	2024-03-06 10:43:30.707+00
f342f6ee-83d5-4350-b3a3-f22067eb98c4	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	file_type	File	2024-03-06 10:43:30.711+00
ae81d6f3-d444-40a2-948c-cf89cded3027	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	file_size	1024	2024-03-06 10:43:30.716+00
9096caf4-154f-4953-8493-2d89d72d67f8	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	rights_copyright	Crown Copyright	2024-03-06 10:43:30.72+00
030df845-0050-42dc-b5f0-537e6abd944a	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	legal_status	Public Record(s)	2024-03-06 10:43:30.731+00
89e8ea71-c683-4f8d-8795-9924f4307df7	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	held_by	The National Archives, Kew	2024-03-06 10:43:30.735+00
a6e2f285-36ea-429a-86f7-dd38512482ff	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	date_last_modified	2024-03-05T15:05:31	2024-03-06 10:43:30.741+00
e97a931e-fcd0-4d32-8f2d-6cdb70eaa69a	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	closure_type	Open	2024-03-06 10:43:30.745+00
b9254bef-a0fd-4687-8709-17498654fa0a	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	title_closed	false	2024-03-06 10:43:30.748+00
b047a188-9409-4096-a3c5-7f9f962c5bb0	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	description_closed	false	2024-03-06 10:43:30.751+00
a247849a-975a-4858-b5a5-5cf196a2f61d	a948a34f-6ba0-4ff2-bef6-a290aec31d3f	language	English	2024-03-06 10:43:30.753+00
1d0254f4-7fe3-4e91-bac5-0d86d9d57258	7fb02107-17e3-4659-a644-69f854a6058d	file_name	E2E_tests	2024-03-06 10:43:30.772+00
191feaf4-c57e-4a39-b672-7b36d9f10961	7fb02107-17e3-4659-a644-69f854a6058d	file_type	Folder	2024-03-06 10:43:30.777+00
7ed5bcac-142b-4a02-b9c4-2fcc0cc6bb43	7fb02107-17e3-4659-a644-69f854a6058d	rights_copyright	Crown Copyright	2024-03-06 10:43:30.78+00
12efc3a4-ed69-40e8-b54e-06057e3b5d36	7fb02107-17e3-4659-a644-69f854a6058d	legal_status	Public Record(s)	2024-03-06 10:43:30.791+00
ae1c9074-be30-44c5-b868-951e46cbaf00	7fb02107-17e3-4659-a644-69f854a6058d	held_by	The National Archives, Kew	2024-03-06 10:43:30.794+00
9de0f59b-0372-4733-b98e-a48f383d05d9	7fb02107-17e3-4659-a644-69f854a6058d	closure_type	Open	2024-03-06 10:43:30.797+00
1ec7249a-324d-4882-a032-0f66a7a05d1e	7fb02107-17e3-4659-a644-69f854a6058d	title_closed	false	2024-03-06 10:43:30.8+00
8a0b1aa1-ba88-4f84-b9f9-52ed1b71a115	7fb02107-17e3-4659-a644-69f854a6058d	description_closed	false	2024-03-06 10:43:30.804+00
7526861a-a4cc-40b1-9349-eed3cbca30cd	7fb02107-17e3-4659-a644-69f854a6058d	language	English	2024-03-06 10:43:30.806+00
ff8607f1-dec1-43cd-8337-cb55c54355ea	47526ba9-88e5-4cc8-8bc1-d682a10fa270	file_name	path1	2024-03-06 10:43:30.812+00
824fd7f6-e909-40cb-9731-c2de4b0788cf	47526ba9-88e5-4cc8-8bc1-d682a10fa270	file_type	File	2024-03-06 10:43:30.814+00
9301503c-f453-4695-b0f4-6fe5820aa7d2	47526ba9-88e5-4cc8-8bc1-d682a10fa270	file_size	1024	2024-03-06 10:43:30.817+00
8ed2786b-d957-4c63-a9b8-73d8e6b6a42e	47526ba9-88e5-4cc8-8bc1-d682a10fa270	rights_copyright	Crown Copyright	2024-03-06 10:43:30.819+00
42f6172f-6bcb-47bb-a878-fc87bc495e58	47526ba9-88e5-4cc8-8bc1-d682a10fa270	legal_status	Public Record(s)	2024-03-06 10:43:30.822+00
544f2823-3545-4229-aff5-97eb20ee29f1	47526ba9-88e5-4cc8-8bc1-d682a10fa270	held_by	The National Archives, Kew	2024-03-06 10:43:30.824+00
ccefbbd9-727b-4055-99e9-d1baa68c7c71	47526ba9-88e5-4cc8-8bc1-d682a10fa270	date_last_modified	2024-03-05T15:05:31	2024-03-06 10:43:30.831+00
a03c036a-a746-449e-9d47-980dc65b9618	47526ba9-88e5-4cc8-8bc1-d682a10fa270	closure_type	Open	2024-03-06 10:43:30.834+00
2c5f9d73-2c09-4cc4-bfbd-20de098b7351	47526ba9-88e5-4cc8-8bc1-d682a10fa270	title_closed	false	2024-03-06 10:43:30.836+00
c9a5a089-1a72-47ff-b539-2383d26b8d8a	47526ba9-88e5-4cc8-8bc1-d682a10fa270	description_closed	false	2024-03-06 10:43:30.839+00
3b4cf046-987a-4e26-804d-765e61385a13	47526ba9-88e5-4cc8-8bc1-d682a10fa270	language	English	2024-03-06 10:43:30.841+00
de9021a5-6134-4a15-b5c9-a49626bf0a1c	b2279f23-8d07-4fa5-b0af-94ec4123e21e	note	This record has a .docx extension, but the file content is PDF	2026-02-23 13:40:22.357821+00
e08eb12e-94e5-4877-94e1-930580e26cc1	b9a8f847-ce98-4894-8c48-3986570dec7d	note	This record has a .docx extension, but the file content is PDF	2026-02-23 13:40:22.357821+00
cf66fa81-f01d-4159-8c3e-65c509167a35	062da4a4-dc6f-4c62-895b-b257811a5cba	source	test_file	2026-03-02 01:56:48.927215+00
b02b20f1-82fd-40fc-a5c7-d5f8e92daa43	062da4a4-dc6f-4c62-895b-b257811a5cba	file_name	AYR 25_KTV6RM.csv	2026-03-02 01:56:48.927289+00
fa7cd9d2-7786-4c65-8a56-40cbddfd5eed	062da4a4-dc6f-4c62-895b-b257811a5cba	file_type	File	2026-03-02 01:56:48.927337+00
2a7a8324-d37c-4ad2-bef2-d9af00243c65	062da4a4-dc6f-4c62-895b-b257811a5cba	file_size	81888	2026-03-02 01:56:48.927378+00
888ae23f-8f1b-40f7-86b9-05eb0e293872	062da4a4-dc6f-4c62-895b-b257811a5cba	rights_copyright	Crown Copyright	2026-03-02 01:56:48.927416+00
197bb302-733e-40e0-996d-2df9670b07b1	062da4a4-dc6f-4c62-895b-b257811a5cba	legal_status	Public Record(s)	2026-03-02 01:56:48.927454+00
fededf9f-51b8-41ee-b8ef-5653ac1826a4	062da4a4-dc6f-4c62-895b-b257811a5cba	held_by	The National Archives	2026-03-02 01:56:48.92749+00
8edddeac-da74-4249-9710-29a1ad8db9bf	062da4a4-dc6f-4c62-895b-b257811a5cba	date_last_modified	2026-03-02T01:56:48.927203+00:00	2026-03-02 01:56:48.92753+00
4817fc03-3531-46e2-a8e8-59c90c0e7571	062da4a4-dc6f-4c62-895b-b257811a5cba	description	Test file for AYR development	2026-03-02 01:56:48.927566+00
d7f9f383-9d92-47bf-8305-0fa4eff111f8	062da4a4-dc6f-4c62-895b-b257811a5cba	closure_type	Open	2026-03-02 01:56:48.927601+00
4ab60c17-a35c-4472-91ae-5caea0a138e8	062da4a4-dc6f-4c62-895b-b257811a5cba	title_closed	false	2026-03-02 01:56:48.927637+00
722bc582-0b88-4b9e-bae1-5bef27f14c55	062da4a4-dc6f-4c62-895b-b257811a5cba	description_closed	false	2026-03-02 01:56:48.927675+00
8d284da5-e64d-4a18-8523-7eb3e07c897d	062da4a4-dc6f-4c62-895b-b257811a5cba	language	English	2026-03-02 01:56:48.92771+00
f24dccba-6132-4e60-97d9-2ccb732e66bf	062da4a4-dc6f-4c62-895b-b257811a5cba	created_at	2026-03-02T01:56:48.927210+00:00	2026-03-02 01:56:48.927746+00
35065d2d-c082-4563-a928-1604aa0b8efa	062da4a4-dc6f-4c62-895b-b257811a5cba	last_transfer_date	2026-03-02T01:56:48.927211+00:00	2026-03-02 01:56:48.927782+00
a8bb5ff9-e094-4b3b-8fa8-db4fe4824c91	062da4a4-dc6f-4c62-895b-b257811a5cba	file_format	CSV	2026-03-02 01:56:48.927815+00
734f4ad9-59c5-4962-8428-6d05e3d992fa	062da4a4-dc6f-4c62-895b-b257811a5cba	file_extension	csv	2026-03-02 01:56:48.927848+00
f09e5e35-d96b-4abd-b732-fbdb1f7704b0	062da4a4-dc6f-4c62-895b-b257811a5cba	closure_status	Open	2026-03-02 01:56:48.927881+00
a33cc4ac-2325-4bd9-b92c-ef73cde05d99	062da4a4-dc6f-4c62-895b-b257811a5cba	closure_period	0	2026-03-02 01:56:48.927915+00
45039213-0128-4a63-8ca3-16605ff1fe93	062da4a4-dc6f-4c62-895b-b257811a5cba	foi_exemption_code	None	2026-03-02 01:56:48.927948+00
2089a3fe-0cd9-4a3e-b90b-1c30ddc59f0b	062da4a4-dc6f-4c62-895b-b257811a5cba	foi_exemption_code_description	None	2026-03-02 01:56:48.927981+00
d9662d2d-0d64-4395-a20c-a226a56b966d	062da4a4-dc6f-4c62-895b-b257811a5cba	title	Test File 1	2026-03-02 01:56:48.928015+00
940bb6a6-b5de-429f-b725-035d48844f6d	271e4cb8-9a68-436a-b5da-263cd26cb10f	source	test_file	2026-03-02 01:56:48.941894+00
22497aa3-3a3e-41fe-8597-ab1116667f9b	271e4cb8-9a68-436a-b5da-263cd26cb10f	file_name	AYR 25_ZFW6DB.doc	2026-03-02 01:56:48.941955+00
f6fc62b6-5956-4ee0-9957-36c4c332b030	271e4cb8-9a68-436a-b5da-263cd26cb10f	file_type	File	2026-03-02 01:56:48.941998+00
968b40d6-ec1a-4e7f-ba74-fce86ec42fd6	271e4cb8-9a68-436a-b5da-263cd26cb10f	file_size	73216	2026-03-02 01:56:48.942043+00
7de35743-2602-4009-a977-64bffc4f5a31	271e4cb8-9a68-436a-b5da-263cd26cb10f	rights_copyright	Crown Copyright	2026-03-02 01:56:48.942083+00
34fcd8d3-ca71-4b6f-b139-0bb9a4d4f87f	271e4cb8-9a68-436a-b5da-263cd26cb10f	legal_status	Public Record(s)	2026-03-02 01:56:48.942119+00
1068a2d0-8391-4c49-ac55-fdaecbb1572b	271e4cb8-9a68-436a-b5da-263cd26cb10f	held_by	The National Archives	2026-03-02 01:56:48.942157+00
1ea297a3-a3f4-4157-bfe3-2948cf353c08	271e4cb8-9a68-436a-b5da-263cd26cb10f	date_last_modified	2026-03-02T01:56:48.941881+00:00	2026-03-02 01:56:48.942192+00
607fb5f0-ed41-436b-bbcc-b6305b3b3817	271e4cb8-9a68-436a-b5da-263cd26cb10f	description	Test file for AYR development	2026-03-02 01:56:48.942227+00
074b272c-5d52-47a1-9ca4-1e4645eff4c7	271e4cb8-9a68-436a-b5da-263cd26cb10f	closure_type	Open	2026-03-02 01:56:48.942262+00
33fe3dcf-9fa4-40a0-b83a-866d604928e3	271e4cb8-9a68-436a-b5da-263cd26cb10f	title_closed	false	2026-03-02 01:56:48.942296+00
ccf5f7fc-8836-4a3f-94ae-fa4777e952d6	271e4cb8-9a68-436a-b5da-263cd26cb10f	description_closed	false	2026-03-02 01:56:48.942333+00
2907f8fd-c7b5-47ad-9dfd-a16b1ca36f46	271e4cb8-9a68-436a-b5da-263cd26cb10f	language	English	2026-03-02 01:56:48.942369+00
bed700df-75ff-4db0-96b9-f3e26a502163	271e4cb8-9a68-436a-b5da-263cd26cb10f	created_at	2026-03-02T01:56:48.941888+00:00	2026-03-02 01:56:48.942405+00
3b112f46-93ce-4545-9191-9934b541279c	271e4cb8-9a68-436a-b5da-263cd26cb10f	last_transfer_date	2026-03-02T01:56:48.941890+00:00	2026-03-02 01:56:48.942442+00
207a9d5a-2b8c-4aa3-9f36-0bff09fd672c	271e4cb8-9a68-436a-b5da-263cd26cb10f	file_format	DOC	2026-03-02 01:56:48.942476+00
3f71e8b1-6142-4956-bee6-902ef3ce8268	271e4cb8-9a68-436a-b5da-263cd26cb10f	file_extension	doc	2026-03-02 01:56:48.942511+00
8e5ecb82-0613-41c3-b529-768b0445b519	271e4cb8-9a68-436a-b5da-263cd26cb10f	closure_status	Open	2026-03-02 01:56:48.942545+00
8cae6737-4913-490d-be65-27c507679c5b	271e4cb8-9a68-436a-b5da-263cd26cb10f	closure_period	0	2026-03-02 01:56:48.94258+00
4c81f768-7ddc-46cf-977d-90a04f98eb7c	271e4cb8-9a68-436a-b5da-263cd26cb10f	foi_exemption_code	None	2026-03-02 01:56:48.942615+00
24a3fe72-a038-48af-8c15-74caa006caa8	271e4cb8-9a68-436a-b5da-263cd26cb10f	foi_exemption_code_description	None	2026-03-02 01:56:48.942648+00
0345de54-adab-403d-9fe4-31af1c95d216	271e4cb8-9a68-436a-b5da-263cd26cb10f	title	Test File 2	2026-03-02 01:56:48.942682+00
14e8e5ab-7fd6-4f5f-a392-cec13a626b99	935645a6-4abe-4387-b877-018377aefdac	source	test_file	2026-03-02 01:56:49.001696+00
5c588c54-b1a8-48f3-8869-b2cbf474a102	935645a6-4abe-4387-b877-018377aefdac	file_name	AYR 25_ZDC8J4.docx	2026-03-02 01:56:49.001753+00
e16a3d8b-b70c-4d39-b442-425822fd7909	935645a6-4abe-4387-b877-018377aefdac	file_type	File	2026-03-02 01:56:49.001795+00
bf405694-f8f6-4237-b717-cf363468ecbe	935645a6-4abe-4387-b877-018377aefdac	file_size	9075	2026-03-02 01:56:49.001838+00
54491bf0-37da-4d88-8868-04cf3ed1c99a	935645a6-4abe-4387-b877-018377aefdac	rights_copyright	Crown Copyright	2026-03-02 01:56:49.001875+00
4a984190-c4a5-4863-b313-7f9301129f44	935645a6-4abe-4387-b877-018377aefdac	legal_status	Public Record(s)	2026-03-02 01:56:49.001914+00
d078475a-7670-4fdf-9545-a178226172ac	935645a6-4abe-4387-b877-018377aefdac	held_by	The National Archives	2026-03-02 01:56:49.001951+00
a18ca91d-ee7d-42bf-8828-4bf3879d1aef	935645a6-4abe-4387-b877-018377aefdac	date_last_modified	2026-03-02T01:56:49.001685+00:00	2026-03-02 01:56:49.001985+00
d8376418-1d1e-4b08-9117-f1080247eb9e	935645a6-4abe-4387-b877-018377aefdac	description	Test file for AYR development	2026-03-02 01:56:49.002018+00
0a4794cd-8041-4c50-9c77-326fa136769c	935645a6-4abe-4387-b877-018377aefdac	closure_type	Open	2026-03-02 01:56:49.00205+00
f6717127-b3fc-41c4-add9-707d4743b984	935645a6-4abe-4387-b877-018377aefdac	title_closed	false	2026-03-02 01:56:49.002084+00
609d2672-27c1-431c-b72b-d78a4ef4e17e	935645a6-4abe-4387-b877-018377aefdac	description_closed	false	2026-03-02 01:56:49.002117+00
81fa2423-f8fa-46c9-84c9-06d209f6fec5	935645a6-4abe-4387-b877-018377aefdac	language	English	2026-03-02 01:56:49.002151+00
4e4bb372-127e-4d1d-9103-d7c192bf3731	935645a6-4abe-4387-b877-018377aefdac	created_at	2026-03-02T01:56:49.001691+00:00	2026-03-02 01:56:49.002185+00
0cbb5092-86d7-49cc-96c6-e42724f9900f	935645a6-4abe-4387-b877-018377aefdac	last_transfer_date	2026-03-02T01:56:49.001692+00:00	2026-03-02 01:56:49.002221+00
a8363e46-a5e1-410b-b2db-38bac5f801de	935645a6-4abe-4387-b877-018377aefdac	file_format	DOCX	2026-03-02 01:56:49.002256+00
b7b4bb7d-2d03-4cf8-bef8-93e44ad8271d	935645a6-4abe-4387-b877-018377aefdac	file_extension	docx	2026-03-02 01:56:49.00229+00
25763801-dbd2-4a13-87e4-f8f4518924e7	935645a6-4abe-4387-b877-018377aefdac	closure_status	Open	2026-03-02 01:56:49.002323+00
54039c84-e4be-4322-ac95-0d3f20bc9fe8	935645a6-4abe-4387-b877-018377aefdac	closure_period	0	2026-03-02 01:56:49.002356+00
59462d08-acf1-43f8-b4cb-7381981a351b	935645a6-4abe-4387-b877-018377aefdac	foi_exemption_code	None	2026-03-02 01:56:49.002389+00
c6bf85cf-2fb0-44f7-91c2-24c59617ebaa	935645a6-4abe-4387-b877-018377aefdac	foi_exemption_code_description	None	2026-03-02 01:56:49.002423+00
5c188cbd-9d81-4497-b164-025102e67cfb	935645a6-4abe-4387-b877-018377aefdac	title	Test File 3	2026-03-02 01:56:49.002457+00
45f2fe4b-b114-49c5-aeed-64978ceaf3fb	32081439-36c9-4f38-8bcb-a8d610f04b0f	source	test_file	2026-03-02 01:56:49.064329+00
916ea1c1-1516-4c69-9035-6bbfcbd8a693	32081439-36c9-4f38-8bcb-a8d610f04b0f	file_name	AYR 25_LW73EO.epub	2026-03-02 01:56:49.0644+00
b021b2e5-5451-4c5d-87d2-c13bfe161a05	32081439-36c9-4f38-8bcb-a8d610f04b0f	file_type	File	2026-03-02 01:56:49.064449+00
7adc6be3-9e2c-4d66-895b-bc3bd8e86dbb	32081439-36c9-4f38-8bcb-a8d610f04b0f	file_size	3999513	2026-03-02 01:56:49.064495+00
6d85f640-fa0d-490e-a0e3-664d61e73a25	32081439-36c9-4f38-8bcb-a8d610f04b0f	rights_copyright	Crown Copyright	2026-03-02 01:56:49.064537+00
50a2b780-e7ac-4b08-9e4f-4ad88a03846b	32081439-36c9-4f38-8bcb-a8d610f04b0f	legal_status	Public Record(s)	2026-03-02 01:56:49.064579+00
52015d82-38d6-4255-9a72-f1863095eca1	32081439-36c9-4f38-8bcb-a8d610f04b0f	held_by	The National Archives	2026-03-02 01:56:49.064618+00
b56c675c-e88e-47d6-aec9-f3772157adfc	32081439-36c9-4f38-8bcb-a8d610f04b0f	date_last_modified	2026-03-02T01:56:49.064313+00:00	2026-03-02 01:56:49.064658+00
e6521bee-556e-48cd-885c-1c92002e4159	32081439-36c9-4f38-8bcb-a8d610f04b0f	description	Test file for AYR development	2026-03-02 01:56:49.064697+00
b8d8ce5a-340a-4590-9426-da9d6d042a41	32081439-36c9-4f38-8bcb-a8d610f04b0f	closure_type	Open	2026-03-02 01:56:49.064736+00
27a4094a-b52a-4e5d-9724-0f6e74663202	32081439-36c9-4f38-8bcb-a8d610f04b0f	title_closed	false	2026-03-02 01:56:49.06478+00
4e5c4bae-a4af-4a0f-b786-b975f5159ffe	32081439-36c9-4f38-8bcb-a8d610f04b0f	description_closed	false	2026-03-02 01:56:49.064825+00
f0d89fd6-16e0-474c-b667-bbdcef56e61c	32081439-36c9-4f38-8bcb-a8d610f04b0f	language	English	2026-03-02 01:56:49.064867+00
63c66655-caad-48af-82cb-18cd71f4fc01	32081439-36c9-4f38-8bcb-a8d610f04b0f	created_at	2026-03-02T01:56:49.064323+00:00	2026-03-02 01:56:49.064907+00
1d8e618c-e1d2-42e0-be26-91b719b5818c	32081439-36c9-4f38-8bcb-a8d610f04b0f	last_transfer_date	2026-03-02T01:56:49.064324+00:00	2026-03-02 01:56:49.064948+00
1bc2c7de-9e83-4339-a0cb-2e3da10d081b	32081439-36c9-4f38-8bcb-a8d610f04b0f	file_format	EPUB	2026-03-02 01:56:49.064987+00
da1e86f0-4321-46cc-9419-685ab6a3595c	32081439-36c9-4f38-8bcb-a8d610f04b0f	file_extension	epub	2026-03-02 01:56:49.065027+00
ba60c88d-c6de-49d9-b6b9-918c3aa6b0bc	32081439-36c9-4f38-8bcb-a8d610f04b0f	closure_status	Open	2026-03-02 01:56:49.065067+00
151207db-5003-44b5-90c1-ef310c50f62e	32081439-36c9-4f38-8bcb-a8d610f04b0f	closure_period	0	2026-03-02 01:56:49.065106+00
6fd084f8-caae-4590-86f2-b712e132eacc	32081439-36c9-4f38-8bcb-a8d610f04b0f	foi_exemption_code	None	2026-03-02 01:56:49.065147+00
b92c0d37-024e-4272-bd1c-128aaecf20ad	32081439-36c9-4f38-8bcb-a8d610f04b0f	foi_exemption_code_description	None	2026-03-02 01:56:49.065186+00
a57aadc0-c1b6-42f5-90c8-e3e1f0b643e3	32081439-36c9-4f38-8bcb-a8d610f04b0f	title	Test File 4	2026-03-02 01:56:49.065226+00
ac505e1e-38f5-410f-ae6b-e17fbd4531be	470e55b9-4758-4d68-8c3d-065413fa7d49	source	test_file	2026-03-02 01:56:49.13044+00
22b6e395-9e0f-4b7e-a31a-8c0d2235ccd2	470e55b9-4758-4d68-8c3d-065413fa7d49	file_name	AYR 25_6YTFTC.jpg	2026-03-02 01:56:49.130504+00
065c82c0-0d4e-49cd-bfe5-2260d09fb4f5	470e55b9-4758-4d68-8c3d-065413fa7d49	file_type	File	2026-03-02 01:56:49.130549+00
71713823-5c65-4053-9377-aaccce123513	470e55b9-4758-4d68-8c3d-065413fa7d49	file_size	5631665	2026-03-02 01:56:49.130592+00
8ff17aa4-1947-46e8-b3c2-bc59625fe65f	470e55b9-4758-4d68-8c3d-065413fa7d49	rights_copyright	Crown Copyright	2026-03-02 01:56:49.130631+00
615eb903-edb4-4af4-8328-c6901b6db4f5	470e55b9-4758-4d68-8c3d-065413fa7d49	legal_status	Public Record(s)	2026-03-02 01:56:49.130667+00
5a73fdd3-35f8-4da1-b4e4-59d44522b1b0	470e55b9-4758-4d68-8c3d-065413fa7d49	held_by	The National Archives	2026-03-02 01:56:49.130702+00
66af24dd-d927-4438-81b8-4e536ca30b41	470e55b9-4758-4d68-8c3d-065413fa7d49	date_last_modified	2026-03-02T01:56:49.130426+00:00	2026-03-02 01:56:49.130735+00
b6748850-edd3-45ae-b304-49fcb3df8883	470e55b9-4758-4d68-8c3d-065413fa7d49	description	Test file for AYR development	2026-03-02 01:56:49.130769+00
0b115927-18f2-4f82-9718-1ddbabc6d452	470e55b9-4758-4d68-8c3d-065413fa7d49	closure_type	Open	2026-03-02 01:56:49.130803+00
e61531c8-6748-43ac-a5f2-39d28c2a1364	470e55b9-4758-4d68-8c3d-065413fa7d49	title_closed	false	2026-03-02 01:56:49.130838+00
74260ccb-a954-4921-9d91-f23da57f2115	470e55b9-4758-4d68-8c3d-065413fa7d49	description_closed	false	2026-03-02 01:56:49.130873+00
4df3d065-c40c-406e-bf2b-123e15e88eb9	470e55b9-4758-4d68-8c3d-065413fa7d49	language	English	2026-03-02 01:56:49.130906+00
9410411e-ba67-4af0-888f-ad1bbfd9595b	470e55b9-4758-4d68-8c3d-065413fa7d49	created_at	2026-03-02T01:56:49.130434+00:00	2026-03-02 01:56:49.130941+00
64d1e2ca-1f93-4d47-b053-387ac9b3b7b1	470e55b9-4758-4d68-8c3d-065413fa7d49	last_transfer_date	2026-03-02T01:56:49.130436+00:00	2026-03-02 01:56:49.130974+00
1c2925bd-c10b-4952-92d6-1861e021f88d	470e55b9-4758-4d68-8c3d-065413fa7d49	file_format	JPG	2026-03-02 01:56:49.131006+00
570135d0-a918-41ce-b4bf-ce1f85f82a91	470e55b9-4758-4d68-8c3d-065413fa7d49	file_extension	jpg	2026-03-02 01:56:49.13104+00
e7cd2474-f17b-40d0-93f1-54acb2a162ec	470e55b9-4758-4d68-8c3d-065413fa7d49	closure_status	Open	2026-03-02 01:56:49.131082+00
3d69896f-430f-4b7d-9bec-962727d1505a	470e55b9-4758-4d68-8c3d-065413fa7d49	closure_period	0	2026-03-02 01:56:49.131116+00
e0d64e3e-f79b-4a85-8532-ec4a8b4c62e4	470e55b9-4758-4d68-8c3d-065413fa7d49	foi_exemption_code	None	2026-03-02 01:56:49.131151+00
fd22b69e-b234-4bb9-8edb-64f23af80821	470e55b9-4758-4d68-8c3d-065413fa7d49	foi_exemption_code_description	None	2026-03-02 01:56:49.131188+00
077e42d4-aa7a-41b1-8a63-3710cb898634	470e55b9-4758-4d68-8c3d-065413fa7d49	title	Test File 5	2026-03-02 01:56:49.131223+00
de6df62d-7968-4e2e-98f7-10f6b49e9e56	5add6a18-1dc6-4552-9bf8-c8266309ce80	source	test_file	2026-03-02 01:56:49.27064+00
b8d4e98b-741d-48d7-81ce-046058cd2f79	5add6a18-1dc6-4552-9bf8-c8266309ce80	file_name	AYR 25_Z9P4WW.odt	2026-03-02 01:56:49.270706+00
0ff4ce6e-4cc2-4bb4-8907-0451e83b848a	5add6a18-1dc6-4552-9bf8-c8266309ce80	file_type	File	2026-03-02 01:56:49.270749+00
86879df2-71b6-4986-8794-d25f212cb29d	5add6a18-1dc6-4552-9bf8-c8266309ce80	file_size	14101361	2026-03-02 01:56:49.270791+00
ae50527a-cfa9-4e06-8541-ea3860c6bfc5	5add6a18-1dc6-4552-9bf8-c8266309ce80	rights_copyright	Crown Copyright	2026-03-02 01:56:49.270829+00
0208e57d-a504-428b-a46d-360e84a2e19c	5add6a18-1dc6-4552-9bf8-c8266309ce80	legal_status	Public Record(s)	2026-03-02 01:56:49.270869+00
def3ec1d-12f4-4069-9a2a-fe50dc1e9f8a	5add6a18-1dc6-4552-9bf8-c8266309ce80	held_by	The National Archives	2026-03-02 01:56:49.270906+00
93e1a3d0-699b-439b-a441-f3b20ee557d7	5add6a18-1dc6-4552-9bf8-c8266309ce80	date_last_modified	2026-03-02T01:56:49.270627+00:00	2026-03-02 01:56:49.270943+00
dfdce843-e235-4abe-aa3a-2dec85db061b	5add6a18-1dc6-4552-9bf8-c8266309ce80	description	Test file for AYR development	2026-03-02 01:56:49.270975+00
a027f2f3-b30f-450a-906b-3af26f11825b	5add6a18-1dc6-4552-9bf8-c8266309ce80	closure_type	Open	2026-03-02 01:56:49.271008+00
59c831e3-7fc7-4f74-b0bc-35149588a042	5add6a18-1dc6-4552-9bf8-c8266309ce80	title_closed	false	2026-03-02 01:56:49.271041+00
e1c36eac-97d9-43ea-8d78-c14e711d9b9f	5add6a18-1dc6-4552-9bf8-c8266309ce80	description_closed	false	2026-03-02 01:56:49.271074+00
6d39ca5f-f5cf-499e-8305-b03845b95fde	5add6a18-1dc6-4552-9bf8-c8266309ce80	language	English	2026-03-02 01:56:49.271108+00
7359631f-e7a2-4ad5-827f-ece4b8296977	5add6a18-1dc6-4552-9bf8-c8266309ce80	created_at	2026-03-02T01:56:49.270635+00:00	2026-03-02 01:56:49.271144+00
2c4b2c85-f753-45ae-95e1-c53e5854d981	5add6a18-1dc6-4552-9bf8-c8266309ce80	last_transfer_date	2026-03-02T01:56:49.270636+00:00	2026-03-02 01:56:49.271178+00
ccbdcf70-d9b4-488b-a62f-ead4276d52d4	5add6a18-1dc6-4552-9bf8-c8266309ce80	file_format	ODT	2026-03-02 01:56:49.271211+00
de8897b7-9d2f-428f-9f54-9a791f7c8874	5add6a18-1dc6-4552-9bf8-c8266309ce80	file_extension	odt	2026-03-02 01:56:49.271245+00
273c26ef-4b4a-429a-8609-7c9b25e5bdd7	5add6a18-1dc6-4552-9bf8-c8266309ce80	closure_status	Open	2026-03-02 01:56:49.27128+00
c0ddafbd-dc29-4482-a52a-d8be034f8827	5add6a18-1dc6-4552-9bf8-c8266309ce80	closure_period	0	2026-03-02 01:56:49.271314+00
19d84081-b570-4823-9a95-2fd962bf871f	5add6a18-1dc6-4552-9bf8-c8266309ce80	foi_exemption_code	None	2026-03-02 01:56:49.27135+00
47dfbc28-9d41-4515-83af-635db796a939	5add6a18-1dc6-4552-9bf8-c8266309ce80	foi_exemption_code_description	None	2026-03-02 01:56:49.271384+00
0cc5d24e-ee29-49a8-8c75-786a52bfbc23	5add6a18-1dc6-4552-9bf8-c8266309ce80	title	Test File 6	2026-03-02 01:56:49.271418+00
05cfb014-202b-4dd7-838b-3cc8a3e18402	a84f03f2-df66-40ba-b446-3e4c563c3f23	source	test_file	2026-03-02 01:56:49.286474+00
ed73c02b-56df-4966-86dd-9e0000112b4c	a84f03f2-df66-40ba-b446-3e4c563c3f23	file_name	AYR 25_ZDKL26.pdf	2026-03-02 01:56:49.286535+00
4330c09c-c0ae-46ed-98e5-e7a7e36bc5ef	a84f03f2-df66-40ba-b446-3e4c563c3f23	file_type	File	2026-03-02 01:56:49.286578+00
ea520833-7fbe-423f-b560-20760e40df68	a84f03f2-df66-40ba-b446-3e4c563c3f23	file_size	117889	2026-03-02 01:56:49.286622+00
4c5a9af5-90e4-4a7b-b436-20d0255160f4	a84f03f2-df66-40ba-b446-3e4c563c3f23	rights_copyright	Crown Copyright	2026-03-02 01:56:49.286663+00
b6b04055-ab4b-4790-ad33-cf1c980e709b	a84f03f2-df66-40ba-b446-3e4c563c3f23	legal_status	Public Record(s)	2026-03-02 01:56:49.286701+00
186db2a9-c97b-4336-a05b-9b177f40ef42	a84f03f2-df66-40ba-b446-3e4c563c3f23	held_by	The National Archives	2026-03-02 01:56:49.286738+00
0681f5ba-996e-4af5-8f08-cd0193065dff	a84f03f2-df66-40ba-b446-3e4c563c3f23	date_last_modified	2026-03-02T01:56:49.286459+00:00	2026-03-02 01:56:49.286774+00
2c4c1d97-2976-4361-a484-6a113a017e95	a84f03f2-df66-40ba-b446-3e4c563c3f23	description	Test file for AYR development	2026-03-02 01:56:49.286809+00
2cfe73ff-ef54-4f98-8d46-cf9f1e68e10b	a84f03f2-df66-40ba-b446-3e4c563c3f23	closure_type	Open	2026-03-02 01:56:49.286846+00
a29f568f-fad2-4993-b0a9-0631817cf631	a84f03f2-df66-40ba-b446-3e4c563c3f23	title_closed	false	2026-03-02 01:56:49.28688+00
08fe816e-d36f-4f43-89fd-71808fe943a7	a84f03f2-df66-40ba-b446-3e4c563c3f23	description_closed	false	2026-03-02 01:56:49.286916+00
74a6196d-af40-4143-916b-093b548360b8	a84f03f2-df66-40ba-b446-3e4c563c3f23	language	English	2026-03-02 01:56:49.28695+00
fee282da-5e5b-4e8d-be95-e8d76bf8e212	a84f03f2-df66-40ba-b446-3e4c563c3f23	created_at	2026-03-02T01:56:49.286468+00:00	2026-03-02 01:56:49.286987+00
76a3e53b-1c4f-4e83-b49a-837685d1478d	a84f03f2-df66-40ba-b446-3e4c563c3f23	last_transfer_date	2026-03-02T01:56:49.286469+00:00	2026-03-02 01:56:49.287022+00
bc773eb6-723f-4c60-824a-7ab50f1463b2	a84f03f2-df66-40ba-b446-3e4c563c3f23	file_format	PDF	2026-03-02 01:56:49.287056+00
720d3a32-25a6-4400-82a7-b0d7de36e3e8	a84f03f2-df66-40ba-b446-3e4c563c3f23	file_extension	pdf	2026-03-02 01:56:49.28709+00
ef303727-073b-4e0f-a2f9-1eaf4d438a1c	a84f03f2-df66-40ba-b446-3e4c563c3f23	closure_status	Open	2026-03-02 01:56:49.287125+00
75d84b62-3c8c-4755-8cdf-9ebcd32110a2	a84f03f2-df66-40ba-b446-3e4c563c3f23	closure_period	0	2026-03-02 01:56:49.28716+00
de69e9c4-76e3-4c29-8eda-2ee5352d2300	a84f03f2-df66-40ba-b446-3e4c563c3f23	foi_exemption_code	None	2026-03-02 01:56:49.287195+00
3a04ec70-95c2-43e3-b79d-b37387d64f01	a84f03f2-df66-40ba-b446-3e4c563c3f23	foi_exemption_code_description	None	2026-03-02 01:56:49.287231+00
51d7a51b-0f42-4b9a-94c2-5e1f06a17ad4	a84f03f2-df66-40ba-b446-3e4c563c3f23	title	Test File 7	2026-03-02 01:56:49.287265+00
e1961104-5675-47f7-bac7-830816c8fe5e	e894c064-812e-4db1-896f-8c82c92f3d01	source	test_file	2026-03-02 01:56:49.425871+00
87974eab-eada-48c2-9781-6c284605c4fe	e894c064-812e-4db1-896f-8c82c92f3d01	file_name	AYR 25_G85D3R.png	2026-03-02 01:56:49.425938+00
6f64f339-62ef-4c91-83b6-6063eac2a665	e894c064-812e-4db1-896f-8c82c92f3d01	file_type	File	2026-03-02 01:56:49.425984+00
9d40729e-3f3d-4d48-9b58-b4d3eac56c9a	e894c064-812e-4db1-896f-8c82c92f3d01	file_size	14089962	2026-03-02 01:56:49.426026+00
3daa4b84-64fb-4314-ae01-1334e9bf7dcb	e894c064-812e-4db1-896f-8c82c92f3d01	rights_copyright	Crown Copyright	2026-03-02 01:56:49.426064+00
2b822165-b482-48b4-a112-ccf3f22ba1a7	e894c064-812e-4db1-896f-8c82c92f3d01	legal_status	Public Record(s)	2026-03-02 01:56:49.426102+00
ebcb4205-c03a-4dd8-91d7-e8bd1860f8c2	e894c064-812e-4db1-896f-8c82c92f3d01	held_by	The National Archives	2026-03-02 01:56:49.42614+00
e5973928-fe42-40eb-97e9-0ca2f5426b01	e894c064-812e-4db1-896f-8c82c92f3d01	date_last_modified	2026-03-02T01:56:49.425857+00:00	2026-03-02 01:56:49.426174+00
c4f3f5b8-137d-41e3-9258-a114a199f1f9	e894c064-812e-4db1-896f-8c82c92f3d01	description	Test file for AYR development	2026-03-02 01:56:49.42621+00
fc0009b5-7240-48df-8a08-6fff58c2f8eb	e894c064-812e-4db1-896f-8c82c92f3d01	closure_type	Open	2026-03-02 01:56:49.426244+00
4ab21f97-2c76-45d0-adac-2558bc8e55c8	e894c064-812e-4db1-896f-8c82c92f3d01	title_closed	false	2026-03-02 01:56:49.426281+00
f2bf2865-71ee-43e7-854c-8bdc1590c018	e894c064-812e-4db1-896f-8c82c92f3d01	description_closed	false	2026-03-02 01:56:49.426317+00
1ba98388-aed4-41b4-8d48-b2c734353d9c	e894c064-812e-4db1-896f-8c82c92f3d01	language	English	2026-03-02 01:56:49.426352+00
b238a6a4-b03e-4cfb-9ae6-4a8e11d7f6df	e894c064-812e-4db1-896f-8c82c92f3d01	created_at	2026-03-02T01:56:49.425865+00:00	2026-03-02 01:56:49.426389+00
2fc1489d-2ed8-4215-916b-1fdf87f35e00	e9cef0ab-e553-4c69-b81e-5676d1749999	file_type	File	2026-03-02 01:56:49.577087+00
4b268815-f3b9-48b9-b502-5f61dcfb012a	e894c064-812e-4db1-896f-8c82c92f3d01	last_transfer_date	2026-03-02T01:56:49.425866+00:00	2026-03-02 01:56:49.426426+00
15c5b15c-9c05-4183-bd48-dcf5965042f1	e894c064-812e-4db1-896f-8c82c92f3d01	file_format	PNG	2026-03-02 01:56:49.42646+00
180b6911-b6c9-4922-85ef-cd3b92f3d8c9	e894c064-812e-4db1-896f-8c82c92f3d01	file_extension	png	2026-03-02 01:56:49.426494+00
02611738-6f1a-40a9-bf1a-a824f23e5053	e894c064-812e-4db1-896f-8c82c92f3d01	closure_status	Open	2026-03-02 01:56:49.426529+00
9d2a41b5-d136-4b84-8ead-82bb1b5885a0	e894c064-812e-4db1-896f-8c82c92f3d01	closure_period	0	2026-03-02 01:56:49.426564+00
21d6c40c-56c5-4fde-98fc-e2ed7e641ea1	e894c064-812e-4db1-896f-8c82c92f3d01	foi_exemption_code	None	2026-03-02 01:56:49.426599+00
0559fea6-5d9d-45c7-8f8d-8d228fba4514	e894c064-812e-4db1-896f-8c82c92f3d01	foi_exemption_code_description	None	2026-03-02 01:56:49.426633+00
1d1f0ceb-c64a-48f0-8cf7-b40ae20986f2	e894c064-812e-4db1-896f-8c82c92f3d01	title	Test File 8	2026-03-02 01:56:49.426668+00
2df60236-0b79-4a5b-a726-55d0f6870054	02ac3799-c40a-4274-8600-e19e052c6432	source	test_file	2026-03-02 01:56:49.446534+00
a3c2860f-a607-41ff-bb61-44a55248fb6b	02ac3799-c40a-4274-8600-e19e052c6432	file_name	AYR 25_Z95P37.ppt	2026-03-02 01:56:49.446593+00
ca9f9231-58b2-46a0-8a67-581eadd77125	02ac3799-c40a-4274-8600-e19e052c6432	file_type	File	2026-03-02 01:56:49.446633+00
17a021d8-b1d2-4ca5-9ef1-ce7bb79b6320	02ac3799-c40a-4274-8600-e19e052c6432	file_size	520704	2026-03-02 01:56:49.446675+00
7547040d-621d-454e-9c60-16ba14b1414c	02ac3799-c40a-4274-8600-e19e052c6432	rights_copyright	Crown Copyright	2026-03-02 01:56:49.446712+00
a2f07339-ac0f-4c3b-a4d1-059f65d89307	02ac3799-c40a-4274-8600-e19e052c6432	legal_status	Public Record(s)	2026-03-02 01:56:49.446746+00
32bd2c90-85ff-4f95-89a2-30f8ab476567	02ac3799-c40a-4274-8600-e19e052c6432	held_by	The National Archives	2026-03-02 01:56:49.446779+00
ba29ea0a-73c1-4de7-94f2-ca8999223fa6	02ac3799-c40a-4274-8600-e19e052c6432	date_last_modified	2026-03-02T01:56:49.446521+00:00	2026-03-02 01:56:49.446815+00
8e6f927f-c56b-4239-ba26-24e33e009589	02ac3799-c40a-4274-8600-e19e052c6432	description	Test file for AYR development	2026-03-02 01:56:49.446848+00
eb79e89d-1763-4cbc-a671-93f2a74d1dc2	02ac3799-c40a-4274-8600-e19e052c6432	closure_type	Open	2026-03-02 01:56:49.446881+00
1f89008d-b85c-4288-aed8-bf893b868014	02ac3799-c40a-4274-8600-e19e052c6432	title_closed	false	2026-03-02 01:56:49.446914+00
c7a41446-cd6f-49ab-b90f-cb1b15e16e75	02ac3799-c40a-4274-8600-e19e052c6432	description_closed	false	2026-03-02 01:56:49.446948+00
02536201-1160-4b27-8b7b-726fb233401d	02ac3799-c40a-4274-8600-e19e052c6432	language	English	2026-03-02 01:56:49.44698+00
cfda03cd-200b-4c87-89f1-46307d22123d	02ac3799-c40a-4274-8600-e19e052c6432	created_at	2026-03-02T01:56:49.446528+00:00	2026-03-02 01:56:49.447015+00
8cc7c09f-e610-4218-ae07-31c7c46a5cc6	02ac3799-c40a-4274-8600-e19e052c6432	last_transfer_date	2026-03-02T01:56:49.446530+00:00	2026-03-02 01:56:49.447048+00
d6878aa5-7578-47e2-ae89-d88b7faac553	02ac3799-c40a-4274-8600-e19e052c6432	file_format	PPT	2026-03-02 01:56:49.44708+00
1919d027-e5e4-4a5d-b609-a8116c309b95	02ac3799-c40a-4274-8600-e19e052c6432	file_extension	ppt	2026-03-02 01:56:49.447113+00
7df24d53-c5ba-4471-ba5b-3057947dc79d	02ac3799-c40a-4274-8600-e19e052c6432	closure_status	Open	2026-03-02 01:56:49.447146+00
05bf2613-d92a-4743-8d23-9345796181b6	02ac3799-c40a-4274-8600-e19e052c6432	closure_period	0	2026-03-02 01:56:49.447178+00
b3d95209-f62b-43a8-8e36-287d77274c3f	02ac3799-c40a-4274-8600-e19e052c6432	foi_exemption_code	None	2026-03-02 01:56:49.447212+00
b8b152d6-09da-4679-b2a7-fa3858c5d96a	02ac3799-c40a-4274-8600-e19e052c6432	foi_exemption_code_description	None	2026-03-02 01:56:49.447246+00
443c6ec0-a103-4814-973d-2c3f3d5e3122	02ac3799-c40a-4274-8600-e19e052c6432	title	Test File 9	2026-03-02 01:56:49.447281+00
338aa94f-52a0-4d06-a253-be74a81aafc8	092de09f-718a-4053-8d4b-a35dce9e76bd	source	test_file	2026-03-02 01:56:49.461973+00
a4639bf8-aa2e-4f27-a780-5c972bd6dde5	092de09f-718a-4053-8d4b-a35dce9e76bd	file_name	AYR 25_ZG8SKW.pptx	2026-03-02 01:56:49.462077+00
8f7a413d-5f9a-4dff-986b-25b748b5f515	092de09f-718a-4053-8d4b-a35dce9e76bd	file_type	File	2026-03-02 01:56:49.462129+00
b7a85056-8860-48ac-abb1-d35440cf1662	092de09f-718a-4053-8d4b-a35dce9e76bd	file_size	70690	2026-03-02 01:56:49.462174+00
900b7898-e5d2-4d7f-b0c4-4f81d73006fd	092de09f-718a-4053-8d4b-a35dce9e76bd	rights_copyright	Crown Copyright	2026-03-02 01:56:49.462214+00
0eb02516-d84b-47a5-9e4e-182f0fd9095f	092de09f-718a-4053-8d4b-a35dce9e76bd	legal_status	Public Record(s)	2026-03-02 01:56:49.462252+00
7215f255-0adc-4b2a-a262-45e3ac432520	092de09f-718a-4053-8d4b-a35dce9e76bd	held_by	The National Archives	2026-03-02 01:56:49.462289+00
563f60ca-3ef7-46b5-a8a9-eba1e037185b	092de09f-718a-4053-8d4b-a35dce9e76bd	date_last_modified	2026-03-02T01:56:49.461957+00:00	2026-03-02 01:56:49.462323+00
0a365f6f-1229-4a08-9d52-507a845d5433	092de09f-718a-4053-8d4b-a35dce9e76bd	description	Test file for AYR development	2026-03-02 01:56:49.462358+00
ec5d06a4-8c8a-46b2-b364-67084441c1ef	092de09f-718a-4053-8d4b-a35dce9e76bd	closure_type	Open	2026-03-02 01:56:49.462393+00
e28f2659-c313-4261-bc10-dc0fc5ade59e	092de09f-718a-4053-8d4b-a35dce9e76bd	title_closed	false	2026-03-02 01:56:49.462429+00
f39a6ba6-dbbc-4ad3-affd-3873a8fc9e56	092de09f-718a-4053-8d4b-a35dce9e76bd	description_closed	false	2026-03-02 01:56:49.462466+00
bfab0cbf-f944-40fc-acfb-d441d6f03085	092de09f-718a-4053-8d4b-a35dce9e76bd	language	English	2026-03-02 01:56:49.462502+00
7215c808-5899-47ff-bcaf-fe373056dfa2	092de09f-718a-4053-8d4b-a35dce9e76bd	created_at	2026-03-02T01:56:49.461966+00:00	2026-03-02 01:56:49.462537+00
76f7aedd-4276-404a-8ee5-b6bbd7a38e84	092de09f-718a-4053-8d4b-a35dce9e76bd	last_transfer_date	2026-03-02T01:56:49.461967+00:00	2026-03-02 01:56:49.462573+00
14a257f9-3d3c-46d0-b316-c16b4326e853	092de09f-718a-4053-8d4b-a35dce9e76bd	file_format	PPTX	2026-03-02 01:56:49.462607+00
4801595d-a457-441b-8378-d2468f74d6bd	092de09f-718a-4053-8d4b-a35dce9e76bd	file_extension	pptx	2026-03-02 01:56:49.462641+00
de458aa3-b9c1-47c0-8a2a-0528f6197a12	092de09f-718a-4053-8d4b-a35dce9e76bd	closure_status	Open	2026-03-02 01:56:49.462676+00
288fa3f0-8c47-489a-bddb-bcf185c22a10	092de09f-718a-4053-8d4b-a35dce9e76bd	closure_period	0	2026-03-02 01:56:49.462711+00
04153efc-6755-445b-a45d-55fb9ad457d6	092de09f-718a-4053-8d4b-a35dce9e76bd	foi_exemption_code	None	2026-03-02 01:56:49.46275+00
7a369916-cce9-4377-869e-91133e7abef6	092de09f-718a-4053-8d4b-a35dce9e76bd	foi_exemption_code_description	None	2026-03-02 01:56:49.462786+00
58340fcd-06a8-491b-ae7d-c0a009a29cd6	092de09f-718a-4053-8d4b-a35dce9e76bd	title	Test File 10	2026-03-02 01:56:49.462825+00
67ae61a9-9e62-4c4a-b051-cc48c1a6b50c	84d189d1-695e-48c2-8eae-77301283c31e	source	test_file	2026-03-02 01:56:49.492305+00
d0237a1c-c92b-44e0-b725-cc432bdee1d1	84d189d1-695e-48c2-8eae-77301283c31e	file_name	AYR 25_ZJ56LA.rtf	2026-03-02 01:56:49.492367+00
494d158f-a843-4fc6-913e-43c3baaf65fc	84d189d1-695e-48c2-8eae-77301283c31e	file_type	File	2026-03-02 01:56:49.49241+00
13558e66-5ae1-4dde-916b-e18c3b2da2d0	84d189d1-695e-48c2-8eae-77301283c31e	file_size	1621760	2026-03-02 01:56:49.492453+00
712cf7cb-02ab-4394-b856-b19a1c1459a3	84d189d1-695e-48c2-8eae-77301283c31e	rights_copyright	Crown Copyright	2026-03-02 01:56:49.492491+00
c15fa768-13d9-4ea4-a62c-3448c9a71b0f	84d189d1-695e-48c2-8eae-77301283c31e	legal_status	Public Record(s)	2026-03-02 01:56:49.492528+00
f700296b-3fab-4c7f-a6bf-792f8891cba5	84d189d1-695e-48c2-8eae-77301283c31e	held_by	The National Archives	2026-03-02 01:56:49.492564+00
87201bd6-ae98-4b1f-ad05-70122da847f6	84d189d1-695e-48c2-8eae-77301283c31e	date_last_modified	2026-03-02T01:56:49.492292+00:00	2026-03-02 01:56:49.492601+00
7f934cf7-227d-4c2d-8e10-def47d7f5a91	84d189d1-695e-48c2-8eae-77301283c31e	description	Test file for AYR development	2026-03-02 01:56:49.492636+00
7e56dbf3-1681-4890-aab5-d86f9ab8e5e1	84d189d1-695e-48c2-8eae-77301283c31e	closure_type	Open	2026-03-02 01:56:49.49267+00
ae124478-2bc0-4073-b721-dda81e5b2ce3	84d189d1-695e-48c2-8eae-77301283c31e	title_closed	false	2026-03-02 01:56:49.492707+00
4ff23ac4-bf28-41d0-bece-ebc4f11d45bc	84d189d1-695e-48c2-8eae-77301283c31e	description_closed	false	2026-03-02 01:56:49.492743+00
743ac061-f617-4096-a3f6-14998bcd46d1	84d189d1-695e-48c2-8eae-77301283c31e	language	English	2026-03-02 01:56:49.492778+00
09c3ed88-21fa-4df6-a731-7bf13c36028e	84d189d1-695e-48c2-8eae-77301283c31e	created_at	2026-03-02T01:56:49.492300+00:00	2026-03-02 01:56:49.492813+00
c3d429c6-f24e-42c5-9f7d-88d9d201bd1d	84d189d1-695e-48c2-8eae-77301283c31e	last_transfer_date	2026-03-02T01:56:49.492301+00:00	2026-03-02 01:56:49.492848+00
b1caa5c7-9016-47e9-ba5b-7df43906656d	84d189d1-695e-48c2-8eae-77301283c31e	file_format	RTF	2026-03-02 01:56:49.492882+00
1e9b7028-8ab2-482e-8898-c0a6094642ab	84d189d1-695e-48c2-8eae-77301283c31e	file_extension	rtf	2026-03-02 01:56:49.492916+00
435558e6-2d3a-4fba-ab0f-7889537978e0	84d189d1-695e-48c2-8eae-77301283c31e	closure_status	Open	2026-03-02 01:56:49.492949+00
959ec715-360c-4c79-9145-2b13e7e42223	84d189d1-695e-48c2-8eae-77301283c31e	closure_period	0	2026-03-02 01:56:49.492984+00
d842bc63-d128-4ef4-add9-fd173f7e5a40	84d189d1-695e-48c2-8eae-77301283c31e	foi_exemption_code	None	2026-03-02 01:56:49.493018+00
4b1276c4-40b1-49df-af8f-edf864127c20	84d189d1-695e-48c2-8eae-77301283c31e	foi_exemption_code_description	None	2026-03-02 01:56:49.493052+00
3e52ff2e-f1e8-4c24-b3b5-4b254a77a4e0	84d189d1-695e-48c2-8eae-77301283c31e	title	Test File 11	2026-03-02 01:56:49.493086+00
24afc789-a527-485b-a7ee-5bdeb809794d	fa297160-2b1e-419c-b466-105f49b54d1e	source	test_file	2026-03-02 01:56:49.508217+00
1079feec-d5ed-412a-a217-6f505654d194	fa297160-2b1e-419c-b466-105f49b54d1e	file_name	AYR 25_VCT56L.tif	2026-03-02 01:56:49.508279+00
8198e60f-5d80-42e9-9032-3bb58f2c63a7	fa297160-2b1e-419c-b466-105f49b54d1e	file_type	File	2026-03-02 01:56:49.508322+00
5d14bc5f-d57f-4a4c-b012-2ce27c12ded4	fa297160-2b1e-419c-b466-105f49b54d1e	file_size	133147	2026-03-02 01:56:49.508362+00
0301dec3-bc15-45e5-b5b1-a33f2cf1b1a7	fa297160-2b1e-419c-b466-105f49b54d1e	rights_copyright	Crown Copyright	2026-03-02 01:56:49.508403+00
43801454-edc1-4d36-87fe-a4f9edaa6646	fa297160-2b1e-419c-b466-105f49b54d1e	legal_status	Public Record(s)	2026-03-02 01:56:49.508439+00
e6d36b9f-e470-4cba-97a8-73e2139e2e8b	fa297160-2b1e-419c-b466-105f49b54d1e	held_by	The National Archives	2026-03-02 01:56:49.508474+00
6e068664-f1ec-4ddb-a81e-8396402a1df0	fa297160-2b1e-419c-b466-105f49b54d1e	date_last_modified	2026-03-02T01:56:49.508204+00:00	2026-03-02 01:56:49.508512+00
45095a75-3461-4b61-ab49-1655c39404da	fa297160-2b1e-419c-b466-105f49b54d1e	description	Test file for AYR development	2026-03-02 01:56:49.508546+00
30e1924c-bd32-4276-92e2-9045ecacfdcc	fa297160-2b1e-419c-b466-105f49b54d1e	closure_type	Open	2026-03-02 01:56:49.508581+00
fc695fe9-f14a-46a1-9ad3-0be019553700	fa297160-2b1e-419c-b466-105f49b54d1e	title_closed	false	2026-03-02 01:56:49.508615+00
635ca780-c802-4095-89b0-0c20aeebb921	fa297160-2b1e-419c-b466-105f49b54d1e	description_closed	false	2026-03-02 01:56:49.508652+00
922adf16-c78a-48a8-9c3d-1f34dc2f3aaa	fa297160-2b1e-419c-b466-105f49b54d1e	language	English	2026-03-02 01:56:49.508688+00
67967cdb-a284-491c-a2ff-3c00bf43fe97	fa297160-2b1e-419c-b466-105f49b54d1e	created_at	2026-03-02T01:56:49.508211+00:00	2026-03-02 01:56:49.508723+00
703df6df-6ec1-4919-9998-e185d573795c	fa297160-2b1e-419c-b466-105f49b54d1e	last_transfer_date	2026-03-02T01:56:49.508213+00:00	2026-03-02 01:56:49.508761+00
324633ee-456a-4fc5-a5ce-ff9155018c4c	fa297160-2b1e-419c-b466-105f49b54d1e	file_format	TIF	2026-03-02 01:56:49.508825+00
841e0205-3501-4d96-8763-9ffb80a742fd	fa297160-2b1e-419c-b466-105f49b54d1e	file_extension	tif	2026-03-02 01:56:49.508861+00
8c37331b-d92e-4d6f-a3e8-a790daa77964	fa297160-2b1e-419c-b466-105f49b54d1e	closure_status	Open	2026-03-02 01:56:49.508898+00
c462d785-751e-4ac6-a654-4611317c2655	fa297160-2b1e-419c-b466-105f49b54d1e	closure_period	0	2026-03-02 01:56:49.508938+00
60e34d6e-2186-4292-8a0b-b0d214019a49	fa297160-2b1e-419c-b466-105f49b54d1e	foi_exemption_code	None	2026-03-02 01:56:49.508975+00
0c8e3138-056a-4761-82f6-3cad00a401d7	fa297160-2b1e-419c-b466-105f49b54d1e	foi_exemption_code_description	None	2026-03-02 01:56:49.509012+00
74c8be44-1b9a-4554-80eb-682f0cbdc2fd	fa297160-2b1e-419c-b466-105f49b54d1e	title	Test File 12	2026-03-02 01:56:49.509048+00
b9316bde-8428-4890-ac46-5ec8b815cfe9	9f536ef7-0100-4e57-a155-6f3c4aff6098	source	test_file	2026-03-02 01:56:49.522982+00
748e1cc2-aa8c-46ce-b076-814ee9fcbb11	9f536ef7-0100-4e57-a155-6f3c4aff6098	file_name	AYR 25_DNI76K.txt	2026-03-02 01:56:49.523055+00
b6073974-6cc4-4d31-98a3-50b941bbd26d	9f536ef7-0100-4e57-a155-6f3c4aff6098	file_type	File	2026-03-02 01:56:49.523101+00
fce41e6d-c940-4095-856a-e2344d6c6a95	9f536ef7-0100-4e57-a155-6f3c4aff6098	file_size	25975	2026-03-02 01:56:49.523144+00
b49a2f4f-6b80-4f0d-9c58-6124f31b64ff	9f536ef7-0100-4e57-a155-6f3c4aff6098	rights_copyright	Crown Copyright	2026-03-02 01:56:49.523184+00
63f90f59-affb-45ab-9e34-750cb1159f41	9f536ef7-0100-4e57-a155-6f3c4aff6098	legal_status	Public Record(s)	2026-03-02 01:56:49.523225+00
3fbc8fce-7a7d-4f1a-a01a-e2a5866ac4b9	9f536ef7-0100-4e57-a155-6f3c4aff6098	held_by	The National Archives	2026-03-02 01:56:49.523262+00
cf61ee3f-8586-440b-a919-9f220f3e0ef2	9f536ef7-0100-4e57-a155-6f3c4aff6098	date_last_modified	2026-03-02T01:56:49.522969+00:00	2026-03-02 01:56:49.5233+00
f62999a1-06e1-4d9a-bb2b-da794ae64983	9f536ef7-0100-4e57-a155-6f3c4aff6098	description	Test file for AYR development	2026-03-02 01:56:49.523336+00
ab25987a-8eec-4c65-9b4d-2e183b79ef19	9f536ef7-0100-4e57-a155-6f3c4aff6098	closure_type	Open	2026-03-02 01:56:49.523371+00
0a24df3a-c1c6-4b88-af2b-72e383420bbf	9f536ef7-0100-4e57-a155-6f3c4aff6098	title_closed	false	2026-03-02 01:56:49.523422+00
88d09b30-ed46-4b7b-9e41-696ec6646647	9f536ef7-0100-4e57-a155-6f3c4aff6098	description_closed	false	2026-03-02 01:56:49.52346+00
8274d85b-f14a-43db-b393-1d95a265b0c1	9f536ef7-0100-4e57-a155-6f3c4aff6098	language	English	2026-03-02 01:56:49.523496+00
08e5573c-9281-4e3b-8600-494c14344c47	9f536ef7-0100-4e57-a155-6f3c4aff6098	created_at	2026-03-02T01:56:49.522976+00:00	2026-03-02 01:56:49.523536+00
fd9ca6bc-5ce8-4840-bad9-271606012ceb	9f536ef7-0100-4e57-a155-6f3c4aff6098	last_transfer_date	2026-03-02T01:56:49.522977+00:00	2026-03-02 01:56:49.523573+00
d9e1e5f1-ac7f-4e66-bcf1-9bb589ba22e2	9f536ef7-0100-4e57-a155-6f3c4aff6098	file_format	TXT	2026-03-02 01:56:49.523609+00
4b44b0ed-3d32-46c1-9a70-8ef716b2fda8	9f536ef7-0100-4e57-a155-6f3c4aff6098	file_extension	txt	2026-03-02 01:56:49.523644+00
5545736d-5b9b-4776-b8d2-c55ad914a0e1	9f536ef7-0100-4e57-a155-6f3c4aff6098	closure_status	Open	2026-03-02 01:56:49.523685+00
67a3fe72-aa63-46be-a097-9f6be53f631d	9f536ef7-0100-4e57-a155-6f3c4aff6098	closure_period	0	2026-03-02 01:56:49.523726+00
734b4c4e-7a95-468e-9ec7-b46adfb61db1	9f536ef7-0100-4e57-a155-6f3c4aff6098	foi_exemption_code	None	2026-03-02 01:56:49.523774+00
6de2c7ef-25cc-4cfa-ad32-f2db2ae2b437	9f536ef7-0100-4e57-a155-6f3c4aff6098	foi_exemption_code_description	None	2026-03-02 01:56:49.52381+00
c83b57db-fc42-42a4-94e9-e65b60a1a0a2	9f536ef7-0100-4e57-a155-6f3c4aff6098	title	Test File 13	2026-03-02 01:56:49.523847+00
4fb4a37f-a321-4db0-935b-f17b949507b7	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	source	test_file	2026-03-02 01:56:49.53793+00
c9067f15-6305-4ff5-ae1b-293c2665b7a2	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	file_name	AYR 25_ZB33RH.wk1	2026-03-02 01:56:49.537992+00
bcc90c63-01b3-43d6-987e-37d803f62e9b	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	file_type	File	2026-03-02 01:56:49.538036+00
ea67b3ed-0af6-4f10-8a79-885e0ea4e9ab	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	file_size	5475	2026-03-02 01:56:49.538081+00
f0b2dea6-2934-47d7-be37-bd1f7b2eecc4	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	rights_copyright	Crown Copyright	2026-03-02 01:56:49.538121+00
80c3bba1-68ea-412d-a0a0-424b191e88e9	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	legal_status	Public Record(s)	2026-03-02 01:56:49.538159+00
95947754-9a6f-416f-b34d-73e4bd02a61e	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	held_by	The National Archives	2026-03-02 01:56:49.538196+00
99391569-d628-403f-bc3f-1432c3c6bbe9	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	date_last_modified	2026-03-02T01:56:49.537918+00:00	2026-03-02 01:56:49.538232+00
bf09e446-3c53-4d65-a487-003efdafc4f9	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	description	Test file for AYR development	2026-03-02 01:56:49.538271+00
47fc4f0a-a0a8-4753-acd5-868dd1f0d385	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	closure_type	Open	2026-03-02 01:56:49.53831+00
a92c3c62-a6cf-4b42-9f76-cafa305d10fb	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	title_closed	false	2026-03-02 01:56:49.538348+00
7f0b0072-3a2b-4ccc-ad1a-8397c2829a4e	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	description_closed	false	2026-03-02 01:56:49.538387+00
9405b818-b1bb-4fd5-8da4-a79dda40dc23	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	language	English	2026-03-02 01:56:49.538427+00
c8e65835-bca6-4d40-ae74-f46fff67b70f	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	created_at	2026-03-02T01:56:49.537925+00:00	2026-03-02 01:56:49.538463+00
eec52255-f024-4bf8-803e-1a562c799532	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	last_transfer_date	2026-03-02T01:56:49.537926+00:00	2026-03-02 01:56:49.538501+00
db1b0800-591c-4480-b6cd-e4fca01b7d29	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	file_format	WK1	2026-03-02 01:56:49.538537+00
842981e9-c4d1-4070-aa43-6ba3439722e8	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	file_extension	wk1	2026-03-02 01:56:49.538572+00
96f4573a-4b4b-49d2-bed3-d049a34794ba	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	closure_status	Open	2026-03-02 01:56:49.538607+00
be1bbe3e-4837-4a9f-850e-682a34091a28	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	closure_period	0	2026-03-02 01:56:49.538643+00
9f2e190e-b5ab-49e4-9122-d061c753b608	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	foi_exemption_code	None	2026-03-02 01:56:49.53868+00
30fd7bcc-c5b7-494f-948a-15d216c1deb9	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	foi_exemption_code_description	None	2026-03-02 01:56:49.538716+00
a4543bb0-7119-4d11-a067-3661ba6354e8	16e03988-a7ae-4198-ac8b-8d1a4c3c3c3c	title	Test File 14	2026-03-02 01:56:49.538752+00
b9ea7fff-2a26-4b7c-86dc-28b318627c81	6c3aa753-1123-455b-aaeb-d5b22e917f79	source	test_file	2026-03-02 01:56:49.562252+00
180475dc-9cec-426e-96fd-88261945b74a	6c3aa753-1123-455b-aaeb-d5b22e917f79	file_name	AYR 25_ZB33RK.wk4	2026-03-02 01:56:49.562315+00
450f99b8-1971-4f8b-a6d1-9aa2bd871c62	6c3aa753-1123-455b-aaeb-d5b22e917f79	file_type	File	2026-03-02 01:56:49.562365+00
6f6cce24-23a2-44ea-a3d3-efd879c0c1c8	6c3aa753-1123-455b-aaeb-d5b22e917f79	file_size	11264	2026-03-02 01:56:49.562405+00
f72f11bf-81cf-495d-bbad-f8872a9e9390	6c3aa753-1123-455b-aaeb-d5b22e917f79	rights_copyright	Crown Copyright	2026-03-02 01:56:49.562444+00
051f8d13-537d-4b9d-8e94-52063a76fb17	6c3aa753-1123-455b-aaeb-d5b22e917f79	legal_status	Public Record(s)	2026-03-02 01:56:49.562483+00
44487b20-d657-4a73-89f2-09a00054645d	6c3aa753-1123-455b-aaeb-d5b22e917f79	held_by	The National Archives	2026-03-02 01:56:49.562523+00
dae0267a-add5-461f-98f4-ac4dca120071	6c3aa753-1123-455b-aaeb-d5b22e917f79	date_last_modified	2026-03-02T01:56:49.562239+00:00	2026-03-02 01:56:49.562558+00
747070c4-4d3c-48dd-9ad5-ba0dfa0065ff	6c3aa753-1123-455b-aaeb-d5b22e917f79	description	Test file for AYR development	2026-03-02 01:56:49.562597+00
b159507f-ebbe-4d45-b087-bd02171410c6	6c3aa753-1123-455b-aaeb-d5b22e917f79	closure_type	Open	2026-03-02 01:56:49.562632+00
86adcb31-6d42-42e5-b079-37e0470d70bb	6c3aa753-1123-455b-aaeb-d5b22e917f79	title_closed	false	2026-03-02 01:56:49.562667+00
40263423-63e5-4e19-8a35-b3a047eba34f	6c3aa753-1123-455b-aaeb-d5b22e917f79	description_closed	false	2026-03-02 01:56:49.562703+00
8b8affdb-f3f3-4b3b-a485-4eef854eaa65	6c3aa753-1123-455b-aaeb-d5b22e917f79	language	English	2026-03-02 01:56:49.562742+00
56b11cdd-a4e3-4272-b787-a6f863cf47ce	6c3aa753-1123-455b-aaeb-d5b22e917f79	created_at	2026-03-02T01:56:49.562247+00:00	2026-03-02 01:56:49.562779+00
1e885c9a-d1ae-413a-bc95-0b6bce925c80	6c3aa753-1123-455b-aaeb-d5b22e917f79	last_transfer_date	2026-03-02T01:56:49.562248+00:00	2026-03-02 01:56:49.562815+00
8e9ef6bc-cb45-4e80-98ce-20d1cd6bdf22	6c3aa753-1123-455b-aaeb-d5b22e917f79	file_format	WK4	2026-03-02 01:56:49.56285+00
14b9e4de-0409-4d8d-9d43-a00d98231351	6c3aa753-1123-455b-aaeb-d5b22e917f79	file_extension	wk4	2026-03-02 01:56:49.562891+00
4895b7a5-5fab-419f-972e-75f7cacda372	6c3aa753-1123-455b-aaeb-d5b22e917f79	closure_status	Open	2026-03-02 01:56:49.562931+00
301b09fa-1562-425e-a01c-909bece4b017	6c3aa753-1123-455b-aaeb-d5b22e917f79	closure_period	0	2026-03-02 01:56:49.56297+00
80e41ffe-62ce-431b-95e1-a57a7b749130	6c3aa753-1123-455b-aaeb-d5b22e917f79	foi_exemption_code	None	2026-03-02 01:56:49.56301+00
8f8dabe8-a45d-4196-a995-8ce87083d5a8	6c3aa753-1123-455b-aaeb-d5b22e917f79	foi_exemption_code_description	None	2026-03-02 01:56:49.563047+00
9c9fdfcc-9a7d-4488-a72e-39a2d2c1f199	6c3aa753-1123-455b-aaeb-d5b22e917f79	title	Test File 15	2026-03-02 01:56:49.563083+00
bff0dcae-b537-438d-8b2d-108addade9b2	e9cef0ab-e553-4c69-b81e-5676d1749999	source	test_file	2026-03-02 01:56:49.576971+00
d009af14-e262-4dac-9a3c-95d5a3488c8b	e9cef0ab-e553-4c69-b81e-5676d1749999	file_name	AYR 25_Z9P523.wpd	2026-03-02 01:56:49.57704+00
e0585526-c4df-4815-92ce-85ca58873d16	e9cef0ab-e553-4c69-b81e-5676d1749999	file_size	6216	2026-03-02 01:56:49.577129+00
ef69f66e-47c5-4da0-a2a7-8f06fed36448	e9cef0ab-e553-4c69-b81e-5676d1749999	rights_copyright	Crown Copyright	2026-03-02 01:56:49.577169+00
e50fd2d8-22e1-4d84-8b54-0a50b4f59bbc	e9cef0ab-e553-4c69-b81e-5676d1749999	legal_status	Public Record(s)	2026-03-02 01:56:49.57721+00
13d1ee11-833c-436a-92e0-797a63f5c4da	e9cef0ab-e553-4c69-b81e-5676d1749999	held_by	The National Archives	2026-03-02 01:56:49.577248+00
92a1ae7f-b416-4a04-8ce4-25edcd1fa17d	e9cef0ab-e553-4c69-b81e-5676d1749999	date_last_modified	2026-03-02T01:56:49.576957+00:00	2026-03-02 01:56:49.577287+00
65e92aab-9a24-4f53-821f-11c957667005	e9cef0ab-e553-4c69-b81e-5676d1749999	description	Test file for AYR development	2026-03-02 01:56:49.577327+00
e29b450d-6946-4287-935d-cf8d1dca015b	e9cef0ab-e553-4c69-b81e-5676d1749999	closure_type	Open	2026-03-02 01:56:49.577363+00
bc182acd-468f-4320-856d-7bce564d8d19	e9cef0ab-e553-4c69-b81e-5676d1749999	title_closed	false	2026-03-02 01:56:49.577402+00
1f67f5fd-45ed-4627-aa4e-f2d8235db8b8	e9cef0ab-e553-4c69-b81e-5676d1749999	description_closed	false	2026-03-02 01:56:49.577441+00
23354f57-bd28-4bf3-8542-b9d0657e8d48	e9cef0ab-e553-4c69-b81e-5676d1749999	language	English	2026-03-02 01:56:49.577479+00
c2ad728f-e229-47be-9217-5a1b0148edd9	e9cef0ab-e553-4c69-b81e-5676d1749999	created_at	2026-03-02T01:56:49.576965+00:00	2026-03-02 01:56:49.577516+00
66803990-c8e7-4f26-a682-b9a4d03576f2	e9cef0ab-e553-4c69-b81e-5676d1749999	last_transfer_date	2026-03-02T01:56:49.576966+00:00	2026-03-02 01:56:49.577555+00
1b070238-c27c-4be2-8464-d0f969644cfe	e9cef0ab-e553-4c69-b81e-5676d1749999	file_format	WPD	2026-03-02 01:56:49.577594+00
f50ab59b-6287-4492-a8ff-b9f95b5a9d6c	e9cef0ab-e553-4c69-b81e-5676d1749999	file_extension	wpd	2026-03-02 01:56:49.577631+00
d9b2cf32-ca3e-4b0d-ba9c-cfbc7728f0e7	e9cef0ab-e553-4c69-b81e-5676d1749999	closure_status	Open	2026-03-02 01:56:49.577671+00
c6944d55-3d03-4690-aaa9-103620894adc	e9cef0ab-e553-4c69-b81e-5676d1749999	closure_period	0	2026-03-02 01:56:49.577709+00
22d8a001-cddc-4ced-92b5-0f1170d53316	e9cef0ab-e553-4c69-b81e-5676d1749999	foi_exemption_code	None	2026-03-02 01:56:49.577751+00
214de514-b0c0-422b-9182-fb6ed2284a44	e9cef0ab-e553-4c69-b81e-5676d1749999	foi_exemption_code_description	None	2026-03-02 01:56:49.577788+00
001a936b-69a2-40b5-81e6-3e025cb062a1	e9cef0ab-e553-4c69-b81e-5676d1749999	title	Test File 16	2026-03-02 01:56:49.577826+00
3342e4be-7153-4f87-8c5b-db9476f3fb1b	451ef2a4-717c-4c5d-b27b-d3904628c3ef	source	test_file	2026-03-02 01:56:49.593139+00
c45c6526-c53d-4cd9-8fe6-7af4d8e6a557	451ef2a4-717c-4c5d-b27b-d3904628c3ef	file_name	AYR 25_VTC9WP.xls	2026-03-02 01:56:49.5932+00
beecbf81-64b5-449a-829a-ef3aedeb9af9	451ef2a4-717c-4c5d-b27b-d3904628c3ef	file_type	File	2026-03-02 01:56:49.593245+00
52302468-a360-4772-889e-333eb2c178c6	451ef2a4-717c-4c5d-b27b-d3904628c3ef	file_size	16652	2026-03-02 01:56:49.593288+00
72c1d6b8-9823-4eef-ad89-8c1d9b0b4b82	451ef2a4-717c-4c5d-b27b-d3904628c3ef	rights_copyright	Crown Copyright	2026-03-02 01:56:49.593327+00
d96cf4e7-1451-4b94-ad55-fe1a53ab70b2	451ef2a4-717c-4c5d-b27b-d3904628c3ef	legal_status	Public Record(s)	2026-03-02 01:56:49.593363+00
5591dd59-e54b-4eb0-9a13-b3c90f8e8275	451ef2a4-717c-4c5d-b27b-d3904628c3ef	held_by	The National Archives	2026-03-02 01:56:49.593401+00
8342e82f-e1ae-46d7-8340-c179792776d5	451ef2a4-717c-4c5d-b27b-d3904628c3ef	date_last_modified	2026-03-02T01:56:49.593127+00:00	2026-03-02 01:56:49.593436+00
10a0aaef-c763-4cfb-99f8-b9c1cbfc58c7	451ef2a4-717c-4c5d-b27b-d3904628c3ef	description	Test file for AYR development	2026-03-02 01:56:49.593471+00
f4908ca2-c28a-43b1-8bbe-e15596c9cbf9	451ef2a4-717c-4c5d-b27b-d3904628c3ef	closure_type	Open	2026-03-02 01:56:49.593505+00
0e631de3-5ecd-417e-bada-fa77651f85ce	451ef2a4-717c-4c5d-b27b-d3904628c3ef	title_closed	false	2026-03-02 01:56:49.593537+00
f40748f2-f71e-4166-ab75-42c08adefcde	451ef2a4-717c-4c5d-b27b-d3904628c3ef	description_closed	false	2026-03-02 01:56:49.593571+00
fed77561-f9ee-4c44-b19b-926c57e2501a	451ef2a4-717c-4c5d-b27b-d3904628c3ef	language	English	2026-03-02 01:56:49.593606+00
a041b529-71da-46cb-b07b-1a2c37c50087	451ef2a4-717c-4c5d-b27b-d3904628c3ef	created_at	2026-03-02T01:56:49.593134+00:00	2026-03-02 01:56:49.59364+00
a6c02074-5706-492e-9415-c399bc2c0ce4	451ef2a4-717c-4c5d-b27b-d3904628c3ef	last_transfer_date	2026-03-02T01:56:49.593135+00:00	2026-03-02 01:56:49.593674+00
e96e89e8-50f2-48db-831a-4ba8cee30d37	451ef2a4-717c-4c5d-b27b-d3904628c3ef	file_format	XLS	2026-03-02 01:56:49.593706+00
3dd4fa2b-2999-415f-82e3-a7c0dce61379	451ef2a4-717c-4c5d-b27b-d3904628c3ef	file_extension	xls	2026-03-02 01:56:49.593739+00
bc137399-b6f4-4471-a4e1-9ffc8d7344df	451ef2a4-717c-4c5d-b27b-d3904628c3ef	closure_status	Open	2026-03-02 01:56:49.593772+00
7a310a97-6a19-4e6a-ba09-bc5738b3f431	451ef2a4-717c-4c5d-b27b-d3904628c3ef	closure_period	0	2026-03-02 01:56:49.593805+00
ca079a72-cdee-49ae-9dd7-f11d36bb0866	451ef2a4-717c-4c5d-b27b-d3904628c3ef	foi_exemption_code	None	2026-03-02 01:56:49.593842+00
593e138b-3beb-47cf-aaf2-b0006d02a2ac	451ef2a4-717c-4c5d-b27b-d3904628c3ef	foi_exemption_code_description	None	2026-03-02 01:56:49.593875+00
d9e794f4-82e3-4047-9c93-823e31cf89b6	451ef2a4-717c-4c5d-b27b-d3904628c3ef	title	Test File 17	2026-03-02 01:56:49.593909+00
7693ce42-54ee-41b6-b59a-9b13aa81c4e9	aa42b744-e64e-489c-95ac-a62927e5716c	source	test_file	2026-03-02 01:56:49.60919+00
45d3e23f-1770-4b4c-abd2-f4fc532f7b3b	aa42b744-e64e-489c-95ac-a62927e5716c	file_name	AYR 25_UYT6DV.xlsx	2026-03-02 01:56:49.609255+00
bd68aa74-0b3b-458c-a3b6-03dcb89c85c2	aa42b744-e64e-489c-95ac-a62927e5716c	file_type	File	2026-03-02 01:56:49.609301+00
bdf25684-e5b2-4bf2-ad92-e1783888653e	aa42b744-e64e-489c-95ac-a62927e5716c	file_size	16652	2026-03-02 01:56:49.609343+00
12a7f78a-077c-40bb-af00-ed21fcc9bc07	aa42b744-e64e-489c-95ac-a62927e5716c	rights_copyright	Crown Copyright	2026-03-02 01:56:49.609384+00
8c0d4e54-bd87-41bb-8c04-2eed693f3e85	aa42b744-e64e-489c-95ac-a62927e5716c	legal_status	Public Record(s)	2026-03-02 01:56:49.609423+00
79759561-386a-4018-8026-36436421291f	aa42b744-e64e-489c-95ac-a62927e5716c	held_by	The National Archives	2026-03-02 01:56:49.60946+00
7ea3f718-bb3b-410f-9e56-d12e4b0f8c2c	aa42b744-e64e-489c-95ac-a62927e5716c	date_last_modified	2026-03-02T01:56:49.609176+00:00	2026-03-02 01:56:49.609498+00
809639fe-93ed-4a85-9ab9-4a1c3787d5ca	aa42b744-e64e-489c-95ac-a62927e5716c	description	Test file for AYR development	2026-03-02 01:56:49.609533+00
c9157f48-beb0-4f67-9822-a8f375d3c180	aa42b744-e64e-489c-95ac-a62927e5716c	closure_type	Open	2026-03-02 01:56:49.609569+00
8e32d9b5-e3cc-4429-8ab9-c2dd88d4941e	aa42b744-e64e-489c-95ac-a62927e5716c	title_closed	false	2026-03-02 01:56:49.609602+00
e9e2d517-24d1-46b6-90ef-551bb1cf1fd4	aa42b744-e64e-489c-95ac-a62927e5716c	description_closed	false	2026-03-02 01:56:49.609639+00
49d7b4a4-8230-49e9-a172-6dde71b12c1a	aa42b744-e64e-489c-95ac-a62927e5716c	language	English	2026-03-02 01:56:49.609675+00
afaf7079-9ad7-4402-b433-dc5c09ed3839	aa42b744-e64e-489c-95ac-a62927e5716c	created_at	2026-03-02T01:56:49.609184+00:00	2026-03-02 01:56:49.60971+00
fb0f5e6a-951d-4d6b-ab74-efb47815f22b	aa42b744-e64e-489c-95ac-a62927e5716c	last_transfer_date	2026-03-02T01:56:49.609185+00:00	2026-03-02 01:56:49.609748+00
8899e634-910c-4c79-883e-1d9ee69253b8	aa42b744-e64e-489c-95ac-a62927e5716c	file_format	XLSX	2026-03-02 01:56:49.609783+00
cf6113f0-e73a-4d30-954a-a04844b69cca	aa42b744-e64e-489c-95ac-a62927e5716c	file_extension	xlsx	2026-03-02 01:56:49.609816+00
d62a4eeb-d330-485a-8c49-44d655328483	aa42b744-e64e-489c-95ac-a62927e5716c	closure_status	Open	2026-03-02 01:56:49.60985+00
c69b694b-6265-460a-9812-95f06b137980	aa42b744-e64e-489c-95ac-a62927e5716c	closure_period	0	2026-03-02 01:56:49.609884+00
5e78597d-0e4b-48fc-9220-fd0e2071f027	aa42b744-e64e-489c-95ac-a62927e5716c	foi_exemption_code	None	2026-03-02 01:56:49.60992+00
184d087a-3eea-47ea-b49a-75acd32fe533	aa42b744-e64e-489c-95ac-a62927e5716c	foi_exemption_code_description	None	2026-03-02 01:56:49.609956+00
6f5b7f8f-63b6-48d5-92db-ba2117b2529b	aa42b744-e64e-489c-95ac-a62927e5716c	title	Test File 18	2026-03-02 01:56:49.60999+00
6dad3e7f-85b6-468c-bafe-0d0598e32f47	f43b4d4d-569a-46b2-98d4-8dec2df46966	source	test_file	2026-03-02 01:56:49.623125+00
471831e5-019b-4e16-b7b6-7b01434d641b	f43b4d4d-569a-46b2-98d4-8dec2df46966	file_name	AYR 25_Z9P524.xml	2026-03-02 01:56:49.623185+00
cd714be0-d685-4736-bf75-49165f2ad6dd	f43b4d4d-569a-46b2-98d4-8dec2df46966	file_type	File	2026-03-02 01:56:49.623227+00
65d271b2-022c-47df-a745-11dace04e917	f43b4d4d-569a-46b2-98d4-8dec2df46966	file_size	7787	2026-03-02 01:56:49.623269+00
c0fd33d2-95b2-4eec-be3c-0025f8adf2ab	f43b4d4d-569a-46b2-98d4-8dec2df46966	rights_copyright	Crown Copyright	2026-03-02 01:56:49.623312+00
35b66cbd-848c-4dcd-a76f-c33605f6ca98	f43b4d4d-569a-46b2-98d4-8dec2df46966	legal_status	Public Record(s)	2026-03-02 01:56:49.623348+00
dd6e3e74-156c-4288-9ee9-213ae83db461	f43b4d4d-569a-46b2-98d4-8dec2df46966	held_by	The National Archives	2026-03-02 01:56:49.623383+00
562417e0-2c51-42bd-9610-d68110338b05	f43b4d4d-569a-46b2-98d4-8dec2df46966	date_last_modified	2026-03-02T01:56:49.623113+00:00	2026-03-02 01:56:49.623466+00
8d6fad87-3fd4-480e-96b0-3ab391184917	f43b4d4d-569a-46b2-98d4-8dec2df46966	description	Test file for AYR development	2026-03-02 01:56:49.623526+00
a376b92b-90ad-495c-81d8-93be75a1261b	f43b4d4d-569a-46b2-98d4-8dec2df46966	closure_type	Open	2026-03-02 01:56:49.623571+00
aaddd99d-df65-4d55-aedd-8ca0710bcf48	f43b4d4d-569a-46b2-98d4-8dec2df46966	title_closed	false	2026-03-02 01:56:49.623614+00
75f609bd-4e18-4607-8191-f0572c7bdaf0	f43b4d4d-569a-46b2-98d4-8dec2df46966	description_closed	false	2026-03-02 01:56:49.623654+00
59a2c402-27f3-42c2-8de0-9522579a9f39	f43b4d4d-569a-46b2-98d4-8dec2df46966	language	English	2026-03-02 01:56:49.623692+00
e7a3ae48-d63a-4216-a4e4-571744aecffb	f43b4d4d-569a-46b2-98d4-8dec2df46966	created_at	2026-03-02T01:56:49.623119+00:00	2026-03-02 01:56:49.62373+00
d7761462-ccff-4662-be7a-5e11c6dcf946	f43b4d4d-569a-46b2-98d4-8dec2df46966	last_transfer_date	2026-03-02T01:56:49.623121+00:00	2026-03-02 01:56:49.623768+00
b7196076-4e0f-4901-8f66-3b2a4993967a	f43b4d4d-569a-46b2-98d4-8dec2df46966	file_format	XML	2026-03-02 01:56:49.623833+00
3d005276-31fb-4c3a-961e-2699baba5720	f43b4d4d-569a-46b2-98d4-8dec2df46966	file_extension	xml	2026-03-02 01:56:49.623909+00
4d4e2f52-dfdb-4f80-bec2-3a244dd7342f	f43b4d4d-569a-46b2-98d4-8dec2df46966	closure_status	Open	2026-03-02 01:56:49.623962+00
b4352e1c-586f-4fd1-a759-fdef26c3caac	f43b4d4d-569a-46b2-98d4-8dec2df46966	closure_period	0	2026-03-02 01:56:49.624005+00
716f6c0c-487e-4a44-aca7-1eae18f1dead	f43b4d4d-569a-46b2-98d4-8dec2df46966	foi_exemption_code	None	2026-03-02 01:56:49.624048+00
c77684f4-2db9-4cae-9e7a-8e0790bd415f	f43b4d4d-569a-46b2-98d4-8dec2df46966	foi_exemption_code_description	None	2026-03-02 01:56:49.624087+00
aef1ca89-75b7-41fc-939c-a2b53fe2127a	f43b4d4d-569a-46b2-98d4-8dec2df46966	title	Test File 19	2026-03-02 01:56:49.624126+00
\.


--
-- Data for Name: Series; Type: TABLE DATA; Schema: public; Owner: local_db_user
--

COPY public."Series" ("SeriesId", "BodyId", "Name", "Description") FROM stdin;
93ed0101-2318-45ab-8730-c681958ded7e	4654e9f9-335b-4ab1-acd8-edff54f908d4	AYR 1	AYR 1
8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	8ccc8cd1-c0ee-431d-afad-70cf404ba337	MOCK1 123	MOCK1 123
1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	TSTA 1	TSTA 1
0c94b4be-80da-4c29-b03b-e8920689fa4f	1dafba21-4ba1-4ad0-91e7-6de105dddb67	SCOT 13	Test Series Description
\.


--
-- Name: Body Body_pkey; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Body"
    ADD CONSTRAINT "Body_pkey" PRIMARY KEY ("BodyId");


--
-- Name: Consignment Consignment_pkey; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT "Consignment_pkey" PRIMARY KEY ("ConsignmentId");


--
-- Name: FileMetadata FileMetadata_pkey; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."FileMetadata"
    ADD CONSTRAINT "FileMetadata_pkey" PRIMARY KEY ("MetadataId");


--
-- Name: File File_pkey; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT "File_pkey" PRIMARY KEY ("FileId");


--
-- Name: Series Series_pkey; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Series"
    ADD CONSTRAINT "Series_pkey" PRIMARY KEY ("SeriesId");


--
-- Name: Body body_name_unq; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Body"
    ADD CONSTRAINT body_name_unq UNIQUE ("Name");


--
-- Name: File consignment_filepath_unq; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT consignment_filepath_unq UNIQUE ("ConsignmentId", "FilePath");


--
-- Name: FileMetadata fileid_property_value_unq; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."FileMetadata"
    ADD CONSTRAINT fileid_property_value_unq UNIQUE ("FileId", "PropertyName", "Value");


--
-- Name: Consignment reference_unique; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT reference_unique UNIQUE ("ConsignmentReference");


--
-- Name: Series series_name_unq; Type: CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Series"
    ADD CONSTRAINT series_name_unq UNIQUE ("Name");


--
-- Name: File FK_File.ConsignmentId; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT "FK_File.ConsignmentId" FOREIGN KEY ("ConsignmentId") REFERENCES public."Consignment"("ConsignmentId");


--
-- Name: AVMetadata avmetadata_fileid_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."AVMetadata"
    ADD CONSTRAINT avmetadata_fileid_file_fkey FOREIGN KEY ("FileId") REFERENCES public."File"("FileId");


--
-- Name: Consignment consignment_bodyid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT consignment_bodyid_fkey FOREIGN KEY ("BodyId") REFERENCES public."Body"("BodyId");


--
-- Name: Consignment consignment_seriesid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT consignment_seriesid_fkey FOREIGN KEY ("SeriesId") REFERENCES public."Series"("SeriesId");


--
-- Name: FFIDMetadata ffidmetadata_fileid_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."FFIDMetadata"
    ADD CONSTRAINT ffidmetadata_fileid_file_fkey FOREIGN KEY ("FileId") REFERENCES public."File"("FileId");


--
-- Name: FileMetadata filemetadata_fileid_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."FileMetadata"
    ADD CONSTRAINT filemetadata_fileid_file_fkey FOREIGN KEY ("FileId") REFERENCES public."File"("FileId");


--
-- Name: Series series_bodyid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: local_db_user
--

ALTER TABLE ONLY public."Series"
    ADD CONSTRAINT series_bodyid_fkey FOREIGN KEY ("BodyId") REFERENCES public."Body"("BodyId");


--
-- PostgreSQL database dump complete
--

\unrestrict 7gWCH43hGT7z9GcO102mxHiIE8qIghELLsPOZfSW2XWne7HDJflwy9NZvKzpbOE
