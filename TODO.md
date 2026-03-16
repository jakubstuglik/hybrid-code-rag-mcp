1. Switched to models specifically for codebases. Faster, test if it is better. What about docs? Can they also be embedded via these models?
2. ## Different hybrid querying testing: RRF, weighted fusion, cascading + rerank, late interaction (ColBERT). QDrant uses Relative Score Fusion (fixed)
3. Include somehow indexed project libraries in specific versions and docs for them from web and/or source codes. Or maybe find available MCP servers for those
and use them to supplement our index with new MCP server search tool?
4. ## More methods for MCP server, e.g. search_method_decl, search_method_def etc. Some sort of documentation for AI agents to know what to use when
5. For SOURCE_DIRS of type git_repo we should have option to check what is to index by git diff. We need to remember commit index in on.
6. Remember on which model QDrant collection was embedded (sparse and dense) to autodetect which model to use on indexing and MCP query embed.
7. Tidy up configs - project config should be in one dir. Indices for them as well, not always in qdrant (it should be purely sources dir). Also it should be in gitignore
8. Tidy up sources, they should all live in src and src_test dirs. Only main config.py should stay in project root. bat helper scripts should go to scripts folder.
Make sure all the paths are updated in scripts, and docs. Make sure opencode.jsonc in ../informica_2_0 is properly updated