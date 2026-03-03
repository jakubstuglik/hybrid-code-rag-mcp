1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
3. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
4. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
5. Persistent MCP server setup - TESTING
6. Chunking of fr3 - why always two chunks? Check other XMLs too. Should be way more
7. Chunking SQLs - is there a way to chunk them more? how are they chunked now? View chunks for some files and check
8. **Change indexing script mode of operation: there should be workers (definitely more than one) chunking files and feeding it via some queue (maybe some robust queue implementation which is thread safe) to 2 (or more - test) workers making embedding (inference) on sentence transformer and upstarting it into vector store. We want max GPU utilization and it waits for chunks to be delivered because it's sequential chunk gen->inference. In this scenario we also need some queue for persisting changes to manifest and worker which will do that**