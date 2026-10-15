# AI Product Research Agent

An AI-powered product research project that collects, normalizes,
indexes, and retrieves technical product information from **multiple
sources**:

-   **TechSpecs API** --- product specifications retrieved through the
    API.
-   **PDF files** --- product information extracted from local PDF
    documents.
-   **CSV files** --- structured product catalogs loaded from local CSV
    datasets.

The project uses **Qdrant** as a vector database and **Sentence
Transformers** to create 768-dimensional embeddings, enabling semantic
product search combined with structured metadata filters. The
application also uses **FastAPI** and **Google Gemini** as part of its
AI application stack.

> **Project focus:** bring product data from API responses and local
> PDF/CSV files into a searchable system. Exact ingestion paths and
> supported fields depend on the corresponding project modules and
> configuration.

## Contents

-   [Overview](#overview)
-   [Features](#features)
-   [Architecture](#architecture)
-   [Technology stack](#technology-stack)
-   [Data sources](#data-sources)
-   [Product ingestion workflow](#product-ingestion-workflow)
-   [Product search](#product-search)
-   [Project structure](#project-structure)
-   [Requirements](#requirements)
-   [Setup on Windows](#setup-on-windows)
-   [Environment configuration](#environment-configuration)
-   [Run the application](#run-the-application)
-   [Testing](#testing)
-   [Troubleshooting](#troubleshooting)
-   [Security and data quality](#security-and-data-quality)
-   [Roadmap](#roadmap)

## Overview

AI Product Research Agent is designed to make technical product
information easier to collect and search. Instead of relying on a single
source, the project can work with API-sourced product details as well as
local product documents and tabular catalogs.

The intended workflow is to ingest product information, normalize fields
where applicable, generate embeddings, store searchable vectors and
metadata in Qdrant, and retrieve relevant products using a
natural-language query.

Example questions include:

-   "Find a Samsung phone with 8 GB RAM."
-   "Which products support 128 GB storage?"
-   "Find Samsung smartphones released in 2012."
-   "Search the catalog for laptops with a particular processor."
-   "Find product specifications mentioned in an imported PDF or CSV
    catalog."

Results depend on which records have actually been ingested and which
fields are present in the source data.

## Features

-   **Multiple data sources:** TechSpecs API, PDF files, and CSV files.
-   **Product-data normalization:** convert available source fields into
    a consistent structure for search.
-   **Vector embeddings:** represent searchable product text as
    768-dimensional vectors using Sentence Transformers.
-   **Qdrant vector storage:** store product vectors with payload
    metadata.
-   **Semantic retrieval:** search for products using natural-language
    descriptions.
-   **Metadata filtering:** combine semantic similarity with structured
    filters such as brand, RAM, storage, or release year when those
    fields are available and indexed correctly.
-   **FastAPI application:** provide an API interface for application
    functionality.
-   **Test scripts:** exercise product ingestion, listing, and search
    workflows.

## Architecture

``` mermaid
flowchart TD
    A[TechSpecs API] --> D[Parse and normalize product data]
    B[PDF files] --> E[PDF extraction and processing]
    C[CSV files] --> F[CSV loading and processing]
    E --> D
    F --> D
    D --> G[Build searchable product text and metadata]
    G --> H[Sentence Transformers embeddings]
    H --> I[Qdrant vector database]
    G --> I
    J[Natural-language product query] --> K[Query parsing and embedding]
    K --> L[Semantic search plus metadata filters]
    I --> L
    L --> M[Relevant product results]
    M --> N[FastAPI / AI application layer]
```

This diagram shows the overall intended data flow. The exact route and
processing details are determined by the implementation of each
ingestion module.

## Technology stack

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Python                              Core application and
                                      data-processing language

  FastAPI                             HTTP API framework

  TechSpecs API                       External source for technical
                                      product information

  PDF processing module               Extract product information from
                                      PDF files

  CSV processing module               Load structured product records
                                      from CSV files

  Sentence Transformers               Generate local text embeddings

  Qdrant                              Store vectors and product metadata

  Google Gemini                       AI capabilities used by the
                                      application

  `uv`                                Python project and dependency
                                      management

  Pydantic / Python data models       Validate and structure data where
                                      used
  -----------------------------------------------------------------------

## Data sources

### 1. TechSpecs API

The API integration retrieves product records and technical details from
TechSpecs. The ingestion workflow should preserve useful source fields
and normalize them for consistent storage and retrieval.

-   API credentials must be configured according to the environment
    variables used by the project.
-   API access and request limits depend on the TechSpecs account and
    available credits.
-   API ingestion requires network access and valid API credentials.

### 2. PDF files

PDF files can provide product specifications in document form. A PDF
ingestion pipeline generally extracts text, processes it into searchable
content, and stores relevant text and metadata for retrieval.

PDF quality and layout can affect extraction results. Scanned PDFs may
require OCR if OCR is not already included in the configured ingestion
pipeline.

### 3. CSV files

CSV files are useful for structured product catalogs with columns such
as brand, model, price, RAM, storage, processor, release date, and
availability.

CSV processing should preserve structured values when possible. Before
ingestion, check column names, missing values, inconsistent units,
duplicate products, and date formats. Avoid treating a CSV row as
unstructured prose only if the application needs to filter on its
individual fields.

**Important:** PDF and CSV ingestion support depends on the relevant
modules and configured data directories. Confirm the current code and
configuration before assuming a particular filename, directory, or
column schema.

## Product ingestion workflow

The general ingestion process is:

1.  **Load source data** from TechSpecs, a PDF file, or a CSV file.
2.  **Extract and normalize fields** into a consistent product
    representation.
3.  **Prepare searchable text** from the product name, specifications,
    and other useful descriptions.
4.  **Generate an embedding** for the searchable text using the
    configured Sentence Transformers model.
5.  **Build the Qdrant payload** containing product metadata and
    searchable text.
6.  **Store the vector and payload** in the configured Qdrant
    collection.
7.  **Verify ingestion** by listing products or running a search query.

The current local embedding setup uses **768-dimensional vectors**. The
Qdrant collection's vector size must match the embedding model output
dimension.

## Product search

The search workflow can combine two approaches:

-   **Semantic search:** finds products whose embedded descriptions are
    similar to the user's query.
-   **Structured filtering:** narrows results using metadata such as
    brand, RAM, storage, or release year.

For example, a query such as `Samsung phone with 8 GB RAM` can be
interpreted into a brand filter and a RAM filter, then used alongside
vector similarity. Correct results depend on consistent
normalization---for example, storing RAM in a consistent unit such as
megabytes and making sure the query parser uses the same representation.

A product will not be returned merely because it exists in a local JSON,
PDF, or CSV file: it must be successfully processed and ingested into
the collection being searched.

## Project structure

The following is a conceptual guide to key areas mentioned in the
project. Verify exact filenames in the repository because modules can
change as development continues.

``` text
ai-qdrant-agent/
├── app/
│   ├── rag/
│   │   ├── embedding.py
│   │   ├── qdrantdb.py
│   │   └── product_ingestion.py
│   └── tools/
│       └── product_normailzer.py
├── tests and test scripts
├── .env.example
├── pyproject.toml
└── README.md
```

Examples of local data and test fixtures may live in the repository root
or in configured data directories. Keep API credentials and private
environment files out of version control.

## Requirements

-   Windows, Linux, or macOS
-   A supported Python version configured by the project
-   `uv`
-   A running Qdrant instance or a configured Qdrant Cloud endpoint
-   TechSpecs API credentials for live API ingestion
-   Google Gemini credentials for features that call Gemini
-   Local PDF/CSV files if you want to test document or catalog
    ingestion

## Setup on Windows

Open PowerShell and move into the repository directory:

``` powershell
cd C:\Users\shazil_ali\Downloads\ai-qdrant-agent
```

Install `uv` if it is not already installed. Then install the project's
dependencies:

``` powershell
uv sync
```

Create your local environment file using the template if one exists:

``` powershell
Copy-Item .env.example .env
```

If the repository does not contain `.env.example`, create `.env` using
the variable names referenced in the project code. Do not copy example
placeholder values as if they were real credentials.

Start Qdrant using your existing local or cloud setup. Confirm that the
configured Qdrant URL and collection name match the application settings
before running ingestion or search scripts.

## Environment configuration

Use the actual variable names referenced in the code. Common
configuration values in this type of setup include:

  -----------------------------------------------------------------------
  Setting                             Purpose
  ----------------------------------- -----------------------------------
  TechSpecs API key                   Authenticates requests to TechSpecs

  Gemini API key                      Authenticates Gemini requests

  Qdrant URL                          Qdrant server endpoint

  Qdrant collection name              Collection used for product vectors

  Embedding model                     Sentence Transformers model used to
                                      generate vectors
  -----------------------------------------------------------------------

Do not assume these illustrative labels are the exact environment
variable names. Check the project's settings and source code for the
names it actually reads.

Keep `.env` private. If a real key has been committed to Git, revoke or
rotate it rather than only deleting it from the latest commit.

## Run the application

Use the repository's actual FastAPI entry point and configured start
command. For example, if the application module is `app.main` and it
exposes `app`, the command may be:

``` powershell
uv run uvicorn app.main:app --reload
```

If your entry point differs, replace `app.main:app` with the correct
module and application variable. When the server starts, open the local
`/docs` endpoint to inspect the available API routes.

## Testing

Run the test scripts that exist in your current checkout. Examples from
the development workflow include:

``` powershell
uv run python test_product_ingestion.py
uv run python test_list_products.py
uv run python test_product_search_integration.py
```

Run only scripts that are present in your repository.

Recommended checks:

1.  Confirm that the source file or API response loads successfully.
2.  Verify normalized fields such as `product_id`, `brand`, `model`,
    `ram_mb`, `storage_gb`, and `release_year`.
3.  Confirm that the generated embedding dimension is 768.
4.  Verify that Qdrant stores the expected payload and record type.
5.  Search for a product that is known to exist in the selected
    collection.
6.  Test metadata filters separately from semantic similarity.
7.  Use a separate test collection or clearly identified fixture records
    when possible, so test data does not contaminate your main
    collection.

A test that expects two products from 2012 will fail if those products
exist only in a JSON fixture and have not been ingested into the
collection under test.

## Troubleshooting

### TechSpecs API returns HTTP 402 or an API-limit message

This generally indicates that the account has reached a provider-side
usage or credit limit. Check the TechSpecs account and plan. Local
PDF/CSV ingestion or saved-response tests may be used to continue
development without additional API requests, provided those paths are
implemented and configured.

### Qdrant vector dimension mismatch

The collection's configured vector size must match the embedding model
output. This project currently expects 768-dimensional vectors. Do not
change the collection dimension without considering existing stored
vectors and the selected embedding model.

### Search returns zero results

-   Confirm that the product was ingested into the same Qdrant
    collection being searched.
-   Check the payload's `record_type`.
-   Inspect normalized metadata and the exact units used for numeric
    fields.
-   Confirm that the query parser produces the intended filters.
-   Check that release dates were normalized into the expected year
    field.
-   Confirm that a test fixture was actually ingested rather than merely
    saved as a file.

### CSV or PDF products are missing

-   Verify that the ingestion script supports the file format.
-   Check the configured input directory and file path.
-   Inspect parsing/extraction errors and the resulting normalized
    records.
-   Verify that records were saved successfully to Qdrant.
-   For scanned PDFs, confirm whether OCR is required.

### Embedding model warning

Library deprecation warnings may indicate that an API method has been
renamed. Review the warning and update the method when appropriate;
distinguish nonfatal warnings from errors that stop ingestion.

## Security and data quality

-   Never commit `.env` files, API keys, access tokens, or private
    customer data.
-   Validate and normalize external API responses and imported files
    before storing them.
-   Treat text extracted from PDFs and other documents as untrusted
    input.
-   Check duplicate product IDs and define a stable ID strategy for
    records from each source.
-   Keep product metadata and searchable text aligned so filters and
    semantic search agree.
-   Avoid mixing temporary test fixtures into production collections.
-   Respect the terms, rate limits, and licensing conditions of the
    TechSpecs API and any imported data.

## Roadmap

Potential improvements include:

-   Add or refine a unified ingestion interface for API, PDF, and CSV
    sources.
-   Standardize product schemas and numeric units across every source.
-   Add source tracking, ingestion timestamps, and duplicate detection.
-   Create a dedicated test collection and automated ingestion/search
    tests.
-   Improve hybrid retrieval and result ranking.
-   Add clear ingestion summaries and validation reports.
-   Document exact API endpoints, environment variable names, supported
    PDF/CSV schemas, and production deployment steps.

## Contributing

1.  Create a feature branch.
2.  Make a focused change.
3.  Run the relevant ingestion and search tests.
4.  Update this README when commands, configuration, or supported data
    sources change.
5.  Open a pull request describing the change and its verification.

## License

Add the license that applies to this repository. Until a license is
added, do not assume others have permission to reuse or redistribute the
project.
