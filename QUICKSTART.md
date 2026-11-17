# Quickstart

Start a local Qdrant, a [Text Embeddings Inference](https://github.com/huggingface/text-embeddings-inference) server, and the hybrid-code-rag-mcp indexer plus MCP server with Docker Compose. It indexes a bundled sample ([ForgeCart](examples/quickstart/sample/), a tiny shopping-cart library) and leaves an MCP endpoint you can query. No Python virtualenv is required.

The default dense model is [`jinaai/jina-embeddings-v2-base-code`](https://huggingface.co/jinaai/jina-embeddings-v2-base-code). BM25 always runs on CPU. With `--gpu` / `-Gpu`, the embedder runs on an NVIDIA GPU. A sourced measurement from one machine is at the end of this page.

Quickstart: start the stack with ./start.sh --repo

https://github.com/user-attachments/assets/3166f503-bc6b-4238-b11a-0443abc7669f

A GPU run looks the same with `./start.sh --gpu --repo ./sample --detach` (or `.\start.ps1 -Gpu -Repo .\sample -Detach`). A recording of that path:


https://github.com/user-attachments/assets/42020e62-c7b3-4bd7-b95b-0553c8cc1436


## Requirements

- Docker Engine with Compose v2 (Docker Desktop on Windows or macOS).
- For `--gpu` / `-Gpu`: a recent NVIDIA driver, and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) on Linux or Docker Desktop with the WSL 2 GPU backend on Windows.

## 1. Start

```bash
git clone https://github.com/jakubstuglik/hybrid-code-rag-mcp.git
cd hybrid-code-rag-mcp/examples/quickstart
./start.sh
```

```powershell
git clone https://github.com/jakubstuglik/hybrid-code-rag-mcp.git
cd hybrid-code-rag-mcp/examples/quickstart
.\start.ps1
```

Or `docker compose up --build` from this directory. The first run builds the app image, pulls Qdrant and the TEI image, downloads the model, indexes the sample, and starts the MCP server. Wait until the `app` service logs that the server is listening. It is then at [http://localhost:8125/mcp](http://localhost:8125/mcp).

Only the MCP port is published on the host (8125 by default; set `MCP_PORT` in `.env` if that port is taken). Qdrant and TEI stay on the Compose network.

## 2. First search

From `examples/quickstart/`, in a second terminal:

```bash
docker compose exec app python examples/quickstart/query.py \
    "how is the discount calculated?"
```

You should see ranked chunks from `examples/quickstart/sample/forgecart/pricing.py`. Other useful queries: `"where is shipment retry handled?"`, `"how are expired sessions handled?"`, `"idempotent refund"`. Index stats: `docker compose exec app python examples/quickstart/query.py --tool get_quickstart_index_state`.

## 3. Connect an MCP client

Point the client at `http://localhost:8125/mcp` (or your `MCP_PORT`).

**Claude Code / Cursor / Cline / Claude Desktop** (`.cursor/mcp.json`, or the same `mcpServers` shape elsewhere):

```json
{
  "mcpServers": {
    "quickstart-rag": {
      "url": "http://localhost:8125/mcp"
    }
  }
}
```

**Grok Build:** `grok mcp add --transport http quickstart-rag http://localhost:8125/mcp`

**OpenCode** (`opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "quickstart-rag": {
      "type": "remote",
      "url": "http://localhost:8125/mcp",
      "oauth": false
    }
  }
}
```

The server exposes `search_quickstart` (`query`, `top_k`) and `get_quickstart_index_state` (no arguments). Clients only send queries; they do not need a GPU, a virtualenv, or the repository path.

## 4. Index your own repository

You do not need to edit any file. Set the source with a start parameter (beats `.env`) or in a `.env` file next to `docker-compose.yml`. Changing the source, or the repo config file, rebuilds the index with `--clear`. If both a path and a URL are set, the URL wins.

`start.sh` and `start.ps1` expose the same options.

| What | Linux (bash) | Windows (PowerShell) |
|---|---|---|
| Local tree | `./start.sh --repo /path/to/your/repo` | `.\start.ps1 -Repo C:\path\to\your\repo` |
| Git URL and ref | `./start.sh --repo https://github.com/org/repo.git --ref main` | `.\start.ps1 -Repo https://github.com/org/repo.git -Ref main` |
| Repo-only config | `./start.sh --repo /path/to/repo --repo-config ./repo_config.py` | `.\start.ps1 -Repo C:\path\to\repo -RepoConfig .\repo_config.py` |
| GPU embedder | `./start.sh --gpu` | `.\start.ps1 -Gpu` |
| Pin one GPU | `./start.sh --gpu-device 1` | `.\start.ps1 -GpuDevice 1` |

`--gpu-device` / `-GpuDevice` implies `--gpu` / `-Gpu`. Without extra compose arguments, both wrappers run `docker compose up --build`.

Copy [examples/quickstart/repo_config.example.py](examples/quickstart/repo_config.example.py) to limit the tree (`SOURCE_DIRS`: subdirectories, extensions, excludes) or to set `MCP_SERVER_NAME`, `MCP_TOOL_NAME`, and `MCP_TOOL_DESCRIPTION`. Paths in that file are relative to the repository root. Infrastructure stays on the CPU or GPU profile; a disallowed key makes startup exit with an error.

Without a repo config, every file under the source root whose suffix is in the list in [examples/quickstart/config.py](examples/quickstart/config.py) is a candidate: `.py`, `.pyi`, `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`, `.mts`, `.cts`, `.tsx`, `.java`, `.kt`, `.kts`, `.groovy`, `.cs`, `.go`, `.rs`, `.php`, `.c`, `.h`, `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh`, `.hxx`, `.ino`, `.pas`, `.dpr`, `.dfm`, `.dproj`, `.sql`, `.ui`, `.hbm.xml`, `.jrxml`, `.fr3`, `.sh`, `.bash`, `.zsh`, `.ps1`, `.psm1`, `.bat`, `.md`, `.txt`, `.json`, `.jsonc`, `.yml`, `.yaml`, `.toml`, `.xml`, `.xsd`, `.wsdl`, `.html`, `.htm`, `.jsp`, `.css`, `.scss`, `.properties`, `.gradle`, `.http`, `.ini`, `.cfg`.

To stop and keep the index: `docker compose down`. To also delete volumes: `docker compose down -v`.

## Advanced

- **MCP port:** `MCP_PORT` in `.env` or the environment. Only this port is published.
- **Repo via environment:** `REPO_PATH=/path/to/repo docker compose up --build`, or `REPO_URL` plus `REPO_REF`. `REPO_CONFIG` needs `docker-compose.repo-config.yml` as well; the wrappers add it for you.
- **Detached, custom project name:** `./start.sh --repo /path/to/repo --project myshop --detach` or `.\start.ps1 -Repo C:\path\to\repo -Project myshop -Detach`. On PowerShell, raw Compose flags (`-p`, `-d`, `-v`) must come after `--`; `powershell.exe -File` does not honour `--`, so prefer `-Project` / `-Detach`.
- **`start.ps1` execution policy:** with the usual `RemoteSigned` policy, `.\start.ps1` runs without `-ExecutionPolicy Bypass` if the file is not marked as coming from the internet (a normal git clone is not). If the policy is `Restricted`, use `powershell -ExecutionPolicy Bypass -File .\start.ps1 ...`.
- **GPU pin on a multi-GPU machine:** `--gpu` with no pin leaves `CUDA_VISIBLE_DEVICES` unset, and TEI uses the first GPU. `--gpu-device` / `GPU_DEVICE` is a 0-based `nvidia-smi` index or a `GPU-...` UUID. On Docker Desktop for Windows, `--gpus device=N` is ignored and every NVIDIA GPU is attached; `GPU_DEVICE` is the pin the CUDA runtime honors. Confirm with `docker compose exec tei nvidia-smi`.
- **Raw Compose GPU:** `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build`. Add `-f docker-compose.gpu-device.yml` when `GPU_DEVICE` is set. Do not add that overlay when `GPU_DEVICE` is empty.

The Compose app uses `QDRANT_MODE = "remote"` and `TEI_MANAGE_DOCKER = False` so it talks to the sibling containers instead of creating its own. For a long-lived host-side install, see the [README Quick Start](README.md#quick-start) and [Configuration](docs/configuration.md).

## Measured

On 2026-11-14, on a Windows 11 laptop (13th Gen Intel Core i9-13980HX, 32 GB RAM, Docker Desktop 29.8.1), a from-scratch CPU run of the bundled sample reached MCP ready in 227 seconds. That included a `docker compose build --no-cache --pull` of the app image (130 s) and a new Hugging Face model-cache volume. Qdrant `v1.17.0` and `text-embeddings-inference:cpu-latest` were already present on the machine (same image IDs as before the run). Peak container RAM (TEI + app + Qdrant) was 2.57 GiB. The app image was 2.41 GB, the TEI CPU image 938 MB, Qdrant 277 MB, and the new model-cache volume 644 MB.

On the same machine and day, a GPU start with `--gpu` (no pin) occupied 1304 MiB on the RTX 4060, and `--gpu-device 1` occupied 1428 MiB on the RTX 3060, each including other workloads already on that GPU (TEI added about 430–440 MiB).
