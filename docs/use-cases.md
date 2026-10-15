# Use Cases

```mermaid
flowchart LR
    Client[Client] --> B[Books manage]
    Client --> A[Authors manage]
    Client --> V[Publishers manage]
    B -->|assign existing references| A
    B -->|assign existing reference| V
```

Books can be created, searched, read, updated and deleted. Authors and publishers are
managed independently; a referenced author or publisher cannot be deleted while books
still refer to it.
