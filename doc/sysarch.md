# System Architecture Overview

This document describes the high-level architecture of the Audio Processing API.

The diagram below illustrates the flow of a typical request from the client to the worker nodes and back.

---

## 🧩 Architecture Diagram

```mermaid
flowchart TD
    Client[Client App<br>(Python / Node.js)]
    API[REST API Service]
    Queue[Job Queue]
    Worker[Audio Processing Worker]
    Storage[(Object Storage)]
    Callback[Webhook Receiver]

    Client -->|HTTP POST /jobs| API
    API --> Queue
    Queue --> Worker
    Worker -->|Upload result| Storage
    Worker -->|Send callback| Callback
    Client -->|HTTP GET /jobs/{id}| API
    API -->|Fetch result| Storage
