--
-- PostgreSQL database dump
--

\restrict 9kyEghew8MAVJtsihSYalXQqSynlJscb0q94pvGEStduenbhroB1CJOQV1V03et

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
b51c2f65-68e1-4dad-9115-eccf31929234	Test Transferring Body	Test Transferring Body Description
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
fdef6846-cbb3-428f-8739-1c2905e60e8f	b51c2f65-68e1-4dad-9115-eccf31929234	5729cee7-a930-4385-bb3b-5137af8a6f61	AYR-2025-KBZR	Test	t	Test User	test@example.com	2025-11-20 04:07:07.183213+00	1994-09-17 20:08:16.550669+00	1995-01-09 18:47:01.870674+00	2025-11-20 04:07:07.183214+00
\.


--
-- Data for Name: FFIDMetadata; Type: TABLE DATA; Schema: public; Owner: -
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
b2279f23-8d07-4fa5-b0af-94ec4123e21e	pdf	fmt/276	Acrobat PDF 1.7 - Portable Document Format	true	Droid	6.7.0	111	20230822
8211c175-5331-4fba-a14b-24db8fdaf6a1	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
0de5cb7e-baf6-4f9c-8a52-450dd117ae83				false	Droid	6.7.0	116	20231127
405ea5a6-b71d-4ecd-be3c-43062af8e1e6	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
cc3a458b-123d-4b01-b7e5-787a05dfd7a7	pdf	fmt/276	Acrobat PDF 1.7 - Portable Document Format	false	Droid	6.7.0	111	20230822
8ecc93c8-dc96-4419-aeba-f79c84298cc8	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
f97b02bb-19c3-4e0e-bfb3-dab351dcc5f5	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
db7455e6-3b09-49c4-89c5-19ad2ce52aa5	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
b9a8f847-ce98-4894-8c48-3986570dec7d	pdf	fmt/276	Acrobat PDF 1.7 - Portable Document Format	true	Droid	6.7.0	111	20230822
100251bb-5b93-48a9-953f-ad5bd9abfbdc	txt	x-fmt/111	Plain Text File	false	Droid	6.7.0	111	20230822
8ffacc5a-443a-4568-a5c9-c9741955b40f	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
47526ba9-88e5-4cc8-8bc1-d682a10fa270	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
6bc75990-86fe-4527-9fb6-43fbe6e16427	doc	fmt/40	Microsoft Word Document	true	Siegfried	IiwjY	KIHgZ	BrMTQ
4fa7658c-f98c-43a4-a788-f4b13c4ae163	docx	fmt/412	Microsoft Word Open XML Document	true	Siegfried	NDFLk	LXBSk	Ggdoq
9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	html	x-fmt/394	HyperText Markup Language	false	Siegfried	MYeUE	itJmM	pwpGS
d4076b8d-fce2-41c9-9663-07b4722b8a17	odt	fmt/39	OpenDocument Text	true	Siegfried	AEYvM	hXbXe	sdthw
e55b7520-6bed-40a7-9372-9f9965fbe7b2	pdf	fmt/276	PDF	false	DROID	FdSKw	IaFBs	VJeph
9760be6c-8c94-497c-8435-822214a8336f	ppt	fmt/214	Microsoft PowerPoint Presentation	false	Siegfried	SubWF	KnJAK	FFHZF
13783f72-cd63-488e-bda0-e7c7b9561128	pptx	fmt/126	Microsoft PowerPoint Open XML Presentation	true	Siegfried	thKqp	RHwYH	kPdxs
a2568af5-019c-41f2-a67a-7b56e768a736	rtf	fmt/61	Rich Text Format	true	Siegfried	kxaNx	Zrjzo	zCqoQ
128f419b-4c5c-4d91-b18f-f6c5a609a907	txt	\N	Plain Text	true	DROID	xxcNp	Bjibb	uiFaV
d7bef5f6-eef2-40b5-af0f-6d707546d119	wk1	x-fmt/44	Lotus 1-2-3 Spreadsheet	true	DROID	ohpWp	Dsxzf	CTnQM
d43dd389-6753-48e2-9a7b-b2693c801499	wk4	x-fmt/45	Lotus 1-2-3 Spreadsheet	true	Siegfried	yKhXa	mmhFt	YrZFB
838aa45e-a70f-47e8-b76e-9d6732e99921	xls	fmt/59	Microsoft Excel Spreadsheet	true	Siegfried	RiNHn	LIUuh	IusCc
5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	xlsx	fmt/215	Microsoft Excel Open XML Spreadsheet	false	Siegfried	qFTIG	lXWgi	TUofB
596df45d-8a7f-49c9-b759-2b32c138db11	xml	fmt/50	Extensible Markup Language	false	Siegfried	viaqZ	dXzHT	shoLo
4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	jpg	x-fmt/111	JPEG Image	true	DROID	ikWKS	pOduU	vHsuI
61a712eb-0600-40c8-88ad-221de3390b4d	png	x-fmt/116	Portable Network Graphics	true	Siegfried	Vbwoq	gDQht	AZofx
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
6bc75990-86fe-4527-9fb6-43fbe6e16427	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZFW6DB.doc	data/content/SCOT 13_ZFW6DB.doc	2IDF	CITE-0001	\N	\N	kJaTgtvbTR	2025-11-20 04:07:07.361706+00
4fa7658c-f98c-43a4-a788-f4b13c4ae163	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZDC8J4.docx	data/content/SCOT 13_ZDC8J4.docx	L1LS	CITE-0002	\N	\N	NFyoyrdACK	2025-11-20 04:07:07.379544+00
9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_Z9P523.html	data/content/SCOT 13_Z9P523.html	ZKMR	CITE-0003	\N	\N	oZLzVPdKkA	2025-11-20 04:07:07.400125+00
d4076b8d-fce2-41c9-9663-07b4722b8a17	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_Z9P4WW.odt	data/content/SCOT 13_Z9P4WW.odt	BJH6	CITE-0005	\N	\N	kQoKArvJwh	2025-11-20 04:07:07.508489+00
e55b7520-6bed-40a7-9372-9f9965fbe7b2	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZDKL26.pdf	data/content/SCOT 13_ZDKL26.pdf	BL6Z	CITE-0006	\N	\N	OpsweBlVXO	2025-11-20 04:07:07.589761+00
9760be6c-8c94-497c-8435-822214a8336f	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_Z95P37.ppt	data/content/SCOT 13_Z95P37.ppt	MLFO	CITE-0008	\N	\N	CurtcHHCqQ	2025-11-20 04:07:07.630357+00
13783f72-cd63-488e-bda0-e7c7b9561128	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZG8SKW.pptx	data/content/SCOT 13_ZG8SKW.pptx	MWKU	CITE-0009	\N	\N	BmtarlkRdI	2025-11-20 04:07:07.730218+00
a2568af5-019c-41f2-a67a-7b56e768a736	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZJ56LA.rtf	data/content/SCOT 13_ZJ56LA.rtf	3C0C	CITE-0010	\N	\N	dLAwMWqvXq	2025-11-20 04:07:07.748623+00
128f419b-4c5c-4d91-b18f-f6c5a609a907	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_DNI76K.txt	data/content/SCOT 13_DNI76K.txt	MUDQ	CITE-0011	\N	\N	VjNOdeXqwe	2025-11-20 04:07:07.761308+00
d7bef5f6-eef2-40b5-af0f-6d707546d119	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZB33RH.wk1	data/content/SCOT 13_ZB33RH.wk1	D4UP	CITE-0012	\N	\N	gSvLJaXAqk	2025-11-20 04:07:07.775112+00
d43dd389-6753-48e2-9a7b-b2693c801499	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_ZB33RK.wk4	data/content/SCOT 13_ZB33RK.wk4	KUSI	CITE-0013	\N	\N	qCfwivluSL	2025-11-20 04:07:07.790838+00
838aa45e-a70f-47e8-b76e-9d6732e99921	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_VTC9WP.xls	data/content/SCOT 13_VTC9WP.xls	F4LD	CITE-0014	\N	\N	xlNnWzYmig	2025-11-20 04:07:07.805617+00
5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_UYT6DV.xlsx	data/content/SCOT 13_UYT6DV.xlsx	CRUS	CITE-0015	\N	\N	gxoaEVFTxz	2025-11-20 04:07:07.824285+00
596df45d-8a7f-49c9-b759-2b32c138db11	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_Z9P524.xml	data/content/SCOT 13_Z9P524.xml	XIYZ	CITE-0016	\N	\N	VxIKLmThPH	2025-11-20 04:07:07.840969+00
4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_6YTFTC.jpg	data/content/SCOT 13_6YTFTC.jpg	HCTB	CITE-0001	\N	\N	zmgayUxiRz	2025-11-25 08:58:02.609041+00
61a712eb-0600-40c8-88ad-221de3390b4d	fdef6846-cbb3-428f-8739-1c2905e60e8f	File	SCOT 13_G85D3R.png	data/content/SCOT 13_G85D3R.png	Q6Y7	CITE-0002	\N	\N	mSLFlrxTeA	2025-11-25 08:58:02.657023+00
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
724effe1-5da5-4f88-b32d-c410a4154d6a	6bc75990-86fe-4527-9fb6-43fbe6e16427	source	test_file	2025-11-20 04:07:07.361874+00
14b8a4a0-abdb-4372-8033-582941e8eca4	6bc75990-86fe-4527-9fb6-43fbe6e16427	file_name	SCOT 13_ZFW6DB.doc	2025-11-20 04:07:07.361955+00
47aecb9c-5772-493f-b1b8-521a4cf2f054	6bc75990-86fe-4527-9fb6-43fbe6e16427	file_type	File	2025-11-20 04:07:07.36201+00
5a30465f-bc31-41a9-a512-b3bb12b64ed7	6bc75990-86fe-4527-9fb6-43fbe6e16427	file_size	2677248	2025-11-20 04:07:07.362059+00
f4f945de-b7f3-4b6d-b51b-135609deaae9	6bc75990-86fe-4527-9fb6-43fbe6e16427	rights_copyright	Crown Copyright	2025-11-20 04:07:07.362107+00
5cb7264e-6ae1-48cb-8619-df77e7ef1f63	6bc75990-86fe-4527-9fb6-43fbe6e16427	legal_status	Public Record(s)	2025-11-20 04:07:07.362153+00
2de90ce6-d0bf-4664-b2f2-bf8b91ccf168	6bc75990-86fe-4527-9fb6-43fbe6e16427	held_by	The National Archives	2025-11-20 04:07:07.362196+00
62a39f19-926b-416b-85d9-bc0d55bf9e8a	6bc75990-86fe-4527-9fb6-43fbe6e16427	date_last_modified	2025-11-20T04:07:07.361860+00:00	2025-11-20 04:07:07.362242+00
f63f2e00-77aa-4a83-a03d-07cea44f007f	6bc75990-86fe-4527-9fb6-43fbe6e16427	description	Test file for AYR development	2025-11-20 04:07:07.362283+00
a048cecb-4057-40a8-9e17-0ad868956ef4	6bc75990-86fe-4527-9fb6-43fbe6e16427	closure_type	Open	2025-11-20 04:07:07.362325+00
cfaaec4e-1eb1-46c7-b28d-01885b040e7e	6bc75990-86fe-4527-9fb6-43fbe6e16427	title_closed	false	2025-11-20 04:07:07.362366+00
e99f4d06-dd84-4bf2-be53-438a6692dc9f	6bc75990-86fe-4527-9fb6-43fbe6e16427	description_closed	false	2025-11-20 04:07:07.36241+00
891f3353-4296-49cc-85f7-b51b0af271f9	6bc75990-86fe-4527-9fb6-43fbe6e16427	language	English	2025-11-20 04:07:07.362452+00
615867cc-247a-4f9c-903c-ce859abfee01	6bc75990-86fe-4527-9fb6-43fbe6e16427	created_at	2025-11-20T04:07:07.361868+00:00	2025-11-20 04:07:07.362493+00
3742173d-423c-492c-a0e4-a7c6e1dff3ee	6bc75990-86fe-4527-9fb6-43fbe6e16427	last_transfer_date	2025-11-20T04:07:07.361870+00:00	2025-11-20 04:07:07.362535+00
6b8dd4cf-0cef-4d68-8c1b-90eeceded05b	6bc75990-86fe-4527-9fb6-43fbe6e16427	file_format	DOC	2025-11-20 04:07:07.362573+00
b4c9530f-6a81-42bb-98c9-244472e8e540	6bc75990-86fe-4527-9fb6-43fbe6e16427	file_extension	doc	2025-11-20 04:07:07.362611+00
7297cc7c-ef01-41dd-9bb6-56743487bf80	6bc75990-86fe-4527-9fb6-43fbe6e16427	closure_status	Open	2025-11-20 04:07:07.36265+00
c9cf36b1-cf6b-4838-9d9c-3b5bf9588ea8	6bc75990-86fe-4527-9fb6-43fbe6e16427	closure_period	0	2025-11-20 04:07:07.362688+00
ffd5afc8-2099-46bd-ac16-46f87c719b57	6bc75990-86fe-4527-9fb6-43fbe6e16427	foi_exemption_code	None	2025-11-20 04:07:07.362728+00
c60117d8-182f-4dcd-a66f-3c086f76192c	6bc75990-86fe-4527-9fb6-43fbe6e16427	foi_exemption_code_description	None	2025-11-20 04:07:07.362766+00
ff124946-4e92-4f6d-920a-da3343e03bb0	6bc75990-86fe-4527-9fb6-43fbe6e16427	title	Test File 1	2025-11-20 04:07:07.362808+00
f78e61a5-48de-4ce3-8138-e9ca76755ff0	4fa7658c-f98c-43a4-a788-f4b13c4ae163	source	test_file	2025-11-20 04:07:07.379683+00
9d6085ec-24cc-47c1-938d-a2eabb91f1ed	4fa7658c-f98c-43a4-a788-f4b13c4ae163	file_name	SCOT 13_ZDC8J4.docx	2025-11-20 04:07:07.379748+00
c1002f64-e14e-4499-b8da-75f3f4ec18ae	4fa7658c-f98c-43a4-a788-f4b13c4ae163	file_type	File	2025-11-20 04:07:07.379792+00
99425e46-43ba-4039-bef2-1cd43f3189b2	4fa7658c-f98c-43a4-a788-f4b13c4ae163	file_size	8558	2025-11-20 04:07:07.379833+00
7a06b0bb-3c8e-436f-85c1-9693377ccbd9	4fa7658c-f98c-43a4-a788-f4b13c4ae163	rights_copyright	Crown Copyright	2025-11-20 04:07:07.379874+00
6cd67bcb-7e0e-4fcf-b5a1-f1692c601c85	4fa7658c-f98c-43a4-a788-f4b13c4ae163	legal_status	Public Record(s)	2025-11-20 04:07:07.379911+00
2be7ca71-341f-464f-832d-e051df5974ea	4fa7658c-f98c-43a4-a788-f4b13c4ae163	held_by	The National Archives	2025-11-20 04:07:07.379947+00
b9b6493d-ccb2-4fe5-80e8-38565b5ddb77	4fa7658c-f98c-43a4-a788-f4b13c4ae163	date_last_modified	2025-11-20T04:07:07.379671+00:00	2025-11-20 04:07:07.379984+00
92915812-0864-4379-97c7-a65421cfba07	4fa7658c-f98c-43a4-a788-f4b13c4ae163	description	Test file for AYR development	2025-11-20 04:07:07.380021+00
d1820ab4-a8a2-4d35-9cdc-fbdc1220a45b	4fa7658c-f98c-43a4-a788-f4b13c4ae163	closure_type	Open	2025-11-20 04:07:07.380059+00
43b30662-ade1-47a7-85ef-5af2c6267edc	4fa7658c-f98c-43a4-a788-f4b13c4ae163	title_closed	false	2025-11-20 04:07:07.380099+00
78027552-9171-451f-a7ad-e1e27116232e	4fa7658c-f98c-43a4-a788-f4b13c4ae163	description_closed	false	2025-11-20 04:07:07.38014+00
736c7ec6-79d7-45f2-be9a-4408046f1718	4fa7658c-f98c-43a4-a788-f4b13c4ae163	language	English	2025-11-20 04:07:07.380178+00
ce868c04-d5b1-480e-a9b5-a2a9f9adec8a	4fa7658c-f98c-43a4-a788-f4b13c4ae163	created_at	2025-11-20T04:07:07.379677+00:00	2025-11-20 04:07:07.380216+00
7e336100-7953-4892-9cff-3bd9f303cd1f	4fa7658c-f98c-43a4-a788-f4b13c4ae163	last_transfer_date	2025-11-20T04:07:07.379679+00:00	2025-11-20 04:07:07.380256+00
da35c277-8e33-47db-b0a8-da701856170f	4fa7658c-f98c-43a4-a788-f4b13c4ae163	file_format	DOCX	2025-11-20 04:07:07.380292+00
e0f9c57d-2610-4d13-8ef5-ba133fe16795	4fa7658c-f98c-43a4-a788-f4b13c4ae163	file_extension	docx	2025-11-20 04:07:07.380327+00
aec38f5e-f90a-48d1-a793-224cc93afa2e	4fa7658c-f98c-43a4-a788-f4b13c4ae163	closure_status	Open	2025-11-20 04:07:07.380363+00
ba772d22-e899-48aa-a9d8-11a4047d727d	4fa7658c-f98c-43a4-a788-f4b13c4ae163	closure_period	0	2025-11-20 04:07:07.380402+00
21f9eb17-5390-43a7-adfa-c3dc08eef0db	4fa7658c-f98c-43a4-a788-f4b13c4ae163	foi_exemption_code	None	2025-11-20 04:07:07.38044+00
5ab9afbd-15ec-4873-b9b0-a4af862e6b07	4fa7658c-f98c-43a4-a788-f4b13c4ae163	foi_exemption_code_description	None	2025-11-20 04:07:07.380475+00
87440e6a-b9a9-4953-bdff-b86ad420dca4	4fa7658c-f98c-43a4-a788-f4b13c4ae163	title	Test File 2	2025-11-20 04:07:07.380512+00
7287918f-d0be-41cd-9f91-f586552530ce	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	source	test_file	2025-11-20 04:07:07.400264+00
78ffe7a9-3146-4b26-bcc1-cde3fdfedf5d	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	file_name	SCOT 13_Z9P523.html	2025-11-20 04:07:07.400353+00
758de7bd-8057-4d5f-a85f-3bb94b7caed8	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	file_type	File	2025-11-20 04:07:07.400413+00
649b3e65-f0d4-463e-9f5d-628e17dbf806	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	file_size	6216	2025-11-20 04:07:07.400454+00
fe7283ad-3637-43c8-9380-91092e2d6520	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	rights_copyright	Crown Copyright	2025-11-20 04:07:07.400497+00
e07f8ceb-309b-41f8-b8fc-3be4ae8163cc	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	legal_status	Public Record(s)	2025-11-20 04:07:07.400538+00
b25eba6f-2463-40fc-a944-8aa46e0d95f5	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	held_by	The National Archives	2025-11-20 04:07:07.400575+00
553553e9-ff86-4451-8d66-dde6b24f925a	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	date_last_modified	2025-11-20T04:07:07.400251+00:00	2025-11-20 04:07:07.400612+00
ee4e17b4-1dc7-40a9-ac96-961bc811793c	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	description	Test file for AYR development	2025-11-20 04:07:07.400647+00
fe004af8-566a-4476-87bf-a7693fbf1724	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	closure_type	Open	2025-11-20 04:07:07.400683+00
e7adb4da-a3d6-4e46-8511-874631f6b275	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	title_closed	false	2025-11-20 04:07:07.400718+00
3873b6e9-d40c-4a44-ad2f-bac2f1b66736	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	description_closed	false	2025-11-20 04:07:07.400755+00
dbe91b00-347a-4dcd-9fb2-f588755a6851	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	language	English	2025-11-20 04:07:07.400789+00
4f2c5d5e-ad58-42b0-8602-0cc2a1402da0	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	created_at	2025-11-20T04:07:07.400258+00:00	2025-11-20 04:07:07.400825+00
a6a9de37-b64f-4ded-abf3-260de100938e	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	last_transfer_date	2025-11-20T04:07:07.400259+00:00	2025-11-20 04:07:07.400862+00
98298274-8889-4554-a5d2-46a59a17bab5	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	file_format	HTML	2025-11-20 04:07:07.400896+00
dbdea426-e3fa-40c3-a22d-869abb01b30a	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	file_extension	html	2025-11-20 04:07:07.400932+00
8d702f0f-d5ae-41c5-83ca-54f4e4a9b300	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	closure_status	Open	2025-11-20 04:07:07.400966+00
2c0c9d69-ad7d-4a40-8b74-bb41a0dc3cc2	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	closure_period	0	2025-11-20 04:07:07.401+00
7d9b2903-8ff4-4999-b432-a296ad5a094d	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	foi_exemption_code	None	2025-11-20 04:07:07.401035+00
66be5905-906b-436b-9bd2-5627ef1d72b2	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	foi_exemption_code_description	None	2025-11-20 04:07:07.401069+00
99b2818f-15f5-45cb-8885-bdc07f699158	9a77366a-b5dc-4e97-9c68-24a5c2c7b39f	title	Test File 3	2025-11-20 04:07:07.401104+00
cc897ece-0969-4353-a577-dcf6311b71e0	d4076b8d-fce2-41c9-9663-07b4722b8a17	source	test_file	2025-11-20 04:07:07.508632+00
61d7bbb2-fbe4-4700-8031-d1424919a578	d4076b8d-fce2-41c9-9663-07b4722b8a17	file_name	SCOT 13_Z9P4WW.odt	2025-11-20 04:07:07.508694+00
c3e0672a-f78d-469d-b53f-ca840ad99420	d4076b8d-fce2-41c9-9663-07b4722b8a17	file_type	File	2025-11-20 04:07:07.508739+00
d4f57294-4e3d-4ddc-9d7a-953988b68b78	d4076b8d-fce2-41c9-9663-07b4722b8a17	file_size	3108267	2025-11-20 04:07:07.508778+00
14cad7d8-90ca-4d35-952b-92ab233bc0eb	d4076b8d-fce2-41c9-9663-07b4722b8a17	rights_copyright	Crown Copyright	2025-11-20 04:07:07.508815+00
f44c1d0f-858f-4cb4-83f5-ab83d0820cf0	d4076b8d-fce2-41c9-9663-07b4722b8a17	legal_status	Public Record(s)	2025-11-20 04:07:07.508852+00
bed9d3cb-32e3-41d1-ab9f-9a7c8d781ff6	d4076b8d-fce2-41c9-9663-07b4722b8a17	held_by	The National Archives	2025-11-20 04:07:07.508894+00
c3d53e88-38d0-4c4f-8108-cdd82431521a	d4076b8d-fce2-41c9-9663-07b4722b8a17	date_last_modified	2025-11-20T04:07:07.508616+00:00	2025-11-20 04:07:07.508934+00
27e26be5-599b-4b35-a269-7c48698cdb1c	d4076b8d-fce2-41c9-9663-07b4722b8a17	description	Test file for AYR development	2025-11-20 04:07:07.508975+00
05d81802-a729-4a1e-bc7d-145fd1856405	d4076b8d-fce2-41c9-9663-07b4722b8a17	closure_type	Open	2025-11-20 04:07:07.509016+00
c6ee7b26-a338-4a45-a9e0-a651a9ec547b	d4076b8d-fce2-41c9-9663-07b4722b8a17	title_closed	false	2025-11-20 04:07:07.509056+00
fdb9dd36-d299-41a4-afe7-7231393ea2f5	d4076b8d-fce2-41c9-9663-07b4722b8a17	description_closed	false	2025-11-20 04:07:07.509096+00
cbc391ee-6fe1-462c-a0e0-35ef35bc1189	d4076b8d-fce2-41c9-9663-07b4722b8a17	language	English	2025-11-20 04:07:07.509134+00
f23971df-949c-462a-b807-68c3dfdc2659	d4076b8d-fce2-41c9-9663-07b4722b8a17	created_at	2025-11-20T04:07:07.508626+00:00	2025-11-20 04:07:07.509173+00
e1544675-488b-44ac-b17d-ced4724aafdb	d4076b8d-fce2-41c9-9663-07b4722b8a17	last_transfer_date	2025-11-20T04:07:07.508628+00:00	2025-11-20 04:07:07.509212+00
534a78db-2077-4e71-b9ba-274edc4570b5	d4076b8d-fce2-41c9-9663-07b4722b8a17	file_format	ODT	2025-11-20 04:07:07.50925+00
8eaf0186-6153-43d6-8039-12b7ebda7a94	d4076b8d-fce2-41c9-9663-07b4722b8a17	file_extension	odt	2025-11-20 04:07:07.509291+00
ce964274-4343-4e6e-b840-20dfa12e4bca	d4076b8d-fce2-41c9-9663-07b4722b8a17	closure_status	Open	2025-11-20 04:07:07.509332+00
ff27e6f0-6001-4fe1-8d81-c520d78c9f22	d4076b8d-fce2-41c9-9663-07b4722b8a17	closure_period	0	2025-11-20 04:07:07.509371+00
a5c7a00b-e2da-4470-bfe9-af2d0f9ad966	d4076b8d-fce2-41c9-9663-07b4722b8a17	foi_exemption_code	None	2025-11-20 04:07:07.50941+00
9c78a8ca-5112-4941-863c-e2c228dede96	d4076b8d-fce2-41c9-9663-07b4722b8a17	foi_exemption_code_description	None	2025-11-20 04:07:07.509453+00
6b7bdc27-ab07-4a26-98de-957b5324b8e3	d4076b8d-fce2-41c9-9663-07b4722b8a17	title	Test File 5	2025-11-20 04:07:07.509496+00
9acd0c24-f9dc-4966-8e09-e4b45ef287d5	e55b7520-6bed-40a7-9372-9f9965fbe7b2	source	test_file	2025-11-20 04:07:07.589898+00
7a6aa1b3-2f1e-4dda-adcd-bc2f1bcc48a9	e55b7520-6bed-40a7-9372-9f9965fbe7b2	file_name	SCOT 13_ZDKL26.pdf	2025-11-20 04:07:07.589963+00
e9edb0a8-273c-461a-bb38-069b41efd960	e55b7520-6bed-40a7-9372-9f9965fbe7b2	file_type	File	2025-11-20 04:07:07.590006+00
7238e44a-1870-4ce4-b15f-bec7b3b8caad	e55b7520-6bed-40a7-9372-9f9965fbe7b2	file_size	6726645	2025-11-20 04:07:07.590047+00
bb0ebc19-0444-4405-bb46-7e299a104ea7	e55b7520-6bed-40a7-9372-9f9965fbe7b2	rights_copyright	Crown Copyright	2025-11-20 04:07:07.590085+00
dda9f475-b208-4248-b7ad-e3623e95350f	e55b7520-6bed-40a7-9372-9f9965fbe7b2	legal_status	Public Record(s)	2025-11-20 04:07:07.590123+00
4ad382c1-569f-4ee2-b42b-072749bf88ec	e55b7520-6bed-40a7-9372-9f9965fbe7b2	held_by	The National Archives	2025-11-20 04:07:07.590161+00
3b160128-ae80-4a17-bc27-d3182fd609d0	e55b7520-6bed-40a7-9372-9f9965fbe7b2	date_last_modified	2025-11-20T04:07:07.589885+00:00	2025-11-20 04:07:07.590195+00
b5d7214c-688a-4ea2-beeb-568b1ba917cb	e55b7520-6bed-40a7-9372-9f9965fbe7b2	description	Test file for AYR development	2025-11-20 04:07:07.59023+00
d5433a2f-bae6-487c-96b5-469645f70715	e55b7520-6bed-40a7-9372-9f9965fbe7b2	closure_type	Open	2025-11-20 04:07:07.590262+00
5486a606-5fad-4171-bf99-6186b09bad23	e55b7520-6bed-40a7-9372-9f9965fbe7b2	title_closed	false	2025-11-20 04:07:07.590294+00
bb2dd493-0b7e-44e6-81cf-d3cf8811cb6a	e55b7520-6bed-40a7-9372-9f9965fbe7b2	description_closed	false	2025-11-20 04:07:07.590329+00
5cc1487c-8f14-46a1-a419-10c39d9c9cac	e55b7520-6bed-40a7-9372-9f9965fbe7b2	language	English	2025-11-20 04:07:07.590362+00
04df5196-a8ca-4c48-a979-c2b5c53d6887	e55b7520-6bed-40a7-9372-9f9965fbe7b2	created_at	2025-11-20T04:07:07.589892+00:00	2025-11-20 04:07:07.590396+00
bab1aa9e-8ecb-4449-956d-b9c1896597aa	e55b7520-6bed-40a7-9372-9f9965fbe7b2	last_transfer_date	2025-11-20T04:07:07.589894+00:00	2025-11-20 04:07:07.59043+00
92f1a722-f9f9-4dc5-b979-95a3ad47ebed	e55b7520-6bed-40a7-9372-9f9965fbe7b2	file_format	PDF	2025-11-20 04:07:07.590464+00
47338482-1821-42f1-9ecb-8a1489ff1641	e55b7520-6bed-40a7-9372-9f9965fbe7b2	file_extension	pdf	2025-11-20 04:07:07.590498+00
696da54c-528a-4ead-8d40-fb1ce72c8643	e55b7520-6bed-40a7-9372-9f9965fbe7b2	closure_status	Open	2025-11-20 04:07:07.590532+00
9cc4b66f-a579-4730-811a-d545475a270c	e55b7520-6bed-40a7-9372-9f9965fbe7b2	closure_period	0	2025-11-20 04:07:07.590566+00
973376ac-f2ab-4933-81fd-38c111cc9212	e55b7520-6bed-40a7-9372-9f9965fbe7b2	foi_exemption_code	None	2025-11-20 04:07:07.590607+00
4ee69273-b80d-4566-86ed-152d9e078176	e55b7520-6bed-40a7-9372-9f9965fbe7b2	foi_exemption_code_description	None	2025-11-20 04:07:07.590641+00
1d699964-1e4c-4827-99ba-b779ceda21a3	e55b7520-6bed-40a7-9372-9f9965fbe7b2	title	Test File 6	2025-11-20 04:07:07.590677+00
dae9a88f-3566-4856-9ba6-d9d8aa9cbb30	9760be6c-8c94-497c-8435-822214a8336f	source	test_file	2025-11-20 04:07:07.630494+00
38c2c0e0-6dc6-4c47-a260-a5c30ad68991	9760be6c-8c94-497c-8435-822214a8336f	file_name	SCOT 13_Z95P37.ppt	2025-11-20 04:07:07.630558+00
235e9e95-0ba2-4230-a5f2-f3165583e398	9760be6c-8c94-497c-8435-822214a8336f	file_type	File	2025-11-20 04:07:07.6306+00
1760c17f-8e22-4070-88e5-80f9f4b4982f	9760be6c-8c94-497c-8435-822214a8336f	file_size	799232	2025-11-20 04:07:07.630641+00
082f4acd-c737-4158-88e6-c1cbceca5bf3	9760be6c-8c94-497c-8435-822214a8336f	rights_copyright	Crown Copyright	2025-11-20 04:07:07.630678+00
18f6656d-f07e-4806-b5ff-574ff76aecbc	9760be6c-8c94-497c-8435-822214a8336f	legal_status	Public Record(s)	2025-11-20 04:07:07.630713+00
3f37e3b1-deb8-4b2c-91b2-6ba91dca1907	9760be6c-8c94-497c-8435-822214a8336f	held_by	The National Archives	2025-11-20 04:07:07.630747+00
90e410ee-b277-4935-b7aa-4f25d29284b1	9760be6c-8c94-497c-8435-822214a8336f	date_last_modified	2025-11-20T04:07:07.630481+00:00	2025-11-20 04:07:07.630783+00
f6724c07-27ec-491c-9baf-26f45ab26916	9760be6c-8c94-497c-8435-822214a8336f	description	Test file for AYR development	2025-11-20 04:07:07.630816+00
88d25562-6a1e-4d75-86bf-c88bbdf9c54c	9760be6c-8c94-497c-8435-822214a8336f	closure_type	Open	2025-11-20 04:07:07.630849+00
d2522933-e195-4a75-9188-2936d3555df0	9760be6c-8c94-497c-8435-822214a8336f	title_closed	false	2025-11-20 04:07:07.630883+00
05843aff-2241-409e-acd2-87929fc34465	9760be6c-8c94-497c-8435-822214a8336f	description_closed	false	2025-11-20 04:07:07.630919+00
ff12f6aa-4a67-4d99-bc00-f7e3f4a28df6	9760be6c-8c94-497c-8435-822214a8336f	language	English	2025-11-20 04:07:07.630953+00
560bc627-7624-4e52-8d25-5548bd468529	9760be6c-8c94-497c-8435-822214a8336f	created_at	2025-11-20T04:07:07.630489+00:00	2025-11-20 04:07:07.630989+00
9b02ac9f-0680-49cc-a87c-fe0a56b34727	9760be6c-8c94-497c-8435-822214a8336f	last_transfer_date	2025-11-20T04:07:07.630490+00:00	2025-11-20 04:07:07.631024+00
7d75a9b1-a645-48f1-9a3a-2e23b5fff5ae	9760be6c-8c94-497c-8435-822214a8336f	file_format	PPT	2025-11-20 04:07:07.631057+00
733cf4d8-7eac-4f9c-a68d-0a385cac8c7e	9760be6c-8c94-497c-8435-822214a8336f	file_extension	ppt	2025-11-20 04:07:07.63109+00
7a1afae2-ff49-43a3-8be9-7e221097a325	9760be6c-8c94-497c-8435-822214a8336f	closure_status	Open	2025-11-20 04:07:07.631127+00
be8ea591-9d58-4591-a209-537680cf2e15	9760be6c-8c94-497c-8435-822214a8336f	closure_period	0	2025-11-20 04:07:07.63116+00
245f5866-5dab-47c1-ab3a-e279599209de	9760be6c-8c94-497c-8435-822214a8336f	foi_exemption_code	None	2025-11-20 04:07:07.631195+00
89e2af6e-75a5-4393-9312-1f341605bece	9760be6c-8c94-497c-8435-822214a8336f	foi_exemption_code_description	None	2025-11-20 04:07:07.631228+00
123ff2cd-b31a-4fc8-81e6-f84065412f75	9760be6c-8c94-497c-8435-822214a8336f	title	Test File 8	2025-11-20 04:07:07.631261+00
96b9e28b-519f-43a9-8808-f663e36ff53a	13783f72-cd63-488e-bda0-e7c7b9561128	source	test_file	2025-11-20 04:07:07.730356+00
a7d88510-c5d6-4799-912b-8eb7c5c8e13b	13783f72-cd63-488e-bda0-e7c7b9561128	file_name	SCOT 13_ZG8SKW.pptx	2025-11-20 04:07:07.730419+00
46e68c08-ebfa-4d41-9eea-7962a6158956	13783f72-cd63-488e-bda0-e7c7b9561128	file_type	File	2025-11-20 04:07:07.730466+00
8e8f1e34-34f7-413c-9054-acbbac9bc467	13783f72-cd63-488e-bda0-e7c7b9561128	file_size	8697919	2025-11-20 04:07:07.730507+00
271a78ff-bd02-486c-92c7-9f6f9fc278be	13783f72-cd63-488e-bda0-e7c7b9561128	rights_copyright	Crown Copyright	2025-11-20 04:07:07.730545+00
3797fc3c-a0c7-42e6-a5b9-aa3333b8c2cb	13783f72-cd63-488e-bda0-e7c7b9561128	legal_status	Public Record(s)	2025-11-20 04:07:07.730581+00
e7c66b84-4cd6-4cc7-af5a-e2cb9a0ca3d6	13783f72-cd63-488e-bda0-e7c7b9561128	held_by	The National Archives	2025-11-20 04:07:07.730618+00
345ed77f-0221-4350-8b3f-6a82abca9cd1	13783f72-cd63-488e-bda0-e7c7b9561128	date_last_modified	2025-11-20T04:07:07.730343+00:00	2025-11-20 04:07:07.730656+00
0a5f75b8-3a91-4748-8736-89233dc53c04	13783f72-cd63-488e-bda0-e7c7b9561128	description	Test file for AYR development	2025-11-20 04:07:07.73069+00
6b2b912a-9b34-4c48-9572-00130296747d	13783f72-cd63-488e-bda0-e7c7b9561128	closure_type	Open	2025-11-20 04:07:07.730724+00
5706a17b-a535-4a6f-a86e-0f6efed4cf01	13783f72-cd63-488e-bda0-e7c7b9561128	title_closed	false	2025-11-20 04:07:07.730758+00
cd21423c-51d0-42ba-a535-a32842df4c21	13783f72-cd63-488e-bda0-e7c7b9561128	description_closed	false	2025-11-20 04:07:07.730794+00
35894ae5-5a91-4982-b234-7421751e2463	13783f72-cd63-488e-bda0-e7c7b9561128	language	English	2025-11-20 04:07:07.730829+00
6bbe7f77-585d-4b34-b91f-bc67937d7dfb	13783f72-cd63-488e-bda0-e7c7b9561128	created_at	2025-11-20T04:07:07.730350+00:00	2025-11-20 04:07:07.730863+00
e1a883e5-04d8-4b5a-b8c0-d2883fed3ac9	13783f72-cd63-488e-bda0-e7c7b9561128	last_transfer_date	2025-11-20T04:07:07.730352+00:00	2025-11-20 04:07:07.730897+00
4ef09691-dfd8-4c65-a5e9-69c17800d88c	13783f72-cd63-488e-bda0-e7c7b9561128	file_format	PPTX	2025-11-20 04:07:07.730928+00
45ec315b-c5f9-421a-b317-c5331136e11f	13783f72-cd63-488e-bda0-e7c7b9561128	file_extension	pptx	2025-11-20 04:07:07.73096+00
e44e7ad6-5abd-423f-8cef-c597592c1f33	13783f72-cd63-488e-bda0-e7c7b9561128	closure_status	Open	2025-11-20 04:07:07.730992+00
76b590c3-6ff1-4800-9e92-b71a23d8843b	13783f72-cd63-488e-bda0-e7c7b9561128	closure_period	0	2025-11-20 04:07:07.731024+00
769893e7-d46b-40e4-adee-fe0f79dfd060	13783f72-cd63-488e-bda0-e7c7b9561128	foi_exemption_code	None	2025-11-20 04:07:07.731056+00
983d0a55-675a-44e6-b051-420b35c01530	13783f72-cd63-488e-bda0-e7c7b9561128	foi_exemption_code_description	None	2025-11-20 04:07:07.73109+00
5d0fa392-7d18-4ecd-b222-e19c746b9b18	13783f72-cd63-488e-bda0-e7c7b9561128	title	Test File 9	2025-11-20 04:07:07.731122+00
ee33c05a-2e9f-4c4b-89f5-b3baadc1d9d0	a2568af5-019c-41f2-a67a-7b56e768a736	source	test_file	2025-11-20 04:07:07.748751+00
630b6d36-a801-48c6-adf6-59946c8c3dcf	a2568af5-019c-41f2-a67a-7b56e768a736	file_name	SCOT 13_ZJ56LA.rtf	2025-11-20 04:07:07.748815+00
9a9d7f22-8d62-4105-a82e-32c7fa6488eb	a2568af5-019c-41f2-a67a-7b56e768a736	file_type	File	2025-11-20 04:07:07.748857+00
2b2fc476-bcf4-4fc2-a01d-fa4305fd0ac9	a2568af5-019c-41f2-a67a-7b56e768a736	file_size	161987	2025-11-20 04:07:07.748897+00
0cdc77cc-bce5-4889-805a-988122b8f881	a2568af5-019c-41f2-a67a-7b56e768a736	rights_copyright	Crown Copyright	2025-11-20 04:07:07.748934+00
6270077d-3e51-4e33-b574-01ca5bcce66e	a2568af5-019c-41f2-a67a-7b56e768a736	legal_status	Public Record(s)	2025-11-20 04:07:07.748971+00
dc59bf63-a823-4d6b-8875-857be721928f	a2568af5-019c-41f2-a67a-7b56e768a736	held_by	The National Archives	2025-11-20 04:07:07.749006+00
2cbdd941-cc1a-453b-918e-89186f227b05	a2568af5-019c-41f2-a67a-7b56e768a736	date_last_modified	2025-11-20T04:07:07.748739+00:00	2025-11-20 04:07:07.749041+00
0d8d0b97-a04e-43be-9b34-88972eb64e6a	a2568af5-019c-41f2-a67a-7b56e768a736	description	Test file for AYR development	2025-11-20 04:07:07.749077+00
01c384c5-2b7d-45e4-abe5-9729af426a0d	a2568af5-019c-41f2-a67a-7b56e768a736	closure_type	Open	2025-11-20 04:07:07.749111+00
738bf7f5-6e22-4cce-b18f-b9d433f1b42f	a2568af5-019c-41f2-a67a-7b56e768a736	title_closed	false	2025-11-20 04:07:07.749145+00
029a63a9-1e5d-43a6-b394-a314ecd59de3	a2568af5-019c-41f2-a67a-7b56e768a736	description_closed	false	2025-11-20 04:07:07.749182+00
e81120cf-797d-4a5c-94a3-824bb01a49a6	a2568af5-019c-41f2-a67a-7b56e768a736	language	English	2025-11-20 04:07:07.749217+00
4b35310c-453a-4267-b544-4dbfe2ccf83b	a2568af5-019c-41f2-a67a-7b56e768a736	created_at	2025-11-20T04:07:07.748746+00:00	2025-11-20 04:07:07.749254+00
4677098b-c84a-45b2-afbf-5f999fe64100	a2568af5-019c-41f2-a67a-7b56e768a736	last_transfer_date	2025-11-20T04:07:07.748747+00:00	2025-11-20 04:07:07.749289+00
b71096d0-c6f7-4dba-a9e2-eae218d8f66a	a2568af5-019c-41f2-a67a-7b56e768a736	file_format	RTF	2025-11-20 04:07:07.749325+00
1dccf81c-e29c-4aeb-951d-02c2851e4ea3	a2568af5-019c-41f2-a67a-7b56e768a736	file_extension	rtf	2025-11-20 04:07:07.749358+00
a614310b-2d96-4d17-b754-1dc60f5c86eb	a2568af5-019c-41f2-a67a-7b56e768a736	closure_status	Open	2025-11-20 04:07:07.749393+00
5c001282-55ab-45ae-9dcc-bdd45348e089	a2568af5-019c-41f2-a67a-7b56e768a736	closure_period	0	2025-11-20 04:07:07.749426+00
352842c9-af27-4129-a048-b48b71df6da6	a2568af5-019c-41f2-a67a-7b56e768a736	foi_exemption_code	None	2025-11-20 04:07:07.749462+00
e5c9b743-7674-42be-b75e-a87f24ca2029	a2568af5-019c-41f2-a67a-7b56e768a736	foi_exemption_code_description	None	2025-11-20 04:07:07.749495+00
09d0d674-f466-404f-b69f-ef9a8857f1c0	a2568af5-019c-41f2-a67a-7b56e768a736	title	Test File 10	2025-11-20 04:07:07.749528+00
7b590caa-3797-4a93-951f-faeb34d9cfd1	128f419b-4c5c-4d91-b18f-f6c5a609a907	source	test_file	2025-11-20 04:07:07.761423+00
559dd695-2141-49ca-92a0-9cff85099a6a	128f419b-4c5c-4d91-b18f-f6c5a609a907	file_name	SCOT 13_DNI76K.txt	2025-11-20 04:07:07.761482+00
5a678d93-fc35-4f54-9678-b8ec7ad9f57e	128f419b-4c5c-4d91-b18f-f6c5a609a907	file_type	File	2025-11-20 04:07:07.761525+00
be03bce4-e18b-42fe-ace8-94d99d576671	128f419b-4c5c-4d91-b18f-f6c5a609a907	file_size	2930	2025-11-20 04:07:07.761568+00
2f849957-ee29-4954-b46d-03af58fb5d2a	128f419b-4c5c-4d91-b18f-f6c5a609a907	rights_copyright	Crown Copyright	2025-11-20 04:07:07.761605+00
c7840999-4b0a-4e3f-8f9f-61b4f227aa53	128f419b-4c5c-4d91-b18f-f6c5a609a907	legal_status	Public Record(s)	2025-11-20 04:07:07.761641+00
df577a7e-5dd3-4fd1-a8e9-9b807dd10e8b	128f419b-4c5c-4d91-b18f-f6c5a609a907	held_by	The National Archives	2025-11-20 04:07:07.761679+00
3820dcd2-d59f-45b2-bfff-e2a46eff15e5	128f419b-4c5c-4d91-b18f-f6c5a609a907	date_last_modified	2025-11-20T04:07:07.761413+00:00	2025-11-20 04:07:07.761714+00
f5a8cd33-12eb-421d-b545-de4b70f3ca27	128f419b-4c5c-4d91-b18f-f6c5a609a907	description	Test file for AYR development	2025-11-20 04:07:07.76175+00
6149fbf5-2000-47b1-99a4-ebf1373674e2	128f419b-4c5c-4d91-b18f-f6c5a609a907	closure_type	Open	2025-11-20 04:07:07.761784+00
85a82222-8fa8-4d55-aefa-592e4db09dff	128f419b-4c5c-4d91-b18f-f6c5a609a907	title_closed	false	2025-11-20 04:07:07.761821+00
9768e684-a7a6-4e5e-b4a0-67a19eb2ec78	128f419b-4c5c-4d91-b18f-f6c5a609a907	description_closed	false	2025-11-20 04:07:07.761858+00
c99f5974-82f7-4505-97ad-2f3de9392a7f	128f419b-4c5c-4d91-b18f-f6c5a609a907	language	English	2025-11-20 04:07:07.761893+00
5c44f34d-327a-4121-8ad1-2bcbad9d992b	128f419b-4c5c-4d91-b18f-f6c5a609a907	created_at	2025-11-20T04:07:07.761418+00:00	2025-11-20 04:07:07.76193+00
3f1e3254-8c65-498e-a47b-87603ae0f5fe	128f419b-4c5c-4d91-b18f-f6c5a609a907	last_transfer_date	2025-11-20T04:07:07.761420+00:00	2025-11-20 04:07:07.761965+00
fd1ec887-cbdc-47da-a5ff-257350e53f1d	128f419b-4c5c-4d91-b18f-f6c5a609a907	file_format	TXT	2025-11-20 04:07:07.761999+00
aea7b467-48fb-4efe-b0ad-f5b6b6210915	128f419b-4c5c-4d91-b18f-f6c5a609a907	file_extension	txt	2025-11-20 04:07:07.762033+00
d5e0b3ea-2c46-4bdf-b7bd-839775fe1c26	128f419b-4c5c-4d91-b18f-f6c5a609a907	closure_status	Open	2025-11-20 04:07:07.762068+00
7cbda00c-b5bd-4014-a3da-d6674a28822e	128f419b-4c5c-4d91-b18f-f6c5a609a907	closure_period	0	2025-11-20 04:07:07.762101+00
95c0eb3b-9572-4d66-8331-150ba1945c7a	128f419b-4c5c-4d91-b18f-f6c5a609a907	foi_exemption_code	None	2025-11-20 04:07:07.762135+00
c69e72dc-9bdd-4e49-88c8-5c9c1bf3ab57	128f419b-4c5c-4d91-b18f-f6c5a609a907	foi_exemption_code_description	None	2025-11-20 04:07:07.76217+00
3593fc5e-21ac-4be0-bd56-7be7231de0de	128f419b-4c5c-4d91-b18f-f6c5a609a907	title	Test File 11	2025-11-20 04:07:07.762204+00
e13601f7-8d3c-4332-910e-ed6c0168588b	d7bef5f6-eef2-40b5-af0f-6d707546d119	source	test_file	2025-11-20 04:07:07.775269+00
3ee2cec7-9860-4a62-9fb9-92c7ddd39da5	d7bef5f6-eef2-40b5-af0f-6d707546d119	file_name	SCOT 13_ZB33RH.wk1	2025-11-20 04:07:07.77534+00
f54ea7a6-03b3-4268-89c8-d5fbd9c21acd	d7bef5f6-eef2-40b5-af0f-6d707546d119	file_type	File	2025-11-20 04:07:07.775384+00
ed9d7620-6fe5-44a4-9c3d-f03e25b42894	d7bef5f6-eef2-40b5-af0f-6d707546d119	file_size	5475	2025-11-20 04:07:07.775428+00
72d8a0e8-d110-4868-892f-ec9cf08f80b4	d7bef5f6-eef2-40b5-af0f-6d707546d119	rights_copyright	Crown Copyright	2025-11-20 04:07:07.775472+00
fad65d48-1dcd-4df3-82f9-b045eafbe776	d7bef5f6-eef2-40b5-af0f-6d707546d119	legal_status	Public Record(s)	2025-11-20 04:07:07.775511+00
dde10dfb-73f3-456c-9c46-499253a9ada0	d7bef5f6-eef2-40b5-af0f-6d707546d119	held_by	The National Archives	2025-11-20 04:07:07.775548+00
d140d311-cbc8-47ca-b276-ea8ee8e76d52	d7bef5f6-eef2-40b5-af0f-6d707546d119	date_last_modified	2025-11-20T04:07:07.775252+00:00	2025-11-20 04:07:07.775588+00
8121e593-d06d-4cc0-95bc-930f3f0d3229	d7bef5f6-eef2-40b5-af0f-6d707546d119	description	Test file for AYR development	2025-11-20 04:07:07.775626+00
ee6fbbe8-df46-4790-8487-410d0b6cf530	d7bef5f6-eef2-40b5-af0f-6d707546d119	closure_type	Open	2025-11-20 04:07:07.775663+00
a09a088d-88b3-43a3-95ea-9b83383fcb80	d7bef5f6-eef2-40b5-af0f-6d707546d119	title_closed	false	2025-11-20 04:07:07.775703+00
1442b46f-4372-40c5-8928-267d225f3979	d7bef5f6-eef2-40b5-af0f-6d707546d119	description_closed	false	2025-11-20 04:07:07.775741+00
3f3c64f2-4876-4832-809e-0d6bc803b739	d7bef5f6-eef2-40b5-af0f-6d707546d119	language	English	2025-11-20 04:07:07.775778+00
e7276540-27d2-4869-bf0e-51986c70106c	d7bef5f6-eef2-40b5-af0f-6d707546d119	created_at	2025-11-20T04:07:07.775263+00:00	2025-11-20 04:07:07.775815+00
fa6cda03-fa4d-428b-b6bc-f8379ba0c155	d7bef5f6-eef2-40b5-af0f-6d707546d119	last_transfer_date	2025-11-20T04:07:07.775264+00:00	2025-11-20 04:07:07.775853+00
f1611de1-d2c2-45dc-a87e-2a7e9e9c377d	d7bef5f6-eef2-40b5-af0f-6d707546d119	file_format	WK1	2025-11-20 04:07:07.77589+00
f9309b2a-9934-4adc-b69e-5105f6a88e81	d7bef5f6-eef2-40b5-af0f-6d707546d119	file_extension	wk1	2025-11-20 04:07:07.775927+00
9965c5c6-e45a-408b-b870-d2d8e88018b9	d7bef5f6-eef2-40b5-af0f-6d707546d119	closure_status	Open	2025-11-20 04:07:07.775963+00
317547d8-1a65-4a79-87db-c7936cf15af0	d7bef5f6-eef2-40b5-af0f-6d707546d119	closure_period	0	2025-11-20 04:07:07.775999+00
50e52719-943c-4ee8-b48c-2a390a5d9df0	d7bef5f6-eef2-40b5-af0f-6d707546d119	foi_exemption_code	None	2025-11-20 04:07:07.776036+00
93a86008-58cc-47d3-b580-4ab0446803ad	d7bef5f6-eef2-40b5-af0f-6d707546d119	foi_exemption_code_description	None	2025-11-20 04:07:07.776071+00
05f65301-b395-45be-8048-f5081a4fda2e	d7bef5f6-eef2-40b5-af0f-6d707546d119	title	Test File 12	2025-11-20 04:07:07.776106+00
c155dd71-db2b-4cfc-aeb2-4e441bdab9e2	d43dd389-6753-48e2-9a7b-b2693c801499	source	test_file	2025-11-20 04:07:07.790975+00
ea1d94b9-a77f-42db-8e9b-f3d0746020b4	d43dd389-6753-48e2-9a7b-b2693c801499	file_name	SCOT 13_ZB33RK.wk4	2025-11-20 04:07:07.791039+00
892f07c4-64af-4912-8bbc-3f3a83eb8f60	d43dd389-6753-48e2-9a7b-b2693c801499	file_type	File	2025-11-20 04:07:07.791082+00
82051af7-7baf-44fa-a5c6-d5381131e48d	d43dd389-6753-48e2-9a7b-b2693c801499	file_size	11264	2025-11-20 04:07:07.791125+00
a50d0c76-292c-45af-b480-a048457b184a	d43dd389-6753-48e2-9a7b-b2693c801499	rights_copyright	Crown Copyright	2025-11-20 04:07:07.791163+00
514d14ac-90bb-4d94-9f08-6f820f25f097	d43dd389-6753-48e2-9a7b-b2693c801499	legal_status	Public Record(s)	2025-11-20 04:07:07.791201+00
7bc9b6ca-1b58-46d5-a5ed-5c072437db93	d43dd389-6753-48e2-9a7b-b2693c801499	held_by	The National Archives	2025-11-20 04:07:07.791237+00
7ef79f0d-891e-41f2-907b-83c08d29a6cf	d43dd389-6753-48e2-9a7b-b2693c801499	date_last_modified	2025-11-20T04:07:07.790961+00:00	2025-11-20 04:07:07.791273+00
82603c69-588a-442a-9cad-517f48a068ad	d43dd389-6753-48e2-9a7b-b2693c801499	description	Test file for AYR development	2025-11-20 04:07:07.791307+00
078acb5f-8bee-45d2-be0f-7d93e6a84f71	d43dd389-6753-48e2-9a7b-b2693c801499	closure_type	Open	2025-11-20 04:07:07.791342+00
987d9399-62cf-4470-834d-f2734fb82361	d43dd389-6753-48e2-9a7b-b2693c801499	title_closed	false	2025-11-20 04:07:07.791376+00
7d682dbe-308b-4bc8-836f-2b599b184659	d43dd389-6753-48e2-9a7b-b2693c801499	description_closed	false	2025-11-20 04:07:07.791412+00
a4f6923f-667f-4e3f-a005-98c784d1617b	d43dd389-6753-48e2-9a7b-b2693c801499	language	English	2025-11-20 04:07:07.791447+00
15479231-d4c7-4f3d-9aa0-82e313a92f6d	d43dd389-6753-48e2-9a7b-b2693c801499	created_at	2025-11-20T04:07:07.790969+00:00	2025-11-20 04:07:07.791485+00
4b7e3e2b-e325-4c61-af43-09c97ef208d7	d43dd389-6753-48e2-9a7b-b2693c801499	last_transfer_date	2025-11-20T04:07:07.790970+00:00	2025-11-20 04:07:07.79152+00
e4cd2fcc-977d-4774-bf11-5e38f3acc408	d43dd389-6753-48e2-9a7b-b2693c801499	file_format	WK4	2025-11-20 04:07:07.791554+00
0e518b22-2562-4cdd-bdf9-8dfa5fb11cbd	d43dd389-6753-48e2-9a7b-b2693c801499	file_extension	wk4	2025-11-20 04:07:07.791588+00
702fa8a1-cf09-4c89-a1f3-35acd380d40e	d43dd389-6753-48e2-9a7b-b2693c801499	closure_status	Open	2025-11-20 04:07:07.791624+00
cc8739bb-1a4b-42dd-be5a-eda1527a0f1e	d43dd389-6753-48e2-9a7b-b2693c801499	closure_period	0	2025-11-20 04:07:07.791657+00
79e4d094-2b26-48bb-b0ea-4443ac71466d	d43dd389-6753-48e2-9a7b-b2693c801499	foi_exemption_code	None	2025-11-20 04:07:07.791691+00
830d14c4-c00b-4181-9f1b-07a063b619fa	d43dd389-6753-48e2-9a7b-b2693c801499	foi_exemption_code_description	None	2025-11-20 04:07:07.791725+00
fc14f539-a25e-490a-9c49-d05f7c9c89b7	d43dd389-6753-48e2-9a7b-b2693c801499	title	Test File 13	2025-11-20 04:07:07.79176+00
453b1d17-cc4a-4834-9b07-81cf012447b4	838aa45e-a70f-47e8-b76e-9d6732e99921	source	test_file	2025-11-20 04:07:07.805746+00
1c3d169d-7742-4c33-9f8e-8c62502f6c50	838aa45e-a70f-47e8-b76e-9d6732e99921	file_name	SCOT 13_VTC9WP.xls	2025-11-20 04:07:07.805815+00
738d23df-957e-42a9-8394-edecfce55366	838aa45e-a70f-47e8-b76e-9d6732e99921	file_type	File	2025-11-20 04:07:07.805858+00
ec80d013-17f9-49c4-9177-890b8b45b972	838aa45e-a70f-47e8-b76e-9d6732e99921	file_size	12679	2025-11-20 04:07:07.805899+00
2da345a3-f6a3-4925-935a-925b95a71e2d	838aa45e-a70f-47e8-b76e-9d6732e99921	rights_copyright	Crown Copyright	2025-11-20 04:07:07.805936+00
521e52f2-4276-4ccf-8282-3041b3df4b86	838aa45e-a70f-47e8-b76e-9d6732e99921	legal_status	Public Record(s)	2025-11-20 04:07:07.80597+00
19a90266-e3db-42bd-9cfa-87d908840c08	838aa45e-a70f-47e8-b76e-9d6732e99921	held_by	The National Archives	2025-11-20 04:07:07.806003+00
6fad6be6-c9c5-4588-9f3f-12de01680040	838aa45e-a70f-47e8-b76e-9d6732e99921	date_last_modified	2025-11-20T04:07:07.805734+00:00	2025-11-20 04:07:07.806037+00
0909c87b-c57d-44da-ad18-a9eca2fc5b60	838aa45e-a70f-47e8-b76e-9d6732e99921	description	Test file for AYR development	2025-11-20 04:07:07.80607+00
ef559669-eeeb-4ec6-829a-cc9d33a54d97	838aa45e-a70f-47e8-b76e-9d6732e99921	closure_type	Open	2025-11-20 04:07:07.806108+00
771f7182-63f3-4c24-a83c-a4ab04fa5c48	838aa45e-a70f-47e8-b76e-9d6732e99921	title_closed	false	2025-11-20 04:07:07.806144+00
72dbc93e-b9a6-4cf6-9620-bf7522acac70	838aa45e-a70f-47e8-b76e-9d6732e99921	description_closed	false	2025-11-20 04:07:07.806179+00
318d0d4c-c8fe-4379-8611-1068ac377c4e	838aa45e-a70f-47e8-b76e-9d6732e99921	language	English	2025-11-20 04:07:07.806212+00
95df144d-c679-4034-9c36-6fad352efaf3	838aa45e-a70f-47e8-b76e-9d6732e99921	created_at	2025-11-20T04:07:07.805741+00:00	2025-11-20 04:07:07.806246+00
fa8a86c4-7e3b-405c-9b9d-f1e1dbdfc8c6	838aa45e-a70f-47e8-b76e-9d6732e99921	last_transfer_date	2025-11-20T04:07:07.805742+00:00	2025-11-20 04:07:07.806279+00
8e2c3012-8094-4ecf-910c-868cf7c29305	838aa45e-a70f-47e8-b76e-9d6732e99921	file_format	XLS	2025-11-20 04:07:07.806311+00
44e4bbf1-1ff0-48e5-9aaa-d7f9286ecc8b	838aa45e-a70f-47e8-b76e-9d6732e99921	file_extension	xls	2025-11-20 04:07:07.806342+00
da7915b0-cf3c-49ee-9dbc-c8f7e8a52bc5	838aa45e-a70f-47e8-b76e-9d6732e99921	closure_status	Open	2025-11-20 04:07:07.806375+00
5fd5eeb5-54b1-4204-9094-16f312638d45	838aa45e-a70f-47e8-b76e-9d6732e99921	closure_period	0	2025-11-20 04:07:07.806407+00
3fcf0c09-ad36-4fc7-bff5-ba607f626d51	838aa45e-a70f-47e8-b76e-9d6732e99921	foi_exemption_code	None	2025-11-20 04:07:07.80644+00
a0c7dc44-35f1-4602-af80-0255dac3bde3	838aa45e-a70f-47e8-b76e-9d6732e99921	foi_exemption_code_description	None	2025-11-20 04:07:07.806473+00
8ea99d0c-e959-4ac1-958e-fd87dd4f338e	838aa45e-a70f-47e8-b76e-9d6732e99921	title	Test File 14	2025-11-20 04:07:07.806507+00
697aae58-b476-4fb8-becb-d89e1ef11533	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	source	test_file	2025-11-20 04:07:07.824412+00
0e43762d-3ec8-4c5c-9cc2-eff671f3d6e3	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	file_name	SCOT 13_UYT6DV.xlsx	2025-11-20 04:07:07.824471+00
fff35548-d901-4e19-bcf1-9f8b7670fd2b	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	file_type	File	2025-11-20 04:07:07.824518+00
9359718a-b895-4726-8ef4-5673bb8e20f7	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	file_size	12679	2025-11-20 04:07:07.824562+00
c5a0c361-25ec-4e84-b458-41f13aa724bd	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	rights_copyright	Crown Copyright	2025-11-20 04:07:07.824602+00
f4de8af8-ee35-4dbd-b228-d2921c55b406	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	legal_status	Public Record(s)	2025-11-20 04:07:07.82464+00
5bec49d5-c9cc-451e-9e94-889fcf031234	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	held_by	The National Archives	2025-11-20 04:07:07.824677+00
027ec2ae-a562-43ea-98cc-07f8d0f39b26	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	date_last_modified	2025-11-20T04:07:07.824401+00:00	2025-11-20 04:07:07.824713+00
7ecda9b5-e3b2-498b-b473-38258ae4bdda	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	description	Test file for AYR development	2025-11-20 04:07:07.824748+00
0d27b172-9c5f-467b-8cde-614688a99e57	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	closure_type	Open	2025-11-20 04:07:07.824783+00
20324431-05d6-4385-a450-439262afc69e	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	title_closed	false	2025-11-20 04:07:07.824816+00
7a802b51-6b0c-4df5-b2c0-b71bee8f162a	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	description_closed	false	2025-11-20 04:07:07.824852+00
4fff7dfe-2e93-49b2-b06c-46189de233a2	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	language	English	2025-11-20 04:07:07.824885+00
619d26b9-7afb-4d1c-b9d3-1c1bb5d8c775	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	created_at	2025-11-20T04:07:07.824407+00:00	2025-11-20 04:07:07.824919+00
9b050889-b60e-49f3-be2c-25ce56473650	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	last_transfer_date	2025-11-20T04:07:07.824408+00:00	2025-11-20 04:07:07.824955+00
e80045ce-8574-44cb-826f-870439d6399e	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	file_format	XLSX	2025-11-20 04:07:07.824988+00
8338392e-052b-4b07-ba1f-10f958d5cce8	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	file_extension	xlsx	2025-11-20 04:07:07.825022+00
596922e9-ce9b-4c87-8c20-5a54e13a67b8	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	closure_status	Open	2025-11-20 04:07:07.825068+00
2887e90a-f5e3-4c28-a1dd-2abdbeed0fcc	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	closure_period	0	2025-11-20 04:07:07.8251+00
e73e2ae2-a406-4e7e-ac89-c4d94f0c7d3e	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	foi_exemption_code	None	2025-11-20 04:07:07.825134+00
104abbce-d0b3-4df9-9932-8bc64cff1d3f	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	foi_exemption_code_description	None	2025-11-20 04:07:07.825166+00
57a3b5c4-f0ec-4fea-a56e-821190ce83b4	5c0f275f-fb8b-49f9-ab58-d6ce8a3f8aef	title	Test File 15	2025-11-20 04:07:07.825199+00
3f05ce2a-69b4-45ea-b355-bdc355bfddc1	596df45d-8a7f-49c9-b759-2b32c138db11	source	test_file	2025-11-20 04:07:07.84109+00
34438276-08f8-4e91-8b32-b4bb80c9c20e	596df45d-8a7f-49c9-b759-2b32c138db11	file_name	SCOT 13_Z9P524.xml	2025-11-20 04:07:07.841147+00
ed383c4a-5708-4226-a2a1-b9601cb0a1fd	596df45d-8a7f-49c9-b759-2b32c138db11	file_type	File	2025-11-20 04:07:07.841191+00
3a7a9e79-9f04-4a89-8469-d4f22ad1227b	596df45d-8a7f-49c9-b759-2b32c138db11	file_size	7787	2025-11-20 04:07:07.841231+00
8f6a25a0-6e08-46c4-8cb1-265e7d99d7c7	596df45d-8a7f-49c9-b759-2b32c138db11	rights_copyright	Crown Copyright	2025-11-20 04:07:07.841267+00
07958047-a45b-403a-aea2-070c790b9b94	596df45d-8a7f-49c9-b759-2b32c138db11	legal_status	Public Record(s)	2025-11-20 04:07:07.841302+00
69627d65-6a63-42c7-a27e-6acec35bd9b3	596df45d-8a7f-49c9-b759-2b32c138db11	held_by	The National Archives	2025-11-20 04:07:07.841337+00
320b3549-5425-49a8-8300-81aa58624c45	596df45d-8a7f-49c9-b759-2b32c138db11	date_last_modified	2025-11-20T04:07:07.841080+00:00	2025-11-20 04:07:07.84137+00
2e742328-8a8d-4710-8cb9-58fe6d8b0b76	596df45d-8a7f-49c9-b759-2b32c138db11	description	Test file for AYR development	2025-11-20 04:07:07.841404+00
e249a841-bcfc-425e-8752-5ee443a82d55	596df45d-8a7f-49c9-b759-2b32c138db11	closure_type	Open	2025-11-20 04:07:07.841437+00
987af4ff-9fde-44af-b851-ad3bc3a2d223	596df45d-8a7f-49c9-b759-2b32c138db11	title_closed	false	2025-11-20 04:07:07.841471+00
58099097-ee14-4056-93eb-9e891fae155c	596df45d-8a7f-49c9-b759-2b32c138db11	description_closed	false	2025-11-20 04:07:07.841505+00
4b64e872-5b4c-431b-97b0-44892210cd3a	596df45d-8a7f-49c9-b759-2b32c138db11	language	English	2025-11-20 04:07:07.84154+00
4c99f887-d506-4eb7-882f-1e7897181f3d	596df45d-8a7f-49c9-b759-2b32c138db11	created_at	2025-11-20T04:07:07.841085+00:00	2025-11-20 04:07:07.841574+00
a75c1281-eff5-4bc3-978c-1421d5b171c1	596df45d-8a7f-49c9-b759-2b32c138db11	last_transfer_date	2025-11-20T04:07:07.841087+00:00	2025-11-20 04:07:07.84161+00
54c23c46-ac45-4425-90a2-152c29dfd1b1	596df45d-8a7f-49c9-b759-2b32c138db11	file_format	XML	2025-11-20 04:07:07.841644+00
47ad912e-1387-41eb-9acc-d26663e7c116	596df45d-8a7f-49c9-b759-2b32c138db11	file_extension	xml	2025-11-20 04:07:07.841678+00
9d0a15d3-a1e7-4c27-874c-b732a81f060b	596df45d-8a7f-49c9-b759-2b32c138db11	closure_status	Open	2025-11-20 04:07:07.841711+00
5e6ab618-f3b9-4f3e-92c3-5f178b6ea56b	596df45d-8a7f-49c9-b759-2b32c138db11	closure_period	0	2025-11-20 04:07:07.841744+00
313e3ccd-c413-4661-8536-62ab3576f529	596df45d-8a7f-49c9-b759-2b32c138db11	foi_exemption_code	None	2025-11-20 04:07:07.841778+00
072e1b78-16ab-4443-917f-379340d45e6e	596df45d-8a7f-49c9-b759-2b32c138db11	foi_exemption_code_description	None	2025-11-20 04:07:07.841812+00
c5d16ee4-99f5-4a1d-bf27-ba36ed74253d	596df45d-8a7f-49c9-b759-2b32c138db11	title	Test File 16	2025-11-20 04:07:07.841845+00
1b419187-75c7-4eda-ae35-908ce188dab6	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	source	test_file	2025-11-25 08:55:40.664385+00
048121de-32f4-48a7-a782-c7cc89775577	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	file_name	SCOT 13_6YTFTC.jpg	2025-11-25 08:55:40.664476+00
6c52e3ff-4ef5-462f-8323-8ac938ac2c2c	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	file_type	File	2025-11-25 08:55:40.664533+00
04972541-c67d-44a7-8270-02cc1275405c	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	file_size	2967064	2025-11-25 08:55:40.664583+00
f122eeec-c7e4-4a6a-969d-e8e9d74e3191	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	rights_copyright	Crown Copyright	2025-11-25 08:55:40.66463+00
533fb7c0-bc2f-40a0-92c7-de21bd7d081c	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	legal_status	Public Record(s)	2025-11-25 08:55:40.664677+00
14488ee1-09d4-4fde-83f1-85217cae7571	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	held_by	The National Archives	2025-11-25 08:55:40.664721+00
002c1d2a-daf5-41af-82d6-dc415417260a	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	date_last_modified	2025-11-25T08:55:40.664372+00:00	2025-11-25 08:55:40.664764+00
f592922a-67eb-4ec3-af0e-b3245b216727	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	description	Test file for AYR development	2025-11-25 08:55:40.664808+00
8020b0c2-59e8-4142-838a-aef20103c3ac	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	closure_type	Open	2025-11-25 08:55:40.66485+00
dfea2c37-322b-41a7-9702-41815f10c319	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	title_closed	false	2025-11-25 08:55:40.664891+00
16909b2c-b3a9-45f0-b640-521e6a8970a5	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	description_closed	false	2025-11-25 08:55:40.664933+00
2556fcd4-c029-4124-afbe-e717de839b64	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	language	English	2025-11-25 08:55:40.664975+00
976201b9-70a3-45a5-bde8-38719ee18d5e	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	created_at	2025-11-25T08:55:40.664380+00:00	2025-11-25 08:55:40.665017+00
bc516c4b-1f0f-479f-98d7-18088c804160	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	last_transfer_date	2025-11-25T08:55:40.664381+00:00	2025-11-25 08:55:40.665058+00
8c5b4477-c501-40c1-9dc2-54517df73880	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	file_format	JPG	2025-11-25 08:55:40.665098+00
98c3a8cf-ddc0-4df2-8016-ba19caa97b18	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	file_extension	jpg	2025-11-25 08:55:40.665138+00
1bd9f508-8c68-4083-bd05-c19d1aeccb90	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	closure_status	Open	2025-11-25 08:55:40.665178+00
c53c729e-ccc3-4e67-80d4-0e0ad913bcd3	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	closure_period	0	2025-11-25 08:55:40.665219+00
5eb47a51-5b1f-4968-9715-a5047f68c29c	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	foi_exemption_code	None	2025-11-25 08:55:40.665262+00
c29ed83b-b35e-4bf8-a838-067b884df9c4	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	foi_exemption_code_description	None	2025-11-25 08:55:40.665303+00
73421409-2904-428c-a5ed-832dc60ebc11	4e21efa3-c543-46ca-ad2f-6d0c6bba8a1b	title	Test File 1	2025-11-25 08:55:40.665342+00
a68da3f5-b309-4fd6-aef1-f8405a6996e8	61a712eb-0600-40c8-88ad-221de3390b4d	source	test_file	2025-11-25 08:55:40.709119+00
32b3b021-2072-436a-ba51-08e5508a9ffe	61a712eb-0600-40c8-88ad-221de3390b4d	file_name	SCOT 13_G85D3R.png	2025-11-25 08:55:40.709183+00
27b48c27-37b4-47a0-8c33-922a2536e135	61a712eb-0600-40c8-88ad-221de3390b4d	file_type	File	2025-11-25 08:55:40.709228+00
feab1ba6-d5f9-46c1-849e-5044620309b2	61a712eb-0600-40c8-88ad-221de3390b4d	file_size	2914861	2025-11-25 08:55:40.709268+00
cfa07ca1-2142-4f80-bdd0-179a2cad4109	61a712eb-0600-40c8-88ad-221de3390b4d	rights_copyright	Crown Copyright	2025-11-25 08:55:40.709311+00
52d362f7-fa66-4224-9631-5c7efc5e4193	61a712eb-0600-40c8-88ad-221de3390b4d	legal_status	Public Record(s)	2025-11-25 08:55:40.709349+00
8197ad03-fb23-476c-9ee6-acc91f42f8f8	61a712eb-0600-40c8-88ad-221de3390b4d	held_by	The National Archives	2025-11-25 08:55:40.709388+00
06f8b3ff-88ac-40c1-9130-90ec007e07be	61a712eb-0600-40c8-88ad-221de3390b4d	date_last_modified	2025-11-25T08:55:40.709104+00:00	2025-11-25 08:55:40.709425+00
1665b1b1-599d-4e62-a688-42bed33bae91	61a712eb-0600-40c8-88ad-221de3390b4d	description	Test file for AYR development	2025-11-25 08:55:40.70946+00
30d6a313-56c2-4747-bcdb-f08a0d1fdf1c	61a712eb-0600-40c8-88ad-221de3390b4d	closure_type	Open	2025-11-25 08:55:40.709495+00
221433c4-f030-4376-8a50-29626b679040	61a712eb-0600-40c8-88ad-221de3390b4d	title_closed	false	2025-11-25 08:55:40.709528+00
ac4346c6-588d-4781-a5d9-5317f4070674	61a712eb-0600-40c8-88ad-221de3390b4d	description_closed	false	2025-11-25 08:55:40.709563+00
111d6096-9299-415d-9702-b10a400a3b6f	61a712eb-0600-40c8-88ad-221de3390b4d	language	English	2025-11-25 08:55:40.709598+00
3e2c83c6-30a3-4b81-9b41-89e949ce21c1	61a712eb-0600-40c8-88ad-221de3390b4d	created_at	2025-11-25T08:55:40.709113+00:00	2025-11-25 08:55:40.709634+00
92775923-d53f-4bd9-9677-ba79628cb9c8	61a712eb-0600-40c8-88ad-221de3390b4d	last_transfer_date	2025-11-25T08:55:40.709115+00:00	2025-11-25 08:55:40.709675+00
b62a6915-73b3-42bc-aa6e-5ac884cedf5d	61a712eb-0600-40c8-88ad-221de3390b4d	file_format	PNG	2025-11-25 08:55:40.709714+00
fe12c571-dd4b-4291-bb01-770072ec9666	61a712eb-0600-40c8-88ad-221de3390b4d	file_extension	png	2025-11-25 08:55:40.709755+00
5666f54d-22bc-46e9-876c-63d4e4cccef8	61a712eb-0600-40c8-88ad-221de3390b4d	closure_status	Open	2025-11-25 08:55:40.709795+00
abec7591-fa17-4cba-99e1-d08778a1f7c8	61a712eb-0600-40c8-88ad-221de3390b4d	closure_period	0	2025-11-25 08:55:40.709834+00
d15f6408-a837-4134-b0a6-8b0f5fe8df8d	61a712eb-0600-40c8-88ad-221de3390b4d	foi_exemption_code	None	2025-11-25 08:55:40.709874+00
262f93d1-c767-4076-ad3b-bf739e53d57b	61a712eb-0600-40c8-88ad-221de3390b4d	foi_exemption_code_description	None	2025-11-25 08:55:40.709913+00
e6927aa1-1059-484c-b4cc-1aa613d30836	61a712eb-0600-40c8-88ad-221de3390b4d	title	Test File 2	2025-11-25 08:55:40.709953+00
\.


--
-- Data for Name: Series; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."Series" ("SeriesId", "BodyId", "Name", "Description") FROM stdin;
93ed0101-2318-45ab-8730-c681958ded7e	4654e9f9-335b-4ab1-acd8-edff54f908d4	AYR 1	AYR 1
8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	8ccc8cd1-c0ee-431d-afad-70cf404ba337	MOCK1 123	MOCK1 123
1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	TSTA 1	TSTA 1
5729cee7-a930-4385-bb3b-5137af8a6f61	b51c2f65-68e1-4dad-9115-eccf31929234	SCOT 13	Test Series Description
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

\unrestrict 9kyEghew8MAVJtsihSYalXQqSynlJscb0q94pvGEStduenbhroB1CJOQV1V03et
