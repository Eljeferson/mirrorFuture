# Real Twin Console Module — Mirror Future

Forensic image analysis and empirical social digital twin simulation.

## Overview

The **Real Twin Console** combines computer vision forensics with retrieval-augmented social twin simulations:
- **`ForensicAndWhatsappTwinComponent`**:
  - **EXIF & Vision Forensics:** Extracts camera metadata, timestamp, and GPS coordinates while evaluating reputational and privacy risk via Meta Llama 3.2 Vision (11B).
  - **WhatsApp Social Twin:** Evaluates proposed actions or messages against contact behavioral profiles using vector RAG over verified chat history, predicting responses, emotional reactions, and response latency.

## Architecture

1. **Vision Pipeline:**
   - Multi-part file upload with EXIF orientation, lens, and location parsing.
   - Llama 3.2 11B Vision inference for scene classification, reputational vulnerability scoring, and preventive advice.
2. **Social Twin RAG:**
   - Query embedding matching against conversational episodes in Supabase pgvector.
   - In-context persona prompting generating realistic tone, dialectal nuance, and latency estimates.
   - Transparent attribution with expandable historical quotes demonstrating prior evidence.
