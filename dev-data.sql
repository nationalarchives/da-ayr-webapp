--
-- PostgreSQL database dump
--

-- Dumped from database version 15.5
-- Dumped by pg_dump version 16.2

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
646056e7-4e94-447d-a5ef-d2f1b795ffa0	yara	4.3.1
8b5e288b-d877-4ba6-adcc-a7d277acd254	yara	4.3.1
025df6ca-cfa9-4ffc-ad59-8eed879258e1	yara	4.3.1
cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	yara	4.3.1
250b162f-df9a-4d27-b237-c9c1a844a7d1	yara	4.3.1
318abd3b-d2b7-4f45-9785-5094c007dfea	yara	4.3.1
48e6132b-1a08-40a3-a704-156d88737f83	yara	4.3.1
cf4c871f-786b-4691-b77f-755bba24462c	yara	4.3.1
7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	yara	4.3.1
3b5431f7-9166-4c9b-bc20-72a2a4dd780a	yara	4.3.1
b6ce8b02-c70d-4771-a4de-d4da189822da	yara	4.3.1
6302998c-97cb-4549-9f60-6eb861314c35	yara	4.3.1
a3e0759f-2d8c-427c-9bb0-6130335e85a5	yara	4.3.1
906097d6-c80c-4e46-aab8-f0743807f984	yara	4.3.1
a65558bb-cedc-4a7a-a518-aa63b0492b91	yara	4.3.1
34e782c4-34dd-44de-96b5-f6d004f26239	yara	4.3.1
7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	yara	4.3.1
1272e8c2-0331-4b11-9379-00ae81e42083	yara	4.3.1
643d14b9-e846-4f06-9efb-e80b0c7894e8	yara	4.3.1
2ba441f8-413e-4a96-8919-a0e7ef8e8029	yara	4.3.1
9e2404a9-ba2a-44d7-8fe8-648d053af548	yara	4.3.1
2574830a-7ea1-4eea-8f4a-e6058437e848	yara	4.3.1
0f52912b-78a6-4e58-bda7-0c2f636e2040	yara	4.3.1
ac20000c-eef8-4941-93ab-6ba684076bee	yara	4.3.1
c6e5150c-2cb1-4f5f-8782-e8eab94dc562	yara	4.3.1
2a426981-df85-4c94-9885-8b7760c86115	yara	4.3.1
b43f6060-6df6-4cf4-a57a-e29f208e17ed	yara	4.3.1
f26f1475-7652-4e8d-8052-cb68ac009b36	yara	4.3.1
097e1fde-70f5-4eef-9a46-c85ea4350bf7	yara	4.3.1
8f67e50d-9082-42af-84e3-80cb616a6665	yara	4.3.1
df115d92-f1cb-41dc-95f0-1f3bfe07ae45	yara	4.3.1
2be81626-7443-4e1f-b228-c9aa9942cd32	yara	4.3.1
3c65376c-bed9-44d0-b391-53acbe561ec8	yara	4.3.1
8f710b6f-ac45-4a1d-b560-873618c253db	yara	4.3.1
c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	yara	4.3.1
81068c3a-ae92-4d1b-8626-321a8437a9b0	yara	4.3.1
e0321af1-38b5-4111-a3e6-261d04bf7677	yara	4.3.1
f550d5b9-2570-4557-8435-cfaca366cee5	yara	4.3.1
b430325c-3242-4d12-bb14-16025837f896	yara	4.3.1
e499f9cf-b947-4f69-8300-24dd0a3aaa03	yara	4.3.1
1263462f-8bbf-47cf-963d-2e7ef79c281d	yara	4.3.1
afcf7478-56ee-4872-9d92-da4655a8972c	yara	4.3.1
2d3efaf1-154b-4c72-bea6-e220e092ab0c	yara	4.3.1
909cf5b8-bd73-432e-bbda-465f20bef6bd	yara	4.3.1
3727c79b-6fac-4f80-b6d9-6fc08a38f383	yara	4.3.1
871b2502-5521-4423-9b0d-4bc243802f96	yara	4.3.1
5d42f6f8-554e-4f22-882e-6a664846a532	yara	4.3.1
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
e308bf4e-b6a4-49ff-a039-7c956befa75e	yara	4.3.1
1ac109a8-c542-4030-8826-c8d614b1943e	yara	4.3.1
6d6fd827-7fdc-49d9-9cf4-a82ec1109941	yara	4.3.1
97243031-46b9-42fe-a107-79a4031d0998	yara	4.3.1
ca63b581-4523-4fde-9009-eade85f2677a	yara	4.3.1
c3e894db-bff4-4e35-9d84-ab6a46800b5e	yara	4.3.1
bdf293f4-22ab-49ea-8a4f-4c313170915d	yara	4.3.1
1fca1fc2-fcb3-447b-8418-f6e4a5728efe	yara	4.3.1
9595f34d-9c81-4cdc-b57b-af76815d904d	yara	4.3.1
769f8459-c5db-42a8-a01b-62a216c390ed	yara	4.3.1
4f5b8b4c-30f9-4efc-a159-fa987b1db093	yara	4.3.1
bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	yara	4.3.1
761e50f5-8441-4e55-884e-26eaf8e12abe	yara	4.3.1
ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	yara	4.3.1
e20dd7a5-ec42-4d62-86ee-a71f875035a2	yara	4.3.1
41f94132-dbdf-43e4-a327-cc5bae432f98	yara	4.3.1
839fce83-82f6-462f-a186-50a27fed68e0	yara	4.3.1
d38f9713-7361-4713-b93a-64aa6beafc1b	yara	4.3.1
28897cd6-3348-4b57-bff6-521c7b120c0c	yara	4.3.1
eaa0b74a-a889-4ea0-ab28-0237d973bdb9	yara	4.3.1
c4f5ca21-2814-4d01-863e-244cfae874fb	yara	4.3.1
2a682900-0f4e-408e-a3ea-ccda2ce52799	yara	4.3.1
0492a61c-801c-4306-9692-f51f17363ef5	yara	4.3.1
edb2c00c-f5be-4677-80d2-509d2aff5d3d	yara	4.3.1
7a5aeb37-98d4-41b4-89d3-d983053371c6	yara	4.3.1
271ca5ba-d409-4400-8410-d60d1821254d	yara	4.3.1
1768f4d3-3204-43aa-9a7b-cecf065a5a6c	yara	4.3.1
71f8205b-bd25-4104-815a-06d3f5f05da1	yara	4.3.1
adb24c10-04df-4d4c-8ed0-42077dd6b012	yara	4.3.1
2bc446e6-9dbb-4c37-abf5-d49ae11483b3	yara	4.3.1
a4024256-ae42-4320-abfd-1057c755d5cb	yara	4.3.1
df1efb2b-3ab0-4913-a93e-fedb84cde33e	yara	4.3.1
4c696e62-b48d-40c7-b32c-dd9f9f59a48c	yara	4.3.1
b753468a-9a29-45b9-bd4f-2ed7c7c26691	yara	4.3.1
07f44a3d-21f9-4b02-9846-c5fd3fa72244	yara	4.3.1
8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	yara	4.3.1
9a7fb80e-2b4d-4411-9afd-d8d33e312327	yara	4.3.1
f9b72ffa-672c-4d0d-aff5-54da5e335e32	yara	4.3.1
e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	yara	4.3.1
e5788ac9-7a20-42bd-b61c-e001d781bcce	yara	4.3.1
e211826c-bfe5-45ea-a080-4cfcd696678c	yara	4.3.1
5f9c5169-2f65-4e5c-a075-0979a579846e	yara	4.3.1
fd947cb3-6917-4162-8068-92ed11d7371a	yara	4.3.1
9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	yara	4.3.1
4fc79a0d-8ae8-4022-9950-7dd837ffe21d	yara	4.3.1
228741f8-65d8-4f24-9a95-6afaf594990a	yara	4.3.1
e8b5ae9d-e696-423d-8d8c-a5583faae6f8	yara	4.3.1
df9bd5f6-0333-4742-bd2e-a479e0ac1c11	yara	4.3.1
99bff3d0-cc22-4082-b6b2-96daa763c5cc	yara	4.3.1
56dce91b-7850-4708-a0f3-5c64bf00f350	yara	4.3.1
505060b5-aac2-4422-b663-6a825da1902a	yara	4.3.1
62f41529-b22a-4eae-bb05-2ce5ddc6fb70	yara	4.3.1
9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	yara	4.3.1
062b8e3c-c6ca-4df3-9ef2-909a72b59d78	yara	4.3.1
baba5d37-db25-40ea-b94c-81cc68ff580f	yara	4.3.1
898aab0b-e0bc-424b-b885-15d13578eea5	yara	4.3.1
1afdc98f-410b-4071-9369-5406ebbf3fd6	yara	4.3.1
21373a76-9a68-4881-8df7-c17f574b9874	yara	4.3.1
c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	yara	4.3.1
0280dca5-97e5-42de-9b9b-4ed673bf8b86	yara	4.3.1
2440bcc9-439b-4735-8183-45da8658614a	yara	4.3.1
03ebf08f-ad7b-4036-ba66-774071d6ea29	yara	4.3.1
b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	yara	4.3.1
4f663ad9-80a8-46ee-a465-babc4bbd3470	yara	4.3.1
b7728c35-3e92-4177-9114-4a4b6d084f56	yara	4.3.1
c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	yara	4.3.1
c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	yara	4.3.1
78ec383b-1d3d-4c2d-8469-5d5f62b7300a	yara	4.3.1
8ffacc5a-443a-4568-a5c9-c9741955b40f	E2E tests software	E2E tests software version
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	E2E tests software	E2E tests software version
47526ba9-88e5-4cc8-8bc1-d682a10fa270	E2E tests software	E2E tests software version
\.


--
-- Data for Name: Body; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."Body" ("BodyId", "Name", "Description") FROM stdin;
8ccc8cd1-c0ee-431d-afad-70cf404ba337	Mock 1 Department	Mock 1 Department
c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	Testing A	Testing A
9ced8d31-ea58-4794-9582-4b4de1409d59	MOCK1 Department	MOCK1 Department
\.


--
-- Data for Name: Consignment; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."Consignment" ("ConsignmentId", "BodyId", "SeriesId", "ConsignmentReference", "ConsignmentType", "IncludeTopLevelFolder", "ContactName", "ContactEmail", "TransferStartDatetime", "TransferCompleteDatetime", "ExportDatetime", "CreatedDatetime") FROM stdin;
b4a8379c-0767-4a9b-8537-181aed23e837	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JMQK	standard	f	Test First Name Test Last Name	e4dnuhvq@testsomething.com	2024-02-07 14:26:31+00	2024-02-07 14:26:42+00	2024-02-07 14:27:23+00	2024-02-20 10:06:04.777+00
8cb97d25-5607-477e-aa79-eaae89aa4dc5	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JQJV	standard	f	Test First Name Test Last Name	cnrs6ayg@testsomething.com	2024-02-12 11:27:00+00	2024-02-12 11:27:11+00	2024-02-12 11:27:55+00	2024-02-20 10:08:37.659+00
696951f9-f52d-4d6e-9b9e-dfe4f0cb2d3a	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JMHS	standard	f	Test First Name Test Last Name	eipzkbx3@testsomething.com	2024-02-07 10:53:03+00	2024-02-07 10:53:11+00	2024-02-07 10:53:52+00	2024-02-20 10:14:59.722+00
64c30a21-d97d-45c7-ac77-1fe905f48add	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-JMF6	standard	f	Test First Name Test Last Name	u7cxznnd@testsomething.com	2024-02-07 10:52:23+00	2024-02-07 10:52:56+00	2024-02-07 10:53:39+00	2024-02-20 10:16:26.092+00
9b92cbc6-b408-404a-b247-e5f419f70cae	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2024-H5DN	standard	f	Phil Ashworth	phil.ashworth@nationalarchives.gov.uk	2024-01-25 09:14:13+00	2024-01-25 09:17:18+00	2024-01-25 09:18:01+00	2024-02-20 10:29:24.189+00
bf203811-357a-45a8-8b38-770d1580691c	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2023-TMT	standard	t	Paul Young	paul.young@something2.com	2023-08-09 11:30:32+00	2023-08-09 11:40:56+00	2023-08-09 11:41:45+00	2024-02-20 10:31:13.751+00
bf883c45-706f-4882-bd62-7177bf0de7a0	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2023-TH4	standard	f	Paul Young	paul.young@something2.com	2023-08-09 10:47:40+00	2023-08-09 11:26:23+00	2023-08-09 11:27:12+00	2024-02-20 10:32:23.499+00
df05b8b8-c222-47c3-903b-9b7f2a8aa1c6	9ced8d31-ea58-4794-9582-4b4de1409d59	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2023-MNJ	standard	f	Test First Name Test Last Name	ufcco8tw@testsomething.com	2023-07-28 09:32:34+00	2023-07-28 09:34:05+00	2023-07-28 09:34:45+00	2024-02-20 10:33:39.34+00
016031db-1398-4fe4-b743-630aa82ea32a	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2023-GXFH	standard	t	Paul Young	paul.young@something2.com	2023-11-30 15:32:58+00	2023-11-30 15:46:20+00	2023-11-30 15:47:09+00	2024-02-20 10:34:51.409+00
3184c737-fe10-4493-8025-77adc5062a84	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-J42R	standard	f	Test First Name Test Last Name	xzbu9vs0@testsomething.com	2024-02-19 08:32:59+00	2024-02-19 08:33:38+00	2024-02-19 08:34:20+00	2024-02-20 16:23:56.124+00
436d6273-fcdb-454e-a9a5-8f55fd064457	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	TDR-2023-BV6	standard	f	Paul Young	paul.young@something2.com	2023-10-18 08:46:20+00	2023-10-18 09:44:07+00	2023-10-18 09:44:51+00	2024-02-20 16:44:57.314+00
2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-J67H	standard	f	Phil Ashworth	phil.ashworth@nationalarchives.gov.uk	2024-02-21 10:01:26+00	2024-02-21 10:13:35+00	2024-02-21 10:14:24+00	2024-02-21 10:20:53.939+00
580472ad-59bb-4718-8f30-7a7bcb6d6b7c	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-KBDM	standard	f	Phil Ashworth	phil.ashworth@nationalarchives.gov.uk	2024-02-22 09:18:31+00	2024-02-22 09:23:20+00	2024-02-22 09:24:04+00	2024-02-22 09:26:27.25+00
b338ab08-1f34-4ad2-8ff0-f2013d859499	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-KBHL	standard	f	Phil Ashworth	phil.ashworth@nationalarchives.gov.uk	2024-02-22 13:38:16+00	2024-02-22 13:44:35+00	2024-02-22 13:45:16+00	2024-02-22 13:46:05.229+00
a03363ac-7e7b-4b92-817e-72ba6423edd5	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-KBHM	standard	t	Phil Ashworth	phil.ashworth@nationalarchives.gov.uk	2024-02-22 14:44:51+00	2024-02-22 14:47:06+00	2024-02-22 14:47:55+00	2024-02-22 15:28:24.651+00
2fd4e03e-5913-4c04-b4f2-5a823fafd430	8ccc8cd1-c0ee-431d-afad-70cf404ba337	8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	TDR-2024-KKX4	standard	f	Test First Name Test Last Name	vskf5utn@testsomething.com	2024-03-05 15:05:30+00	2024-03-05 15:05:38+00	2024-03-05 15:06:21+00	2024-03-06 10:43:30.509+00
\.


--
-- Data for Name: FFIDMetadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."FFIDMetadata" ("FileId", "Extension", "PUID", "FormatName", "ExtensionMismatch", "FFID-Software", "FFID-SoftwareVersion", "FFID-BinarySignatureFileVersion", "FFID-ContainerSignatureFileVersion") FROM stdin;
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
646056e7-4e94-447d-a5ef-d2f1b795ffa0				false	Droid	6.7.0	116	20231127
8b5e288b-d877-4ba6-adcc-a7d277acd254	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
025df6ca-cfa9-4ffc-ad59-8eed879258e1	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
250b162f-df9a-4d27-b237-c9c1a844a7d1	ppt	fmt/126	Microsoft Powerpoint 2000 OLE2	false	Droid	6.7.0	116	20231127
318abd3b-d2b7-4f45-9785-5094c007dfea	doc	fmt/40	Microsoft Word 97 OLE2	false	Droid	6.7.0	116	20231127
48e6132b-1a08-40a3-a704-156d88737f83	png	fmt/12	Portable Network Graphics	false	Droid	6.7.0	116	20231127
cf4c871f-786b-4691-b77f-755bba24462c	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
3b5431f7-9166-4c9b-bc20-72a2a4dd780a	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
b6ce8b02-c70d-4771-a4de-d4da189822da	db	fmt/682	Microsoft Thumbs.db XP	false	Droid	6.7.0	116	20231127
6302998c-97cb-4549-9f60-6eb861314c35	pptx	fmt/215	Microsoft Powerpoint 2007 OOXML	false	Droid	6.7.0	116	20231127
a3e0759f-2d8c-427c-9bb0-6130335e85a5	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
906097d6-c80c-4e46-aab8-f0743807f984	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
a65558bb-cedc-4a7a-a518-aa63b0492b91	msg	x-fmt/430	Microsoft Outlook Email Message	false	Droid	6.7.0	116	20231127
34e782c4-34dd-44de-96b5-f6d004f26239	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	csv	x-fmt/18	Comma Separated Values	false	Droid	6.7.0	116	20231127
1272e8c2-0331-4b11-9379-00ae81e42083	png	fmt/12	\N	\N	Droid	6.6.1	111	20230510
643d14b9-e846-4f06-9efb-e80b0c7894e8	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
2ba441f8-413e-4a96-8919-a0e7ef8e8029	ppt	fmt/126	\N	\N	Droid	6.6.1	111	20230510
9e2404a9-ba2a-44d7-8fe8-648d053af548	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
2574830a-7ea1-4eea-8f4a-e6058437e848	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
0f52912b-78a6-4e58-bda7-0c2f636e2040	doc	fmt/40	\N	\N	Droid	6.6.1	111	20230510
ac20000c-eef8-4941-93ab-6ba684076bee	msg	x-fmt/430	\N	\N	Droid	6.6.1	111	20230510
c6e5150c-2cb1-4f5f-8782-e8eab94dc562	pptx	fmt/215	\N	\N	Droid	6.6.1	111	20230510
2a426981-df85-4c94-9885-8b7760c86115	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
b43f6060-6df6-4cf4-a57a-e29f208e17ed	csv	x-fmt/18	\N	\N	Droid	6.6.1	111	20230510
f26f1475-7652-4e8d-8052-cb68ac009b36	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
097e1fde-70f5-4eef-9a46-c85ea4350bf7	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
8f67e50d-9082-42af-84e3-80cb616a6665	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
df115d92-f1cb-41dc-95f0-1f3bfe07ae45	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
2be81626-7443-4e1f-b228-c9aa9942cd32	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
3c65376c-bed9-44d0-b391-53acbe561ec8	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
8f710b6f-ac45-4a1d-b560-873618c253db	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	pptx	fmt/215	\N	\N	Droid	6.6.1	111	20230510
81068c3a-ae92-4d1b-8626-321a8437a9b0	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
e0321af1-38b5-4111-a3e6-261d04bf7677	doc	fmt/40	\N	\N	Droid	6.6.1	111	20230510
f550d5b9-2570-4557-8435-cfaca366cee5	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
b430325c-3242-4d12-bb14-16025837f896	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
e499f9cf-b947-4f69-8300-24dd0a3aaa03	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
1263462f-8bbf-47cf-963d-2e7ef79c281d	msg	x-fmt/430	\N	\N	Droid	6.6.1	111	20230510
afcf7478-56ee-4872-9d92-da4655a8972c	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
2d3efaf1-154b-4c72-bea6-e220e092ab0c	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
909cf5b8-bd73-432e-bbda-465f20bef6bd	csv	x-fmt/18	\N	\N	Droid	6.6.1	111	20230510
3727c79b-6fac-4f80-b6d9-6fc08a38f383	ppt	fmt/126	\N	\N	Droid	6.6.1	111	20230510
871b2502-5521-4423-9b0d-4bc243802f96	png	fmt/12	\N	\N	Droid	6.6.1	111	20230510
5d42f6f8-554e-4f22-882e-6a664846a532	docx	fmt/412	\N	\N	Droid	6.6.1	111	20230510
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
e308bf4e-b6a4-49ff-a039-7c956befa75e	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
1ac109a8-c542-4030-8826-c8d614b1943e	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
6d6fd827-7fdc-49d9-9cf4-a82ec1109941	doc	fmt/40	Microsoft Word 97 OLE2	false	Droid	6.7.0	116	20231127
97243031-46b9-42fe-a107-79a4031d0998	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
ca63b581-4523-4fde-9009-eade85f2677a	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
c3e894db-bff4-4e35-9d84-ab6a46800b5e	db	fmt/682	Microsoft Thumbs.db XP	false	Droid	6.7.0	116	20231127
bdf293f4-22ab-49ea-8a4f-4c313170915d	png	fmt/12	Portable Network Graphics	false	Droid	6.7.0	116	20231127
1fca1fc2-fcb3-447b-8418-f6e4a5728efe	pptx	fmt/215	Microsoft Powerpoint 2007 OOXML	false	Droid	6.7.0	116	20231127
9595f34d-9c81-4cdc-b57b-af76815d904d	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
769f8459-c5db-42a8-a01b-62a216c390ed	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
4f5b8b4c-30f9-4efc-a159-fa987b1db093				false	Droid	6.7.0	116	20231127
bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
761e50f5-8441-4e55-884e-26eaf8e12abe	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	ppt	fmt/126	Microsoft Powerpoint 2000 OLE2	false	Droid	6.7.0	116	20231127
e20dd7a5-ec42-4d62-86ee-a71f875035a2	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
41f94132-dbdf-43e4-a327-cc5bae432f98	msg	x-fmt/430	Microsoft Outlook Email Message	false	Droid	6.7.0	116	20231127
839fce83-82f6-462f-a186-50a27fed68e0	csv	x-fmt/18	Comma Separated Values	false	Droid	6.7.0	116	20231127
d38f9713-7361-4713-b93a-64aa6beafc1b	doc	fmt/40	Microsoft Word 97 OLE2	false	Droid	6.7.0	116	20231127
28897cd6-3348-4b57-bff6-521c7b120c0c	pptx	fmt/215	Microsoft Powerpoint 2007 OOXML	false	Droid	6.7.0	116	20231127
eaa0b74a-a889-4ea0-ab28-0237d973bdb9				false	Droid	6.7.0	116	20231127
c4f5ca21-2814-4d01-863e-244cfae874fb	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
2a682900-0f4e-408e-a3ea-ccda2ce52799	ppt	fmt/126	Microsoft Powerpoint 2000 OLE2	false	Droid	6.7.0	116	20231127
0492a61c-801c-4306-9692-f51f17363ef5	png	fmt/12	Portable Network Graphics	false	Droid	6.7.0	116	20231127
edb2c00c-f5be-4677-80d2-509d2aff5d3d	msg	x-fmt/430	Microsoft Outlook Email Message	false	Droid	6.7.0	116	20231127
7a5aeb37-98d4-41b4-89d3-d983053371c6	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
271ca5ba-d409-4400-8410-d60d1821254d	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
1768f4d3-3204-43aa-9a7b-cecf065a5a6c	csv	x-fmt/18	Comma Separated Values	false	Droid	6.7.0	116	20231127
71f8205b-bd25-4104-815a-06d3f5f05da1	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
adb24c10-04df-4d4c-8ed0-42077dd6b012	db	fmt/682	Microsoft Thumbs.db XP	false	Droid	6.7.0	116	20231127
2bc446e6-9dbb-4c37-abf5-d49ae11483b3	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
a4024256-ae42-4320-abfd-1057c755d5cb	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
df1efb2b-3ab0-4913-a93e-fedb84cde33e	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
4c696e62-b48d-40c7-b32c-dd9f9f59a48c	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
b753468a-9a29-45b9-bd4f-2ed7c7c26691	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
07f44a3d-21f9-4b02-9846-c5fd3fa72244	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
9a7fb80e-2b4d-4411-9afd-d8d33e312327	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
f9b72ffa-672c-4d0d-aff5-54da5e335e32	ppt	fmt/126	Microsoft Powerpoint 2000 OLE2	false	Droid	6.7.0	116	20231127
e97ff998-1ef2-496a-9a0c-2d2ad52f67bb				false	Droid	6.7.0	116	20231127
e5788ac9-7a20-42bd-b61c-e001d781bcce	doc	fmt/40	Microsoft Word 97 OLE2	false	Droid	6.7.0	116	20231127
e211826c-bfe5-45ea-a080-4cfcd696678c	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
5f9c5169-2f65-4e5c-a075-0979a579846e	msg	x-fmt/430	Microsoft Outlook Email Message	false	Droid	6.7.0	116	20231127
fd947cb3-6917-4162-8068-92ed11d7371a	db	fmt/682	Microsoft Thumbs.db XP	false	Droid	6.7.0	116	20231127
9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
4fc79a0d-8ae8-4022-9950-7dd837ffe21d	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
228741f8-65d8-4f24-9a95-6afaf594990a	png	fmt/12	Portable Network Graphics	false	Droid	6.7.0	116	20231127
e8b5ae9d-e696-423d-8d8c-a5583faae6f8	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
df9bd5f6-0333-4742-bd2e-a479e0ac1c11	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
99bff3d0-cc22-4082-b6b2-96daa763c5cc	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
56dce91b-7850-4708-a0f3-5c64bf00f350	csv	x-fmt/18	Comma Separated Values	false	Droid	6.7.0	116	20231127
505060b5-aac2-4422-b663-6a825da1902a	pptx	fmt/215	Microsoft Powerpoint 2007 OOXML	false	Droid	6.7.0	116	20231127
62f41529-b22a-4eae-bb05-2ce5ddc6fb70	ppt	fmt/126	Microsoft Powerpoint 2000 OLE2	false	Droid	6.7.0	116	20231127
9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
062b8e3c-c6ca-4df3-9ef2-909a72b59d78				false	Droid	6.7.0	116	20231127
baba5d37-db25-40ea-b94c-81cc68ff580f	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
898aab0b-e0bc-424b-b885-15d13578eea5	db	fmt/682	Microsoft Thumbs.db XP	false	Droid	6.7.0	116	20231127
1afdc98f-410b-4071-9369-5406ebbf3fd6	doc	fmt/40	Microsoft Word 97 OLE2	false	Droid	6.7.0	116	20231127
21373a76-9a68-4881-8df7-c17f574b9874	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
0280dca5-97e5-42de-9b9b-4ed673bf8b86	png	fmt/12	Portable Network Graphics	false	Droid	6.7.0	116	20231127
2440bcc9-439b-4735-8183-45da8658614a	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
03ebf08f-ad7b-4036-ba66-774071d6ea29	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	pptx	fmt/215	Microsoft Powerpoint 2007 OOXML	false	Droid	6.7.0	116	20231127
4f663ad9-80a8-46ee-a465-babc4bbd3470	msg	x-fmt/430	Microsoft Outlook Email Message	false	Droid	6.7.0	116	20231127
b7728c35-3e92-4177-9114-4a4b6d084f56	csv	x-fmt/18	Comma Separated Values	false	Droid	6.7.0	116	20231127
c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
78ec383b-1d3d-4c2d-8469-5d5f62b7300a	docx	fmt/412	Microsoft Word OOXML	false	Droid	6.7.0	116	20231127
8ffacc5a-443a-4568-a5c9-c9741955b40f	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
47526ba9-88e5-4cc8-8bc1-d682a10fa270	txt	x-fmt/111		false	e2e-test-software	e2e-test-software-version	e2e-test-binary-signature-file	e2e-test-container-signature.xml
\.


--
-- Data for Name: File; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."File" ("FileId", "ConsignmentId", "FileType", "FileName", "FilePath", "FileReference", "CiteableReference", "ParentReference", "OriginalFilePath", "Checksum", "CreatedDatetime") FROM stdin;
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
eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	9b92cbc6-b408-404a-b247-e5f419f70cae	Folder	content	data/content	ZD5B3V	TSTA 1/ZD5B3V			\N	2024-02-20 10:29:24.238+00
646056e7-4e94-447d-a5ef-d2f1b795ffa0	9b92cbc6-b408-404a-b247-e5f419f70cae	File	nord-lead-viewer.mxf	data/content/nord-lead-viewer.mxf	ZD5B3K	TSTA 1/ZD5B3K	ZD5B3V		00a3756798b248c7f924711df5947931aac8cdc5a9768d417fc5dc93fd001a8d	2024-02-20 10:29:24.266+00
8b5e288b-d877-4ba6-adcc-a7d277acd254	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	ZD5B47	TSTA 1/ZD5B47	ZD5B3V		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-20 10:29:24.3+00
025df6ca-cfa9-4ffc-ad59-8eed879258e1	9b92cbc6-b408-404a-b247-e5f419f70cae	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	ZD5B45	TSTA 1/ZD5B45	ZD5B3N		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-20 10:29:24.321+00
cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	ZD5B3R	TSTA 1/ZD5B3R	ZD5B43		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-20 10:29:24.341+00
250b162f-df9a-4d27-b237-c9c1a844a7d1	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Gateways.ppt	data/content/Gateways.ppt	ZD5B3W	TSTA 1/ZD5B3W	ZD5B3V		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-20 10:29:24.363+00
318abd3b-d2b7-4f45-9785-5094c007dfea	9b92cbc6-b408-404a-b247-e5f419f70cae	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	ZD5B3S	TSTA 1/ZD5B3S	ZD5B3V		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-20 10:29:24.382+00
48e6132b-1a08-40a3-a704-156d88737f83	9b92cbc6-b408-404a-b247-e5f419f70cae	File	base_de_donnees.png	data/content/base_de_donnees.png	ZD5B48	TSTA 1/ZD5B48	ZD5B3V		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-20 10:29:24.405+00
cf4c871f-786b-4691-b77f-755bba24462c	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	ZD5B46	TSTA 1/ZD5B46	ZD5B43		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-20 10:29:24.428+00
7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	9b92cbc6-b408-404a-b247-e5f419f70cae	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	ZD5B44	TSTA 1/ZD5B44	ZD5B3N		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-20 10:29:24.449+00
3b5431f7-9166-4c9b-bc20-72a2a4dd780a	9b92cbc6-b408-404a-b247-e5f419f70cae	File	DTP.docx	data/content/DTP.docx	ZD5B3P	TSTA 1/ZD5B3P	ZD5B3V		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-20 10:29:24.47+00
b6ce8b02-c70d-4771-a4de-d4da189822da	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Thumbs.db	data/content/Thumbs.db	ZD5B4B	TSTA 1/ZD5B4B	ZD5B3V		48800f0b95ee0c35783c1a3bf23ad1a69c0f83e7edee5daa56663ccdc2f11d3f	2024-02-20 10:29:24.495+00
c4e40b55-ac62-43d8-a26c-dd50b0b339f9	9b92cbc6-b408-404a-b247-e5f419f70cae	Folder	Emergency Response Team	data/content/Emergency Response Team	ZD5B43	TSTA 1/ZD5B43	ZD5B3V		\N	2024-02-20 10:29:24.532+00
80ec3f41-ca06-4589-9826-b2ba2ca17970	9b92cbc6-b408-404a-b247-e5f419f70cae	Folder	Workflows	data/content/Workflows	ZD5B3N	TSTA 1/ZD5B3N	ZD5B3V		\N	2024-02-20 10:29:24.547+00
6302998c-97cb-4549-9f60-6eb861314c35	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Presentation.pptx	data/content/Presentation.pptx	ZD5B42	TSTA 1/ZD5B42	ZD5B3V		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-20 10:29:24.57+00
a3e0759f-2d8c-427c-9bb0-6130335e85a5	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Remove.docx	data/content/Workflows/Remove.docx	ZD5B3T	TSTA 1/ZD5B3T	ZD5B3N		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-20 10:29:24.589+00
906097d6-c80c-4e46-aab8-f0743807f984	9b92cbc6-b408-404a-b247-e5f419f70cae	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	ZD5B3L	TSTA 1/ZD5B3L	ZD5B3N		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-20 10:29:24.622+00
a65558bb-cedc-4a7a-a518-aa63b0492b91	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	ZD5B49	TSTA 1/ZD5B49	ZD5B3V		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-20 10:29:24.645+00
34e782c4-34dd-44de-96b5-f6d004f26239	9b92cbc6-b408-404a-b247-e5f419f70cae	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	ZD5B3M	TSTA 1/ZD5B3M	ZD5B43		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-20 10:29:24.668+00
7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	9b92cbc6-b408-404a-b247-e5f419f70cae	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	ZD5B3J	TSTA 1/ZD5B3J	ZD5B3V		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-20 10:29:24.692+00
1272e8c2-0331-4b11-9379-00ae81e42083	bf203811-357a-45a8-8b38-770d1580691c	File	base_de_donnees.png	data/content/base_de_donnees.png	\N	\N	\N		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-20 10:31:13.804+00
643d14b9-e846-4f06-9efb-e80b0c7894e8	bf203811-357a-45a8-8b38-770d1580691c	File	Remove.docx	data/content/Workflows/Remove.docx	\N	\N	\N		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-20 10:31:13.848+00
2ba441f8-413e-4a96-8919-a0e7ef8e8029	bf203811-357a-45a8-8b38-770d1580691c	File	Gateways.ppt	data/content/Gateways.ppt	\N	\N	\N		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-20 10:31:13.887+00
9e2404a9-ba2a-44d7-8fe8-648d053af548	bf203811-357a-45a8-8b38-770d1580691c	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	\N	\N	\N		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-20 10:31:13.926+00
70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	bf203811-357a-45a8-8b38-770d1580691c	Folder	Emergency Response Team	data/content/Emergency Response Team	\N	\N	\N		\N	2024-02-20 10:31:13.963+00
2574830a-7ea1-4eea-8f4a-e6058437e848	bf203811-357a-45a8-8b38-770d1580691c	File	DTP.docx	data/content/DTP.docx	\N	\N	\N		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-20 10:31:13.995+00
0f52912b-78a6-4e58-bda7-0c2f636e2040	bf203811-357a-45a8-8b38-770d1580691c	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	\N	\N	\N		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-20 10:31:14.034+00
596d6280-2ebf-4f32-a5e5-e54faa73f4ad	bf203811-357a-45a8-8b38-770d1580691c	Folder	Workflows	data/content/Workflows	\N	\N	\N		\N	2024-02-20 10:31:14.08+00
ac20000c-eef8-4941-93ab-6ba684076bee	bf203811-357a-45a8-8b38-770d1580691c	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	\N	\N	\N		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-20 10:31:14.106+00
c6e5150c-2cb1-4f5f-8782-e8eab94dc562	bf203811-357a-45a8-8b38-770d1580691c	File	Presentation.pptx	data/content/Presentation.pptx	\N	\N	\N		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-20 10:31:14.154+00
2a426981-df85-4c94-9885-8b7760c86115	bf203811-357a-45a8-8b38-770d1580691c	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	\N	\N	\N		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-20 10:31:14.205+00
b43f6060-6df6-4cf4-a57a-e29f208e17ed	bf203811-357a-45a8-8b38-770d1580691c	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	\N	\N	\N		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-20 10:31:14.254+00
f26f1475-7652-4e8d-8052-cb68ac009b36	bf203811-357a-45a8-8b38-770d1580691c	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	\N	\N	\N		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-20 10:31:14.3+00
097e1fde-70f5-4eef-9a46-c85ea4350bf7	bf203811-357a-45a8-8b38-770d1580691c	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	\N	\N	\N		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-20 10:31:14.335+00
8f67e50d-9082-42af-84e3-80cb616a6665	bf203811-357a-45a8-8b38-770d1580691c	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	\N	\N	\N		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-20 10:31:14.375+00
df115d92-f1cb-41dc-95f0-1f3bfe07ae45	bf203811-357a-45a8-8b38-770d1580691c	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	\N	\N	\N		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-20 10:31:14.416+00
2be81626-7443-4e1f-b228-c9aa9942cd32	bf203811-357a-45a8-8b38-770d1580691c	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	\N	\N	\N		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-20 10:31:14.48+00
326e55e9-b406-46ef-9570-ca51fb02e944	bf203811-357a-45a8-8b38-770d1580691c	Folder	content	data/content	\N	\N	\N		\N	2024-02-20 10:31:14.522+00
3c65376c-bed9-44d0-b391-53acbe561ec8	bf883c45-706f-4882-bd62-7177bf0de7a0	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	\N	\N	\N		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-20 10:32:23.549+00
8f710b6f-ac45-4a1d-b560-873618c253db	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	\N	\N	\N		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-20 10:32:23.597+00
8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	bf883c45-706f-4882-bd62-7177bf0de7a0	Folder	content	data/content	\N	\N	\N		\N	2024-02-20 10:32:23.631+00
c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Presentation.pptx	data/content/Presentation.pptx	\N	\N	\N		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-20 10:32:23.648+00
81068c3a-ae92-4d1b-8626-321a8437a9b0	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Remove.docx	data/content/Workflows/Remove.docx	\N	\N	\N		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-20 10:32:23.68+00
e0321af1-38b5-4111-a3e6-261d04bf7677	bf883c45-706f-4882-bd62-7177bf0de7a0	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	\N	\N	\N		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-20 10:32:23.714+00
f550d5b9-2570-4557-8435-cfaca366cee5	bf883c45-706f-4882-bd62-7177bf0de7a0	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	\N	\N	\N		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-20 10:32:23.735+00
b430325c-3242-4d12-bb14-16025837f896	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	\N	\N	\N		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-20 10:32:23.759+00
e499f9cf-b947-4f69-8300-24dd0a3aaa03	bf883c45-706f-4882-bd62-7177bf0de7a0	File	DTP.docx	data/content/DTP.docx	\N	\N	\N		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-20 10:32:23.787+00
1263462f-8bbf-47cf-963d-2e7ef79c281d	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	\N	\N	\N		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-20 10:32:23.811+00
c147d5e8-1ff8-46bd-924b-b87db8b143e8	bf883c45-706f-4882-bd62-7177bf0de7a0	Folder	Emergency Response Team	data/content/Emergency Response Team	\N	\N	\N		\N	2024-02-20 10:32:23.837+00
afcf7478-56ee-4872-9d92-da4655a8972c	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	\N	\N	\N		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-20 10:32:23.854+00
2d3efaf1-154b-4c72-bea6-e220e092ab0c	bf883c45-706f-4882-bd62-7177bf0de7a0	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	\N	\N	\N		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-20 10:32:23.872+00
909cf5b8-bd73-432e-bbda-465f20bef6bd	bf883c45-706f-4882-bd62-7177bf0de7a0	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	\N	\N	\N		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-20 10:32:23.89+00
3727c79b-6fac-4f80-b6d9-6fc08a38f383	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Gateways.ppt	data/content/Gateways.ppt	\N	\N	\N		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-20 10:32:23.908+00
dca177e9-c1e9-485d-92ac-384eb81c9919	bf883c45-706f-4882-bd62-7177bf0de7a0	Folder	Workflows	data/content/Workflows	\N	\N	\N		\N	2024-02-20 10:32:23.928+00
871b2502-5521-4423-9b0d-4bc243802f96	bf883c45-706f-4882-bd62-7177bf0de7a0	File	base_de_donnees.png	data/content/base_de_donnees.png	\N	\N	\N		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-20 10:32:23.945+00
5d42f6f8-554e-4f22-882e-6a664846a532	bf883c45-706f-4882-bd62-7177bf0de7a0	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	\N	\N	\N		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-20 10:32:23.969+00
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
e308bf4e-b6a4-49ff-a039-7c956befa75e	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Remove.docx	data/content/Workflows/Remove.docx	ZD7RWC	MOCK1 123/ZD7RWC	ZD7RW7		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-21 10:20:53.988+00
c657f264-8a4c-475e-a121-4adb2bc7766c	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	Folder	Workflows	data/content/Workflows	ZD7RW7	MOCK1 123/ZD7RW7	ZD7RWD		\N	2024-02-21 10:20:54.044+00
1ac109a8-c542-4030-8826-c8d614b1943e	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	ZD7RWM	MOCK1 123/ZD7RWM	ZD7RWD		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-21 10:20:54.085+00
6d6fd827-7fdc-49d9-9cf4-a82ec1109941	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	ZD7RWB	MOCK1 123/ZD7RWB	ZD7RWD		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-21 10:20:54.136+00
97243031-46b9-42fe-a107-79a4031d0998	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	ZD7RW5	MOCK1 123/ZD7RW5	ZD7RW7		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-21 10:20:54.172+00
ca63b581-4523-4fde-9009-eade85f2677a	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	ZD7RWK	MOCK1 123/ZD7RWK	ZD7RW7		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-21 10:20:54.225+00
ecb51977-bfe6-4507-871e-e6844b35caac	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	Folder	Emergency Response Team	data/content/Emergency Response Team	ZD7RWH	MOCK1 123/ZD7RWH	ZD7RWD		\N	2024-02-21 10:20:54.301+00
c3e894db-bff4-4e35-9d84-ab6a46800b5e	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Thumbs.db	data/content/Thumbs.db	ZD7RWR	MOCK1 123/ZD7RWR	ZD7RWD		48800f0b95ee0c35783c1a3bf23ad1a69c0f83e7edee5daa56663ccdc2f11d3f	2024-02-21 10:20:54.335+00
bdf293f4-22ab-49ea-8a4f-4c313170915d	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	base_de_donnees.png	data/content/base_de_donnees.png	ZD7RWN	MOCK1 123/ZD7RWN	ZD7RWD		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-21 10:20:54.375+00
1fca1fc2-fcb3-447b-8418-f6e4a5728efe	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Presentation.pptx	data/content/Presentation.pptx	ZD7RWG	MOCK1 123/ZD7RWG	ZD7RWD		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-21 10:20:54.414+00
9595f34d-9c81-4cdc-b57b-af76815d904d	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	ZD7RWL	MOCK1 123/ZD7RWL	ZD7RWH		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-21 10:20:54.448+00
769f8459-c5db-42a8-a01b-62a216c390ed	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	ZD7RWJ	MOCK1 123/ZD7RWJ	ZD7RW7		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-21 10:20:54.482+00
4f5b8b4c-30f9-4efc-a159-fa987b1db093	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	nord-lead-viewer.mxf	data/content/nord-lead-viewer.mxf	ZD7RW4	MOCK1 123/ZD7RW4	ZD7RWD		00a3756798b248c7f924711df5947931aac8cdc5a9768d417fc5dc93fd001a8d	2024-02-21 10:20:54.522+00
bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	ZD7RW9	MOCK1 123/ZD7RW9	ZD7RWH		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-21 10:20:54.558+00
761e50f5-8441-4e55-884e-26eaf8e12abe	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	ZD7RW6	MOCK1 123/ZD7RW6	ZD7RWH		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-21 10:20:54.589+00
9bf0a29a-863a-4b34-9553-1592981e876c	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	Folder	content	data/content	ZD7RWD	MOCK1 123/ZD7RWD			\N	2024-02-21 10:20:54.629+00
ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Gateways.ppt	data/content/Gateways.ppt	ZD7RWF	MOCK1 123/ZD7RWF	ZD7RWD		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-21 10:20:54.653+00
e20dd7a5-ec42-4d62-86ee-a71f875035a2	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	DTP.docx	data/content/DTP.docx	ZD7RW8	MOCK1 123/ZD7RW8	ZD7RWD		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-21 10:20:54.693+00
41f94132-dbdf-43e4-a327-cc5bae432f98	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	ZD7RWP	MOCK1 123/ZD7RWP	ZD7RWD		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-21 10:20:54.731+00
839fce83-82f6-462f-a186-50a27fed68e0	2a5eb22e-0d59-4f64-ae1b-dd75d1fe81f9	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	ZD7RW3	MOCK1 123/ZD7RW3	ZD7RWD		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-21 10:20:54.765+00
d38f9713-7361-4713-b93a-64aa6beafc1b	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	ZD7VRN	MOCK1 123/ZD7VRN	ZD7VRR		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-22 09:26:27.3+00
a3086873-0df1-457e-9818-8f13f5796d26	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	Folder	Workflows	data/content/Workflows	ZD7VRK	MOCK1 123/ZD7VRK	ZD7VRR		\N	2024-02-22 09:26:27.332+00
28897cd6-3348-4b57-bff6-521c7b120c0c	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Presentation.pptx	data/content/Presentation.pptx	ZD7VRT	MOCK1 123/ZD7VRT	ZD7VRR		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-22 09:26:27.352+00
eaa0b74a-a889-4ea0-ab28-0237d973bdb9	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	nord-lead-viewer.mxf	data/content/nord-lead-viewer.mxf	ZD7VRG	MOCK1 123/ZD7VRG	ZD7VRR		00a3756798b248c7f924711df5947931aac8cdc5a9768d417fc5dc93fd001a8d	2024-02-22 09:26:27.371+00
c4f5ca21-2814-4d01-863e-244cfae874fb	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	ZD7VRH	MOCK1 123/ZD7VRH	ZD7VRK		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-22 09:26:27.389+00
2a682900-0f4e-408e-a3ea-ccda2ce52799	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Gateways.ppt	data/content/Gateways.ppt	ZD7VRS	MOCK1 123/ZD7VRS	ZD7VRR		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-22 09:26:27.411+00
0492a61c-801c-4306-9692-f51f17363ef5	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	base_de_donnees.png	data/content/base_de_donnees.png	ZD7VS5	MOCK1 123/ZD7VS5	ZD7VRR		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-22 09:26:27.441+00
edb2c00c-f5be-4677-80d2-509d2aff5d3d	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	ZD7VS6	MOCK1 123/ZD7VS6	ZD7VRR		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-22 09:26:27.476+00
7a5aeb37-98d4-41b4-89d3-d983053371c6	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	ZD7VS2	MOCK1 123/ZD7VS2	ZD7VRK		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-22 09:26:27.492+00
271ca5ba-d409-4400-8410-d60d1821254d	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	ZD7VS4	MOCK1 123/ZD7VS4	ZD7VRR		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-22 09:26:27.513+00
fdf879e4-3796-45ea-bd54-137a5ea2e4f1	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	Folder	content	data/content	ZD7VRR	MOCK1 123/ZD7VRR			\N	2024-02-22 09:26:27.528+00
1768f4d3-3204-43aa-9a7b-cecf065a5a6c	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	ZD7VRF	MOCK1 123/ZD7VRF	ZD7VRR		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-22 09:26:27.539+00
71f8205b-bd25-4104-815a-06d3f5f05da1	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	ZD7VS3	MOCK1 123/ZD7VS3	ZD7VRV		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-22 09:26:27.557+00
adb24c10-04df-4d4c-8ed0-42077dd6b012	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Thumbs.db	data/content/Thumbs.db	ZD7VS7	MOCK1 123/ZD7VS7	ZD7VRR		48800f0b95ee0c35783c1a3bf23ad1a69c0f83e7edee5daa56663ccdc2f11d3f	2024-02-22 09:26:27.577+00
2bc446e6-9dbb-4c37-abf5-d49ae11483b3	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Remove.docx	data/content/Workflows/Remove.docx	ZD7VRP	MOCK1 123/ZD7VRP	ZD7VRK		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-22 09:26:27.596+00
a4024256-ae42-4320-abfd-1057c755d5cb	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	ZD7VRM	MOCK1 123/ZD7VRM	ZD7VRV		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-22 09:26:27.621+00
df1efb2b-3ab0-4913-a93e-fedb84cde33e	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	ZD7VRJ	MOCK1 123/ZD7VRJ	ZD7VRV		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-22 09:26:27.642+00
4c696e62-b48d-40c7-b32c-dd9f9f59a48c	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	ZD7VRW	MOCK1 123/ZD7VRW	ZD7VRK		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-22 09:26:27.657+00
8b16df3a-d778-435b-bb55-d5b3c594b87d	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	Folder	Emergency Response Team	data/content/Emergency Response Team	ZD7VRV	MOCK1 123/ZD7VRV	ZD7VRR		\N	2024-02-22 09:26:27.672+00
b753468a-9a29-45b9-bd4f-2ed7c7c26691	580472ad-59bb-4718-8f30-7a7bcb6d6b7c	File	DTP.docx	data/content/DTP.docx	ZD7VRL	MOCK1 123/ZD7VRL	ZD7VRR		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-22 09:26:27.682+00
07f44a3d-21f9-4b02-9846-c5fd3fa72244	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	ZD7W6R	MOCK1 123/ZD7W6R	ZD7W6M		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-22 13:46:05.271+00
8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	ZD7W6F	MOCK1 123/ZD7W6F	ZD7W6M		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-22 13:46:05.294+00
9a7fb80e-2b4d-4411-9afd-d8d33e312327	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	ZD7W6B	MOCK1 123/ZD7W6B	ZD7W6M		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-22 13:46:05.311+00
f9b72ffa-672c-4d0d-aff5-54da5e335e32	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Gateways.ppt	data/content/Gateways.ppt	ZD7W6K	MOCK1 123/ZD7W6K	ZD7W6J		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-22 13:46:05.331+00
e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	nord-lead-viewer.mxf	data/content/nord-lead-viewer.mxf	ZD7W68	MOCK1 123/ZD7W68	ZD7W6J		00a3756798b248c7f924711df5947931aac8cdc5a9768d417fc5dc93fd001a8d	2024-02-22 13:46:05.351+00
e5788ac9-7a20-42bd-b61c-e001d781bcce	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	ZD7W6G	MOCK1 123/ZD7W6G	ZD7W6J		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-22 13:46:05.376+00
e211826c-bfe5-45ea-a080-4cfcd696678c	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	ZD7W6N	MOCK1 123/ZD7W6N	ZD7W6C		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-22 13:46:05.395+00
5f9c5169-2f65-4e5c-a075-0979a579846e	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	ZD7W6V	MOCK1 123/ZD7W6V	ZD7W6J		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-22 13:46:05.415+00
fd947cb3-6917-4162-8068-92ed11d7371a	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Thumbs.db	data/content/Thumbs.db	ZD7W6W	MOCK1 123/ZD7W6W	ZD7W6J		48800f0b95ee0c35783c1a3bf23ad1a69c0f83e7edee5daa56663ccdc2f11d3f	2024-02-22 13:46:05.431+00
9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	ZD7W6P	MOCK1 123/ZD7W6P	ZD7W6C		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-22 13:46:05.447+00
4fc79a0d-8ae8-4022-9950-7dd837ffe21d	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	ZD7W69	MOCK1 123/ZD7W69	ZD7W6C		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-22 13:46:05.469+00
228741f8-65d8-4f24-9a95-6afaf594990a	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	base_de_donnees.png	data/content/base_de_donnees.png	ZD7W6T	MOCK1 123/ZD7W6T	ZD7W6J		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-22 13:46:05.488+00
e8b5ae9d-e696-423d-8d8c-a5583faae6f8	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	ZD7W6S	MOCK1 123/ZD7W6S	ZD7W6J		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-22 13:46:05.506+00
df9bd5f6-0333-4742-bd2e-a479e0ac1c11	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Remove.docx	data/content/Workflows/Remove.docx	ZD7W6H	MOCK1 123/ZD7W6H	ZD7W6C		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-22 13:46:05.523+00
268251a2-df75-46b5-ae1a-c1f29da62367	b338ab08-1f34-4ad2-8ff0-f2013d859499	Folder	content	data/content	ZD7W6J	MOCK1 123/ZD7W6J			\N	2024-02-22 13:46:05.54+00
6e80512e-c881-4192-8d7b-4c8b7dcbecca	b338ab08-1f34-4ad2-8ff0-f2013d859499	Folder	Emergency Response Team	data/content/Emergency Response Team	ZD7W6M	MOCK1 123/ZD7W6M	ZD7W6J		\N	2024-02-22 13:46:05.553+00
99bff3d0-cc22-4082-b6b2-96daa763c5cc	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	DTP.docx	data/content/DTP.docx	ZD7W6D	MOCK1 123/ZD7W6D	ZD7W6J		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-22 13:46:05.565+00
ec2ba87e-fb29-409f-82f5-b5419a4a8672	b338ab08-1f34-4ad2-8ff0-f2013d859499	Folder	Workflows	data/content/Workflows	ZD7W6C	MOCK1 123/ZD7W6C	ZD7W6J		\N	2024-02-22 13:46:05.584+00
56dce91b-7850-4708-a0f3-5c64bf00f350	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	ZD7W67	MOCK1 123/ZD7W67	ZD7W6J		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-22 13:46:05.595+00
505060b5-aac2-4422-b663-6a825da1902a	b338ab08-1f34-4ad2-8ff0-f2013d859499	File	Presentation.pptx	data/content/Presentation.pptx	ZD7W6L	MOCK1 123/ZD7W6L	ZD7W6J		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-22 13:46:05.621+00
62f41529-b22a-4eae-bb05-2ce5ddc6fb70	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Gateways.ppt	data/content/Gateways.ppt	ZD7W7D	MOCK1 123/ZD7W7D	ZD7W7C		b7fc8546e36ac8a70a5608eb66a09ff02cafdd1e6639366b095804ba6bd1c7be	2024-02-22 15:28:24.702+00
569d6988-a40f-41d8-904b-179d4ae29931	a03363ac-7e7b-4b92-817e-72ba6423edd5	Folder	Emergency Response Team	data/content/Emergency Response Team	ZD7W7G	MOCK1 123/ZD7W7G	ZD7W7C		\N	2024-02-22 15:28:24.728+00
9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Response Procedure.docx	data/content/Emergency Response Team/Response Procedure.docx	ZD7W78	MOCK1 123/ZD7W78	ZD7W7G		711198f1a80f0e369a849386eb4e893dda4c3fb570d31e21d6be9543a0bf128e	2024-02-22 15:28:24.746+00
062b8e3c-c6ca-4df3-9ef2-909a72b59d78	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	nord-lead-viewer.mxf	data/content/nord-lead-viewer.mxf	ZD7W73	MOCK1 123/ZD7W73	ZD7W7C		00a3756798b248c7f924711df5947931aac8cdc5a9768d417fc5dc93fd001a8d	2024-02-22 15:28:24.768+00
baba5d37-db25-40ea-b94c-81cc68ff580f	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	DTP_ Digital Transfer process diagram v 6.docx	data/content/Workflows/DTP_ Digital Transfer process diagram v 6.docx	ZD7W7J	MOCK1 123/ZD7W7J	ZD7W76		6312ad3a0daf51aa964a4eab1ab3228847368f6271110bdd0a300e13e2bcf744	2024-02-22 15:28:24.788+00
898aab0b-e0bc-424b-b885-15d13578eea5	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Thumbs.db	data/content/Thumbs.db	ZD7W7P	MOCK1 123/ZD7W7P	ZD7W7C		48800f0b95ee0c35783c1a3bf23ad1a69c0f83e7edee5daa56663ccdc2f11d3f	2024-02-22 15:28:24.806+00
1afdc98f-410b-4071-9369-5406ebbf3fd6	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	delivery-form-digital.doc	data/content/delivery-form-digital.doc	ZD7W79	MOCK1 123/ZD7W79	ZD7W7C		3c53ff71e95012e1a4c7559d38eaa248d0767a9126cb2ba9a4afef99f4273423	2024-02-22 15:28:24.826+00
21373a76-9a68-4881-8df7-c17f574b9874	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	DTP.docx	data/content/DTP.docx	ZD7W77	MOCK1 123/ZD7W77	ZD7W7C		6b65b6293d43e94a1243eecd06bb309d72d860b5e8d350c9faf1144526a5baa6	2024-02-22 15:28:24.846+00
c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	DTP_ Digital Transfer process diagram UG.docx	data/content/Workflows/DTP_ Digital Transfer process diagram UG.docx	ZD7W74	MOCK1 123/ZD7W74	ZD7W76		ba6c1792cf7b2f0d9a8c0a7bc4400bde0076ef7d6c98b9b0efe81b24784d5bcc	2024-02-22 15:28:24.884+00
0280dca5-97e5-42de-9b9b-4ed673bf8b86	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	base_de_donnees.png	data/content/base_de_donnees.png	ZD7W7M	MOCK1 123/ZD7W7M	ZD7W7C		ed3b3a1fc6f4057e1be76cfb78a31f486004208fd9b1b110a6f2c88a00724382	2024-02-22 15:28:24.908+00
2440bcc9-439b-4735-8183-45da8658614a	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Response Policy.docx	data/content/Emergency Response Team/Response Policy.docx	ZD7W7K	MOCK1 123/ZD7W7K	ZD7W7G		247004c0b1663df76af2e52824834f281d59dacacb17fcfa7c97a001f8c482e1	2024-02-22 15:28:24.933+00
3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	a03363ac-7e7b-4b92-817e-72ba6423edd5	Folder	content	data/content	ZD7W7C	MOCK1 123/ZD7W7C			\N	2024-02-22 15:28:24.95+00
03ebf08f-ad7b-4036-ba66-774071d6ea29	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Remove.docx	data/content/Workflows/Remove.docx	ZD7W7B	MOCK1 123/ZD7W7B	ZD7W76		866ad48e43dc7f7747de5d6b4623e64f05ef0ffb6b86be0f7d1ef391609cfc10	2024-02-22 15:28:24.972+00
b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Presentation.pptx	data/content/Presentation.pptx	ZD7W7F	MOCK1 123/ZD7W7F	ZD7W7C		08f6b021a4cfcf5be53f9e2185ecd534b825003dab73c08b0140652407873872	2024-02-22 15:28:24.99+00
738262e7-5e16-433d-9c26-030a713aba2a	a03363ac-7e7b-4b92-817e-72ba6423edd5	Folder	Workflows	data/content/Workflows	ZD7W76	MOCK1 123/ZD7W76	ZD7W7C		\N	2024-02-22 15:28:25.02+00
4f663ad9-80a8-46ee-a465-babc4bbd3470	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Digital Transfer training email .msg	data/content/Digital Transfer training email .msg	ZD7W7N	MOCK1 123/ZD7W7N	ZD7W7C		5a3b46d02be7375fc7354d90945c802bda2c7aeddf2880b65c6cfadf75d539df	2024-02-22 15:28:25.033+00
b7728c35-3e92-4177-9114-4a4b6d084f56	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	data/content/tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	ZD7W72	MOCK1 123/ZD7W72	ZD7W7C		41d7487dc7d043d709a5e9174e8ca916333fbd26dfeed0999f638b32ac0f0589	2024-02-22 15:28:25.052+00
c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Emergency Contact Details Paul Young.docx	data/content/Emergency Response Team/Emergency Contact Details Paul Young.docx	ZD7W75	MOCK1 123/ZD7W75	ZD7W7G		4747e87ceaa29ad39fce67f0a7f86a137bdcc9216d60a5b702533bfceb8bbccb	2024-02-22 15:28:25.068+00
c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	Draft DDRO 05.docx	data/content/Draft DDRO 05.docx	ZD7W7L	MOCK1 123/ZD7W7L	ZD7W7C		30d0510e9cfbb5435722cbefed04d8ee754a2210b6ca4f6730125d35f27e8c37	2024-02-22 15:28:25.085+00
78ec383b-1d3d-4c2d-8469-5d5f62b7300a	a03363ac-7e7b-4b92-817e-72ba6423edd5	File	DTP_ Sensitivity review process.docx	data/content/Workflows/DTP_ Sensitivity review process.docx	ZD7W7H	MOCK1 123/ZD7W7H	ZD7W76		70c73d3e2270c90d9d36efcee379bdd44fd61c938f5da707f9d68972cefaca15	2024-02-22 15:28:25.104+00
b5cdde0f-93e8-4975-accf-93372d5774c3	2fd4e03e-5913-4c04-b4f2-5a823fafd430	Folder	original	data/E2E_tests/original	ZD8MCP	MOCK1 123/ZD8MCP	ZD8MCM		\N	2024-03-06 10:43:30.565+00
8ffacc5a-443a-4568-a5c9-c9741955b40f	2fd4e03e-5913-4c04-b4f2-5a823fafd430	File	path0	data/E2E_tests/original/path0	ZD8MCK	MOCK1 123/ZD8MCK	ZD8MCP		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-03-06 10:43:30.624+00
a948a34f-6ba0-4ff2-bef6-a290aec31d3f	2fd4e03e-5913-4c04-b4f2-5a823fafd430	File	path2	data/E2E_tests/original/path2	ZD8MCN	MOCK1 123/ZD8MCN	ZD8MCP		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-03-06 10:43:30.685+00
7fb02107-17e3-4659-a644-69f854a6058d	2fd4e03e-5913-4c04-b4f2-5a823fafd430	Folder	E2E_tests	data/E2E_tests	ZD8MCM	MOCK1 123/ZD8MCM			\N	2024-03-06 10:43:30.768+00
47526ba9-88e5-4cc8-8bc1-d682a10fa270	2fd4e03e-5913-4c04-b4f2-5a823fafd430	File	path1	data/E2E_tests/original/path1	ZD8MCL	MOCK1 123/ZD8MCL	ZD8MCP		e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855	2024-03-06 10:43:30.809+00
\.


--
-- Data for Name: FileMetadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."FileMetadata" ("MetadataId", "FileId", "PropertyName", "Value", "CreatedDatetime") FROM stdin;
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
6bc01c9c-4d21-467a-a83a-d3368485268b	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	file_name	content	2024-02-20 10:29:24.244+00
8d9e61b7-da21-4b00-830d-5a935d568c7d	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	file_type	Folder	2024-02-20 10:29:24.247+00
cc52a320-df6e-495d-96b4-a9d79467b3a2	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	rights_copyright	Crown Copyright	2024-02-20 10:29:24.249+00
c0a397a3-cc8f-4f00-b665-4cfc9fc05825	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	legal_status	Public Record(s)	2024-02-20 10:29:24.252+00
b7dfa980-bad3-4dd2-b93e-38ab01b6f8f9	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	held_by	The National Archives, Kew	2024-02-20 10:29:24.256+00
f6c1618c-06b2-4525-9809-439597df27f9	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	closure_type	Open	2024-02-20 10:29:24.258+00
b69b7440-cfa7-48c8-8498-a5a2e5d71f1d	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	title_closed	false	2024-02-20 10:29:24.26+00
ec143d7f-4984-4376-927e-be25b4045204	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	description_closed	false	2024-02-20 10:29:24.262+00
15e9ac6f-26c7-4c3a-8ac9-a4371a3701af	eb491fd5-0f5a-4ae6-b582-a37f76dae5c6	language	English	2024-02-20 10:29:24.263+00
d860cad0-cf98-4753-b3be-687a8a368a21	646056e7-4e94-447d-a5ef-d2f1b795ffa0	file_name	nord-lead-viewer.mxf	2024-02-20 10:29:24.268+00
33d46608-4f42-457f-8b06-a2ddae37cd7a	646056e7-4e94-447d-a5ef-d2f1b795ffa0	file_type	File	2024-02-20 10:29:24.272+00
b3877eae-3b31-47b8-a717-fa04dc9f1139	646056e7-4e94-447d-a5ef-d2f1b795ffa0	file_size	1179295	2024-02-20 10:29:24.274+00
1ed2dd91-81b2-43e5-a27a-df9253109b8d	646056e7-4e94-447d-a5ef-d2f1b795ffa0	rights_copyright	Crown Copyright	2024-02-20 10:29:24.276+00
e865efdb-d2fd-436b-bc80-7900f74472e2	646056e7-4e94-447d-a5ef-d2f1b795ffa0	legal_status	Public Record(s)	2024-02-20 10:29:24.278+00
ad5690f6-cd0c-46af-8aa9-173b2aa2abad	646056e7-4e94-447d-a5ef-d2f1b795ffa0	held_by	The National Archives, Kew	2024-02-20 10:29:24.279+00
5784a948-70c0-44ab-8f72-711c8ba54d55	646056e7-4e94-447d-a5ef-d2f1b795ffa0	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.286+00
ad43b4de-e2e6-4a78-9773-3ef352e71687	646056e7-4e94-447d-a5ef-d2f1b795ffa0	closure_type	Open	2024-02-20 10:29:24.289+00
93c72312-8fe1-49c6-9d8d-e5bc6f037d34	646056e7-4e94-447d-a5ef-d2f1b795ffa0	title_closed	false	2024-02-20 10:29:24.291+00
cece944c-6d21-4cb2-9278-679ceae1fc17	646056e7-4e94-447d-a5ef-d2f1b795ffa0	description_closed	false	2024-02-20 10:29:24.292+00
824f5635-d16a-4a7c-aa2b-411be267e2c8	646056e7-4e94-447d-a5ef-d2f1b795ffa0	language	English	2024-02-20 10:29:24.294+00
6b42780b-92c6-49cc-9df9-efde6a733c1a	8b5e288b-d877-4ba6-adcc-a7d277acd254	file_name	Draft DDRO 05.docx	2024-02-20 10:29:24.301+00
3d800cc0-c8be-4d2a-9d09-383f3936af2a	8b5e288b-d877-4ba6-adcc-a7d277acd254	file_type	File	2024-02-20 10:29:24.303+00
889654dc-c1ed-4b72-9606-b7452f488078	8b5e288b-d877-4ba6-adcc-a7d277acd254	file_size	21707	2024-02-20 10:29:24.304+00
f6933dd0-8017-4fc4-b7a4-51db8f48839c	8b5e288b-d877-4ba6-adcc-a7d277acd254	rights_copyright	Crown Copyright	2024-02-20 10:29:24.305+00
7402033f-5ce1-4ad2-a5d2-35f3e5eaf435	8b5e288b-d877-4ba6-adcc-a7d277acd254	legal_status	Public Record(s)	2024-02-20 10:29:24.307+00
9955c7f9-29ac-413d-b3d7-acec15245d74	8b5e288b-d877-4ba6-adcc-a7d277acd254	held_by	The National Archives, Kew	2024-02-20 10:29:24.308+00
ec743c35-3872-4778-a22c-a3655aed96a3	8b5e288b-d877-4ba6-adcc-a7d277acd254	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.309+00
1b0a5a26-4a54-4b32-8c1d-bf36fb93dc1b	8b5e288b-d877-4ba6-adcc-a7d277acd254	closure_type	Open	2024-02-20 10:29:24.311+00
00262726-c3ef-42f8-96bb-7fc5ceeec977	8b5e288b-d877-4ba6-adcc-a7d277acd254	title_closed	false	2024-02-20 10:29:24.313+00
254ddc91-ed66-40e2-a626-af856a40d378	8b5e288b-d877-4ba6-adcc-a7d277acd254	description_closed	false	2024-02-20 10:29:24.314+00
5fcf5e84-7872-40f1-ba45-7f9a4af8493c	8b5e288b-d877-4ba6-adcc-a7d277acd254	language	English	2024-02-20 10:29:24.315+00
51ce8d6a-6761-45c4-8391-36efe5898eb0	025df6ca-cfa9-4ffc-ad59-8eed879258e1	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-20 10:29:24.322+00
4717cb24-814c-415c-8279-4caba672750b	025df6ca-cfa9-4ffc-ad59-8eed879258e1	file_type	File	2024-02-20 10:29:24.323+00
8190ed8d-b87b-49c3-b348-5ee6573916b2	025df6ca-cfa9-4ffc-ad59-8eed879258e1	file_size	70263	2024-02-20 10:29:24.325+00
fa8bf81e-ce51-44b3-b7a2-c81a64e72092	025df6ca-cfa9-4ffc-ad59-8eed879258e1	rights_copyright	Crown Copyright	2024-02-20 10:29:24.326+00
b34bed4f-29ce-4a9f-8dfc-f6179d98df8c	025df6ca-cfa9-4ffc-ad59-8eed879258e1	legal_status	Public Record(s)	2024-02-20 10:29:24.327+00
0be14022-cf99-40ac-9aea-ec8e95ca5618	025df6ca-cfa9-4ffc-ad59-8eed879258e1	held_by	The National Archives, Kew	2024-02-20 10:29:24.329+00
c1f43522-3bed-48db-885f-adfdf332047a	025df6ca-cfa9-4ffc-ad59-8eed879258e1	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.33+00
7e97956e-d32b-4217-9ac1-9b416ed7fb0e	025df6ca-cfa9-4ffc-ad59-8eed879258e1	closure_type	Open	2024-02-20 10:29:24.332+00
bcd8cec5-be02-437b-a655-e39f74a8e97d	025df6ca-cfa9-4ffc-ad59-8eed879258e1	title_closed	false	2024-02-20 10:29:24.333+00
1f1b5fb9-a5f7-48ce-8491-69115133642b	025df6ca-cfa9-4ffc-ad59-8eed879258e1	description_closed	false	2024-02-20 10:29:24.335+00
e142d8c3-6b5c-4c9b-a819-ea35f50b5c13	025df6ca-cfa9-4ffc-ad59-8eed879258e1	language	English	2024-02-20 10:29:24.336+00
c2ef5c0a-f5e6-4a15-b884-e0d5afe72281	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	file_name	Response Procedure.docx	2024-02-20 10:29:24.343+00
740af022-597d-45b3-930e-2d06f973e326	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	file_type	File	2024-02-20 10:29:24.345+00
fee4baaa-c78c-4f7f-a8c3-43f4098e7496	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	file_size	12610	2024-02-20 10:29:24.346+00
a28375af-aacc-4374-9e66-0e69145e0992	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	rights_copyright	Crown Copyright	2024-02-20 10:29:24.348+00
ac2bc54d-73c7-4f13-b1c9-c74b455373d6	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	legal_status	Public Record(s)	2024-02-20 10:29:24.35+00
1c80d50d-dc8c-40a4-9aaa-1787c650ee80	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	held_by	The National Archives, Kew	2024-02-20 10:29:24.351+00
2deac154-b7ed-4c94-a56a-1d5299df402a	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.352+00
90047582-f20b-405d-8f4d-7951ebfc563b	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	closure_type	Open	2024-02-20 10:29:24.354+00
9cd1abb5-6b82-4fea-962b-e71933cfb9ab	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	title_closed	false	2024-02-20 10:29:24.355+00
00db712b-10e0-442a-b024-dc15fc899451	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	description_closed	false	2024-02-20 10:29:24.357+00
e99b8bd3-a23c-417a-8f44-f8cc6ab21130	cfccf0b6-36dc-4cee-b63f-d6f9ddb8055b	language	English	2024-02-20 10:29:24.358+00
1fa781c5-663a-4858-99d6-bc4251b3c571	250b162f-df9a-4d27-b237-c9c1a844a7d1	file_name	Gateways.ppt	2024-02-20 10:29:24.365+00
2ae82bac-f5d1-4906-aff0-edf732e2ca78	250b162f-df9a-4d27-b237-c9c1a844a7d1	file_type	File	2024-02-20 10:29:24.366+00
25350294-6bf8-4bef-8e45-807e545a9281	250b162f-df9a-4d27-b237-c9c1a844a7d1	file_size	446464	2024-02-20 10:29:24.368+00
b3ed8213-3686-4c4d-85bd-918025a4871a	250b162f-df9a-4d27-b237-c9c1a844a7d1	rights_copyright	Crown Copyright	2024-02-20 10:29:24.369+00
56340686-91d2-4d47-aeaa-999c8bf2e073	250b162f-df9a-4d27-b237-c9c1a844a7d1	legal_status	Public Record(s)	2024-02-20 10:29:24.37+00
202b1ac6-40af-4add-8526-bca7d14233bf	250b162f-df9a-4d27-b237-c9c1a844a7d1	held_by	The National Archives, Kew	2024-02-20 10:29:24.372+00
8dd8d7de-ae35-4a24-930c-e85f786a3eff	250b162f-df9a-4d27-b237-c9c1a844a7d1	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.373+00
dd030689-51b2-4703-b6d5-8400317e4517	250b162f-df9a-4d27-b237-c9c1a844a7d1	closure_type	Open	2024-02-20 10:29:24.374+00
f6b591c5-3c53-4d6b-8cde-4431570fea50	250b162f-df9a-4d27-b237-c9c1a844a7d1	title_closed	false	2024-02-20 10:29:24.375+00
24dbfb18-707b-466a-a106-9c15aec2ef9b	250b162f-df9a-4d27-b237-c9c1a844a7d1	description_closed	false	2024-02-20 10:29:24.377+00
fdc6db17-4ae5-48dc-91a0-b6b8dbb44ade	250b162f-df9a-4d27-b237-c9c1a844a7d1	language	English	2024-02-20 10:29:24.378+00
ead9f658-2a89-42fd-9412-c06edc0956ee	318abd3b-d2b7-4f45-9785-5094c007dfea	file_name	delivery-form-digital.doc	2024-02-20 10:29:24.384+00
9218008a-b09a-4c4e-996a-38b8f2195010	318abd3b-d2b7-4f45-9785-5094c007dfea	file_type	File	2024-02-20 10:29:24.389+00
5c8cfc5e-8cd3-487b-9ce9-8e9ee800f3e0	318abd3b-d2b7-4f45-9785-5094c007dfea	file_size	139776	2024-02-20 10:29:24.391+00
259f4d05-dfff-41df-9a81-15249941cf0d	318abd3b-d2b7-4f45-9785-5094c007dfea	rights_copyright	Crown Copyright	2024-02-20 10:29:24.392+00
3786549b-4760-49f9-aeae-60acc0f5f9b9	318abd3b-d2b7-4f45-9785-5094c007dfea	legal_status	Public Record(s)	2024-02-20 10:29:24.393+00
d9688dc9-0723-4201-b5d4-fdeadf75c55f	318abd3b-d2b7-4f45-9785-5094c007dfea	held_by	The National Archives, Kew	2024-02-20 10:29:24.394+00
c9d52853-d0a3-446f-bc9b-eb688203b1c5	318abd3b-d2b7-4f45-9785-5094c007dfea	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.395+00
09d3f704-1696-4b96-a119-f2c9ed80ccb9	318abd3b-d2b7-4f45-9785-5094c007dfea	closure_type	Open	2024-02-20 10:29:24.397+00
c6e2e925-ba5a-4389-8db0-01f476e0bf61	318abd3b-d2b7-4f45-9785-5094c007dfea	title_closed	false	2024-02-20 10:29:24.398+00
219a4a74-6723-4d06-b108-684ca3469e46	318abd3b-d2b7-4f45-9785-5094c007dfea	description_closed	false	2024-02-20 10:29:24.399+00
0823b18b-2dad-4755-a044-7bec10b0fa6c	318abd3b-d2b7-4f45-9785-5094c007dfea	language	English	2024-02-20 10:29:24.4+00
5cb9a04a-229f-45c6-a043-998b2f565bcb	48e6132b-1a08-40a3-a704-156d88737f83	file_name	base_de_donnees.png	2024-02-20 10:29:24.406+00
f60adc13-b7e6-41a2-b908-42724e17bb9f	48e6132b-1a08-40a3-a704-156d88737f83	file_type	File	2024-02-20 10:29:24.407+00
713f66c8-4c61-4e21-bae0-cba3bccb6fb6	48e6132b-1a08-40a3-a704-156d88737f83	file_size	165098	2024-02-20 10:29:24.409+00
386e67e8-01cd-4dc3-9757-3d2f566409f5	48e6132b-1a08-40a3-a704-156d88737f83	rights_copyright	Crown Copyright	2024-02-20 10:29:24.41+00
dbb7f4fb-4f9b-4191-907d-ac595cffbb82	48e6132b-1a08-40a3-a704-156d88737f83	legal_status	Public Record(s)	2024-02-20 10:29:24.411+00
af7effa6-2743-4612-ac52-f413a31cd7b1	48e6132b-1a08-40a3-a704-156d88737f83	held_by	The National Archives, Kew	2024-02-20 10:29:24.413+00
34006fd4-81bc-47c0-989c-88acfac7dd07	48e6132b-1a08-40a3-a704-156d88737f83	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.414+00
9581e56b-3681-448b-8226-178377cc5d76	48e6132b-1a08-40a3-a704-156d88737f83	closure_type	Open	2024-02-20 10:29:24.416+00
0747c93e-38aa-40b0-9d16-3480dbc76832	48e6132b-1a08-40a3-a704-156d88737f83	title_closed	false	2024-02-20 10:29:24.417+00
80a002c6-2511-49bc-af93-0898633db043	48e6132b-1a08-40a3-a704-156d88737f83	description_closed	false	2024-02-20 10:29:24.419+00
6ffffcbb-f43e-4ae2-a2d7-fed77bebd5e6	48e6132b-1a08-40a3-a704-156d88737f83	language	English	2024-02-20 10:29:24.42+00
cf437b62-bf39-4772-8db6-126b6bf9bd44	cf4c871f-786b-4691-b77f-755bba24462c	file_name	Response Policy.docx	2024-02-20 10:29:24.43+00
da42432f-5bcc-42ca-9116-69d305ccac99	cf4c871f-786b-4691-b77f-755bba24462c	file_type	File	2024-02-20 10:29:24.432+00
bbfdde40-ba4b-4f0a-890f-66b44e6a4d2a	cf4c871f-786b-4691-b77f-755bba24462c	file_size	12651	2024-02-20 10:29:24.433+00
0a52f85e-5f32-4283-9732-c572e24440f6	cf4c871f-786b-4691-b77f-755bba24462c	rights_copyright	Crown Copyright	2024-02-20 10:29:24.434+00
1899a2b6-b795-4e25-b1d0-be46df1e9456	cf4c871f-786b-4691-b77f-755bba24462c	legal_status	Public Record(s)	2024-02-20 10:29:24.437+00
f11dc611-af4f-4972-aa12-71816ef4c759	cf4c871f-786b-4691-b77f-755bba24462c	held_by	The National Archives, Kew	2024-02-20 10:29:24.438+00
097d1fd8-ba52-4bcf-b44e-4eb66304e33b	cf4c871f-786b-4691-b77f-755bba24462c	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.439+00
a20f70ba-f36c-4d92-9537-2a4302b268d4	cf4c871f-786b-4691-b77f-755bba24462c	closure_type	Open	2024-02-20 10:29:24.441+00
e700d20e-3415-4d8e-aa3f-f35e686e8e70	cf4c871f-786b-4691-b77f-755bba24462c	title_closed	false	2024-02-20 10:29:24.442+00
eaa53c03-0d93-443b-a2aa-14634defb087	cf4c871f-786b-4691-b77f-755bba24462c	description_closed	false	2024-02-20 10:29:24.444+00
accc2cea-dfa9-472f-9b87-e13dd8b5920f	cf4c871f-786b-4691-b77f-755bba24462c	language	English	2024-02-20 10:29:24.446+00
60d60303-23fc-4da9-8391-65d6510e7d07	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	file_name	DTP_ Sensitivity review process.docx	2024-02-20 10:29:24.451+00
8ca6d475-1538-45d5-a6ac-7b0f79688f17	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	file_type	File	2024-02-20 10:29:24.452+00
e5bb2ab2-ce31-4028-af65-5effa6fb919a	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	file_size	70674	2024-02-20 10:29:24.454+00
ee7e6426-f7dd-4a31-a8eb-4133fa82765b	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	rights_copyright	Crown Copyright	2024-02-20 10:29:24.455+00
51ea939d-f375-4acf-9037-984c6e987237	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	legal_status	Public Record(s)	2024-02-20 10:29:24.456+00
4dea2980-8628-4f20-b4ec-1c167d88b8f4	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	held_by	The National Archives, Kew	2024-02-20 10:29:24.457+00
413765e6-1bc3-4e14-9ab9-555274985568	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.458+00
ed1c6cac-df15-443e-b921-48f86d7b471f	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	closure_type	Open	2024-02-20 10:29:24.461+00
171f03aa-fa2f-400e-888e-93ab3749c4f3	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	title_closed	false	2024-02-20 10:29:24.462+00
e060e8ef-53b1-4e39-b107-d75b79ee882c	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	description_closed	false	2024-02-20 10:29:24.463+00
4670dee0-a12e-406e-8ad3-84ab8d391028	7ca40ff9-0381-4e95-a0fa-6c7ed5d286a5	language	English	2024-02-20 10:29:24.466+00
fbc95480-888b-4355-b91e-b39e474102c9	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	file_name	DTP.docx	2024-02-20 10:29:24.473+00
c206de9b-8bb3-4f9c-bb49-dacc13946b42	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	file_type	File	2024-02-20 10:29:24.476+00
20ec9a55-bff3-498b-a52b-2b0dcc0d5c2d	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	file_size	70263	2024-02-20 10:29:24.477+00
000828ee-8aa0-4e85-a105-5e035cf1cc22	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	rights_copyright	Crown Copyright	2024-02-20 10:29:24.479+00
9327fb76-78e1-45c2-acf2-c8d1a0a3403d	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	legal_status	Public Record(s)	2024-02-20 10:29:24.481+00
69395945-6226-4aa7-9391-881139640236	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	held_by	The National Archives, Kew	2024-02-20 10:29:24.483+00
a4261d10-238e-48ab-b928-183c10ffedac	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.484+00
32849634-f264-4d97-918d-4775dc10f98d	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	closure_type	Open	2024-02-20 10:29:24.485+00
72b7b4eb-f702-41c4-ac85-d5ac2aec258d	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	title_closed	false	2024-02-20 10:29:24.486+00
b3d1d6e0-d7ac-470b-8bde-36c5f51ae591	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	description_closed	false	2024-02-20 10:29:24.488+00
7f860809-9c13-4b36-8a54-c990ec2a9336	3b5431f7-9166-4c9b-bc20-72a2a4dd780a	language	English	2024-02-20 10:29:24.489+00
75e0f563-56f6-47a5-80f5-85ad1dbb9e42	b6ce8b02-c70d-4771-a4de-d4da189822da	file_name	Thumbs.db	2024-02-20 10:29:24.496+00
1f29bc42-4e21-4d0e-bef5-434fac0cd917	b6ce8b02-c70d-4771-a4de-d4da189822da	file_type	File	2024-02-20 10:29:24.497+00
c7276128-284b-4d80-9169-73663da6d0d1	b6ce8b02-c70d-4771-a4de-d4da189822da	file_size	685124	2024-02-20 10:29:24.498+00
a7194e11-22cf-4970-972b-b87b2f99b58e	b6ce8b02-c70d-4771-a4de-d4da189822da	rights_copyright	Crown Copyright	2024-02-20 10:29:24.499+00
a40ea8f4-c93c-47dd-823e-25b33c0b49e8	b6ce8b02-c70d-4771-a4de-d4da189822da	legal_status	Public Record(s)	2024-02-20 10:29:24.501+00
22b59a08-e78d-4e78-8b86-c1e5228f3bea	b6ce8b02-c70d-4771-a4de-d4da189822da	held_by	The National Archives, Kew	2024-02-20 10:29:24.502+00
9282ee67-a2b1-4dd3-a86b-8f105af83032	b6ce8b02-c70d-4771-a4de-d4da189822da	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.503+00
45a54282-9ee4-4e54-8fa7-284b83488031	b6ce8b02-c70d-4771-a4de-d4da189822da	closure_type	Open	2024-02-20 10:29:24.504+00
9f277c4f-285b-4fa1-8aa1-46283422b12b	b6ce8b02-c70d-4771-a4de-d4da189822da	title_closed	false	2024-02-20 10:29:24.511+00
596fcccb-01f4-4e90-bacf-eef04754a007	b6ce8b02-c70d-4771-a4de-d4da189822da	description_closed	false	2024-02-20 10:29:24.512+00
e036e898-ee81-4fb2-ba6b-f15d15212a75	b6ce8b02-c70d-4771-a4de-d4da189822da	language	English	2024-02-20 10:29:24.522+00
bd5b7333-9393-4c35-a743-7328e374170f	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	file_name	Emergency Response Team	2024-02-20 10:29:24.534+00
e0f5c6a7-85ee-46d3-85e4-ac85a05ecfad	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	file_type	Folder	2024-02-20 10:29:24.535+00
d3f507e6-60db-4d98-9516-2bc92d02ce5a	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	rights_copyright	Crown Copyright	2024-02-20 10:29:24.537+00
a2a09bed-eeff-4d96-93f4-f148497cded3	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	legal_status	Public Record(s)	2024-02-20 10:29:24.538+00
20355644-d3b3-49bb-b6ee-95676d8c36e3	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	held_by	The National Archives, Kew	2024-02-20 10:29:24.539+00
f6c74d0f-5945-4818-be4b-8503b74ffd3f	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	closure_type	Open	2024-02-20 10:29:24.541+00
ba84c259-6ce8-48a2-96a8-9a0d8f48a168	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	title_closed	false	2024-02-20 10:29:24.542+00
d9941719-709b-4484-9772-b17ef71e4874	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	description_closed	false	2024-02-20 10:29:24.543+00
1ef7a8ae-c655-4454-ac4c-623af0029b06	c4e40b55-ac62-43d8-a26c-dd50b0b339f9	language	English	2024-02-20 10:29:24.545+00
25e87f65-f812-49f8-96a8-33b3a9e91b58	80ec3f41-ca06-4589-9826-b2ba2ca17970	file_name	Workflows	2024-02-20 10:29:24.551+00
375dfc6e-7b92-4b65-8821-7eb1d5e34464	80ec3f41-ca06-4589-9826-b2ba2ca17970	file_type	Folder	2024-02-20 10:29:24.556+00
22abc6b8-58fb-4672-ba70-a8168fadfb76	80ec3f41-ca06-4589-9826-b2ba2ca17970	rights_copyright	Crown Copyright	2024-02-20 10:29:24.559+00
f8b1edb9-a7be-46fc-ae2e-f79a5b9c9fc7	80ec3f41-ca06-4589-9826-b2ba2ca17970	legal_status	Public Record(s)	2024-02-20 10:29:24.56+00
0b954514-ed99-4d7c-a78b-086f60a8b1ba	80ec3f41-ca06-4589-9826-b2ba2ca17970	held_by	The National Archives, Kew	2024-02-20 10:29:24.562+00
747b450e-09ee-446e-b59b-a697b0adc97f	80ec3f41-ca06-4589-9826-b2ba2ca17970	closure_type	Open	2024-02-20 10:29:24.563+00
315b88b0-0878-47c8-bc58-7bfcddfc342d	80ec3f41-ca06-4589-9826-b2ba2ca17970	title_closed	false	2024-02-20 10:29:24.566+00
0cd72290-6f6f-4cdd-9e27-e4947ba6d366	80ec3f41-ca06-4589-9826-b2ba2ca17970	description_closed	false	2024-02-20 10:29:24.567+00
55f6347f-0a15-4bb1-a25a-cf4737b6243b	80ec3f41-ca06-4589-9826-b2ba2ca17970	language	English	2024-02-20 10:29:24.568+00
3b5b4ac7-ebb4-4e7d-8e15-44b75a534a1e	6302998c-97cb-4549-9f60-6eb861314c35	file_name	Presentation.pptx	2024-02-20 10:29:24.571+00
e13e0576-09b2-4105-b864-46c47a0e72f7	6302998c-97cb-4549-9f60-6eb861314c35	file_type	File	2024-02-20 10:29:24.572+00
7da2222c-a5c9-4b50-b153-6435e5b3cd23	6302998c-97cb-4549-9f60-6eb861314c35	file_size	697817	2024-02-20 10:29:24.574+00
db2fad4e-9e12-46fb-8a03-9658512fefbf	6302998c-97cb-4549-9f60-6eb861314c35	rights_copyright	Crown Copyright	2024-02-20 10:29:24.575+00
4668395c-f2e8-4385-aad4-44a91289dceb	6302998c-97cb-4549-9f60-6eb861314c35	legal_status	Public Record(s)	2024-02-20 10:29:24.577+00
5e310291-7b7b-45f3-99d6-0919cd081898	6302998c-97cb-4549-9f60-6eb861314c35	held_by	The National Archives, Kew	2024-02-20 10:29:24.578+00
0414ce7f-0e37-4f41-b718-0f7f9b4dde53	6302998c-97cb-4549-9f60-6eb861314c35	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.579+00
beaf85ca-75cb-4bcf-8599-62aec44ccde0	6302998c-97cb-4549-9f60-6eb861314c35	closure_type	Open	2024-02-20 10:29:24.581+00
53079844-274f-437a-94c6-7e8d07e21479	6302998c-97cb-4549-9f60-6eb861314c35	title_closed	false	2024-02-20 10:29:24.582+00
87686f5b-a435-4f0b-b4a0-149ea0bc9f28	6302998c-97cb-4549-9f60-6eb861314c35	description_closed	false	2024-02-20 10:29:24.583+00
e0c0d1aa-4705-4e24-9fb5-20ae2f5b698f	6302998c-97cb-4549-9f60-6eb861314c35	language	English	2024-02-20 10:29:24.585+00
bc0e8bce-12c1-40c7-93c8-dbf291b250a1	a3e0759f-2d8c-427c-9bb0-6130335e85a5	file_name	Remove.docx	2024-02-20 10:29:24.59+00
c1b0eb28-6f13-41f7-90cb-897ec5fc1e36	a3e0759f-2d8c-427c-9bb0-6130335e85a5	file_type	File	2024-02-20 10:29:24.593+00
3b51e803-26b6-4293-a291-2b464d63a0b3	a3e0759f-2d8c-427c-9bb0-6130335e85a5	file_size	12609	2024-02-20 10:29:24.595+00
b0feabfb-1d05-4e87-b694-21b080a0222d	a3e0759f-2d8c-427c-9bb0-6130335e85a5	rights_copyright	Crown Copyright	2024-02-20 10:29:24.596+00
034de7ec-25a3-4bc3-86dd-7549766c5bef	a3e0759f-2d8c-427c-9bb0-6130335e85a5	legal_status	Public Record(s)	2024-02-20 10:29:24.598+00
9cc675b9-e195-450f-9bcb-c2989fc74da1	a3e0759f-2d8c-427c-9bb0-6130335e85a5	held_by	The National Archives, Kew	2024-02-20 10:29:24.601+00
e9859e16-6720-49f2-a3b8-7522fa8c5670	a3e0759f-2d8c-427c-9bb0-6130335e85a5	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.605+00
aa0de124-cd16-4a0d-8b89-b9cba6e6c3e6	a3e0759f-2d8c-427c-9bb0-6130335e85a5	closure_type	Open	2024-02-20 10:29:24.607+00
d429874d-f317-4853-a793-f6477d1797a3	a3e0759f-2d8c-427c-9bb0-6130335e85a5	title_closed	false	2024-02-20 10:29:24.615+00
0ffad655-05b0-40df-8dda-c6ec20eda77d	a3e0759f-2d8c-427c-9bb0-6130335e85a5	description_closed	false	2024-02-20 10:29:24.616+00
2c7c71b5-a729-43b4-afe5-a4ba47d36876	a3e0759f-2d8c-427c-9bb0-6130335e85a5	language	English	2024-02-20 10:29:24.618+00
e2705d0b-f31e-4d06-aaf8-737e757e0509	906097d6-c80c-4e46-aab8-f0743807f984	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-20 10:29:24.624+00
ca49b40b-ffa4-4c46-acf7-5efc0ecacd98	906097d6-c80c-4e46-aab8-f0743807f984	file_type	File	2024-02-20 10:29:24.626+00
a7b0c3dc-265b-4dc2-bdf7-5301af431371	906097d6-c80c-4e46-aab8-f0743807f984	file_size	68364	2024-02-20 10:29:24.627+00
ed9402d0-122a-4422-aa60-39e05261df4d	906097d6-c80c-4e46-aab8-f0743807f984	rights_copyright	Crown Copyright	2024-02-20 10:29:24.629+00
cb0af003-5f80-42b1-bf48-e9c07d907c58	906097d6-c80c-4e46-aab8-f0743807f984	legal_status	Public Record(s)	2024-02-20 10:29:24.631+00
bedad87d-0560-4989-a792-596e8bef5e28	906097d6-c80c-4e46-aab8-f0743807f984	held_by	The National Archives, Kew	2024-02-20 10:29:24.632+00
3e105eeb-d402-4342-9d3c-de2881357e1c	906097d6-c80c-4e46-aab8-f0743807f984	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.633+00
2f93071c-0f7a-48fe-8cbb-1f446fd8a960	906097d6-c80c-4e46-aab8-f0743807f984	closure_type	Open	2024-02-20 10:29:24.635+00
d2f734fa-fc88-452d-a85c-0d6cd22e51d3	906097d6-c80c-4e46-aab8-f0743807f984	title_closed	false	2024-02-20 10:29:24.636+00
d29d2457-8d08-41fd-ac38-1f8c32903dcd	906097d6-c80c-4e46-aab8-f0743807f984	description_closed	false	2024-02-20 10:29:24.637+00
e50f1dce-a989-4843-90a3-f970c1d114c1	906097d6-c80c-4e46-aab8-f0743807f984	language	English	2024-02-20 10:29:24.639+00
ee2aa7be-0ee3-4889-ae71-907373d1655d	a65558bb-cedc-4a7a-a518-aa63b0492b91	file_name	Digital Transfer training email .msg	2024-02-20 10:29:24.646+00
d629bd43-a7c3-482e-a11f-656245d46c1a	a65558bb-cedc-4a7a-a518-aa63b0492b91	file_type	File	2024-02-20 10:29:24.647+00
a615f24c-20c0-4806-8180-7abaf38c8791	a65558bb-cedc-4a7a-a518-aa63b0492b91	file_size	39424	2024-02-20 10:29:24.648+00
95633200-e22d-4d92-aba8-b02df7fdc8ef	a65558bb-cedc-4a7a-a518-aa63b0492b91	rights_copyright	Crown Copyright	2024-02-20 10:29:24.65+00
1b7f156f-f5c3-4085-9cb9-e39d40e96bee	a65558bb-cedc-4a7a-a518-aa63b0492b91	legal_status	Public Record(s)	2024-02-20 10:29:24.651+00
762e3be2-f698-4ebc-91cd-b09ab8e2c46d	a65558bb-cedc-4a7a-a518-aa63b0492b91	held_by	The National Archives, Kew	2024-02-20 10:29:24.653+00
c11714e5-555f-46e8-8cf1-a83e7667ddad	a65558bb-cedc-4a7a-a518-aa63b0492b91	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.654+00
f567fb51-f0e3-4224-86eb-d50b201e4492	a65558bb-cedc-4a7a-a518-aa63b0492b91	closure_type	Open	2024-02-20 10:29:24.655+00
dd9b77c6-4aa9-43d8-90d6-575a76d75776	a65558bb-cedc-4a7a-a518-aa63b0492b91	title_closed	false	2024-02-20 10:29:24.656+00
a4d49274-9b2a-491d-a222-2c51b6f1806a	a65558bb-cedc-4a7a-a518-aa63b0492b91	description_closed	false	2024-02-20 10:29:24.657+00
c9636cf7-1e2b-417f-a222-f5890b233c1e	a65558bb-cedc-4a7a-a518-aa63b0492b91	language	English	2024-02-20 10:29:24.658+00
e9e20220-bd5f-476e-a8dd-26b8c5641a5c	34e782c4-34dd-44de-96b5-f6d004f26239	file_name	Emergency Contact Details Paul Young.docx	2024-02-20 10:29:24.672+00
836c4a90-d14d-4110-a452-ee9d2b3fcc4c	34e782c4-34dd-44de-96b5-f6d004f26239	file_type	File	2024-02-20 10:29:24.673+00
baaa6211-99c4-4dae-8622-e29a190053a2	34e782c4-34dd-44de-96b5-f6d004f26239	file_size	12825	2024-02-20 10:29:24.674+00
47427a2a-ae41-4c2c-a888-94517e547e1e	34e782c4-34dd-44de-96b5-f6d004f26239	rights_copyright	Crown Copyright	2024-02-20 10:29:24.676+00
381f60ad-4100-4202-97cc-8445e3a2bdea	34e782c4-34dd-44de-96b5-f6d004f26239	legal_status	Public Record(s)	2024-02-20 10:29:24.677+00
66afea96-7afe-4aa6-9078-275a5aa5911a	34e782c4-34dd-44de-96b5-f6d004f26239	held_by	The National Archives, Kew	2024-02-20 10:29:24.68+00
2d5411d6-a3a8-4abb-acc4-f9cbe2c0558a	34e782c4-34dd-44de-96b5-f6d004f26239	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.681+00
9c465e22-88c8-49eb-8c90-7394dbbc3f95	34e782c4-34dd-44de-96b5-f6d004f26239	closure_type	Open	2024-02-20 10:29:24.683+00
4240564b-39d3-4fa6-9973-269b1b1eb431	34e782c4-34dd-44de-96b5-f6d004f26239	title_closed	false	2024-02-20 10:29:24.684+00
14a0f72c-bc2b-4b38-a9d2-84e1d67a31b3	34e782c4-34dd-44de-96b5-f6d004f26239	description_closed	false	2024-02-20 10:29:24.686+00
a98ac2c9-d31a-4a37-a2af-d1921884c295	34e782c4-34dd-44de-96b5-f6d004f26239	language	English	2024-02-20 10:29:24.688+00
33c941e2-21e8-4d94-8572-8bf0e3f582fc	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-20 10:29:24.693+00
bdcd4c86-082f-4ce9-baae-66536af8cdd1	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	file_type	File	2024-02-20 10:29:24.694+00
9ceafebd-d786-4263-94b8-424cae6a8797	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	file_size	177875	2024-02-20 10:29:24.696+00
2345823c-26df-41f4-87cd-b7fa85b56705	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	rights_copyright	Crown Copyright	2024-02-20 10:29:24.697+00
8d33a18a-d948-4b00-88a7-965566d27762	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	legal_status	Public Record(s)	2024-02-20 10:29:24.698+00
01caf091-7a05-4d6e-8a05-ca6c4722e6e1	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	held_by	The National Archives, Kew	2024-02-20 10:29:24.699+00
486c175f-a524-4ef0-96b7-6949fd570c99	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	date_last_modified	2022-07-18T00:00:00	2024-02-20 10:29:24.7+00
56d419f6-bfd3-4052-8087-900193ecf431	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	closure_type	Open	2024-02-20 10:29:24.701+00
cdf8ca2e-7021-4c64-a40e-e79140c768a2	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	title_closed	false	2024-02-20 10:29:24.702+00
928ebffd-976d-460f-86cb-27e48e3a66df	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	description_closed	false	2024-02-20 10:29:24.703+00
89daf4fb-9470-4983-b045-dbb077c77a3b	7b3c115e-f5d8-4cd8-96b6-a1058c6bfa2b	language	English	2024-02-20 10:29:24.704+00
e7c131b3-1272-4343-8c27-cacc5f619462	1272e8c2-0331-4b11-9379-00ae81e42083	file_name	base_de_donnees.png	2024-02-20 10:31:13.809+00
927c85ce-be72-4591-af11-387aef01895b	1272e8c2-0331-4b11-9379-00ae81e42083	file_type	File	2024-02-20 10:31:13.813+00
c6196797-8f3c-4b7b-8842-f5c618f977b4	1272e8c2-0331-4b11-9379-00ae81e42083	file_size	165098	2024-02-20 10:31:13.816+00
58c47e0b-e2c6-4898-9410-4cee27507863	1272e8c2-0331-4b11-9379-00ae81e42083	rights_copyright	Crown Copyright	2024-02-20 10:31:13.819+00
d8bca26b-7612-449c-9336-0c56d1cf9240	1272e8c2-0331-4b11-9379-00ae81e42083	legal_status	Public Record(s)	2024-02-20 10:31:13.822+00
ca7dafe0-a8d9-4003-afb8-2fb27185572e	1272e8c2-0331-4b11-9379-00ae81e42083	held_by	The National Archives, Kew	2024-02-20 10:31:13.825+00
1de4bc21-1d72-4350-951c-faeed17d62a2	1272e8c2-0331-4b11-9379-00ae81e42083	date_last_modified	2022-08-03T13:47:04	2024-02-20 10:31:13.828+00
c2a00d2f-fd2b-4bc4-a5d9-567c6376849e	1272e8c2-0331-4b11-9379-00ae81e42083	closure_type	Open	2024-02-20 10:31:13.831+00
19fade82-d26f-4a10-b909-b70c07401da2	1272e8c2-0331-4b11-9379-00ae81e42083	title_closed	false	2024-02-20 10:31:13.834+00
0a30ca9d-e9fe-4d31-99c0-d2fe50a1b0b4	1272e8c2-0331-4b11-9379-00ae81e42083	description_closed	false	2024-02-20 10:31:13.836+00
5e6cc27c-17af-4d21-8203-e44d5934d6b6	1272e8c2-0331-4b11-9379-00ae81e42083	language	English	2024-02-20 10:31:13.839+00
e0dbc3e5-6cdf-450e-8b36-242f26ea908d	643d14b9-e846-4f06-9efb-e80b0c7894e8	file_name	Remove.docx	2024-02-20 10:31:13.851+00
e10e5350-a9a2-448b-bef4-a14185a83fa6	643d14b9-e846-4f06-9efb-e80b0c7894e8	file_type	File	2024-02-20 10:31:13.854+00
4af23566-957a-4207-bf4d-e8323301ada0	643d14b9-e846-4f06-9efb-e80b0c7894e8	file_size	12609	2024-02-20 10:31:13.857+00
59ed7207-8419-4dda-99f2-996cbf28ed06	643d14b9-e846-4f06-9efb-e80b0c7894e8	rights_copyright	Crown Copyright	2024-02-20 10:31:13.859+00
59e5d599-e679-4b7e-98de-677318f93bbf	643d14b9-e846-4f06-9efb-e80b0c7894e8	legal_status	Public Record(s)	2024-02-20 10:31:13.862+00
51d8c139-f59d-44b6-b58a-a506e1fc2709	643d14b9-e846-4f06-9efb-e80b0c7894e8	held_by	The National Archives, Kew	2024-02-20 10:31:13.864+00
826b5cd5-7894-422c-80d1-65183044294b	643d14b9-e846-4f06-9efb-e80b0c7894e8	date_last_modified	2022-08-03T13:47:41	2024-02-20 10:31:13.867+00
68f2f844-26a9-4a11-b55d-21b0b9f7310c	643d14b9-e846-4f06-9efb-e80b0c7894e8	closure_type	Open	2024-02-20 10:31:13.869+00
a88a7ca0-58de-4f52-8a2b-ef7eac478a20	643d14b9-e846-4f06-9efb-e80b0c7894e8	title_closed	false	2024-02-20 10:31:13.872+00
127e04a6-b86f-4a6a-b5f6-dceef920ef21	643d14b9-e846-4f06-9efb-e80b0c7894e8	description_closed	false	2024-02-20 10:31:13.876+00
f5c47c3a-79c3-46f2-a767-18abf24cfb0d	643d14b9-e846-4f06-9efb-e80b0c7894e8	language	English	2024-02-20 10:31:13.879+00
31ac240c-41c6-4bb8-9060-7d407440f88a	2ba441f8-413e-4a96-8919-a0e7ef8e8029	file_name	Gateways.ppt	2024-02-20 10:31:13.89+00
45894a87-9450-4d0c-af67-a480264188ab	2ba441f8-413e-4a96-8919-a0e7ef8e8029	file_type	File	2024-02-20 10:31:13.892+00
5eb349d0-43e9-4314-9d13-8d26010a65ca	2ba441f8-413e-4a96-8919-a0e7ef8e8029	file_size	446464	2024-02-20 10:31:13.894+00
5ef20a59-3378-40a3-93f7-86e2eb740c5d	2ba441f8-413e-4a96-8919-a0e7ef8e8029	rights_copyright	Crown Copyright	2024-02-20 10:31:13.897+00
d0fd83ec-afc7-43a2-bf01-2b0cc7e93d2a	2ba441f8-413e-4a96-8919-a0e7ef8e8029	legal_status	Public Record(s)	2024-02-20 10:31:13.899+00
8d5a3e93-30a6-43c6-a7ce-0273cd4a4546	2ba441f8-413e-4a96-8919-a0e7ef8e8029	held_by	The National Archives, Kew	2024-02-20 10:31:13.902+00
0a72d11a-3dc4-43e0-ae7e-668a3b21f3cf	2ba441f8-413e-4a96-8919-a0e7ef8e8029	date_last_modified	2022-08-03T13:47:15	2024-02-20 10:31:13.904+00
276fa1d1-6789-403b-9b75-773348b60021	2ba441f8-413e-4a96-8919-a0e7ef8e8029	closure_type	Open	2024-02-20 10:31:13.907+00
ec2e9bd8-a939-468c-b8ab-55d0f4654d5a	2ba441f8-413e-4a96-8919-a0e7ef8e8029	title_closed	false	2024-02-20 10:31:13.909+00
c3c48544-778f-4f08-9ee5-9ae7de17fdd7	2ba441f8-413e-4a96-8919-a0e7ef8e8029	description_closed	false	2024-02-20 10:31:13.912+00
3bfd7c05-3c65-48b6-8cbd-e85eabe572fc	2ba441f8-413e-4a96-8919-a0e7ef8e8029	language	English	2024-02-20 10:31:13.916+00
db2524f5-30c2-43a5-a487-3e8df5c7d2bd	9e2404a9-ba2a-44d7-8fe8-648d053af548	file_name	Response Policy.docx	2024-02-20 10:31:13.929+00
f3f896af-106d-4331-8279-e3433d58c943	9e2404a9-ba2a-44d7-8fe8-648d053af548	file_type	File	2024-02-20 10:31:13.931+00
9b41d52c-735a-4a3f-a514-489aa90294b2	9e2404a9-ba2a-44d7-8fe8-648d053af548	file_size	12651	2024-02-20 10:31:13.934+00
751e2431-1a73-4479-91fa-e1830b267da9	9e2404a9-ba2a-44d7-8fe8-648d053af548	rights_copyright	Crown Copyright	2024-02-20 10:31:13.937+00
88d73cdd-aa24-4efe-b914-fea32a96edd5	9e2404a9-ba2a-44d7-8fe8-648d053af548	legal_status	Public Record(s)	2024-02-20 10:31:13.939+00
eb1d33fd-9848-4e8e-a51d-a6d2055cd9fc	2a426981-df85-4c94-9885-8b7760c86115	description_closed	false	2024-02-20 10:31:14.242+00
543e1aee-2f6d-41b6-a43a-dbf5947dee01	9e2404a9-ba2a-44d7-8fe8-648d053af548	held_by	The National Archives, Kew	2024-02-20 10:31:13.942+00
bbdc9983-efb7-4090-8c15-7c61e0db5dd5	9e2404a9-ba2a-44d7-8fe8-648d053af548	date_last_modified	2022-08-03T13:47:31	2024-02-20 10:31:13.945+00
c91b8fd4-0834-4290-9196-72c33b2803a7	9e2404a9-ba2a-44d7-8fe8-648d053af548	closure_type	Open	2024-02-20 10:31:13.948+00
0e70b3a7-ebb3-4f6f-8c1a-0cb9de0adce5	9e2404a9-ba2a-44d7-8fe8-648d053af548	title_closed	false	2024-02-20 10:31:13.95+00
edc6101c-b20b-4061-a7d4-83680f61bf7e	9e2404a9-ba2a-44d7-8fe8-648d053af548	description_closed	false	2024-02-20 10:31:13.952+00
70031ffc-4590-40d0-8b1a-0c19804139b8	9e2404a9-ba2a-44d7-8fe8-648d053af548	language	English	2024-02-20 10:31:13.955+00
50921091-1652-44fb-b319-e196d81767cc	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	file_name	Emergency Response Team	2024-02-20 10:31:13.966+00
2c2205a4-c6e6-44a4-a456-21e2ed77094c	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	file_type	Folder	2024-02-20 10:31:13.968+00
0127317e-ae81-4b59-895c-11af649a7f47	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	rights_copyright	Crown Copyright	2024-02-20 10:31:13.971+00
104a323f-d483-48ca-a63a-6aa94595e7bf	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	legal_status	Public Record(s)	2024-02-20 10:31:13.977+00
2298ecb6-3378-483e-aeba-7168f31a15a0	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	held_by	The National Archives, Kew	2024-02-20 10:31:13.98+00
d6dc6f89-7d70-4848-b1ba-903d697e99e9	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	closure_type	Open	2024-02-20 10:31:13.984+00
47f25c26-b8dd-495d-96e6-0623fb8ed47f	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	title_closed	false	2024-02-20 10:31:13.987+00
f0754f29-aff0-407c-a222-5a13d9d01f5c	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	description_closed	false	2024-02-20 10:31:13.99+00
ba5bbba9-3ca0-4fda-a25d-ba7ff8148900	70858fca-f2fb-45c4-b5ca-8cc4bb43e05a	language	English	2024-02-20 10:31:13.993+00
c9523333-d777-4a6d-94a8-0645894442c2	2574830a-7ea1-4eea-8f4a-e6058437e848	file_name	DTP.docx	2024-02-20 10:31:14+00
90b13c3a-ace9-4c90-9052-76f6b08a9081	2574830a-7ea1-4eea-8f4a-e6058437e848	file_type	File	2024-02-20 10:31:14.003+00
7f1edb9a-ec94-45b9-8ae4-d047841fbb0f	2574830a-7ea1-4eea-8f4a-e6058437e848	file_size	70263	2024-02-20 10:31:14.006+00
3acbc7a7-90a8-4bb8-9fd8-161520b005ab	2574830a-7ea1-4eea-8f4a-e6058437e848	rights_copyright	Crown Copyright	2024-02-20 10:31:14.008+00
01723042-08c3-47ec-a70b-01815e36c1d9	2574830a-7ea1-4eea-8f4a-e6058437e848	legal_status	Public Record(s)	2024-02-20 10:31:14.011+00
24ebde3f-88bc-4766-933a-9c648b08437e	2574830a-7ea1-4eea-8f4a-e6058437e848	held_by	The National Archives, Kew	2024-02-20 10:31:14.014+00
c8b93849-1ac7-4555-b997-1b295d3380a8	2574830a-7ea1-4eea-8f4a-e6058437e848	date_last_modified	2022-08-03T13:47:13	2024-02-20 10:31:14.016+00
9e226f58-4619-424b-90a2-07faf75ee186	2574830a-7ea1-4eea-8f4a-e6058437e848	closure_type	Open	2024-02-20 10:31:14.019+00
6d9a7dc9-3482-4966-91c5-bbab116c8f29	2574830a-7ea1-4eea-8f4a-e6058437e848	title_closed	false	2024-02-20 10:31:14.021+00
6d4b9ea9-a4bc-465d-a1db-fc62e7456d73	2574830a-7ea1-4eea-8f4a-e6058437e848	description_closed	false	2024-02-20 10:31:14.024+00
9a7b3fdb-4bfb-4448-aa2a-8e0f0f0d68ab	2574830a-7ea1-4eea-8f4a-e6058437e848	language	English	2024-02-20 10:31:14.026+00
516dc77d-a130-41f5-a3c9-35c24ab74b7b	0f52912b-78a6-4e58-bda7-0c2f636e2040	file_name	delivery-form-digital.doc	2024-02-20 10:31:14.036+00
f46a9333-8fbc-49b8-8dac-504c2dd83154	0f52912b-78a6-4e58-bda7-0c2f636e2040	file_type	File	2024-02-20 10:31:14.039+00
eae44441-ec69-430c-82e5-e25ae7fa05c3	0f52912b-78a6-4e58-bda7-0c2f636e2040	file_size	139776	2024-02-20 10:31:14.041+00
ca075b4c-8441-4ae4-8fb7-a88a2ac7e700	0f52912b-78a6-4e58-bda7-0c2f636e2040	rights_copyright	Crown Copyright	2024-02-20 10:31:14.044+00
851c71be-42d3-44b0-9f0a-f3eafb0679d3	0f52912b-78a6-4e58-bda7-0c2f636e2040	legal_status	Public Record(s)	2024-02-20 10:31:14.049+00
c2134cb0-9a0e-4760-a5eb-0fd2cd2aa14d	0f52912b-78a6-4e58-bda7-0c2f636e2040	held_by	The National Archives, Kew	2024-02-20 10:31:14.051+00
c4efc16f-e07c-4ff4-9958-12a242095d9b	0f52912b-78a6-4e58-bda7-0c2f636e2040	date_last_modified	2022-08-03T13:47:07	2024-02-20 10:31:14.06+00
5b8658c3-675a-4dc4-b1d6-ce9fa988d6d3	0f52912b-78a6-4e58-bda7-0c2f636e2040	closure_type	Open	2024-02-20 10:31:14.064+00
9fc53ec8-8456-497d-b6bf-7ed4bdbe6344	0f52912b-78a6-4e58-bda7-0c2f636e2040	title_closed	false	2024-02-20 10:31:14.067+00
60d7281a-e98e-4933-baf9-6533f048c9e4	0f52912b-78a6-4e58-bda7-0c2f636e2040	description_closed	false	2024-02-20 10:31:14.07+00
2aa7d8f9-f4c6-471b-911e-a0a17a638d3c	0f52912b-78a6-4e58-bda7-0c2f636e2040	language	English	2024-02-20 10:31:14.073+00
2e9dea18-ac7c-477d-a60e-9b89669bccca	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	file_name	Workflows	2024-02-20 10:31:14.083+00
acfafcaf-b958-4e97-8580-b5f63f8d4a80	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	file_type	Folder	2024-02-20 10:31:14.085+00
390c1666-17ff-4471-b6a9-c24a9821f559	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	rights_copyright	Crown Copyright	2024-02-20 10:31:14.087+00
a2ea1285-5e73-4537-a80c-9c8b167a2c02	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	legal_status	Public Record(s)	2024-02-20 10:31:14.09+00
53cf8f3f-eb5c-4ed9-9062-319b0c774fab	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	held_by	The National Archives, Kew	2024-02-20 10:31:14.094+00
890db2e1-4344-4558-a657-588e25087466	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	closure_type	Open	2024-02-20 10:31:14.096+00
d8c4406a-e180-411e-8f22-b26d78b6904f	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	title_closed	false	2024-02-20 10:31:14.098+00
62bc4220-bfbf-4043-a695-dd26da078e4e	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	description_closed	false	2024-02-20 10:31:14.101+00
d6a9b062-af27-4cbb-b07c-fe8764f913c5	596d6280-2ebf-4f32-a5e5-e54faa73f4ad	language	English	2024-02-20 10:31:14.103+00
b090c3cf-9d03-4b2b-bf2f-f88c9c61484d	ac20000c-eef8-4941-93ab-6ba684076bee	file_name	Digital Transfer training email .msg	2024-02-20 10:31:14.111+00
e38a0f58-fd68-4178-8cea-1c7a524c2494	ac20000c-eef8-4941-93ab-6ba684076bee	file_type	File	2024-02-20 10:31:14.115+00
8eac07d8-e086-47ce-b121-38fa7e8284f9	ac20000c-eef8-4941-93ab-6ba684076bee	file_size	39424	2024-02-20 10:31:14.119+00
3699dd0a-5760-41e5-93fb-11705c4caebb	ac20000c-eef8-4941-93ab-6ba684076bee	rights_copyright	Crown Copyright	2024-02-20 10:31:14.127+00
f6b87348-dd6d-492a-b1e0-73dc1910c8d9	ac20000c-eef8-4941-93ab-6ba684076bee	legal_status	Public Record(s)	2024-02-20 10:31:14.132+00
2137bb90-759e-456b-a0b1-c88da9f08e7c	ac20000c-eef8-4941-93ab-6ba684076bee	held_by	The National Archives, Kew	2024-02-20 10:31:14.135+00
f82d8e4f-d250-4a83-9340-1ef6006a4f53	ac20000c-eef8-4941-93ab-6ba684076bee	date_last_modified	2022-08-03T13:47:09	2024-02-20 10:31:14.138+00
fc799c73-2fc5-4dcc-a63e-b2ab5ce64359	ac20000c-eef8-4941-93ab-6ba684076bee	closure_type	Open	2024-02-20 10:31:14.14+00
bb223420-e659-4d18-b41a-debc2a29ed3b	ac20000c-eef8-4941-93ab-6ba684076bee	title_closed	false	2024-02-20 10:31:14.142+00
eedc5cac-b1e0-4b6a-8a29-4c8bbd06f8d1	ac20000c-eef8-4941-93ab-6ba684076bee	description_closed	false	2024-02-20 10:31:14.145+00
df77ffd6-9fd4-4bf2-a7d7-f7b0c1e94ecd	ac20000c-eef8-4941-93ab-6ba684076bee	language	English	2024-02-20 10:31:14.147+00
82443267-0b18-4a2e-8f1f-af9b3bf52dbf	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	file_name	Presentation.pptx	2024-02-20 10:31:14.159+00
f8bb23f1-057d-47c0-a853-8664deb9b4f8	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	file_type	File	2024-02-20 10:31:14.162+00
3854c75e-ef0a-437f-b2ef-433a9ca28cec	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	file_size	697817	2024-02-20 10:31:14.164+00
15b54638-7243-4358-b22e-4aa887dd4d08	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	rights_copyright	Crown Copyright	2024-02-20 10:31:14.167+00
7f49eb68-655e-4cdd-a476-472586b34e08	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	legal_status	Public Record(s)	2024-02-20 10:31:14.17+00
80e34a0f-b7d4-49fd-839c-21b2495a9ed6	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	held_by	The National Archives, Kew	2024-02-20 10:31:14.172+00
5f8d14b7-296d-44ee-8f8b-55b8b5c31410	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	date_last_modified	2022-08-03T13:47:21	2024-02-20 10:31:14.175+00
2b04328e-af7e-494f-a04b-784b4f506a24	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	closure_type	Closed	2024-02-20 10:31:14.177+00
4f22bc42-df0e-4226-9e55-013c3960d915	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	closure_start_date	2022-08-03T00:00:00	2024-02-20 10:31:14.18+00
9165eb7e-01d0-428f-9dfa-e7869d8578fd	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	closure_period	100	2024-02-20 10:31:14.182+00
fedead0f-b115-4428-99f6-9253dbfdeee8	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	foi_exemption_code	24|40(2)	2024-02-20 10:31:14.185+00
b6e3c7fe-72fb-449b-bb2c-1b081806de74	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	foi_exemption_asserted	2023-08-09T00:00:00	2024-02-20 10:31:14.189+00
abb1c46e-b6f4-4ad5-9b13-03d93b7a7926	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	title_closed	false	2024-02-20 10:31:14.191+00
332d8d88-e581-42b8-b55e-8a9e4f9dd0ed	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	description_closed	false	2024-02-20 10:31:14.193+00
ea6e0013-0dab-45c7-8eb7-ef44a7d9805b	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	language	English	2024-02-20 10:31:14.196+00
766c6fcc-78da-4456-a022-f6cdc6662944	c6e5150c-2cb1-4f5f-8782-e8eab94dc562	opening_date	2122-08-04T13:47:21	2024-02-20 10:31:14.198+00
03936aef-4cdc-452a-a930-200887bc75da	2a426981-df85-4c94-9885-8b7760c86115	file_name	DTP_ Sensitivity review process.docx	2024-02-20 10:31:14.209+00
4a4e2a9b-36cd-47ca-8eba-fedc0301d7df	2a426981-df85-4c94-9885-8b7760c86115	file_type	File	2024-02-20 10:31:14.218+00
9eba0160-daad-4754-b2d5-0ca041981c53	2a426981-df85-4c94-9885-8b7760c86115	file_size	70674	2024-02-20 10:31:14.221+00
24d8ccc8-5e6c-4fe3-8245-58f8245ee4af	2a426981-df85-4c94-9885-8b7760c86115	rights_copyright	Crown Copyright	2024-02-20 10:31:14.224+00
932fafb6-f7d6-4387-9daf-26228bac9981	2a426981-df85-4c94-9885-8b7760c86115	legal_status	Public Record(s)	2024-02-20 10:31:14.228+00
aba0c6a4-8dbc-416b-af95-3d2081059703	2a426981-df85-4c94-9885-8b7760c86115	held_by	The National Archives, Kew	2024-02-20 10:31:14.231+00
cfe8575f-60b2-4141-859f-71fa8f6eb5b7	2a426981-df85-4c94-9885-8b7760c86115	date_last_modified	2022-08-03T13:47:39	2024-02-20 10:31:14.234+00
bfc749c9-712f-4944-98f7-c1844fd1cf2c	2a426981-df85-4c94-9885-8b7760c86115	closure_type	Open	2024-02-20 10:31:14.236+00
5edff7d1-1ab6-4b5d-b384-7f70bc3bcbf0	2a426981-df85-4c94-9885-8b7760c86115	title_closed	false	2024-02-20 10:31:14.239+00
08066754-6772-4603-b55e-01ca523a82aa	2a426981-df85-4c94-9885-8b7760c86115	language	English	2024-02-20 10:31:14.245+00
c28ad284-a5a6-4a32-b59a-cb42407802cf	b43f6060-6df6-4cf4-a57a-e29f208e17ed	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-20 10:31:14.257+00
15420e48-3654-41a1-881b-042a1c21f916	b43f6060-6df6-4cf4-a57a-e29f208e17ed	file_type	File	2024-02-20 10:31:14.259+00
5c36f6fa-da88-42dd-a9e4-1b755ef7f92e	b43f6060-6df6-4cf4-a57a-e29f208e17ed	file_size	177875	2024-02-20 10:31:14.263+00
799079d7-dbdb-4f99-8856-9789ecbe616b	b43f6060-6df6-4cf4-a57a-e29f208e17ed	rights_copyright	Crown Copyright	2024-02-20 10:31:14.27+00
7fad3f5f-e696-4eb6-a0e2-44637239545b	b43f6060-6df6-4cf4-a57a-e29f208e17ed	legal_status	Public Record(s)	2024-02-20 10:31:14.277+00
8dd458f5-26d6-4d3f-abe1-f8e2f5c0c25f	b43f6060-6df6-4cf4-a57a-e29f208e17ed	held_by	The National Archives, Kew	2024-02-20 10:31:14.28+00
f77b1fc3-3c7a-4cde-b454-7c3690c41195	b43f6060-6df6-4cf4-a57a-e29f208e17ed	date_last_modified	2022-08-03T13:47:24	2024-02-20 10:31:14.282+00
b9ab7927-a0ca-4ed0-b14a-8f21fb53ed79	b43f6060-6df6-4cf4-a57a-e29f208e17ed	closure_type	Open	2024-02-20 10:31:14.285+00
bcc077da-df1f-4138-8f3f-e4a5f22681d8	b43f6060-6df6-4cf4-a57a-e29f208e17ed	title_closed	false	2024-02-20 10:31:14.287+00
267b7d36-0ce5-44ce-a722-55ce9ba76ac7	b43f6060-6df6-4cf4-a57a-e29f208e17ed	description_closed	false	2024-02-20 10:31:14.29+00
b8b9c211-7e7d-480a-be55-26e7791e63f5	b43f6060-6df6-4cf4-a57a-e29f208e17ed	language	English	2024-02-20 10:31:14.292+00
aba14f25-1844-4387-9666-8951629ffbed	f26f1475-7652-4e8d-8052-cb68ac009b36	file_name	Draft DDRO 05.docx	2024-02-20 10:31:14.302+00
4299d530-1123-403f-8b62-e16fd2493dee	f26f1475-7652-4e8d-8052-cb68ac009b36	file_type	File	2024-02-20 10:31:14.304+00
cd4a2b70-12cd-4391-9872-c0570ea88ebb	f26f1475-7652-4e8d-8052-cb68ac009b36	file_size	21707	2024-02-20 10:31:14.307+00
df24c6dc-c6d0-4440-99b4-1a4db3340bf1	f26f1475-7652-4e8d-8052-cb68ac009b36	rights_copyright	Crown Copyright	2024-02-20 10:31:14.31+00
7768f5f3-e502-4951-a257-75f3199b4316	f26f1475-7652-4e8d-8052-cb68ac009b36	legal_status	Public Record(s)	2024-02-20 10:31:14.312+00
07d44254-d505-439c-8fed-16a6ccd4d4f0	f26f1475-7652-4e8d-8052-cb68ac009b36	held_by	The National Archives, Kew	2024-02-20 10:31:14.315+00
48f3d0c4-f2cf-4c86-bc1b-c6fcd1e70b84	f26f1475-7652-4e8d-8052-cb68ac009b36	date_last_modified	2022-08-03T13:47:11	2024-02-20 10:31:14.318+00
467b8fbd-26b1-4f57-9c4d-6e02519e9f3e	f26f1475-7652-4e8d-8052-cb68ac009b36	closure_type	Open	2024-02-20 10:31:14.32+00
e82b96bc-202e-4f5c-b8bc-7ccf0191ef74	f26f1475-7652-4e8d-8052-cb68ac009b36	title_closed	false	2024-02-20 10:31:14.322+00
ea12f49d-6e54-4a86-af38-d0cee114e62a	f26f1475-7652-4e8d-8052-cb68ac009b36	description_closed	false	2024-02-20 10:31:14.325+00
6dcd9212-cf30-4918-b3b3-78bd77e916c1	f26f1475-7652-4e8d-8052-cb68ac009b36	language	English	2024-02-20 10:31:14.327+00
cdd4fde0-c5f8-4f57-b075-dc9acae4d92b	097e1fde-70f5-4eef-9a46-c85ea4350bf7	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-20 10:31:14.338+00
8d773283-b70e-483f-a117-5a0b7870c071	097e1fde-70f5-4eef-9a46-c85ea4350bf7	file_type	File	2024-02-20 10:31:14.34+00
021ab6ee-04a0-4dde-aa2e-b9e72c96e24f	097e1fde-70f5-4eef-9a46-c85ea4350bf7	file_size	68364	2024-02-20 10:31:14.343+00
9f8a0e5f-5688-4081-bc90-eabe0c351e44	097e1fde-70f5-4eef-9a46-c85ea4350bf7	rights_copyright	Crown Copyright	2024-02-20 10:31:14.346+00
292a9cea-54b6-49c4-9f68-5cd2fd537a95	097e1fde-70f5-4eef-9a46-c85ea4350bf7	legal_status	Public Record(s)	2024-02-20 10:31:14.348+00
b7a64c51-b2ed-4e9b-8a38-996035add93b	097e1fde-70f5-4eef-9a46-c85ea4350bf7	held_by	The National Archives, Kew	2024-02-20 10:31:14.354+00
d628b584-df76-4b43-83c6-2f8a5c9564c3	097e1fde-70f5-4eef-9a46-c85ea4350bf7	date_last_modified	2022-08-03T13:47:35	2024-02-20 10:31:14.357+00
4e1b67af-658f-44e7-9b38-bf50aaed8f4d	097e1fde-70f5-4eef-9a46-c85ea4350bf7	closure_type	Open	2024-02-20 10:31:14.36+00
dadf079b-8e59-4506-9c81-9b75255485c4	097e1fde-70f5-4eef-9a46-c85ea4350bf7	title_closed	false	2024-02-20 10:31:14.362+00
a6fb03e0-35a4-4873-bafe-366f1304cd02	097e1fde-70f5-4eef-9a46-c85ea4350bf7	description_closed	false	2024-02-20 10:31:14.364+00
e15858b6-06ab-40de-a2ab-5453280e6283	097e1fde-70f5-4eef-9a46-c85ea4350bf7	language	English	2024-02-20 10:31:14.367+00
9a2da90f-063e-4970-8115-15315c703485	8f67e50d-9082-42af-84e3-80cb616a6665	file_name	Response Procedure.docx	2024-02-20 10:31:14.377+00
3ef9f3f5-06fa-457c-82ef-c2b206fa6437	8f67e50d-9082-42af-84e3-80cb616a6665	file_type	File	2024-02-20 10:31:14.38+00
eae88f88-1b39-45b1-a519-c0ebf2367563	8f67e50d-9082-42af-84e3-80cb616a6665	file_size	12610	2024-02-20 10:31:14.382+00
8f80585e-6eae-42b1-9a62-99ca26b8fe74	8f67e50d-9082-42af-84e3-80cb616a6665	rights_copyright	Crown Copyright	2024-02-20 10:31:14.385+00
2c2d33ab-567d-4b28-9160-fa8b4c569cb5	8f67e50d-9082-42af-84e3-80cb616a6665	legal_status	Public Record(s)	2024-02-20 10:31:14.387+00
6c148f39-7c83-4403-b84c-ec2678788090	8f67e50d-9082-42af-84e3-80cb616a6665	held_by	The National Archives, Kew	2024-02-20 10:31:14.391+00
cf155ebe-f17b-4681-aaf4-d357b70d09c6	8f67e50d-9082-42af-84e3-80cb616a6665	date_last_modified	2022-08-03T13:47:33	2024-02-20 10:31:14.393+00
50837a4e-65ea-4fc5-879f-33ddb755d909	8f67e50d-9082-42af-84e3-80cb616a6665	closure_type	Open	2024-02-20 10:31:14.396+00
a845e5bb-dd95-42d6-bd16-ddb8f5a23cf3	8f67e50d-9082-42af-84e3-80cb616a6665	title_closed	false	2024-02-20 10:31:14.398+00
6ea2dd84-8c6e-4c1c-914f-7bede445ed2d	8f67e50d-9082-42af-84e3-80cb616a6665	description_closed	false	2024-02-20 10:31:14.401+00
58d53940-2360-4a53-9944-7525a1dd3ab5	8f67e50d-9082-42af-84e3-80cb616a6665	language	English	2024-02-20 10:31:14.403+00
32904bdc-b3a6-4719-a877-1be65dd1ca19	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	file_name	Emergency Contact Details Paul Young.docx	2024-02-20 10:31:14.422+00
b39c01e7-1f2c-44c9-bdc4-469ac8038bec	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	file_type	File	2024-02-20 10:31:14.425+00
549c9a20-d734-4dd9-aa29-8564066fb3a8	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	file_size	12825	2024-02-20 10:31:14.428+00
cc99d8d8-6479-4596-a42e-7ad5085ee016	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	rights_copyright	Crown Copyright	2024-02-20 10:31:14.43+00
1a2fdf5b-3b03-4268-ba4f-7ab7eb106453	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	legal_status	Public Record(s)	2024-02-20 10:31:14.433+00
6b8d4dca-1786-4dd3-b961-0d371b0906bd	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	held_by	The National Archives, Kew	2024-02-20 10:31:14.436+00
b331b7a8-5c89-42ed-9442-af5bbec10b1c	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	date_last_modified	2022-08-03T13:47:28	2024-02-20 10:31:14.439+00
86f0e8dd-fcaa-4852-8e49-1bd2a4970837	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	closure_type	Closed	2024-02-20 10:31:14.443+00
acbaf12c-cba8-44ed-a04e-916b75b26907	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	closure_start_date	2021-12-25T00:00:00	2024-02-20 10:31:14.446+00
59983f7b-859a-4c24-9c11-a7eb5d77b6af	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	closure_period	100	2024-02-20 10:31:14.448+00
d85a88db-63ca-452b-ae1a-c223509b2c49	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	foi_exemption_code	40(2)	2024-02-20 10:31:14.45+00
9f2e27e2-e928-441d-ac8f-a209f753a32c	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	foi_exemption_asserted	2023-08-09T00:00:00	2024-02-20 10:31:14.453+00
68fc0c09-ced4-4534-90f7-2e99fbfc8c12	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	title_closed	true	2024-02-20 10:31:14.455+00
d30ae33f-53ab-48b5-a4aa-94884b42ccf6	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	title_alternate	Emergency Contact Details [name withheld]	2024-02-20 10:31:14.457+00
fde71fb5-0af8-44a0-8bca-661607d5b7bb	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	description	Emergency Contact Details Paul Young	2024-02-20 10:31:14.459+00
b2912737-78ac-446b-aab8-b5ee57b05076	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	description_closed	true	2024-02-20 10:31:14.462+00
58e94a71-c360-40bc-8436-4a4cbbe7423f	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	description_alternate	Emergency Contact Details [name withheld]	2024-02-20 10:31:14.464+00
4cd910e5-b633-4742-9ecd-bb1a535cee6b	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	language	English	2024-02-20 10:31:14.466+00
6b6b0b44-1acb-4f4b-8e4b-0b7cc1dbf640	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	end_date	2021-12-25T00:00:00	2024-02-20 10:31:14.469+00
2c5be1bf-1931-453f-bc6e-84463dcb25ef	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	former_reference_department	Former 1	2024-02-20 10:31:14.471+00
4e0c2359-3a46-4dea-89d8-ea984d8cd619	df115d92-f1cb-41dc-95f0-1f3bfe07ae45	opening_date	2121-12-26T00:00:00	2024-02-20 10:31:14.473+00
f5b51306-de78-4209-85fe-8c177c20afe2	2be81626-7443-4e1f-b228-c9aa9942cd32	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-20 10:31:14.482+00
4e061a73-3a15-4fa4-b632-a160af963155	2be81626-7443-4e1f-b228-c9aa9942cd32	file_type	File	2024-02-20 10:31:14.484+00
00216cdd-9d36-4ccf-b1f5-9060ecc4c543	2be81626-7443-4e1f-b228-c9aa9942cd32	file_size	70263	2024-02-20 10:31:14.487+00
e584b18c-3d74-4b44-a180-01adf5a701e5	2be81626-7443-4e1f-b228-c9aa9942cd32	rights_copyright	Crown Copyright	2024-02-20 10:31:14.489+00
4916ee34-80df-46dc-a148-089f17733907	2be81626-7443-4e1f-b228-c9aa9942cd32	legal_status	Public Record(s)	2024-02-20 10:31:14.492+00
961e02cb-c36e-44f9-8a53-427bfdc6133e	2be81626-7443-4e1f-b228-c9aa9942cd32	held_by	The National Archives, Kew	2024-02-20 10:31:14.494+00
3aa79af1-1ff2-4b65-9721-efbee5a10b1f	2be81626-7443-4e1f-b228-c9aa9942cd32	date_last_modified	2022-08-03T13:47:37	2024-02-20 10:31:14.497+00
dfe0735e-11f6-42ed-90d2-cee78698d914	2be81626-7443-4e1f-b228-c9aa9942cd32	closure_type	Open	2024-02-20 10:31:14.5+00
b9988e61-b0a8-4d42-9030-ceb67673096b	2be81626-7443-4e1f-b228-c9aa9942cd32	title_closed	false	2024-02-20 10:31:14.502+00
85eaf084-65ca-425e-a3e6-a74d0782ce76	2be81626-7443-4e1f-b228-c9aa9942cd32	description_closed	false	2024-02-20 10:31:14.505+00
df73c830-a43d-4c3c-8dba-1482c8644915	2be81626-7443-4e1f-b228-c9aa9942cd32	language	English	2024-02-20 10:31:14.51+00
2f47bb33-34c4-485a-89b0-2156dfd62605	326e55e9-b406-46ef-9570-ca51fb02e944	file_name	content	2024-02-20 10:31:14.524+00
11da7f14-8870-4e71-aa81-d148994ae365	326e55e9-b406-46ef-9570-ca51fb02e944	file_type	Folder	2024-02-20 10:31:14.527+00
2329dd35-f1e3-496a-8538-3a3bccfc87d8	326e55e9-b406-46ef-9570-ca51fb02e944	rights_copyright	Crown Copyright	2024-02-20 10:31:14.529+00
d68944ff-5ff3-4e9f-a15a-07c05fbbf141	326e55e9-b406-46ef-9570-ca51fb02e944	legal_status	Public Record(s)	2024-02-20 10:31:14.532+00
8cf250f8-e325-4f39-91be-831fcd19cf44	326e55e9-b406-46ef-9570-ca51fb02e944	held_by	The National Archives, Kew	2024-02-20 10:31:14.534+00
ba11d8d2-5c77-4d4b-b065-12e84cee16aa	326e55e9-b406-46ef-9570-ca51fb02e944	closure_type	Open	2024-02-20 10:31:14.537+00
1b75c570-7b65-46f0-b868-2ca3e8ac4403	326e55e9-b406-46ef-9570-ca51fb02e944	title_closed	false	2024-02-20 10:31:14.539+00
95678ff5-c1e6-4c2d-a31d-725a267a51d9	326e55e9-b406-46ef-9570-ca51fb02e944	description_closed	false	2024-02-20 10:31:14.541+00
7a178cf4-494c-42ea-8596-dd004368a9c9	326e55e9-b406-46ef-9570-ca51fb02e944	language	English	2024-02-20 10:31:14.549+00
07ec735f-8a6f-4ac2-be02-4c123ccb5577	3c65376c-bed9-44d0-b391-53acbe561ec8	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-20 10:32:23.553+00
206afaed-1f89-4d27-8f93-8bc29b18a45e	3c65376c-bed9-44d0-b391-53acbe561ec8	file_type	File	2024-02-20 10:32:23.555+00
4f348519-7e9d-44c3-8661-4ef543f42aec	3c65376c-bed9-44d0-b391-53acbe561ec8	file_size	68364	2024-02-20 10:32:23.557+00
3bbd2891-3817-4f1c-ae18-3b6f691e0479	3c65376c-bed9-44d0-b391-53acbe561ec8	rights_copyright	Crown Copyright	2024-02-20 10:32:23.562+00
9fbeb82f-1f02-470a-8d53-0389a4a65ea7	3c65376c-bed9-44d0-b391-53acbe561ec8	legal_status	Public Record(s)	2024-02-20 10:32:23.564+00
f0811a7f-edc4-4150-aad3-1c852c712dd9	3c65376c-bed9-44d0-b391-53acbe561ec8	held_by	The National Archives, Kew	2024-02-20 10:32:23.574+00
21a920f0-7458-4ecd-bd1b-87563b2f10c3	3c65376c-bed9-44d0-b391-53acbe561ec8	date_last_modified	2022-08-03T13:47:35	2024-02-20 10:32:23.577+00
4b01c8ad-28e4-4447-b708-6a325f5b347a	3c65376c-bed9-44d0-b391-53acbe561ec8	closure_type	Open	2024-02-20 10:32:23.579+00
a932ed7e-a443-4ad5-9dc0-10dd563f1149	3c65376c-bed9-44d0-b391-53acbe561ec8	title_closed	false	2024-02-20 10:32:23.58+00
44763617-72e0-4010-888a-92193e5ac6df	3c65376c-bed9-44d0-b391-53acbe561ec8	description_closed	false	2024-02-20 10:32:23.582+00
b671bab5-1646-4a28-bab5-6e518fca59d7	3c65376c-bed9-44d0-b391-53acbe561ec8	language	English	2024-02-20 10:32:23.584+00
a0fb8f4c-5f97-4bde-9c83-5420a0a70eee	8f710b6f-ac45-4a1d-b560-873618c253db	file_name	Response Procedure.docx	2024-02-20 10:32:23.599+00
977a31fc-3de7-4410-ad74-9457120f36d4	8f710b6f-ac45-4a1d-b560-873618c253db	file_type	File	2024-02-20 10:32:23.601+00
6e6e0f42-72a7-4058-b269-855b241c049a	8f710b6f-ac45-4a1d-b560-873618c253db	file_size	12610	2024-02-20 10:32:23.603+00
25192747-75c4-446b-920d-4f58664b5ddd	8f710b6f-ac45-4a1d-b560-873618c253db	rights_copyright	Crown Copyright	2024-02-20 10:32:23.605+00
bff42851-6d03-49c4-81e9-d8aebebb5474	8f710b6f-ac45-4a1d-b560-873618c253db	legal_status	Public Record(s)	2024-02-20 10:32:23.607+00
d7824a20-c7aa-4c1a-afba-448ed7e4d0ea	8f710b6f-ac45-4a1d-b560-873618c253db	held_by	The National Archives, Kew	2024-02-20 10:32:23.608+00
42c5d17e-4e6b-4210-a064-6543779fb2c9	8f710b6f-ac45-4a1d-b560-873618c253db	date_last_modified	2022-08-03T13:47:33	2024-02-20 10:32:23.609+00
bd6798c6-721a-45fe-a3e7-85aa4e47e273	8f710b6f-ac45-4a1d-b560-873618c253db	closure_type	Open	2024-02-20 10:32:23.612+00
e7ab64db-b392-464e-b212-05c9436cca7b	8f710b6f-ac45-4a1d-b560-873618c253db	title_closed	false	2024-02-20 10:32:23.614+00
e8fb3ba5-7686-4344-8443-c437b18cbe8e	8f710b6f-ac45-4a1d-b560-873618c253db	description_closed	false	2024-02-20 10:32:23.62+00
bb84c683-3518-42f8-a9cf-3c606824ca18	8f710b6f-ac45-4a1d-b560-873618c253db	language	English	2024-02-20 10:32:23.624+00
83033aab-d5d6-42f0-ba6a-969d0f9623df	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	file_name	content	2024-02-20 10:32:23.635+00
6d20135f-cc0b-4498-ae78-58bd92dbbc94	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	file_type	Folder	2024-02-20 10:32:23.636+00
aa823168-4d5a-432d-a418-c0d6c3ad2c39	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	rights_copyright	Crown Copyright	2024-02-20 10:32:23.637+00
1c189d90-47db-49b3-8d10-c77592241a8e	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	legal_status	Public Record(s)	2024-02-20 10:32:23.639+00
bd432a97-81ca-4c0d-9b07-869b6680ea0f	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	held_by	The National Archives, Kew	2024-02-20 10:32:23.64+00
47beaa58-0b8f-4aac-9343-e99b87610b04	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	closure_type	Open	2024-02-20 10:32:23.641+00
db7628d8-e059-43ad-9e92-1c863441043e	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	title_closed	false	2024-02-20 10:32:23.643+00
528f36db-b445-4330-bb8c-b2bb99ab097e	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	description_closed	false	2024-02-20 10:32:23.645+00
b055767c-0473-4ca0-9d6b-da33770b9a12	8b9ce388-3c0d-44ba-aaa6-1ac86c99e901	language	English	2024-02-20 10:32:23.646+00
21606607-323d-4352-bf79-f79e866e3858	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	file_name	Presentation.pptx	2024-02-20 10:32:23.651+00
954192ac-a988-4943-9b41-ab68eb0ba40a	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	file_type	File	2024-02-20 10:32:23.652+00
8e0a662f-6789-44ed-80ea-2360f42935e3	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	file_size	697817	2024-02-20 10:32:23.655+00
597cf549-8b0a-4671-9281-aba26f1fc81f	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	rights_copyright	Crown Copyright	2024-02-20 10:32:23.657+00
ba842eda-5573-463c-b38e-136099e337bc	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	legal_status	Public Record(s)	2024-02-20 10:32:23.658+00
a668f695-5828-413d-ac43-a84eec3248c6	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	held_by	The National Archives, Kew	2024-02-20 10:32:23.66+00
e09bf785-80d9-4345-bf07-cf3857549566	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	date_last_modified	2022-08-03T13:47:21	2024-02-20 10:32:23.661+00
b45b46bf-c18a-4571-9408-a878c3c5fdb5	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	closure_type	Open	2024-02-20 10:32:23.664+00
dd3b1693-19e0-41e8-a347-85049ad579a1	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	title_closed	false	2024-02-20 10:32:23.669+00
ad8d2ed1-0a1a-40f7-858d-7440f18eca68	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	description_closed	false	2024-02-20 10:32:23.671+00
19cf328d-ad3f-42a6-a4d8-71197a75a6e9	c1f7aac4-2fa7-4fa4-a5e1-3d7fa2e24cf5	language	English	2024-02-20 10:32:23.674+00
01e2ae04-2dc2-47cc-8542-b39e548c57b3	81068c3a-ae92-4d1b-8626-321a8437a9b0	file_name	Remove.docx	2024-02-20 10:32:23.682+00
2464343b-c160-47ff-bbd0-793dc500c713	81068c3a-ae92-4d1b-8626-321a8437a9b0	file_type	File	2024-02-20 10:32:23.69+00
2a0f6d7c-fab7-4bc3-b087-caf1357a250e	81068c3a-ae92-4d1b-8626-321a8437a9b0	file_size	12609	2024-02-20 10:32:23.692+00
68703a3e-2c1f-4e6f-91cd-5b6b85b119b9	81068c3a-ae92-4d1b-8626-321a8437a9b0	rights_copyright	Crown Copyright	2024-02-20 10:32:23.694+00
2129397e-ab21-4e46-bf70-9984853f99b2	81068c3a-ae92-4d1b-8626-321a8437a9b0	legal_status	Public Record(s)	2024-02-20 10:32:23.696+00
06a0bf7d-a3ce-4772-b256-3b6e6220029e	81068c3a-ae92-4d1b-8626-321a8437a9b0	held_by	The National Archives, Kew	2024-02-20 10:32:23.7+00
94cb1c69-9a17-4e16-82c3-9e54651a677d	81068c3a-ae92-4d1b-8626-321a8437a9b0	date_last_modified	2022-08-03T13:47:41	2024-02-20 10:32:23.702+00
fec571e4-a9cf-4320-9315-dfa502a28cb6	81068c3a-ae92-4d1b-8626-321a8437a9b0	closure_type	Open	2024-02-20 10:32:23.704+00
dda2dde5-73e6-41f4-8976-47074d0f8743	81068c3a-ae92-4d1b-8626-321a8437a9b0	title_closed	false	2024-02-20 10:32:23.705+00
77bafa40-6200-4c35-80c0-34eeca0ebe0c	81068c3a-ae92-4d1b-8626-321a8437a9b0	description_closed	false	2024-02-20 10:32:23.707+00
b1228226-2df3-466e-8483-5da28ffaf065	81068c3a-ae92-4d1b-8626-321a8437a9b0	language	English	2024-02-20 10:32:23.709+00
2657f942-f8e2-4647-acff-aa9963eb572e	e0321af1-38b5-4111-a3e6-261d04bf7677	file_name	delivery-form-digital.doc	2024-02-20 10:32:23.715+00
05b1a674-3f7c-4622-bf65-997165847177	e0321af1-38b5-4111-a3e6-261d04bf7677	file_type	File	2024-02-20 10:32:23.717+00
07dc67b6-e840-4857-bc14-f821f67f7388	e0321af1-38b5-4111-a3e6-261d04bf7677	file_size	139776	2024-02-20 10:32:23.718+00
916ee7c4-7f19-4ac5-a363-df08eabb9522	e0321af1-38b5-4111-a3e6-261d04bf7677	rights_copyright	Crown Copyright	2024-02-20 10:32:23.719+00
8de5bd6e-f614-4603-b6f8-506cce35751d	e0321af1-38b5-4111-a3e6-261d04bf7677	legal_status	Public Record(s)	2024-02-20 10:32:23.722+00
8f7eb498-6fdc-47a5-9457-aa85d65697bd	e0321af1-38b5-4111-a3e6-261d04bf7677	held_by	The National Archives, Kew	2024-02-20 10:32:23.724+00
fc27613c-8f27-4bd9-9dab-646c892c62af	e0321af1-38b5-4111-a3e6-261d04bf7677	date_last_modified	2022-08-03T13:47:07	2024-02-20 10:32:23.725+00
980240a2-ed96-453e-ae75-0064c07c8ede	e0321af1-38b5-4111-a3e6-261d04bf7677	closure_type	Open	2024-02-20 10:32:23.727+00
17004fbf-560e-4923-9858-f63efe531425	e0321af1-38b5-4111-a3e6-261d04bf7677	title_closed	false	2024-02-20 10:32:23.728+00
f4a2484e-46e1-4640-bb31-f0da598dc53d	e0321af1-38b5-4111-a3e6-261d04bf7677	description_closed	false	2024-02-20 10:32:23.729+00
4d0c7665-364a-49da-b593-f372a2adb84c	e0321af1-38b5-4111-a3e6-261d04bf7677	language	English	2024-02-20 10:32:23.731+00
76df813d-4e09-4be8-b9e3-3b0a0b57011c	f550d5b9-2570-4557-8435-cfaca366cee5	file_name	DTP_ Sensitivity review process.docx	2024-02-20 10:32:23.737+00
305dc5a5-281d-4e13-bbc7-3548a9cae3c5	f550d5b9-2570-4557-8435-cfaca366cee5	file_type	File	2024-02-20 10:32:23.738+00
b78e90c9-39da-4c74-9edd-9211013be1d7	f550d5b9-2570-4557-8435-cfaca366cee5	file_size	70674	2024-02-20 10:32:23.74+00
172f5f21-202e-49b2-a5bb-97d946277294	f550d5b9-2570-4557-8435-cfaca366cee5	rights_copyright	Crown Copyright	2024-02-20 10:32:23.741+00
fb9d9f9c-ed6e-4e21-9744-7ad2da26867f	f550d5b9-2570-4557-8435-cfaca366cee5	legal_status	Public Record(s)	2024-02-20 10:32:23.743+00
5acc2b95-2298-447d-9c5c-ea13d9996893	f550d5b9-2570-4557-8435-cfaca366cee5	held_by	The National Archives, Kew	2024-02-20 10:32:23.744+00
481653a8-1e4d-413e-91d5-997923946c3d	f550d5b9-2570-4557-8435-cfaca366cee5	date_last_modified	2022-08-03T13:47:39	2024-02-20 10:32:23.745+00
0ab610a6-c2e1-4e04-b6e1-4f560b6d6265	f550d5b9-2570-4557-8435-cfaca366cee5	closure_type	Open	2024-02-20 10:32:23.747+00
e133c9e0-784a-4029-bbfd-a6009eb582d8	f550d5b9-2570-4557-8435-cfaca366cee5	title_closed	false	2024-02-20 10:32:23.749+00
ab7697db-9b12-4fcb-a7bb-e6efa1896d89	f550d5b9-2570-4557-8435-cfaca366cee5	description_closed	false	2024-02-20 10:32:23.75+00
33e73eb5-3f3d-4339-8767-51509947341b	f550d5b9-2570-4557-8435-cfaca366cee5	language	English	2024-02-20 10:32:23.753+00
3715c4fc-0a37-4cf2-88a6-a01129eb5fa1	b430325c-3242-4d12-bb14-16025837f896	file_name	Emergency Contact Details Paul Young.docx	2024-02-20 10:32:23.76+00
fac3f71f-f141-487a-8006-1a2dd421c460	b430325c-3242-4d12-bb14-16025837f896	file_type	File	2024-02-20 10:32:23.762+00
c87174cc-1f46-479a-8039-6aa99d0d6a9e	b430325c-3242-4d12-bb14-16025837f896	file_size	12825	2024-02-20 10:32:23.763+00
66b64589-05dc-4d87-bffc-837ba919dfcd	b430325c-3242-4d12-bb14-16025837f896	rights_copyright	Crown Copyright	2024-02-20 10:32:23.765+00
f939af98-5e20-40c9-a2c1-073679777560	b430325c-3242-4d12-bb14-16025837f896	legal_status	Public Record(s)	2024-02-20 10:32:23.766+00
7ab77e24-0948-4721-a2af-a1d241d6678e	b430325c-3242-4d12-bb14-16025837f896	held_by	The National Archives, Kew	2024-02-20 10:32:23.768+00
e92f0cbb-82b1-4f17-b4f6-dd60e1e5aac2	b430325c-3242-4d12-bb14-16025837f896	date_last_modified	2022-08-03T13:47:28	2024-02-20 10:32:23.77+00
e7d408c7-036d-46a0-9756-2d1d3474bc92	b430325c-3242-4d12-bb14-16025837f896	closure_type	Open	2024-02-20 10:32:23.772+00
0faf96c2-47dc-4c8c-aad1-4b24d97a1a6b	b430325c-3242-4d12-bb14-16025837f896	title_closed	false	2024-02-20 10:32:23.773+00
a79afe93-cf47-40cc-838d-a5538494a8e2	b430325c-3242-4d12-bb14-16025837f896	description_closed	false	2024-02-20 10:32:23.775+00
7e282605-2b33-4c71-942c-090de38f4ada	b430325c-3242-4d12-bb14-16025837f896	language	English	2024-02-20 10:32:23.78+00
703fd992-7e96-4c34-8e87-380e9563359e	e499f9cf-b947-4f69-8300-24dd0a3aaa03	file_name	DTP.docx	2024-02-20 10:32:23.789+00
69031516-40cc-4491-8c6c-977335579fd3	e499f9cf-b947-4f69-8300-24dd0a3aaa03	file_type	File	2024-02-20 10:32:23.79+00
fc972153-c999-4f06-9094-aeee849804a9	e499f9cf-b947-4f69-8300-24dd0a3aaa03	file_size	70263	2024-02-20 10:32:23.791+00
d3762655-c926-4728-9035-2bf635cdbb50	e499f9cf-b947-4f69-8300-24dd0a3aaa03	rights_copyright	Crown Copyright	2024-02-20 10:32:23.793+00
0f42f561-5baf-4694-92be-b5923daefa77	e499f9cf-b947-4f69-8300-24dd0a3aaa03	legal_status	Public Record(s)	2024-02-20 10:32:23.794+00
abd415a3-9b75-485c-834b-4b07320aa9fd	e499f9cf-b947-4f69-8300-24dd0a3aaa03	held_by	The National Archives, Kew	2024-02-20 10:32:23.795+00
4955866e-d31d-4e87-a584-54dff896dc24	e499f9cf-b947-4f69-8300-24dd0a3aaa03	date_last_modified	2022-08-03T13:47:13	2024-02-20 10:32:23.797+00
e519eeaf-954d-4790-a704-78a896fc3a90	e499f9cf-b947-4f69-8300-24dd0a3aaa03	closure_type	Open	2024-02-20 10:32:23.798+00
db659af8-99bd-4b94-bf29-3b32dd0b2c1f	e499f9cf-b947-4f69-8300-24dd0a3aaa03	title_closed	false	2024-02-20 10:32:23.799+00
097866fa-8b52-4a86-a3b3-ade8fbccae3b	e499f9cf-b947-4f69-8300-24dd0a3aaa03	description_closed	false	2024-02-20 10:32:23.8+00
ec775341-7d35-40b7-b5ce-37212b9fa341	e499f9cf-b947-4f69-8300-24dd0a3aaa03	language	English	2024-02-20 10:32:23.802+00
1edbc36d-5717-4c59-87a8-e7ebad92263b	1263462f-8bbf-47cf-963d-2e7ef79c281d	file_name	Digital Transfer training email .msg	2024-02-20 10:32:23.813+00
eda6c597-1e3a-4453-90c8-3ec03978ba9a	1263462f-8bbf-47cf-963d-2e7ef79c281d	file_type	File	2024-02-20 10:32:23.814+00
3d3c368e-2472-429b-b6e3-a95b2794228e	1263462f-8bbf-47cf-963d-2e7ef79c281d	file_size	39424	2024-02-20 10:32:23.815+00
9f659319-a21f-41bc-9133-66383e1a115e	1263462f-8bbf-47cf-963d-2e7ef79c281d	rights_copyright	Crown Copyright	2024-02-20 10:32:23.817+00
94a8401f-cb01-4236-b413-a5f3cfe7ede7	1263462f-8bbf-47cf-963d-2e7ef79c281d	legal_status	Public Record(s)	2024-02-20 10:32:23.818+00
9592c24d-1a57-46b9-8651-d14d04adbca1	1263462f-8bbf-47cf-963d-2e7ef79c281d	held_by	The National Archives, Kew	2024-02-20 10:32:23.819+00
bda4c187-e808-4b59-bd54-51282726c184	1263462f-8bbf-47cf-963d-2e7ef79c281d	date_last_modified	2022-08-03T13:47:09	2024-02-20 10:32:23.82+00
14147c6a-49c7-46a5-8d66-1e0929ac59cc	1263462f-8bbf-47cf-963d-2e7ef79c281d	closure_type	Open	2024-02-20 10:32:23.822+00
0066ec5b-c9bb-46f1-bc33-a5da783b9f45	1263462f-8bbf-47cf-963d-2e7ef79c281d	title_closed	false	2024-02-20 10:32:23.83+00
72ee3a84-c7c3-4e37-a821-450a57db1473	1263462f-8bbf-47cf-963d-2e7ef79c281d	description_closed	false	2024-02-20 10:32:23.831+00
6956ac88-9ccf-4193-88de-7fcef07650b4	1263462f-8bbf-47cf-963d-2e7ef79c281d	language	English	2024-02-20 10:32:23.833+00
c2984cf0-4f54-4b70-b5f7-498e210800f9	c147d5e8-1ff8-46bd-924b-b87db8b143e8	file_name	Emergency Response Team	2024-02-20 10:32:23.839+00
c14d5ca0-3971-49f1-a108-40ac9bc68600	c147d5e8-1ff8-46bd-924b-b87db8b143e8	file_type	Folder	2024-02-20 10:32:23.84+00
47e0d011-6f47-4b93-81b4-b299b315a71c	c147d5e8-1ff8-46bd-924b-b87db8b143e8	rights_copyright	Crown Copyright	2024-02-20 10:32:23.841+00
b30fdecf-0367-40b7-a561-c1c6b295323a	c147d5e8-1ff8-46bd-924b-b87db8b143e8	legal_status	Public Record(s)	2024-02-20 10:32:23.843+00
ea4700b0-e506-468a-97e0-948476b0cee7	c147d5e8-1ff8-46bd-924b-b87db8b143e8	held_by	The National Archives, Kew	2024-02-20 10:32:23.844+00
957abff6-cfb8-4d37-abfe-060efd7e5ca8	c147d5e8-1ff8-46bd-924b-b87db8b143e8	closure_type	Open	2024-02-20 10:32:23.845+00
80658051-a44f-4b54-b032-9732920ab265	c147d5e8-1ff8-46bd-924b-b87db8b143e8	title_closed	false	2024-02-20 10:32:23.846+00
25bd73c2-4069-4f2c-b91d-e657e92a1ea5	c147d5e8-1ff8-46bd-924b-b87db8b143e8	description_closed	false	2024-02-20 10:32:23.848+00
0977944d-2467-494a-b61c-01f5388474d7	c147d5e8-1ff8-46bd-924b-b87db8b143e8	language	English	2024-02-20 10:32:23.849+00
80a1b5fb-b54b-4286-a929-6fe0f9dc26f7	afcf7478-56ee-4872-9d92-da4655a8972c	file_name	Response Policy.docx	2024-02-20 10:32:23.855+00
a14dd97d-67e8-4066-8951-ae95b756787f	afcf7478-56ee-4872-9d92-da4655a8972c	file_type	File	2024-02-20 10:32:23.856+00
b0908003-fa6d-4e4b-8b10-7567e22220d8	afcf7478-56ee-4872-9d92-da4655a8972c	file_size	12651	2024-02-20 10:32:23.858+00
0e4143a2-4e5d-4f53-a732-2c8739d5c421	afcf7478-56ee-4872-9d92-da4655a8972c	rights_copyright	Crown Copyright	2024-02-20 10:32:23.859+00
469be60d-0f34-4c0f-a31b-1dd86b382d14	afcf7478-56ee-4872-9d92-da4655a8972c	legal_status	Public Record(s)	2024-02-20 10:32:23.86+00
0208f8b8-f604-40ba-af5b-69aed7494764	afcf7478-56ee-4872-9d92-da4655a8972c	held_by	The National Archives, Kew	2024-02-20 10:32:23.861+00
60113de8-f20f-4aee-86e4-e1f3fda1f2a8	afcf7478-56ee-4872-9d92-da4655a8972c	date_last_modified	2022-08-03T13:47:31	2024-02-20 10:32:23.863+00
d66f00b6-f6c8-4151-86c8-27d9093bafb2	afcf7478-56ee-4872-9d92-da4655a8972c	closure_type	Open	2024-02-20 10:32:23.864+00
18d94cf7-3990-4325-923a-284349cf6ca1	afcf7478-56ee-4872-9d92-da4655a8972c	title_closed	false	2024-02-20 10:32:23.865+00
e7b3f7f5-a823-4f07-8ff1-673c11e728d2	afcf7478-56ee-4872-9d92-da4655a8972c	description_closed	false	2024-02-20 10:32:23.866+00
84249ec3-f0d2-415a-97fc-8e8dbe6e613a	afcf7478-56ee-4872-9d92-da4655a8972c	language	English	2024-02-20 10:32:23.867+00
7f3a0b1b-9071-40b0-beea-86d3de3b7734	2d3efaf1-154b-4c72-bea6-e220e092ab0c	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-20 10:32:23.873+00
48f5754c-5b31-4865-8de8-8dc36cbee594	2d3efaf1-154b-4c72-bea6-e220e092ab0c	file_type	File	2024-02-20 10:32:23.875+00
48b5e797-ac23-41f9-b386-79979ef60a04	2d3efaf1-154b-4c72-bea6-e220e092ab0c	file_size	70263	2024-02-20 10:32:23.876+00
1a2ede2b-b96d-4c47-80cf-d00521956891	2d3efaf1-154b-4c72-bea6-e220e092ab0c	rights_copyright	Crown Copyright	2024-02-20 10:32:23.877+00
d34c4120-39ad-47c3-94d0-ecf5e596d793	2d3efaf1-154b-4c72-bea6-e220e092ab0c	legal_status	Public Record(s)	2024-02-20 10:32:23.878+00
a7336901-a3b4-4e6c-adc0-f0965602d8b5	2d3efaf1-154b-4c72-bea6-e220e092ab0c	held_by	The National Archives, Kew	2024-02-20 10:32:23.879+00
b89558e2-8292-47b5-ae97-fe38aabee91e	2d3efaf1-154b-4c72-bea6-e220e092ab0c	date_last_modified	2022-08-03T13:47:37	2024-02-20 10:32:23.88+00
2e22aab4-8c43-4bba-bf5e-be690d465f98	2d3efaf1-154b-4c72-bea6-e220e092ab0c	closure_type	Open	2024-02-20 10:32:23.881+00
714f7047-2368-47a1-abdc-2e2af61289d9	2d3efaf1-154b-4c72-bea6-e220e092ab0c	title_closed	false	2024-02-20 10:32:23.883+00
4eec2d76-86b5-4c82-a67b-ada1746ec4ec	2d3efaf1-154b-4c72-bea6-e220e092ab0c	description_closed	false	2024-02-20 10:32:23.884+00
94344fea-c4a4-4f6e-86c4-395bd1f7765b	2d3efaf1-154b-4c72-bea6-e220e092ab0c	language	English	2024-02-20 10:32:23.885+00
f05902fc-a529-4498-846f-f1f8bf74d2e9	909cf5b8-bd73-432e-bbda-465f20bef6bd	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-20 10:32:23.891+00
8a023f44-8128-48a1-868d-f39440a4dc82	909cf5b8-bd73-432e-bbda-465f20bef6bd	file_type	File	2024-02-20 10:32:23.892+00
4db66de5-db61-4d31-a059-e239af5d81b3	909cf5b8-bd73-432e-bbda-465f20bef6bd	file_size	177875	2024-02-20 10:32:23.893+00
b09d43f8-a5f7-4fd6-b63b-adf46a8a69cd	909cf5b8-bd73-432e-bbda-465f20bef6bd	rights_copyright	Crown Copyright	2024-02-20 10:32:23.894+00
3d5ff0a0-e5db-472c-b4da-f8520f1a9733	909cf5b8-bd73-432e-bbda-465f20bef6bd	legal_status	Public Record(s)	2024-02-20 10:32:23.895+00
9f212f05-566b-4324-98e4-2a20eecf38de	909cf5b8-bd73-432e-bbda-465f20bef6bd	held_by	The National Archives, Kew	2024-02-20 10:32:23.897+00
c234fb62-a912-41db-99f7-d76678d44175	909cf5b8-bd73-432e-bbda-465f20bef6bd	date_last_modified	2022-08-03T13:47:24	2024-02-20 10:32:23.898+00
05cf08ad-03c3-4d32-a512-d03f5f7c29ee	909cf5b8-bd73-432e-bbda-465f20bef6bd	closure_type	Open	2024-02-20 10:32:23.9+00
b26934cd-8bbb-4343-a4d7-4a50aab68cd4	909cf5b8-bd73-432e-bbda-465f20bef6bd	title_closed	false	2024-02-20 10:32:23.901+00
0224fadc-b901-4bb0-b6ee-f671dd1a6705	909cf5b8-bd73-432e-bbda-465f20bef6bd	description_closed	false	2024-02-20 10:32:23.903+00
ececedd5-b188-46be-9a73-b89712178df6	909cf5b8-bd73-432e-bbda-465f20bef6bd	language	English	2024-02-20 10:32:23.904+00
cbfa1d06-0390-4f7e-975e-64cfad2ecf5e	3727c79b-6fac-4f80-b6d9-6fc08a38f383	file_name	Gateways.ppt	2024-02-20 10:32:23.909+00
51d499f4-2f7b-4c3a-b618-9a52c59da4c0	3727c79b-6fac-4f80-b6d9-6fc08a38f383	file_type	File	2024-02-20 10:32:23.91+00
7c21034b-0032-486a-8154-d94e9a77d7e2	3727c79b-6fac-4f80-b6d9-6fc08a38f383	file_size	446464	2024-02-20 10:32:23.914+00
32ed58c8-036c-4c05-8d96-8512e94451b5	3727c79b-6fac-4f80-b6d9-6fc08a38f383	rights_copyright	Crown Copyright	2024-02-20 10:32:23.915+00
5ed54dc5-be0e-41c2-ae6d-0c969cfadf8b	3727c79b-6fac-4f80-b6d9-6fc08a38f383	legal_status	Public Record(s)	2024-02-20 10:32:23.916+00
6b6e7dce-4c56-4c92-a793-5851972c9ea3	3727c79b-6fac-4f80-b6d9-6fc08a38f383	held_by	The National Archives, Kew	2024-02-20 10:32:23.917+00
d0623512-dfa9-4992-9272-59669a352458	3727c79b-6fac-4f80-b6d9-6fc08a38f383	date_last_modified	2022-08-03T13:47:15	2024-02-20 10:32:23.919+00
98fad566-814c-474a-b31d-79f43e77f81f	3727c79b-6fac-4f80-b6d9-6fc08a38f383	closure_type	Open	2024-02-20 10:32:23.92+00
51e90dd6-a0b2-4645-ad35-fad05941cb38	3727c79b-6fac-4f80-b6d9-6fc08a38f383	title_closed	false	2024-02-20 10:32:23.921+00
9325ef59-ee86-48a0-a337-f14f008f3e4b	3727c79b-6fac-4f80-b6d9-6fc08a38f383	description_closed	false	2024-02-20 10:32:23.922+00
15dac11d-cff6-4eb2-964a-d591ffd117e3	3727c79b-6fac-4f80-b6d9-6fc08a38f383	language	English	2024-02-20 10:32:23.924+00
2a9d1ad9-0145-4e6d-b705-07e323df1c8a	dca177e9-c1e9-485d-92ac-384eb81c9919	file_name	Workflows	2024-02-20 10:32:23.929+00
d3dc1934-e31f-46bc-88ad-7e757de8efd9	dca177e9-c1e9-485d-92ac-384eb81c9919	file_type	Folder	2024-02-20 10:32:23.93+00
170e542e-c133-49aa-9748-2f6747e94e61	dca177e9-c1e9-485d-92ac-384eb81c9919	rights_copyright	Crown Copyright	2024-02-20 10:32:23.931+00
e46e5906-640d-43c6-8cc4-72f5b326971f	dca177e9-c1e9-485d-92ac-384eb81c9919	legal_status	Public Record(s)	2024-02-20 10:32:23.933+00
98231be3-703b-4d31-b04f-0c3c4b12c3a1	dca177e9-c1e9-485d-92ac-384eb81c9919	held_by	The National Archives, Kew	2024-02-20 10:32:23.934+00
6f2d78d4-9f6a-4c8d-bbeb-7c5008be4df8	dca177e9-c1e9-485d-92ac-384eb81c9919	closure_type	Open	2024-02-20 10:32:23.938+00
9e0fe4e0-d39a-4546-a8af-d8719eb52c75	dca177e9-c1e9-485d-92ac-384eb81c9919	title_closed	false	2024-02-20 10:32:23.94+00
7998cb82-f4ea-4ccd-9889-bfec0664bcff	dca177e9-c1e9-485d-92ac-384eb81c9919	description_closed	false	2024-02-20 10:32:23.942+00
71d8e7a2-6aae-4550-84c1-210f05b489e6	dca177e9-c1e9-485d-92ac-384eb81c9919	language	English	2024-02-20 10:32:23.943+00
b6aea2c6-85ef-4406-9804-73bf69240f3a	871b2502-5521-4423-9b0d-4bc243802f96	file_name	base_de_donnees.png	2024-02-20 10:32:23.946+00
0b60d1fe-45cb-45b4-97be-1035f99ad3b0	871b2502-5521-4423-9b0d-4bc243802f96	file_type	File	2024-02-20 10:32:23.947+00
803ccd3a-cc06-454f-b584-93a0dd0da5b1	871b2502-5521-4423-9b0d-4bc243802f96	file_size	165098	2024-02-20 10:32:23.95+00
45b3a58b-22de-4e8a-bc2e-2140b4d42938	871b2502-5521-4423-9b0d-4bc243802f96	rights_copyright	Crown Copyright	2024-02-20 10:32:23.953+00
1370295f-60db-4693-b87f-9d82b004c182	871b2502-5521-4423-9b0d-4bc243802f96	legal_status	Public Record(s)	2024-02-20 10:32:23.958+00
28fc0775-2b9e-4823-904e-85b67cb53627	871b2502-5521-4423-9b0d-4bc243802f96	held_by	The National Archives, Kew	2024-02-20 10:32:23.96+00
524d4bf9-579f-4fb2-9d2d-a5b6c1f1fc0f	871b2502-5521-4423-9b0d-4bc243802f96	date_last_modified	2022-08-03T13:47:04	2024-02-20 10:32:23.961+00
ef980fa5-fd06-4f30-8aa9-0ecf6585a795	871b2502-5521-4423-9b0d-4bc243802f96	closure_type	Open	2024-02-20 10:32:23.962+00
850966a6-2aca-4494-9852-19c51886a665	871b2502-5521-4423-9b0d-4bc243802f96	title_closed	false	2024-02-20 10:32:23.964+00
1e919e2b-c231-4472-8fb0-4e1d38d2e800	871b2502-5521-4423-9b0d-4bc243802f96	description_closed	false	2024-02-20 10:32:23.965+00
4eff23f6-55c4-4d44-ad5b-656a04609ca9	871b2502-5521-4423-9b0d-4bc243802f96	language	English	2024-02-20 10:32:23.966+00
fc575a0c-c949-4343-9969-d65270a71af3	5d42f6f8-554e-4f22-882e-6a664846a532	file_name	Draft DDRO 05.docx	2024-02-20 10:32:23.971+00
bdb06f86-140c-4dc9-847e-a460c2b6ae4b	5d42f6f8-554e-4f22-882e-6a664846a532	file_type	File	2024-02-20 10:32:23.972+00
04ef914a-5d40-4627-93ef-d7775cd02289	5d42f6f8-554e-4f22-882e-6a664846a532	file_size	21707	2024-02-20 10:32:23.974+00
babcbdf3-ecbb-4ac8-b890-49015adea39b	5d42f6f8-554e-4f22-882e-6a664846a532	rights_copyright	Crown Copyright	2024-02-20 10:32:23.977+00
c06b2506-853e-4caa-9d4c-d591305f9938	5d42f6f8-554e-4f22-882e-6a664846a532	legal_status	Public Record(s)	2024-02-20 10:32:23.978+00
a994ceb9-0ffd-4c83-aa61-21e18824411d	5d42f6f8-554e-4f22-882e-6a664846a532	held_by	The National Archives, Kew	2024-02-20 10:32:23.981+00
a9692a5c-21d4-41c9-84c3-5a5bff065f89	5d42f6f8-554e-4f22-882e-6a664846a532	date_last_modified	2022-08-03T13:47:11	2024-02-20 10:32:23.985+00
6f58e86d-bfd3-45d8-ac30-e02681118c1f	5d42f6f8-554e-4f22-882e-6a664846a532	closure_type	Open	2024-02-20 10:32:23.988+00
fc8aeebd-f376-47ae-a369-f465fc49d28c	5d42f6f8-554e-4f22-882e-6a664846a532	title_closed	false	2024-02-20 10:32:23.99+00
73271617-3c92-4a9e-823c-2ff736a5ea85	5d42f6f8-554e-4f22-882e-6a664846a532	description_closed	false	2024-02-20 10:32:23.991+00
72b4b322-9358-478e-ae06-8c240c7059ac	5d42f6f8-554e-4f22-882e-6a664846a532	language	English	2024-02-20 10:32:23.993+00
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
149e5c93-acb9-438a-b3f4-08eca2b61277	e308bf4e-b6a4-49ff-a039-7c956befa75e	file_name	Remove.docx	2024-02-21 10:20:53.994+00
f1c6217d-7e4b-496a-8626-c865f12f1dc1	e308bf4e-b6a4-49ff-a039-7c956befa75e	file_type	File	2024-02-21 10:20:53.998+00
48358745-a9f1-45cb-9f6f-2a48f8ba7b50	e308bf4e-b6a4-49ff-a039-7c956befa75e	file_size	12609	2024-02-21 10:20:54.001+00
837ad898-6a0d-48ee-b38a-835c475af977	e308bf4e-b6a4-49ff-a039-7c956befa75e	rights_copyright	Crown Copyright	2024-02-21 10:20:54.004+00
7679ec29-4002-4cd3-ae5a-4b76fd5e15ae	e308bf4e-b6a4-49ff-a039-7c956befa75e	legal_status	Public Record(s)	2024-02-21 10:20:54.008+00
3bfc8d6a-e712-487a-ba22-75a7b0547a89	e308bf4e-b6a4-49ff-a039-7c956befa75e	held_by	The National Archives, Kew	2024-02-21 10:20:54.012+00
0a1550b9-1a81-4afa-96ee-6be1e25a0348	e308bf4e-b6a4-49ff-a039-7c956befa75e	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.015+00
a7cca2e7-9f06-4023-b2db-b7f25586a778	e308bf4e-b6a4-49ff-a039-7c956befa75e	closure_type	Open	2024-02-21 10:20:54.018+00
98fe2e97-f682-49a1-b888-b5aeb0fcec2b	e308bf4e-b6a4-49ff-a039-7c956befa75e	title_closed	false	2024-02-21 10:20:54.021+00
398a4a4b-c1b9-43d9-b104-745986f58c27	e308bf4e-b6a4-49ff-a039-7c956befa75e	description_closed	false	2024-02-21 10:20:54.027+00
21c5d958-bd26-4769-a750-b5aaab44118b	e308bf4e-b6a4-49ff-a039-7c956befa75e	language	English	2024-02-21 10:20:54.033+00
43543a12-72a2-4408-97a3-417ec1a6191a	c657f264-8a4c-475e-a121-4adb2bc7766c	file_name	Workflows	2024-02-21 10:20:54.046+00
3afcb810-48a5-4663-93cd-acf91f14e716	c657f264-8a4c-475e-a121-4adb2bc7766c	file_type	Folder	2024-02-21 10:20:54.05+00
aaefde81-147d-441e-93b7-e8a7e1cca856	c657f264-8a4c-475e-a121-4adb2bc7766c	rights_copyright	Crown Copyright	2024-02-21 10:20:54.053+00
35e74eac-986b-44a0-8765-4194ab7a3157	c657f264-8a4c-475e-a121-4adb2bc7766c	legal_status	Public Record(s)	2024-02-21 10:20:54.056+00
586c588c-dd83-4888-8fc1-68124689df86	c657f264-8a4c-475e-a121-4adb2bc7766c	held_by	The National Archives, Kew	2024-02-21 10:20:54.059+00
bc59d9af-6318-4178-af9b-4e13ee5c9fa8	c657f264-8a4c-475e-a121-4adb2bc7766c	closure_type	Open	2024-02-21 10:20:54.061+00
99fb31ae-36f5-4a7c-b14d-76b4c554b683	c657f264-8a4c-475e-a121-4adb2bc7766c	title_closed	false	2024-02-21 10:20:54.064+00
88172c54-2c20-4018-b6b6-7adc884fce55	c657f264-8a4c-475e-a121-4adb2bc7766c	description_closed	false	2024-02-21 10:20:54.071+00
2b3bf610-ae24-46b2-987b-e31885796655	c657f264-8a4c-475e-a121-4adb2bc7766c	language	English	2024-02-21 10:20:54.08+00
a4d522b6-e611-4f84-99ab-8a27032f4908	1ac109a8-c542-4030-8826-c8d614b1943e	file_name	Draft DDRO 05.docx	2024-02-21 10:20:54.088+00
bb18b700-1ebf-4fa2-a145-ff4a985b534d	1ac109a8-c542-4030-8826-c8d614b1943e	file_type	File	2024-02-21 10:20:54.092+00
00364291-f005-4307-a346-997003f4ff69	1ac109a8-c542-4030-8826-c8d614b1943e	file_size	21707	2024-02-21 10:20:54.095+00
ab24c303-a3fb-44f2-a7e8-02d019dc0699	1ac109a8-c542-4030-8826-c8d614b1943e	rights_copyright	Crown Copyright	2024-02-21 10:20:54.098+00
67c7632d-5508-4486-b311-19d7e6c41a9d	1ac109a8-c542-4030-8826-c8d614b1943e	legal_status	Public Record(s)	2024-02-21 10:20:54.101+00
2549514d-b3a0-45a3-8e65-c5c464b61472	1ac109a8-c542-4030-8826-c8d614b1943e	held_by	The National Archives, Kew	2024-02-21 10:20:54.103+00
68e63c9f-c906-4e25-aa75-7b0ef189064a	1ac109a8-c542-4030-8826-c8d614b1943e	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.106+00
b260ddb1-3eaf-40e1-bbe6-0aca9415ceca	1ac109a8-c542-4030-8826-c8d614b1943e	closure_type	Open	2024-02-21 10:20:54.116+00
74e1d2ac-d912-4659-bcd6-d614aea337d3	1ac109a8-c542-4030-8826-c8d614b1943e	title_closed	false	2024-02-21 10:20:54.118+00
999f2783-0ef9-40f0-83a4-43687b14259a	1ac109a8-c542-4030-8826-c8d614b1943e	description_closed	false	2024-02-21 10:20:54.121+00
f8d25a5e-d275-41c7-8a78-593fc5f73809	1ac109a8-c542-4030-8826-c8d614b1943e	language	English	2024-02-21 10:20:54.125+00
e94020a8-e204-41d8-9b9c-b808ab079093	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	file_name	delivery-form-digital.doc	2024-02-21 10:20:54.138+00
9f171f63-171e-41f0-a070-658531cbe212	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	file_type	File	2024-02-21 10:20:54.141+00
355d1f3f-205a-408d-988a-1a76a80509e2	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	file_size	139776	2024-02-21 10:20:54.143+00
8b8c84d5-e9b8-4704-8c60-45d4f448de62	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	rights_copyright	Crown Copyright	2024-02-21 10:20:54.146+00
1a3cb2f8-5a52-425a-8480-cf66cc6d89cf	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	legal_status	Public Record(s)	2024-02-21 10:20:54.148+00
c8beb4c8-da25-46e3-80cf-550b20b4db47	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	held_by	The National Archives, Kew	2024-02-21 10:20:54.151+00
f31d3ba3-c81c-44d7-8ceb-f7cbeb50859f	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.153+00
1ee7a7e5-e7ba-44ee-b509-a32280ea767d	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	closure_type	Open	2024-02-21 10:20:54.156+00
383e2133-e3c7-4f5a-8594-8695f34d44dc	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	title_closed	false	2024-02-21 10:20:54.158+00
dbc2f181-4e96-433c-b82a-0929d283c849	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	description_closed	false	2024-02-21 10:20:54.161+00
8273bee2-ae01-4efb-9ded-d6a8fc81fb3a	6d6fd827-7fdc-49d9-9cf4-a82ec1109941	language	English	2024-02-21 10:20:54.163+00
2833b324-56d2-4211-90b2-411739cb493c	97243031-46b9-42fe-a107-79a4031d0998	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-21 10:20:54.174+00
d9415d33-cd73-4532-91d5-b67ddeef8fe6	97243031-46b9-42fe-a107-79a4031d0998	file_type	File	2024-02-21 10:20:54.176+00
2a320af7-1544-4f43-babc-35baa0d419be	97243031-46b9-42fe-a107-79a4031d0998	file_size	68364	2024-02-21 10:20:54.179+00
5e150ad7-f8e4-483a-914c-245dde71054b	97243031-46b9-42fe-a107-79a4031d0998	rights_copyright	Crown Copyright	2024-02-21 10:20:54.181+00
a81c604f-2dc3-43a6-910e-c51c628e710c	97243031-46b9-42fe-a107-79a4031d0998	legal_status	Public Record(s)	2024-02-21 10:20:54.185+00
a146d410-6396-4c1c-bfed-e720adfc3e53	97243031-46b9-42fe-a107-79a4031d0998	held_by	The National Archives, Kew	2024-02-21 10:20:54.188+00
5c407b83-a159-4d47-992e-1b6530418a42	97243031-46b9-42fe-a107-79a4031d0998	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.19+00
a021f870-f9af-4248-9846-297b63dd54bd	97243031-46b9-42fe-a107-79a4031d0998	closure_type	Open	2024-02-21 10:20:54.197+00
e6a02861-6d29-46f7-8745-5f9923fbb602	97243031-46b9-42fe-a107-79a4031d0998	title_closed	false	2024-02-21 10:20:54.201+00
857a1acb-ce28-4612-b5dc-10279e7e14a4	97243031-46b9-42fe-a107-79a4031d0998	description_closed	false	2024-02-21 10:20:54.208+00
0f8ac46e-f844-4a7c-8c75-f83b37042bbf	97243031-46b9-42fe-a107-79a4031d0998	language	English	2024-02-21 10:20:54.212+00
6deb575f-8891-4cdd-98bc-fc4da8b6ce60	ca63b581-4523-4fde-9009-eade85f2677a	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-21 10:20:54.228+00
4831d524-1740-40d2-838d-7f7fcdacc0e1	ca63b581-4523-4fde-9009-eade85f2677a	file_type	File	2024-02-21 10:20:54.233+00
54b19d73-2459-44c4-a4f2-03de62a2d69d	ca63b581-4523-4fde-9009-eade85f2677a	file_size	70263	2024-02-21 10:20:54.239+00
cf145176-e57d-4f47-837c-a1251fb229f1	ca63b581-4523-4fde-9009-eade85f2677a	rights_copyright	Crown Copyright	2024-02-21 10:20:54.244+00
35fdbb8d-27c7-4def-937b-b36e3390f840	ca63b581-4523-4fde-9009-eade85f2677a	legal_status	Public Record(s)	2024-02-21 10:20:54.247+00
b0cd3a8c-349e-43b8-bae9-75019391f261	ca63b581-4523-4fde-9009-eade85f2677a	held_by	The National Archives, Kew	2024-02-21 10:20:54.254+00
f76dba97-5c66-445d-93bf-6185b02a7451	ca63b581-4523-4fde-9009-eade85f2677a	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.259+00
7f7b6600-031e-403b-834e-269e358e94d3	ca63b581-4523-4fde-9009-eade85f2677a	closure_type	Open	2024-02-21 10:20:54.263+00
a13d3eb8-e16b-453e-8208-6307712d6a0d	ca63b581-4523-4fde-9009-eade85f2677a	title_closed	false	2024-02-21 10:20:54.267+00
ede1a758-30a1-40e3-af5a-a31b1045aa6a	ca63b581-4523-4fde-9009-eade85f2677a	description_closed	false	2024-02-21 10:20:54.272+00
4a38e0e3-5231-47a4-899a-24a2b9b40285	ca63b581-4523-4fde-9009-eade85f2677a	language	English	2024-02-21 10:20:54.276+00
14e3d6b6-bf86-4659-b60f-e21739c3f1f7	ecb51977-bfe6-4507-871e-e6844b35caac	file_name	Emergency Response Team	2024-02-21 10:20:54.305+00
fc940925-30dc-4113-9001-1fc1d42602ec	ecb51977-bfe6-4507-871e-e6844b35caac	file_type	Folder	2024-02-21 10:20:54.311+00
64c7a89b-54a3-45e0-a853-8a36f959bc0d	ecb51977-bfe6-4507-871e-e6844b35caac	rights_copyright	Crown Copyright	2024-02-21 10:20:54.315+00
4663805b-214f-4502-8449-ca2340d8db86	ecb51977-bfe6-4507-871e-e6844b35caac	legal_status	Public Record(s)	2024-02-21 10:20:54.318+00
30583487-aeec-4fce-bbfe-4449164ae003	ecb51977-bfe6-4507-871e-e6844b35caac	held_by	The National Archives, Kew	2024-02-21 10:20:54.321+00
1f7b0996-da5a-4669-a013-f83b0f2fc353	ecb51977-bfe6-4507-871e-e6844b35caac	closure_type	Open	2024-02-21 10:20:54.325+00
84110fe3-f0c2-494f-a1b7-d526a0200ced	ecb51977-bfe6-4507-871e-e6844b35caac	title_closed	false	2024-02-21 10:20:54.327+00
968ec071-144a-4c2c-bd2e-883bded08e3b	ecb51977-bfe6-4507-871e-e6844b35caac	description_closed	false	2024-02-21 10:20:54.33+00
d2044b33-e325-4de7-83ad-28f4e8feca0e	ecb51977-bfe6-4507-871e-e6844b35caac	language	English	2024-02-21 10:20:54.333+00
03bcacfd-9f45-4b56-9483-219e69e69f1a	c3e894db-bff4-4e35-9d84-ab6a46800b5e	file_name	Thumbs.db	2024-02-21 10:20:54.338+00
2eb83658-4023-4146-bd70-5b9bbc3d2402	c3e894db-bff4-4e35-9d84-ab6a46800b5e	file_type	File	2024-02-21 10:20:54.341+00
75bed96e-7545-4ea6-a12a-a5ae804b3915	c3e894db-bff4-4e35-9d84-ab6a46800b5e	file_size	685124	2024-02-21 10:20:54.343+00
4e9ee818-6d6a-4fe7-80b9-6e26c4daf6bd	c3e894db-bff4-4e35-9d84-ab6a46800b5e	rights_copyright	Crown Copyright	2024-02-21 10:20:54.345+00
fc78969c-f4d2-42d5-968d-f677c2adf0be	c3e894db-bff4-4e35-9d84-ab6a46800b5e	legal_status	Public Record(s)	2024-02-21 10:20:54.347+00
da96fa17-c5dd-40d5-b3a6-1e0b8e17210c	c3e894db-bff4-4e35-9d84-ab6a46800b5e	held_by	The National Archives, Kew	2024-02-21 10:20:54.35+00
53a4cc10-bf1b-45a8-8e86-a0a79901be98	c3e894db-bff4-4e35-9d84-ab6a46800b5e	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.352+00
a5ca7f92-0d4b-4297-a15a-d9851cf4d5e1	c3e894db-bff4-4e35-9d84-ab6a46800b5e	closure_type	Open	2024-02-21 10:20:54.354+00
ef63ea5f-f12e-44ff-af3c-22c3aa79e5b1	c3e894db-bff4-4e35-9d84-ab6a46800b5e	title_closed	false	2024-02-21 10:20:54.356+00
d80870a5-7346-44b5-9820-048e84660291	c3e894db-bff4-4e35-9d84-ab6a46800b5e	description_closed	false	2024-02-21 10:20:54.365+00
cd9ad918-743b-4a28-aa38-ca61e848d547	c3e894db-bff4-4e35-9d84-ab6a46800b5e	language	English	2024-02-21 10:20:54.367+00
6393f28c-2dca-487d-880d-b348cdeb8284	bdf293f4-22ab-49ea-8a4f-4c313170915d	file_name	base_de_donnees.png	2024-02-21 10:20:54.378+00
1213774b-eed6-4400-a482-473180d9a943	bdf293f4-22ab-49ea-8a4f-4c313170915d	file_type	File	2024-02-21 10:20:54.381+00
fbd36193-6cb1-474a-a459-d684184a94e4	bdf293f4-22ab-49ea-8a4f-4c313170915d	file_size	165098	2024-02-21 10:20:54.383+00
b6dbc4ec-b4ff-4be5-9f14-5417010d99f8	bdf293f4-22ab-49ea-8a4f-4c313170915d	rights_copyright	Crown Copyright	2024-02-21 10:20:54.386+00
6b0b849b-e691-4479-9105-4a84ce7837b4	bdf293f4-22ab-49ea-8a4f-4c313170915d	legal_status	Public Record(s)	2024-02-21 10:20:54.388+00
6d4ac715-f304-4caf-afcd-83d58810a622	bdf293f4-22ab-49ea-8a4f-4c313170915d	held_by	The National Archives, Kew	2024-02-21 10:20:54.392+00
9129bc5d-13ec-4157-bff0-fc6699c24e53	bdf293f4-22ab-49ea-8a4f-4c313170915d	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.395+00
10a08139-3455-4c3c-9b71-e75ebd43a72d	bdf293f4-22ab-49ea-8a4f-4c313170915d	closure_type	Open	2024-02-21 10:20:54.397+00
2814919e-9d23-4179-a91f-8f6b7e7c414b	bdf293f4-22ab-49ea-8a4f-4c313170915d	title_closed	false	2024-02-21 10:20:54.4+00
e81c7d4e-11ac-4b98-9c30-f9479f21807d	bdf293f4-22ab-49ea-8a4f-4c313170915d	description_closed	false	2024-02-21 10:20:54.402+00
4e904d04-bd8b-4da0-9f84-4449c187cc6e	bdf293f4-22ab-49ea-8a4f-4c313170915d	language	English	2024-02-21 10:20:54.405+00
b0aff9f6-6f62-4bb1-b9a1-ff71b06eac1a	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	file_name	Presentation.pptx	2024-02-21 10:20:54.417+00
28b2efd0-4959-4f7a-8a8b-5c71a74b24d6	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	file_type	File	2024-02-21 10:20:54.419+00
53ca5b0b-4383-4e13-9b59-cbd067a31b8f	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	file_size	697817	2024-02-21 10:20:54.422+00
8164b7a4-008d-4da8-8ad6-639bd6bfa67d	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	rights_copyright	Crown Copyright	2024-02-21 10:20:54.425+00
ba8e3e29-7282-4e5b-9fa6-7f04219cceb4	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	legal_status	Public Record(s)	2024-02-21 10:20:54.427+00
91e9f8af-886a-4476-9cff-1b4d69a60121	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	held_by	The National Archives, Kew	2024-02-21 10:20:54.429+00
05576d1d-8cde-40a0-90aa-cc9976d68de9	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.431+00
eee6edae-cede-44e6-9f0d-b201d7489608	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	closure_type	Open	2024-02-21 10:20:54.434+00
d3fcbf5b-7d7c-4afc-b60b-fbf458e47aaf	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	title_closed	false	2024-02-21 10:20:54.436+00
0fd21c06-4e96-4a04-85a6-38bf47f1d903	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	description_closed	false	2024-02-21 10:20:54.439+00
99057d5a-aa03-46ea-b301-75a10e5ed61e	1fca1fc2-fcb3-447b-8418-f6e4a5728efe	language	English	2024-02-21 10:20:54.441+00
f3721cdb-acb1-4765-8dd5-63ccfebc39a6	9595f34d-9c81-4cdc-b57b-af76815d904d	file_name	Response Policy.docx	2024-02-21 10:20:54.45+00
7e90dd5f-2dcd-4948-b389-8d85fa702cb4	9595f34d-9c81-4cdc-b57b-af76815d904d	file_type	File	2024-02-21 10:20:54.454+00
a0245e82-6ce5-45a1-ba7a-bb129f31d2b1	9595f34d-9c81-4cdc-b57b-af76815d904d	file_size	12651	2024-02-21 10:20:54.456+00
71d0e76d-2f2a-4128-ace5-85e72855901b	9595f34d-9c81-4cdc-b57b-af76815d904d	rights_copyright	Crown Copyright	2024-02-21 10:20:54.459+00
90c1c2e8-d1c9-422e-b57a-722b63d97146	9595f34d-9c81-4cdc-b57b-af76815d904d	legal_status	Public Record(s)	2024-02-21 10:20:54.462+00
9eebc2f2-ad22-4da6-b9f7-1fa85ec724b2	9595f34d-9c81-4cdc-b57b-af76815d904d	held_by	The National Archives, Kew	2024-02-21 10:20:54.464+00
71006e01-1beb-448d-8b44-ef22882beed5	9595f34d-9c81-4cdc-b57b-af76815d904d	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.466+00
ccbcedab-4e4a-4c65-9acb-111280362353	9595f34d-9c81-4cdc-b57b-af76815d904d	closure_type	Open	2024-02-21 10:20:54.468+00
276f4534-5c26-488f-a859-10a2c610a914	9595f34d-9c81-4cdc-b57b-af76815d904d	title_closed	false	2024-02-21 10:20:54.471+00
df6d6576-5d53-46d5-9cbd-b5d21907521f	9595f34d-9c81-4cdc-b57b-af76815d904d	description_closed	false	2024-02-21 10:20:54.473+00
18ac49dc-57dc-4b0f-83ad-bdea69173ae4	9595f34d-9c81-4cdc-b57b-af76815d904d	language	English	2024-02-21 10:20:54.475+00
64522045-8432-4219-9c4e-faabfb88d692	769f8459-c5db-42a8-a01b-62a216c390ed	file_name	DTP_ Sensitivity review process.docx	2024-02-21 10:20:54.485+00
d7847dca-ebff-49e7-8e43-aabff7d69e47	769f8459-c5db-42a8-a01b-62a216c390ed	file_type	File	2024-02-21 10:20:54.488+00
9f2b17b8-8d38-420d-97eb-db7a8a694733	769f8459-c5db-42a8-a01b-62a216c390ed	file_size	70674	2024-02-21 10:20:54.491+00
c8c9bb62-24e5-4478-85e6-13c220d71778	769f8459-c5db-42a8-a01b-62a216c390ed	rights_copyright	Crown Copyright	2024-02-21 10:20:54.493+00
194bf5ad-8085-4c73-acff-3f36c0aab662	769f8459-c5db-42a8-a01b-62a216c390ed	legal_status	Public Record(s)	2024-02-21 10:20:54.495+00
e298e9a4-4f9f-4428-8389-8cb08d60db70	769f8459-c5db-42a8-a01b-62a216c390ed	held_by	The National Archives, Kew	2024-02-21 10:20:54.503+00
64e56a99-d171-47fc-8215-db5bd6c7930e	769f8459-c5db-42a8-a01b-62a216c390ed	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.506+00
3c98f805-1b3a-4dba-b529-c099d5e8e2be	769f8459-c5db-42a8-a01b-62a216c390ed	closure_type	Open	2024-02-21 10:20:54.508+00
012ad429-e2d2-48a7-9a65-f75e109677b7	769f8459-c5db-42a8-a01b-62a216c390ed	title_closed	false	2024-02-21 10:20:54.51+00
53cd4170-4c3f-4b2e-9d5d-bdba2b22a134	769f8459-c5db-42a8-a01b-62a216c390ed	description_closed	false	2024-02-21 10:20:54.513+00
7a440c74-8299-4d4a-ae5e-bc82fcba9b1b	769f8459-c5db-42a8-a01b-62a216c390ed	language	English	2024-02-21 10:20:54.515+00
517e2438-8e78-4b5b-8055-34e890d7b27b	4f5b8b4c-30f9-4efc-a159-fa987b1db093	file_name	nord-lead-viewer.mxf	2024-02-21 10:20:54.525+00
ea8a6617-030f-4a32-89a3-6e367a535443	4f5b8b4c-30f9-4efc-a159-fa987b1db093	file_type	File	2024-02-21 10:20:54.528+00
44cd84a6-c9b4-47db-932c-7bd85d162793	4f5b8b4c-30f9-4efc-a159-fa987b1db093	file_size	1179295	2024-02-21 10:20:54.531+00
868e0a60-4d83-4aef-bc0a-ce7ac6fd367d	4f5b8b4c-30f9-4efc-a159-fa987b1db093	rights_copyright	Crown Copyright	2024-02-21 10:20:54.534+00
9f6428d5-7404-47ee-812b-a98337bea7c7	4f5b8b4c-30f9-4efc-a159-fa987b1db093	legal_status	Public Record(s)	2024-02-21 10:20:54.537+00
80e980fc-10ec-4bb8-9a53-2f8057644e4c	4f5b8b4c-30f9-4efc-a159-fa987b1db093	held_by	The National Archives, Kew	2024-02-21 10:20:54.539+00
0547eab8-cb6a-4000-b6de-52394fb602fa	4f5b8b4c-30f9-4efc-a159-fa987b1db093	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.542+00
c5d64450-01b9-4c41-b07e-f41f79378be8	4f5b8b4c-30f9-4efc-a159-fa987b1db093	closure_type	Open	2024-02-21 10:20:54.544+00
008771c6-733e-47a2-acaf-0d31b5e4a935	4f5b8b4c-30f9-4efc-a159-fa987b1db093	title_closed	false	2024-02-21 10:20:54.546+00
4c104b6a-cc7a-4da9-b83f-be171ae459d5	4f5b8b4c-30f9-4efc-a159-fa987b1db093	description_closed	false	2024-02-21 10:20:54.548+00
54a6d73d-c962-423e-a973-3e8244e16836	4f5b8b4c-30f9-4efc-a159-fa987b1db093	language	English	2024-02-21 10:20:54.55+00
e03efabc-6c2b-4f37-b282-57cfb6a65815	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	file_name	Response Procedure.docx	2024-02-21 10:20:54.56+00
5caa581f-ecbf-4dca-b65b-1300580f0a3e	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	file_type	File	2024-02-21 10:20:54.562+00
4779a789-6c29-42d4-bccf-44b1c3e2496b	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	file_size	12610	2024-02-21 10:20:54.564+00
d1677862-f4e1-4663-b5b3-a845c80ebe8f	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	rights_copyright	Crown Copyright	2024-02-21 10:20:54.566+00
a890c1c8-1adc-4418-94e2-90f9ec7aaeaa	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	legal_status	Public Record(s)	2024-02-21 10:20:54.568+00
6dc7618e-1180-49f6-b91a-a8a13f3bbe00	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	held_by	The National Archives, Kew	2024-02-21 10:20:54.571+00
0910b03d-d33d-4fcd-b361-89d1e7edc074	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.573+00
40d37d99-a89c-4a28-a72a-511fd4478923	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	closure_type	Open	2024-02-21 10:20:54.576+00
cf1ccac7-705a-4231-98ec-78fd096cffb3	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	title_closed	false	2024-02-21 10:20:54.578+00
7d3cc75c-d1ad-46ab-937b-a2e80f6e17d7	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	description_closed	false	2024-02-21 10:20:54.58+00
85a5bd92-2c0b-470a-829a-3dccb72a8a98	bddcb515-81b7-4fb9-8c10-ee3b6645cd5f	language	English	2024-02-21 10:20:54.582+00
c54107ea-c1ae-4efb-a09f-7d93ee753c98	761e50f5-8441-4e55-884e-26eaf8e12abe	file_name	Emergency Contact Details Paul Young.docx	2024-02-21 10:20:54.594+00
77c36fff-2a27-403b-b7b6-fc4e7b6ec199	761e50f5-8441-4e55-884e-26eaf8e12abe	file_type	File	2024-02-21 10:20:54.596+00
89e8783a-b337-4ab6-b35f-2476dab30285	761e50f5-8441-4e55-884e-26eaf8e12abe	file_size	12825	2024-02-21 10:20:54.603+00
210029ac-13bf-4a7e-83db-95c5de49ad03	761e50f5-8441-4e55-884e-26eaf8e12abe	rights_copyright	Crown Copyright	2024-02-21 10:20:54.606+00
ed86b9b4-9d79-4cc3-9b19-2749a6b1c898	761e50f5-8441-4e55-884e-26eaf8e12abe	legal_status	Public Record(s)	2024-02-21 10:20:54.608+00
b3776e58-c4f0-4ef9-982d-9ac067799205	761e50f5-8441-4e55-884e-26eaf8e12abe	held_by	The National Archives, Kew	2024-02-21 10:20:54.611+00
1a088fdb-27a5-46a8-ac05-ff3166db9a72	761e50f5-8441-4e55-884e-26eaf8e12abe	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.613+00
5bd7b4b1-85c4-48b1-8b64-edce644fc7ed	761e50f5-8441-4e55-884e-26eaf8e12abe	closure_type	Open	2024-02-21 10:20:54.615+00
7c95db88-be61-4f6c-93c9-7d61bc44a20f	761e50f5-8441-4e55-884e-26eaf8e12abe	title_closed	false	2024-02-21 10:20:54.618+00
f03650ff-8c27-492d-b92b-c9c373561fe5	761e50f5-8441-4e55-884e-26eaf8e12abe	description_closed	false	2024-02-21 10:20:54.62+00
b95324dc-8357-428a-a08a-fdba988357a6	761e50f5-8441-4e55-884e-26eaf8e12abe	language	English	2024-02-21 10:20:54.622+00
aee47a5e-419b-4302-973b-0a469562b5ca	9bf0a29a-863a-4b34-9553-1592981e876c	file_name	content	2024-02-21 10:20:54.632+00
e5210787-cdb1-4964-9ea7-fd64a2d280ea	9bf0a29a-863a-4b34-9553-1592981e876c	file_type	Folder	2024-02-21 10:20:54.634+00
9ab6e692-22b1-4492-ae05-3297525ea96d	9bf0a29a-863a-4b34-9553-1592981e876c	rights_copyright	Crown Copyright	2024-02-21 10:20:54.636+00
a0a98f26-d841-4654-840c-f4b21eea8dff	9bf0a29a-863a-4b34-9553-1592981e876c	legal_status	Public Record(s)	2024-02-21 10:20:54.639+00
c9ecaab3-a84b-4057-a424-31690cbd464f	9bf0a29a-863a-4b34-9553-1592981e876c	held_by	The National Archives, Kew	2024-02-21 10:20:54.641+00
501e5550-63c9-4ee8-ada5-8486084fc78d	9bf0a29a-863a-4b34-9553-1592981e876c	closure_type	Open	2024-02-21 10:20:54.644+00
d75016ba-ce65-40b4-b2b2-453cc0ffe434	9bf0a29a-863a-4b34-9553-1592981e876c	title_closed	false	2024-02-21 10:20:54.646+00
e8399a7f-1548-4345-bedd-5ec2e46f6bfb	9bf0a29a-863a-4b34-9553-1592981e876c	description_closed	false	2024-02-21 10:20:54.648+00
f82801ad-6065-4873-a657-d41616a26849	9bf0a29a-863a-4b34-9553-1592981e876c	language	English	2024-02-21 10:20:54.651+00
886a2689-9ecf-48fc-bb3b-ba3e82f4cbe1	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	file_name	Gateways.ppt	2024-02-21 10:20:54.656+00
028087a5-dbbc-4062-879c-c2dc971e7aec	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	file_type	File	2024-02-21 10:20:54.658+00
69b47083-3b10-4432-8cac-a2e9eadbe9ae	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	file_size	446464	2024-02-21 10:20:54.66+00
de766ed0-f28d-4a34-87b1-58c9e2d3b10e	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	rights_copyright	Crown Copyright	2024-02-21 10:20:54.663+00
dc16245c-de19-43d1-889b-7f71e48fe639	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	legal_status	Public Record(s)	2024-02-21 10:20:54.666+00
307b9896-ebb5-4075-8959-4b49763185fd	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	held_by	The National Archives, Kew	2024-02-21 10:20:54.671+00
a2bedd0c-e7bc-459a-8fcb-0160fc643d08	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.676+00
723f6bc8-96ef-4e5e-a4de-f1edbaa13266	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	closure_type	Open	2024-02-21 10:20:54.679+00
23ac1be6-9dba-48f7-898a-f9b52aae5509	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	title_closed	false	2024-02-21 10:20:54.682+00
bbf398b4-dc60-4c8c-be5a-19755f946667	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	description_closed	false	2024-02-21 10:20:54.684+00
f5a25132-9092-48a4-b06f-ca7290c05954	ee902d90-3ba6-4be5-bc0a-aa6ff3cee57b	language	English	2024-02-21 10:20:54.687+00
13280da6-a0b0-4cd5-adf0-31cb74308d35	e20dd7a5-ec42-4d62-86ee-a71f875035a2	file_name	DTP.docx	2024-02-21 10:20:54.697+00
8f5bc1f0-69eb-49e1-8c37-287c2647d90f	e20dd7a5-ec42-4d62-86ee-a71f875035a2	file_type	File	2024-02-21 10:20:54.702+00
20c08de9-1959-43dc-876d-e9226e0ea7ef	e20dd7a5-ec42-4d62-86ee-a71f875035a2	file_size	70263	2024-02-21 10:20:54.706+00
fe0d178b-daf0-4156-9726-b1b4e44bf919	e20dd7a5-ec42-4d62-86ee-a71f875035a2	rights_copyright	Crown Copyright	2024-02-21 10:20:54.708+00
21de5ed5-df4c-495e-824c-2d5654a5dcc6	e20dd7a5-ec42-4d62-86ee-a71f875035a2	legal_status	Public Record(s)	2024-02-21 10:20:54.711+00
937cb4f7-43eb-4652-8c92-5af7e920933b	e20dd7a5-ec42-4d62-86ee-a71f875035a2	held_by	The National Archives, Kew	2024-02-21 10:20:54.713+00
937853eb-020b-4d85-bfcb-1cd1873f9889	e20dd7a5-ec42-4d62-86ee-a71f875035a2	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.715+00
3e826a1c-967f-43b4-8146-9c1363e0cf1e	e20dd7a5-ec42-4d62-86ee-a71f875035a2	closure_type	Open	2024-02-21 10:20:54.717+00
aba01346-e8d6-4c35-890b-b20102e0fb03	e20dd7a5-ec42-4d62-86ee-a71f875035a2	title_closed	false	2024-02-21 10:20:54.72+00
b501ff3e-70b1-42f9-b732-2687819e38e1	e20dd7a5-ec42-4d62-86ee-a71f875035a2	description_closed	false	2024-02-21 10:20:54.722+00
0bb381eb-b991-4469-a813-f6781e1bb796	e20dd7a5-ec42-4d62-86ee-a71f875035a2	language	English	2024-02-21 10:20:54.724+00
f1447ad7-1732-4155-aaf3-506ebd1f5a55	41f94132-dbdf-43e4-a327-cc5bae432f98	file_name	Digital Transfer training email .msg	2024-02-21 10:20:54.733+00
92b09169-b2fd-4247-affe-f7fe95e83d25	41f94132-dbdf-43e4-a327-cc5bae432f98	file_type	File	2024-02-21 10:20:54.736+00
cc1617a2-4301-4b87-ba2d-70c36b8110d0	41f94132-dbdf-43e4-a327-cc5bae432f98	file_size	39424	2024-02-21 10:20:54.738+00
8003cf2e-4dfe-4e2b-b4e3-5e5566f4246d	41f94132-dbdf-43e4-a327-cc5bae432f98	rights_copyright	Crown Copyright	2024-02-21 10:20:54.74+00
3517a566-8159-46d5-a741-4b99976b5ff5	41f94132-dbdf-43e4-a327-cc5bae432f98	legal_status	Public Record(s)	2024-02-21 10:20:54.742+00
97d60036-8c3a-4951-9ea4-c11db8443b98	41f94132-dbdf-43e4-a327-cc5bae432f98	held_by	The National Archives, Kew	2024-02-21 10:20:54.745+00
5591bdd1-14f1-46d6-a005-88efd9c2f498	41f94132-dbdf-43e4-a327-cc5bae432f98	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.747+00
981d9684-b5c5-47c0-a15b-2bdf96d7741c	41f94132-dbdf-43e4-a327-cc5bae432f98	closure_type	Open	2024-02-21 10:20:54.749+00
e344ff97-5ed3-4377-b018-e08956e3f92f	41f94132-dbdf-43e4-a327-cc5bae432f98	title_closed	false	2024-02-21 10:20:54.753+00
a25629c3-6331-4e78-a080-5e7ca1f3c840	41f94132-dbdf-43e4-a327-cc5bae432f98	description_closed	false	2024-02-21 10:20:54.755+00
b7039964-da60-4caf-a8dc-6d7b9e40510b	41f94132-dbdf-43e4-a327-cc5bae432f98	language	English	2024-02-21 10:20:54.757+00
04cd3c17-0bd9-4860-b3ab-8a0291f5cd62	839fce83-82f6-462f-a186-50a27fed68e0	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-21 10:20:54.768+00
3abd6be8-ec72-433d-8381-4edd890bd134	839fce83-82f6-462f-a186-50a27fed68e0	file_type	File	2024-02-21 10:20:54.77+00
413b233d-5652-480e-b9b5-0e18c79bb967	839fce83-82f6-462f-a186-50a27fed68e0	file_size	177875	2024-02-21 10:20:54.773+00
87ed2c61-6e78-4923-aec2-6b72768432c7	839fce83-82f6-462f-a186-50a27fed68e0	rights_copyright	Crown Copyright	2024-02-21 10:20:54.775+00
d1fd286d-e93e-48a1-8d1c-fed9be3b70fb	839fce83-82f6-462f-a186-50a27fed68e0	legal_status	Public Record(s)	2024-02-21 10:20:54.777+00
899e471c-8282-4cf7-8a10-e28a850fc318	839fce83-82f6-462f-a186-50a27fed68e0	held_by	The National Archives, Kew	2024-02-21 10:20:54.78+00
0a2efec4-c9e9-4e8e-a0ac-efa68af15d67	839fce83-82f6-462f-a186-50a27fed68e0	date_last_modified	2022-07-18T00:00:00	2024-02-21 10:20:54.782+00
362df962-38dc-406f-b969-397b3575addb	839fce83-82f6-462f-a186-50a27fed68e0	closure_type	Open	2024-02-21 10:20:54.784+00
655f68d8-896b-4b89-885b-0ac24e53f364	839fce83-82f6-462f-a186-50a27fed68e0	title_closed	false	2024-02-21 10:20:54.787+00
aef2ec03-71a5-494e-8f9c-561df84de5ff	839fce83-82f6-462f-a186-50a27fed68e0	description_closed	false	2024-02-21 10:20:54.789+00
bae242bc-4c1e-4682-911d-36e4f7833db9	839fce83-82f6-462f-a186-50a27fed68e0	language	English	2024-02-21 10:20:54.791+00
889b7faf-468e-49b4-bdab-5cff94c46b48	d38f9713-7361-4713-b93a-64aa6beafc1b	file_name	delivery-form-digital.doc	2024-02-22 09:26:27.304+00
797d69c6-1150-4a94-a21a-ffece35a636e	d38f9713-7361-4713-b93a-64aa6beafc1b	file_type	File	2024-02-22 09:26:27.307+00
d71851a7-aa55-4c1b-83ba-750cac48ee47	d38f9713-7361-4713-b93a-64aa6beafc1b	file_size	139776	2024-02-22 09:26:27.309+00
3c58ee55-f525-4cb3-8c86-6988f23a0fd5	d38f9713-7361-4713-b93a-64aa6beafc1b	rights_copyright	Crown Copyright	2024-02-22 09:26:27.31+00
302c8a98-04cb-435d-94c7-b5c23e1c469a	d38f9713-7361-4713-b93a-64aa6beafc1b	legal_status	Public Record(s)	2024-02-22 09:26:27.313+00
49b3a970-0946-474c-8222-a3e1cd32f1b8	d38f9713-7361-4713-b93a-64aa6beafc1b	held_by	The National Archives, Kew	2024-02-22 09:26:27.315+00
06b48bf6-6533-42e8-a140-8ceaca6faab2	d38f9713-7361-4713-b93a-64aa6beafc1b	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.319+00
e63805e7-fe80-46a5-8a87-cfc3701ede4c	d38f9713-7361-4713-b93a-64aa6beafc1b	closure_type	Open	2024-02-22 09:26:27.32+00
1f060300-578e-4035-88b1-f5b67bcba1b9	d38f9713-7361-4713-b93a-64aa6beafc1b	title_closed	false	2024-02-22 09:26:27.322+00
a3594b14-b6fc-4231-a14e-cfd98321896d	d38f9713-7361-4713-b93a-64aa6beafc1b	description_closed	false	2024-02-22 09:26:27.323+00
b2e4c44d-c13b-4099-a8d0-aced210cff88	d38f9713-7361-4713-b93a-64aa6beafc1b	language	English	2024-02-22 09:26:27.324+00
d408bd46-97e1-483b-811b-e61f4b6f255e	a3086873-0df1-457e-9818-8f13f5796d26	file_name	Workflows	2024-02-22 09:26:27.335+00
257819c1-3d18-4a8d-9a3e-b6c81a4f13fc	a3086873-0df1-457e-9818-8f13f5796d26	file_type	Folder	2024-02-22 09:26:27.337+00
aff9a69f-025c-444c-aa52-b76dd9a6e528	a3086873-0df1-457e-9818-8f13f5796d26	rights_copyright	Crown Copyright	2024-02-22 09:26:27.341+00
04edd037-4b3b-4c18-a35d-ee8913506d2b	a3086873-0df1-457e-9818-8f13f5796d26	legal_status	Public Record(s)	2024-02-22 09:26:27.344+00
0efe8d8c-2b26-4502-9d28-7c166e8a7487	a3086873-0df1-457e-9818-8f13f5796d26	held_by	The National Archives, Kew	2024-02-22 09:26:27.345+00
e1940418-ffe0-4f80-bcbc-53fdcabcef51	a3086873-0df1-457e-9818-8f13f5796d26	closure_type	Open	2024-02-22 09:26:27.347+00
dcae520b-b047-452a-a0ff-b73bb7de4abc	a3086873-0df1-457e-9818-8f13f5796d26	title_closed	false	2024-02-22 09:26:27.348+00
c498785f-afe6-4893-bc77-728bfbca70ad	a3086873-0df1-457e-9818-8f13f5796d26	description_closed	false	2024-02-22 09:26:27.349+00
c4b13f54-148d-4493-a6ed-f76094d9b513	a3086873-0df1-457e-9818-8f13f5796d26	language	English	2024-02-22 09:26:27.351+00
9ea929bb-5db0-45ce-b1fd-84502849a57e	28897cd6-3348-4b57-bff6-521c7b120c0c	file_name	Presentation.pptx	2024-02-22 09:26:27.353+00
341e4ec4-c13f-4ac7-9325-b05e3acf071c	28897cd6-3348-4b57-bff6-521c7b120c0c	file_type	File	2024-02-22 09:26:27.355+00
2836ef7e-7615-433b-95b3-a8de24ab181e	28897cd6-3348-4b57-bff6-521c7b120c0c	file_size	697817	2024-02-22 09:26:27.356+00
13927e53-8c8b-43e8-b49d-0f62389c08e1	28897cd6-3348-4b57-bff6-521c7b120c0c	rights_copyright	Crown Copyright	2024-02-22 09:26:27.357+00
d34fc876-da7a-4352-8833-d443ee5400a6	28897cd6-3348-4b57-bff6-521c7b120c0c	legal_status	Public Record(s)	2024-02-22 09:26:27.358+00
2a3ecfba-29d5-4976-8472-14f701660689	28897cd6-3348-4b57-bff6-521c7b120c0c	held_by	The National Archives, Kew	2024-02-22 09:26:27.359+00
a1ee2f4c-eef4-4c2a-bc79-c64a5fc6cdc3	28897cd6-3348-4b57-bff6-521c7b120c0c	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.36+00
53c91539-c3d3-4649-add1-da1312143c5d	28897cd6-3348-4b57-bff6-521c7b120c0c	closure_type	Open	2024-02-22 09:26:27.362+00
063c2de4-69df-4d17-8a52-19679a8cf45e	28897cd6-3348-4b57-bff6-521c7b120c0c	title_closed	false	2024-02-22 09:26:27.364+00
12cfa494-5a72-434c-a19a-be5024c27f0b	28897cd6-3348-4b57-bff6-521c7b120c0c	description_closed	false	2024-02-22 09:26:27.365+00
23d76532-7ffd-43fb-8c87-97cc56ae3b44	28897cd6-3348-4b57-bff6-521c7b120c0c	language	English	2024-02-22 09:26:27.366+00
282e6d98-0e88-4b1a-94d6-a5603894054b	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	file_name	nord-lead-viewer.mxf	2024-02-22 09:26:27.372+00
b8c87562-edad-4bd6-9cba-d0fe8f72308c	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	file_type	File	2024-02-22 09:26:27.374+00
7123e682-26aa-49e5-a201-0d250f3a5bd8	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	file_size	1179295	2024-02-22 09:26:27.375+00
0243f293-7f76-4d53-8bfe-b5735c64f95e	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	rights_copyright	Crown Copyright	2024-02-22 09:26:27.376+00
02e585f1-60f9-487e-9ec9-f1dbee81b562	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	legal_status	Public Record(s)	2024-02-22 09:26:27.378+00
6773ac37-dcb4-45d4-b405-173fbfa259be	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	held_by	The National Archives, Kew	2024-02-22 09:26:27.379+00
ed19681b-11b4-4ce8-9e8c-5e697379cc8a	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.38+00
bbdf44e5-0227-47ea-8371-f7cfa38ddb4c	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	closure_type	Open	2024-02-22 09:26:27.381+00
7b4df5e9-bec4-40b2-af89-d0933f92640c	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	title_closed	false	2024-02-22 09:26:27.383+00
301e360f-a8e0-471a-b4a5-f9f849000f1e	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	description_closed	false	2024-02-22 09:26:27.384+00
9e82b4a8-127e-49ae-bfd7-bc8e3a8343fa	eaa0b74a-a889-4ea0-ab28-0237d973bdb9	language	English	2024-02-22 09:26:27.385+00
49eddebd-81f6-49ea-8cdc-c81818f184c3	c4f5ca21-2814-4d01-863e-244cfae874fb	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-22 09:26:27.391+00
6f8bb870-af09-4200-b4e7-0f19df800734	c4f5ca21-2814-4d01-863e-244cfae874fb	file_type	File	2024-02-22 09:26:27.393+00
0cdaa4eb-2c31-4c1c-96b2-4c51ea6fb8c1	c4f5ca21-2814-4d01-863e-244cfae874fb	file_size	68364	2024-02-22 09:26:27.395+00
a0e61ead-01a1-4a41-82d8-157ee9946800	c4f5ca21-2814-4d01-863e-244cfae874fb	rights_copyright	Crown Copyright	2024-02-22 09:26:27.396+00
c497ceda-e5de-4d56-9166-190700d0849f	c4f5ca21-2814-4d01-863e-244cfae874fb	legal_status	Public Record(s)	2024-02-22 09:26:27.397+00
bcfce88a-5448-4944-9c2a-dc8f2e950a1d	c4f5ca21-2814-4d01-863e-244cfae874fb	held_by	The National Archives, Kew	2024-02-22 09:26:27.398+00
41bba760-ef33-458a-bb32-0382c856abd2	c4f5ca21-2814-4d01-863e-244cfae874fb	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.399+00
13efc753-227a-4690-8f01-f44511bf6cf8	c4f5ca21-2814-4d01-863e-244cfae874fb	closure_type	Open	2024-02-22 09:26:27.401+00
8614192a-7010-41c8-9b17-324c268d281b	c4f5ca21-2814-4d01-863e-244cfae874fb	title_closed	false	2024-02-22 09:26:27.403+00
bba08ef3-ac58-4fba-94a0-a85f2f032e24	c4f5ca21-2814-4d01-863e-244cfae874fb	description_closed	false	2024-02-22 09:26:27.404+00
046e948b-74e6-4307-bb9a-18b9afc59e1e	c4f5ca21-2814-4d01-863e-244cfae874fb	language	English	2024-02-22 09:26:27.406+00
96b41262-7795-4f38-93f9-d3e8b4549e51	2a682900-0f4e-408e-a3ea-ccda2ce52799	file_name	Gateways.ppt	2024-02-22 09:26:27.413+00
12030648-0f52-4f41-b42b-8b37c80b5da7	2a682900-0f4e-408e-a3ea-ccda2ce52799	file_type	File	2024-02-22 09:26:27.415+00
d676e552-e7e4-4626-998d-7860f2fbd990	2a682900-0f4e-408e-a3ea-ccda2ce52799	file_size	446464	2024-02-22 09:26:27.417+00
50ad0827-e4ea-41d1-a902-34065724771e	2a682900-0f4e-408e-a3ea-ccda2ce52799	rights_copyright	Crown Copyright	2024-02-22 09:26:27.418+00
ed8f8d31-1cfd-4375-a4c7-edc85d8f9bd7	2a682900-0f4e-408e-a3ea-ccda2ce52799	legal_status	Public Record(s)	2024-02-22 09:26:27.42+00
47cf6419-4d4d-4b40-8169-89571cf96ba6	2a682900-0f4e-408e-a3ea-ccda2ce52799	held_by	The National Archives, Kew	2024-02-22 09:26:27.422+00
bca21b21-3622-4cde-b588-c03636436e82	2a682900-0f4e-408e-a3ea-ccda2ce52799	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.427+00
b41fb69d-04fd-4236-9a02-40b1b53ced5a	2a682900-0f4e-408e-a3ea-ccda2ce52799	closure_type	Open	2024-02-22 09:26:27.428+00
36e13755-b3c6-41d3-b7d0-1d067b084774	2a682900-0f4e-408e-a3ea-ccda2ce52799	title_closed	false	2024-02-22 09:26:27.433+00
be9af49b-5ab8-47a7-960f-cd0c584c7d58	2a682900-0f4e-408e-a3ea-ccda2ce52799	description_closed	false	2024-02-22 09:26:27.436+00
563bc498-7ec5-4738-ab9b-6b1c84322629	2a682900-0f4e-408e-a3ea-ccda2ce52799	language	English	2024-02-22 09:26:27.437+00
ff71d646-3ea3-4fd7-b7ba-0e0fb631762f	0492a61c-801c-4306-9692-f51f17363ef5	file_name	base_de_donnees.png	2024-02-22 09:26:27.443+00
5727fd0f-c753-47a0-8d43-aa75419dd6df	0492a61c-801c-4306-9692-f51f17363ef5	file_type	File	2024-02-22 09:26:27.448+00
dc03df25-6723-49ac-982e-eea6c7bd67f4	0492a61c-801c-4306-9692-f51f17363ef5	file_size	165098	2024-02-22 09:26:27.45+00
ae694944-a41c-4708-9923-b56e9084cec2	0492a61c-801c-4306-9692-f51f17363ef5	rights_copyright	Crown Copyright	2024-02-22 09:26:27.451+00
4a8846ff-f9c7-4996-86d7-39c8da6a3e53	0492a61c-801c-4306-9692-f51f17363ef5	legal_status	Public Record(s)	2024-02-22 09:26:27.457+00
4081883b-9850-4e37-94db-9b2b82727e11	0492a61c-801c-4306-9692-f51f17363ef5	held_by	The National Archives, Kew	2024-02-22 09:26:27.459+00
783fb488-1ebe-4369-9828-04afd96c0ac2	0492a61c-801c-4306-9692-f51f17363ef5	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.46+00
46b33eb0-38c4-4b39-8f84-88fd90f1df45	0492a61c-801c-4306-9692-f51f17363ef5	closure_type	Open	2024-02-22 09:26:27.462+00
909a20af-d924-44e0-865c-73b753696c38	0492a61c-801c-4306-9692-f51f17363ef5	title_closed	false	2024-02-22 09:26:27.464+00
b0a05d25-f03c-464b-bcb1-03f5932e288a	0492a61c-801c-4306-9692-f51f17363ef5	description_closed	false	2024-02-22 09:26:27.47+00
a6155c29-f760-42c1-8ea1-c65aa1a7c857	0492a61c-801c-4306-9692-f51f17363ef5	language	English	2024-02-22 09:26:27.471+00
bf87932a-1389-4dc5-9ca0-a5f8e2a4be24	edb2c00c-f5be-4677-80d2-509d2aff5d3d	file_name	Digital Transfer training email .msg	2024-02-22 09:26:27.477+00
2cd62cd2-edea-4169-a916-aab207fb142c	edb2c00c-f5be-4677-80d2-509d2aff5d3d	file_type	File	2024-02-22 09:26:27.478+00
aaa09e3f-57fc-4490-926a-327111aa39f7	edb2c00c-f5be-4677-80d2-509d2aff5d3d	file_size	39424	2024-02-22 09:26:27.48+00
36194f1d-cea0-462c-8c05-b13255b24938	edb2c00c-f5be-4677-80d2-509d2aff5d3d	rights_copyright	Crown Copyright	2024-02-22 09:26:27.481+00
fec87976-91e0-46e1-8211-9d5125c799e8	edb2c00c-f5be-4677-80d2-509d2aff5d3d	legal_status	Public Record(s)	2024-02-22 09:26:27.482+00
2dbc9df3-5641-4859-89c3-2e680320f47d	edb2c00c-f5be-4677-80d2-509d2aff5d3d	held_by	The National Archives, Kew	2024-02-22 09:26:27.483+00
a41c5ba7-5d23-42ad-b176-63b2e230261b	edb2c00c-f5be-4677-80d2-509d2aff5d3d	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.484+00
11482911-3e9d-4604-923f-409b0ac0e4b5	edb2c00c-f5be-4677-80d2-509d2aff5d3d	closure_type	Open	2024-02-22 09:26:27.485+00
55a018dc-9820-4c57-8c50-54369cd13680	edb2c00c-f5be-4677-80d2-509d2aff5d3d	title_closed	false	2024-02-22 09:26:27.486+00
03ab8c42-ab1d-4a77-94fa-cce60b27409c	edb2c00c-f5be-4677-80d2-509d2aff5d3d	description_closed	false	2024-02-22 09:26:27.487+00
067510e1-c5c0-4097-b328-62da20f5e0ff	edb2c00c-f5be-4677-80d2-509d2aff5d3d	language	English	2024-02-22 09:26:27.488+00
0c1e8dcd-3c58-4c09-aaaf-ca0e6276ec66	7a5aeb37-98d4-41b4-89d3-d983053371c6	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-22 09:26:27.494+00
90edf850-eaea-4a4e-bb69-3ffd00f3f36a	7a5aeb37-98d4-41b4-89d3-d983053371c6	file_type	File	2024-02-22 09:26:27.497+00
266a3fb7-cf5e-43ad-83b7-095b7d713e9c	7a5aeb37-98d4-41b4-89d3-d983053371c6	file_size	70263	2024-02-22 09:26:27.499+00
32cfe916-0238-4821-bda0-20f9fd3dcbc6	7a5aeb37-98d4-41b4-89d3-d983053371c6	rights_copyright	Crown Copyright	2024-02-22 09:26:27.5+00
c64392b2-69ea-46da-b635-fe932ae59eb3	7a5aeb37-98d4-41b4-89d3-d983053371c6	legal_status	Public Record(s)	2024-02-22 09:26:27.501+00
fb2833d1-870a-4aff-a36d-2cc63e39dce0	7a5aeb37-98d4-41b4-89d3-d983053371c6	held_by	The National Archives, Kew	2024-02-22 09:26:27.502+00
d2f6d506-348d-4d0d-b3f9-77a96b8cf83d	7a5aeb37-98d4-41b4-89d3-d983053371c6	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.503+00
41678f05-33e6-48c0-8585-43519399605b	7a5aeb37-98d4-41b4-89d3-d983053371c6	closure_type	Open	2024-02-22 09:26:27.505+00
1fd44f2d-3545-46d3-84a6-82a600874e4c	7a5aeb37-98d4-41b4-89d3-d983053371c6	title_closed	false	2024-02-22 09:26:27.506+00
b1464c3f-348a-4143-a53a-35954045f242	7a5aeb37-98d4-41b4-89d3-d983053371c6	description_closed	false	2024-02-22 09:26:27.507+00
caf87496-60da-4fa4-b2b8-eb8e43ef06c0	7a5aeb37-98d4-41b4-89d3-d983053371c6	language	English	2024-02-22 09:26:27.508+00
59950ef6-1612-441a-9c17-723cd404c5cd	271ca5ba-d409-4400-8410-d60d1821254d	file_name	Draft DDRO 05.docx	2024-02-22 09:26:27.514+00
3a39a150-c89d-44f0-a7a4-1733410e1091	271ca5ba-d409-4400-8410-d60d1821254d	file_type	File	2024-02-22 09:26:27.515+00
385bfe1e-8dad-4347-a783-37d5de661731	271ca5ba-d409-4400-8410-d60d1821254d	file_size	21707	2024-02-22 09:26:27.516+00
0898d2e7-ab4d-4b1e-a9d0-658d0a687892	271ca5ba-d409-4400-8410-d60d1821254d	rights_copyright	Crown Copyright	2024-02-22 09:26:27.517+00
e9f78cea-fec7-4935-a183-12c59f9ffa1f	271ca5ba-d409-4400-8410-d60d1821254d	legal_status	Public Record(s)	2024-02-22 09:26:27.518+00
05926dfd-8217-4b36-8ae6-6c1d0400efaa	271ca5ba-d409-4400-8410-d60d1821254d	held_by	The National Archives, Kew	2024-02-22 09:26:27.519+00
e3399cbb-f078-4abe-9d9e-02554ad2bbb8	271ca5ba-d409-4400-8410-d60d1821254d	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.52+00
dcb656cd-9803-4291-96d9-fcdc5340462a	271ca5ba-d409-4400-8410-d60d1821254d	closure_type	Open	2024-02-22 09:26:27.521+00
1c7485f4-b663-4a39-be18-1e7dea1124ad	271ca5ba-d409-4400-8410-d60d1821254d	title_closed	false	2024-02-22 09:26:27.522+00
249ea1f1-7d20-4ff6-8b70-c0436e3d8abb	271ca5ba-d409-4400-8410-d60d1821254d	description_closed	false	2024-02-22 09:26:27.523+00
eaf3a129-455c-416c-a63f-aea13517dfe3	271ca5ba-d409-4400-8410-d60d1821254d	language	English	2024-02-22 09:26:27.524+00
84547f6f-46f4-4bbb-9700-452134853e61	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	file_name	content	2024-02-22 09:26:27.529+00
08627d70-0fa9-4dfb-9a25-6bf4ece6ec1c	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	file_type	Folder	2024-02-22 09:26:27.531+00
607e6fd4-7c49-4102-a1e1-5631972d2c65	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	rights_copyright	Crown Copyright	2024-02-22 09:26:27.532+00
b9fbdad3-d4ab-46b4-9a73-ce455c7886c2	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	legal_status	Public Record(s)	2024-02-22 09:26:27.533+00
674c3d8f-09aa-4970-9707-7db3936ab313	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	held_by	The National Archives, Kew	2024-02-22 09:26:27.534+00
667076fd-c600-4333-92ae-e72cd9cbd8db	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	closure_type	Open	2024-02-22 09:26:27.535+00
df732b7f-1211-49fc-9557-e960b75060c0	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	title_closed	false	2024-02-22 09:26:27.536+00
15eae6b7-e0c8-4501-b0ed-02ed8eb98f19	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	description_closed	false	2024-02-22 09:26:27.537+00
f2fcacc8-ab91-4eea-b7ea-a754cdb191ca	fdf879e4-3796-45ea-bd54-137a5ea2e4f1	language	English	2024-02-22 09:26:27.538+00
0f6bb76e-5130-451c-8832-32693637fecd	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-22 09:26:27.54+00
94053557-c2b1-47f5-aa1f-c279cef6c0e4	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	file_type	File	2024-02-22 09:26:27.541+00
44a490c4-554b-42a6-8f94-1968b5db88b7	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	file_size	177875	2024-02-22 09:26:27.543+00
d760bd64-d33c-4480-bd51-f0805b1e276d	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	rights_copyright	Crown Copyright	2024-02-22 09:26:27.544+00
96e808be-d156-4312-b708-3c2142c1a146	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	legal_status	Public Record(s)	2024-02-22 09:26:27.546+00
c20ebe0f-ca42-4ebb-92dc-e56cc34f1cae	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	held_by	The National Archives, Kew	2024-02-22 09:26:27.547+00
b93e9ced-a97d-4b43-b85f-7292d30f885a	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.548+00
c6efebdb-a789-4a41-b763-2b2ee994f344	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	closure_type	Open	2024-02-22 09:26:27.55+00
71223b54-c001-43e6-8c15-81bcd6105951	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	title_closed	false	2024-02-22 09:26:27.551+00
eb16d3fb-f29b-49ee-82f0-d376c029469a	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	description_closed	false	2024-02-22 09:26:27.552+00
8890eadc-955d-4fbf-b3ce-b9064a46c319	1768f4d3-3204-43aa-9a7b-cecf065a5a6c	language	English	2024-02-22 09:26:27.553+00
760252eb-51d5-4448-9a94-61268f2f24d9	71f8205b-bd25-4104-815a-06d3f5f05da1	file_name	Response Policy.docx	2024-02-22 09:26:27.558+00
65b47500-9b76-4d18-89ba-3a534c6d22cb	71f8205b-bd25-4104-815a-06d3f5f05da1	file_type	File	2024-02-22 09:26:27.559+00
c22536d7-1400-44ce-a2b2-18ea7d34660a	71f8205b-bd25-4104-815a-06d3f5f05da1	file_size	12651	2024-02-22 09:26:27.56+00
f67789d2-5072-4f81-9de0-0e50c2a47272	71f8205b-bd25-4104-815a-06d3f5f05da1	rights_copyright	Crown Copyright	2024-02-22 09:26:27.562+00
ebf51e71-6dbd-4dc2-89fd-d086304a5351	71f8205b-bd25-4104-815a-06d3f5f05da1	legal_status	Public Record(s)	2024-02-22 09:26:27.563+00
e377a60f-8469-42dd-8608-da62cdddd7f1	71f8205b-bd25-4104-815a-06d3f5f05da1	held_by	The National Archives, Kew	2024-02-22 09:26:27.564+00
ba715d17-f53c-493f-a848-46b2cd0a7237	71f8205b-bd25-4104-815a-06d3f5f05da1	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.565+00
60cff946-66b2-44fa-a223-b586e89f2219	71f8205b-bd25-4104-815a-06d3f5f05da1	closure_type	Open	2024-02-22 09:26:27.566+00
6cf1aa52-5f56-4bd3-9121-cdde92b70f20	71f8205b-bd25-4104-815a-06d3f5f05da1	title_closed	false	2024-02-22 09:26:27.572+00
57a834df-ce99-4bab-ae5a-c2744ab32d6b	71f8205b-bd25-4104-815a-06d3f5f05da1	description_closed	false	2024-02-22 09:26:27.573+00
0da45a6f-9979-4509-aff0-f634cc3d25b8	71f8205b-bd25-4104-815a-06d3f5f05da1	language	English	2024-02-22 09:26:27.574+00
a549c916-47aa-4894-9aae-2f57f3e1b1a8	adb24c10-04df-4d4c-8ed0-42077dd6b012	file_name	Thumbs.db	2024-02-22 09:26:27.578+00
97887623-3b4a-45a4-a652-c9645864a6f4	adb24c10-04df-4d4c-8ed0-42077dd6b012	file_type	File	2024-02-22 09:26:27.579+00
f6519a41-3edd-4dc9-985c-b7b8db6ac0cd	adb24c10-04df-4d4c-8ed0-42077dd6b012	file_size	685124	2024-02-22 09:26:27.58+00
3189b7db-faa7-45b8-a15d-13df4ce876da	adb24c10-04df-4d4c-8ed0-42077dd6b012	rights_copyright	Crown Copyright	2024-02-22 09:26:27.581+00
7c71a0e8-4cf3-483a-89b4-5f66e6e31e0c	adb24c10-04df-4d4c-8ed0-42077dd6b012	legal_status	Public Record(s)	2024-02-22 09:26:27.582+00
8ac10775-99eb-483b-ae47-64875e9b6451	adb24c10-04df-4d4c-8ed0-42077dd6b012	held_by	The National Archives, Kew	2024-02-22 09:26:27.583+00
af2515a6-752d-417a-aa86-d4a30066ac88	adb24c10-04df-4d4c-8ed0-42077dd6b012	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.585+00
31eed49a-6f7f-471a-be3e-eaa44a1a40e8	adb24c10-04df-4d4c-8ed0-42077dd6b012	closure_type	Open	2024-02-22 09:26:27.586+00
e422e636-45ca-4b0c-b876-2a75ec9375c9	adb24c10-04df-4d4c-8ed0-42077dd6b012	title_closed	false	2024-02-22 09:26:27.587+00
ba2a10b0-6692-4406-b1e3-b437e9b596f1	adb24c10-04df-4d4c-8ed0-42077dd6b012	description_closed	false	2024-02-22 09:26:27.588+00
ddc7d21d-47df-4eba-b575-c662f1d9c15e	adb24c10-04df-4d4c-8ed0-42077dd6b012	language	English	2024-02-22 09:26:27.589+00
1a956ef0-1bea-4c2c-a0c3-1eb819c72e41	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	file_name	Remove.docx	2024-02-22 09:26:27.597+00
184e88e5-f22b-4714-9e3a-60fbe0db4f21	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	file_type	File	2024-02-22 09:26:27.599+00
629a1471-27c9-46be-b4e6-7724e6def195	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	file_size	12609	2024-02-22 09:26:27.601+00
de7d875a-ba6d-4c81-8259-7230660d9e62	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	rights_copyright	Crown Copyright	2024-02-22 09:26:27.602+00
4e0119fe-e3d9-4989-a576-cf07139773e1	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	legal_status	Public Record(s)	2024-02-22 09:26:27.603+00
749b2302-3bde-4195-8d79-2dad2f91ad0b	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	held_by	The National Archives, Kew	2024-02-22 09:26:27.604+00
794ff073-0528-4618-8901-fb37d0fa6d90	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.605+00
2f1199a7-0b81-42d0-b1c0-6d1eb81bd917	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	closure_type	Open	2024-02-22 09:26:27.606+00
4861341e-ead6-4087-aa2c-a55c68c880ef	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	title_closed	false	2024-02-22 09:26:27.607+00
050f9968-7914-4d30-a4ff-af681bd0e629	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	description_closed	false	2024-02-22 09:26:27.608+00
95a369b6-0923-4b9e-8ca6-bf7ec0b77c29	2bc446e6-9dbb-4c37-abf5-d49ae11483b3	language	English	2024-02-22 09:26:27.609+00
5a311de3-fce6-4d16-b863-1d0b9cc978c6	a4024256-ae42-4320-abfd-1057c755d5cb	file_name	Response Procedure.docx	2024-02-22 09:26:27.626+00
e47e228d-88ec-4f68-b3fb-9876537cbc62	a4024256-ae42-4320-abfd-1057c755d5cb	file_type	File	2024-02-22 09:26:27.629+00
113b9443-9235-4253-a1c2-f499420c5604	a4024256-ae42-4320-abfd-1057c755d5cb	file_size	12610	2024-02-22 09:26:27.63+00
1e73df6c-9e3a-4748-af32-b3b83599a816	a4024256-ae42-4320-abfd-1057c755d5cb	rights_copyright	Crown Copyright	2024-02-22 09:26:27.631+00
a2f6160f-e9ee-4d74-a41f-9a3f753d8ef6	a4024256-ae42-4320-abfd-1057c755d5cb	legal_status	Public Record(s)	2024-02-22 09:26:27.632+00
553e1351-1863-4a06-b9d2-50e2d4db0408	a4024256-ae42-4320-abfd-1057c755d5cb	held_by	The National Archives, Kew	2024-02-22 09:26:27.633+00
580a59a9-4564-412d-9a0d-f5398c5b4525	a4024256-ae42-4320-abfd-1057c755d5cb	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.635+00
a3a549fb-000e-4af1-a1dd-b0b110632e60	a4024256-ae42-4320-abfd-1057c755d5cb	closure_type	Open	2024-02-22 09:26:27.636+00
11933f0a-1174-45b6-9816-823cf2cc8e1a	a4024256-ae42-4320-abfd-1057c755d5cb	title_closed	false	2024-02-22 09:26:27.637+00
b30e6250-6a38-458a-861f-477a14c267d9	a4024256-ae42-4320-abfd-1057c755d5cb	description_closed	false	2024-02-22 09:26:27.638+00
8dc49a65-bf8a-4334-a04b-e41e5d843478	a4024256-ae42-4320-abfd-1057c755d5cb	language	English	2024-02-22 09:26:27.639+00
8f2f140f-b860-444e-b71b-a2e7de85ca26	df1efb2b-3ab0-4913-a93e-fedb84cde33e	file_name	Emergency Contact Details Paul Young.docx	2024-02-22 09:26:27.643+00
99881863-5f1c-41d1-a90f-43a441640c03	df1efb2b-3ab0-4913-a93e-fedb84cde33e	file_type	File	2024-02-22 09:26:27.644+00
81cc5d2d-07bd-4655-beef-49c6216bf1e8	df1efb2b-3ab0-4913-a93e-fedb84cde33e	file_size	12825	2024-02-22 09:26:27.646+00
80cd7a42-8da5-43ef-892c-9c7822185bda	df1efb2b-3ab0-4913-a93e-fedb84cde33e	rights_copyright	Crown Copyright	2024-02-22 09:26:27.647+00
dea45900-e37b-42e6-b841-8dcbd2e96b52	df1efb2b-3ab0-4913-a93e-fedb84cde33e	legal_status	Public Record(s)	2024-02-22 09:26:27.648+00
9d88d2d6-631d-46d1-9149-8f499df8c014	df1efb2b-3ab0-4913-a93e-fedb84cde33e	held_by	The National Archives, Kew	2024-02-22 09:26:27.649+00
d56472f1-6378-4ca9-9ef9-733e2238a95c	df1efb2b-3ab0-4913-a93e-fedb84cde33e	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.65+00
450eb071-d769-4cf5-a4fe-3997f4f1ebf3	df1efb2b-3ab0-4913-a93e-fedb84cde33e	closure_type	Open	2024-02-22 09:26:27.651+00
3cbf06cb-26c6-42e5-807e-d805af34abce	df1efb2b-3ab0-4913-a93e-fedb84cde33e	title_closed	false	2024-02-22 09:26:27.652+00
70e71fdf-1618-4ed7-9a3d-8da0c8a07585	df1efb2b-3ab0-4913-a93e-fedb84cde33e	description_closed	false	2024-02-22 09:26:27.653+00
9c9e06a1-992d-4b44-abd9-af8a354389a8	df1efb2b-3ab0-4913-a93e-fedb84cde33e	language	English	2024-02-22 09:26:27.654+00
44aacb40-aa92-4601-805a-0002510127fb	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	file_name	DTP_ Sensitivity review process.docx	2024-02-22 09:26:27.658+00
73475b96-9d08-42ed-a2ce-d71ceb288bff	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	file_type	File	2024-02-22 09:26:27.659+00
7b3cfda3-40e4-4fc7-aeae-e10376aa124b	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	file_size	70674	2024-02-22 09:26:27.66+00
9056ad6f-e019-4d97-8ce7-69ef162d69b3	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	rights_copyright	Crown Copyright	2024-02-22 09:26:27.661+00
606e204a-bc60-47e3-9ab8-f8002b7e092d	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	legal_status	Public Record(s)	2024-02-22 09:26:27.662+00
8979be99-428e-4615-9950-cbdb168a6bea	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	held_by	The National Archives, Kew	2024-02-22 09:26:27.663+00
0241c9fc-6e1a-436f-be07-e98969e31c57	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.664+00
674f4388-598f-44b3-bc7b-5ff252ba51c2	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	closure_type	Open	2024-02-22 09:26:27.665+00
ae6f4e6c-d091-4f84-96f1-201c2c0b2195	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	title_closed	false	2024-02-22 09:26:27.666+00
0131eb8f-8993-4ba5-8ac4-dee5241979f0	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	description_closed	false	2024-02-22 09:26:27.667+00
5d006d18-e609-4f04-8ae4-8ab1c70372df	4c696e62-b48d-40c7-b32c-dd9f9f59a48c	language	English	2024-02-22 09:26:27.668+00
5205ae59-1f2f-4b36-97d7-ce2361b8ca0f	8b16df3a-d778-435b-bb55-d5b3c594b87d	file_name	Emergency Response Team	2024-02-22 09:26:27.673+00
51777ec8-bef7-41ad-9096-4914975aea3b	8b16df3a-d778-435b-bb55-d5b3c594b87d	file_type	Folder	2024-02-22 09:26:27.674+00
6d259435-32c8-46aa-a941-916ebfb76338	8b16df3a-d778-435b-bb55-d5b3c594b87d	rights_copyright	Crown Copyright	2024-02-22 09:26:27.675+00
e18e39c7-ae82-4e63-af7d-d6a8f863e889	8b16df3a-d778-435b-bb55-d5b3c594b87d	legal_status	Public Record(s)	2024-02-22 09:26:27.676+00
0afc636c-89e9-4705-874d-007c82073b89	8b16df3a-d778-435b-bb55-d5b3c594b87d	held_by	The National Archives, Kew	2024-02-22 09:26:27.678+00
20eb3a35-1ca8-49d7-a85e-cccffefe92c2	8b16df3a-d778-435b-bb55-d5b3c594b87d	closure_type	Open	2024-02-22 09:26:27.679+00
c36b57e5-bb3d-49f6-9c85-377d523cab25	8b16df3a-d778-435b-bb55-d5b3c594b87d	title_closed	false	2024-02-22 09:26:27.68+00
84370c15-f546-4177-ac8b-db9c0d965e30	8b16df3a-d778-435b-bb55-d5b3c594b87d	description_closed	false	2024-02-22 09:26:27.681+00
64d4c03f-f534-4705-8d6a-219886b57e00	8b16df3a-d778-435b-bb55-d5b3c594b87d	language	English	2024-02-22 09:26:27.681+00
3953da2c-a82d-4d3f-acab-c75ad5441f3a	b753468a-9a29-45b9-bd4f-2ed7c7c26691	file_name	DTP.docx	2024-02-22 09:26:27.683+00
6acdb99f-fecb-406e-b14b-31e19e2adb9c	b753468a-9a29-45b9-bd4f-2ed7c7c26691	file_type	File	2024-02-22 09:26:27.685+00
9c1836b8-0137-4c0f-b88d-33ee9011ba1c	b753468a-9a29-45b9-bd4f-2ed7c7c26691	file_size	70263	2024-02-22 09:26:27.686+00
181c1ceb-40de-4b74-bd52-c25f9b0380f2	b753468a-9a29-45b9-bd4f-2ed7c7c26691	rights_copyright	Crown Copyright	2024-02-22 09:26:27.687+00
4b1fae4b-3e16-4fa7-b0d2-c49119028bbe	b753468a-9a29-45b9-bd4f-2ed7c7c26691	legal_status	Public Record(s)	2024-02-22 09:26:27.688+00
a64daa78-6cc9-47bb-abd4-1dc4aec06426	b753468a-9a29-45b9-bd4f-2ed7c7c26691	held_by	The National Archives, Kew	2024-02-22 09:26:27.689+00
5355841e-002d-492b-94df-da1191ab6c23	b753468a-9a29-45b9-bd4f-2ed7c7c26691	date_last_modified	2022-07-18T00:00:00	2024-02-22 09:26:27.69+00
af4a02f8-8945-4f26-b87d-0c9168b91596	b753468a-9a29-45b9-bd4f-2ed7c7c26691	closure_type	Open	2024-02-22 09:26:27.691+00
223ad405-0ce5-478a-827e-ef52ec3871e2	b753468a-9a29-45b9-bd4f-2ed7c7c26691	title_closed	false	2024-02-22 09:26:27.692+00
8bc45a8f-50d0-4675-956f-7ce42b557d94	b753468a-9a29-45b9-bd4f-2ed7c7c26691	description_closed	false	2024-02-22 09:26:27.693+00
d5b87148-807f-4db8-82b1-fa82548f13e1	b753468a-9a29-45b9-bd4f-2ed7c7c26691	language	English	2024-02-22 09:26:27.694+00
285da911-3bf8-462d-9724-4fa817774594	07f44a3d-21f9-4b02-9846-c5fd3fa72244	file_name	Response Policy.docx	2024-02-22 13:46:05.274+00
97e3043e-3196-4add-9eb2-3bd04494c26b	07f44a3d-21f9-4b02-9846-c5fd3fa72244	file_type	File	2024-02-22 13:46:05.276+00
a3ad0423-3ca7-481c-aaaf-ab8b8234c3cc	07f44a3d-21f9-4b02-9846-c5fd3fa72244	file_size	12651	2024-02-22 13:46:05.278+00
ff0449c0-45be-4c32-828a-dff6e9637984	07f44a3d-21f9-4b02-9846-c5fd3fa72244	rights_copyright	Crown Copyright	2024-02-22 13:46:05.279+00
b4fc85d9-2ad3-4548-85b8-6d5c9fdbc42f	07f44a3d-21f9-4b02-9846-c5fd3fa72244	legal_status	Public Record(s)	2024-02-22 13:46:05.281+00
c1a43c81-cbe5-45de-9467-63b4232d1992	07f44a3d-21f9-4b02-9846-c5fd3fa72244	held_by	The National Archives, Kew	2024-02-22 13:46:05.283+00
85bdfe2f-6b54-4de8-8f5b-54135a0b3422	07f44a3d-21f9-4b02-9846-c5fd3fa72244	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.284+00
d3390f54-8809-472a-be13-12f497596e83	07f44a3d-21f9-4b02-9846-c5fd3fa72244	closure_type	Open	2024-02-22 13:46:05.285+00
98088622-e088-4f79-9b11-608d337076e7	07f44a3d-21f9-4b02-9846-c5fd3fa72244	title_closed	false	2024-02-22 13:46:05.287+00
5b2f8231-4ab9-44cd-bb8b-7aa01f58f02d	07f44a3d-21f9-4b02-9846-c5fd3fa72244	description_closed	false	2024-02-22 13:46:05.288+00
e7ab1306-5604-4f93-9339-e5e6c9707a38	07f44a3d-21f9-4b02-9846-c5fd3fa72244	language	English	2024-02-22 13:46:05.289+00
f33ee305-c04e-4670-ba4c-204681bc7182	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	file_name	Response Procedure.docx	2024-02-22 13:46:05.296+00
6c09b7c2-928c-49ab-ba8e-63c44fbdea4d	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	file_type	File	2024-02-22 13:46:05.297+00
7950b0a1-dad3-48c0-857c-d7cecbef24ce	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	file_size	12610	2024-02-22 13:46:05.298+00
d7fd534f-5b12-421b-ba79-d6fdde19cdae	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	rights_copyright	Crown Copyright	2024-02-22 13:46:05.299+00
b9307b5e-9e6f-43ef-8fe7-cbaf3fad806d	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	legal_status	Public Record(s)	2024-02-22 13:46:05.3+00
4b3f5c09-35ce-4418-8be8-1ccf348c4768	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	held_by	The National Archives, Kew	2024-02-22 13:46:05.301+00
74d7afd1-2522-45fb-95c8-d31b3932b2c8	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.302+00
d64217a0-650b-4ada-99ff-93f4264a6801	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	closure_type	Open	2024-02-22 13:46:05.303+00
3e672b1f-ebe4-450e-9587-d59d9bb49c70	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	title_closed	false	2024-02-22 13:46:05.304+00
785c92db-ebfc-43a2-b143-b4127c3796b2	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	description_closed	false	2024-02-22 13:46:05.306+00
5e5abd02-90e9-4ec9-bd04-61a158dde03a	8146bb42-dbc2-4d8d-b9f2-bfdd6380da47	language	English	2024-02-22 13:46:05.307+00
d7d17235-e6ae-46b8-8e09-750a0aeacaf3	9a7fb80e-2b4d-4411-9afd-d8d33e312327	file_name	Emergency Contact Details Paul Young.docx	2024-02-22 13:46:05.312+00
748da175-9be0-4837-9363-290f02189458	9a7fb80e-2b4d-4411-9afd-d8d33e312327	file_type	File	2024-02-22 13:46:05.313+00
1e5e82de-c4ca-46bc-a659-0dbf6a6ff5dc	9a7fb80e-2b4d-4411-9afd-d8d33e312327	file_size	12825	2024-02-22 13:46:05.314+00
cf3d64b5-499a-4de3-b923-afbe59638fa9	9a7fb80e-2b4d-4411-9afd-d8d33e312327	rights_copyright	Crown Copyright	2024-02-22 13:46:05.315+00
bdd72a93-f07c-489a-b67e-bdd27eb26f35	9a7fb80e-2b4d-4411-9afd-d8d33e312327	legal_status	Public Record(s)	2024-02-22 13:46:05.317+00
3aa1b578-0694-4a6c-878b-16f66f17974b	9a7fb80e-2b4d-4411-9afd-d8d33e312327	held_by	The National Archives, Kew	2024-02-22 13:46:05.318+00
b2350a47-8702-415b-822b-6015089fdde2	9a7fb80e-2b4d-4411-9afd-d8d33e312327	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.32+00
2618324d-1eba-4d0f-a771-f3fd1e6013ca	9a7fb80e-2b4d-4411-9afd-d8d33e312327	closure_type	Open	2024-02-22 13:46:05.323+00
e7c86fb5-31a2-42b6-82e0-9c97ca2a12e7	9a7fb80e-2b4d-4411-9afd-d8d33e312327	title_closed	false	2024-02-22 13:46:05.324+00
fd8d2788-0d6f-4bf4-afb8-4c04cb5c69c1	9a7fb80e-2b4d-4411-9afd-d8d33e312327	description_closed	false	2024-02-22 13:46:05.325+00
8af5aa60-94ea-451c-9b56-75afc0b9f8d4	9a7fb80e-2b4d-4411-9afd-d8d33e312327	language	English	2024-02-22 13:46:05.327+00
1de3d058-1831-4d00-939b-db5d6633031a	f9b72ffa-672c-4d0d-aff5-54da5e335e32	file_name	Gateways.ppt	2024-02-22 13:46:05.332+00
ca5c97eb-25f5-4874-a07c-04638183f360	f9b72ffa-672c-4d0d-aff5-54da5e335e32	file_type	File	2024-02-22 13:46:05.334+00
c4647bed-ea2a-483b-a14c-37d9c5dac6b0	f9b72ffa-672c-4d0d-aff5-54da5e335e32	file_size	446464	2024-02-22 13:46:05.335+00
207867a9-97d5-47fe-a49a-dd2a4d326a25	f9b72ffa-672c-4d0d-aff5-54da5e335e32	rights_copyright	Crown Copyright	2024-02-22 13:46:05.336+00
d3342500-a3bf-43c4-8029-0f27f1cdeecb	f9b72ffa-672c-4d0d-aff5-54da5e335e32	legal_status	Public Record(s)	2024-02-22 13:46:05.338+00
8ec8ce20-6df4-48ca-809a-cb0e2abe7542	f9b72ffa-672c-4d0d-aff5-54da5e335e32	held_by	The National Archives, Kew	2024-02-22 13:46:05.339+00
8be134b6-e925-4d0b-b6f8-bf1c64293ce1	f9b72ffa-672c-4d0d-aff5-54da5e335e32	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.34+00
afc5b228-a1a5-4ee7-9874-8c530d813c2d	f9b72ffa-672c-4d0d-aff5-54da5e335e32	closure_type	Open	2024-02-22 13:46:05.341+00
467e4b3a-b987-4542-99d1-f7f48ab6e6e2	f9b72ffa-672c-4d0d-aff5-54da5e335e32	title_closed	false	2024-02-22 13:46:05.342+00
084d45cd-e63f-4175-b4b1-4335f2985490	f9b72ffa-672c-4d0d-aff5-54da5e335e32	description_closed	false	2024-02-22 13:46:05.343+00
d8e00eb6-8d55-4e68-b2c6-e4cdd4eb0873	f9b72ffa-672c-4d0d-aff5-54da5e335e32	language	English	2024-02-22 13:46:05.344+00
2203a76f-4f0d-4eb4-bc29-87d0f176475d	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	file_name	nord-lead-viewer.mxf	2024-02-22 13:46:05.352+00
cf024548-3eb9-46fa-8783-ebcfbf98491c	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	file_type	File	2024-02-22 13:46:05.353+00
f4217c2e-cd73-4a16-8a0a-e90de8dce595	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	file_size	1179295	2024-02-22 13:46:05.354+00
29719d27-e39c-4b33-9c16-51dbb5866060	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	rights_copyright	Crown Copyright	2024-02-22 13:46:05.355+00
a9bf6f41-461d-455f-b2f3-0c4efa199c3b	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	legal_status	Public Record(s)	2024-02-22 13:46:05.356+00
be0a665e-c346-4c34-93e5-9161134cdff9	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	held_by	The National Archives, Kew	2024-02-22 13:46:05.357+00
a7642673-4f8d-4e75-ba14-6b7cea9ac2c3	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.359+00
173494ad-f70b-46f6-ae5f-e02e27791967	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	closure_type	Open	2024-02-22 13:46:05.363+00
b26ac0e0-22b2-4685-8b01-8b02ce2b4554	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	title_closed	false	2024-02-22 13:46:05.366+00
575fb58f-16b1-4a18-937e-db3b64fc2cda	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	description_closed	false	2024-02-22 13:46:05.37+00
71995a0f-1ce8-44a0-b44f-4774e31bf37e	e97ff998-1ef2-496a-9a0c-2d2ad52f67bb	language	English	2024-02-22 13:46:05.371+00
04ef0a32-5de7-489c-a0e2-a947ab42eefa	e5788ac9-7a20-42bd-b61c-e001d781bcce	file_name	delivery-form-digital.doc	2024-02-22 13:46:05.377+00
06f9808d-888e-4eff-936b-82debd84e9fc	e5788ac9-7a20-42bd-b61c-e001d781bcce	file_type	File	2024-02-22 13:46:05.378+00
8609c86c-a164-446c-881d-9ae34e493ca4	e5788ac9-7a20-42bd-b61c-e001d781bcce	file_size	139776	2024-02-22 13:46:05.379+00
e16f6338-5820-4ee1-8afb-1fead7b8f6f0	e5788ac9-7a20-42bd-b61c-e001d781bcce	rights_copyright	Crown Copyright	2024-02-22 13:46:05.381+00
39cccb95-2e64-4802-be45-1b6b36b7b810	e5788ac9-7a20-42bd-b61c-e001d781bcce	legal_status	Public Record(s)	2024-02-22 13:46:05.382+00
68a280c9-0839-49ee-80a0-1191dd510065	e5788ac9-7a20-42bd-b61c-e001d781bcce	held_by	The National Archives, Kew	2024-02-22 13:46:05.383+00
a6162f1e-f471-4f71-a903-a17ba2ce21f7	e5788ac9-7a20-42bd-b61c-e001d781bcce	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.384+00
8b53b4d4-0896-4290-9152-08cc5be92294	e5788ac9-7a20-42bd-b61c-e001d781bcce	closure_type	Open	2024-02-22 13:46:05.385+00
0ed8a3d6-259f-4500-969e-eda197aa41fb	e5788ac9-7a20-42bd-b61c-e001d781bcce	title_closed	false	2024-02-22 13:46:05.386+00
4ee9b51a-3ee8-4a62-bde0-b2f21edbae6d	e5788ac9-7a20-42bd-b61c-e001d781bcce	description_closed	false	2024-02-22 13:46:05.387+00
b11107bc-cd07-41ce-943a-812cb8d57bbc	e5788ac9-7a20-42bd-b61c-e001d781bcce	language	English	2024-02-22 13:46:05.388+00
61782ee4-f9b3-4697-868b-eadc88b0e3dc	e211826c-bfe5-45ea-a080-4cfcd696678c	file_name	DTP_ Sensitivity review process.docx	2024-02-22 13:46:05.396+00
e34b08d6-95a8-43f0-ada0-cc5bbaa06df9	e211826c-bfe5-45ea-a080-4cfcd696678c	file_type	File	2024-02-22 13:46:05.398+00
0e0a54ad-71ab-47c8-ac70-f2397c09e672	e211826c-bfe5-45ea-a080-4cfcd696678c	file_size	70674	2024-02-22 13:46:05.399+00
89916a4a-9688-4605-b38b-15471f864116	e211826c-bfe5-45ea-a080-4cfcd696678c	rights_copyright	Crown Copyright	2024-02-22 13:46:05.402+00
a76f43ed-fc38-4455-ad9e-cdc3733e83c2	e211826c-bfe5-45ea-a080-4cfcd696678c	legal_status	Public Record(s)	2024-02-22 13:46:05.404+00
c92b177c-139a-450e-b843-b100c38fe8ea	e211826c-bfe5-45ea-a080-4cfcd696678c	held_by	The National Archives, Kew	2024-02-22 13:46:05.405+00
d1e6a927-9306-499a-93fb-178abca3353d	e211826c-bfe5-45ea-a080-4cfcd696678c	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.407+00
be1693dc-e606-4290-8b2b-5bf53c091c8f	e211826c-bfe5-45ea-a080-4cfcd696678c	closure_type	Open	2024-02-22 13:46:05.408+00
16c5339e-e39c-409a-98fa-34ccce44751c	e211826c-bfe5-45ea-a080-4cfcd696678c	title_closed	false	2024-02-22 13:46:05.41+00
092d4fa3-6b2b-4b3e-9fbd-15fc22e102c9	e211826c-bfe5-45ea-a080-4cfcd696678c	description_closed	false	2024-02-22 13:46:05.411+00
d28e01fc-6e21-42c8-a239-c7905eecf1f6	e211826c-bfe5-45ea-a080-4cfcd696678c	language	English	2024-02-22 13:46:05.412+00
993d953a-1268-45b6-897c-96ea872fef67	5f9c5169-2f65-4e5c-a075-0979a579846e	file_name	Digital Transfer training email .msg	2024-02-22 13:46:05.416+00
2e080544-8eec-47bf-a791-9f06f72f54d9	5f9c5169-2f65-4e5c-a075-0979a579846e	file_type	File	2024-02-22 13:46:05.417+00
58f9116c-0e84-43ce-a26d-4186a00d58bc	5f9c5169-2f65-4e5c-a075-0979a579846e	file_size	39424	2024-02-22 13:46:05.419+00
3b438c4d-0905-4204-bff0-dc24400fda2d	5f9c5169-2f65-4e5c-a075-0979a579846e	rights_copyright	Crown Copyright	2024-02-22 13:46:05.42+00
7bd1860a-0fc3-47a5-bb86-6ad39a46f026	5f9c5169-2f65-4e5c-a075-0979a579846e	legal_status	Public Record(s)	2024-02-22 13:46:05.421+00
2126cc30-a1a6-462b-a3a4-bfcafeb711be	5f9c5169-2f65-4e5c-a075-0979a579846e	held_by	The National Archives, Kew	2024-02-22 13:46:05.422+00
ffed8b94-6d46-4425-9830-13c6db8b8524	5f9c5169-2f65-4e5c-a075-0979a579846e	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.423+00
ac5d92c3-91d2-4dd8-9b5e-abfeefce54f5	5f9c5169-2f65-4e5c-a075-0979a579846e	closure_type	Open	2024-02-22 13:46:05.424+00
1f3838c2-63ae-4564-880c-02ff8b45dc63	5f9c5169-2f65-4e5c-a075-0979a579846e	title_closed	false	2024-02-22 13:46:05.425+00
fd8eabec-8b44-41b9-b70b-26d5fb8a9e66	5f9c5169-2f65-4e5c-a075-0979a579846e	description_closed	false	2024-02-22 13:46:05.426+00
412df5f4-ae3c-4ded-bd76-df98ff154166	5f9c5169-2f65-4e5c-a075-0979a579846e	language	English	2024-02-22 13:46:05.427+00
ba4f6c09-c034-45c0-9fe6-afbbde925b81	fd947cb3-6917-4162-8068-92ed11d7371a	file_name	Thumbs.db	2024-02-22 13:46:05.432+00
82974520-5695-4952-a76c-ab36ea0450d0	fd947cb3-6917-4162-8068-92ed11d7371a	file_type	File	2024-02-22 13:46:05.433+00
7897e8e6-d9dd-4a3a-a9a4-f4d32526ba87	fd947cb3-6917-4162-8068-92ed11d7371a	file_size	685124	2024-02-22 13:46:05.434+00
f96a2306-6d22-4a9e-ae2b-b2925277109d	fd947cb3-6917-4162-8068-92ed11d7371a	rights_copyright	Crown Copyright	2024-02-22 13:46:05.435+00
683cdd3a-d805-48f7-9560-e14c51e7028c	fd947cb3-6917-4162-8068-92ed11d7371a	legal_status	Public Record(s)	2024-02-22 13:46:05.436+00
84ca1921-f8da-4ed2-a49a-3eda1b910829	fd947cb3-6917-4162-8068-92ed11d7371a	held_by	The National Archives, Kew	2024-02-22 13:46:05.438+00
398ddaf8-ed66-4f09-9c89-210e0714a83f	fd947cb3-6917-4162-8068-92ed11d7371a	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.439+00
d5a77f3c-b848-4acf-ae4d-78b001a5807d	fd947cb3-6917-4162-8068-92ed11d7371a	closure_type	Open	2024-02-22 13:46:05.44+00
8dd53e4f-9268-4128-b046-f40e7ccdcea7	fd947cb3-6917-4162-8068-92ed11d7371a	title_closed	false	2024-02-22 13:46:05.441+00
d12a632d-67a2-41d7-8e23-3d5ea4297d80	fd947cb3-6917-4162-8068-92ed11d7371a	description_closed	false	2024-02-22 13:46:05.442+00
858ef734-dd38-4fff-813f-967dbe61e08c	fd947cb3-6917-4162-8068-92ed11d7371a	language	English	2024-02-22 13:46:05.443+00
815be26e-da70-4e33-bc8e-7c0b2f99935e	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-22 13:46:05.448+00
55d6c639-3bd4-40a0-893b-bdec1d1d3dd6	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	file_type	File	2024-02-22 13:46:05.449+00
4c571642-f10c-403c-b606-10004eddfdb7	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	file_size	70263	2024-02-22 13:46:05.451+00
e5044d19-71e4-4d46-9d5f-17e446a9aca1	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	rights_copyright	Crown Copyright	2024-02-22 13:46:05.452+00
84ec2762-cbc8-4825-9153-6a1875cd9d5c	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	legal_status	Public Record(s)	2024-02-22 13:46:05.454+00
b6f5b6e0-3e0f-4b78-b134-1270e3515c80	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	held_by	The National Archives, Kew	2024-02-22 13:46:05.458+00
590265cb-f35a-48f7-94e2-f7b1452f0260	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.46+00
0abbe68b-bf0c-44fe-8656-f93a16e07359	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	closure_type	Open	2024-02-22 13:46:05.461+00
6481cf9c-765c-4fd1-87fe-0d0f12751bf1	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	title_closed	false	2024-02-22 13:46:05.463+00
bd315b31-68b9-4ba6-9dba-4bb26b198b72	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	description_closed	false	2024-02-22 13:46:05.464+00
8c223461-c280-40d8-85ca-8bf6716aa4ae	9d27d5c4-a8b0-4ed7-9880-175b88ae6caa	language	English	2024-02-22 13:46:05.466+00
fdfd4c74-37d4-40d9-8c8f-5371dd4863b7	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-22 13:46:05.47+00
c079212d-983c-4262-9894-c81f913b9fee	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	file_type	File	2024-02-22 13:46:05.471+00
3e77d98b-cf2c-4920-a1b1-9af3a98565f2	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	file_size	68364	2024-02-22 13:46:05.472+00
876f62d6-d7f1-4130-9227-ffdfe6984083	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	rights_copyright	Crown Copyright	2024-02-22 13:46:05.474+00
931fca29-808c-4233-8c82-cb53d764f730	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	legal_status	Public Record(s)	2024-02-22 13:46:05.475+00
7495ca9b-392e-41c2-9498-fa40cd9c3057	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	held_by	The National Archives, Kew	2024-02-22 13:46:05.476+00
909efd91-1da9-412f-8497-95a9c9adcd45	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.477+00
917825f6-7c8a-467b-8164-d0c28abf3937	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	closure_type	Open	2024-02-22 13:46:05.478+00
6309a0f1-d961-451e-a16a-4a1891609516	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	title_closed	false	2024-02-22 13:46:05.479+00
a2d1bde3-2f11-4a97-b35a-66104dec28b4	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	description_closed	false	2024-02-22 13:46:05.481+00
2fdd0b87-0494-487d-9291-a8aef6f76a2a	4fc79a0d-8ae8-4022-9950-7dd837ffe21d	language	English	2024-02-22 13:46:05.482+00
5b3242d5-2df6-43bd-a91d-85b8f649c35a	228741f8-65d8-4f24-9a95-6afaf594990a	file_name	base_de_donnees.png	2024-02-22 13:46:05.49+00
4f17093b-eb5a-4d99-9239-fe5680e721a7	228741f8-65d8-4f24-9a95-6afaf594990a	file_type	File	2024-02-22 13:46:05.491+00
261c080c-795b-4c8f-b92e-a03210ba9317	228741f8-65d8-4f24-9a95-6afaf594990a	file_size	165098	2024-02-22 13:46:05.493+00
32362022-b50a-4ca9-9f8e-9a86fb6aeadb	228741f8-65d8-4f24-9a95-6afaf594990a	rights_copyright	Crown Copyright	2024-02-22 13:46:05.494+00
8e0c0b42-1a87-48c9-af6f-8c0d4b200f7e	228741f8-65d8-4f24-9a95-6afaf594990a	legal_status	Public Record(s)	2024-02-22 13:46:05.495+00
d7874bce-c8d4-41a8-b9ac-64fcc809426c	228741f8-65d8-4f24-9a95-6afaf594990a	held_by	The National Archives, Kew	2024-02-22 13:46:05.496+00
eb1163f7-6a98-436f-9a1c-635935b0b29e	228741f8-65d8-4f24-9a95-6afaf594990a	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.497+00
23cebc11-b2e9-469f-af0a-74359b19e3e7	228741f8-65d8-4f24-9a95-6afaf594990a	closure_type	Open	2024-02-22 13:46:05.498+00
e7ccd354-a430-412b-a40b-4595f2d0cad8	228741f8-65d8-4f24-9a95-6afaf594990a	title_closed	false	2024-02-22 13:46:05.499+00
b1133b41-4ce8-4c18-a09c-00eac9fab428	228741f8-65d8-4f24-9a95-6afaf594990a	description_closed	false	2024-02-22 13:46:05.501+00
f04d1bac-0fe8-4d09-afb3-7ecf31939652	228741f8-65d8-4f24-9a95-6afaf594990a	language	English	2024-02-22 13:46:05.502+00
e11ed930-a61c-465f-9c3e-693be24cfb42	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	file_name	Draft DDRO 05.docx	2024-02-22 13:46:05.507+00
426d81a8-db18-4c46-bd44-61ea8601ccf7	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	file_type	File	2024-02-22 13:46:05.509+00
a68269bc-cf0c-4a38-beac-2f92fc881169	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	file_size	21707	2024-02-22 13:46:05.51+00
a3b98c3a-acea-4016-8718-a248bcc56395	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	rights_copyright	Crown Copyright	2024-02-22 13:46:05.511+00
17a6ba66-a51a-48d0-adee-4b5c6a419a9a	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	legal_status	Public Record(s)	2024-02-22 13:46:05.512+00
bdd3c369-7c5e-4793-87fc-bdb5a88e7eca	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	held_by	The National Archives, Kew	2024-02-22 13:46:05.513+00
5ab0ff37-ae4f-47f6-8ec0-f7f35c561201	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.514+00
8b81424b-1895-4603-ba2c-77f805dcf39b	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	closure_type	Open	2024-02-22 13:46:05.516+00
c83d0cfa-03bf-4eae-acf8-9b94230f7de0	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	title_closed	false	2024-02-22 13:46:05.517+00
71aff67b-66a5-4bf6-8b7f-5a082cb76f20	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	description_closed	false	2024-02-22 13:46:05.518+00
c1a3a1a6-7ae1-436d-816f-dd5632b176ea	e8b5ae9d-e696-423d-8d8c-a5583faae6f8	language	English	2024-02-22 13:46:05.519+00
70b8aaea-f28f-4c83-80d9-63c1ee1cbc79	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	file_name	Remove.docx	2024-02-22 13:46:05.524+00
e2e4ce05-727c-4579-a6ae-41a6453ed485	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	file_type	File	2024-02-22 13:46:05.525+00
de17da65-c864-4ee9-96fc-39b9f14bf269	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	file_size	12609	2024-02-22 13:46:05.526+00
36ec839c-a756-486c-80d4-08276c908330	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	rights_copyright	Crown Copyright	2024-02-22 13:46:05.528+00
b0a01d7d-f65b-45bb-a559-e1558e9141a2	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	legal_status	Public Record(s)	2024-02-22 13:46:05.529+00
84de4302-5eef-4d27-8373-2a7c07b160d7	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	held_by	The National Archives, Kew	2024-02-22 13:46:05.53+00
09eb8e6b-3fc3-4507-a540-3e33dd1da4ad	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.531+00
3fac1e67-d911-4a37-ae5c-1f7790dae85a	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	closure_type	Open	2024-02-22 13:46:05.533+00
d4e04f98-4654-4198-bebb-20aa3a393c61	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	title_closed	false	2024-02-22 13:46:05.534+00
b8108502-e2e3-4682-ab75-795ad0ff9987	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	description_closed	false	2024-02-22 13:46:05.535+00
a73387f3-c3fa-4f26-9621-df9ae4d9a41f	df9bd5f6-0333-4742-bd2e-a479e0ac1c11	language	English	2024-02-22 13:46:05.536+00
201eb984-9ec1-4116-aee1-5d66c95db97f	268251a2-df75-46b5-ae1a-c1f29da62367	file_name	content	2024-02-22 13:46:05.541+00
ec4e72ed-d261-4c1d-a3c1-9b8ed279e6ed	268251a2-df75-46b5-ae1a-c1f29da62367	file_type	Folder	2024-02-22 13:46:05.543+00
5960765e-0b69-4895-862a-26adc6018246	268251a2-df75-46b5-ae1a-c1f29da62367	rights_copyright	Crown Copyright	2024-02-22 13:46:05.544+00
5afc66c9-f6c3-45c7-b245-9cef93c04ef7	268251a2-df75-46b5-ae1a-c1f29da62367	legal_status	Public Record(s)	2024-02-22 13:46:05.546+00
6b6e7729-facd-4fce-8584-bd40822d9f01	268251a2-df75-46b5-ae1a-c1f29da62367	held_by	The National Archives, Kew	2024-02-22 13:46:05.548+00
e41b49b6-62c0-453b-ac19-e49e0b694a73	268251a2-df75-46b5-ae1a-c1f29da62367	closure_type	Open	2024-02-22 13:46:05.549+00
09fd2415-13ba-4c6d-9a95-5e5a52a87e89	268251a2-df75-46b5-ae1a-c1f29da62367	title_closed	false	2024-02-22 13:46:05.55+00
e38d48b6-7fde-4377-adc0-73ba95dbef02	268251a2-df75-46b5-ae1a-c1f29da62367	description_closed	false	2024-02-22 13:46:05.551+00
906527f1-51e7-4377-93f9-8b262cd27929	268251a2-df75-46b5-ae1a-c1f29da62367	language	English	2024-02-22 13:46:05.552+00
64b19399-3b76-4c0f-bcec-2b948b938791	6e80512e-c881-4192-8d7b-4c8b7dcbecca	file_name	Emergency Response Team	2024-02-22 13:46:05.554+00
a0be80fa-6ecf-416b-abe1-c82e8b5fa7f2	6e80512e-c881-4192-8d7b-4c8b7dcbecca	file_type	Folder	2024-02-22 13:46:05.556+00
06ac2d14-f69b-4c00-a9bb-f5ffa1374102	6e80512e-c881-4192-8d7b-4c8b7dcbecca	rights_copyright	Crown Copyright	2024-02-22 13:46:05.557+00
58ba2e50-e17b-41e6-8882-2d6ac4cdebd8	6e80512e-c881-4192-8d7b-4c8b7dcbecca	legal_status	Public Record(s)	2024-02-22 13:46:05.558+00
536a8b98-f92b-4b25-8609-2b8176cb1d66	6e80512e-c881-4192-8d7b-4c8b7dcbecca	held_by	The National Archives, Kew	2024-02-22 13:46:05.559+00
d304de08-d47b-40db-a9cc-bd09c5207e0a	6e80512e-c881-4192-8d7b-4c8b7dcbecca	closure_type	Open	2024-02-22 13:46:05.56+00
a125aff6-055e-4351-a775-0a68cf50ed8f	6e80512e-c881-4192-8d7b-4c8b7dcbecca	title_closed	false	2024-02-22 13:46:05.561+00
364ff5ba-f2c9-4636-baf0-ddebec34e0a4	6e80512e-c881-4192-8d7b-4c8b7dcbecca	description_closed	false	2024-02-22 13:46:05.563+00
99dfb727-fae8-4b12-8997-ca2276c1b054	6e80512e-c881-4192-8d7b-4c8b7dcbecca	language	English	2024-02-22 13:46:05.564+00
ecfb9eaa-3d07-4a88-80a1-3a801d4c861d	99bff3d0-cc22-4082-b6b2-96daa763c5cc	file_name	DTP.docx	2024-02-22 13:46:05.567+00
f30d1f95-d501-42f2-b2b0-63589f9cb7e8	99bff3d0-cc22-4082-b6b2-96daa763c5cc	file_type	File	2024-02-22 13:46:05.568+00
bbae0d41-38d9-40a8-8584-9b131f46db0d	99bff3d0-cc22-4082-b6b2-96daa763c5cc	file_size	70263	2024-02-22 13:46:05.57+00
4b2626f3-a6b3-4361-9fb9-827e3773550c	99bff3d0-cc22-4082-b6b2-96daa763c5cc	rights_copyright	Crown Copyright	2024-02-22 13:46:05.572+00
cd8a2e4d-b068-442c-8aa6-e7a89cb4eab6	99bff3d0-cc22-4082-b6b2-96daa763c5cc	legal_status	Public Record(s)	2024-02-22 13:46:05.573+00
00885d46-8256-4e7a-8f5f-d22e679c94e4	99bff3d0-cc22-4082-b6b2-96daa763c5cc	held_by	The National Archives, Kew	2024-02-22 13:46:05.574+00
072b7fe4-fbda-40e3-91d0-72b5ebc09435	99bff3d0-cc22-4082-b6b2-96daa763c5cc	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.575+00
5e456284-a7cb-4c4c-9f76-e1bf464b39bf	99bff3d0-cc22-4082-b6b2-96daa763c5cc	closure_type	Open	2024-02-22 13:46:05.576+00
932d08bf-8f0f-4831-9511-802d7dfb8af0	99bff3d0-cc22-4082-b6b2-96daa763c5cc	title_closed	false	2024-02-22 13:46:05.578+00
f3a7832a-f1a9-4eed-9690-b75e78a125b1	99bff3d0-cc22-4082-b6b2-96daa763c5cc	description_closed	false	2024-02-22 13:46:05.579+00
3e0856e8-f647-4623-ae0a-45e1cc232766	99bff3d0-cc22-4082-b6b2-96daa763c5cc	language	English	2024-02-22 13:46:05.58+00
847c7e37-ac6f-4de3-8207-fb12d3590d4c	ec2ba87e-fb29-409f-82f5-b5419a4a8672	file_name	Workflows	2024-02-22 13:46:05.585+00
b82f45f8-fc01-47b8-924b-2a59fff2ad9d	ec2ba87e-fb29-409f-82f5-b5419a4a8672	file_type	Folder	2024-02-22 13:46:05.586+00
17c20c6a-707c-49fd-9555-9eb06b240ca1	ec2ba87e-fb29-409f-82f5-b5419a4a8672	rights_copyright	Crown Copyright	2024-02-22 13:46:05.587+00
741fe24e-ac4a-4841-836c-6d802caa933f	ec2ba87e-fb29-409f-82f5-b5419a4a8672	legal_status	Public Record(s)	2024-02-22 13:46:05.588+00
712f1a44-8f3d-4434-8769-48b170771106	ec2ba87e-fb29-409f-82f5-b5419a4a8672	held_by	The National Archives, Kew	2024-02-22 13:46:05.589+00
753e47e7-3b05-4754-8cbd-2a9199dd908c	ec2ba87e-fb29-409f-82f5-b5419a4a8672	closure_type	Open	2024-02-22 13:46:05.59+00
091c7592-8f6b-4ecd-8093-3e276cf1cf49	ec2ba87e-fb29-409f-82f5-b5419a4a8672	title_closed	false	2024-02-22 13:46:05.591+00
d36fa3dd-4297-4153-996d-babbbc556dc4	ec2ba87e-fb29-409f-82f5-b5419a4a8672	description_closed	false	2024-02-22 13:46:05.593+00
4b4f4ca8-a543-47af-a0e0-8c6b80d5bb0c	ec2ba87e-fb29-409f-82f5-b5419a4a8672	language	English	2024-02-22 13:46:05.594+00
e6890939-44c7-4da6-9371-3c74d503fe23	56dce91b-7850-4708-a0f3-5c64bf00f350	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-22 13:46:05.596+00
7ec1e14e-2331-46a1-9a47-eedf7b777fb3	56dce91b-7850-4708-a0f3-5c64bf00f350	file_type	File	2024-02-22 13:46:05.598+00
2ad1d9f5-bd56-467d-aab6-f3545422dbd4	56dce91b-7850-4708-a0f3-5c64bf00f350	file_size	177875	2024-02-22 13:46:05.599+00
e97aca0e-0749-4845-a921-fa552e6f64ff	56dce91b-7850-4708-a0f3-5c64bf00f350	rights_copyright	Crown Copyright	2024-02-22 13:46:05.6+00
48336f33-87a3-406c-ad36-a897705ba000	56dce91b-7850-4708-a0f3-5c64bf00f350	legal_status	Public Record(s)	2024-02-22 13:46:05.602+00
37e572a2-6176-42f8-a66b-6835d2694472	56dce91b-7850-4708-a0f3-5c64bf00f350	held_by	The National Archives, Kew	2024-02-22 13:46:05.603+00
75ec8c89-9a97-4b9b-9244-3b752ae704d8	56dce91b-7850-4708-a0f3-5c64bf00f350	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.604+00
2a4aa715-896c-4416-a64b-d3d5fe66c5b7	56dce91b-7850-4708-a0f3-5c64bf00f350	closure_type	Open	2024-02-22 13:46:05.611+00
77d9ae53-78f8-4373-a762-db44f5db745a	56dce91b-7850-4708-a0f3-5c64bf00f350	title_closed	false	2024-02-22 13:46:05.613+00
c599319c-6966-4e3b-af67-75c727b9024b	56dce91b-7850-4708-a0f3-5c64bf00f350	description_closed	false	2024-02-22 13:46:05.616+00
49e379f9-a92e-415e-8ee8-3af1a6d53557	56dce91b-7850-4708-a0f3-5c64bf00f350	language	English	2024-02-22 13:46:05.617+00
f8dcfd29-7583-4033-89e9-5b0eabd01b75	505060b5-aac2-4422-b663-6a825da1902a	file_name	Presentation.pptx	2024-02-22 13:46:05.622+00
03e068fc-a927-431e-afc2-dced4f11c3bd	505060b5-aac2-4422-b663-6a825da1902a	file_type	File	2024-02-22 13:46:05.623+00
7d05505b-98b3-425d-bf3e-730e67e2159b	505060b5-aac2-4422-b663-6a825da1902a	file_size	697817	2024-02-22 13:46:05.624+00
2d291bbd-4bb2-4f4f-be36-a080bc4e7f60	505060b5-aac2-4422-b663-6a825da1902a	rights_copyright	Crown Copyright	2024-02-22 13:46:05.626+00
629e2e62-221c-4c40-b2b1-72d38ccc8704	505060b5-aac2-4422-b663-6a825da1902a	legal_status	Public Record(s)	2024-02-22 13:46:05.627+00
308f0eaf-6a66-416d-b899-f4e50ccd4ed5	505060b5-aac2-4422-b663-6a825da1902a	held_by	The National Archives, Kew	2024-02-22 13:46:05.628+00
11d8a7e5-062f-4c9e-8feb-3fd9b242196f	505060b5-aac2-4422-b663-6a825da1902a	date_last_modified	2022-07-18T00:00:00	2024-02-22 13:46:05.629+00
6fea1394-b136-4ef6-9fa8-a57f04eb36a4	505060b5-aac2-4422-b663-6a825da1902a	closure_type	Open	2024-02-22 13:46:05.63+00
f8bfee29-6d8b-480a-a27d-4a2f2a27c563	505060b5-aac2-4422-b663-6a825da1902a	title_closed	false	2024-02-22 13:46:05.631+00
f0112fc1-499e-4c42-8758-d3398e28b140	505060b5-aac2-4422-b663-6a825da1902a	description_closed	false	2024-02-22 13:46:05.632+00
7fbe62e7-6924-4e3c-a88f-ed325835ebda	505060b5-aac2-4422-b663-6a825da1902a	language	English	2024-02-22 13:46:05.633+00
e0a8d261-7f90-4b97-8cca-f066aa39f6a6	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	file_name	Gateways.ppt	2024-02-22 15:28:24.705+00
789b095c-af70-4f35-969f-e9ffa7495a4f	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	file_type	File	2024-02-22 15:28:24.707+00
ae210399-d28d-4563-962e-77acd696a2ac	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	file_size	446464	2024-02-22 15:28:24.709+00
369d41d1-b7d0-486a-975b-7c6c05c6ec5d	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	rights_copyright	Crown Copyright	2024-02-22 15:28:24.711+00
2c36f1bf-664f-4a7a-bd8e-182a95e5f133	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	legal_status	Public Record(s)	2024-02-22 15:28:24.713+00
0b80b2d0-24e2-4f0f-8fbb-e3e6e142d3c6	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	held_by	The National Archives, Kew	2024-02-22 15:28:24.715+00
d4d868f1-20a3-4c04-a80c-ed82f120cbae	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.717+00
9b972886-0b1a-468a-b448-fddccca00dbf	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	closure_type	Open	2024-02-22 15:28:24.718+00
52e70786-1a6e-4a9d-b478-341e110892c8	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	title_closed	false	2024-02-22 15:28:24.72+00
bef799e0-5a42-440d-943e-3159e0ee4768	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	description_closed	false	2024-02-22 15:28:24.721+00
ac4dfdb9-bc69-496a-8d96-5fb2e4525f86	62f41529-b22a-4eae-bb05-2ce5ddc6fb70	language	English	2024-02-22 15:28:24.722+00
05508976-77f9-4168-a9bb-ef6c463a69a6	569d6988-a40f-41d8-904b-179d4ae29931	file_name	Emergency Response Team	2024-02-22 15:28:24.73+00
e7e2805f-cd44-4119-a362-7ab3d04c9e84	569d6988-a40f-41d8-904b-179d4ae29931	file_type	Folder	2024-02-22 15:28:24.731+00
7a4e5b9c-dfc1-424d-98f9-6d7b0dac7c3f	569d6988-a40f-41d8-904b-179d4ae29931	rights_copyright	Crown Copyright	2024-02-22 15:28:24.732+00
66203599-9af7-4cf8-b61f-3e7e4025da15	569d6988-a40f-41d8-904b-179d4ae29931	legal_status	Public Record(s)	2024-02-22 15:28:24.734+00
92022f2e-1376-4506-89b3-f48076116afe	569d6988-a40f-41d8-904b-179d4ae29931	held_by	The National Archives, Kew	2024-02-22 15:28:24.736+00
3381f68d-9ecc-488e-a6bc-47031c27461c	569d6988-a40f-41d8-904b-179d4ae29931	closure_type	Open	2024-02-22 15:28:24.738+00
6283923e-c652-46d7-98f7-0378dc29f31a	569d6988-a40f-41d8-904b-179d4ae29931	title_closed	false	2024-02-22 15:28:24.739+00
ce9ecbca-b847-4628-85a8-a698ff2f87be	569d6988-a40f-41d8-904b-179d4ae29931	description_closed	false	2024-02-22 15:28:24.743+00
4b8b3d9b-bb2e-45b1-bec0-fa476214b05c	569d6988-a40f-41d8-904b-179d4ae29931	language	English	2024-02-22 15:28:24.744+00
29836ebf-840e-4fbf-8eed-576fee85f83c	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	file_name	Response Procedure.docx	2024-02-22 15:28:24.748+00
e8b493ba-598f-43e8-8360-d71b95ae0b0e	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	file_type	File	2024-02-22 15:28:24.749+00
50e5f314-6637-4805-80a5-ad456248167b	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	file_size	12610	2024-02-22 15:28:24.75+00
05195507-589d-4708-a89e-e3dd02f2808e	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	rights_copyright	Crown Copyright	2024-02-22 15:28:24.752+00
77bc0804-ca8e-4afd-9fe9-7552db15f5d0	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	legal_status	Public Record(s)	2024-02-22 15:28:24.753+00
15383bdf-0c84-4ca2-adcf-3e15bd254311	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	held_by	The National Archives, Kew	2024-02-22 15:28:24.755+00
a749618a-ea38-4df0-b9e7-2c487efa15af	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.756+00
d1f0db00-a669-4890-b1e4-89bfd8e0c2fd	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	closure_type	Open	2024-02-22 15:28:24.757+00
baeab2b8-c6e0-431b-bf28-004b2ae1a2cd	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	title_closed	false	2024-02-22 15:28:24.759+00
5023a798-468b-4563-bd23-402b048d8bff	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	description_closed	false	2024-02-22 15:28:24.76+00
1faddd6d-4052-447a-bf9f-3abfd5718b94	9a0f9b40-b9d4-4269-8c2d-272adb1bab5c	language	English	2024-02-22 15:28:24.763+00
99dc2b4a-9d76-489f-b5b3-06cc10cd519b	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	file_name	nord-lead-viewer.mxf	2024-02-22 15:28:24.77+00
45383c33-dd26-4b76-9ae8-a388d98c209c	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	file_type	File	2024-02-22 15:28:24.771+00
e70f7631-8d79-446d-b6fb-d60061601211	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	file_size	1179295	2024-02-22 15:28:24.773+00
897e53d3-97f3-4e7c-b44e-b24b493e9813	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	rights_copyright	Crown Copyright	2024-02-22 15:28:24.774+00
d1f0d837-2887-4f72-afbc-ee25308a3c38	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	legal_status	Public Record(s)	2024-02-22 15:28:24.776+00
9ff81c0d-20d5-42cb-acfd-2677eb25d78a	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	held_by	The National Archives, Kew	2024-02-22 15:28:24.777+00
79587c37-6638-4fb7-98e7-e6876b635617	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.778+00
f7023a17-5a40-4f9d-80d2-f86dd2ad024d	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	closure_type	Open	2024-02-22 15:28:24.779+00
797d9a4b-8a36-4a92-8364-614d44e96b72	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	title_closed	false	2024-02-22 15:28:24.78+00
16ba64ce-baac-4c7f-81ac-549f203eec1e	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	description_closed	false	2024-02-22 15:28:24.782+00
14ff54e1-bb15-43ac-babc-faf265b1233d	062b8e3c-c6ca-4df3-9ef2-909a72b59d78	language	English	2024-02-22 15:28:24.783+00
d889ff7b-002e-4727-9a7c-743a3032d5b4	baba5d37-db25-40ea-b94c-81cc68ff580f	file_name	DTP_ Digital Transfer process diagram v 6.docx	2024-02-22 15:28:24.79+00
52f36941-8d95-4c4c-baec-a516e1e25916	baba5d37-db25-40ea-b94c-81cc68ff580f	file_type	File	2024-02-22 15:28:24.791+00
1d6330fd-bb23-4d54-95fa-e75b3d6e3e90	baba5d37-db25-40ea-b94c-81cc68ff580f	file_size	70263	2024-02-22 15:28:24.793+00
8778090e-7ce6-421c-8d71-db0e8a7f39b7	baba5d37-db25-40ea-b94c-81cc68ff580f	rights_copyright	Crown Copyright	2024-02-22 15:28:24.794+00
48e77728-2ce6-4a8b-bf3b-20c57816e2ea	baba5d37-db25-40ea-b94c-81cc68ff580f	legal_status	Public Record(s)	2024-02-22 15:28:24.795+00
2deae223-c28a-4009-bb1b-700d20170902	baba5d37-db25-40ea-b94c-81cc68ff580f	held_by	The National Archives, Kew	2024-02-22 15:28:24.796+00
b59958bd-c769-4123-a0b5-88d88ad15e9d	baba5d37-db25-40ea-b94c-81cc68ff580f	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.797+00
a6afa9fc-5749-48b5-8259-3bd45e1ab4dd	baba5d37-db25-40ea-b94c-81cc68ff580f	closure_type	Open	2024-02-22 15:28:24.799+00
52e0379c-f969-489b-a6ff-859c6b55c2d8	baba5d37-db25-40ea-b94c-81cc68ff580f	title_closed	false	2024-02-22 15:28:24.8+00
e37efb17-c316-4c7c-8ce6-bf8c470b1e03	baba5d37-db25-40ea-b94c-81cc68ff580f	description_closed	false	2024-02-22 15:28:24.801+00
8c7a35c0-59ac-466a-8866-bb854f441754	baba5d37-db25-40ea-b94c-81cc68ff580f	language	English	2024-02-22 15:28:24.802+00
f870cd91-1a45-45eb-8be6-6a956c93b53e	898aab0b-e0bc-424b-b885-15d13578eea5	file_name	Thumbs.db	2024-02-22 15:28:24.808+00
ea83749f-aa5d-422f-8912-fe0c6dff1bda	898aab0b-e0bc-424b-b885-15d13578eea5	file_type	File	2024-02-22 15:28:24.809+00
aa8fe0f2-9dba-4510-b220-17a32accf390	898aab0b-e0bc-424b-b885-15d13578eea5	file_size	685124	2024-02-22 15:28:24.811+00
71a0c34e-3b55-44ba-9035-3bbf6ce10aa7	898aab0b-e0bc-424b-b885-15d13578eea5	rights_copyright	Crown Copyright	2024-02-22 15:28:24.812+00
51e3961b-08d6-4264-a989-bca2b15b1dd0	898aab0b-e0bc-424b-b885-15d13578eea5	legal_status	Public Record(s)	2024-02-22 15:28:24.813+00
d11c0850-ec7f-4e1c-a376-b474da9ec480	898aab0b-e0bc-424b-b885-15d13578eea5	held_by	The National Archives, Kew	2024-02-22 15:28:24.814+00
20489a06-1d08-40e1-a518-6b0b0b8587d1	898aab0b-e0bc-424b-b885-15d13578eea5	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.816+00
71943f8b-161a-408e-bff4-8b88ba853c3d	898aab0b-e0bc-424b-b885-15d13578eea5	closure_type	Open	2024-02-22 15:28:24.817+00
a6e6d54e-c9e3-42f4-86fd-a12113aa558f	898aab0b-e0bc-424b-b885-15d13578eea5	title_closed	false	2024-02-22 15:28:24.819+00
c1dc6341-ced6-4b75-aec4-ff7b8bd75f26	898aab0b-e0bc-424b-b885-15d13578eea5	description_closed	false	2024-02-22 15:28:24.82+00
78000473-1317-46f9-9f89-e76c6ba7921d	898aab0b-e0bc-424b-b885-15d13578eea5	language	English	2024-02-22 15:28:24.821+00
949e18e2-4cb2-4916-8aaf-7fae690976e4	1afdc98f-410b-4071-9369-5406ebbf3fd6	file_name	delivery-form-digital.doc	2024-02-22 15:28:24.828+00
dc9eb73e-276f-4fa2-89e0-448612bc49f5	1afdc98f-410b-4071-9369-5406ebbf3fd6	file_type	File	2024-02-22 15:28:24.83+00
e54a3f1e-c0c0-4574-8602-0bc6557442f9	1afdc98f-410b-4071-9369-5406ebbf3fd6	file_size	139776	2024-02-22 15:28:24.831+00
1252c755-2f98-4f02-b3f7-57f99004e4f3	1afdc98f-410b-4071-9369-5406ebbf3fd6	rights_copyright	Crown Copyright	2024-02-22 15:28:24.832+00
90f221ea-89f2-445c-9a61-63eb43ba4e11	1afdc98f-410b-4071-9369-5406ebbf3fd6	legal_status	Public Record(s)	2024-02-22 15:28:24.833+00
977223c3-17e9-40b0-9473-b0329981be30	1afdc98f-410b-4071-9369-5406ebbf3fd6	held_by	The National Archives, Kew	2024-02-22 15:28:24.834+00
f9526fec-0e8b-4247-b776-2213c7f5766f	1afdc98f-410b-4071-9369-5406ebbf3fd6	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.835+00
87db31a3-360e-4b9f-9e5a-50e953a7d5b5	1afdc98f-410b-4071-9369-5406ebbf3fd6	closure_type	Open	2024-02-22 15:28:24.836+00
2f30f0f3-13b8-4f9c-baa4-a9404e5bc1ca	1afdc98f-410b-4071-9369-5406ebbf3fd6	title_closed	false	2024-02-22 15:28:24.837+00
e22e8ae0-c0a6-45b9-a2ff-2192cde6dc09	1afdc98f-410b-4071-9369-5406ebbf3fd6	description_closed	false	2024-02-22 15:28:24.838+00
de1310b0-8f2b-4bcc-bb90-d5e3915fa1f7	1afdc98f-410b-4071-9369-5406ebbf3fd6	language	English	2024-02-22 15:28:24.84+00
88a032f1-69a0-4023-a00b-4c1652ca53c8	21373a76-9a68-4881-8df7-c17f574b9874	file_name	DTP.docx	2024-02-22 15:28:24.849+00
1474f6d6-4b11-4dcb-a3e8-918e72cdafef	21373a76-9a68-4881-8df7-c17f574b9874	file_type	File	2024-02-22 15:28:24.856+00
da4ed4d0-59b6-4637-8893-9d438b12b34b	21373a76-9a68-4881-8df7-c17f574b9874	file_size	70263	2024-02-22 15:28:24.861+00
74705210-3faf-4089-97a0-7f0d1465e7dc	21373a76-9a68-4881-8df7-c17f574b9874	rights_copyright	Crown Copyright	2024-02-22 15:28:24.863+00
9ebd138a-8411-4262-a862-3a254dca87ae	21373a76-9a68-4881-8df7-c17f574b9874	legal_status	Public Record(s)	2024-02-22 15:28:24.866+00
072aadd8-bad3-4b9a-a5b4-b800925b1741	21373a76-9a68-4881-8df7-c17f574b9874	held_by	The National Archives, Kew	2024-02-22 15:28:24.867+00
27e82e5c-b571-4b4c-a672-28f760147aee	21373a76-9a68-4881-8df7-c17f574b9874	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.869+00
fe615cf5-6132-4567-b6e0-91e7266742fc	21373a76-9a68-4881-8df7-c17f574b9874	closure_type	Open	2024-02-22 15:28:24.871+00
77529778-9013-4ece-b2f5-a48dcc6706c5	21373a76-9a68-4881-8df7-c17f574b9874	title_closed	false	2024-02-22 15:28:24.873+00
87a70964-82d9-4632-bb21-95ab673597fb	21373a76-9a68-4881-8df7-c17f574b9874	description_closed	false	2024-02-22 15:28:24.878+00
8ca24d46-3e14-40e2-98f4-cd52846d3b04	21373a76-9a68-4881-8df7-c17f574b9874	language	English	2024-02-22 15:28:24.879+00
a55d05db-2b39-45a9-bf61-e357b2892408	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	file_name	DTP_ Digital Transfer process diagram UG.docx	2024-02-22 15:28:24.886+00
8c20f7b7-46d5-41b9-b0bc-cf00c9002a93	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	file_type	File	2024-02-22 15:28:24.888+00
8d68ee3e-ee36-4a22-8496-c5781e6c0123	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	file_size	68364	2024-02-22 15:28:24.889+00
993d8675-fcbe-4e41-9c5d-3bae72b9bf2c	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	rights_copyright	Crown Copyright	2024-02-22 15:28:24.892+00
b36595ca-c936-4976-a2aa-e5a0a1cb821d	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	legal_status	Public Record(s)	2024-02-22 15:28:24.893+00
25d46387-ba5c-4c6b-afd5-31979680795c	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	held_by	The National Archives, Kew	2024-02-22 15:28:24.895+00
79004c55-b8f0-4364-836c-a8c167e3973f	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.896+00
916246c7-8159-4c31-b02b-f6c4e038ff5e	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	closure_type	Open	2024-02-22 15:28:24.897+00
b198cdd0-abea-4a6e-a795-79ec50396ec5	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	title_closed	false	2024-02-22 15:28:24.901+00
74caffbf-51cd-43e2-8d2c-86e07e3f9249	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	description_closed	false	2024-02-22 15:28:24.902+00
3fe398f3-0cbc-450a-afd5-c079f5b623e3	c0ec5bf3-c8b6-41e0-90d7-2ffe95dd22e0	language	English	2024-02-22 15:28:24.904+00
a5f2ad78-4e99-4d58-b883-5645d6f89e4e	0280dca5-97e5-42de-9b9b-4ed673bf8b86	file_name	base_de_donnees.png	2024-02-22 15:28:24.909+00
2d870ed3-6a5e-457e-a21f-69826a14e0df	0280dca5-97e5-42de-9b9b-4ed673bf8b86	file_type	File	2024-02-22 15:28:24.91+00
5644d790-7b8c-4331-a81b-07652927bc6c	0280dca5-97e5-42de-9b9b-4ed673bf8b86	file_size	165098	2024-02-22 15:28:24.912+00
75555157-10c4-4555-a304-61d1e6fcc7f5	0280dca5-97e5-42de-9b9b-4ed673bf8b86	rights_copyright	Crown Copyright	2024-02-22 15:28:24.913+00
51ca04f6-730b-4a70-b7b1-6a903331f45e	0280dca5-97e5-42de-9b9b-4ed673bf8b86	legal_status	Public Record(s)	2024-02-22 15:28:24.918+00
e6467768-0a60-4c58-ad3a-0b6508d8cb53	0280dca5-97e5-42de-9b9b-4ed673bf8b86	held_by	The National Archives, Kew	2024-02-22 15:28:24.922+00
efab51f6-ee7d-4f05-97e7-f0523ea7ede5	0280dca5-97e5-42de-9b9b-4ed673bf8b86	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.924+00
1a46d378-27e7-4d4e-a1aa-b0b9f5a56580	0280dca5-97e5-42de-9b9b-4ed673bf8b86	closure_type	Open	2024-02-22 15:28:24.925+00
4443c3b3-353f-45ea-a8e8-f11df13abf2b	0280dca5-97e5-42de-9b9b-4ed673bf8b86	title_closed	false	2024-02-22 15:28:24.926+00
878decbc-0a22-430b-bac8-85793f6a4974	0280dca5-97e5-42de-9b9b-4ed673bf8b86	description_closed	false	2024-02-22 15:28:24.928+00
47359364-7af9-45c3-aad7-888523c819ac	0280dca5-97e5-42de-9b9b-4ed673bf8b86	language	English	2024-02-22 15:28:24.929+00
5ad63ff9-ac37-414d-b661-e5f331c0c53c	2440bcc9-439b-4735-8183-45da8658614a	file_name	Response Policy.docx	2024-02-22 15:28:24.934+00
d8331f91-c6ee-46f0-b23f-e731d5c18fc7	2440bcc9-439b-4735-8183-45da8658614a	file_type	File	2024-02-22 15:28:24.935+00
b277369b-2196-48b6-b055-844ac6270e43	2440bcc9-439b-4735-8183-45da8658614a	file_size	12651	2024-02-22 15:28:24.936+00
16620e67-5c3f-4e42-af3a-46844a2bf913	2440bcc9-439b-4735-8183-45da8658614a	rights_copyright	Crown Copyright	2024-02-22 15:28:24.938+00
fdcca72b-3c43-41b0-a13f-3671c4901c98	2440bcc9-439b-4735-8183-45da8658614a	legal_status	Public Record(s)	2024-02-22 15:28:24.939+00
79c579fb-2110-4234-bacc-f2c9295d11e0	2440bcc9-439b-4735-8183-45da8658614a	held_by	The National Archives, Kew	2024-02-22 15:28:24.94+00
721b0787-1f93-42aa-963c-59e5cb8ec72f	2440bcc9-439b-4735-8183-45da8658614a	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.941+00
41935d24-a848-4d31-be3f-2189308ca887	2440bcc9-439b-4735-8183-45da8658614a	closure_type	Open	2024-02-22 15:28:24.944+00
70fd35f4-666d-47a4-bd4a-0f85709296bd	2440bcc9-439b-4735-8183-45da8658614a	title_closed	false	2024-02-22 15:28:24.945+00
8205e9c4-7a5d-4f62-945a-9f70c7ac153e	2440bcc9-439b-4735-8183-45da8658614a	description_closed	false	2024-02-22 15:28:24.946+00
02d78b93-3643-4975-92bd-db74dbcbd4a2	2440bcc9-439b-4735-8183-45da8658614a	language	English	2024-02-22 15:28:24.947+00
de9ac8e5-2c04-452c-9b31-0b1e15c4286a	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	file_name	content	2024-02-22 15:28:24.951+00
97931cef-43d0-4aec-bdb3-6820cf5ca3c2	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	file_type	Folder	2024-02-22 15:28:24.952+00
0d0c05f2-d254-4479-aea2-b519880cf0e4	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	rights_copyright	Crown Copyright	2024-02-22 15:28:24.954+00
fc1bc59b-eff4-4a1f-95db-2000ec72c14a	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	legal_status	Public Record(s)	2024-02-22 15:28:24.956+00
c840f37c-3a02-4432-88df-b0a7ad7e938d	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	held_by	The National Archives, Kew	2024-02-22 15:28:24.957+00
f0e6e568-5102-46b3-8c49-b4491aa8adb3	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	closure_type	Open	2024-02-22 15:28:24.959+00
d97d77d0-bacf-4786-b4ce-ad190793eec5	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	title_closed	false	2024-02-22 15:28:24.96+00
00c990ab-1ed0-4e7f-ad2a-8d9374366a7c	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	description_closed	false	2024-02-22 15:28:24.961+00
71d15735-4d10-4871-b2d4-43cbfcb8bf4c	3ae2e688-e5c7-44f7-a8f2-6a3a052bebfc	language	English	2024-02-22 15:28:24.962+00
41d2b583-f6ea-4307-a4eb-f11b5ed55170	03ebf08f-ad7b-4036-ba66-774071d6ea29	file_name	Remove.docx	2024-02-22 15:28:24.973+00
0b1bf4ad-086e-4b89-b31b-030cad04bc62	03ebf08f-ad7b-4036-ba66-774071d6ea29	file_type	File	2024-02-22 15:28:24.975+00
75da5640-7614-4013-bcf4-66f1189a3862	03ebf08f-ad7b-4036-ba66-774071d6ea29	file_size	12609	2024-02-22 15:28:24.976+00
de67eb24-7fd0-4488-ad85-47ce62fc8db7	03ebf08f-ad7b-4036-ba66-774071d6ea29	rights_copyright	Crown Copyright	2024-02-22 15:28:24.977+00
6dc8e6f6-08f3-439c-a640-cb6461181ac4	03ebf08f-ad7b-4036-ba66-774071d6ea29	legal_status	Public Record(s)	2024-02-22 15:28:24.978+00
5bb1ea66-458f-495b-9984-6f4ad4403b46	03ebf08f-ad7b-4036-ba66-774071d6ea29	held_by	The National Archives, Kew	2024-02-22 15:28:24.979+00
3fa0acda-1f73-4bc3-aec1-1759ac6ef39b	03ebf08f-ad7b-4036-ba66-774071d6ea29	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:24.981+00
9e6ce732-44fe-4ca8-bf5c-bd306d5830f0	03ebf08f-ad7b-4036-ba66-774071d6ea29	closure_type	Open	2024-02-22 15:28:24.982+00
e43e9874-5917-48ae-9b7b-7f83ad4f44cd	03ebf08f-ad7b-4036-ba66-774071d6ea29	title_closed	false	2024-02-22 15:28:24.983+00
5a95a610-6f50-443f-94e1-d7836d2c98c8	03ebf08f-ad7b-4036-ba66-774071d6ea29	description_closed	false	2024-02-22 15:28:24.985+00
780157cc-6b92-4475-9d11-496d375c3fed	03ebf08f-ad7b-4036-ba66-774071d6ea29	language	English	2024-02-22 15:28:24.986+00
6e8d6558-431c-45c0-b3c5-2a7d3ff95f09	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	file_name	Presentation.pptx	2024-02-22 15:28:24.997+00
14e44388-9315-4e31-82f6-968a37e59b9b	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	file_type	File	2024-02-22 15:28:24.998+00
a671194e-c8af-46b5-843b-6628dfbdb942	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	file_size	697817	2024-02-22 15:28:25.002+00
5c20a975-e2aa-4941-abd3-71505fa675c9	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	rights_copyright	Crown Copyright	2024-02-22 15:28:25.008+00
b8c9ce88-652c-46ec-836a-e39d26f78868	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	legal_status	Public Record(s)	2024-02-22 15:28:25.009+00
ac2f435d-8b51-4162-8085-e5f23c429bc8	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	held_by	The National Archives, Kew	2024-02-22 15:28:25.011+00
b7898a89-aeef-477f-a419-816d00113dc6	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:25.012+00
77625b8c-0f4f-4806-894a-aeba486581d4	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	closure_type	Open	2024-02-22 15:28:25.013+00
a12e99e2-52ed-422a-8063-da6602bcea18	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	title_closed	false	2024-02-22 15:28:25.014+00
1871ac39-62da-48c9-810f-bde1c5a80eea	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	description_closed	false	2024-02-22 15:28:25.015+00
6bc61ffb-cfde-4520-8e05-80614a2fbae9	b749cdb8-04b0-4fc1-a3f5-b26bd203aa5a	language	English	2024-02-22 15:28:25.016+00
62223a87-e8eb-4235-a252-4e2ad3d7698a	738262e7-5e16-433d-9c26-030a713aba2a	file_name	Workflows	2024-02-22 15:28:25.021+00
cb830b42-8184-4731-8126-aab2ac590b1f	738262e7-5e16-433d-9c26-030a713aba2a	file_type	Folder	2024-02-22 15:28:25.024+00
17f195a3-f1ca-4279-a10d-c2c50ffe6054	738262e7-5e16-433d-9c26-030a713aba2a	rights_copyright	Crown Copyright	2024-02-22 15:28:25.025+00
374244d9-9801-43a6-9006-4a4d71d90a66	738262e7-5e16-433d-9c26-030a713aba2a	legal_status	Public Record(s)	2024-02-22 15:28:25.026+00
1e56b266-960f-4048-9333-0eb5b20dbe35	738262e7-5e16-433d-9c26-030a713aba2a	held_by	The National Archives, Kew	2024-02-22 15:28:25.027+00
0119bccf-7a0b-468e-9855-f9c5086b8119	738262e7-5e16-433d-9c26-030a713aba2a	closure_type	Open	2024-02-22 15:28:25.029+00
6284d1d6-7537-409b-bb29-a232222d3220	738262e7-5e16-433d-9c26-030a713aba2a	title_closed	false	2024-02-22 15:28:25.03+00
70f041d0-0589-437c-ab24-e01d1f493e1b	738262e7-5e16-433d-9c26-030a713aba2a	description_closed	false	2024-02-22 15:28:25.031+00
5b62da1d-5fed-4056-b7e0-fcca614a702f	738262e7-5e16-433d-9c26-030a713aba2a	language	English	2024-02-22 15:28:25.032+00
00da909a-cc8e-40e4-b07a-f8e1393304df	4f663ad9-80a8-46ee-a465-babc4bbd3470	file_name	Digital Transfer training email .msg	2024-02-22 15:28:25.034+00
60d6ac5e-6e01-4dc8-a4fc-d686d1b7f8d7	4f663ad9-80a8-46ee-a465-babc4bbd3470	file_type	File	2024-02-22 15:28:25.035+00
6d42ceb2-1547-41c0-926d-17f32e1db20e	4f663ad9-80a8-46ee-a465-babc4bbd3470	file_size	39424	2024-02-22 15:28:25.037+00
48e4619c-bc61-4235-a28b-21a835cd3955	4f663ad9-80a8-46ee-a465-babc4bbd3470	rights_copyright	Crown Copyright	2024-02-22 15:28:25.038+00
a9d339d2-b93f-471e-b177-29179ac68bd0	4f663ad9-80a8-46ee-a465-babc4bbd3470	legal_status	Public Record(s)	2024-02-22 15:28:25.041+00
71e61e8c-bfb9-40fa-a082-62fe75ff7030	4f663ad9-80a8-46ee-a465-babc4bbd3470	held_by	The National Archives, Kew	2024-02-22 15:28:25.042+00
ff6660b3-0e21-441a-8707-c90e3c11f97c	4f663ad9-80a8-46ee-a465-babc4bbd3470	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:25.043+00
4a62ffff-13dc-40fc-8892-68e30f07f29d	4f663ad9-80a8-46ee-a465-babc4bbd3470	closure_type	Open	2024-02-22 15:28:25.044+00
1d0baecb-5b58-4705-a2bb-4c7c4d7c8e7c	4f663ad9-80a8-46ee-a465-babc4bbd3470	title_closed	false	2024-02-22 15:28:25.045+00
e1cbb451-c7d9-4131-a831-21ffc0d99dc7	4f663ad9-80a8-46ee-a465-babc4bbd3470	description_closed	false	2024-02-22 15:28:25.046+00
be81724b-3393-4916-8ee9-e8e999b8ceae	4f663ad9-80a8-46ee-a465-babc4bbd3470	language	English	2024-02-22 15:28:25.048+00
2396aa1d-15bc-4536-8c22-2df83dba1600	b7728c35-3e92-4177-9114-4a4b6d084f56	file_name	tech_acq_metadata_vmUNKNOWN-VERSION-NUMBER_tmtsample01.csv	2024-02-22 15:28:25.053+00
adee0df0-be01-40a3-9a50-9a376a613ef2	b7728c35-3e92-4177-9114-4a4b6d084f56	file_type	File	2024-02-22 15:28:25.054+00
55589252-6ac5-40c0-b9c2-43823b11aaa0	b7728c35-3e92-4177-9114-4a4b6d084f56	file_size	177875	2024-02-22 15:28:25.056+00
2a1c9ea4-cbb7-4d35-8d90-6073aafe999f	b7728c35-3e92-4177-9114-4a4b6d084f56	rights_copyright	Crown Copyright	2024-02-22 15:28:25.057+00
55405d91-de2a-4722-bab6-4adbed292cb3	b7728c35-3e92-4177-9114-4a4b6d084f56	legal_status	Public Record(s)	2024-02-22 15:28:25.058+00
bdd051f7-3704-4482-99c3-b45d945496b9	b7728c35-3e92-4177-9114-4a4b6d084f56	held_by	The National Archives, Kew	2024-02-22 15:28:25.059+00
cf7e7751-fd63-4128-b4cc-8f0ed3fc80c9	b7728c35-3e92-4177-9114-4a4b6d084f56	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:25.06+00
271ac1b7-30d2-4b7c-b1ca-040d2e3edf5e	b7728c35-3e92-4177-9114-4a4b6d084f56	closure_type	Open	2024-02-22 15:28:25.061+00
508d87cb-6431-4c8a-b5b2-9c52d50ce4a4	b7728c35-3e92-4177-9114-4a4b6d084f56	title_closed	false	2024-02-22 15:28:25.063+00
7f504fab-5fe0-45c2-a1e9-8b8d82b39a29	b7728c35-3e92-4177-9114-4a4b6d084f56	description_closed	false	2024-02-22 15:28:25.064+00
4da2ce6c-50d4-4667-afdc-14d5b6d405ef	b7728c35-3e92-4177-9114-4a4b6d084f56	language	English	2024-02-22 15:28:25.065+00
6cc34ac5-faa6-4dee-aff9-b1d2876c8cb2	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	file_name	Emergency Contact Details Paul Young.docx	2024-02-22 15:28:25.07+00
855819d0-0162-4c73-96f9-84cb3b1c30c6	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	file_type	File	2024-02-22 15:28:25.071+00
d6d1a9dc-c463-4760-aad4-e66fcfa2fa72	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	file_size	12825	2024-02-22 15:28:25.072+00
52001c76-8aed-4a12-8cba-e12229661b89	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	rights_copyright	Crown Copyright	2024-02-22 15:28:25.073+00
452a2572-fb96-47b9-baed-567925523421	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	legal_status	Public Record(s)	2024-02-22 15:28:25.074+00
3de267b3-1e41-4e57-8a5c-2f821c2f575a	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	held_by	The National Archives, Kew	2024-02-22 15:28:25.076+00
b94d37d9-37b6-44a4-a6d7-b4bd7d5926e3	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:25.077+00
b022803e-b3b1-41ae-9f4f-42d22caaa9f5	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	closure_type	Open	2024-02-22 15:28:25.078+00
2e107ce2-5369-4d17-a88a-85dbc8f79e8b	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	title_closed	false	2024-02-22 15:28:25.079+00
2faa88fb-bd02-4f6e-9488-bbcef03c2b76	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	description_closed	false	2024-02-22 15:28:25.08+00
30d734ec-863f-49fe-b8f3-c31d474c5160	c6b9dc8b-6eb2-4f48-bbad-b91e9205ff66	language	English	2024-02-22 15:28:25.081+00
74c8ef55-df1d-4d73-98bb-673cba1b09b0	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	file_name	Draft DDRO 05.docx	2024-02-22 15:28:25.086+00
2131c84a-387a-470a-9a5e-0d95900cfd81	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	file_type	File	2024-02-22 15:28:25.087+00
a0cc089f-9315-417d-ad7f-3072a9c32c9f	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	file_size	21707	2024-02-22 15:28:25.088+00
2dee176c-936a-4c2d-a9d4-636d2be88cd6	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	rights_copyright	Crown Copyright	2024-02-22 15:28:25.089+00
2357aec5-06ab-4209-84f4-76fd9c80042d	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	legal_status	Public Record(s)	2024-02-22 15:28:25.09+00
5c709ef8-ff26-465c-9659-5f6b653eb283	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	held_by	The National Archives, Kew	2024-02-22 15:28:25.092+00
6309e8ca-5166-4dad-96f7-7f40c3164ab8	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:25.095+00
db805803-8374-453d-8e98-54acb9778352	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	closure_type	Open	2024-02-22 15:28:25.096+00
a20015e2-4559-40df-aa62-d8a794a84c8e	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	title_closed	false	2024-02-22 15:28:25.098+00
dfa4d467-2cd4-423a-9632-fb8e88d80681	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	description_closed	false	2024-02-22 15:28:25.099+00
867db56f-53db-4bf0-af84-d8ec8963e532	c2d8cb01-d4ea-4cb2-9268-e8e1a5ad0f2d	language	English	2024-02-22 15:28:25.101+00
fb83bea6-89a2-449e-9a0d-d78ecc63a520	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	file_name	DTP_ Sensitivity review process.docx	2024-02-22 15:28:25.105+00
a9b0c726-362a-42de-9bc4-8c9b60df9772	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	file_type	File	2024-02-22 15:28:25.106+00
06f017ed-76b5-4779-9792-7d7e5cadac9f	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	file_size	70674	2024-02-22 15:28:25.107+00
3e574502-d73d-4e61-9b6f-6edc71008e78	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	rights_copyright	Crown Copyright	2024-02-22 15:28:25.109+00
27c5151f-81e9-4319-a34d-2001c340bcd1	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	legal_status	Public Record(s)	2024-02-22 15:28:25.11+00
19d33868-844a-4c16-aa2b-a236176a4160	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	held_by	The National Archives, Kew	2024-02-22 15:28:25.111+00
a3d85f07-c579-4546-b59c-90aaba3ae684	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	date_last_modified	2022-07-18T00:00:00	2024-02-22 15:28:25.112+00
315fa1bc-8fbc-4734-a586-1c0c24d7071d	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	closure_type	Open	2024-02-22 15:28:25.113+00
364bc79e-8605-49be-814f-3095fa248548	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	title_closed	false	2024-02-22 15:28:25.114+00
37eec65b-5a78-4032-b6d4-1f1ea4f85049	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	description_closed	false	2024-02-22 15:28:25.115+00
290bb0dc-459f-4696-b340-24a5b19b37ad	78ec383b-1d3d-4c2d-8469-5d5f62b7300a	language	English	2024-02-22 15:28:25.117+00
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
\.


--
-- Data for Name: Series; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."Series" ("SeriesId", "BodyId", "Name", "Description") FROM stdin;
8bd7ad22-90d1-4c7f-ae00-645dfd1987cc	8ccc8cd1-c0ee-431d-afad-70cf404ba337	MOCK1 123	MOCK1 123
1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7	c3e3fd83-4d52-4638-a085-1f4e4e4dfa50	TSTA 1	TSTA 1
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
