# TEI on Intel XPU (Phase 2 — Not Yet Implemented)

## Status

Phase 2 is **deferred**. Phase 1 covers NVIDIA GPU and CPU Docker images only.

## Background

HuggingFace Text Embeddings Inference (TEI) does not provide prebuilt Docker images
for Intel GPUs (Arc, Data Center Max). Running TEI on Intel XPU requires building a
custom Docker image from source with oneAPI/SYCL support.

## What Would Be Needed

### 1. Custom Docker Image Build

TEI's Intel XPU support uses the `sycl` Cargo feature. A Dockerfile would need to:

- Start from an Intel oneAPI base image (e.g., `intel/oneapi-basekit`)
- Install Rust toolchain and Cargo
- Clone the TEI repository
- Build with `cargo build --release --features sycl`
- Install the Intel GPU compute runtime (Level Zero)

### 2. Config Changes

```python
# New TEI image variant for Intel XPU
TEI_DOCKER_IMAGE = "local/tei-intel-xpu:latest"  # Custom-built image
```

The `_detect_tei_image(cfg)` function in `shared/docker_utils.py` would need a third
branch: if no NVIDIA GPU is detected but Intel GPU is present (detectable via
`intel_gpu_top` or `/dev/dri/renderD*` devices), select the Intel XPU image.

### 3. Docker Run Flags

Intel GPU passthrough requires different Docker flags than NVIDIA:

```
docker run --device /dev/dri -v /dev/dri:/dev/dri ...
```

Instead of `--gpus all` used for NVIDIA.

### 4. Vector Compatibility

TEI on Intel XPU would use the same Candle inference engine as TEI on NVIDIA/CPU.
Vectors produced by TEI-Intel-XPU should be compatible with TEI-NVIDIA and TEI-CPU
(all are in the `"tei"` provenance family).

This needs verification — numerical differences between SYCL and CUDA backends could
potentially produce slightly different embeddings. Testing would be needed to confirm
cross-backend compatibility within the TEI family.

## Prerequisites

- Intel Arc A-series or Data Center GPU Max series
- Intel GPU compute drivers (Level Zero runtime)
- Docker with Intel GPU passthrough support
- oneAPI Base Toolkit (for the build)

## References

- [TEI GitHub — Intel GPU support](https://github.com/huggingface/text-embeddings-inference)
- [Intel oneAPI Docker images](https://hub.docker.com/r/intel/oneapi-basekit)
- [Intel GPU compute runtime](https://github.com/intel/compute-runtime)
