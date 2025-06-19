--
-- PostgreSQL database dump
--

-- Dumped from database version 11.18 (Debian 11.18-0+deb10u1)
-- Dumped by pg_dump version 17.4

-- Started on 2025-06-19 18:19:59

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
-- TOC entry 6 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 240 (class 1255 OID 22574)
-- Name: get_price_detail(character varying, character varying); Type: FUNCTION; Schema: public; Owner: main
--

CREATE FUNCTION public.get_price_detail(group_id_param character varying, channel_param character varying) RETURNS TABLE(sold_price numeric, total_qty bigint, total_revenue numeric, total_gross_profit numeric)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.soldprice AS sold_price,
        SUM(s.qty) AS total_qty,
        ROUND(SUM(
            CASE 
                WHEN s.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                ELSE s.soldprice * s.qty
            END
        ), 2) AS total_revenue,
        ROUND(SUM(
            CASE 
                WHEN s.tax = 1 THEN ((s.soldprice / 1.2) - s.cost::NUMERIC) * s.qty
                ELSE (s.soldprice - s.cost::NUMERIC) * s.qty
            END
        ), 2) AS total_gross_profit
    FROM sales s
    WHERE s.groupid = group_id_param
      AND s.channel = channel_param
    GROUP BY s.soldprice
    ORDER BY sold_price DESC;
END;
$$;


ALTER FUNCTION public.get_price_detail(group_id_param character varying, channel_param character varying) OWNER TO main;

--
-- TOC entry 253 (class 1255 OID 22575)
-- Name: get_recent_incoming_stock(); Type: FUNCTION; Schema: public; Owner: main
--

CREATE FUNCTION public.get_recent_incoming_stock() RETURNS TABLE(groupid character varying, code character varying, created_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.groupid, 
        i.code, 
        i.created_at
    FROM incoming_stock i
    WHERE i.created_at >= CURRENT_DATE - INTERVAL '8 days'
    ORDER BY i.created_at DESC;
END;
$$;


ALTER FUNCTION public.get_recent_incoming_stock() OWNER TO main;

--
-- TOC entry 254 (class 1255 OID 22576)
-- Name: groupid_summary_performance(); Type: FUNCTION; Schema: public; Owner: main
--

CREATE FUNCTION public.groupid_summary_performance() RETURNS TABLE(supplier character varying, groupid character varying, net_sales_qty numeric, revenue numeric, total_cost numeric, gross_profit numeric)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH sales_data AS (
        SELECT
            s.groupid,
            SUM(s.qty)::NUMERIC AS net_sales_qty, -- Explicitly cast SUM to NUMERIC
            SUM(
                CASE 
                    WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                    ELSE s.soldprice * s.qty
                END
            ) AS total_revenue
        FROM sales s
        JOIN skusummary ss ON s.groupid = ss.groupid
        GROUP BY s.groupid, ss.tax
    )
    SELECT
        ss.supplier::VARCHAR(100), -- Cast supplier to VARCHAR(100)
        sd.groupid::VARCHAR(100),  -- Cast groupid to VARCHAR(100)
        sd.net_sales_qty,
        ROUND(sd.total_revenue, 2) AS revenue,
        ROUND(COALESCE(ss.cost::NUMERIC, 0) * ABS(sd.net_sales_qty), 2) AS total_cost,
        ROUND(
            sd.total_revenue - (COALESCE(ss.cost::NUMERIC, 0) * ABS(sd.net_sales_qty)),
            2
        ) AS gross_profit
    FROM sales_data sd
    JOIN skusummary ss ON sd.groupid = ss.groupid
    ORDER BY gross_profit DESC;
END;
$$;


ALTER FUNCTION public.groupid_summary_performance() OWNER TO main;

--
-- TOC entry 255 (class 1255 OID 22577)
-- Name: groupid_summary_performance_90(); Type: FUNCTION; Schema: public; Owner: main
--

CREATE FUNCTION public.groupid_summary_performance_90() RETURNS TABLE(supplier character varying, groupid character varying, net_sales_qty numeric, revenue numeric, total_cost numeric, gross_profit numeric)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    WITH sales_data AS (
        SELECT
            s.groupid,
            SUM(s.qty)::NUMERIC AS net_sales_qty, -- Explicitly cast SUM to NUMERIC
            SUM(
                CASE 
                    WHEN ss.tax = 1 THEN (s.soldprice / 1.2) * s.qty
                    ELSE s.soldprice * s.qty
                END
            ) AS total_revenue
        FROM sales s
        JOIN skusummary ss ON s.groupid = ss.groupid
        WHERE s.solddate >= CURRENT_DATE - INTERVAL '90 days' -- Filter for the last 90 days
        GROUP BY s.groupid, ss.tax
    )
    SELECT
        ss.supplier::VARCHAR(100), -- Cast supplier to VARCHAR(100)
        sd.groupid::VARCHAR(100),  -- Cast groupid to VARCHAR(100)
        sd.net_sales_qty,
        ROUND(sd.total_revenue, 2) AS revenue,
        ROUND(COALESCE(ss.cost::NUMERIC, 0) * ABS(sd.net_sales_qty), 2) AS total_cost,
        ROUND(
            sd.total_revenue - (COALESCE(ss.cost::NUMERIC, 0) * ABS(sd.net_sales_qty)),
            2
        ) AS gross_profit
    FROM sales_data sd
    JOIN skusummary ss ON sd.groupid = ss.groupid
    ORDER BY gross_profit DESC;
END;
$$;


ALTER FUNCTION public.groupid_summary_performance_90() OWNER TO main;

SET default_tablespace = '';

--
-- TOC entry 196 (class 1259 OID 22578)
-- Name: amzfeed; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.amzfeed (
    sku character varying(50) NOT NULL,
    fnsku character varying(50),
    groupid character varying(50),
    code character varying(50) NOT NULL,
    fbafee character varying(50),
    asin character varying(50),
    amzreturn integer,
    amzsold integer,
    amzsoldprice character varying(10),
    amzsolddate character varying(30),
    amzprice character varying(10),
    amztotal integer,
    amzlive integer,
    amzsold7 integer,
    buybox character varying(10)
);


ALTER TABLE public.amzfeed OWNER TO brookfield_prod_user;

--
-- TOC entry 197 (class 1259 OID 22581)
-- Name: amzshipment; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.amzshipment (
    box integer NOT NULL,
    supplier character varying(50),
    code character varying(50),
    sku character varying(50) NOT NULL,
    fnsku character varying(50),
    qty integer,
    weight character varying(10),
    length character varying(10),
    height character varying(10),
    width character varying(10)
);


ALTER TABLE public.amzshipment OWNER TO brookfield_prod_user;

--
-- TOC entry 198 (class 1259 OID 22584)
-- Name: amzshipment_archive; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.amzshipment_archive (
    box integer,
    supplier character varying(50),
    code character varying(50),
    sku character varying(50),
    fnsku character varying(50),
    qty integer,
    created_at timestamp without time zone DEFAULT now(),
    id integer,
    weight character varying(10),
    length character varying(10),
    height character varying(10),
    width character varying(10)
);


ALTER TABLE public.amzshipment_archive OWNER TO brookfield_prod_user;

--
-- TOC entry 199 (class 1259 OID 22588)
-- Name: amzstockreport; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.amzstockreport (
    sku character varying(100) NOT NULL,
    fnsku character varying(20),
    title character varying(200),
    groupid character varying(50),
    code character varying(50) NOT NULL,
    supplier character varying(30),
    minlocal integer,
    localstock integer,
    ukd integer,
    amztotal integer,
    amzlive integer,
    sold integer,
    return integer,
    profit character varying(10),
    floor character varying(10),
    rrp character varying(10),
    price character varying(10),
    soldprice character varying(10),
    roi character varying(10),
    solddate character varying(20),
    inamazon integer,
    barcode character varying(20),
    season character varying(10),
    cost character varying(10),
    netsold integer,
    shopify integer,
    created character varying(20),
    pfgstock integer
);


ALTER TABLE public.amzstockreport OWNER TO brookfield_prod_user;

--
-- TOC entry 200 (class 1259 OID 22594)
-- Name: attributes; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.attributes (
    groupid character varying(100) NOT NULL,
    updated character varying(30),
    gender character varying(20),
    producttype character varying(100),
    tag1 character varying(50),
    tag2 character varying(50),
    tag3 character varying(50),
    tag4 character varying(50),
    tag5 character varying(50),
    tag6 character varying(50),
    tag7 character varying(50),
    tag8 character varying(50),
    tag9 character varying(50),
    tag10 character varying(50),
    alt character varying(50)
);


ALTER TABLE public.attributes OWNER TO brookfield_prod_user;

--
-- TOC entry 201 (class 1259 OID 22600)
-- Name: bclog; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.bclog (
    id integer NOT NULL,
    workstation character varying(50) NOT NULL,
    log character varying(500),
    section character varying(50),
    date date,
    "time" character varying(10),
    created_at timestamp with time zone
);


ALTER TABLE public.bclog OWNER TO brookfield_prod_user;

--
-- TOC entry 202 (class 1259 OID 22606)
-- Name: bclog_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE public.bclog ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.bclog_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 203 (class 1259 OID 22608)
-- Name: birkstock; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.birkstock (
    groupid character varying(100) NOT NULL,
    style character varying(50),
    material character varying(50),
    width character varying(50),
    colour character varying(50),
    link character varying(200),
    size35 smallint,
    size35order smallint,
    size36 smallint,
    size36order smallint,
    size37 smallint,
    size37order smallint,
    size38 smallint,
    size38order smallint,
    size39 smallint,
    size39order smallint,
    size40 smallint,
    size40order smallint,
    size41 smallint,
    size41order smallint,
    size42 smallint,
    size42order smallint,
    size43 smallint,
    size43order smallint,
    size44 smallint,
    size44order smallint,
    size45 smallint,
    size45order smallint,
    size46 smallint,
    size46order smallint,
    title character varying(200)
);


ALTER TABLE public.birkstock OWNER TO brookfield_prod_user;

--
-- TOC entry 204 (class 1259 OID 22614)
-- Name: birktracker; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.birktracker (
    code character varying(100) NOT NULL,
    ordernum character varying(100) NOT NULL,
    placedate character varying(20),
    bksize character varying(20),
    requested integer,
    invoiced integer,
    arrived integer,
    invoicedate character varying(20),
    invoicenum character varying(20),
    justarrived integer,
    rrp character varying(10),
    cost character varying(10),
    colouralt integer,
    due character varying(20),
    ean character varying(20)
);


ALTER TABLE public.birktracker OWNER TO brookfield_prod_user;

--
-- TOC entry 205 (class 1259 OID 22617)
-- Name: brand; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.brand (
    brand character varying(50) NOT NULL,
    supplier character varying(50)
);


ALTER TABLE public.brand OWNER TO brookfield_prod_user;

--
-- TOC entry 206 (class 1259 OID 22620)
-- Name: campaign; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.campaign (
    title character varying(50) NOT NULL,
    budget character varying(10),
    roas character varying(10),
    id character varying(10) NOT NULL,
    items bigint,
    troas character varying(10),
    startdate date
);


ALTER TABLE public.campaign OWNER TO brookfield_prod_user;

--
-- TOC entry 207 (class 1259 OID 22623)
-- Name: category; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.category (
    id integer NOT NULL,
    categoryname character varying(50),
    gender character varying(20),
    brand character varying(100),
    producttype character varying(100),
    onbuy character varying(200),
    tiktok character varying(200)
);


ALTER TABLE public.category OWNER TO brookfield_prod_user;

--
-- TOC entry 208 (class 1259 OID 22629)
-- Name: colour; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.colour (
    colour character varying(50) NOT NULL
);


ALTER TABLE public.colour OWNER TO brookfield_prod_user;

--
-- TOC entry 209 (class 1259 OID 22632)
-- Name: grouplabel; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.grouplabel (
    label character varying(50),
    code character varying(20) NOT NULL
);


ALTER TABLE public.grouplabel OWNER TO brookfield_prod_user;

--
-- TOC entry 210 (class 1259 OID 22635)
-- Name: incoming_stock; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.incoming_stock (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    groupid character varying(100) NOT NULL,
    arrival_date date NOT NULL,
    quantity_added integer NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    target character varying(50),
    workstation character varying(50)
);


ALTER TABLE public.incoming_stock OWNER TO brookfield_prod_user;

--
-- TOC entry 211 (class 1259 OID 22640)
-- Name: incoming_stock_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.incoming_stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.incoming_stock_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3183 (class 0 OID 0)
-- Dependencies: 211
-- Name: incoming_stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.incoming_stock_id_seq OWNED BY public.incoming_stock.id;


--
-- TOC entry 212 (class 1259 OID 22642)
-- Name: inivalues; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.inivalues (
    attribute character varying(100) NOT NULL,
    value character varying(100) NOT NULL
);


ALTER TABLE public.inivalues OWNER TO brookfield_prod_user;

--
-- TOC entry 213 (class 1259 OID 22645)
-- Name: localstock; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.localstock (
    id character varying(100) NOT NULL,
    updated character varying(50),
    ordernum character varying(100),
    location character varying(100),
    groupid character varying(100),
    code character varying(100),
    supplier character varying(100),
    qty integer,
    brand character varying(100),
    deleted integer,
    assigned character varying(20),
    pickorder integer,
    allocated character varying(50)
);


ALTER TABLE public.localstock OWNER TO brookfield_prod_user;

--
-- TOC entry 214 (class 1259 OID 22652)
-- Name: location; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.location (
    updated character varying(30),
    location character varying(50) NOT NULL,
    anypicks character varying(10),
    barcode character varying(20) NOT NULL,
    pickorder integer
);


ALTER TABLE public.location OWNER TO brookfield_prod_user;

--
-- TOC entry 215 (class 1259 OID 22655)
-- Name: offlinesold; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.offlinesold (
    id character varying(30) NOT NULL,
    location character varying(30),
    code character varying(50),
    orderdate date,
    groupid character varying(50),
    qty integer,
    ordertime character varying(10),
    soldprice numeric(5,2),
    collectedvat numeric(5,2),
    paytype character varying(10)
);


ALTER TABLE public.offlinesold OWNER TO brookfield_prod_user;

--
-- TOC entry 216 (class 1259 OID 22658)
-- Name: orderstatus; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.orderstatus (
    ordernum character varying(100) NOT NULL,
    shopifysku character varying(50) NOT NULL,
    qty integer,
    updated character varying(50),
    created character varying(50),
    batch character varying(10),
    supplier character varying(50),
    title character varying(200),
    shippingname character varying(100),
    postcode character varying(20),
    address1 character varying(200),
    address2 character varying(200),
    company character varying(100),
    city character varying(100),
    county character varying(100),
    country character varying(100),
    phone character varying(50),
    shippingnotes character varying(200),
    orderdate character varying(50),
    ukd integer,
    localstock integer,
    amz integer,
    othersupplier integer,
    fnsku character varying(20),
    weight character varying(10),
    pickedqty integer,
    email character varying(100),
    courier character varying(100),
    courierfixed integer,
    customerwaiting integer,
    notorderamz integer,
    alloworder integer,
    searchalt character varying(50),
    channel character varying(50),
    picknotfound integer,
    fbaordered character varying(20),
    notes character varying(255),
    shopcustomer integer,
    shippingcost character varying(20),
    ordertype integer,
    ponumber character varying(50),
    createddate date,
    arrived smallint,
    arriveddate date
);


ALTER TABLE public.orderstatus OWNER TO brookfield_prod_user;

--
-- TOC entry 238 (class 1259 OID 23994)
-- Name: pickpin; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.pickpin (
    pin integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.pickpin OWNER TO brookfield_prod_user;

--
-- TOC entry 237 (class 1259 OID 23992)
-- Name: pickpin_pin_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.pickpin_pin_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pickpin_pin_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3184 (class 0 OID 0)
-- Dependencies: 237
-- Name: pickpin_pin_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.pickpin_pin_seq OWNED BY public.pickpin.pin;


--
-- TOC entry 239 (class 1259 OID 24011)
-- Name: price_track; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.price_track (
    groupid character varying(100) NOT NULL,
    date date NOT NULL,
    brand character varying(100),
    amazon_stock integer,
    amazon_sales integer DEFAULT 0,
    amazon_avg_sold_price numeric(10,2),
    amazon_price numeric(10,2),
    shopify_stock integer,
    shopify_sales integer DEFAULT 0,
    shopify_avg_sold_price numeric(10,2),
    shopify_price numeric(10,2)
);


ALTER TABLE public.price_track OWNER TO brookfield_prod_user;

--
-- TOC entry 217 (class 1259 OID 22664)
-- Name: productlink; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.productlink (
    groupid character varying(50) NOT NULL,
    updated date
);


ALTER TABLE public.productlink OWNER TO brookfield_prod_user;

--
-- TOC entry 218 (class 1259 OID 22667)
-- Name: producttype; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.producttype (
    producttype character varying(50) NOT NULL
);


ALTER TABLE public.producttype OWNER TO brookfield_prod_user;

--
-- TOC entry 219 (class 1259 OID 22670)
-- Name: sales; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.sales (
    id integer NOT NULL,
    code character varying(50),
    solddate date,
    groupid character varying(50),
    ordernum character varying(50),
    ordertime character varying(20),
    qty integer,
    soldprice numeric(5,2),
    channel character varying(20),
    paytype character varying(20),
    collectedvat numeric(5,2),
    productname character varying(200),
    returnsaleid character varying(20),
    brand character varying(50),
    profit numeric(5,2) DEFAULT 0,
    discount integer
);


ALTER TABLE public.sales OWNER TO brookfield_prod_user;

--
-- TOC entry 220 (class 1259 OID 22677)
-- Name: sales_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.sales_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sales_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3185 (class 0 OID 0)
-- Dependencies: 220
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.sales_id_seq OWNED BY public.sales.id;


--
-- TOC entry 221 (class 1259 OID 22679)
-- Name: shopifyimages; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.shopifyimages (
    handle character varying(200) NOT NULL,
    imagepos smallint NOT NULL,
    imagesrc character varying(200)
);


ALTER TABLE public.shopifyimages OWNER TO brookfield_prod_user;

--
-- TOC entry 222 (class 1259 OID 22682)
-- Name: shopifysnapshot; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.shopifysnapshot (
    groupid character varying(100),
    code character varying(100) NOT NULL,
    stock integer,
    price character varying(10)
);


ALTER TABLE public.shopifysnapshot OWNER TO brookfield_prod_user;

--
-- TOC entry 223 (class 1259 OID 22685)
-- Name: shopifysold; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.shopifysold (
    id character varying(30) NOT NULL,
    code character varying(50),
    solddate date,
    groupid character varying(50),
    ordernum character varying(50),
    ordertime character varying(20),
    qty integer,
    soldprice character varying(10)
);


ALTER TABLE public.shopifysold OWNER TO brookfield_prod_user;

--
-- TOC entry 224 (class 1259 OID 22688)
-- Name: shopprices; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.shopprices (
    groupid character varying(50) NOT NULL,
    price character varying(10),
    location character varying(50),
    rrp character varying(10),
    changed integer,
    label character varying(20)
);


ALTER TABLE public.shopprices OWNER TO brookfield_prod_user;

--
-- TOC entry 225 (class 1259 OID 22691)
-- Name: skumap; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.skumap (
    sku character varying(50),
    updated character varying(30),
    groupid character varying(50) NOT NULL,
    variantlink character varying(20),
    optionsize character varying(100),
    uksize character varying(30),
    eurosize character varying(20),
    ean character varying(20),
    code character varying(50) NOT NULL,
    googleid character varying(100),
    googlestatus integer,
    search2 character varying(20),
    status character varying(10),
    notes character varying(200),
    cost character varying(10),
    tax integer,
    fba character varying(10),
    soldprice character varying(10),
    amzprice character varying(10),
    floor character varying(10),
    msp character varying(10),
    supplier character varying(30),
    nextdelivery character varying(20),
    deleted integer,
    minstock integer,
    weight character varying(10),
    amzreturn integer,
    amzsold integer,
    amzsoldprice character varying(10),
    amzsolddate character varying(20),
    googleadstatus character varying(20),
    amzminprice character varying(10),
    amzperformance integer,
    shelf integer,
    shopifyprice character varying(10),
    reportgroup_a character varying(50),
    reportgroup_b character varying(50),
    reportgroup_c character varying(50),
    reportgroup_d character varying(50),
    shopifyminprice character varying(10),
    amzmaxprice character varying(10),
    shopifymaxprice character varying(10),
    pricestatus integer,
    googlecampaign character varying(10),
    amzprofit character varying(10),
    tiktokskuid character varying(20),
    amzallow character varying(20),
    amz365 integer,
    shp365 integer,
    amzfeatureprice character varying(10),
    shopifynotes character varying(200),
    shopifyreplenstatus character varying(10),
    localreserve integer,
    order365 integer,
    amzorderdate2 date,
    fbafee numeric(5,2),
    amzrank integer,
    amzstorage numeric(5,2),
    cmb365 integer,
    stockcheck_class character varying(10),
    stockcheck_date date,
    amzrequest integer,
    amzpickrequest integer
);


ALTER TABLE public.skumap OWNER TO brookfield_prod_user;

--
-- TOC entry 226 (class 1259 OID 22697)
-- Name: skusummary; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.skusummary (
    groupid character varying(50) NOT NULL,
    updated character varying(30),
    shopify integer,
    googlestatus integer,
    colour character varying(20),
    colourmap character varying(20),
    variants integer,
    stockvariants integer,
    handle character varying(300),
    supplier character varying(30),
    brand character varying(30),
    notes character varying(200),
    rrp character varying(10),
    season character varying(10),
    imagename character varying(200),
    custom_label_0 character varying(200),
    custom_label_1 character varying(200),
    custom_label_2 character varying(200),
    custom_label_3 character varying(200),
    custom_label_4 character varying(200),
    created character varying(20),
    karen integer,
    tiktokshop integer,
    googlecampaign character varying(20),
    shopifyprice character varying(10),
    tiktokshopid character varying(20),
    minshopifyprice character varying(10),
    cost character varying(10),
    maxshopifyprice character varying(10),
    lowbench character varying(10),
    highbench character varying(10),
    insights character varying(10),
    birkcore integer,
    noukd integer,
    troas numeric(5,2),
    cmpbudget numeric(5,2),
    tax integer,
    shopifychange integer,
    width character varying(20),
    regular_groupid character varying(50),
    narrow_groupid character varying(50),
    material character varying(50),
    usereport integer DEFAULT 1
);


ALTER TABLE public.skusummary OWNER TO brookfield_prod_user;

--
-- TOC entry 227 (class 1259 OID 22704)
-- Name: stockorder; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.stockorder (
    id character varying(30) NOT NULL,
    code character varying(50),
    orderdate date,
    groupid character varying(50),
    qty integer,
    cost character varying(10)
);


ALTER TABLE public.stockorder OWNER TO brookfield_prod_user;

--
-- TOC entry 228 (class 1259 OID 22707)
-- Name: supplier; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.supplier (
    supplier character varying(100)
);


ALTER TABLE public.supplier OWNER TO brookfield_prod_user;

--
-- TOC entry 229 (class 1259 OID 22710)
-- Name: taglist; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.taglist (
    tag character varying(100) NOT NULL
);


ALTER TABLE public.taglist OWNER TO brookfield_prod_user;

--
-- TOC entry 230 (class 1259 OID 22713)
-- Name: title; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.title (
    groupid character varying(100) NOT NULL,
    updated character varying(30),
    shopifytitle character varying(200),
    googletitle character varying(150),
    googletitleb character varying(150)
);


ALTER TABLE public.title OWNER TO brookfield_prod_user;

--
-- TOC entry 231 (class 1259 OID 22719)
-- Name: ukdstock; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.ukdstock (
    groupid character varying(100) NOT NULL,
    code character varying(50) NOT NULL,
    stock integer,
    prevstock integer
);


ALTER TABLE public.ukdstock OWNER TO brookfield_prod_user;

--
-- TOC entry 232 (class 1259 OID 22722)
-- Name: weekly_stock_levels; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.weekly_stock_levels (
    id integer NOT NULL,
    groupid character varying(100) NOT NULL,
    week_start_date date NOT NULL,
    opening_stock integer NOT NULL,
    purchases integer DEFAULT 0,
    sales integer DEFAULT 0,
    returns integer DEFAULT 0,
    closing_stock integer NOT NULL,
    notes character varying(200)
);


ALTER TABLE public.weekly_stock_levels OWNER TO brookfield_prod_user;

--
-- TOC entry 233 (class 1259 OID 22728)
-- Name: weekly_stock_levels_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.weekly_stock_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.weekly_stock_levels_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3186 (class 0 OID 0)
-- Dependencies: 233
-- Name: weekly_stock_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.weekly_stock_levels_id_seq OWNED BY public.weekly_stock_levels.id;


--
-- TOC entry 234 (class 1259 OID 22730)
-- Name: winner_channels; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.winner_channels (
    id integer NOT NULL,
    groupid character varying(100) NOT NULL,
    channel character varying(10) NOT NULL
);


ALTER TABLE public.winner_channels OWNER TO brookfield_prod_user;

--
-- TOC entry 235 (class 1259 OID 22733)
-- Name: winner_channels_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.winner_channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.winner_channels_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3187 (class 0 OID 0)
-- Dependencies: 235
-- Name: winner_channels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.winner_channels_id_seq OWNED BY public.winner_channels.id;


--
-- TOC entry 236 (class 1259 OID 22735)
-- Name: winner_products; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.winner_products (
    groupid character varying(100) NOT NULL,
    priority character varying(10),
    start_date date NOT NULL,
    end_date date,
    notes text,
    CONSTRAINT winner_products_priority_check CHECK (((priority)::text = ANY (ARRAY[('High'::character varying)::text, ('Medium'::character varying)::text, ('Low'::character varying)::text])))
);


ALTER TABLE public.winner_products OWNER TO brookfield_prod_user;

--
-- TOC entry 2953 (class 2604 OID 22742)
-- Name: incoming_stock id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.incoming_stock ALTER COLUMN id SET DEFAULT nextval('public.incoming_stock_id_seq'::regclass);


--
-- TOC entry 2964 (class 2604 OID 23997)
-- Name: pickpin pin; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.pickpin ALTER COLUMN pin SET DEFAULT nextval('public.pickpin_pin_seq'::regclass);


--
-- TOC entry 2956 (class 2604 OID 22743)
-- Name: sales id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.sales ALTER COLUMN id SET DEFAULT nextval('public.sales_id_seq'::regclass);


--
-- TOC entry 2959 (class 2604 OID 22744)
-- Name: weekly_stock_levels id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.weekly_stock_levels ALTER COLUMN id SET DEFAULT nextval('public.weekly_stock_levels_id_seq'::regclass);


--
-- TOC entry 2963 (class 2604 OID 22745)
-- Name: winner_channels id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.winner_channels ALTER COLUMN id SET DEFAULT nextval('public.winner_channels_id_seq'::regclass);


--
-- TOC entry 2969 (class 2606 OID 22747)
-- Name: amzfeed amzfeed_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.amzfeed
    ADD CONSTRAINT amzfeed_pkey PRIMARY KEY (code);


--
-- TOC entry 2971 (class 2606 OID 22749)
-- Name: amzshipment amzshipment_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.amzshipment
    ADD CONSTRAINT amzshipment_pkey PRIMARY KEY (box, sku);


--
-- TOC entry 2973 (class 2606 OID 22751)
-- Name: amzstockreport amzstockreport_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.amzstockreport
    ADD CONSTRAINT amzstockreport_pkey PRIMARY KEY (code);


--
-- TOC entry 2975 (class 2606 OID 22753)
-- Name: attributes attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.attributes
    ADD CONSTRAINT attributes_pkey PRIMARY KEY (groupid);


--
-- TOC entry 2977 (class 2606 OID 22755)
-- Name: bclog bclog_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.bclog
    ADD CONSTRAINT bclog_pkey PRIMARY KEY (id);


--
-- TOC entry 2979 (class 2606 OID 22757)
-- Name: birkstock birkstock_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.birkstock
    ADD CONSTRAINT birkstock_primary PRIMARY KEY (groupid);


--
-- TOC entry 2981 (class 2606 OID 22759)
-- Name: birktracker birktracker_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.birktracker
    ADD CONSTRAINT birktracker_primary PRIMARY KEY (code, ordernum);


--
-- TOC entry 2983 (class 2606 OID 22761)
-- Name: brand brand_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.brand
    ADD CONSTRAINT brand_pkey PRIMARY KEY (brand);


--
-- TOC entry 2985 (class 2606 OID 22763)
-- Name: campaign campaign_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.campaign
    ADD CONSTRAINT campaign_pkey PRIMARY KEY (id);


--
-- TOC entry 2987 (class 2606 OID 22765)
-- Name: category category_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_primary PRIMARY KEY (id);


--
-- TOC entry 2989 (class 2606 OID 22767)
-- Name: colour colour_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.colour
    ADD CONSTRAINT colour_pkey PRIMARY KEY (colour);


--
-- TOC entry 2991 (class 2606 OID 22769)
-- Name: grouplabel grouplabel_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.grouplabel
    ADD CONSTRAINT grouplabel_pkey PRIMARY KEY (code);


--
-- TOC entry 2997 (class 2606 OID 22771)
-- Name: localstock id_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.localstock
    ADD CONSTRAINT id_pkey PRIMARY KEY (id);


--
-- TOC entry 2993 (class 2606 OID 22773)
-- Name: incoming_stock incoming_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.incoming_stock
    ADD CONSTRAINT incoming_stock_pkey PRIMARY KEY (id);


--
-- TOC entry 2995 (class 2606 OID 22775)
-- Name: inivalues inivalues_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.inivalues
    ADD CONSTRAINT inivalues_pkey PRIMARY KEY (attribute);


--
-- TOC entry 3002 (class 2606 OID 22777)
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (barcode);


--
-- TOC entry 3004 (class 2606 OID 22779)
-- Name: offlinesold offlinesold_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.offlinesold
    ADD CONSTRAINT offlinesold_pkey PRIMARY KEY (id);


--
-- TOC entry 3006 (class 2606 OID 22781)
-- Name: orderstatus orderstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.orderstatus
    ADD CONSTRAINT orderstatus_pkey PRIMARY KEY (ordernum, shopifysku);


--
-- TOC entry 3052 (class 2606 OID 24002)
-- Name: pickpin pickpin_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.pickpin
    ADD CONSTRAINT pickpin_pkey PRIMARY KEY (pin);


--
-- TOC entry 3054 (class 2606 OID 24017)
-- Name: price_track price_track_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.price_track
    ADD CONSTRAINT price_track_pkey PRIMARY KEY (groupid, date);


--
-- TOC entry 3008 (class 2606 OID 22783)
-- Name: productlink productlink_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.productlink
    ADD CONSTRAINT productlink_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3010 (class 2606 OID 22785)
-- Name: producttype producttype_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.producttype
    ADD CONSTRAINT producttype_pkey PRIMARY KEY (producttype);


--
-- TOC entry 3017 (class 2606 OID 22787)
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- TOC entry 3019 (class 2606 OID 22789)
-- Name: shopifyimages shopifyimages_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopifyimages
    ADD CONSTRAINT shopifyimages_primary PRIMARY KEY (handle, imagepos);


--
-- TOC entry 3021 (class 2606 OID 22791)
-- Name: shopifysnapshot shopifysnapshot_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopifysnapshot
    ADD CONSTRAINT shopifysnapshot_primary PRIMARY KEY (code);


--
-- TOC entry 3023 (class 2606 OID 22793)
-- Name: shopifysold shopifysold_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopifysold
    ADD CONSTRAINT shopifysold_pkey PRIMARY KEY (id);


--
-- TOC entry 3025 (class 2606 OID 22795)
-- Name: shopprices shopprices_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopprices
    ADD CONSTRAINT shopprices_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3030 (class 2606 OID 22797)
-- Name: skumap skumap_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.skumap
    ADD CONSTRAINT skumap_pkey PRIMARY KEY (code);


--
-- TOC entry 3033 (class 2606 OID 22799)
-- Name: skusummary skusummary_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.skusummary
    ADD CONSTRAINT skusummary_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3035 (class 2606 OID 22801)
-- Name: stockorder stockorder_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.stockorder
    ADD CONSTRAINT stockorder_pkey PRIMARY KEY (id);


--
-- TOC entry 3037 (class 2606 OID 22803)
-- Name: taglist taglist_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.taglist
    ADD CONSTRAINT taglist_pkey PRIMARY KEY (tag);


--
-- TOC entry 3039 (class 2606 OID 22805)
-- Name: title title_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.title
    ADD CONSTRAINT title_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3041 (class 2606 OID 22807)
-- Name: ukdstock ukdstock_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.ukdstock
    ADD CONSTRAINT ukdstock_pkey PRIMARY KEY (code);


--
-- TOC entry 3046 (class 2606 OID 22809)
-- Name: winner_channels unique_groupid_channel; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.winner_channels
    ADD CONSTRAINT unique_groupid_channel UNIQUE (groupid, channel);


--
-- TOC entry 3044 (class 2606 OID 22811)
-- Name: weekly_stock_levels weekly_stock_levels_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.weekly_stock_levels
    ADD CONSTRAINT weekly_stock_levels_pkey PRIMARY KEY (id);


--
-- TOC entry 3048 (class 2606 OID 22813)
-- Name: winner_channels winner_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.winner_channels
    ADD CONSTRAINT winner_channels_pkey PRIMARY KEY (id);


--
-- TOC entry 3050 (class 2606 OID 22815)
-- Name: winner_products winner_products_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.winner_products
    ADD CONSTRAINT winner_products_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3042 (class 1259 OID 22816)
-- Name: idx_groupid_week; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_groupid_week ON public.weekly_stock_levels USING btree (groupid, week_start_date);


--
-- TOC entry 2998 (class 1259 OID 22817)
-- Name: idx_localstock_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_localstock_code ON public.localstock USING btree (code);


--
-- TOC entry 2999 (class 1259 OID 22818)
-- Name: idx_localstock_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_localstock_groupid ON public.localstock USING btree (groupid);


--
-- TOC entry 3000 (class 1259 OID 22819)
-- Name: idx_localstock_location_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_localstock_location_code ON public.localstock USING btree (location, code);


--
-- TOC entry 3011 (class 1259 OID 22820)
-- Name: idx_sales_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_code ON public.sales USING btree (code);


--
-- TOC entry 3012 (class 1259 OID 24031)
-- Name: idx_sales_date_channel_group; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_date_channel_group ON public.sales USING btree (solddate, channel, groupid);


--
-- TOC entry 3013 (class 1259 OID 22821)
-- Name: idx_sales_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_groupid ON public.sales USING btree (groupid);


--
-- TOC entry 3014 (class 1259 OID 22822)
-- Name: idx_sales_ordernum; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_ordernum ON public.sales USING btree (ordernum);


--
-- TOC entry 3015 (class 1259 OID 22823)
-- Name: idx_sales_solddate; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_solddate ON public.sales USING btree (solddate);


--
-- TOC entry 3026 (class 1259 OID 22824)
-- Name: idx_skumap_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skumap_code ON public.skumap USING btree (code);


--
-- TOC entry 3027 (class 1259 OID 22825)
-- Name: idx_skumap_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skumap_groupid ON public.skumap USING btree (groupid);


--
-- TOC entry 3028 (class 1259 OID 22826)
-- Name: idx_skumap_groupid_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skumap_groupid_code ON public.skumap USING btree (groupid, code);


--
-- TOC entry 3031 (class 1259 OID 22827)
-- Name: idx_skusummary_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skusummary_groupid ON public.skusummary USING btree (groupid);


--
-- TOC entry 3055 (class 2606 OID 22828)
-- Name: winner_channels winner_channels_groupid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.winner_channels
    ADD CONSTRAINT winner_channels_groupid_fkey FOREIGN KEY (groupid) REFERENCES public.winner_products(groupid);


--
-- TOC entry 3182 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2025-06-19 18:20:02

--
-- PostgreSQL database dump complete
--

