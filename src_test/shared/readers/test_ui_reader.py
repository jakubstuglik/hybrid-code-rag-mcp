"""Tests for the Qt Designer .ui reader."""

import xml.etree.ElementTree as ET

import pytest

from shared.readers.ui_reader import (
    CONTEXT_SIZE_FLOOR,
    MAX_GROUP_CHARS,
    VISIBLE_TEXT_CHAR_CAP,
    UiFileReader,
    configure_ui_chunk_context,
    set_ui_chunk_context,
)


_UI = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>DlgSettingsUi</class>
 <widget class="QDialog" name="DlgSettingsUi">
  <property name="windowTitle">
   <string>Ustawienia ogólne</string>
  </property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QGroupBox" name="groupBox">
     <property name="title">
      <string>Directory</string>
     </property>
     <layout class="QHBoxLayout" name="horizontalLayout">
      <item>
       <widget class="QLineEdit" name="dirEdit"/>
      </item>
      <item>
       <widget class="QPushButton" name="dirButton">
        <property name="text"><string>...</string></property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="okButton">
     <property name="text"><string>OK</string></property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="cancelButton">
     <property name="text"><string>Cancel</string></property>
    </widget>
   </item>
  </layout>
 </widget>
 <customwidgets>
  <customwidget>
   <class>DateRange</class>
   <extends>QWidget</extends>
   <header>daterange.h</header>
  </customwidget>
 </customwidgets>
 <connections>
  <connection>
   <sender>okButton</sender>
   <signal>clicked()</signal>
   <receiver>DlgSettingsUi</receiver>
   <slot>accept()</slot>
  </connection>
 </connections>
</ui>
"""


def _docs(tmp_path, text: str, name: str = "dlg_settings.ui"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return UiFileReader().load_data(path)


def _by_type(docs, node_type: str):
    return [doc for doc in docs if doc.metadata["node_type"] == node_type]


class TestUiReader:
    def test_form_header_has_class_title_and_custom_widget(self, tmp_path):
        docs = _docs(tmp_path, _UI)
        headers = _by_type(docs, "ui_form_header")
        assert len(headers) == 1
        text = headers[0].text
        assert "// Form: DlgSettingsUi (dlg_settings.ui)" in text
        assert "Ustawienia ogólne" in text
        assert "DateRange extends QWidget (daterange.h)" in text
        assert "QDialog" in text
        meta = headers[0].metadata
        assert meta["class_name"] == "DlgSettingsUi"
        assert meta["unit_name"] == "dlg_settings"
        assert meta["form_type"] == "QDialog"
        assert meta["object_name"] == "DlgSettingsUi"

    def test_nested_widget_stays_with_its_parent(self, tmp_path):
        docs = _docs(tmp_path, _UI)
        names = [doc.metadata["object_name"] for doc in docs]
        assert "dirEdit" not in names
        group = _by_type(docs, "ui_object")
        assert len(group) == 1
        assert group[0].metadata["object_name"] == "groupBox"
        assert "dirEdit" in group[0].text
        assert "Directory" in group[0].text

    def test_small_same_class_widgets_are_grouped(self, tmp_path):
        docs = _docs(tmp_path, _UI)
        grouped = _by_type(docs, "ui_object_group")
        assert len(grouped) == 1
        assert grouped[0].metadata["object_type"] == "QPushButton"
        assert "okButton" in grouped[0].text
        assert "cancelButton" in grouped[0].text
        assert "Cancel" in grouped[0].text
        assert grouped[0].metadata["class_name"] == "DlgSettingsUi"

    def test_connections_chunk(self, tmp_path):
        docs = _docs(tmp_path, _UI)
        conns = _by_type(docs, "ui_connections")
        assert len(conns) == 1
        assert "okButton.clicked() -> DlgSettingsUi.accept()" in conns[0].text

    def test_malformed_xml_is_one_full_file(self, tmp_path):
        docs = _docs(tmp_path, "<ui><widget>")
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"

    def test_empty_file(self, tmp_path):
        assert _docs(tmp_path, "  \n") == []


_VISIBLE_PROPS = frozenset(
    {
        "text",
        "toolTip",
        "statusTip",
        "whatsThis",
        "title",
        "placeholderText",
        "windowTitle",
    }
)

_SIMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QLabel" name="nameLabel">
     <property name="text"><string>Name</string></property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="saveButton">
     <property name="text"><string>Save</string></property>
    </widget>
   </item>
  </layout>
 </widget>
</ui>
"""

_TWO_BUTTONS = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QPushButton" name="okButton">
     <property name="text"><string>OK</string></property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="cancelButton">
     <property name="text"><string>Cancel</string></property>
    </widget>
   </item>
  </layout>
 </widget>
 <connections>
  <connection>
   <sender>okButton</sender>
   <signal>clicked()</signal>
   <receiver>OrderDialog</receiver>
   <slot>accept()</slot>
  </connection>
 </connections>
</ui>
"""

_RICH = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <property name="alignment"><enum>Qt::AlignLeft</enum></property>
  <property name="modal"><bool>true</bool></property>
  <layout class="QVBoxLayout" name="mainLayout">
   <item>
    <widget class="QLabel" name="dupLabel">
     <property name="text"><string>Customer details</string></property>
    </widget>
   </item>
   <item>
    <widget class="QLabel" name="nameLabel">
     <property name="text"><string>Name</string></property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="saveButton">
     <property name="text"><string>Save</string></property>
     <property name="toolTip"><string>Save the order</string></property>
     <property name="statusTip"><string>Ready</string></property>
     <property name="whatsThis"><string>Help text</string></property>
    </widget>
   </item>
   <item>
    <widget class="QGroupBox" name="addressBox">
     <property name="title"><string>Address</string></property>
     <layout class="QVBoxLayout" name="addressLayout">
      <item>
       <widget class="QLineEdit" name="cityEdit">
        <property name="placeholderText"><string>City</string></property>
       </widget>
      </item>
     </layout>
    </widget>
   </item>
   <item>
    <widget class="QComboBox" name="statusCombo">
     <item><property name="text"><string>Open</string></property></item>
     <item><property name="text"><string>Open</string></property></item>
     <item><property name="text"><string>Closed</string></property></item>
    </widget>
   </item>
   <item>
    <widget class="QTableWidget" name="ordersTable">
     <column><property name="text"><string>Order id</string></property></column>
    </widget>
   </item>
   <item>
    <widget class="QTabWidget" name="tabWidget">
     <widget class="QWidget" name="tabPayment">
      <attribute name="title"><string>Payment</string></attribute>
      <layout class="QVBoxLayout" name="payLayout">
       <item>
        <widget class="QLabel" name="payLabel">
         <property name="text"><string>Pay now</string></property>
        </widget>
       </item>
      </layout>
     </widget>
    </widget>
   </item>
  </layout>
  <action name="actionSave">
   <property name="text"><string>Save</string></property>
  </action>
 </widget>
</ui>
"""


def _load(tmp_path, text, name="order_dialog.ui", extra=None, parent=None):
    directory = tmp_path / parent if parent else tmp_path
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return UiFileReader().load_data(path, extra)


def _sig(docs):
    return [
        (doc.metadata["node_type"], doc.metadata.get("object_name"), doc.text)
        for doc in docs
    ]


def _blob(docs) -> str:
    return "\n".join(doc.text for doc in docs)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _xml_names_and_texts(xml: str):
    root = ET.fromstring(xml)
    names = []
    texts = []
    for elem in root.iter():
        tag = _local(elem.tag)
        if tag == "widget" and elem.get("name"):
            names.append(elem.get("name"))
        if tag not in ("property", "attribute"):
            continue
        if (elem.get("name") or "") not in _VISIBLE_PROPS:
            continue
        for node in elem.iter():
            if node is elem or _local(node.tag) != "string":
                continue
            value = " ".join("".join(node.itertext()).split())
            if value:
                texts.append(value)
    return names, texts


def _assert_no_loss(xml: str, docs) -> None:
    raw = _blob(docs)
    folded = _norm(raw)
    names, texts = _xml_names_and_texts(xml)
    for name in names:
        assert name in raw
    for text in texts:
        assert _norm(text) in folded


def _on(tmp_path, text, name="order_dialog.ui"):
    return _load(
        tmp_path,
        text,
        name=name,
        extra={"ui_chunk_context": True},
        parent="Ui",
    )


@pytest.fixture(autouse=True)
def _reset_ui_context():
    yield
    set_ui_chunk_context(False)


class TestUiChunkContextOff:
    """Default off stays on the legacy chunk text."""

    def test_several_forms_match_explicit_off(self, tmp_path):
        forms = (_SIMPLE, _TWO_BUTTONS, _RICH)
        for index, xml in enumerate(forms):
            name = f"form_{index}.ui"
            plain = _load(tmp_path, xml, name=name)
            flagged = _load(
                tmp_path, xml, name=name, extra={"ui_chunk_context": False}
            )
            word = _load(
                tmp_path, xml, name=name, extra={"ui_chunk_context": "false"}
            )
            zero = _load(tmp_path, xml, name=name, extra={"ui_chunk_context": 0})
            off = _load(
                tmp_path, xml, name=name, extra={"ui_chunk_context": "off"}
            )
            assert _sig(plain) == _sig(flagged) == _sig(word) == _sig(zero) == _sig(off)
            blob = _blob(plain)
            assert "// Title:" not in blob
            assert "// Path:" not in blob
            assert "Visible texts:" not in blob

    def test_simple_form_bytes(self, tmp_path):
        docs = _load(tmp_path, _SIMPLE, parent="Ui")
        assert [doc.metadata["node_type"] for doc in docs] == [
            "ui_form_header",
            "ui_object",
            "ui_object",
        ]
        assert docs[0].text == (
            "// Form: OrderDialog (order_dialog.ui)\n"
            "class: OrderDialog\n"
            "widget: QDialog name=OrderDialog\n"
            "windowTitle: Customer details"
        )
        assert docs[1].metadata["object_name"] == "nameLabel"
        assert docs[2].metadata["object_name"] == "saveButton"
        assert "Ui/" not in _blob(docs)
        assert str(tmp_path) not in _blob(docs)

    def test_same_class_buttons_still_group(self, tmp_path):
        docs = _load(tmp_path, _TWO_BUTTONS)
        grouped = _by_type(docs, "ui_object_group")
        assert len(grouped) == 1
        assert grouped[0].text == (
            "// Form: OrderDialog (order_dialog.ui)\n"
            "// Object group: 2 x QPushButton\n"
            "widget QPushButton okButton\n"
            "  text: OK\n"
            "widget QPushButton cancelButton\n"
            "  text: Cancel"
        )
        assert _by_type(docs, "ui_connections")[0].text.startswith(
            "// Form: OrderDialog (order_dialog.ui)\n// Connections\n"
        )

    def test_base_config_defaults_off(self):
        import config

        assert config.UI_CHUNK_CONTEXT is False


class TestUiChunkContextOn:
    def test_every_chunk_has_title_and_relative_path(self, tmp_path):
        docs = _on(tmp_path, _TWO_BUTTONS)
        assert docs
        blob = _blob(docs)
        assert str(tmp_path) not in blob
        assert ":\\" not in blob
        for doc in docs:
            text = doc.text
            assert text.startswith("// Form: OrderDialog (Ui/order_dialog.ui)\n")
            assert "// Title: Customer details\n" in text
            assert "// Path:" in text
            assert "ui_chunk_context" not in doc.metadata
        kinds = {doc.metadata["node_type"] for doc in docs}
        assert "ui_form_header" in kinds
        assert "ui_connections" in kinds

    def test_visible_texts_order_dedup_and_skip_non_text(self, tmp_path):
        docs = _on(tmp_path, _RICH)
        header = _by_type(docs, "ui_form_header")[0].text
        line = next(
            item for item in header.splitlines() if item.startswith("Visible texts:")
        )
        assert line == (
            "Visible texts: Customer details | Name | Save | Save the order | "
            "Ready | Help text | Address | City | Open | Closed | Order id | "
            "Payment | Pay now"
        )
        assert "Qt::AlignLeft" not in line
        assert "true" not in line.split("Visible texts:", 1)[1]
        assert "actionSave: Save" in header
        _assert_no_loss(_RICH, docs)

    def test_visible_texts_are_capped(self, tmp_path):
        labels = []
        for index in range(40):
            labels.append(
                f'<item><widget class="QLabel" name="label{index:02d}">'
                f'<property name="text"><string>'
                f"Visible text number {index:02d} with extra padding words"
                f"</string></property></widget></item>"
            )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<ui version="4.0">\n'
            "<class>OrderDialog</class>\n"
            '<widget class="QDialog" name="OrderDialog">\n'
            '<property name="windowTitle"><string>Customer details</string>'
            "</property>\n"
            '<layout class="QVBoxLayout" name="verticalLayout">\n'
            + "\n".join(labels)
            + "\n</layout>\n</widget>\n</ui>\n"
        )
        docs = _on(tmp_path, xml)
        header = _by_type(docs, "ui_form_header")[0].text
        line = next(
            item for item in header.splitlines() if item.startswith("Visible texts:")
        )
        payload = line.split("Visible texts: ", 1)[1]
        assert len(payload) <= VISIBLE_TEXT_CHAR_CAP
        assert payload.endswith("[...]")
        assert payload.startswith("Customer details | ")
        assert "Visible text number 00" in payload
        assert "Visible text number 39" not in payload
        _assert_no_loss(xml, docs)

    def test_tiny_siblings_of_any_class_merge(self, tmp_path):
        docs = _on(tmp_path, _SIMPLE)
        grouped = _by_type(docs, "ui_object_group")
        assert len(grouped) == 1
        assert _by_type(docs, "ui_object") == []
        meta = grouped[0].metadata
        assert "nameLabel" in meta["object_name"]
        assert "saveButton" in meta["object_name"]
        assert "QLabel" in meta["object_type"]
        assert "QPushButton" in meta["object_type"]
        assert "nameLabel" in grouped[0].text
        assert "saveButton" in grouped[0].text
        assert '// Path: OrderDialog "Customer details"' in grouped[0].text

    def test_floor_does_not_merge_larger_same_class_siblings(self, tmp_path):
        body = "A" * 400
        other = "B" * 400
        assert len(body) >= CONTEXT_SIZE_FLOOR
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QLabel" name="labelA">
     <property name="text"><string>{body}</string></property>
    </widget>
   </item>
   <item>
    <widget class="QLabel" name="labelB">
     <property name="text"><string>{other}</string></property>
    </widget>
   </item>
  </layout>
 </widget>
</ui>
"""
        off = _load(tmp_path, xml, extra={"ui_chunk_context": False})
        assert len(_by_type(off, "ui_object_group")) == 1
        on = _on(tmp_path, xml)
        objects = _by_type(on, "ui_object")
        assert [doc.metadata["object_name"] for doc in objects] == ["labelA", "labelB"]
        assert _by_type(on, "ui_object_group") == []

    def test_tiny_merge_stops_at_the_ceiling(self, tmp_path):
        chunk = "C" * 250
        items = []
        for index in range(20):
            items.append(
                f'<item><widget class="QLabel" name="label{index:02d}">'
                f'<property name="text"><string>{chunk}</string></property>'
                f"</widget></item>"
            )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n<ui version="4.0">\n'
            "<class>OrderDialog</class>\n"
            '<widget class="QDialog" name="OrderDialog">\n'
            '<property name="windowTitle"><string>Customer details</string>'
            "</property>\n"
            '<layout class="QVBoxLayout" name="verticalLayout">\n'
            + "\n".join(items)
            + "\n</layout>\n</widget>\n</ui>\n"
        )
        docs = _on(tmp_path, xml)
        groups = _by_type(docs, "ui_object_group")
        assert len(groups) >= 2
        seen = []
        for doc in groups:
            body = doc.text.split("// Object group:", 1)[1]
            assert len(body) <= MAX_GROUP_CHARS + 80
            seen.extend(part.strip() for part in doc.metadata["object_name"].split(","))
        assert seen == [f"label{index:02d}" for index in range(20)]

    def test_oversized_tab_widget_splits_per_page(self, tmp_path):
        page = "P" * (MAX_GROUP_CHARS // 2 + 200)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QTabWidget" name="tabWidget">
     <widget class="QWidget" name="tabPayment">
      <attribute name="title"><string>Payment</string></attribute>
      <layout class="QVBoxLayout" name="payLayout">
       <item>
        <widget class="QLabel" name="payLabel">
         <property name="text"><string>{page}</string></property>
        </widget>
       </item>
      </layout>
     </widget>
     <widget class="QWidget" name="tabHistory">
      <attribute name="title"><string>History</string></attribute>
      <layout class="QVBoxLayout" name="histLayout">
       <item>
        <widget class="QLabel" name="histLabel">
         <property name="text"><string>{page}</string></property>
        </widget>
       </item>
      </layout>
     </widget>
    </widget>
   </item>
  </layout>
 </widget>
</ui>
"""
        docs = _on(tmp_path, xml)
        objects = _by_type(docs, "ui_object")
        by_name = {doc.metadata["object_name"]: doc.text for doc in objects}
        assert "tabPayment" in by_name
        assert "tabHistory" in by_name
        assert "payLabel" in by_name["tabPayment"]
        assert "histLabel" not in by_name["tabPayment"]
        assert "histLabel" in by_name["tabHistory"]
        assert "payLabel" not in by_name["tabHistory"]
        assert (
            'OrderDialog "Customer details" > tabWidget > tabPayment "Payment"'
            in by_name["tabPayment"]
        )
        assert (
            'OrderDialog "Customer details" > tabWidget > tabHistory "History"'
            in by_name["tabHistory"]
        )
        _assert_no_loss(xml, docs)

    def test_tiny_children_do_not_merge_across_parents(self, tmp_path):
        huge = "H" * MAX_GROUP_CHARS
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <widget class="QTabWidget" name="tabWidget">
   <widget class="QWidget" name="tabPayment">
    <attribute name="title"><string>Payment</string></attribute>
    <widget class="QLabel" name="payHuge">
     <property name="text"><string>{huge}</string></property>
    </widget>
    <widget class="QPushButton" name="payButton">
     <property name="text"><string>Pay</string></property>
    </widget>
    <widget class="QPushButton" name="payExtra">
     <property name="text"><string>More</string></property>
    </widget>
   </widget>
   <widget class="QWidget" name="tabHistory">
    <attribute name="title"><string>History</string></attribute>
    <widget class="QLabel" name="histHuge">
     <property name="text"><string>{huge}</string></property>
    </widget>
    <widget class="QPushButton" name="histButton">
     <property name="text"><string>Past</string></property>
    </widget>
   </widget>
  </widget>
 </widget>
</ui>
"""
        docs = _on(tmp_path, xml)
        pay = [
            doc
            for doc in docs
            if "payButton" in doc.text and doc.metadata["node_type"] != "ui_form_header"
        ]
        assert len(pay) == 1
        assert "payExtra" in pay[0].text
        assert "histButton" not in pay[0].text
        assert 'tabPayment "Payment"' in pay[0].text
        hist = [
            doc
            for doc in docs
            if doc.metadata.get("object_name") == "histButton"
            or (
                "histButton" in (doc.metadata.get("object_name") or "")
                and "payButton" not in (doc.metadata.get("object_name") or "")
            )
        ]
        assert hist
        assert all("payButton" not in doc.text for doc in hist)
        assert any('tabHistory "History"' in doc.text for doc in hist)
        _assert_no_loss(xml, docs)

    def test_malformed_xml_stays_full_file(self, tmp_path):
        raw = "<ui><widget>"
        docs = _load(tmp_path, raw, extra={"ui_chunk_context": True})
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert docs[0].text == raw

    def test_no_widget_stays_full_file(self, tmp_path):
        raw = '<?xml version="1.0"?><ui version="4.0"><class>OrderDialog</class></ui>'
        docs = _on(tmp_path, raw)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert docs[0].text == raw

    def test_string_on_enables_and_extra_info_overrides_config(self, tmp_path):
        import types

        assert configure_ui_chunk_context(types.SimpleNamespace()) is False
        assert (
            configure_ui_chunk_context(
                types.SimpleNamespace(UI_CHUNK_CONTEXT="true")
            )
            is True
        )
        try:
            enabled = _load(tmp_path, _SIMPLE, name="from_config.ui")
            assert "// Title: Customer details" in enabled[0].text
            forced_off = _load(
                tmp_path,
                _SIMPLE,
                name="forced_off.ui",
                extra={"ui_chunk_context": "no"},
            )
            assert "// Title:" not in _blob(forced_off)
        finally:
            set_ui_chunk_context(False)
        plain = _load(tmp_path, _SIMPLE, name="after_reset.ui")
        assert "// Title:" not in _blob(plain)

    def test_missing_title_and_display_name(self, tmp_path):
        from pathlib import Path

        from shared.readers.ui_reader import _display_file

        assert _display_file(Path("order_dialog.ui")) == "order_dialog.ui"
        assert _display_file(Path("Ui") / "order_dialog.ui") == "Ui/order_dialog.ui"
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <widget class="QDialog" name="BlankDialog">
  <property name="modal"><bool>true</bool></property>
  <widget class="QPushButton" name="okButton"/>
 </widget>
</ui>
"""
        docs = _on(tmp_path, xml)
        blob = _blob(docs)
        assert "// Form: BlankDialog (Ui/order_dialog.ui)" in blob
        assert "// Title:\n" in blob
        assert "Visible texts:" not in blob
        assert "okButton" in blob
        assert str(tmp_path) not in blob

    def test_first_visible_text_is_truncated(self, tmp_path):
        title = "T" * (VISIBLE_TEXT_CHAR_CAP + 200)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>{title}</string></property>
 </widget>
</ui>
"""
        docs = _on(tmp_path, xml)
        line = next(
            item
            for item in docs[0].text.splitlines()
            if item.startswith("Visible texts:")
        )
        payload = line.split("Visible texts: ", 1)[1]
        assert len(payload) <= VISIBLE_TEXT_CHAR_CAP
        assert payload.endswith("[...]")
        assert title not in payload
        assert payload.startswith("T" * 20)

    def test_visible_list_trims_a_cut_separator(self, tmp_path):
        first = "A" * (VISIBLE_TEXT_CHAR_CAP - 7)
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>{first}</string></property>
  <widget class="QLabel" name="shortLabel">
   <property name="text"><string>B</string></property>
  </widget>
  <widget class="QLabel" name="lateLabel">
   <property name="text"><string>{"C" * 40}</string></property>
  </widget>
 </widget>
</ui>
"""
        docs = _on(tmp_path, xml)
        line = next(
            item
            for item in _by_type(docs, "ui_form_header")[0].text.splitlines()
            if item.startswith("Visible texts:")
        )
        payload = line.split("Visible texts: ", 1)[1]
        assert len(payload) <= VISIBLE_TEXT_CHAR_CAP
        assert payload.endswith("[...]")
        assert "C" * 40 not in payload
        _assert_no_loss(xml, docs)

    def test_actions_custom_widgets_and_non_text_items(self, tmp_path):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <widget class="QComboBox" name="statusCombo">
   <attribute name="toolBarArea"><string>TopToolBarArea</string></attribute>
   <item>
    <property name="icon"><string>icon.png</string></property>
    <property name="text"><string>Open</string></property>
   </item>
  </widget>
  <action name="actionTip">
   <property name="toolTip"><string>Hover help</string></property>
  </action>
  <action name="actionBare"/>
  <action/>
 </widget>
 <customwidgets>
  <customwidget>
   <class>DateField</class>
   <extends>QWidget</extends>
   <header>datefield.h</header>
  </customwidget>
 </customwidgets>
</ui>
"""
        docs = _on(tmp_path, xml)
        header = _by_type(docs, "ui_form_header")[0].text
        assert "DateField extends QWidget (datefield.h)" in header
        assert "actionTip: toolTip: Hover help" in header
        assert "actionBare" in header
        assert "TopToolBarArea" not in header.split("Visible texts:", 1)[-1]
        assert "icon.png" not in _blob(docs).split("Visible texts:", 1)[-1]
        assert "item text: Open" in _blob(docs)
        _assert_no_loss(xml, docs)

    def test_tiny_sibling_does_not_swallow_a_larger_one(self, tmp_path):
        large = "D" * 400
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>OrderDialog</class>
 <widget class="QDialog" name="OrderDialog">
  <property name="windowTitle"><string>Customer details</string></property>
  <layout class="QVBoxLayout" name="verticalLayout">
   <item>
    <widget class="QLabel" name="smallLabel">
     <property name="text"><string>Name</string></property>
    </widget>
   </item>
   <item>
    <widget class="QLabel" name="largeLabel">
     <property name="text"><string>{large}</string></property>
    </widget>
   </item>
  </layout>
 </widget>
</ui>
"""
        docs = _on(tmp_path, xml)
        names = [doc.metadata["object_name"] for doc in docs]
        assert "smallLabel" in names
        assert "largeLabel" in names
        assert not any(
            "smallLabel" in name and "largeLabel" in name for name in names
        )
