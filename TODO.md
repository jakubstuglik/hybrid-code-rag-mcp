1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
2. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
3. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
# **STALE: Analyze what takes what time during indexing: it is embedding. Probably the problem is that in some cases when we have big chunks to embed then GPU has to garbage collect VRAM and this hangs the process for a long time. Small model is fast because there is a lot of VRAM available. How to do it? Maybe some chunks grouping by size to not exceed some limit with total chunks size in batch? Dynamic batch size also**
# **Change embedding batches groupping: it was supposed to be groupping nodes to batches not to exceed some limit but it actually DROPS small nodes!!! FIX, outline exact desired behavior for AI to implement**
4. Persistent MCP server setup - TESTING
5. Chunking of fr3 - why always two chunks? Check other XMLs too. Should be way more
6. Chunking SQLs - is there a way to chunk them more? how are they chunked now? View chunks for some files and check
7. Include somehow indexed project libraries in specific versions and docs for them from web and/or source codes
8. Tests for informica-rag project
9. Indexing given branches on git repo using .git contents, not bu imdexing full contents bu checking out branch
10. **TESTS**
