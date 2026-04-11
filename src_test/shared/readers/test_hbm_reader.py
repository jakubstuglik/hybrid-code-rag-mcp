"""
Tests for shared/readers/hbm_reader.py — Hibernate Mapping (.hbm.xml) reader.

Tests cover:
    - XML helpers: _strip_doctype, _short_class_name, _attr
    - ID extraction: simple ID, sequence generator, composite-id
    - Property extraction: business, read-only, formula, trace, validity
    - Collection extraction: set, bag, list, map with all attributes
    - Filter and sql-delete extraction
    - Version column extraction
    - Overview builder: all sections, context prefix, ordering
    - HBMFileReader: class attributes, load_data() for all 5 HBM patterns
    - Entity stem extraction from compound filename
    - Empty file, parse error fallback, missing class element
    - Metadata correctness (unit_name, class_name, table_name, node_type)
    - Large file raw_mapping chunk emission
    - extra_info forwarding
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from shared.readers.hbm_reader import (
    HBMFileReader,
    _attr,
    _build_entity_overview,
    _extract_collections,
    _extract_filters,
    _extract_id_info,
    _extract_properties,
    _extract_sql_delete,
    _extract_version,
    _short_class_name,
    _strip_doctype,
)

import xml.etree.ElementTree as ET


# ────────────────────────────────────────────────
# Test XML samples
# ────────────────────────────────────────────────

STANDARD_HBM = """\
<?xml version="1.0"?>
<!DOCTYPE hibernate-mapping PUBLIC
    "-//Hibernate/Hibernate Mapping DTD 3.0//EN"
    "http://hibernate.sourceforge.net/hibernate-mapping-3.0.dtd">
<hibernate-mapping default-access="field">
  <class name="com.example.app.persistence.dbo.impl.PHStop"
         table="PT_STOP"
         persister="com.inno.persistence.NSingleTableEntityPersister">
    <id name="id" column="ID_STOP">
      <generator class="sequence">
        <param name="sequence">SEQ_PT_STOP</param>
      </generator>
    </id>
    <version name="version" column="VERSION"/>
    <property name="name" column="NAME" not-null="true"/>
    <property name="code" column="CODE" type="string"/>
    <property name="latitude" column="LATITUDE"/>
    <property name="longitude" column="LONGITUDE"/>
    <property name="traceCreated" column="TRACE_CREATED"/>
    <property name="traceModified" column="TRACE_MODIFIED"/>
    <property name="validFrom" column="VALID_FROM"/>
    <property name="validTo" column="VALID_TO"/>
    <filter name="traceFilter"/>
    <sql-delete>UPDATE PT_STOP SET TRACE_DELETED = SYSDATE WHERE ID_STOP = ?</sql-delete>
  </class>
</hibernate-mapping>"""

COMPOSITE_ID_HBM = """\
<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.inno.persistence.dbo.impl.PHRouteStop" table="PV_ROUTE_STOP">
    <composite-id>
      <key-property name="routeId" column="ID_ROUTE"/>
      <key-property name="stopId" column="ID_STOP"/>
      <key-property name="sequence" column="SEQ_NO"/>
    </composite-id>
    <property name="arrivalTime" column="ARRIVAL_TIME"/>
    <property name="departureTime" column="DEPARTURE_TIME"/>
  </class>
</hibernate-mapping>"""

READ_ONLY_HBM = """\
<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.inno.persistence.dbo.impl.PHStopLookup" table="PV_STOP_LOOKUP"
         where="ACTIVE = 1">
    <id name="id" column="ID_STOP"/>
    <property name="name" column="NAME" update="false" insert="false"/>
    <property name="code" column="CODE" update="false" insert="false"/>
  </class>
</hibernate-mapping>"""

COLLECTION_HBM = """\
<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.inno.persistence.dbo.impl.PHRoute" table="PT_ROUTE">
    <id name="id" column="ID_ROUTE">
      <generator class="sequence">
        <param name="sequence">SEQ_PT_ROUTE</param>
      </generator>
    </id>
    <property name="name" column="NAME"/>
    <set name="stops" table="PT_ROUTE_STOP" cascade="all-delete-orphan" fetch="select"
         where="ACTIVE = 1">
      <key column="ID_ROUTE"/>
      <one-to-many class="com.inno.persistence.dbo.impl.PHRouteStop"/>
    </set>
    <map name="attributes" table="PT_ROUTE_ATTR">
      <key column="ID_ROUTE"/>
      <map-key column="ATTR_NAME" type="string"/>
      <element column="ATTR_VALUE" type="string"/>
    </map>
  </class>
</hibernate-mapping>"""

POSTGIS_HBM = """\
<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.inno.persistence.dbo.impl.PHOsmNode" table="PT_OSM_NODE">
    <id name="id" column="ID_NODE"/>
    <property name="latitude" column="LATITUDE"/>
    <property name="longitude" column="LONGITUDE"/>
    <property name="geom" formula="SDO_CS.TRANSFORM(GEOM, 4326)"/>
  </class>
</hibernate-mapping>"""

MINIMAL_HBM = """\
<?xml version="1.0"?>
<hibernate-mapping>
  <class name="PHMinimal" table="T_MINIMAL">
    <id name="id" column="ID"/>
    <property name="value" column="VAL"/>
  </class>
</hibernate-mapping>"""

NO_CLASS_HBM = """\
<?xml version="1.0"?>
<hibernate-mapping>
  <!-- Empty mapping with no class element -->
</hibernate-mapping>"""

INVALID_XML = """\
<?xml version="1.0"?>
<hibernate-mapping>
  <class name="Broken" table="T_BROKEN">
    <id name="id" column="ID">
  <!-- Missing closing tags -->
"""


# ────────────────────────────────────────────────
# XML helpers
# ────────────────────────────────────────────────


class TestStripDoctype:
    """Tests for _strip_doctype() — DOCTYPE removal."""

    def test_removes_standard_hibernate_doctype(self):
        """Standard Hibernate DTD should be stripped."""
        result = _strip_doctype(STANDARD_HBM)
        assert "<!DOCTYPE" not in result
        assert "<hibernate-mapping" in result

    def test_preserves_content_without_doctype(self):
        """Content without DOCTYPE should pass through unchanged."""
        content = '<hibernate-mapping>\n  <class name="Foo"/>\n</hibernate-mapping>'
        result = _strip_doctype(content)
        assert result == content

    def test_removes_only_first_doctype(self):
        """Only the first DOCTYPE should be removed (count=1)."""
        content = "<!DOCTYPE a><!DOCTYPE b><root/>"
        result = _strip_doctype(content)
        assert result.count("<!DOCTYPE") == 1
        assert "<!DOCTYPE b>" in result


class TestShortClassName:
    """Tests for _short_class_name() — FQN to short name."""

    def test_fully_qualified_name(self):
        assert _short_class_name("com.inno.persistence.dbo.impl.PHStop") == "PHStop"

    def test_already_short_name(self):
        assert _short_class_name("PHStop") == "PHStop"

    def test_single_level_package(self):
        assert _short_class_name("com.PHStop") == "PHStop"

    def test_empty_string(self):
        assert _short_class_name("") == ""


class TestAttrHelper:
    """Tests for _attr() — attribute extraction with default."""

    def test_existing_attribute(self):
        elem = ET.fromstring('<class name="Foo"/>')
        assert _attr(elem, "name") == "Foo"

    def test_missing_attribute_returns_default(self):
        elem = ET.fromstring('<class name="Foo"/>')
        assert _attr(elem, "table", "UNKNOWN") == "UNKNOWN"

    def test_missing_attribute_returns_empty_default(self):
        elem = ET.fromstring('<class name="Foo"/>')
        assert _attr(elem, "table") == ""


# ────────────────────────────────────────────────
# Entity analysis functions
# ────────────────────────────────────────────────


class TestExtractIdInfo:
    """Tests for _extract_id_info() — primary key strategy detection."""

    def test_sequence_id(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        strategy, cols = _extract_id_info(class_elem)
        assert "sequence" in strategy.lower()
        assert "SEQ_PT_STOP" in strategy
        assert cols == ["ID_STOP"]

    def test_composite_id(self):
        root = ET.fromstring(COMPOSITE_ID_HBM)
        class_elem = root.find("class")
        strategy, cols = _extract_id_info(class_elem)
        assert "composite-id" in strategy
        assert "3 columns" in strategy
        assert "ID_ROUTE" in cols
        assert "ID_STOP" in cols
        assert "SEQ_NO" in cols

    def test_simple_id_no_generator(self):
        root = ET.fromstring(READ_ONLY_HBM)
        class_elem = root.find("class")
        strategy, cols = _extract_id_info(class_elem)
        assert strategy == "simple ID"
        assert cols == ["ID_STOP"]

    def test_no_id_element(self):
        xml = '<class name="NoId" table="T_NOID"/>'
        elem = ET.fromstring(xml)
        strategy, cols = _extract_id_info(elem)
        assert strategy == "unknown"
        assert cols == []

    def test_generator_without_param(self):
        xml = """<class name="Foo" table="T_FOO">
            <id name="id" column="ID"><generator class="native"/></id>
        </class>"""
        elem = ET.fromstring(xml)
        strategy, cols = _extract_id_info(elem)
        assert "native" in strategy
        assert "seq=" not in strategy  # no sequence param

    def test_nested_column_element(self):
        xml = """<class name="Foo" table="T_FOO">
            <id name="id"><column name="MY_ID"/></id>
        </class>"""
        elem = ET.fromstring(xml)
        strategy, cols = _extract_id_info(elem)
        assert cols == ["MY_ID"]


class TestExtractProperties:
    """Tests for _extract_properties()."""

    def test_standard_properties(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        props = _extract_properties(class_elem)
        names = [p["name"] for p in props]
        assert "name" in names
        assert "code" in names
        assert "latitude" in names

    def test_not_null_flag(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        props = _extract_properties(class_elem)
        name_prop = [p for p in props if p["name"] == "name"][0]
        assert name_prop.get("not_null") == "true"

    def test_type_attribute(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        props = _extract_properties(class_elem)
        code_prop = [p for p in props if p["name"] == "code"][0]
        assert code_prop.get("type") == "string"

    def test_read_only_properties(self):
        root = ET.fromstring(READ_ONLY_HBM)
        class_elem = root.find("class")
        props = _extract_properties(class_elem)
        for p in props:
            assert p.get("read_only") == "true"

    def test_formula_property(self):
        root = ET.fromstring(POSTGIS_HBM)
        class_elem = root.find("class")
        props = _extract_properties(class_elem)
        geom_prop = [p for p in props if p["name"] == "geom"][0]
        assert "SDO_CS.TRANSFORM" in geom_prop.get("formula", "")

    def test_no_properties(self):
        xml = '<class name="Empty" table="T_EMPTY"><id name="id" column="ID"/></class>'
        elem = ET.fromstring(xml)
        props = _extract_properties(elem)
        assert props == []


class TestExtractCollections:
    """Tests for _extract_collections()."""

    def test_set_with_one_to_many(self):
        root = ET.fromstring(COLLECTION_HBM)
        class_elem = root.find("class")
        colls = _extract_collections(class_elem)
        set_coll = [c for c in colls if c["type"] == "set"][0]
        assert set_coll["name"] == "stops"
        assert set_coll["table"] == "PT_ROUTE_STOP"
        assert set_coll["key_column"] == "ID_ROUTE"
        assert set_coll["target_class"] == "PHRouteStop"
        assert set_coll["cascade"] == "all-delete-orphan"
        assert set_coll["fetch"] == "select"
        assert set_coll["where"] == "ACTIVE = 1"

    def test_map_collection(self):
        root = ET.fromstring(COLLECTION_HBM)
        class_elem = root.find("class")
        colls = _extract_collections(class_elem)
        map_coll = [c for c in colls if c["type"] == "map"][0]
        assert map_coll["name"] == "attributes"
        assert map_coll["table"] == "PT_ROUTE_ATTR"
        assert map_coll["key_column"] == "ID_ROUTE"
        assert map_coll["map_key_column"] == "ATTR_NAME"
        assert map_coll["map_key_type"] == "string"
        assert map_coll["element_type"] == "string"
        assert map_coll["element_column"] == "ATTR_VALUE"

    def test_no_collections(self):
        root = ET.fromstring(COMPOSITE_ID_HBM)
        class_elem = root.find("class")
        colls = _extract_collections(class_elem)
        assert colls == []


class TestExtractFilters:
    """Tests for _extract_filters()."""

    def test_single_filter(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        filters = _extract_filters(class_elem)
        assert filters == ["traceFilter"]

    def test_no_filters(self):
        root = ET.fromstring(COMPOSITE_ID_HBM)
        class_elem = root.find("class")
        filters = _extract_filters(class_elem)
        assert filters == []

    def test_multiple_filters(self):
        xml = """<class name="X" table="T">
            <id name="id" column="ID"/>
            <filter name="activeFilter"/>
            <filter name="traceFilter"/>
        </class>"""
        elem = ET.fromstring(xml)
        filters = _extract_filters(elem)
        assert filters == ["activeFilter", "traceFilter"]


class TestExtractSqlDelete:
    """Tests for _extract_sql_delete()."""

    def test_standard_soft_delete(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        result = _extract_sql_delete(class_elem)
        assert result is not None
        assert "UPDATE PT_STOP SET TRACE_DELETED" in result

    def test_no_sql_delete(self):
        root = ET.fromstring(COMPOSITE_ID_HBM)
        class_elem = root.find("class")
        result = _extract_sql_delete(class_elem)
        assert result is None


class TestExtractVersion:
    """Tests for _extract_version()."""

    def test_version_column(self):
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        result = _extract_version(class_elem)
        assert result == "VERSION"

    def test_no_version(self):
        root = ET.fromstring(COMPOSITE_ID_HBM)
        class_elem = root.find("class")
        result = _extract_version(class_elem)
        assert result is None


# ────────────────────────────────────────────────
# Overview builder
# ────────────────────────────────────────────────


class TestBuildEntityOverview:
    """Tests for _build_entity_overview()."""

    def _build_standard(self):
        """Helper: parse standard HBM and build overview."""
        xml = _strip_doctype(STANDARD_HBM)
        root = ET.fromstring(xml)
        class_elem = root.find("class")
        prefix = "<!-- HBM: PHStop (PT_STOP) — PHStop.hbm.xml -->"
        return _build_entity_overview(class_elem, prefix, "field")

    def test_contains_context_prefix(self):
        overview = self._build_standard()
        assert "<!-- HBM: PHStop (PT_STOP)" in overview

    def test_contains_entity_header(self):
        overview = self._build_standard()
        assert "Hibernate entity: PHStop" in overview
        assert "class: com.example.app.persistence.dbo.impl.PHStop" in overview
        assert "table: PT_STOP" in overview

    def test_contains_id_strategy(self):
        overview = self._build_standard()
        assert "Primary key: sequence ID" in overview
        assert "SEQ_PT_STOP" in overview

    def test_contains_version(self):
        overview = self._build_standard()
        assert "Optimistic locking: version column VERSION" in overview

    def test_contains_business_properties(self):
        overview = self._build_standard()
        assert "name → NAME" in overview
        assert "NOT NULL" in overview
        assert "code → CODE" in overview

    def test_contains_trace_columns(self):
        overview = self._build_standard()
        assert "Trace columns:" in overview
        assert "TRACE_CREATED" in overview

    def test_contains_validity_period(self):
        overview = self._build_standard()
        assert "Validity period:" in overview
        assert "VALID_FROM" in overview

    def test_contains_soft_delete(self):
        overview = self._build_standard()
        assert "Soft-delete:" in overview
        assert "UPDATE PT_STOP SET TRACE_DELETED" in overview

    def test_contains_filters(self):
        overview = self._build_standard()
        assert "Filters: traceFilter" in overview

    def test_contains_persister(self):
        overview = self._build_standard()
        assert "persister: NSingleTableEntityPersister" in overview

    def test_contains_access_mode(self):
        overview = self._build_standard()
        assert "access: field" in overview

    def test_composite_id_overview(self):
        root = ET.fromstring(COMPOSITE_ID_HBM)
        class_elem = root.find("class")
        prefix = "<!-- HBM: PHRouteStop (PV_ROUTE_STOP) -->"
        overview = _build_entity_overview(class_elem, prefix, "field")
        assert "composite-id (3 columns)" in overview
        assert "ID_ROUTE" in overview

    def test_read_only_overview(self):
        root = ET.fromstring(READ_ONLY_HBM)
        class_elem = root.find("class")
        prefix = "<!-- HBM: PHStopLookup (PV_STOP_LOOKUP) -->"
        overview = _build_entity_overview(class_elem, prefix, "field")
        assert "Read-only properties" in overview
        assert "where: ACTIVE = 1" in overview

    def test_collection_overview(self):
        root = ET.fromstring(COLLECTION_HBM)
        class_elem = root.find("class")
        prefix = "<!-- HBM: PHRoute (PT_ROUTE) -->"
        overview = _build_entity_overview(class_elem, prefix, "field")
        assert "Collections (2)" in overview
        assert "set stops" in overview
        assert "PHRouteStop" in overview
        assert "map attributes" in overview

    def test_formula_overview(self):
        root = ET.fromstring(POSTGIS_HBM)
        class_elem = root.find("class")
        prefix = "<!-- HBM: PHOsmNode (PT_OSM_NODE) -->"
        overview = _build_entity_overview(class_elem, prefix, "field")
        assert "Computed properties" in overview
        assert "SDO_CS.TRANSFORM" in overview


# ────────────────────────────────────────────────
# HBMFileReader — class attributes
# ────────────────────────────────────────────────


class TestHBMFileReaderAttributes:
    """Tests for HBMFileReader class attributes and constants."""

    def test_min_chunk_size(self):
        reader = HBMFileReader()
        assert reader.MIN_CHUNK_SIZE == 20

    def test_max_overview_chars(self):
        reader = HBMFileReader()
        assert reader.MAX_OVERVIEW_CHARS == 6000

    def test_is_base_file_reader(self):
        from shared.readers._base import BaseFileReader

        reader = HBMFileReader()
        assert isinstance(reader, BaseFileReader)


# ────────────────────────────────────────────────
# HBMFileReader — load_data() with real temp files
# ────────────────────────────────────────────────


class TestHBMFileReaderLoadData:
    """Tests for HBMFileReader.load_data() using temporary files."""

    @pytest.fixture
    def reader(self):
        return HBMFileReader()

    def _write_hbm(self, tmp_path, content, filename="PHTest.hbm.xml"):
        f = tmp_path / filename
        f.write_text(content, encoding="utf-8")
        return f

    # ── Standard entity (Pattern 1) ──

    def test_standard_entity_produces_one_chunk(self, reader, tmp_path):
        """Standard entity should produce exactly one hbm_entity_overview chunk."""
        f = self._write_hbm(tmp_path, STANDARD_HBM, "PHStop.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "hbm_entity_overview"

    def test_standard_entity_metadata(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, STANDARD_HBM, "PHStop.hbm.xml")
        docs = reader.load_data(f)
        meta = docs[0].metadata
        assert meta["unit_name"] == "PHStop"
        assert meta["class_name"] == "PHStop"
        assert meta["table_name"] == "PT_STOP"
        assert meta["package_name"] == "com.example.app.persistence.dbo.impl"
        assert meta["node_type"] == "hbm_entity_overview"
        assert "start_line" in meta
        assert "end_line" in meta
        assert "start_byte" in meta
        assert "end_byte" in meta
        assert "creation_datetime" in meta
        assert "modification_datetime" in meta

    def test_standard_entity_context_prefix(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, STANDARD_HBM, "PHStop.hbm.xml")
        docs = reader.load_data(f)
        text = docs[0].text
        assert text.startswith("<!-- HBM: PHStop (PT_STOP)")
        assert "PHStop.hbm.xml" in text.split("\n")[0]

    def test_standard_entity_overview_content(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, STANDARD_HBM, "PHStop.hbm.xml")
        docs = reader.load_data(f)
        text = docs[0].text
        assert "Hibernate entity: PHStop" in text
        assert "PT_STOP" in text
        assert "sequence ID" in text
        assert "name → NAME" in text

    # ── Composite ID (Pattern 2) ──

    def test_composite_id_entity(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, COMPOSITE_ID_HBM, "PHRouteStop.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        text = docs[0].text
        assert "composite-id (3 columns)" in text
        meta = docs[0].metadata
        assert meta["unit_name"] == "PHRouteStop"
        assert meta["class_name"] == "PHRouteStop"
        assert meta["table_name"] == "PV_ROUTE_STOP"

    # ── Read-only lookup (Pattern 3) ──

    def test_read_only_entity(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, READ_ONLY_HBM, "PHStopLookup.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        text = docs[0].text
        assert "Read-only properties" in text
        assert "where: ACTIVE = 1" in text

    # ── Collection (Pattern 4) ──

    def test_collection_entity(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, COLLECTION_HBM, "PHRoute.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        text = docs[0].text
        assert "Collections (2)" in text
        assert "set stops" in text
        assert "map attributes" in text

    # ── PostGIS (Pattern 5) ──

    def test_postgis_entity(self, reader, tmp_path):
        f = self._write_hbm(tmp_path, POSTGIS_HBM, "PHOsmNode.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        text = docs[0].text
        assert "Computed properties" in text
        assert "SDO_CS.TRANSFORM" in text

    # ── Entity stem extraction ──

    def test_entity_stem_from_hbm_filename(self, reader, tmp_path):
        """unit_name comes from filename stem, not XML class name.
        PHStop.hbm.xml → unit_name='PHStop', regardless of XML class name."""
        f = self._write_hbm(tmp_path, MINIMAL_HBM, "PHStop.hbm.xml")
        docs = reader.load_data(f)
        assert docs[0].metadata["unit_name"] == "PHStop"  # from filename
        assert docs[0].metadata["class_name"] == "PHMinimal"  # from XML

    def test_entity_stem_no_hbm_suffix(self, reader, tmp_path):
        """If file doesn't have .hbm in stem, use full stem."""
        f = self._write_hbm(tmp_path, MINIMAL_HBM, "Entity.xml")
        docs = reader.load_data(f)
        # entity_stem = "Entity" (no .hbm to strip)
        # But class name from XML is "PHMinimal"
        assert docs[0].metadata["class_name"] == "PHMinimal"

    # ── Edge cases ──

    def test_empty_file_returns_empty(self, reader, tmp_path):
        """Empty file should return empty list."""
        f = self._write_hbm(tmp_path, "", "Empty.hbm.xml")
        docs = reader.load_data(f)
        assert docs == []

    def test_whitespace_only_returns_empty(self, reader, tmp_path):
        """Whitespace-only file should return empty list."""
        f = self._write_hbm(tmp_path, "   \n\n  ", "Space.hbm.xml")
        docs = reader.load_data(f)
        assert docs == []

    def test_xml_parse_error_returns_full_file(self, reader, tmp_path):
        """Invalid XML should fall back to full_file chunk."""
        f = self._write_hbm(tmp_path, INVALID_XML, "Broken.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        meta = docs[0].metadata
        assert meta["node_type"] == "full_file"
        assert "parse_error" in meta
        assert meta["unit_name"] == "Broken"

    def test_no_class_element_returns_full_file(self, reader, tmp_path):
        """HBM with no <class> element should return full_file chunk."""
        f = self._write_hbm(tmp_path, NO_CLASS_HBM, "NoClass.hbm.xml")
        docs = reader.load_data(f)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert docs[0].metadata["unit_name"] == "NoClass"

    # ── Minimal entity (no package) ──

    def test_minimal_entity_no_package(self, reader, tmp_path):
        """Entity with short class name (no package) should have empty package_name."""
        f = self._write_hbm(tmp_path, MINIMAL_HBM, "PHMinimal.hbm.xml")
        docs = reader.load_data(f)
        assert docs[0].metadata["package_name"] == ""
        assert docs[0].metadata["class_name"] == "PHMinimal"

    # ── extra_info forwarding ──

    def test_extra_info_merged_into_metadata(self, reader, tmp_path):
        """extra_info should be merged into chunk metadata."""
        f = self._write_hbm(tmp_path, MINIMAL_HBM, "PHMinimal.hbm.xml")
        extra = {"project": "test_project", "branch": "feature/x"}
        docs = reader.load_data(f, extra_info=extra)
        assert len(docs) == 1
        meta = docs[0].metadata
        assert meta["project"] == "test_project"
        assert meta["branch"] == "feature/x"

    def test_no_extra_info(self, reader, tmp_path):
        """Without extra_info, metadata should not contain extra keys."""
        f = self._write_hbm(tmp_path, MINIMAL_HBM, "PHMinimal.hbm.xml")
        docs = reader.load_data(f)
        assert "project" not in docs[0].metadata


# ────────────────────────────────────────────────
# HBMFileReader — raw mapping emission
# ────────────────────────────────────────────────


class TestHBMFileReaderRawMapping:
    """Tests for raw_mapping chunk emission for large files."""

    @pytest.fixture
    def reader(self):
        return HBMFileReader()

    def test_small_file_no_raw_mapping(self, reader, tmp_path):
        """Files producing overview < MAX_OVERVIEW_CHARS should NOT emit raw_mapping."""
        f = tmp_path / "Small.hbm.xml"
        f.write_text(STANDARD_HBM, encoding="utf-8")
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]
        assert "hbm_raw_mapping" not in node_types

    def test_large_file_emits_raw_mapping(self, reader, tmp_path):
        """Files producing overview > MAX_OVERVIEW_CHARS should emit raw_mapping."""
        # Build an HBM with many properties to exceed the threshold
        props = "\n".join(
            f'    <property name="prop{i}" column="COL_{i}" type="string" not-null="true"/>'
            for i in range(200)
        )
        large_hbm = f"""<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.inno.persistence.dbo.impl.PHLarge" table="PT_LARGE"
         persister="com.inno.persistence.NSingleTableEntityPersister">
    <id name="id" column="ID_LARGE">
      <generator class="sequence">
        <param name="sequence">SEQ_PT_LARGE</param>
      </generator>
    </id>
{props}
    <filter name="traceFilter"/>
    <sql-delete>UPDATE PT_LARGE SET TRACE_DELETED = SYSDATE WHERE ID_LARGE = ?</sql-delete>
  </class>
</hibernate-mapping>"""
        f = tmp_path / "PHLarge.hbm.xml"
        f.write_text(large_hbm, encoding="utf-8")
        docs = reader.load_data(f)
        node_types = [d.metadata["node_type"] for d in docs]
        assert "hbm_entity_overview" in node_types
        assert "hbm_raw_mapping" in node_types
        assert len(docs) == 2

    def test_raw_mapping_contains_xml_content(self, reader, tmp_path):
        """The raw_mapping chunk should contain the original XML."""
        # Use same large HBM approach
        props = "\n".join(
            f'    <property name="prop{i}" column="COL_{i}" type="string" not-null="true"/>'
            for i in range(200)
        )
        large_hbm = f"""<?xml version="1.0"?>
<hibernate-mapping default-access="field">
  <class name="com.inno.persistence.dbo.impl.PHLarge" table="PT_LARGE">
    <id name="id" column="ID_LARGE">
      <generator class="sequence">
        <param name="sequence">SEQ_PT_LARGE</param>
      </generator>
    </id>
{props}
  </class>
</hibernate-mapping>"""
        f = tmp_path / "PHLarge.hbm.xml"
        f.write_text(large_hbm, encoding="utf-8")
        docs = reader.load_data(f)
        raw_doc = [d for d in docs if d.metadata["node_type"] == "hbm_raw_mapping"][0]
        assert "<hibernate-mapping" in raw_doc.text
        assert "PHLarge" in raw_doc.text
        # Should have context prefix
        assert "<!-- HBM:" in raw_doc.text


# ────────────────────────────────────────────────
# HBMFileReader — load_nodes() (TextNode output)
# ────────────────────────────────────────────────


class TestHBMFileReaderLoadNodes:
    """Tests for load_nodes() — TextNode conversion from load_data()."""

    @pytest.fixture
    def reader(self):
        return HBMFileReader()

    def test_returns_text_nodes(self, reader, tmp_path):
        """load_nodes should return TextNode objects."""
        from llama_index.core.schema import TextNode

        f = tmp_path / "PHStop.hbm.xml"
        f.write_text(STANDARD_HBM, encoding="utf-8")
        nodes = reader.load_nodes(f)
        assert len(nodes) >= 1
        assert all(isinstance(n, TextNode) for n in nodes)

    def test_text_node_has_same_content(self, reader, tmp_path):
        """TextNode text should match Document text from load_data."""
        f = tmp_path / "PHStop.hbm.xml"
        f.write_text(STANDARD_HBM, encoding="utf-8")
        docs = reader.load_data(f)
        nodes = reader.load_nodes(f)
        assert len(docs) == len(nodes)
        for doc, node in zip(docs, nodes):
            assert doc.text == node.text

    def test_text_node_metadata_preserved(self, reader, tmp_path):
        """TextNode should carry all metadata from Document."""
        f = tmp_path / "PHStop.hbm.xml"
        f.write_text(STANDARD_HBM, encoding="utf-8")
        nodes = reader.load_nodes(f)
        meta = nodes[0].metadata
        assert meta["node_type"] == "hbm_entity_overview"
        assert meta["class_name"] == "PHStop"
        assert meta["table_name"] == "PT_STOP"


# ────────────────────────────────────────────────
# HBMFileReader — default-access handling
# ────────────────────────────────────────────────


class TestHBMDefaultAccess:
    """Tests for default-access attribute handling."""

    @pytest.fixture
    def reader(self):
        return HBMFileReader()

    def test_field_access(self, reader, tmp_path):
        """default-access='field' should appear in overview."""
        f = tmp_path / "PHStop.hbm.xml"
        f.write_text(STANDARD_HBM, encoding="utf-8")
        docs = reader.load_data(f)
        assert "access: field" in docs[0].text

    def test_property_access(self, reader, tmp_path):
        """default-access='property' should appear in overview."""
        hbm = MINIMAL_HBM.replace(
            "<hibernate-mapping>", '<hibernate-mapping default-access="property">'
        )
        f = tmp_path / "Test.hbm.xml"
        f.write_text(hbm, encoding="utf-8")
        docs = reader.load_data(f)
        assert "access: property" in docs[0].text

    def test_missing_access_defaults_to_field(self, reader, tmp_path):
        """Missing default-access should default to 'field'."""
        f = tmp_path / "Test.hbm.xml"
        f.write_text(MINIMAL_HBM, encoding="utf-8")
        docs = reader.load_data(f)
        assert "access: field" in docs[0].text
