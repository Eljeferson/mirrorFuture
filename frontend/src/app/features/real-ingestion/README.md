# Real Ingestion Module — Mirror Future

Secure multi-source data ingestion pipeline for real-world user activity, communication patterns, and telemetry.

## Overview

The **Real Ingestion** module enables users to securely upload and process real data sources:
- **WhatsApp Chat Exports:** `.txt` and `.zip` chat histories parsed with regex regex pattern detection and anonymization.
- **Calendar Feeds:** Google Calendar and Outlook `.ics` files providing baseline routine allocations.
- **Developer Telemetry:** GitHub commits, repository activity, and daily coding rhythm analysis.
- **Statistical Dashboard:** Real-time ingestion breakdown showing total messages, unique participants, and time-span coverage.

## Privacy & Security

- **Local Anonymization:** Client-side sanitization of names, phone numbers, and identifying tokens prior to processing.
- **Cryptographic Ephemerality:** In-memory analysis without secondary persistence unless explicitly authorized.
- **One-Click Purge:** Immediate cascade deletion of all user embeddings and profile vectors.
