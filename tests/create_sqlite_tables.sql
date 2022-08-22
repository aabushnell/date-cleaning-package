/*
drop table if exists tl_date_checked;
drop table if exists tl_date_manual_mapping;
drop table if exists tl_chrono_cache;
drop table if exists tl_synonyms;
drop table if exists objects;

CREATE TABLE tl_date_checked (
    id integer,
    date_english text,
    location_mapped_country text,
    date_start integer,
    date_end integer,
    correct integer,
    date_match_id text,
    date_match_label text,
    date_match_score real,
    date_match_spatial text,
    date_debug text,
    date_debug_spatial text
);

CREATE TABLE tl_date_manual_mapping (
    id integer,
    input_string text,
    date_start integer,
    date_end integer,
    countries text,
    comment text,
    url_source text
);

CREATE TABLE tl_chrono_cache (
    input_string text,
    date_start integer,
    date_end integer,
    date_match_label text,
    date_match_score real,
    date_match_spatial text,
    date_match_id text,
    date_debug text,
    date_debug_spatial text
);

CREATE TABLE tl_synonyms (
    original_string text,
    synonym text,
    comment text,
    country_code text
);*/

drop table if exists tl_date_checked;
drop table if exists tl_date_manual_mapping;
drop table if exists tl_chrono_cache;
drop table if exists tl_synonyms;
drop table if exists objects;

CREATE TABLE tl_date_checked (
    id integer,
    date_english text,
    location_mapped_country text,
    date_start integer,
    date_end integer,
    correct integer,
    date_match_id text,
    date_match_label text,
    date_match_score real,
    date_match_spatial text,
    date_debug text,
    date_debug_spatial text
);

CREATE TABLE tl_date_manual_mapping (
    id integer,
    input_string text,
    date_start integer,
    date_end integer,
    countries text,
    comment text,
    url_source text,
    is_date_original boolean
);

CREATE TABLE tl_chrono_cache (
    input_string text,
    date_start integer,
    date_end integer,
    date_match_label text,
    date_match_score real,
    date_match_spatial text,
    date_match_id text,
    date_debug text,
    date_debug_spatial text
);

CREATE TABLE tl_synonyms (
    original_string text,
    synonym text,
    comment text,
    country_code text,
    is_date_original boolean
);

CREATE TABLE objects (
    id text,
    date_english text,
    date_debug text,
    date_debug_spatial text,
    date_flags text,
    date_start integer,
    date_end integer,
    location_mapped_country text,
    date_match_label text,
    date_match_score real,
    date_match_id text,
    date_match_spatial text,
    datasource_id text,
    location_original text,
    date_original_lang text,
    url_object_page text,
    object_id text,
    location_debug text,
    attribute_name_english text
);

drop table if exists tl_date_periodo;
create table tl_date_periodo(
    periodo_id text,
    label text,
    country_list text,
    date_start numeric,
    date_end numeric,
    source text,
    publication_year text
);