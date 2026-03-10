"""
Heuristic line-based T-SQL chunker for stored procedures, functions, and DDL.

Replaces the TokenTextSplitter fallback in sql_reader.py with semantically-aware
splitting that understands T-SQL structural patterns:

- GO batch boundaries (absolute splits)
- CREATE PROCEDURE/FUNCTION/TABLE/VIEW detection with parameter extraction
- Dash-separator lines (developer-intended section breaks)
- UNION ALL boundaries within large SELECT chains
- Dynamic SQL block detection (SET @Sql = ... kept together)
- Top-level IF/ELSE/BEGIN/END nesting
- GOTO label targets
- Context prefix on every chunk (procedure name + parameters)

Target chunk sizes:
- Sweet spot: 500-5000 chars
- Maximum before force-split: 12000 chars
- Minimum: 100 chars (skip trivial SET NOCOUNT ON etc.)
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


# ------------------------------------------------
# Constants
# ------------------------------------------------

MIN_CHUNK_CHARS = 100
MAX_CHUNK_CHARS = 12000
FORCE_SPLIT_CHARS = 16000


# ------------------------------------------------
# Compiled regex patterns
# ------------------------------------------------

RE_GO = re.compile(r"^\s*GO\s*$", re.IGNORECASE)

RE_CREATE_OBJECT = re.compile(
    r"^\s*CREATE\s+(PROCEDURE|FUNCTION|TABLE|VIEW|TRIGGER|INDEX)\s+",
    re.IGNORECASE,
)

RE_OBJECT_NAME = re.compile(
    r"(?:CREATE|ALTER)\s+(?:PROCEDURE|FUNCTION|TABLE|VIEW|TRIGGER)\s+"
    r"(\[?\w+\]?\.\[?\w+\]?)",
    re.IGNORECASE,
)

RE_OBJECT_TYPE = re.compile(
    r"(?:CREATE|ALTER)\s+(PROCEDURE|FUNCTION|TABLE|VIEW|TRIGGER)",
    re.IGNORECASE,
)

RE_DASH_SEPARATOR = re.compile(r"^[\s]*-{20,}.*$")

RE_UNION = re.compile(r"^\s*UNION(\s+ALL)?\s*$", re.IGNORECASE)

RE_DYNAMIC_SQL_START = re.compile(
    r"^\s*SET\s+@\w*[Ss]ql\w*\s*=\s*",
    re.IGNORECASE,
)
RE_DYNAMIC_SQL_CONTINUE = re.compile(
    r"^\s*SET\s+@\w*[Ss]ql\w*\s*=\s*@\w*[Ss]ql\w*\s*\+",
    re.IGNORECASE,
)
RE_DYNAMIC_SQL_IF_APPEND = re.compile(
    r"^\s*IF\s+.*\s+SET\s+@\w*[Ss]ql\w*\s*=\s*@\w*[Ss]ql\w*\s*\+",
    re.IGNORECASE,
)

RE_EXECUTE_SQL = re.compile(
    r"^\s*EXEC(?:UTE)?\s*\(\s*@\w*[Ss]ql",
    re.IGNORECASE,
)

RE_IF_BEGIN = re.compile(r"^\s{0,8}IF\s+", re.IGNORECASE)

RE_BEGIN = re.compile(r"^\s{0,8}BEGIN\s*$", re.IGNORECASE)

RE_AS_KEYWORD = re.compile(r"^\s*AS\s*$", re.IGNORECASE)

RE_WITH_EXECUTE = re.compile(
    r"^\s*WITH\s+EXECUTE\s+AS\s+",
    re.IGNORECASE,
)

RE_GOTO_LABEL = re.compile(r"^\s*(\w+)\s*:\s*$")

RE_SET_PREAMBLE = re.compile(
    r"^\s*SET\s+(QUOTED_IDENTIFIER|ANSI_NULLS|ANSI_WARNINGS|NOCOUNT)\s+",
    re.IGNORECASE,
)

RE_DECLARE = re.compile(r"^\s*DECLARE\s+", re.IGNORECASE)

RE_SET_VAR = re.compile(r"^\s*SET\s+@", re.IGNORECASE)

RE_CREATE_TEMP_TABLE = re.compile(
    r"^\s*CREATE\s+TABLE\s+#",
    re.IGNORECASE,
)

RE_ALTER = re.compile(r"^\s*ALTER\s+TABLE\s+", re.IGNORECASE)

RE_INDEX = re.compile(
    r"^\s*CREATE\s+(?:NONCLUSTERED\s+|CLUSTERED\s+)?INDEX\s+",
    re.IGNORECASE,
)

RE_EXEC = re.compile(r"^\s*EXEC\s+", re.IGNORECASE)

RE_SELECT = re.compile(r"^\s*SELECT\s+", re.IGNORECASE)

RE_INSERT_INTO = re.compile(r"^\s*INSERT\s+INTO\s+", re.IGNORECASE)

# ------------------------------------------------
# Data classes
# ------------------------------------------------


@dataclass
class TSqlChunk:
    """A semantically-meaningful chunk of T-SQL code."""
    text: str
    node_type: str
    start_line: int
    end_line: int
    object_name: Optional[str] = None
    object_type: Optional[str] = None
    parameters: Optional[str] = None


# ------------------------------------------------
# Main entry point
# ------------------------------------------------


def chunk_tsql(content: str) -> List[TSqlChunk]:
    """Split T-SQL content into semantically meaningful chunks.

    This is the main entry point. It orchestrates:
    1. Split on GO batch boundaries
    2. Detect object type (procedure/function/table) per batch
    3. For procedures/functions: extract header+declarations, split body at boundaries
    4. For DDL (CREATE TABLE, ALTER, INDEX): group small consecutive batches
    5. Force-split any oversized chunks
    6. Filter out chunks below minimum size

    Args:
        content: Full T-SQL file content as a string.

    Returns:
        List of TSqlChunk objects ready for embedding.
    """
    lines = content.split("\n")
    batches = _split_on_go(lines)

    all_chunks: List[TSqlChunk] = []

    for batch_lines, batch_start in batches:
        if _is_preamble_batch(batch_lines):
            continue

        obj_type, obj_name, params = _detect_object(batch_lines)

        if obj_type in ("PROCEDURE", "FUNCTION"):
            chunks = _chunk_procedure(
                batch_lines, batch_start, obj_type, obj_name, params
            )
            all_chunks.extend(chunks)
        elif obj_type in ("TABLE", "VIEW", "TRIGGER") and not _is_ddl_batch(batch_lines):
            text = "\n".join(batch_lines).strip()
            if text:
                all_chunks.append(TSqlChunk(
                    text=text,
                    node_type=f"create_{obj_type.lower()}",
                    start_line=batch_start + 1,
                    end_line=batch_start + len(batch_lines),
                    object_name=obj_name,
                    object_type=obj_type,
                    parameters=None,
                ))
        elif _is_ddl_batch(batch_lines):
            text = "\n".join(batch_lines).strip()
            if text:
                node_type = _classify_ddl_batch(batch_lines)
                all_chunks.append(TSqlChunk(
                    text=text,
                    node_type=node_type,
                    start_line=batch_start + 1,
                    end_line=batch_start + len(batch_lines),
                    object_name=obj_name,
                    object_type=obj_type,
                    parameters=None,
                ))
        else:
            text = "\n".join(batch_lines).strip()
            if text:
                all_chunks.append(TSqlChunk(
                    text=text,
                    node_type="sql_batch",
                    start_line=batch_start + 1,
                    end_line=batch_start + len(batch_lines),
                    object_name=obj_name,
                    object_type=obj_type,
                    parameters=params,
                ))

    all_chunks = _group_small_ddl_batches(all_chunks)
    all_chunks = _force_split_oversized(all_chunks)
    all_chunks = [c for c in all_chunks if len(c.text.strip()) >= MIN_CHUNK_CHARS]

    return all_chunks

# ------------------------------------------------
# GO batch splitting
# ------------------------------------------------


def _split_on_go(lines: List[str]) -> List[Tuple[List[str], int]]:
    """Split lines into batches separated by GO statements.

    Returns:
        List of (batch_lines, start_line_index) tuples.
        start_line_index is 0-based index into the original lines list.
    """
    batches: List[Tuple[List[str], int]] = []
    current_batch: List[str] = []
    batch_start = 0

    for i, line in enumerate(lines):
        if RE_GO.match(line):
            if current_batch:
                batches.append((current_batch, batch_start))
            current_batch = []
            batch_start = i + 1
        else:
            if not current_batch:
                batch_start = i
            current_batch.append(line)

    if current_batch:
        batches.append((current_batch, batch_start))

    return batches


# ------------------------------------------------
# Batch classification helpers
# ------------------------------------------------


def _is_preamble_batch(batch_lines: List[str]) -> bool:
    """Check if a batch is just SET preamble (QUOTED_IDENTIFIER, ANSI_NULLS, etc.)."""
    for line in batch_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not RE_SET_PREAMBLE.match(stripped):
            return False
    return True


def _is_ddl_batch(batch_lines: List[str]) -> bool:
    """Check if a batch is a DDL statement (ALTER TABLE, CREATE INDEX, EXEC)."""
    for line in batch_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        return bool(
            RE_ALTER.match(stripped)
            or RE_INDEX.match(stripped)
            or RE_EXEC.match(stripped)
        )
    return False


def _classify_ddl_batch(batch_lines: List[str]) -> str:
    """Classify a DDL batch into a node_type string."""
    for line in batch_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if RE_ALTER.match(stripped):
            return "alter_table"
        if RE_INDEX.match(stripped):
            return "create_index"
        if RE_EXEC.match(stripped):
            return "exec_statement"
        break
    return "ddl_statement"

# ------------------------------------------------
# Object detection and parameter extraction
# ------------------------------------------------


def _detect_object(
    batch_lines: List[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Detect the database object type, name, and parameters from a batch.

    Returns:
        (object_type, object_name, parameters_compact) or (None, None, None)
    """
    search_text = "\n".join(batch_lines[:60])

    type_match = RE_OBJECT_TYPE.search(search_text)
    name_match = RE_OBJECT_NAME.search(search_text)

    obj_type = type_match.group(1).upper() if type_match else None
    obj_name = name_match.group(1) if name_match else None

    params = None
    if obj_type in ("PROCEDURE", "FUNCTION"):
        params = _extract_parameters(batch_lines)

    return obj_type, obj_name, params


def _extract_parameters(batch_lines: List[str]) -> Optional[str]:
    """Extract parameter list from a CREATE PROCEDURE/FUNCTION statement.

    Returns a compact one-line summary like:
    "@DateFrom NVARCHAR(23), @DateTo NVARCHAR(23), @Mode TINYINT"
    """
    create_idx = None
    for i, line in enumerate(batch_lines):
        if RE_CREATE_OBJECT.match(line):
            create_idx = i
            break

    if create_idx is None:
        return None

    param_lines: List[str] = []
    in_params = False

    for i in range(create_idx, min(create_idx + 80, len(batch_lines))):
        line = batch_lines[i]
        stripped = line.strip()

        if stripped.startswith("--"):
            continue

        if RE_WITH_EXECUTE.match(stripped):
            continue

        if RE_AS_KEYWORD.match(stripped):
            break

        if RE_BEGIN.match(stripped) and in_params:
            break

        if i == create_idx:
            at_pos = stripped.find("@")
            if at_pos >= 0:
                param_part = stripped[at_pos:]
                param_lines.append(param_part)
                in_params = True
            else:
                paren_pos = stripped.find("(")
                if paren_pos >= 0:
                    after_paren = stripped[paren_pos + 1:].strip()
                    if after_paren:
                        param_lines.append(after_paren)
                    in_params = True
            continue

        if "@" in stripped or in_params:
            in_params = True
            upper = stripped.upper()
            if upper == "AS" or (upper.startswith("AS") and len(upper) > 2 and not upper[2:3].isalpha()):
                break
            if upper == "BEGIN":
                break
            param_lines.append(stripped)

    if not param_lines:
        return None

    raw = " ".join(param_lines)
    raw = re.sub(r"--[^@]*(?=@|$)", " ", raw)
    raw = re.sub(r"\)\s*RETURNS\s+.*", ")", raw, flags=re.IGNORECASE)
    raw = raw.rstrip().rstrip(",").rstrip(")")
    raw = re.sub(r"\s+", " ", raw).strip()

    if len(raw) > 200:
        raw = raw[:197] + "..."

    return raw if raw else None

# ------------------------------------------------
# Procedure/Function chunking
# ------------------------------------------------


def _chunk_procedure(
    batch_lines: List[str],
    batch_start: int,
    obj_type: str,
    obj_name: Optional[str],
    params: Optional[str],
) -> List[TSqlChunk]:
    """Chunk a procedure or function batch into meaningful sections.

    Strategy:
    1. Header chunk: CREATE ... AS + declarations (DECLARE, SET, CREATE TABLE #temp)
    2. Body chunks: split at dash separators, UNION ALL, IF/ELSE, GOTO labels
    3. Each body chunk gets a context prefix with procedure name + parameters
    """
    chunks: List[TSqlChunk] = []
    context_prefix = _make_context_prefix(obj_type, obj_name, params)

    body_start = _find_body_start(batch_lines)

    if body_start is None or body_start >= len(batch_lines):
        text = context_prefix + "\n".join(batch_lines).strip()
        chunks.append(TSqlChunk(
            text=text,
            node_type=f"{obj_type.lower()}_full",
            start_line=batch_start + 1,
            end_line=batch_start + len(batch_lines),
            object_name=obj_name,
            object_type=obj_type,
            parameters=params,
        ))
        return chunks

    decl_end = _find_declarations_end(batch_lines, body_start)

    header_lines = batch_lines[:decl_end]
    header_text = context_prefix + "\n".join(header_lines).strip()
    if header_text.strip():
        chunks.append(TSqlChunk(
            text=header_text,
            node_type=f"{obj_type.lower()}_header",
            start_line=batch_start + 1,
            end_line=batch_start + decl_end,
            object_name=obj_name,
            object_type=obj_type,
            parameters=params,
        ))

    body_lines = batch_lines[decl_end:]
    if not body_lines:
        return chunks

    boundaries = _find_section_boundaries(body_lines)
    sections = _split_at_boundaries(body_lines, boundaries)

    for section_lines, section_offset in sections:
        text = "\n".join(section_lines).strip()
        if not text:
            continue

        text = context_prefix + text

        abs_start = batch_start + decl_end + section_offset
        chunks.append(TSqlChunk(
            text=text,
            node_type=f"{obj_type.lower()}_body",
            start_line=abs_start + 1,
            end_line=abs_start + len(section_lines),
            object_name=obj_name,
            object_type=obj_type,
            parameters=params,
        ))

    return chunks


def _make_context_prefix(
    obj_type: Optional[str],
    obj_name: Optional[str],
    params: Optional[str],
) -> str:
    """Build a context prefix string to prepend to chunks."""
    if not obj_name:
        return ""

    type_label = obj_type.capitalize() if obj_type else "Object"
    lines = [f"-- {type_label}: {obj_name}"]
    if params:
        lines.append(f"-- Parameters: {params}")

    return "\n".join(lines) + "\n"

def _find_body_start(batch_lines: List[str]) -> Optional[int]:
    """Find the line index where the procedure/function body starts.

    This is the line after AS (and possibly BEGIN).
    """
    for i, line in enumerate(batch_lines):
        stripped = line.strip().upper()

        if stripped == "AS":
            for j in range(i + 1, min(i + 3, len(batch_lines))):
                next_stripped = batch_lines[j].strip().upper()
                if next_stripped == "BEGIN":
                    return j + 1
                if next_stripped:
                    return j
            return i + 1

        if stripped == "AS BEGIN":
            return i + 1

        if stripped.endswith(" AS") and len(stripped) > 3:
            for j in range(i + 1, min(i + 3, len(batch_lines))):
                next_stripped = batch_lines[j].strip().upper()
                if next_stripped == "BEGIN":
                    return j + 1
                if next_stripped:
                    return j
            return i + 1

    return None


def _find_declarations_end(batch_lines: List[str], body_start: int) -> int:
    """Find where declarations end and real logic begins, starting from body_start.

    Declarations include: DECLARE, SET @var = ISNULL(...), CREATE TABLE #temp,
    IF ... object_id ... tempdb patterns.
    """
    decl_end = body_start

    for i in range(body_start, len(batch_lines)):
        stripped = batch_lines[i].strip()

        if not stripped or stripped.startswith("--"):
            decl_end = i + 1
            continue

        if RE_DECLARE.match(stripped):
            decl_end = i + 1
            continue

        if RE_SET_VAR.match(stripped):
            decl_end = i + 1
            continue

        if RE_SET_PREAMBLE.match(stripped):
            decl_end = i + 1
            continue

        if RE_CREATE_TEMP_TABLE.match(stripped):
            decl_end = _find_create_table_end(batch_lines, i) + 1
            continue

        if re.match(r"^\s*SELECT\s+@\w+\s*=", stripped, re.IGNORECASE):
            decl_end = i + 1
            continue

        if re.match(r"^\s*IF\s+ISNULL\s*\(\s*@", stripped, re.IGNORECASE):
            decl_end = _find_if_block_end(batch_lines, i) + 1
            continue

        upper = stripped.upper()
        if upper == "BEGIN":
            end_idx = _find_matching_end(batch_lines, i)
            if end_idx is not None and end_idx - i < 15:
                is_init = True
                for j in range(i + 1, end_idx):
                    inner = batch_lines[j].strip()
                    if not inner or inner.startswith("--"):
                        continue
                    if not (RE_SET_VAR.match(inner)
                            or RE_DECLARE.match(inner)
                            or RE_SET_PREAMBLE.match(inner)
                            or inner.upper() in ("BEGIN", "END", "END;")
                            or inner.upper().startswith("IF ")
                            or inner.upper().startswith("ELSE")):
                        is_init = False
                        break
                if is_init:
                    decl_end = end_idx + 1
                    continue

        break

    return decl_end


def _find_create_table_end(batch_lines: List[str], start: int) -> int:
    """Find the end of a CREATE TABLE statement (closing paren)."""
    depth = 0
    for i in range(start, len(batch_lines)):
        line = batch_lines[i]
        for ch in line:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return i
    return start


def _find_if_block_end(batch_lines: List[str], start: int) -> int:
    """Find the end of a simple IF block (single statement or IF...BEGIN...END)."""
    for i in range(start + 1, min(start + 3, len(batch_lines))):
        next_line = batch_lines[i].strip().upper()
        if next_line == "BEGIN":
            end_idx = _find_matching_end(batch_lines, i)
            return end_idx if end_idx is not None else start + 1
        if next_line and not next_line.startswith("--"):
            return i

    return start + 1


def _find_matching_end(batch_lines: List[str], begin_idx: int) -> Optional[int]:
    """Find the END matching a BEGIN at begin_idx."""
    depth = 0
    for i in range(begin_idx, len(batch_lines)):
        stripped = batch_lines[i].strip().upper()
        if stripped == "BEGIN":
            depth += 1
        elif stripped in ("END", "END;", "END ;"):
            depth -= 1
            if depth == 0:
                return i
    return None

# ------------------------------------------------
# Section boundary detection
# ------------------------------------------------


def _find_section_boundaries(body_lines: List[str]) -> List[int]:
    """Find line indices within body_lines where section boundaries occur.

    Boundary types (in priority order):
    1. Dash separator lines (20+ dashes)
    2. UNION ALL on its own line
    3. Top-level GOTO label targets

    Dynamic SQL blocks (SET @Sql = ... EXECUTE(@Sql)) are protected from splitting.

    Returns:
        Sorted list of 0-based line indices within body_lines where splits should occur.
    """
    boundaries: List[int] = []

    protected_ranges = _find_dynamic_sql_ranges(body_lines)

    def _is_protected(idx: int) -> bool:
        for r_start, r_end in protected_ranges:
            if r_start <= idx <= r_end:
                return True
        return False

    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        stripped = line.strip()

        if _is_protected(i):
            i += 1
            continue

        # Dash separator lines
        if RE_DASH_SEPARATOR.match(line):
            boundary_line = i
            while (boundary_line > 0
                   and RE_DASH_SEPARATOR.match(body_lines[boundary_line - 1])):
                boundary_line -= 1
            if boundary_line not in boundaries and boundary_line > 0:
                boundaries.append(boundary_line)
            while i < len(body_lines) and RE_DASH_SEPARATOR.match(body_lines[i]):
                i += 1
            continue

        # UNION ALL on its own line
        if RE_UNION.match(stripped):
            if i > 0:
                boundaries.append(i)
            i += 1
            continue

        # GOTO label targets
        if RE_GOTO_LABEL.match(stripped) and not stripped.upper().startswith("BEGIN"):
            if i > 0:
                boundaries.append(i)
            i += 1
            continue

        i += 1

    boundaries = sorted(set(boundaries))
    return boundaries


def _find_dynamic_sql_ranges(
    body_lines: List[str],
) -> List[Tuple[int, int]]:
    """Find ranges of lines that are dynamic SQL construction blocks.

    These should not be split. A dynamic SQL block starts with
    SET @Sql = ... and ends at EXECUTE(@Sql) or when the pattern breaks.
    """
    ranges: List[Tuple[int, int]] = []
    i = 0

    while i < len(body_lines):
        stripped = body_lines[i].strip()

        if RE_DYNAMIC_SQL_START.match(stripped):
            block_start = i
            block_end = i

            for j in range(i + 1, len(body_lines)):
                jstripped = body_lines[j].strip()

                if not jstripped or jstripped.startswith("--"):
                    block_end = j
                    continue

                if (RE_DYNAMIC_SQL_CONTINUE.match(jstripped)
                        or RE_DYNAMIC_SQL_IF_APPEND.match(jstripped)):
                    block_end = j
                    continue

                if RE_SET_VAR.match(jstripped) and "@sql" in jstripped.lower():
                    block_end = j
                    continue

                if re.match(r"^\s*IF\s+", jstripped, re.IGNORECASE):
                    block_end = j
                    continue

                if RE_EXECUTE_SQL.match(jstripped):
                    block_end = j
                    ranges.append((block_start, block_end))
                    i = j + 1
                    break

                block_end = j - 1
                ranges.append((block_start, block_end))
                i = j
                break
            else:
                ranges.append((block_start, block_end))
                i = block_end + 1
            continue

        i += 1

    return ranges

# ------------------------------------------------
# Section splitting
# ------------------------------------------------


def _split_at_boundaries(
    body_lines: List[str], boundaries: List[int]
) -> List[Tuple[List[str], int]]:
    """Split body_lines at the given boundary indices.

    Returns:
        List of (section_lines, offset_within_body) tuples.
    """
    if not boundaries:
        if body_lines:
            return [(body_lines, 0)]
        return []

    sections: List[Tuple[List[str], int]] = []
    prev = 0

    for boundary in boundaries:
        if boundary > prev:
            sections.append((body_lines[prev:boundary], prev))
        prev = boundary

    if prev < len(body_lines):
        sections.append((body_lines[prev:], prev))

    return sections


# ------------------------------------------------
# DDL grouping
# ------------------------------------------------


def _group_small_ddl_batches(chunks: List[TSqlChunk]) -> List[TSqlChunk]:
    """Group consecutive small DDL chunks (ALTER TABLE, CREATE INDEX, EXEC) into larger ones.

    Small = under MAX_CHUNK_CHARS / 3 chars. This avoids 20+ tiny index/FK chunks.
    """
    ddl_types = {"alter_table", "create_index", "exec_statement", "ddl_statement"}
    threshold = MAX_CHUNK_CHARS // 3

    result: List[TSqlChunk] = []
    group: List[TSqlChunk] = []
    group_size = 0

    def flush_group():
        nonlocal group, group_size
        if not group:
            return
        if len(group) == 1:
            result.append(group[0])
        else:
            combined_text = "\n\n".join(c.text for c in group)
            node_types = {c.node_type for c in group}
            if len(node_types) == 1:
                combined_type = f"{node_types.pop()}_group"
            else:
                combined_type = "ddl_group"
            result.append(TSqlChunk(
                text=combined_text,
                node_type=combined_type,
                start_line=group[0].start_line,
                end_line=group[-1].end_line,
                object_name=group[0].object_name,
                object_type=group[0].object_type,
                parameters=None,
            ))
        group = []
        group_size = 0

    for chunk in chunks:
        if chunk.node_type in ddl_types and len(chunk.text) < threshold:
            if group_size + len(chunk.text) > MAX_CHUNK_CHARS and group:
                flush_group()
            group.append(chunk)
            group_size += len(chunk.text)
        else:
            flush_group()
            result.append(chunk)

    flush_group()
    return result


# ------------------------------------------------
# Force-splitting oversized chunks
# ------------------------------------------------


def _force_split_oversized(chunks: List[TSqlChunk]) -> List[TSqlChunk]:
    """Split any chunks exceeding FORCE_SPLIT_CHARS at the best available boundary."""
    result: List[TSqlChunk] = []

    for chunk in chunks:
        if len(chunk.text) <= FORCE_SPLIT_CHARS:
            result.append(chunk)
            continue

        sub_chunks = _force_split_chunk(chunk)
        result.extend(sub_chunks)

    return result


def _force_split_chunk(chunk: TSqlChunk) -> List[TSqlChunk]:
    """Split an oversized chunk at the best available internal boundary.

    Tries to split at (in order of preference):
    1. Dash separator lines
    2. Blank lines
    3. Lines starting with major SQL keywords (SELECT, INSERT, UPDATE, IF)
    4. Arbitrary midpoint (last resort)
    """
    lines = chunk.text.split("\n")
    total_lines = len(lines)

    if total_lines <= 2:
        return [chunk]

    split_candidates: List[Tuple[int, int]] = []

    running_size = 0
    for i, line in enumerate(lines):
        running_size += len(line) + 1
        if running_size < MIN_CHUNK_CHARS:
            continue
        remaining = len(chunk.text) - running_size
        if remaining < MIN_CHUNK_CHARS:
            continue

        stripped = line.strip()
        if RE_DASH_SEPARATOR.match(line):
            split_candidates.append((i, 1))
        elif not stripped:
            split_candidates.append((i, 2))
        elif RE_SELECT.match(stripped) or RE_INSERT_INTO.match(stripped):
            split_candidates.append((i, 3))
        elif RE_IF_BEGIN.match(stripped):
            split_candidates.append((i, 4))

    if not split_candidates:
        mid = total_lines // 2
        return _do_split(chunk, lines, mid)

    ideal_size = FORCE_SPLIT_CHARS // 2
    best_candidate = None
    best_score = float("inf")

    for idx, priority in split_candidates:
        size_before = sum(len(lines[j]) + 1 for j in range(idx))
        distance = abs(size_before - ideal_size)
        score = distance + priority * 1000
        if score < best_score:
            best_score = score
            best_candidate = idx

    if best_candidate is None:
        return [chunk]

    sub_chunks = _do_split(chunk, lines, best_candidate)

    final: List[TSqlChunk] = []
    for sc in sub_chunks:
        if len(sc.text) > FORCE_SPLIT_CHARS:
            final.extend(_force_split_chunk(sc))
        else:
            final.append(sc)

    return final


def _do_split(
    chunk: TSqlChunk, lines: List[str], split_at: int
) -> List[TSqlChunk]:
    """Split a chunk at the given line index."""
    part1_lines = lines[:split_at]
    part2_lines = lines[split_at:]

    part1_text = "\n".join(part1_lines).strip()
    part2_text = "\n".join(part2_lines).strip()

    result: List[TSqlChunk] = []

    if part1_text:
        result.append(TSqlChunk(
            text=part1_text,
            node_type=chunk.node_type,
            start_line=chunk.start_line,
            end_line=chunk.start_line + split_at - 1,
            object_name=chunk.object_name,
            object_type=chunk.object_type,
            parameters=chunk.parameters,
        ))

    if part2_text:
        prefix = ""
        if chunk.object_name and "body" in chunk.node_type:
            prefix = _make_context_prefix(
                chunk.object_type, chunk.object_name, chunk.parameters
            )

        result.append(TSqlChunk(
            text=prefix + part2_text,
            node_type=chunk.node_type,
            start_line=chunk.start_line + split_at,
            end_line=chunk.end_line,
            object_name=chunk.object_name,
            object_type=chunk.object_type,
            parameters=chunk.parameters,
        ))

    return result
