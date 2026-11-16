# ForgeCart

A tiny, self-contained shopping-cart library used as the sample corpus in
the hybrid-code-rag-mcp CPU quickstart. It is not a real product: the
code exists so you can ask the MCP server questions and see ranked
chunks come back.

The library covers:

- adding and removing cart lines, and computing a total
- coupon and quantity-break discounts (`calculate_discount`)
- stock reservation and restocking
- shipment dispatch with exponential backoff (`retry_shipment`)
- session login and expiry
- charging and idempotent refunds

Licensed under the Apache License, Version 2.0, the same as the parent
repository.
