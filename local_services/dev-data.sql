--
-- PostgreSQL database dump
--

-- Dumped from database version 18.1 (Debian 18.1-1.pgdg13+2)
-- Dumped by pg_dump version 18.1

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
-- Name: EXTENSION tablefunc; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION tablefunc IS 'functions that manipulate whole tables, including crosstab';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: AVMetadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."AVMetadata" (
    "FileId" uuid NOT NULL,
    "AV-Software" text,
    "AV-SoftwareVersion" text
);


--
-- Name: Body; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Body" (
    "BodyId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "Name" text NOT NULL,
    "Description" text
);


--
-- Name: Consignment; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: FFIDMetadata; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: File; Type: TABLE; Schema: public; Owner: -
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


--
-- Name: FileMetadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."FileMetadata" (
    "MetadataId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "FileId" uuid,
    "PropertyName" text,
    "Value" text,
    "CreatedDatetime" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: Series; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."Series" (
    "SeriesId" uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "BodyId" uuid,
    "Name" text NOT NULL,
    "Description" text
);


--
-- Data for Name: AVMetadata; Type: TABLE DATA; Schema: public; Owner: -
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
-- Data for Name: Body; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."Body" ("BodyId", "Name", "Description") FROM stdin;
4654e9f9-335b-4ab1-acd8-edff54f908d4	AYR Test Data Department	AYR Test Data Department
8ccc8cd1-c0ee-431d-afad-70cf404ba337	Mock 1 Department	Mock 1 Department
c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	Testing A	Testing A
9ced8d31-ea58-4794-9582-4b4de1409d59	MOCK1 Department	MOCK1 Department
05b7267f-a0c8-47dc-b062-f04bff369fea	Test Transferring Body	Test Transferring Body Description
\.


--
-- Data for Name: Consignment; Type: TABLE DATA; Schema: public; Owner: -
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
bfd487c4-068a-4463-a0ed-315efa4842dc	\N	e43c4f33-bad8-4f58-9423-6bb2d5598194	AYR-2025-ESA6	Test	t	Test User	test@example.com	2025-11-19 14:18:49.804293+00	2015-02-20 10:47:41.150927+00	2000-01-03 09:35:43.853047+00	2025-11-19 14:18:49.804294+00
\.


--
-- Data for Name: FFIDMetadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."FFIDMetadata" ("FileId", "Extension", "PUID", "FormatName", "ExtensionMismatch", "FFID-Software", "FFID-SoftwareVersion", "FFID-BinarySignatureFileVersion", "FFID-ContainerSignatureFileVersion") FROM stdin;
5e1e2f6c-f6db-40fb-a83b-c2c33aaeb024	png	x-fmt/11	Portable Network Graphics (PNG)	    false	Droid	6.7.0	11	20230822
5458dc04-8a9d-42c4-bb5e-8239b92eb120	gif	x-fmt/3	Graphics Interchange Format (GIF)	false	Droid	6.7.0	111	20230822
123e4567-e89b-12d3-a456-426614174000	webp	fmt/278	WebP Image	false	Droid	6.7.0	111	20230822
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
14206664-7c1c-4277-a7ca-8911785d417e	txt	SPLxrUcQ	JPEG Image	false	DROID	MaAmH	PmQsM	KOHGm
75bc52b5-2858-4e00-be65-c97b1ef06fb3	pdf	qcpyYjic	Word Document	true	Siegfried	Pqqdw	WKMko	AJqHe
4c050849-d396-4167-83d4-180cf8888ef2	docx	xCuzWiSJ	Adobe PDF	false	Siegfried	yPKEn	jAsYH	KiDvj
657c62b7-aed1-4fdd-9ca5-059835f7047c	txt	Owkonzil	Plain Text	true	DROID	oIvUH	kBkGA	WKIvf
64ab4d01-56a5-4601-9119-fe7c38d6796e	pdf	JVVvHLQI	Plain Text	true	Siegfried	FOxVn	cumZU	mynKK
dd2f4484-243f-4a30-9dc9-c9006e87a744	docx	KUoiFzHj	JPEG Image	true	DROID	ybaJS	SZwMI	ViKYo
3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	docx	afNzDfKI	Plain Text	false	Siegfried	dsyvW	roeaK	PqaTx
c76c647f-bf99-44de-b7ca-26329ae56e82	jpg	psmRCkTX	Plain Text	false	Siegfried	DdFrd	gqlAG	wvIFc
a851b362-d00e-4a3e-9745-7325aefeff9d	txt	QCtJltPS	Plain Text	false	DROID	xoNQk	PvjKx	pzAhb
f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	docx	PjOPqyWI	Adobe PDF	false	Siegfried	hyWHP	XJyhn	bvOra
acf6733e-587b-4fe8-b1d8-f678271b2786	jpg	lWUkdWmT	JPEG Image	false	DROID	VLAlh	QufQH	aqXTD
f52ff646-9f9f-4261-a495-2806894684e6	jpg	HHQDWSxw	JPEG Image	true	Siegfried	sYSyE	UxUFM	OYVjE
56809bd9-060a-421b-9d0b-d77e52e151e4	pdf	SUayYbDD	Adobe PDF	false	DROID	glPDQ	RbGqT	jMIua
c83d1866-f1ae-479b-b770-3117a12c4c65	txt	bpBaVRdg	Adobe PDF	true	Siegfried	AMjYn	UdvFE	LGdlF
\.


--
-- Data for Name: File; Type: TABLE DATA; Schema: public; Owner: -
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
14206664-7c1c-4277-a7ca-8911785d417e	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZDC8J4.docx	bfd487c4-068a-4463-a0ed-315efa4842dc/14206664-7c1c-4277-a7ca-8911785d417e/SCOT 13_ZDC8J4.docx	14206664-7c1c-4277-a7ca-8911785d417e	cKIZeKRQYU	\N	\N	XiIitkCiVz	2025-11-19 14:18:49.962939+00
75bc52b5-2858-4e00-be65-c97b1ef06fb3	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZDKL26.pdf	bfd487c4-068a-4463-a0ed-315efa4842dc/75bc52b5-2858-4e00-be65-c97b1ef06fb3/SCOT 13_ZDKL26.pdf	75bc52b5-2858-4e00-be65-c97b1ef06fb3	OnNiwigLeT	\N	\N	EoLgJFGqkt	2025-11-19 14:18:50.046188+00
4c050849-d396-4167-83d4-180cf8888ef2	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZB33RH.wk1	bfd487c4-068a-4463-a0ed-315efa4842dc/4c050849-d396-4167-83d4-180cf8888ef2/SCOT 13_ZB33RH.wk1	4c050849-d396-4167-83d4-180cf8888ef2	TbovVruPUX	\N	\N	gPOWYORPWY	2025-11-19 14:18:50.071382+00
657c62b7-aed1-4fdd-9ca5-059835f7047c	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZFW6DB.doc	bfd487c4-068a-4463-a0ed-315efa4842dc/657c62b7-aed1-4fdd-9ca5-059835f7047c/SCOT 13_ZFW6DB.doc	657c62b7-aed1-4fdd-9ca5-059835f7047c	oZwgHoLSaO	\N	\N	ftRonSmDdb	2025-11-19 14:18:50.156919+00
64ab4d01-56a5-4601-9119-fe7c38d6796e	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_Z9P4WW.odt	bfd487c4-068a-4463-a0ed-315efa4842dc/64ab4d01-56a5-4601-9119-fe7c38d6796e/SCOT 13_Z9P4WW.odt	64ab4d01-56a5-4601-9119-fe7c38d6796e	jwWLBrMqMV	\N	\N	sXDbfSMRkF	2025-11-19 14:18:50.209513+00
dd2f4484-243f-4a30-9dc9-c9006e87a744	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZJ56LA.rtf	bfd487c4-068a-4463-a0ed-315efa4842dc/dd2f4484-243f-4a30-9dc9-c9006e87a744/SCOT 13_ZJ56LA.rtf	dd2f4484-243f-4a30-9dc9-c9006e87a744	eickaoQCCi	\N	\N	yKMjRTKqdZ	2025-11-19 14:18:50.227562+00
3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_DNI76K.txt	bfd487c4-068a-4463-a0ed-315efa4842dc/3e4ec2b8-b06a-49d2-9604-9b42be8bbf85/SCOT 13_DNI76K.txt	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	TXmYZTKIcb	\N	\N	mSTVCfHGEL	2025-11-19 14:18:50.241942+00
c76c647f-bf99-44de-b7ca-26329ae56e82	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZG8SKW.pptx	bfd487c4-068a-4463-a0ed-315efa4842dc/c76c647f-bf99-44de-b7ca-26329ae56e82/SCOT 13_ZG8SKW.pptx	c76c647f-bf99-44de-b7ca-26329ae56e82	qMdPAQKEeR	\N	\N	fZxEqyyewf	2025-11-19 14:18:50.344767+00
a851b362-d00e-4a3e-9745-7325aefeff9d	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_ZB33RK.wk4	bfd487c4-068a-4463-a0ed-315efa4842dc/a851b362-d00e-4a3e-9745-7325aefeff9d/SCOT 13_ZB33RK.wk4	a851b362-d00e-4a3e-9745-7325aefeff9d	INGAuEClNs	\N	\N	mOhlrGPEQo	2025-11-19 14:18:50.362459+00
f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_Z9P523.html	bfd487c4-068a-4463-a0ed-315efa4842dc/f39b7792-eeb9-4bf9-8eac-f4084b7ed18e/SCOT 13_Z9P523.html	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	txXvbFFyHJ	\N	\N	sjFAWlEFwK	2025-11-19 14:18:50.384278+00
acf6733e-587b-4fe8-b1d8-f678271b2786	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_VTC9WP.xls	bfd487c4-068a-4463-a0ed-315efa4842dc/acf6733e-587b-4fe8-b1d8-f678271b2786/SCOT 13_VTC9WP.xls	acf6733e-587b-4fe8-b1d8-f678271b2786	MuVMSOBMTm	\N	\N	VMWSrSvnYw	2025-11-19 14:18:50.399838+00
f52ff646-9f9f-4261-a495-2806894684e6	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_Z9P524.xml	bfd487c4-068a-4463-a0ed-315efa4842dc/f52ff646-9f9f-4261-a495-2806894684e6/SCOT 13_Z9P524.xml	f52ff646-9f9f-4261-a495-2806894684e6	HnfMeTVkqL	\N	\N	UdyzODsmrH	2025-11-19 14:18:50.41554+00
56809bd9-060a-421b-9d0b-d77e52e151e4	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_Z95P37.ppt	bfd487c4-068a-4463-a0ed-315efa4842dc/56809bd9-060a-421b-9d0b-d77e52e151e4/SCOT 13_Z95P37.ppt	56809bd9-060a-421b-9d0b-d77e52e151e4	ZwErQbMMGp	\N	\N	KXZabigrJJ	2025-11-19 14:18:50.439834+00
c83d1866-f1ae-479b-b770-3117a12c4c65	bfd487c4-068a-4463-a0ed-315efa4842dc	File	SCOT 13_UYT6DV.xlsx	bfd487c4-068a-4463-a0ed-315efa4842dc/c83d1866-f1ae-479b-b770-3117a12c4c65/SCOT 13_UYT6DV.xlsx	c83d1866-f1ae-479b-b770-3117a12c4c65	hbqdgWWkeJ	\N	\N	DpihWdHsGN	2025-11-19 14:18:50.4574+00
\.


--
-- Data for Name: FileMetadata; Type: TABLE DATA; Schema: public; Owner: -
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
b4f58fd4-c8d8-4307-8943-1451c1f33ce5	14206664-7c1c-4277-a7ca-8911785d417e	source	test_file	2025-11-19 14:18:49.963332+00
280cab04-0d47-4772-8a81-105503a725b0	14206664-7c1c-4277-a7ca-8911785d417e	file_type	docx	2025-11-19 14:18:49.963503+00
c1445ab1-5cfc-4296-94a3-56ad3751eb33	14206664-7c1c-4277-a7ca-8911785d417e	created_at	2025-11-19T14:18:49.963294+00:00	2025-11-19 14:18:49.963565+00
41622388-3928-4bde-92a4-cbb35df7777c	14206664-7c1c-4277-a7ca-8911785d417e	last_transfer_date	2025-11-19T14:18:49.963301+00:00	2025-11-19 14:18:49.963607+00
1e51051d-7030-4902-b2fc-0c9a1cafd0e8	14206664-7c1c-4277-a7ca-8911785d417e	file_size	8558	2025-11-19 14:18:49.963645+00
cf577b77-4106-48db-8a2d-2ec114e7deab	14206664-7c1c-4277-a7ca-8911785d417e	file_format	DOCX	2025-11-19 14:18:49.963683+00
eb5f032c-acdf-4a20-822e-b245b843b62c	14206664-7c1c-4277-a7ca-8911785d417e	file_extension	docx	2025-11-19 14:18:49.963719+00
d22675ce-b280-43eb-8a51-085e49822a7e	14206664-7c1c-4277-a7ca-8911785d417e	mime_type	application/vnd.openxmlformats-officedocument.wordprocessingml.document	2025-11-19 14:18:49.96376+00
5e191d58-03ce-442a-a5b8-1d3158a34825	14206664-7c1c-4277-a7ca-8911785d417e	closure_status	Open	2025-11-19 14:18:49.963797+00
e568b9ac-797f-4cfd-aab2-38e67998967b	14206664-7c1c-4277-a7ca-8911785d417e	closure_type	Open	2025-11-19 14:18:49.963832+00
b47ec979-9a49-40cc-bd2a-3b0b465a38d3	14206664-7c1c-4277-a7ca-8911785d417e	closure_period	0	2025-11-19 14:18:49.963867+00
bda70389-3f42-4b6f-b8cd-024e679df91a	14206664-7c1c-4277-a7ca-8911785d417e	foi_exemption_code	None	2025-11-19 14:18:49.963901+00
d790b748-fb9a-4428-ad73-6e73f2c1f945	14206664-7c1c-4277-a7ca-8911785d417e	foi_exemption_code_description	None	2025-11-19 14:18:49.963936+00
ecdabe7d-cdcd-4a15-9106-cec9de305fae	14206664-7c1c-4277-a7ca-8911785d417e	title	Test File 1	2025-11-19 14:18:49.963973+00
d14bcbee-ff6f-4b8c-a829-e4db7a9afff8	14206664-7c1c-4277-a7ca-8911785d417e	description	Test file for AYR development	2025-11-19 14:18:49.964007+00
cce3e80b-9889-46d3-acb6-0947adb25254	14206664-7c1c-4277-a7ca-8911785d417e	language	English	2025-11-19 14:18:49.96404+00
2def5a1b-9ba6-4f80-bed1-d912a72bddda	14206664-7c1c-4277-a7ca-8911785d417e	security_classification	Open	2025-11-19 14:18:49.964074+00
3290a7ae-30ea-4ef1-b570-f926f49f9e95	14206664-7c1c-4277-a7ca-8911785d417e	copyright_status	Crown Copyright	2025-11-19 14:18:49.964109+00
23819cdd-f6e3-46d5-94f2-9c163c3bc7b8	14206664-7c1c-4277-a7ca-8911785d417e	legal_status	Public Record	2025-11-19 14:18:49.964142+00
c530d7f8-8793-4946-bf24-11aeda0ca576	75bc52b5-2858-4e00-be65-c97b1ef06fb3	source	test_file	2025-11-19 14:18:50.046542+00
d093c905-d450-486a-b720-6792a618ca43	75bc52b5-2858-4e00-be65-c97b1ef06fb3	file_type	pdf	2025-11-19 14:18:50.046613+00
d7d6aafb-e5b2-47d3-84c7-0d51ce7c11c9	75bc52b5-2858-4e00-be65-c97b1ef06fb3	created_at	2025-11-19T14:18:50.046502+00:00	2025-11-19 14:18:50.046657+00
c445f449-dde7-409e-a634-f9e6c8b622d1	75bc52b5-2858-4e00-be65-c97b1ef06fb3	last_transfer_date	2025-11-19T14:18:50.046510+00:00	2025-11-19 14:18:50.046698+00
357e02c2-ff49-4d90-876b-624ae9c61606	75bc52b5-2858-4e00-be65-c97b1ef06fb3	file_size	6726645	2025-11-19 14:18:50.04674+00
9f0aac9d-6ace-4e8c-a2a0-d920e1b83f16	75bc52b5-2858-4e00-be65-c97b1ef06fb3	file_format	PDF	2025-11-19 14:18:50.046778+00
5ff80675-39ca-405c-b214-fc0dc80dad9e	75bc52b5-2858-4e00-be65-c97b1ef06fb3	file_extension	pdf	2025-11-19 14:18:50.046815+00
8ffeaabf-646b-4647-8ba8-897cbd92523d	75bc52b5-2858-4e00-be65-c97b1ef06fb3	mime_type	application/pdf	2025-11-19 14:18:50.046852+00
3635dd52-fc5f-4dc2-a6c2-ce64d21a7a73	75bc52b5-2858-4e00-be65-c97b1ef06fb3	closure_status	Open	2025-11-19 14:18:50.046885+00
d78c69c0-555d-45c0-9ea9-6f1bac58ae80	75bc52b5-2858-4e00-be65-c97b1ef06fb3	closure_type	Open	2025-11-19 14:18:50.04692+00
c2ba374f-709d-4614-99bb-2c13c63273c4	75bc52b5-2858-4e00-be65-c97b1ef06fb3	closure_period	0	2025-11-19 14:18:50.046954+00
60192098-9a22-4e08-8e7b-fb3cc9e42a75	75bc52b5-2858-4e00-be65-c97b1ef06fb3	foi_exemption_code	None	2025-11-19 14:18:50.046989+00
7836ade9-2b90-4851-93fa-cf40534143d5	75bc52b5-2858-4e00-be65-c97b1ef06fb3	foi_exemption_code_description	None	2025-11-19 14:18:50.047024+00
d515d53c-c439-4a3a-828b-e4ee77c6d090	75bc52b5-2858-4e00-be65-c97b1ef06fb3	title	Test File 2	2025-11-19 14:18:50.04706+00
bb32dd83-f665-4934-9b65-52416d067c3c	75bc52b5-2858-4e00-be65-c97b1ef06fb3	description	Test file for AYR development	2025-11-19 14:18:50.047095+00
12ff0640-8939-4132-9da6-4f40afed1238	75bc52b5-2858-4e00-be65-c97b1ef06fb3	language	English	2025-11-19 14:18:50.047128+00
a257ce2d-63f9-448e-972a-56babd484f1d	75bc52b5-2858-4e00-be65-c97b1ef06fb3	security_classification	Open	2025-11-19 14:18:50.04716+00
55d8d17e-2838-417b-99df-9e49325e65e4	75bc52b5-2858-4e00-be65-c97b1ef06fb3	copyright_status	Crown Copyright	2025-11-19 14:18:50.047193+00
c3ce5edf-bfaa-426c-afb8-0fb36b90af60	75bc52b5-2858-4e00-be65-c97b1ef06fb3	legal_status	Public Record	2025-11-19 14:18:50.047229+00
5eab10ff-b4cc-456e-905d-908ae4f31eac	4c050849-d396-4167-83d4-180cf8888ef2	source	test_file	2025-11-19 14:18:50.071684+00
7bc621c2-c8f5-4cc4-8faa-1f1b3d586dc5	4c050849-d396-4167-83d4-180cf8888ef2	file_type	wk1	2025-11-19 14:18:50.071748+00
10ffbca1-006a-4175-abba-7334aad6950f	4c050849-d396-4167-83d4-180cf8888ef2	created_at	2025-11-19T14:18:50.071653+00:00	2025-11-19 14:18:50.071793+00
0f50e044-a417-42ec-83de-9acd1f8eaa0c	4c050849-d396-4167-83d4-180cf8888ef2	last_transfer_date	2025-11-19T14:18:50.071660+00:00	2025-11-19 14:18:50.071832+00
bf449797-553f-43df-8592-09d8ec59db5a	4c050849-d396-4167-83d4-180cf8888ef2	file_size	5475	2025-11-19 14:18:50.071872+00
37d787df-2790-4c6c-9b3e-81825dc752e9	4c050849-d396-4167-83d4-180cf8888ef2	file_format	WK1	2025-11-19 14:18:50.071909+00
b291b337-b425-4743-b5fe-6e49c549789e	4c050849-d396-4167-83d4-180cf8888ef2	file_extension	wk1	2025-11-19 14:18:50.071945+00
ebb9918d-7d05-4d14-9ad9-900f90980d1a	4c050849-d396-4167-83d4-180cf8888ef2	mime_type	application/vnd.lotus-1-2-3	2025-11-19 14:18:50.071981+00
39bc5112-d995-4dfc-9c93-090f30d22bd8	4c050849-d396-4167-83d4-180cf8888ef2	closure_status	Open	2025-11-19 14:18:50.072017+00
06a9a400-7f0c-40f4-8c41-64a0d24b9af0	4c050849-d396-4167-83d4-180cf8888ef2	closure_type	Open	2025-11-19 14:18:50.072052+00
57315684-501e-454b-a5ec-7f32a0bc90cb	4c050849-d396-4167-83d4-180cf8888ef2	closure_period	0	2025-11-19 14:18:50.072087+00
1668f4c6-dbe4-4cd7-b509-9462a28c323f	4c050849-d396-4167-83d4-180cf8888ef2	foi_exemption_code	None	2025-11-19 14:18:50.072125+00
4331730c-300b-4202-b4a8-269ef77db36b	4c050849-d396-4167-83d4-180cf8888ef2	foi_exemption_code_description	None	2025-11-19 14:18:50.072161+00
35f610dd-f161-4d2e-a21c-18e3ee5bef09	4c050849-d396-4167-83d4-180cf8888ef2	title	Test File 3	2025-11-19 14:18:50.072196+00
bd46a6c0-37fa-4cf7-86e9-acf66e3bc61e	4c050849-d396-4167-83d4-180cf8888ef2	description	Test file for AYR development	2025-11-19 14:18:50.072231+00
808689ef-6ca4-4ec5-8aab-81efda8ab7a1	4c050849-d396-4167-83d4-180cf8888ef2	language	English	2025-11-19 14:18:50.072265+00
b04c3edb-0051-4468-93a0-b9e4e5aaebd0	4c050849-d396-4167-83d4-180cf8888ef2	security_classification	Open	2025-11-19 14:18:50.072299+00
4787dba0-ab5d-4515-a8f1-bdb9cfeff0cc	4c050849-d396-4167-83d4-180cf8888ef2	copyright_status	Crown Copyright	2025-11-19 14:18:50.072333+00
965d9920-856c-4eeb-8223-d08f9df68893	4c050849-d396-4167-83d4-180cf8888ef2	legal_status	Public Record	2025-11-19 14:18:50.072366+00
637c6a2a-47af-47cb-9360-6804d3c699bc	657c62b7-aed1-4fdd-9ca5-059835f7047c	source	test_file	2025-11-19 14:18:50.15722+00
358a1144-f60c-4b21-b35a-f2fe19ba5971	657c62b7-aed1-4fdd-9ca5-059835f7047c	file_type	doc	2025-11-19 14:18:50.157282+00
92994655-b5e7-4cfd-8dbe-4fffd557da62	657c62b7-aed1-4fdd-9ca5-059835f7047c	created_at	2025-11-19T14:18:50.157191+00:00	2025-11-19 14:18:50.157323+00
33993b5d-bb2e-4d4a-b8c1-95d123e844dd	657c62b7-aed1-4fdd-9ca5-059835f7047c	last_transfer_date	2025-11-19T14:18:50.157197+00:00	2025-11-19 14:18:50.157363+00
5b7548c7-9b7f-404c-b4e7-4bf854f6cc4b	657c62b7-aed1-4fdd-9ca5-059835f7047c	file_size	2677248	2025-11-19 14:18:50.157398+00
3e673374-ffee-4486-bfdb-4560ede5a3ca	657c62b7-aed1-4fdd-9ca5-059835f7047c	file_format	DOC	2025-11-19 14:18:50.157434+00
5e97f6eb-544d-4f68-8021-2ff615276373	657c62b7-aed1-4fdd-9ca5-059835f7047c	file_extension	doc	2025-11-19 14:18:50.157467+00
58c5de8a-8ab7-4f6e-bf94-c76ec809c0fd	657c62b7-aed1-4fdd-9ca5-059835f7047c	mime_type	application/msword	2025-11-19 14:18:50.1575+00
444af2c5-157d-4e07-bdb9-c888ea6032c9	657c62b7-aed1-4fdd-9ca5-059835f7047c	closure_status	Open	2025-11-19 14:18:50.157533+00
abab017b-6af3-4358-9826-bdb756b8331a	657c62b7-aed1-4fdd-9ca5-059835f7047c	closure_type	Open	2025-11-19 14:18:50.157565+00
0aa719df-4636-4562-aab5-6d7e5a96909f	657c62b7-aed1-4fdd-9ca5-059835f7047c	closure_period	0	2025-11-19 14:18:50.157598+00
02b134c8-f4db-4127-ad9e-9f22498145c6	657c62b7-aed1-4fdd-9ca5-059835f7047c	foi_exemption_code	None	2025-11-19 14:18:50.157631+00
3145a12c-2c6b-4564-a930-62c54488dfcd	657c62b7-aed1-4fdd-9ca5-059835f7047c	foi_exemption_code_description	None	2025-11-19 14:18:50.157664+00
70bdce04-619a-4731-a19a-90b2d6cae05c	657c62b7-aed1-4fdd-9ca5-059835f7047c	title	Test File 4	2025-11-19 14:18:50.157697+00
e7506191-53e9-42a7-8fa0-42543459d8ef	657c62b7-aed1-4fdd-9ca5-059835f7047c	description	Test file for AYR development	2025-11-19 14:18:50.157731+00
481c3fdd-6b2e-44c1-b8b7-ad67200f9f09	657c62b7-aed1-4fdd-9ca5-059835f7047c	language	English	2025-11-19 14:18:50.157763+00
8af08b8e-dd02-4ce0-a8c7-213c95567a7f	657c62b7-aed1-4fdd-9ca5-059835f7047c	security_classification	Open	2025-11-19 14:18:50.157795+00
3eab4e98-7d05-479e-987e-3ed4082282ca	657c62b7-aed1-4fdd-9ca5-059835f7047c	copyright_status	Crown Copyright	2025-11-19 14:18:50.157828+00
3f5175b3-4bb0-482e-b41b-88c19119d764	657c62b7-aed1-4fdd-9ca5-059835f7047c	legal_status	Public Record	2025-11-19 14:18:50.157859+00
773be342-e70d-4e65-84a9-6ec2d6d0a1ab	64ab4d01-56a5-4601-9119-fe7c38d6796e	source	test_file	2025-11-19 14:18:50.209809+00
5d8ed7e1-3f59-47e3-9357-5e5b603207a3	64ab4d01-56a5-4601-9119-fe7c38d6796e	file_type	odt	2025-11-19 14:18:50.209876+00
dc611936-05df-401d-ad5b-ef9798eaf06e	64ab4d01-56a5-4601-9119-fe7c38d6796e	created_at	2025-11-19T14:18:50.209774+00:00	2025-11-19 14:18:50.209918+00
0541fa10-240d-406d-b386-67bf44203a6b	64ab4d01-56a5-4601-9119-fe7c38d6796e	last_transfer_date	2025-11-19T14:18:50.209780+00:00	2025-11-19 14:18:50.209958+00
6391c2f2-b43a-4d2d-a1f3-034266475111	64ab4d01-56a5-4601-9119-fe7c38d6796e	file_size	3108267	2025-11-19 14:18:50.209995+00
b557ae7c-2d00-48ef-89c9-91636c4cf536	64ab4d01-56a5-4601-9119-fe7c38d6796e	file_format	ODT	2025-11-19 14:18:50.210029+00
95e5432a-bb6b-4f04-9b90-83409b71eb6e	64ab4d01-56a5-4601-9119-fe7c38d6796e	file_extension	odt	2025-11-19 14:18:50.210062+00
bdf5dbb0-db31-41b0-91f6-80e967618e32	64ab4d01-56a5-4601-9119-fe7c38d6796e	mime_type	application/vnd.oasis.opendocument.text	2025-11-19 14:18:50.210095+00
eedc2736-ae0b-4eba-9444-e1ff3e23faa6	64ab4d01-56a5-4601-9119-fe7c38d6796e	closure_status	Open	2025-11-19 14:18:50.210127+00
10bbf6f4-9528-4410-ae4e-9d17765028c4	64ab4d01-56a5-4601-9119-fe7c38d6796e	closure_type	Open	2025-11-19 14:18:50.210159+00
79ac7bcd-a1ec-4cd8-88e5-3ae6f11ca7d7	64ab4d01-56a5-4601-9119-fe7c38d6796e	closure_period	0	2025-11-19 14:18:50.210191+00
b59971cc-6ded-4bc8-bd93-f6db02dcfa10	64ab4d01-56a5-4601-9119-fe7c38d6796e	foi_exemption_code	None	2025-11-19 14:18:50.210226+00
34f59add-fe81-44fb-869a-91041a4049c0	64ab4d01-56a5-4601-9119-fe7c38d6796e	foi_exemption_code_description	None	2025-11-19 14:18:50.210259+00
ab31cac6-adb6-43d4-9037-700386f79c3b	64ab4d01-56a5-4601-9119-fe7c38d6796e	title	Test File 5	2025-11-19 14:18:50.210295+00
fd38cb8c-0912-4455-a426-f0e8249ef215	64ab4d01-56a5-4601-9119-fe7c38d6796e	description	Test file for AYR development	2025-11-19 14:18:50.210329+00
48a7dee6-6671-479b-8374-9752c5387098	64ab4d01-56a5-4601-9119-fe7c38d6796e	language	English	2025-11-19 14:18:50.210414+00
b8272f66-4d51-49c4-acec-c6416c57673d	64ab4d01-56a5-4601-9119-fe7c38d6796e	security_classification	Open	2025-11-19 14:18:50.210468+00
50854aec-7094-4f7d-aca2-1715a1210c34	64ab4d01-56a5-4601-9119-fe7c38d6796e	copyright_status	Crown Copyright	2025-11-19 14:18:50.210511+00
6edc8010-60d7-4643-9b97-0e52526caf90	64ab4d01-56a5-4601-9119-fe7c38d6796e	legal_status	Public Record	2025-11-19 14:18:50.21055+00
a7c49fdf-afb8-44b8-bbdf-bef1b3b828ce	dd2f4484-243f-4a30-9dc9-c9006e87a744	source	test_file	2025-11-19 14:18:50.22785+00
ba90dc13-751e-4c55-8f0c-5abbc3becb93	dd2f4484-243f-4a30-9dc9-c9006e87a744	file_type	rtf	2025-11-19 14:18:50.227913+00
e4299621-8078-4a14-ad37-7006619e11e3	dd2f4484-243f-4a30-9dc9-c9006e87a744	created_at	2025-11-19T14:18:50.227819+00:00	2025-11-19 14:18:50.227954+00
3cb44563-54e4-4fcd-9c56-b8ac60dfdfb4	dd2f4484-243f-4a30-9dc9-c9006e87a744	last_transfer_date	2025-11-19T14:18:50.227826+00:00	2025-11-19 14:18:50.227991+00
2ae59796-8b7c-4024-a636-fb31700b9d6c	dd2f4484-243f-4a30-9dc9-c9006e87a744	file_size	161986	2025-11-19 14:18:50.228028+00
d0cce713-7be4-4d31-af9b-556f9059dd6b	dd2f4484-243f-4a30-9dc9-c9006e87a744	file_format	RTF	2025-11-19 14:18:50.228062+00
dbf487fd-f836-4a7f-b381-484e9e989534	dd2f4484-243f-4a30-9dc9-c9006e87a744	file_extension	rtf	2025-11-19 14:18:50.228095+00
4ec225d7-0a04-498e-a5b4-966e995ac27c	dd2f4484-243f-4a30-9dc9-c9006e87a744	mime_type	application/rtf	2025-11-19 14:18:50.228127+00
76e59598-68a5-426f-82ad-c959031ecb68	dd2f4484-243f-4a30-9dc9-c9006e87a744	closure_status	Open	2025-11-19 14:18:50.228158+00
3a0a2261-4d28-4e88-a623-ab9ff90ccc7d	dd2f4484-243f-4a30-9dc9-c9006e87a744	closure_type	Open	2025-11-19 14:18:50.228192+00
33c80b7e-c877-4ac7-96e8-3a2868092f8f	dd2f4484-243f-4a30-9dc9-c9006e87a744	closure_period	0	2025-11-19 14:18:50.228226+00
4c514dc2-ab82-4122-91bb-32b17b8d4dcb	dd2f4484-243f-4a30-9dc9-c9006e87a744	foi_exemption_code	None	2025-11-19 14:18:50.228266+00
767a8ba0-bdd9-43bb-9b3c-b6ef7df37ee6	dd2f4484-243f-4a30-9dc9-c9006e87a744	foi_exemption_code_description	None	2025-11-19 14:18:50.2283+00
9369377d-2877-4213-9360-e03a26c74286	dd2f4484-243f-4a30-9dc9-c9006e87a744	title	Test File 6	2025-11-19 14:18:50.228335+00
59963d43-1bb1-43a4-8f52-f2db59e8ca55	dd2f4484-243f-4a30-9dc9-c9006e87a744	description	Test file for AYR development	2025-11-19 14:18:50.228368+00
be43ac79-49c7-4e7b-81d2-2b2fd883d1b7	dd2f4484-243f-4a30-9dc9-c9006e87a744	language	English	2025-11-19 14:18:50.228402+00
695f17a3-121e-4cc0-b08a-d6bdb54f5e38	dd2f4484-243f-4a30-9dc9-c9006e87a744	security_classification	Open	2025-11-19 14:18:50.228435+00
5d9695af-cc1a-43dc-b59e-85f3399bf184	dd2f4484-243f-4a30-9dc9-c9006e87a744	copyright_status	Crown Copyright	2025-11-19 14:18:50.228468+00
ba680c89-0214-46ff-85c6-6c9815ee5225	dd2f4484-243f-4a30-9dc9-c9006e87a744	legal_status	Public Record	2025-11-19 14:18:50.228503+00
7eb3aeff-9f60-405e-a510-107b01d91010	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	source	test_file	2025-11-19 14:18:50.242228+00
1580c891-0baf-4509-b1bf-1c1e7076934d	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	file_type	txt	2025-11-19 14:18:50.242289+00
da57947a-dffa-408b-8677-6dd29ba413a5	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	created_at	2025-11-19T14:18:50.242197+00:00	2025-11-19 14:18:50.242331+00
c253c723-1dc7-4949-bd79-55cb7affa835	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	last_transfer_date	2025-11-19T14:18:50.242202+00:00	2025-11-19 14:18:50.242371+00
1583ea33-09b7-4199-ade2-2235d32276f5	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	file_size	2931	2025-11-19 14:18:50.242408+00
76453024-20d9-4ed1-8057-43de7db8cd9f	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	file_format	TXT	2025-11-19 14:18:50.242445+00
82f3fe1b-64b0-41e4-abc4-73c2b8d5ec30	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	file_extension	txt	2025-11-19 14:18:50.24248+00
5589b465-0a57-479f-b5b9-83c592766efa	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	mime_type	text/plain	2025-11-19 14:18:50.242513+00
802159e5-ca07-44cc-b366-0beb160c3319	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	closure_status	Open	2025-11-19 14:18:50.242545+00
2cb94989-4153-4a15-845c-5ad5d337c9d6	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	closure_type	Open	2025-11-19 14:18:50.242576+00
d41171eb-038d-4729-8310-225bc97bd3c5	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	closure_period	0	2025-11-19 14:18:50.242607+00
cd6027f7-1537-4523-8bdd-ab74731a6385	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	foi_exemption_code	None	2025-11-19 14:18:50.242638+00
f150aec2-20e8-475d-821a-3e4cda5c5bb9	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	foi_exemption_code_description	None	2025-11-19 14:18:50.242669+00
b97e3cf1-8324-4ca2-b14e-aa5ae42b59a3	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	title	Test File 7	2025-11-19 14:18:50.242703+00
20c57185-854e-4797-9023-0565245c5c02	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	description	Test file for AYR development	2025-11-19 14:18:50.242734+00
4e102d1a-9cfa-420d-8780-acf459daf9fa	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	language	English	2025-11-19 14:18:50.242765+00
4fcbd20b-df0a-4386-a819-db032815ab77	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	security_classification	Open	2025-11-19 14:18:50.242796+00
8a8c0412-c995-4b40-b50d-f1c2d45ad2d9	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	copyright_status	Crown Copyright	2025-11-19 14:18:50.242826+00
0d29a1c8-bd07-4a19-9789-e5b098a16e0c	3e4ec2b8-b06a-49d2-9604-9b42be8bbf85	legal_status	Public Record	2025-11-19 14:18:50.242857+00
92be865b-c409-4064-83af-50f3edc3c678	c76c647f-bf99-44de-b7ca-26329ae56e82	source	test_file	2025-11-19 14:18:50.345086+00
513e2d92-1a34-41c4-a0c9-12edddfbd705	c76c647f-bf99-44de-b7ca-26329ae56e82	file_type	pptx	2025-11-19 14:18:50.345154+00
cdeff9c6-5e4d-4bf6-a397-f6064fdbcfd9	c76c647f-bf99-44de-b7ca-26329ae56e82	created_at	2025-11-19T14:18:50.345050+00:00	2025-11-19 14:18:50.345196+00
4a31ec7a-04c1-430f-8d2e-32c7367a9ba7	c76c647f-bf99-44de-b7ca-26329ae56e82	last_transfer_date	2025-11-19T14:18:50.345057+00:00	2025-11-19 14:18:50.345235+00
e4652d10-b77a-4e97-9dee-17ca6ed84236	c76c647f-bf99-44de-b7ca-26329ae56e82	file_size	8697919	2025-11-19 14:18:50.345277+00
8ee1435f-59b6-4730-be7d-960fc1aae8e6	c76c647f-bf99-44de-b7ca-26329ae56e82	file_format	PPTX	2025-11-19 14:18:50.345314+00
dc7c58a3-0395-4b5f-81a7-50b9d2e7188f	c76c647f-bf99-44de-b7ca-26329ae56e82	file_extension	pptx	2025-11-19 14:18:50.345349+00
fd6ca19b-15d9-4d66-9af6-94fabd68bb75	c76c647f-bf99-44de-b7ca-26329ae56e82	mime_type	application/vnd.openxmlformats-officedocument.presentationml.presentation	2025-11-19 14:18:50.345384+00
13ac3098-b684-456a-acc6-ea5d998ef757	c76c647f-bf99-44de-b7ca-26329ae56e82	closure_status	Open	2025-11-19 14:18:50.345417+00
bb8a739b-f780-4bc3-8848-f13f5a61137d	c76c647f-bf99-44de-b7ca-26329ae56e82	closure_type	Open	2025-11-19 14:18:50.345449+00
7f1cd411-cf7c-4e13-abe3-69d4778ce3e1	c76c647f-bf99-44de-b7ca-26329ae56e82	closure_period	0	2025-11-19 14:18:50.345482+00
6cee0258-6742-40c0-a60e-b7523530363c	c76c647f-bf99-44de-b7ca-26329ae56e82	foi_exemption_code	None	2025-11-19 14:18:50.345517+00
c75fe4f5-9652-4ea7-8894-871c33f1abf2	c76c647f-bf99-44de-b7ca-26329ae56e82	foi_exemption_code_description	None	2025-11-19 14:18:50.34555+00
82d43d82-a5a3-4e57-b4d7-cc57b3bdd370	c76c647f-bf99-44de-b7ca-26329ae56e82	title	Test File 8	2025-11-19 14:18:50.345584+00
f26cc758-6464-4d24-9ada-d23641984954	c76c647f-bf99-44de-b7ca-26329ae56e82	description	Test file for AYR development	2025-11-19 14:18:50.345616+00
7ace2a7f-7279-409f-94bb-d4002483b8f6	c76c647f-bf99-44de-b7ca-26329ae56e82	language	English	2025-11-19 14:18:50.345649+00
299764b0-4df6-47ce-b598-0ff0b6b62a51	c76c647f-bf99-44de-b7ca-26329ae56e82	security_classification	Open	2025-11-19 14:18:50.345681+00
f31221bd-903a-479a-8e86-9c8e091667d5	c76c647f-bf99-44de-b7ca-26329ae56e82	copyright_status	Crown Copyright	2025-11-19 14:18:50.345712+00
881ace3a-302a-4bf0-8998-53646e7ac9f3	c76c647f-bf99-44de-b7ca-26329ae56e82	legal_status	Public Record	2025-11-19 14:18:50.345742+00
e28178fb-2776-4b4a-90ac-ee9d7158c461	a851b362-d00e-4a3e-9745-7325aefeff9d	source	test_file	2025-11-19 14:18:50.362821+00
135db6c5-b925-40a6-b087-a8c164ffb5d9	a851b362-d00e-4a3e-9745-7325aefeff9d	file_type	wk4	2025-11-19 14:18:50.362891+00
78116e6b-2a8d-4c7b-9e90-26143429e7a9	a851b362-d00e-4a3e-9745-7325aefeff9d	created_at	2025-11-19T14:18:50.362783+00:00	2025-11-19 14:18:50.362936+00
d662e685-a8e0-4407-87b6-d18e27470f9f	a851b362-d00e-4a3e-9745-7325aefeff9d	last_transfer_date	2025-11-19T14:18:50.362792+00:00	2025-11-19 14:18:50.362979+00
7e0218e4-6c1d-432e-a8dd-dc4cc9484e63	a851b362-d00e-4a3e-9745-7325aefeff9d	file_size	11264	2025-11-19 14:18:50.363017+00
93ec498a-9a9a-4c59-b46b-e33c23304941	a851b362-d00e-4a3e-9745-7325aefeff9d	file_format	WK4	2025-11-19 14:18:50.363054+00
ca253b29-0401-4553-9252-56de8ba9a6c4	a851b362-d00e-4a3e-9745-7325aefeff9d	file_extension	wk4	2025-11-19 14:18:50.363089+00
08829d56-6f0e-436d-b31e-ff291648aa14	a851b362-d00e-4a3e-9745-7325aefeff9d	mime_type	application/vnd.lotus-1-2-3	2025-11-19 14:18:50.363124+00
5a157afb-c5a5-43e2-a09d-4807d5569afd	a851b362-d00e-4a3e-9745-7325aefeff9d	closure_status	Open	2025-11-19 14:18:50.363157+00
0fe7b44b-3db2-4dd4-9d47-4d955613f564	a851b362-d00e-4a3e-9745-7325aefeff9d	closure_type	Open	2025-11-19 14:18:50.36319+00
526ad153-2b9b-46a6-873b-5e43d92015ab	a851b362-d00e-4a3e-9745-7325aefeff9d	closure_period	0	2025-11-19 14:18:50.363223+00
81f7bdfa-6d96-44cc-94c5-036bb39ea630	a851b362-d00e-4a3e-9745-7325aefeff9d	foi_exemption_code	None	2025-11-19 14:18:50.363257+00
49dc5293-9c0e-4ea9-bda1-cc842d9a3916	a851b362-d00e-4a3e-9745-7325aefeff9d	foi_exemption_code_description	None	2025-11-19 14:18:50.36329+00
ecdf12dc-6e98-4ba5-b335-78294a8440e8	a851b362-d00e-4a3e-9745-7325aefeff9d	title	Test File 9	2025-11-19 14:18:50.363324+00
0a099e9d-c9f3-41f1-9bec-739dc2fa1034	a851b362-d00e-4a3e-9745-7325aefeff9d	description	Test file for AYR development	2025-11-19 14:18:50.363356+00
83947837-45fc-406c-a97d-5624bcd0edac	a851b362-d00e-4a3e-9745-7325aefeff9d	language	English	2025-11-19 14:18:50.363389+00
0e9129f2-ed8b-4ff0-a592-6f3b31068a36	a851b362-d00e-4a3e-9745-7325aefeff9d	security_classification	Open	2025-11-19 14:18:50.363422+00
8a471659-c6f0-4919-95d5-c957623fdcf2	a851b362-d00e-4a3e-9745-7325aefeff9d	copyright_status	Crown Copyright	2025-11-19 14:18:50.363456+00
97ed72b1-9782-49ab-89e7-116ca9cd863f	a851b362-d00e-4a3e-9745-7325aefeff9d	legal_status	Public Record	2025-11-19 14:18:50.363489+00
07428a9c-3557-4f89-9f58-cbdb981cca39	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	source	test_file	2025-11-19 14:18:50.384598+00
9ff4cbd0-47fa-4a45-abaa-63d41f29320c	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	file_type	html	2025-11-19 14:18:50.384664+00
92078de2-ed37-457e-be09-e9dcd5afcd5c	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	created_at	2025-11-19T14:18:50.384561+00:00	2025-11-19 14:18:50.384705+00
4482ff97-b754-4547-bdea-1e7d60d2a789	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	last_transfer_date	2025-11-19T14:18:50.384568+00:00	2025-11-19 14:18:50.384744+00
4a41ef96-e246-4c58-a119-9f87317e7a94	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	file_size	5387	2025-11-19 14:18:50.384781+00
6fb3631b-8ba7-4f9e-954e-94e0ea6288bd	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	file_format	HTML	2025-11-19 14:18:50.384817+00
802bfb0c-260e-46e4-b8f1-7e347601c157	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	file_extension	html	2025-11-19 14:18:50.384851+00
3066143d-e837-4a55-bc55-63a1fe20eb38	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	mime_type	text/html	2025-11-19 14:18:50.384885+00
a1ff174e-0f4d-414c-9d14-6e19ef1c2470	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	closure_status	Open	2025-11-19 14:18:50.38492+00
06428a7b-c28b-4bf1-b7fd-4bb85ffb64bf	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	closure_type	Open	2025-11-19 14:18:50.384954+00
d300c204-6fac-4e07-8d82-026894100445	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	closure_period	0	2025-11-19 14:18:50.384987+00
af7705fd-29da-4c51-9de6-c3c86db15fbe	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	foi_exemption_code	None	2025-11-19 14:18:50.385021+00
e13fb402-3823-440a-8d3a-c52aa3597cf7	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	foi_exemption_code_description	None	2025-11-19 14:18:50.385055+00
26d0b265-0e8a-4e56-93a9-d011c05cd72d	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	title	Test File 10	2025-11-19 14:18:50.38509+00
046287f6-9085-43ac-902b-b576cd02999e	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	description	Test file for AYR development	2025-11-19 14:18:50.385122+00
5b2bb0c5-cf72-4ec3-b707-1f2138ca891d	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	language	English	2025-11-19 14:18:50.385154+00
6c86debc-65f1-4fca-ac9f-2a496de6ca8c	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	security_classification	Open	2025-11-19 14:18:50.385189+00
b33998a4-4fc5-4081-a306-44c123d4acfd	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	copyright_status	Crown Copyright	2025-11-19 14:18:50.385225+00
7327ea1e-e093-4f3e-ab62-7e3491b6fd89	f39b7792-eeb9-4bf9-8eac-f4084b7ed18e	legal_status	Public Record	2025-11-19 14:18:50.385258+00
a36c8915-02e2-4224-b861-47851668794c	acf6733e-587b-4fe8-b1d8-f678271b2786	source	test_file	2025-11-19 14:18:50.400126+00
d67b2cbb-3179-4eca-8106-506a341cd850	acf6733e-587b-4fe8-b1d8-f678271b2786	file_type	xls	2025-11-19 14:18:50.400188+00
91b392da-d54e-4ab6-bd34-9a6e3335213b	acf6733e-587b-4fe8-b1d8-f678271b2786	created_at	2025-11-19T14:18:50.400100+00:00	2025-11-19 14:18:50.400233+00
80355723-d90b-4c5c-b2a2-7147062c3eaf	acf6733e-587b-4fe8-b1d8-f678271b2786	last_transfer_date	2025-11-19T14:18:50.400105+00:00	2025-11-19 14:18:50.400273+00
14b8c434-6be2-4024-972c-e13a88af5970	acf6733e-587b-4fe8-b1d8-f678271b2786	file_size	12679	2025-11-19 14:18:50.40031+00
1c3a28f5-7718-4fe2-887e-6ee017da0283	acf6733e-587b-4fe8-b1d8-f678271b2786	file_format	XLS	2025-11-19 14:18:50.400346+00
059c2351-5985-4107-b3e5-e31cbb82629a	acf6733e-587b-4fe8-b1d8-f678271b2786	file_extension	xls	2025-11-19 14:18:50.400382+00
0593f213-12a8-4ac1-9d7b-b60c941015d1	acf6733e-587b-4fe8-b1d8-f678271b2786	mime_type	application/vnd.ms-excel	2025-11-19 14:18:50.400415+00
1417b95c-01a2-4dfd-aa02-cbbae69f881c	acf6733e-587b-4fe8-b1d8-f678271b2786	closure_status	Open	2025-11-19 14:18:50.40045+00
0216044e-03dc-4f92-b87a-31f6f9449865	acf6733e-587b-4fe8-b1d8-f678271b2786	closure_type	Open	2025-11-19 14:18:50.400484+00
6961c9e6-8830-4a68-b94f-5fc2302b2e76	acf6733e-587b-4fe8-b1d8-f678271b2786	closure_period	0	2025-11-19 14:18:50.40052+00
fc03a540-0c3e-4637-978b-056fcecefc83	acf6733e-587b-4fe8-b1d8-f678271b2786	foi_exemption_code	None	2025-11-19 14:18:50.400556+00
c6216b2c-601e-4d34-89f2-78d596776b67	acf6733e-587b-4fe8-b1d8-f678271b2786	foi_exemption_code_description	None	2025-11-19 14:18:50.40059+00
c3570ae9-4593-4eb0-ac69-2444207737b5	acf6733e-587b-4fe8-b1d8-f678271b2786	title	Test File 11	2025-11-19 14:18:50.400624+00
30061c12-e77d-4a75-87ff-bce3827935b3	acf6733e-587b-4fe8-b1d8-f678271b2786	description	Test file for AYR development	2025-11-19 14:18:50.400659+00
0980ef43-36cd-4ee2-bbf7-c54769b132fd	acf6733e-587b-4fe8-b1d8-f678271b2786	language	English	2025-11-19 14:18:50.400693+00
40eb8e62-51df-49ed-b14c-a122330f266b	acf6733e-587b-4fe8-b1d8-f678271b2786	security_classification	Open	2025-11-19 14:18:50.400728+00
ccde3025-e9a6-4c1c-99a7-37b029230483	acf6733e-587b-4fe8-b1d8-f678271b2786	copyright_status	Crown Copyright	2025-11-19 14:18:50.400761+00
aac4e730-b128-4457-b786-91e779c88df0	acf6733e-587b-4fe8-b1d8-f678271b2786	legal_status	Public Record	2025-11-19 14:18:50.400794+00
00cae932-c90c-4414-a4c7-20f4ad2905cb	f52ff646-9f9f-4261-a495-2806894684e6	source	test_file	2025-11-19 14:18:50.415831+00
11ec28e9-45e1-464e-918b-581fb3473f31	f52ff646-9f9f-4261-a495-2806894684e6	file_type	xml	2025-11-19 14:18:50.415901+00
21f8cbba-8571-44f5-9005-1ffc9a392e5b	f52ff646-9f9f-4261-a495-2806894684e6	created_at	2025-11-19T14:18:50.415796+00:00	2025-11-19 14:18:50.415947+00
73b61491-f9fe-49f8-b816-1a67af4a3f7e	f52ff646-9f9f-4261-a495-2806894684e6	last_transfer_date	2025-11-19T14:18:50.415802+00:00	2025-11-19 14:18:50.415989+00
5accbbaa-af2b-4209-894d-1564f3b60eff	f52ff646-9f9f-4261-a495-2806894684e6	file_size	7787	2025-11-19 14:18:50.416027+00
cfde2cf1-c109-470d-8fce-816990932aea	f52ff646-9f9f-4261-a495-2806894684e6	file_format	XML	2025-11-19 14:18:50.416064+00
d90d6b36-6132-4873-9d80-e0d0cd985c71	f52ff646-9f9f-4261-a495-2806894684e6	file_extension	xml	2025-11-19 14:18:50.416101+00
d30b8e0e-aec1-443b-a315-9d8bc26cd88d	f52ff646-9f9f-4261-a495-2806894684e6	mime_type	application/xml	2025-11-19 14:18:50.416135+00
08a52221-d8fe-4108-ae85-2e9b0f60b73e	f52ff646-9f9f-4261-a495-2806894684e6	closure_status	Open	2025-11-19 14:18:50.416213+00
44b1faef-4377-4f0e-96d2-87f8840ff696	f52ff646-9f9f-4261-a495-2806894684e6	closure_type	Open	2025-11-19 14:18:50.416305+00
094acf39-e837-4515-b5c7-a89559be5e91	f52ff646-9f9f-4261-a495-2806894684e6	closure_period	0	2025-11-19 14:18:50.416374+00
1219ff82-4a5f-49b8-8a22-33853a91c3b5	f52ff646-9f9f-4261-a495-2806894684e6	foi_exemption_code	None	2025-11-19 14:18:50.416425+00
5d2cc4cf-cd12-40e2-94e7-292bc2e30504	f52ff646-9f9f-4261-a495-2806894684e6	foi_exemption_code_description	None	2025-11-19 14:18:50.416568+00
071ba077-0467-4c66-8471-0882c4a9327e	f52ff646-9f9f-4261-a495-2806894684e6	title	Test File 12	2025-11-19 14:18:50.416629+00
cd9fb4a3-6761-4a72-9320-bd978c5cc7d4	f52ff646-9f9f-4261-a495-2806894684e6	description	Test file for AYR development	2025-11-19 14:18:50.416675+00
08eb25f6-9f68-4ba3-a294-d0a814e30178	f52ff646-9f9f-4261-a495-2806894684e6	language	English	2025-11-19 14:18:50.416715+00
684b9124-455a-42ca-ae80-25c0f87847f1	f52ff646-9f9f-4261-a495-2806894684e6	security_classification	Open	2025-11-19 14:18:50.416755+00
6cc28edb-e79f-4f9f-95ec-893f6d288817	f52ff646-9f9f-4261-a495-2806894684e6	copyright_status	Crown Copyright	2025-11-19 14:18:50.416794+00
64f9690c-0feb-4b6d-9885-a55337dd5392	f52ff646-9f9f-4261-a495-2806894684e6	legal_status	Public Record	2025-11-19 14:18:50.416834+00
6a942c29-40da-4d75-956c-1d130592f03b	56809bd9-060a-421b-9d0b-d77e52e151e4	source	test_file	2025-11-19 14:18:50.440124+00
f9d54ca0-564d-4d5d-9383-e46518702ecd	56809bd9-060a-421b-9d0b-d77e52e151e4	file_type	ppt	2025-11-19 14:18:50.440189+00
75f147be-e50f-484b-b7dd-eeeb259b8c44	56809bd9-060a-421b-9d0b-d77e52e151e4	created_at	2025-11-19T14:18:50.440093+00:00	2025-11-19 14:18:50.440231+00
a122ec9e-8112-4a04-aef9-57f3c85528e4	56809bd9-060a-421b-9d0b-d77e52e151e4	last_transfer_date	2025-11-19T14:18:50.440100+00:00	2025-11-19 14:18:50.440271+00
0e0ee35c-516d-4c14-ad7e-af75778c21c0	56809bd9-060a-421b-9d0b-d77e52e151e4	file_size	799232	2025-11-19 14:18:50.440309+00
67f46d82-d7b6-4ecf-888d-8bd53a0a8e26	56809bd9-060a-421b-9d0b-d77e52e151e4	file_format	PPT	2025-11-19 14:18:50.440366+00
2a73029c-9f5a-4199-9084-8a23f5e454ef	56809bd9-060a-421b-9d0b-d77e52e151e4	file_extension	ppt	2025-11-19 14:18:50.440442+00
7b85ee2a-cea7-4842-830e-92387856aa9e	56809bd9-060a-421b-9d0b-d77e52e151e4	mime_type	application/vnd.ms-powerpoint	2025-11-19 14:18:50.440497+00
42337835-5489-4c75-9651-d1caad723d7c	56809bd9-060a-421b-9d0b-d77e52e151e4	closure_status	Open	2025-11-19 14:18:50.440538+00
b73a19f6-65c6-4352-9e4a-9536104a5256	56809bd9-060a-421b-9d0b-d77e52e151e4	closure_type	Open	2025-11-19 14:18:50.440576+00
b2629115-bbd5-481a-bf32-26c3751b59f0	56809bd9-060a-421b-9d0b-d77e52e151e4	closure_period	0	2025-11-19 14:18:50.440615+00
ceb8c3bc-65b8-4b6b-883a-05ae148c27c2	56809bd9-060a-421b-9d0b-d77e52e151e4	foi_exemption_code	None	2025-11-19 14:18:50.440652+00
05653db3-de00-4167-8758-c759a96f5222	56809bd9-060a-421b-9d0b-d77e52e151e4	foi_exemption_code_description	None	2025-11-19 14:18:50.440688+00
37182dbe-5fc1-4bf0-8b7b-776fd9ba350e	56809bd9-060a-421b-9d0b-d77e52e151e4	title	Test File 13	2025-11-19 14:18:50.440725+00
2059e04e-ad8e-44e4-8485-6b2d52193897	56809bd9-060a-421b-9d0b-d77e52e151e4	description	Test file for AYR development	2025-11-19 14:18:50.440759+00
66b99f6a-3a7f-42ca-ad51-f0362a01ac03	56809bd9-060a-421b-9d0b-d77e52e151e4	language	English	2025-11-19 14:18:50.440794+00
c7188e8a-ecd9-486c-b1bc-d0a3e9fbcbca	56809bd9-060a-421b-9d0b-d77e52e151e4	security_classification	Open	2025-11-19 14:18:50.440828+00
07984572-4748-4952-a841-97cac5d4b7ad	56809bd9-060a-421b-9d0b-d77e52e151e4	copyright_status	Crown Copyright	2025-11-19 14:18:50.440863+00
4327c5ba-ebcb-4c9b-949b-e5b0ebb6160e	56809bd9-060a-421b-9d0b-d77e52e151e4	legal_status	Public Record	2025-11-19 14:18:50.440894+00
394eda60-abff-404a-a571-1585ff320f5d	c83d1866-f1ae-479b-b770-3117a12c4c65	source	test_file	2025-11-19 14:18:50.457701+00
cc7d63b8-b1a5-4b35-9657-5925599a65f8	c83d1866-f1ae-479b-b770-3117a12c4c65	file_type	xlsx	2025-11-19 14:18:50.457763+00
261b8757-a6dd-449f-b47d-9c9b17b31184	c83d1866-f1ae-479b-b770-3117a12c4c65	created_at	2025-11-19T14:18:50.457666+00:00	2025-11-19 14:18:50.457803+00
f8c1c725-439b-4169-9037-b048abb020c3	c83d1866-f1ae-479b-b770-3117a12c4c65	last_transfer_date	2025-11-19T14:18:50.457675+00:00	2025-11-19 14:18:50.457839+00
8867c0aa-058d-4868-8e5b-10eb36152e34	c83d1866-f1ae-479b-b770-3117a12c4c65	file_size	12679	2025-11-19 14:18:50.457873+00
39de8a0c-a597-4e30-a407-018b3ef48406	c83d1866-f1ae-479b-b770-3117a12c4c65	file_format	XLSX	2025-11-19 14:18:50.457907+00
8cf90b21-bb02-4b07-9051-43553f8b483b	c83d1866-f1ae-479b-b770-3117a12c4c65	file_extension	xlsx	2025-11-19 14:18:50.457939+00
eccc60d4-2690-4218-a7f9-22d2710878d2	c83d1866-f1ae-479b-b770-3117a12c4c65	mime_type	application/vnd.openxmlformats-officedocument.spreadsheetml.sheet	2025-11-19 14:18:50.457972+00
dd827f82-6c06-409e-828a-cd3ec0ec2b1e	c83d1866-f1ae-479b-b770-3117a12c4c65	closure_status	Open	2025-11-19 14:18:50.458003+00
cefe3e35-d0c8-4c66-b37f-aa681bb50e60	c83d1866-f1ae-479b-b770-3117a12c4c65	closure_type	Open	2025-11-19 14:18:50.458034+00
928299df-11b2-4094-b365-b219add0cc93	c83d1866-f1ae-479b-b770-3117a12c4c65	closure_period	0	2025-11-19 14:18:50.458065+00
c67f5657-6aa9-4558-8953-cfcb13a59158	c83d1866-f1ae-479b-b770-3117a12c4c65	foi_exemption_code	None	2025-11-19 14:18:50.458098+00
fb574936-58ba-48d4-98d9-58c75e7a5ee2	c83d1866-f1ae-479b-b770-3117a12c4c65	foi_exemption_code_description	None	2025-11-19 14:18:50.45813+00
2e6cf8da-38da-4f5a-8abc-5fbc24d8fe2a	c83d1866-f1ae-479b-b770-3117a12c4c65	title	Test File 14	2025-11-19 14:18:50.458164+00
3f4332c8-9be2-4ffa-8ce5-95af6a6e568d	c83d1866-f1ae-479b-b770-3117a12c4c65	description	Test file for AYR development	2025-11-19 14:18:50.458198+00
2e6b2b9d-e7f8-40bb-99ba-ec7ccbca5bd1	c83d1866-f1ae-479b-b770-3117a12c4c65	language	English	2025-11-19 14:18:50.458231+00
b654af5a-5f4d-4196-93a0-003bb7a2180c	c83d1866-f1ae-479b-b770-3117a12c4c65	security_classification	Open	2025-11-19 14:18:50.458264+00
899c6219-11ed-44aa-963b-b1381a24304b	c83d1866-f1ae-479b-b770-3117a12c4c65	copyright_status	Crown Copyright	2025-11-19 14:18:50.458301+00
063ce336-c801-4bb7-8948-4fea88518b2e	c83d1866-f1ae-479b-b770-3117a12c4c65	legal_status	Public Record	2025-11-19 14:18:50.458333+00
\.


--
-- Data for Name: Series; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."Series" ("SeriesId", "BodyId", "Name", "Description") FROM stdin;
93ed0101-2318-45ab-8730-c681958ded7e	4654e9f9-335b-4ab1-acd8-edff54f908d4	AYR 1	AYR 1
8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	8ccc8cd1-c0ee-431d-afad-70cf404ba337	MOCK1 123	MOCK1 123
1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	TSTA 1	TSTA 1
e43c4f33-bad8-4f58-9423-6bb2d5598194	05b7267f-a0c8-47dc-b062-f04bff369fea	SCOT 13	Test Series Description
\.


--
-- Name: Body Body_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Body"
    ADD CONSTRAINT "Body_pkey" PRIMARY KEY ("BodyId");


--
-- Name: Consignment Consignment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT "Consignment_pkey" PRIMARY KEY ("ConsignmentId");


--
-- Name: FileMetadata FileMetadata_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."FileMetadata"
    ADD CONSTRAINT "FileMetadata_pkey" PRIMARY KEY ("MetadataId");


--
-- Name: File File_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT "File_pkey" PRIMARY KEY ("FileId");


--
-- Name: Series Series_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Series"
    ADD CONSTRAINT "Series_pkey" PRIMARY KEY ("SeriesId");


--
-- Name: Body body_name_unq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Body"
    ADD CONSTRAINT body_name_unq UNIQUE ("Name");


--
-- Name: File consignment_filepath_unq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT consignment_filepath_unq UNIQUE ("ConsignmentId", "FilePath");


--
-- Name: FileMetadata fileid_property_value_unq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."FileMetadata"
    ADD CONSTRAINT fileid_property_value_unq UNIQUE ("FileId", "PropertyName", "Value");


--
-- Name: Consignment reference_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT reference_unique UNIQUE ("ConsignmentReference");


--
-- Name: Series series_name_unq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Series"
    ADD CONSTRAINT series_name_unq UNIQUE ("Name");


--
-- Name: File FK_File.ConsignmentId; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."File"
    ADD CONSTRAINT "FK_File.ConsignmentId" FOREIGN KEY ("ConsignmentId") REFERENCES public."Consignment"("ConsignmentId");


--
-- Name: AVMetadata avmetadata_fileid_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."AVMetadata"
    ADD CONSTRAINT avmetadata_fileid_file_fkey FOREIGN KEY ("FileId") REFERENCES public."File"("FileId");


--
-- Name: Consignment consignment_bodyid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT consignment_bodyid_fkey FOREIGN KEY ("BodyId") REFERENCES public."Body"("BodyId");


--
-- Name: Consignment consignment_seriesid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Consignment"
    ADD CONSTRAINT consignment_seriesid_fkey FOREIGN KEY ("SeriesId") REFERENCES public."Series"("SeriesId");


--
-- Name: FFIDMetadata ffidmetadata_fileid_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."FFIDMetadata"
    ADD CONSTRAINT ffidmetadata_fileid_file_fkey FOREIGN KEY ("FileId") REFERENCES public."File"("FileId");


--
-- Name: FileMetadata filemetadata_fileid_file_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."FileMetadata"
    ADD CONSTRAINT filemetadata_fileid_file_fkey FOREIGN KEY ("FileId") REFERENCES public."File"("FileId");


--
-- Name: Series series_bodyid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."Series"
    ADD CONSTRAINT series_bodyid_fkey FOREIGN KEY ("BodyId") REFERENCES public."Body"("BodyId");


--
-- PostgreSQL database dump complete
--
