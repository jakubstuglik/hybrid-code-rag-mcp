"""Tests for the Qt Designer .ui reader."""

from shared.readers.ui_reader import UiFileReader


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
