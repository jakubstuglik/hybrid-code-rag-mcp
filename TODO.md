1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
2. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
3. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
# **Change embedding batches groupping: it was supposed to be groupping nodes to batches not to exceed some limit but it actually DROPS small nodes!!! FIX, outline exact desired behavior for AI to implement**
# **!!!!!! sparse and dense on GPU now but sparse draws 20-30W, does it have smart batch groupping? Almost certainly not. DESIGN AND IMPLEMENT ^^ with dynamic chunk size, smart grouping**
4. Persistent MCP server setup - TESTING
5. Chunking of fr3 - why always two chunks? Check other XMLs too. Should be way more
6. Chunking SQLs - is there a way to chunk them more? how are they chunked now? View chunks for some files and check

# Rebuild README.md - this is now general RAG indexing and MCP project

7. Include somehow indexed project libraries in specific versions and docs for them from web and/or source codes
8. Indexing given branches on git repo using .git contents, not bu imdexing full contents bu checking out branch
9. **TESTS**
