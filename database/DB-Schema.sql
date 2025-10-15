--
-- PostgreSQL database dump
--

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 17.4

-- Started on 2025-10-15 15:10:24

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
-- TOC entry 264 (class 1255 OID 16390)
-- Name: get_price_detail(character varying, character varying); Type: FUNCTION; Schema: public; Owner: brookfield_prod_user
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


ALTER FUNCTION public.get_price_detail(group_id_param character varying, channel_param character varying) OWNER TO brookfield_prod_user;

--
-- TOC entry 265 (class 1255 OID 16391)
-- Name: get_recent_incoming_stock(); Type: FUNCTION; Schema: public; Owner: brookfield_prod_user
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


ALTER FUNCTION public.get_recent_incoming_stock() OWNER TO brookfield_prod_user;

--
-- TOC entry 277 (class 1255 OID 16392)
-- Name: groupid_summary_performance(); Type: FUNCTION; Schema: public; Owner: brookfield_prod_user
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


ALTER FUNCTION public.groupid_summary_performance() OWNER TO brookfield_prod_user;

--
-- TOC entry 278 (class 1255 OID 16393)
-- Name: groupid_summary_performance_90(); Type: FUNCTION; Schema: public; Owner: brookfield_prod_user
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


ALTER FUNCTION public.groupid_summary_performance_90() OWNER TO brookfield_prod_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 215 (class 1259 OID 16394)
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
-- TOC entry 216 (class 1259 OID 16397)
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
-- TOC entry 217 (class 1259 OID 16400)
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
-- TOC entry 218 (class 1259 OID 16404)
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
-- TOC entry 219 (class 1259 OID 16409)
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
-- TOC entry 220 (class 1259 OID 16414)
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
-- TOC entry 221 (class 1259 OID 16415)
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
-- TOC entry 222 (class 1259 OID 16420)
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
-- TOC entry 223 (class 1259 OID 16423)
-- Name: brand; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.brand (
    brand character varying(50) NOT NULL,
    supplier character varying(50)
);


ALTER TABLE public.brand OWNER TO brookfield_prod_user;

--
-- TOC entry 224 (class 1259 OID 16426)
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
-- TOC entry 225 (class 1259 OID 16429)
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
-- TOC entry 226 (class 1259 OID 16434)
-- Name: colour; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.colour (
    colour character varying(50) NOT NULL
);


ALTER TABLE public.colour OWNER TO brookfield_prod_user;

--
-- TOC entry 263 (class 1259 OID 21978)
-- Name: google_stock_track; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.google_stock_track (
    id integer NOT NULL,
    live_stock_value numeric(10,2),
    live_stock_units integer,
    snapshot_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    total_stock_value numeric(10,2),
    total_stock_units integer,
    shopify_sales numeric(10,2),
    shopify_units integer,
    google_ad_spend numeric(10,2),
    google_clicks integer,
    google_impressions integer
);


ALTER TABLE public.google_stock_track OWNER TO brookfield_prod_user;

--
-- TOC entry 262 (class 1259 OID 21977)
-- Name: google_stock_track_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.google_stock_track_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.google_stock_track_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3682 (class 0 OID 0)
-- Dependencies: 262
-- Name: google_stock_track_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.google_stock_track_id_seq OWNED BY public.google_stock_track.id;


--
-- TOC entry 227 (class 1259 OID 16437)
-- Name: groupid_performance; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.groupid_performance (
    groupid text NOT NULL,
    channel text NOT NULL,
    annual_profit numeric(12,2),
    sold_qty integer,
    avg_profit_per_unit numeric(12,2),
    segment text,
    notes text,
    owner text,
    brand text,
    next_review_date date,
    review_date date,
    avg_gross_margin numeric(6,4),
    recommended_price numeric(10,2),
    stock integer
);


ALTER TABLE public.groupid_performance OWNER TO brookfield_prod_user;

--
-- TOC entry 228 (class 1259 OID 16442)
-- Name: groupid_performance_week; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.groupid_performance_week (
    year_week text NOT NULL,
    groupid text NOT NULL,
    channel text NOT NULL,
    annual_profit numeric(12,2),
    sold_qty integer,
    avg_profit_per_unit numeric(12,2),
    status text,
    segment text,
    notes text,
    owner text,
    snapshot_date date DEFAULT CURRENT_DATE,
    brand text,
    avg_gross_margin numeric(6,4),
    recommended_price numeric(10,2)
);


ALTER TABLE public.groupid_performance_week OWNER TO brookfield_prod_user;

--
-- TOC entry 229 (class 1259 OID 16448)
-- Name: grouplabel; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.grouplabel (
    label character varying(50),
    code character varying(20) NOT NULL
);


ALTER TABLE public.grouplabel OWNER TO brookfield_prod_user;

--
-- TOC entry 230 (class 1259 OID 16451)
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
-- TOC entry 231 (class 1259 OID 16456)
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
-- TOC entry 3683 (class 0 OID 0)
-- Dependencies: 231
-- Name: incoming_stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.incoming_stock_id_seq OWNED BY public.incoming_stock.id;


--
-- TOC entry 232 (class 1259 OID 16457)
-- Name: inivalues; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.inivalues (
    attribute character varying(100) NOT NULL,
    value character varying(100) NOT NULL
);


ALTER TABLE public.inivalues OWNER TO brookfield_prod_user;

--
-- TOC entry 233 (class 1259 OID 16460)
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
-- TOC entry 234 (class 1259 OID 16465)
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
-- TOC entry 235 (class 1259 OID 16468)
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
-- TOC entry 236 (class 1259 OID 16471)
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
    arriveddate date,
    last_seen timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.orderstatus OWNER TO brookfield_prod_user;

--
-- TOC entry 237 (class 1259 OID 16477)
-- Name: orderstatus_archive; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.orderstatus_archive (
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
    arriveddate date,
    archivedate timestamp with time zone DEFAULT now()
);


ALTER TABLE public.orderstatus_archive OWNER TO brookfield_prod_user;

--
-- TOC entry 238 (class 1259 OID 16483)
-- Name: performance; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.performance (
    code character varying(100) NOT NULL,
    channel character varying(20) NOT NULL,
    groupid text,
    brand text,
    sold_qty integer,
    revenue numeric(12,2),
    annual_profit numeric(12,2),
    profit_per_unit numeric(12,2),
    segment text,
    fail_reason text,
    status text DEFAULT 'New'::text,
    notes text,
    owner text,
    last_reviewed timestamp with time zone,
    status_date timestamp with time zone,
    gross_margin numeric(6,4),
    stock integer
);


ALTER TABLE public.performance OWNER TO brookfield_prod_user;

--
-- TOC entry 239 (class 1259 OID 16489)
-- Name: pickpin; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.pickpin (
    pin integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.pickpin OWNER TO brookfield_prod_user;

--
-- TOC entry 240 (class 1259 OID 16494)
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
-- TOC entry 3684 (class 0 OID 0)
-- Dependencies: 240
-- Name: pickpin_pin_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.pickpin_pin_seq OWNED BY public.pickpin.pin;


--
-- TOC entry 241 (class 1259 OID 16495)
-- Name: price_change_log; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.price_change_log (
    groupid character varying(100) NOT NULL,
    old_price numeric(10,2),
    new_price numeric(10,2),
    change_date date DEFAULT CURRENT_DATE,
    reason_code text,
    id integer NOT NULL,
    channel text,
    reason_notes text,
    changed_by text
);


ALTER TABLE public.price_change_log OWNER TO brookfield_prod_user;

--
-- TOC entry 242 (class 1259 OID 16501)
-- Name: price_change_log_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.price_change_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.price_change_log_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3685 (class 0 OID 0)
-- Dependencies: 242
-- Name: price_change_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.price_change_log_id_seq OWNED BY public.price_change_log.id;


--
-- TOC entry 261 (class 1259 OID 16755)
-- Name: price_change_reasons; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.price_change_reasons (
    id integer NOT NULL,
    reason text NOT NULL
);


ALTER TABLE public.price_change_reasons OWNER TO brookfield_prod_user;

--
-- TOC entry 260 (class 1259 OID 16754)
-- Name: price_change_reasons_id_seq; Type: SEQUENCE; Schema: public; Owner: brookfield_prod_user
--

CREATE SEQUENCE public.price_change_reasons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.price_change_reasons_id_seq OWNER TO brookfield_prod_user;

--
-- TOC entry 3686 (class 0 OID 0)
-- Dependencies: 260
-- Name: price_change_reasons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.price_change_reasons_id_seq OWNED BY public.price_change_reasons.id;


--
-- TOC entry 243 (class 1259 OID 16502)
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
-- TOC entry 244 (class 1259 OID 16507)
-- Name: productlink; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.productlink (
    groupid character varying(50) NOT NULL,
    updated date
);


ALTER TABLE public.productlink OWNER TO brookfield_prod_user;

--
-- TOC entry 245 (class 1259 OID 16510)
-- Name: producttype; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.producttype (
    producttype character varying(50) NOT NULL
);


ALTER TABLE public.producttype OWNER TO brookfield_prod_user;

--
-- TOC entry 246 (class 1259 OID 16513)
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
    paytype character varying(100),
    collectedvat numeric(5,2),
    productname character varying(200),
    returnsaleid character varying(20),
    brand character varying(50),
    profit numeric(5,2) DEFAULT 0,
    discount integer
);


ALTER TABLE public.sales OWNER TO brookfield_prod_user;

--
-- TOC entry 247 (class 1259 OID 16519)
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
-- TOC entry 3687 (class 0 OID 0)
-- Dependencies: 247
-- Name: sales_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: brookfield_prod_user
--

ALTER SEQUENCE public.sales_id_seq OWNED BY public.sales.id;


--
-- TOC entry 248 (class 1259 OID 16520)
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
    "karen-delete" integer,
    "tiktokshop-delete" integer,
    googlecampaign character varying(20),
    shopifyprice character varying(10),
    "tiktokshopid-delete" character varying(20),
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
    usereport integer DEFAULT 1,
    ignore_auto_price integer,
    catalogue integer,
    check_stock date,
    check_stock_notes text
);


ALTER TABLE public.skusummary OWNER TO brookfield_prod_user;

--
-- TOC entry 249 (class 1259 OID 16526)
-- Name: title; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.title (
    groupid character varying(100) NOT NULL,
    updated character varying(30),
    shopifytitle character varying(200),
    googletitle character varying(150),
    googletitleb character varying(150),
    last_shopify_sync timestamp with time zone
);


ALTER TABLE public.title OWNER TO brookfield_prod_user;

--
-- TOC entry 250 (class 1259 OID 16531)
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
-- TOC entry 251 (class 1259 OID 16534)
-- Name: shopify_health_check; Type: VIEW; Schema: public; Owner: brookfield_prod_user
--

CREATE VIEW public.shopify_health_check AS
 WITH sales_30d AS (
         SELECT sales.code,
            sum(sales.qty) AS sales_30d,
            round(avg(sales.soldprice), 2) AS avg_price_30d
           FROM public.sales
          WHERE (((sales.channel)::text = 'SHP'::text) AND (sales.solddate >= (CURRENT_DATE - '30 days'::interval)))
          GROUP BY sales.code
        ), sales_90d AS (
         SELECT sales.code,
            sum(sales.qty) AS sales_90d
           FROM public.sales
          WHERE (((sales.channel)::text = 'SHP'::text) AND (sales.solddate >= (CURRENT_DATE - '90 days'::interval)))
          GROUP BY sales.code
        ), local_stock AS (
         SELECT localstock.code,
            sum(localstock.qty) AS local_stock
           FROM public.localstock
          WHERE (localstock.deleted = 0)
          GROUP BY localstock.code
        ), ukd_stock AS (
         SELECT ukdstock.code,
            sum(ukdstock.stock) AS ukd_stock
           FROM public.ukdstock
          GROUP BY ukdstock.code
        ), shopify_price AS (
         SELECT skusummary.groupid,
            skusummary.shopifyprice AS shopifyprice_current,
            skusummary.rrp
           FROM public.skusummary
        ), health_check AS (
         SELECT p.code,
            p.channel,
            p.groupid,
            p.brand,
            p.owner,
            p.status,
            p.last_reviewed,
            p.notes,
            p.sold_qty,
            p.annual_profit,
            p.profit_per_unit,
            p.segment,
            COALESCE(ls.local_stock, (0)::bigint) AS local_stock,
            COALESCE(us.ukd_stock, (0)::bigint) AS ukd_stock,
            (COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) AS total_stock,
            sp.shopifyprice_current,
            sp.rrp,
            COALESCE(s30.sales_30d, (0)::bigint) AS sales_30d,
            COALESCE(s90.sales_90d, (0)::bigint) AS sales_90d,
            round(((COALESCE(s30.sales_30d, (0)::bigint))::numeric / 30.0), 2) AS sales_velocity_per_day,
            round(
                CASE
                    WHEN (COALESCE(s30.sales_30d, (0)::bigint) = 0) THEN (0)::numeric
                    ELSE (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)))::numeric / ((s30.sales_30d)::numeric / 30.0))
                END, 2) AS days_of_stock_left,
            (COALESCE(s90.sales_90d, (0)::bigint) = 0) AS no_sales_90d_flag,
            ((COALESCE(s30.sales_30d, (0)::bigint))::numeric < ((COALESCE(s90.sales_90d, (0)::bigint))::numeric / 3.0)) AS sales_slowdown_flag,
            ((NULLIF((sp.shopifyprice_current)::text, ''::text))::numeric > (COALESCE(s30.avg_price_30d, (0)::numeric) * 1.10)) AS price_check_flag,
            ((p.segment = 'Winner'::text) AND (COALESCE(s90.sales_90d, (0)::bigint) = 0) AND ((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) > 0)) AS overstock_flag,
                CASE
                    WHEN ((p.segment = 'Winner'::text) AND (p.brand = ANY (ARRAY['Birkenstock'::text, 'Skechers'::text, 'Rieker'::text])) AND (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) < 5) OR ((((COALESCE(s30.sales_30d, (0)::bigint))::numeric / 30.0) > (0)::numeric) AND (round(
                    CASE
                        WHEN (COALESCE(s30.sales_30d, (0)::bigint) = 0) THEN (0)::numeric
                        ELSE (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)))::numeric / ((s30.sales_30d)::numeric / 30.0))
                    END, 2) < (14)::numeric)))) THEN 'Price Too Low'::text
                    WHEN ((p.segment = 'Winner'::text) AND (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) < 5) OR ((((COALESCE(s30.sales_30d, (0)::bigint))::numeric / 30.0) > (0)::numeric) AND (round(
                    CASE
                        WHEN (COALESCE(s30.sales_30d, (0)::bigint) = 0) THEN (0)::numeric
                        ELSE (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)))::numeric / ((s30.sales_30d)::numeric / 30.0))
                    END, 2) < (14)::numeric)))) THEN 'Restock'::text
                    WHEN ((p.segment = 'Winner'::text) AND ((NULLIF((sp.shopifyprice_current)::text, ''::text))::numeric > (COALESCE(s30.avg_price_30d, (0)::numeric) * 1.10))) THEN 'Price Too High'::text
                    WHEN ((p.segment = 'Winner'::text) AND (COALESCE(s90.sales_90d, (0)::bigint) = 0) AND ((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) > 0)) THEN 'Stock Not Moving'::text
                    WHEN ((p.segment = 'Winner'::text) AND (COALESCE(s90.sales_90d, (0)::bigint) = 0)) THEN 'No Sales 90d'::text
                    WHEN ((p.segment = 'Winner'::text) AND ((COALESCE(s30.sales_30d, (0)::bigint))::numeric < ((COALESCE(s90.sales_90d, (0)::bigint))::numeric / 3.0))) THEN 'Sales Dropping'::text
                    WHEN ((p.segment = 'Loser'::text) AND (p.annual_profit < (0)::numeric)) THEN 'Discontinue'::text
                    WHEN ((p.segment = 'Loser'::text) AND (p.profit_per_unit < (2)::numeric) AND (p.sold_qty >= 20)) THEN 'Review Cost / Price'::text
                    WHEN ((p.segment = 'Loser'::text) AND (COALESCE(s90.sales_90d, (0)::bigint) = 0)) THEN 'Clearance'::text
                    WHEN ((p.segment = 'Loser'::text) AND (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) < 5) OR ((((COALESCE(s30.sales_30d, (0)::bigint))::numeric / 30.0) > (0)::numeric) AND (round(
                    CASE
                        WHEN (COALESCE(s30.sales_30d, (0)::bigint) = 0) THEN (0)::numeric
                        ELSE (((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)))::numeric / ((s30.sales_30d)::numeric / 30.0))
                    END, 2) < (14)::numeric)))) THEN 'Price Too Low'::text
                    WHEN ((p.segment = 'Loser'::text) AND (COALESCE(s90.sales_90d, (0)::bigint) = 0) AND ((COALESCE(ls.local_stock, (0)::bigint) + COALESCE(us.ukd_stock, (0)::bigint)) > 0)) THEN 'Stock Not Moving'::text
                    WHEN ((p.segment = 'Loser'::text) AND ((COALESCE(s30.sales_30d, (0)::bigint))::numeric < ((COALESCE(s90.sales_90d, (0)::bigint))::numeric / 3.0))) THEN 'Sales Dropping'::text
                    ELSE 'OK'::text
                END AS recommended_action,
            t.shopifytitle AS title
           FROM ((((((public.performance p
             LEFT JOIN local_stock ls ON (((p.code)::text = (ls.code)::text)))
             LEFT JOIN ukd_stock us ON (((p.code)::text = (us.code)::text)))
             LEFT JOIN shopify_price sp ON ((p.groupid = (sp.groupid)::text)))
             LEFT JOIN sales_30d s30 ON (((p.code)::text = (s30.code)::text)))
             LEFT JOIN sales_90d s90 ON (((p.code)::text = (s90.code)::text)))
             LEFT JOIN public.title t ON ((p.groupid = (t.groupid)::text)))
          WHERE ((p.channel)::text = 'SHP'::text)
        )
 SELECT code,
    channel,
    groupid,
    brand,
    owner,
    status,
    last_reviewed,
    notes,
    sold_qty,
    annual_profit,
    profit_per_unit,
    segment,
    local_stock,
    ukd_stock,
    total_stock,
    shopifyprice_current,
    rrp,
    sales_30d,
    sales_90d,
    sales_velocity_per_day,
    days_of_stock_left,
    no_sales_90d_flag,
    sales_slowdown_flag,
    price_check_flag,
    overstock_flag,
    recommended_action,
    title
   FROM health_check;


ALTER VIEW public.shopify_health_check OWNER TO brookfield_prod_user;

--
-- TOC entry 252 (class 1259 OID 16539)
-- Name: shopifyimages; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.shopifyimages (
    handle character varying(200) NOT NULL,
    imagepos smallint NOT NULL,
    imagesrc character varying(200)
);


ALTER TABLE public.shopifyimages OWNER TO brookfield_prod_user;

--
-- TOC entry 253 (class 1259 OID 16542)
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
-- TOC entry 254 (class 1259 OID 16545)
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
-- TOC entry 255 (class 1259 OID 16548)
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
-- TOC entry 256 (class 1259 OID 16551)
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
    amzpickrequest integer,
    shopifyrequest integer
);


ALTER TABLE public.skumap OWNER TO brookfield_prod_user;

--
-- TOC entry 257 (class 1259 OID 16556)
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
-- TOC entry 258 (class 1259 OID 16559)
-- Name: supplier; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.supplier (
    supplier character varying(100)
);


ALTER TABLE public.supplier OWNER TO brookfield_prod_user;

--
-- TOC entry 259 (class 1259 OID 16562)
-- Name: taglist; Type: TABLE; Schema: public; Owner: brookfield_prod_user
--

CREATE TABLE public.taglist (
    tag character varying(100) NOT NULL
);


ALTER TABLE public.taglist OWNER TO brookfield_prod_user;

--
-- TOC entry 3440 (class 2604 OID 21981)
-- Name: google_stock_track id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.google_stock_track ALTER COLUMN id SET DEFAULT nextval('public.google_stock_track_id_seq'::regclass);


--
-- TOC entry 3425 (class 2604 OID 16565)
-- Name: incoming_stock id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.incoming_stock ALTER COLUMN id SET DEFAULT nextval('public.incoming_stock_id_seq'::regclass);


--
-- TOC entry 3431 (class 2604 OID 16566)
-- Name: pickpin pin; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.pickpin ALTER COLUMN pin SET DEFAULT nextval('public.pickpin_pin_seq'::regclass);


--
-- TOC entry 3433 (class 2604 OID 16567)
-- Name: price_change_log id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.price_change_log ALTER COLUMN id SET DEFAULT nextval('public.price_change_log_id_seq'::regclass);


--
-- TOC entry 3439 (class 2604 OID 16758)
-- Name: price_change_reasons id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.price_change_reasons ALTER COLUMN id SET DEFAULT nextval('public.price_change_reasons_id_seq'::regclass);


--
-- TOC entry 3436 (class 2604 OID 16568)
-- Name: sales id; Type: DEFAULT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.sales ALTER COLUMN id SET DEFAULT nextval('public.sales_id_seq'::regclass);


--
-- TOC entry 3443 (class 2606 OID 16578)
-- Name: amzfeed amzfeed_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.amzfeed
    ADD CONSTRAINT amzfeed_pkey PRIMARY KEY (code);


--
-- TOC entry 3445 (class 2606 OID 16580)
-- Name: amzshipment amzshipment_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.amzshipment
    ADD CONSTRAINT amzshipment_pkey PRIMARY KEY (box, sku);


--
-- TOC entry 3447 (class 2606 OID 16582)
-- Name: attributes attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.attributes
    ADD CONSTRAINT attributes_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3449 (class 2606 OID 16584)
-- Name: bclog bclog_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.bclog
    ADD CONSTRAINT bclog_pkey PRIMARY KEY (id);


--
-- TOC entry 3451 (class 2606 OID 16586)
-- Name: birkstock birkstock_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.birkstock
    ADD CONSTRAINT birkstock_primary PRIMARY KEY (groupid);


--
-- TOC entry 3453 (class 2606 OID 16588)
-- Name: birktracker birktracker_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.birktracker
    ADD CONSTRAINT birktracker_primary PRIMARY KEY (code, ordernum);


--
-- TOC entry 3455 (class 2606 OID 16590)
-- Name: brand brand_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.brand
    ADD CONSTRAINT brand_pkey PRIMARY KEY (brand);


--
-- TOC entry 3457 (class 2606 OID 16592)
-- Name: campaign campaign_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.campaign
    ADD CONSTRAINT campaign_pkey PRIMARY KEY (id);


--
-- TOC entry 3459 (class 2606 OID 16594)
-- Name: category category_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.category
    ADD CONSTRAINT category_primary PRIMARY KEY (id);


--
-- TOC entry 3461 (class 2606 OID 16596)
-- Name: colour colour_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.colour
    ADD CONSTRAINT colour_pkey PRIMARY KEY (colour);


--
-- TOC entry 3531 (class 2606 OID 21984)
-- Name: google_stock_track google_stock_track_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.google_stock_track
    ADD CONSTRAINT google_stock_track_pkey PRIMARY KEY (id);


--
-- TOC entry 3463 (class 2606 OID 16598)
-- Name: groupid_performance groupid_performance_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.groupid_performance
    ADD CONSTRAINT groupid_performance_pkey PRIMARY KEY (groupid, channel);


--
-- TOC entry 3465 (class 2606 OID 16600)
-- Name: groupid_performance_week groupid_performance_week_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.groupid_performance_week
    ADD CONSTRAINT groupid_performance_week_pkey PRIMARY KEY (year_week, groupid, channel);


--
-- TOC entry 3467 (class 2606 OID 16602)
-- Name: grouplabel grouplabel_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.grouplabel
    ADD CONSTRAINT grouplabel_pkey PRIMARY KEY (code);


--
-- TOC entry 3473 (class 2606 OID 16604)
-- Name: localstock id_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.localstock
    ADD CONSTRAINT id_pkey PRIMARY KEY (id);


--
-- TOC entry 3469 (class 2606 OID 16606)
-- Name: incoming_stock incoming_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.incoming_stock
    ADD CONSTRAINT incoming_stock_pkey PRIMARY KEY (id);


--
-- TOC entry 3471 (class 2606 OID 16608)
-- Name: inivalues inivalues_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.inivalues
    ADD CONSTRAINT inivalues_pkey PRIMARY KEY (attribute);


--
-- TOC entry 3478 (class 2606 OID 16610)
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (barcode);


--
-- TOC entry 3480 (class 2606 OID 16612)
-- Name: offlinesold offlinesold_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.offlinesold
    ADD CONSTRAINT offlinesold_pkey PRIMARY KEY (id);


--
-- TOC entry 3484 (class 2606 OID 16614)
-- Name: orderstatus_archive orderstatus_archive_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.orderstatus_archive
    ADD CONSTRAINT orderstatus_archive_pkey PRIMARY KEY (ordernum, shopifysku);


--
-- TOC entry 3482 (class 2606 OID 16616)
-- Name: orderstatus orderstatus_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.orderstatus
    ADD CONSTRAINT orderstatus_pkey PRIMARY KEY (ordernum, shopifysku);


--
-- TOC entry 3486 (class 2606 OID 16618)
-- Name: performance performance_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.performance
    ADD CONSTRAINT performance_pkey PRIMARY KEY (code, channel);


--
-- TOC entry 3488 (class 2606 OID 16620)
-- Name: pickpin pickpin_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.pickpin
    ADD CONSTRAINT pickpin_pkey PRIMARY KEY (pin);


--
-- TOC entry 3490 (class 2606 OID 16622)
-- Name: price_change_log price_change_log_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.price_change_log
    ADD CONSTRAINT price_change_log_pkey PRIMARY KEY (id);


--
-- TOC entry 3529 (class 2606 OID 16762)
-- Name: price_change_reasons price_change_reasons_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.price_change_reasons
    ADD CONSTRAINT price_change_reasons_pkey PRIMARY KEY (id);


--
-- TOC entry 3492 (class 2606 OID 16624)
-- Name: price_track price_track_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.price_track
    ADD CONSTRAINT price_track_pkey PRIMARY KEY (groupid, date);


--
-- TOC entry 3494 (class 2606 OID 16626)
-- Name: productlink productlink_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.productlink
    ADD CONSTRAINT productlink_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3496 (class 2606 OID 16628)
-- Name: producttype producttype_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.producttype
    ADD CONSTRAINT producttype_pkey PRIMARY KEY (producttype);


--
-- TOC entry 3503 (class 2606 OID 16630)
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (id);


--
-- TOC entry 3512 (class 2606 OID 16632)
-- Name: shopifyimages shopifyimages_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopifyimages
    ADD CONSTRAINT shopifyimages_primary PRIMARY KEY (handle, imagepos);


--
-- TOC entry 3514 (class 2606 OID 16634)
-- Name: shopifysnapshot shopifysnapshot_primary; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopifysnapshot
    ADD CONSTRAINT shopifysnapshot_primary PRIMARY KEY (code);


--
-- TOC entry 3516 (class 2606 OID 16636)
-- Name: shopifysold shopifysold_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopifysold
    ADD CONSTRAINT shopifysold_pkey PRIMARY KEY (id);


--
-- TOC entry 3518 (class 2606 OID 16638)
-- Name: shopprices shopprices_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.shopprices
    ADD CONSTRAINT shopprices_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3523 (class 2606 OID 16640)
-- Name: skumap skumap_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.skumap
    ADD CONSTRAINT skumap_pkey PRIMARY KEY (code);


--
-- TOC entry 3506 (class 2606 OID 16642)
-- Name: skusummary skusummary_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.skusummary
    ADD CONSTRAINT skusummary_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3525 (class 2606 OID 16644)
-- Name: stockorder stockorder_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.stockorder
    ADD CONSTRAINT stockorder_pkey PRIMARY KEY (id);


--
-- TOC entry 3527 (class 2606 OID 16646)
-- Name: taglist taglist_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.taglist
    ADD CONSTRAINT taglist_pkey PRIMARY KEY (tag);


--
-- TOC entry 3508 (class 2606 OID 16648)
-- Name: title title_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.title
    ADD CONSTRAINT title_pkey PRIMARY KEY (groupid);


--
-- TOC entry 3510 (class 2606 OID 16650)
-- Name: ukdstock ukdstock_pkey; Type: CONSTRAINT; Schema: public; Owner: brookfield_prod_user
--

ALTER TABLE ONLY public.ukdstock
    ADD CONSTRAINT ukdstock_pkey PRIMARY KEY (code);


--
-- TOC entry 3474 (class 1259 OID 16651)
-- Name: idx_localstock_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_localstock_code ON public.localstock USING btree (code);


--
-- TOC entry 3475 (class 1259 OID 16652)
-- Name: idx_localstock_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_localstock_groupid ON public.localstock USING btree (groupid);


--
-- TOC entry 3476 (class 1259 OID 16653)
-- Name: idx_localstock_location_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_localstock_location_code ON public.localstock USING btree (location, code);


--
-- TOC entry 3497 (class 1259 OID 16654)
-- Name: idx_sales_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_code ON public.sales USING btree (code);


--
-- TOC entry 3498 (class 1259 OID 16655)
-- Name: idx_sales_date_channel_group; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_date_channel_group ON public.sales USING btree (solddate, channel, groupid);


--
-- TOC entry 3499 (class 1259 OID 16656)
-- Name: idx_sales_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_groupid ON public.sales USING btree (groupid);


--
-- TOC entry 3500 (class 1259 OID 16657)
-- Name: idx_sales_ordernum; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_ordernum ON public.sales USING btree (ordernum);


--
-- TOC entry 3501 (class 1259 OID 16658)
-- Name: idx_sales_solddate; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_sales_solddate ON public.sales USING btree (solddate);


--
-- TOC entry 3519 (class 1259 OID 16659)
-- Name: idx_skumap_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skumap_code ON public.skumap USING btree (code);


--
-- TOC entry 3520 (class 1259 OID 16660)
-- Name: idx_skumap_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skumap_groupid ON public.skumap USING btree (groupid);


--
-- TOC entry 3521 (class 1259 OID 16661)
-- Name: idx_skumap_groupid_code; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skumap_groupid_code ON public.skumap USING btree (groupid, code);


--
-- TOC entry 3504 (class 1259 OID 16662)
-- Name: idx_skusummary_groupid; Type: INDEX; Schema: public; Owner: brookfield_prod_user
--

CREATE INDEX idx_skusummary_groupid ON public.skusummary USING btree (groupid);


--
-- TOC entry 3681 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2025-10-15 15:10:26

--
-- PostgreSQL database dump complete
--

