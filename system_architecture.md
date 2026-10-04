# System Architecture

## Overview

Your system should follow an **Orchestrator → Workers** pattern where a central Orchestrator Agent routes customer requests to specialist worker agents. Each worker should operate on a specific domain (inventory, policy, refunds, communication) and write its findings to a shared DynamoDB WorkflowState record.

## Agent Graph

A flowchart illustrates the process of handling a customer request to return an order.

- The customer initiates a return by stating their order number.
- The request is routed through various agents including:
  - Orchestrator
  - Inventory
  - Refund
  - Policy
  - Communication
- The flow shows steps for:
  - checking order status
  - evaluating refund eligibility
  - composing the final response to the customer

## Request Flow

The sequence diagram below shows how a typical return request should flow through the system.

## Shared WorkflowState

The WorkflowState record in DynamoDB should use **optimistic locking** — each update should include an `expected_version` that must match the current version. This prevents concurrent agents from overwriting each other's results.

Another flowchart illustrates the session initialization and state update process:

- `initialize_session()` leads to `Created`
- Version 0 includes:
  - `session_id`
  - `customer_id`
- Version 1 adds:
  - `inventory_agent` column
- `InventoryAgent` writes findings
- `RefundAgent` and `PolicyAgent` then update the record
- This leads to:
  - `RefundPopulated`
  - `PolicyPopulated`
- `CommunicationAgent` writes responses
- This leads to:
  - `CommunicationPopulated`
- The response is delivered to the customer
- Final note:
  - version N indicates all agent columns are populated

## Recommended Agent Roles

| Agent | Model | Responsibility | Tools |
|-------|-------|----------------|-------|
| **OrchestratorAgent** | Claude 4.5 Haiku | Routes requests, creates/updates WorkflowState | `initialize_session`, `route_to_inventory_agent`, `route_to_policy_agent`, `route_to_refund_agent`, `route_to_communication_agent` |
| **InventoryAgent** | Claude 4.5 Sonnet | Gathers order and customer facts from DynamoDB | `check_order_status`, `get_customer_tier`, `list_customer_orders` |
| **PolicyAgent** | Claude 4.5 Sonnet | Coordinates parallel RAG retrieval from 3 KBs, synthesizes results | `search_all_policies` (internally fans out to 3 retriever sub-agents) |
| **RefundAgent** | Claude 4.5 Sonnet | Makes return/refund eligibility decisions (30-day Standard, 60-day Premium) | `get_inventory_context`, `initiate_refund` |
| **CommunicationAgent** | Claude 4.5 Sonnet | Drafts final, empathetic customer-facing response | `get_full_workflow_context` |

## Architecture Diagram Notes

A second architecture flowchart shows:

- A customer request process managed by an **OrchestratorAgent (Claude 3 Haiku)** that:
  - routes requests
  - manages WorkflowState
- Connected agents include:
  - `PolicyAgent`
  - `RefundAgent`
  - `CommunicationAgent`
- Policy retrieval components include:
  - `InventoryAgent`
  - `ReturnsPolicyRetriever`
  - `ShippingPolicyRetriever`
  - `WarrantyPolicyRetriever`
- A `WorkflowStateTable` in DynamoDB is used for shared state
- The diagram shows parallel interactions and write operations among agents and the workflow state table
