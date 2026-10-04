"""Unit tests for System1 rerank ordering and launch commands."""

from types import SimpleNamespace

from shared.system1_rerank import (
    blend_nudge,
    build_system1_body,
    noul_from_response,
    order_by_noul,
    system1_base_url,
    system1_mode,
)
from shared.system1_server import basal_serve_argv, docker_run_args


class _Node:
    def __init__(self, text, file_path, node_type):
        self.metadata = {"file_path": file_path, "node_type": node_type}
        self._text = text

    def get_content(self):
        return self._text


def _wrap(text, file_path, node_type):
    return SimpleNamespace(score=0.1, node=_Node(text, file_path, node_type))


def test_mode_off_and_aliases():
    assert system1_mode(SimpleNamespace()) == "off"
    assert system1_mode(SimpleNamespace(SYSTEM1_MODE="disabled")) == "off"
    assert system1_mode(SimpleNamespace(SYSTEM1_MODE="gpu")) == "gpu"
    assert system1_mode(SimpleNamespace(SYSTEM1_MODE="CPU")) == "cpu"
    assert system1_mode(SimpleNamespace(SYSTEM1_MODE="remote")) == "remote"
    assert system1_mode(SimpleNamespace(SYSTEM1_MODE="nope")) == "off"


def test_url_derivation():
    gpu = SimpleNamespace(SYSTEM1_MODE="gpu", SYSTEM1_PORT=8095, SYSTEM1_URL=None)
    assert system1_base_url(gpu) == "http://127.0.0.1:8095"
    remote = SimpleNamespace(SYSTEM1_MODE="remote", SYSTEM1_URL="http://ao:8095/")
    assert system1_base_url(remote) == "http://ao:8095"
    assert system1_base_url(SimpleNamespace(SYSTEM1_MODE="off")) is None


def test_body_is_pointwise_and_omits_hybrid_score():
    cfg = SimpleNamespace(SYSTEM1_MODEL="Remek/basal-1.5-mini", SYSTEM1_CHUNK_CHARS=20)
    node = _wrap("TdmMain is a data module with many methods", "MainDM.pas", "class_summary")
    body = build_system1_body("What is TdmMain?", node, cfg)
    assert body["model"] == "Remek/basal-1.5-mini"
    assert body["questions"]["defines"]["type"] == "noul"
    assert "score" not in body["state"]
    assert body["state"]["file"] == "MainDM.pas"
    assert len(body["state"]["text"]) == 20


def test_blend_body_asks_overview_and_unit():
    cfg = SimpleNamespace(SYSTEM1_MODEL="m", SYSTEM1_STRATEGY="blend", SYSTEM1_CHUNK_CHARS=50)
    node = _wrap("class TdmMain", "MainDM.pas", "class_summary")
    body = build_system1_body("What is TdmMain?", node, cfg)
    assert set(body["questions"]) == {"overview", "unit"}
    assert "score" not in body["state"]
    assert blend_nudge(0.5, 0.5, cfg) == 0.0
    assert blend_nudge(1.0, 1.0, cfg) > blend_nudge(0.0, 0.0, cfg)


def test_noul_parse_and_order():
    assert noul_from_response({"answers": {"defines": {"noul": 0.2}}}) == 0.2
    assert noul_from_response({"answers": {}}) is None
    nodes = ["mention", "definition", "other"]
    ordered = order_by_noul(nodes, [0.1, 0.9, 0.1], top_k=2)
    assert ordered == ["definition", "mention"]


def test_gpu_and_cpu_commands():
    gpu = SimpleNamespace(
        SYSTEM1_MODE="gpu",
        SYSTEM1_MODEL="Remek/basal-1.5-mini",
        SYSTEM1_GPU="1",
        SYSTEM1_PORT=8095,
        SYSTEM1_BIN="basal-serve",
        SYSTEM1_DOCKER_IMAGE="basal-serve:local",
        SYSTEM1_DOCKER_CONTAINER=None,
    )
    assert basal_serve_argv(gpu)[:4] == [
        "basal-serve",
        "--model",
        "Remek/basal-1.5-mini",
        "--mode",
    ]
    assert "fast" in basal_serve_argv(gpu)
    gpu_args = docker_run_args(gpu)
    assert "--gpus" in gpu_args
    assert "device=1" in gpu_args
    assert "CUDA_VISIBLE_DEVICES=1" in gpu_args

    cpu = SimpleNamespace(
        SYSTEM1_MODE="cpu",
        SYSTEM1_MODEL="Remek/basal-1.5-mini",
        SYSTEM1_GPU="1",
        SYSTEM1_PORT=8095,
        SYSTEM1_BIN="basal-serve",
        SYSTEM1_DOCKER_IMAGE="basal-serve:local",
        SYSTEM1_DOCKER_CONTAINER=None,
    )
    assert "eager" in basal_serve_argv(cpu)
    cpu_args = docker_run_args(cpu)
    assert "--gpus" not in cpu_args
    assert "CUDA_VISIBLE_DEVICES=" in cpu_args
