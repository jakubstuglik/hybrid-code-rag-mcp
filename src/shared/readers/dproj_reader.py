"""
Delphi project file reader (.dproj) using XML parsing with MSBuild namespace.

Extracts project metadata, build configurations, and unit references from
Delphi .dproj files. Handles the MSBuild XML namespace and BOM encoding.

Chunking strategy:
- One dproj_project_overview chunk: project name, GUID, MainSource, framework,
  platform, version info, compiler settings summary.
- One dproj_build_config chunk per named configuration: Release, Debug, etc.
  Includes DCC_Define, DCC_DcuOutput, and other compiler settings.
- Multiple dproj_unit_group chunks: DCCReference items grouped into batches
  of ~25, with unit->form mappings preserved. This turns 1716 individual
  references into ~69 searchable chunks.
- Context prefix on every chunk: // Project: <stem> (<filename>)
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Dict

from llama_index.core import Document
from llama_index.core.schema import TextNode

from shared.readers._base import BaseFileReader, get_file_datetime, node_from_doc
from shared.log import log_warn


# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────

# MSBuild XML namespace used in all .dproj files
_NS = "http://schemas.microsoft.com/developer/msbuild/2003"
_NSP = f"{{{_NS}}}"

# Number of DCCReference items per group chunk
REFS_PER_GROUP = 25

# Minimum chunk content size (chars)
MIN_CHUNK_SIZE = 40


# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _context_prefix(file_name: str, project_stem: str) -> str:
    """Build context prefix line for a chunk."""
    return f"// Project: {project_stem} ({file_name})"


def _ns(tag: str) -> str:
    """Wrap a tag name with the MSBuild namespace."""
    return f"{_NSP}{tag}"


def _find_text(parent: ET.Element, tag: str) -> str:
    """Find a child element by tag (with namespace) and return its text, or ''."""
    elem = parent.find(_ns(tag))
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""


def _extract_condition_config_name(condition: str) -> str:
    """Extract a human-readable config name from a Condition attribute.

    Examples:
        "'$(Config)'=='Release' or '$(Cfg_1)'!=''" -> "Release"
        "'$(Config)'=='Debug' or '$(Cfg_2)'!=''" -> "Debug"
        "'$(Base)'!=''" -> "Base"
        "'$(Platform)'=='Win32' and '$(Cfg_1)'=='true'..." -> "Cfg_1_Win32"
    """
    if not condition:
        return ""

    m = re.search(r"\$\(Config\)'\s*==\s*'([^']+)'", condition)
    if m:
        return m.group(1)

    # Try Platform + Cfg combination
    platform_m = re.search(r"\$\(Platform\)'\s*==\s*'([^']+)'", condition)
    cfg_m = re.search(r"\$\((Cfg_\d+)\)'\s*==\s*'true'", condition)
    if platform_m and cfg_m:
        return f"{cfg_m.group(1)}_{platform_m.group(1)}"

    # Try Base/Base_Win32 etc.
    base_m = re.search(r"\$\((Base(?:_\w+)?)\)'\s*!=\s*''", condition)
    if base_m:
        return base_m.group(1)

    # Fallback: return first Cfg_ reference
    cfg_any = re.search(r"\$\((Cfg_\d+(?:_\w+)?)\)", condition)
    if cfg_any:
        return cfg_any.group(1)

    return condition[:60]


def _build_cfg_name_map(prop_groups: List[ET.Element]) -> Dict[str, str]:
    """Build a mapping from Cfg_N codes to human-readable config names.

    Scans PropertyGroups for conditions like:
        '$(Config)'=='Release' or '$(Cfg_1)'!=''
    and extracts {Cfg_1: Release, Cfg_2: Debug, ...}.

    Returns:
        Dict mapping Cfg_N code to config name, e.g. {"Cfg_1": "Release"}.
    """
    cfg_map: Dict[str, str] = {}
    for pg in prop_groups:
        condition = pg.get("Condition", "")
        if not condition:
            continue
        # Match: '$(Config)'=='Name' or '$(Cfg_N)'!=''
        config_m = re.search(r"\$\(Config\)'\s*==\s*'([^']+)'", condition)
        cfg_m = re.search(r"\$\((Cfg_\d+)\)'\s*!=\s*''", condition)
        if config_m and cfg_m:
            cfg_map[cfg_m.group(1)] = config_m.group(1)
    return cfg_map


def _resolve_config_name(raw_name: str, cfg_map: Dict[str, str]) -> str:
    """Resolve a config name from Cfg_N code to human-readable name.

    Examples (given cfg_map = {"Cfg_1": "Release", "Cfg_2": "Debug"}):
        "Cfg_1" -> "Release"
        "Cfg_1_Win32" -> "Release_Win32"
        "Cfg_2" -> "Debug"
        "Release" -> "Release"  (pass-through)
        "Base" -> "Base"  (pass-through)
    """
    if not raw_name.startswith("Cfg_"):
        return raw_name

    # Check for exact match first: Cfg_1
    if raw_name in cfg_map:
        return cfg_map[raw_name]

    # Check for platform suffix: Cfg_1_Win32 -> split on first _ after Cfg_N
    parts = raw_name.split("_", 2)  # ["Cfg", "1", "Win32"] or ["Cfg", "1"]
    if len(parts) >= 2:
        cfg_code = f"Cfg_{parts[1]}"
        if cfg_code in cfg_map:
            suffix = raw_name[len(cfg_code) :]  # e.g. "_Win32"
            return cfg_map[cfg_code] + suffix

    return raw_name


def _format_ref_line(ref_elem: ET.Element) -> str:
    """Format a DCCReference element as a readable line.

    Example outputs:
        "MainTurdus.pas -> Form: frmMainTurdus"
        "..\\Common\\FileLog\\FileLog.pas"
        "TUserEditorFrame.pas -> Form: frameUser (TFrame)"
    """
    include = ref_elem.get("Include", "")
    form = _find_text(ref_elem, "Form")
    design_class = _find_text(ref_elem, "DesignClass")

    line = include
    if form:
        line += f" -> Form: {form}"
        if design_class:
            line += f" ({design_class})"
    return line


# ────────────────────────────────────────────────
# Reader
# ────────────────────────────────────────────────


class DPROJFileReader(BaseFileReader):
    """
    Extracts structured chunks from Delphi .dproj XML files.

    Handles MSBuild namespace and BOM encoding. Produces:
    - dproj_project_overview: project metadata summary
    - dproj_build_config: one per build configuration
    - dproj_unit_group: grouped DCCReference batches
    """

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        documents: List[Document] = []
        content: Optional[str] = None
        file_path_str = str(file)
        file_name = file.name
        project_stem = file.stem

        # ── Parse XML (handle BOM) ──
        try:
            try:
                with open(file, "r", encoding="utf-8-sig") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            root = ET.fromstring(content)
        except ET.ParseError as e:
            log_warn(f"XML parse error for {file}: {e}")
            if content:
                documents.append(
                    Document(
                        text=content[:5000],
                        metadata={
                            "file_path": file_path_str,
                            "node_type": "raw_dproj",
                            "parse_error": str(e),
                            **get_file_datetime(file),
                        },
                    )
                )
            return documents
        except Exception as e:
            log_warn(f"Could not read {file}: {e}")
            return []

        file_datetime = get_file_datetime(file)
        prefix = _context_prefix(file_name, project_stem)

        # ── Extract project overview info ──
        overview_lines: List[str] = [prefix]

        # Find the first PropertyGroup (no Condition = base project properties)
        all_prop_groups = root.findall(_ns("PropertyGroup"))

        # Project metadata from the first (base) PropertyGroup
        project_guid = ""
        main_source = ""
        default_config = ""
        framework_type = ""
        platform = ""
        project_version = ""
        app_type = ""
        project_name = project_stem  # Default to file stem

        if all_prop_groups:
            base_pg = all_prop_groups[0]
            project_guid = _find_text(base_pg, "ProjectGuid")
            main_source = _find_text(base_pg, "MainSource")
            default_config_elem = base_pg.find(_ns("Config"))
            if default_config_elem is not None and default_config_elem.text:
                default_config = default_config_elem.text.strip()
            framework_type = _find_text(base_pg, "FrameworkType")
            platform_elem = base_pg.find(_ns("Platform"))
            if platform_elem is not None and platform_elem.text:
                platform = platform_elem.text.strip()
            project_version = _find_text(base_pg, "ProjectVersion")
            app_type = _find_text(base_pg, "AppType")

        overview_lines.append(f"Delphi project: {project_name}")
        if project_guid:
            overview_lines.append(f"GUID: {project_guid}")
        if main_source:
            overview_lines.append(f"Main source: {main_source}")
        if framework_type:
            overview_lines.append(f"Framework: {framework_type}")
        if app_type:
            overview_lines.append(f"Application type: {app_type}")
        if platform:
            overview_lines.append(f"Default platform: {platform}")
        if default_config:
            overview_lines.append(f"Default configuration: {default_config}")
        if project_version:
            overview_lines.append(f"Project version: {project_version}")

        # Version info and base defines from the '$(Base)'!='' PropertyGroup.
        # There can be multiple PGs matching (e.g. '$(Config)'=='Base' or '$(Base)'!=''
        # vs just '$(Base)'!=''). The one with VerInfo_Keys is the one we want.
        ver_info_keys = ""
        sanitized_name = ""
        for pg in all_prop_groups:
            condition = pg.get("Condition", "")
            if not condition:
                continue
            if "'$(Base)'!=''" in condition and "Platform" not in condition:
                vik = _find_text(pg, "VerInfo_Keys")
                sn = _find_text(pg, "SanitizedProjectName")
                dcc = _find_text(pg, "DCC_Define")
                # Accept this PG if it has VerInfo or DCC_Define (skip empty ones)
                if vik or dcc:
                    ver_info_keys = vik
                    sanitized_name = sn
                    if dcc:
                        overview_lines.append(f"Base defines: {dcc}")
                    break

        if sanitized_name and sanitized_name != project_stem:
            overview_lines.append(f"Sanitized name: {sanitized_name}")
        if ver_info_keys:
            # Extract key info from the VerInfo string
            for part in ver_info_keys.split(";"):
                if "=" in part:
                    key, val = part.split("=", 1)
                    if val and key in (
                        "CompanyName",
                        "ProductName",
                        "FileVersion",
                        "FileDescription",
                    ):
                        overview_lines.append(f"  {key}: {val}")

        # ── Count items for overview ──
        item_groups = root.findall(_ns("ItemGroup"))
        total_dcc_refs = 0
        total_forms = 0
        for ig in item_groups:
            for child in ig:
                local_tag = child.tag.replace(_NSP, "")
                if local_tag == "DCCReference":
                    total_dcc_refs += 1
                    form = _find_text(child, "Form")
                    if form:
                        total_forms += 1

        if total_dcc_refs:
            overview_lines.append(
                f"Units: {total_dcc_refs} DCCReferences"
                + (f" ({total_forms} with forms)" if total_forms else "")
            )

        # Build Cfg_N -> human name mapping (e.g. Cfg_1 -> Release)
        cfg_map = _build_cfg_name_map(all_prop_groups)

        # Count build configs (using resolved names, deduplicating)
        config_names: List[str] = []
        for pg in all_prop_groups:
            condition = pg.get("Condition", "")
            if not condition:
                continue
            raw_name = _extract_condition_config_name(condition)
            resolved = _resolve_config_name(raw_name, cfg_map) if raw_name else ""
            if resolved and resolved not in config_names:
                config_names.append(resolved)

        if config_names:
            overview_lines.append(f"Build configurations: {', '.join(config_names)}")

        # ── Emit project overview ──
        overview_text = "\n".join(overview_lines)
        if len(overview_text.strip()) >= MIN_CHUNK_SIZE:
            documents.append(
                Document(
                    text=overview_text,
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "dproj_project_overview",
                        "unit_name": project_stem,
                        "project_name": project_name,
                        "project_guid": project_guid,
                        "main_source": main_source,
                        "framework_type": framework_type,
                        "unit_count": total_dcc_refs,
                        **file_datetime,
                    },
                )
            )

        # ── Build configuration chunks ──
        # Only emit configs that have meaningful settings (DCC_Define, etc.)
        for pg in all_prop_groups:
            condition = pg.get("Condition", "")
            if not condition:
                continue

            raw_config_name = _extract_condition_config_name(condition)
            if not raw_config_name:
                continue

            config_name = _resolve_config_name(raw_config_name, cfg_map)

            # Skip platform-only or base variants that just set flags
            # Only emit configs with interesting compiler settings
            config_lines: List[str] = []
            for child in pg:
                local_tag = child.tag.replace(_NSP, "")
                if child.text and child.text.strip():
                    value = child.text.strip()
                    # Skip boolean flags and auto-generated stuff
                    if value.lower() in ("true", "false") and local_tag in (
                        "Base",
                        "CfgParent",
                        raw_config_name,
                    ):
                        continue
                    # Skip internal Cfg hierarchy flags
                    if local_tag.startswith("Cfg_") or local_tag in (
                        "Base",
                        "CfgParent",
                        "Base_Win32",
                        "Base_Win64",
                    ):
                        continue
                    config_lines.append(f"  {local_tag}: {value}")

            if config_lines:
                chunk_lines = [prefix]
                chunk_lines.append(f"// Build configuration: {config_name}")
                if condition:
                    chunk_lines.append(f"// Condition: {condition}")
                chunk_lines.append("")
                chunk_lines.extend(config_lines)

                chunk_text = "\n".join(chunk_lines)
                if len(chunk_text.strip()) >= MIN_CHUNK_SIZE:
                    documents.append(
                        Document(
                            text=chunk_text,
                            metadata={
                                "file_path": file_path_str,
                                "node_type": "dproj_build_config",
                                "unit_name": project_stem,
                                "config_name": config_name,
                                "condition": condition,
                                **file_datetime,
                            },
                        )
                    )

        # ── DCCReference groups ──
        all_refs: List[ET.Element] = []
        for ig in item_groups:
            for child in ig:
                local_tag = child.tag.replace(_NSP, "")
                if local_tag == "DCCReference":
                    all_refs.append(child)

        # Group into batches
        for batch_start in range(0, len(all_refs), REFS_PER_GROUP):
            batch = all_refs[batch_start : batch_start + REFS_PER_GROUP]
            batch_num = batch_start // REFS_PER_GROUP + 1
            total_batches = (len(all_refs) + REFS_PER_GROUP - 1) // REFS_PER_GROUP

            chunk_lines = [prefix]
            chunk_lines.append(
                f"// Unit references (group {batch_num}/{total_batches})"
            )
            chunk_lines.append("")

            form_count = 0
            for ref in batch:
                line = _format_ref_line(ref)
                chunk_lines.append(f"  {line}")
                if _find_text(ref, "Form"):
                    form_count += 1

            chunk_text = "\n".join(chunk_lines)
            if len(chunk_text.strip()) >= MIN_CHUNK_SIZE:
                documents.append(
                    Document(
                        text=chunk_text,
                        metadata={
                            "file_path": file_path_str,
                            "node_type": "dproj_unit_group",
                            "unit_name": project_stem,
                            "group_number": batch_num,
                            "group_total": total_batches,
                            "ref_count": len(batch),
                            "form_count": form_count,
                            **file_datetime,
                        },
                    )
                )

        # ── Other ItemGroup items (non-DCCReference) ──
        # DelphiCompile, RcCompile, BuildConfiguration, None, etc.
        other_items: List[str] = []
        for ig in item_groups:
            for child in ig:
                local_tag = child.tag.replace(_NSP, "")
                if local_tag == "DCCReference":
                    continue
                include = child.get("Include", "")
                if include:
                    form = _find_text(child, "Form")
                    if form:
                        other_items.append(f"  {local_tag}: {include} -> {form}")
                    else:
                        other_items.append(f"  {local_tag}: {include}")
                elif local_tag == "BuildConfiguration" and child.get("Include"):
                    bc_include = child.get("Include", "")
                    other_items.append(f"  BuildConfiguration: {bc_include}")

        if other_items:
            chunk_lines = [prefix]
            chunk_lines.append("// Other project items")
            chunk_lines.append("")
            chunk_lines.extend(other_items)
            chunk_text = "\n".join(chunk_lines)
            if len(chunk_text.strip()) >= MIN_CHUNK_SIZE:
                documents.append(
                    Document(
                        text=chunk_text,
                        metadata={
                            "file_path": file_path_str,
                            "node_type": "dproj_unit_group",
                            "unit_name": project_stem,
                            "group_number": 0,
                            "group_total": 0,
                            "ref_count": len(other_items),
                            **file_datetime,
                        },
                    )
                )

        # ── Fallback ──
        if not documents and content:
            documents.append(
                Document(
                    text=content[:8000],
                    metadata={
                        "file_path": file_path_str,
                        "node_type": "full_file",
                        "unit_name": project_stem,
                        **file_datetime,
                    },
                )
            )

        return documents

    def load_nodes(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[TextNode]:
        """Parse DPROJ file and return TextNodes ready for indexing."""
        docs = self.load_data(file, extra_info)
        return [node_from_doc(doc) for doc in docs]
