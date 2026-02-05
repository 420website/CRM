
QUERY_POSTGRES ={
  "name": "query_postgres",
  "description": "Run a read-only SQL query against the PostgreSQL database",
  "input_schema": {
    "type": "object",
    "properties": {
      "sql": {
        "type": "string",
        "description": "A SELECT-only SQL query that follows the provided schema"
      }
    },
    "required": ["sql"]
  }
}


QUERY_MONGODB = {
    "name": "query_mongo",
    "description": "Query MongoDB using aggregation pipeline for data analysis",
    "input_schema": {
        "type": "object",
        "properties": {
            "pipeline": {
                "type": "array",
                "description": "MongoDB aggregation pipeline stages (e.g., [{\"$group\": {\"_id\": \"$Disposition\", \"count\": {\"$sum\": 1}}}])"
            }
        },
        "required": ["pipeline"]
    }
}


