1. Verify requirements, very specific pytorch packages required for CUDA and ROC to run. Tidy up.
3. Smaller models, what is the quality difference? Save generated vector db on bigger model first!!!
4. Different parameters on models to fit in VRAM and not used shared GPU memory etc.
   5. Persistent MCP server setup - TESTING
       - Implement **dense and sparse hybrid** in FastMCP and **Reciprocal Rank Fusion**, example code:
         ```from fastmcp import FastMCP
         from FlagEmbedding import BGEM3FlagModel
         import qdrant_client # Przykładowa baza wspierająca hybrydę

         mcp = FastMCP("SourceCodeRAG")
         # Inicjalizacja modelu BGE-M3 (obsługuje gęste i rzadkie wektory)
         model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
    
         @mcp.tool()
         async def search_code(query: str):
         """Przeszukuje bazę kodów Pascal i SQL."""
         # 1. Generowanie wektorów (Dense + Sparse) za jednym razem
         output = model.encode(query, return_dense=True, return_sparse=True)
         dense_vec = output['dense_vecs']
         sparse_vec = output['lexical_weights'] # Kluczowe dla Pascal/SQL
    
             # 2. Zapytanie hybrydowe do bazy (np. Qdrant lub Milvus)
             # Tutaj Twoja baza łączy oba wyniki (RRF) i zwraca chunki
             results = db.search_hybrid(dense=dense_vec, sparse=sparse_vec)
        
             return format_results_for_opencode(results)
         ```
       - Index with **TWO** indexes for collection in QDrant: sparse and dense 
         ```from qdrant_client import QdrantClient, models
    
            client = QdrantClient("localhost", port=6333)
    
            client.create_collection(
            collection_name="source_code_rag",
           # Indeks dla wektorów gęstych (Semantyka)
           vectors_config={
             "dense": models.VectorParams(
             size=1024,              # Wymiar dla BGE-M3
             distance=models.Distance.COSINE
             )
           },
           # Indeks dla wektorów rzadkich (Słowa kluczowe/SQL/Pascal)
           sparse_vectors_config={
             "sparse": models.SparseVectorParams(
             index=models.SparseIndexParams(
             on_disk=True,       # Oszczędność RAM przy dużych zbiorach
           )
           )
           }
         )
       ```
      ```# Załóżmy, że model_output to wynik z model.encode()
         # dense_vector = model_output['dense_vecs']
         # sparse_vector = model_output['lexical_weights']

         # Konwersja sparse dict na format Qdrant
         indices = [int(k) for k in sparse_vector.keys()]
         values = [float(v) for v in sparse_vector.values()]
    
         client.upsert(
         collection_name="source_code_rag",
         points=[
         models.PointStruct(
         id=1,
         payload={"text": "procedure CalculateTax...", "lang": "pascal"},
         vector={
            "dense": dense_vector,
            "sparse": models.SparseVector(indices=indices, values=values)
         }
        )
        ]
      )
      ```
      ```
      results = client.query_points(
      collection_name="source_code_rag",
      prefetch=[
      # Szukaj semantycznie
      models.Prefetch(query=dense_query_vector, using="dense", limit=20),
      # Szukaj po słowach kluczowych (Pascal/SQL)
      models.Prefetch(
      query=models.SparseVector(indices=q_indices, values=q_values),
      using="sparse",
       limit=20
      ),
      ],
      query=models.FusionQuery(fusion=models.Fusion.RRF), # Łączenie wyników
      limit=10
      )
      ```

6. Chunking of fr3 - why always two chunks? Check other XMLs too. Should be way more
7. Chunking SQLs - is there a way to chunk them more? how are they chunked now? View chunks for some files and check
8. **Change indexing script mode of operation: there should be workers (definitely more than one) chunking files and feeding it via some queue (maybe some robust queue implementation which is thread safe) to 2 (or more - test) workers making embedding (inference) on sentence transformer and upstarting it into vector store. We want max GPU utilization and it waits for chunks to be delivered because it's sequential chunk gen->inference. In this scenario we also need some queue for persisting changes to manifest and worker which will do that**