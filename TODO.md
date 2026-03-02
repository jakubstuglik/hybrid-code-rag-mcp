1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
2. Index refresh on modified sources, not embedding from scratch!!!!
3. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
4. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
5. Persistent MCP server setup
6. Qdrant Vector database setup for parallel embedding