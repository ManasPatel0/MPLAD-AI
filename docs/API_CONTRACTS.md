# MPLAD-AI: API Contracts & Interface Specification
**FastAPI v1 RESTful Gateway | SIH 2026 Problem Statement ID: 26102**

---

## 1. Overview & Standards
- **Base URL**: `/api/v1`
- **Protocol**: HTTPS / REST
- **Authentication**: JWT Bearer token in HTTP Header `Authorization: Bearer <token>`
- **Response Format**: `application/json`
- **Standard Error Format**:
  ```json
  {
    "detail": "Error description message",
    "error_code": "RESOURCE_NOT_FOUND",
    "timestamp": "2026-10-23T00:15:00Z"
  }
  ```

---

## 2. Authentication Router (`/api/v1/auth`)

### 2.1 Login User
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "email": "collector.varanasi@gov.in",
    "password": "Password123!"
  }
  ```
- **Response 200 OK**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "e812d08a-4467-4d92-9602-581d6f51950e",
      "email": "collector.varanasi@gov.in",
      "full_name": "District Magistrate Varanasi",
      "role": "DISTRICT_COLLECTOR",
      "constituency_id": "b3c94d12-1111-2222-3333-444455556666",
      "district_id": "a1f87e44-5555-6666-7777-888899990000"
    }
  }
  ```
- **Response 401 Unauthorized**: Invalid email or password.

### 2.2 Get Current Profile
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Access**: Authenticated

---

## 3. Projects Router (`/api/v1/projects`)

### 3.1 List & Filter Projects
- **Method**: `GET`
- **Path**: `/api/v1/projects`
- **Access**: All authenticated roles
- **Query Parameters**:
  - `constituency_id` (UUID, optional)
  - `status` (String, optional: `PROPOSED`, `SANCTIONED`, `IN_PROGRESS`, etc.)
  - `category` (String, optional: `DRINKING_WATER`, `ROADS_BRIDGES`, etc.)
  - `priority_quota` (String, optional: `GENERAL`, `SC_MANDATE`, `ST_MANDATE`)
  - `has_delay_risk` (Boolean, optional)
  - `page` (Integer, default: 1)
  - `limit` (Integer, default: 20)
- **Response 200 OK**:
  ```json
  {
    "total": 48,
    "page": 1,
    "limit": 20,
    "items": [
      {
        "id": "7f8b3c10-82a1-4235-99d8-c0b9683935ec",
        "project_code": "MPLADS-VNS-2026-0042",
        "title": "Solar Street Light Installation in Rohania Block",
        "category": "COMMUNITY_INFRASTRUCTURE",
        "priority_quota": "SC_MANDATE",
        "estimated_cost": 2500000.00,
        "sanctioned_cost": 2450000.00,
        "actual_expenditure": 1200000.00,
        "status": "IN_PROGRESS",
        "latitude": 25.2677,
        "longitude": 82.9913,
        "location_address": "Rohania Block, Varanasi, UP",
        "recommendation_date": "2026-08-10",
        "target_completion_date": "2027-02-15",
        "delay_risk_score": 18.5,
        "is_anomaly": false,
        "progress_percentage": 50.0
      }
    ]
  }
  ```

### 3.2 Recommend New Work
- **Method**: `POST`
- **Path**: `/api/v1/projects`
- **Access**: `MP`, `DISTRICT_COLLECTOR`, `MOSPI_ADMIN`
- **Request Body**:
  ```json
  {
    "constituency_id": "b3c94d12-1111-2222-3333-444455556666",
    "district_id": "a1f87e44-5555-6666-7777-888899990000",
    "title": "Construction of Primary Health Centre Sub-Station",
    "description": "Constructing a 4-bed primary health care centre with solar power backup in village Kashi.",
    "category": "PUBLIC_HEALTH",
    "priority_quota": "GENERAL",
    "estimated_cost": 4500000.00,
    "latitude": 25.3211,
    "longitude": 82.9872,
    "location_address": "Village Kashi, Block Sevapuri, Varanasi",
    "recommendation_date": "2026-10-23",
    "target_completion_date": "2027-08-30"
  }
  ```
- **Response 201 Created**:
  ```json
  {
    "id": "1e5c3b99-312a-4428-a55b-80a221fbc301",
    "project_code": "MPLADS-VNS-2026-0043",
    "status": "PROPOSED",
    "ai_precheck": {
      "duplicate_flag": false,
      "cost_anomaly_flag": false,
      "predicted_delay_days": 12.0,
      "message": "Project passed initial automated eligibility and non-duplication pre-checks."
    }
  }
  ```
- **Response 409 Conflict** (When AI detects high duplicate similarity):
  ```json
  {
    "detail": "Potential duplicate work proposal detected within 250 meters.",
    "duplicate_match": {
      "existing_project_id": "89b3a101-...",
      "title": "Establishment of Primary Health Sub-Unit Sevapuri",
      "distance_meters": 180.4,
      "similarity_score": 0.91
    }
  }
  ```

### 3.3 Project Details Dossier
- **Method**: `GET`
- **Path**: `/api/v1/projects/{id}`
- **Access**: All authenticated roles
- **Response 200 OK**: Returns full project entity, milestones list, inspections list, AI risk assessment, and audit logs.

### 3.4 Transition Project Status
- **Method**: `PATCH`
- **Path**: `/api/v1/projects/{id}/status`
- **Access**: `DISTRICT_COLLECTOR`, `MOSPI_ADMIN`
- **Request Body**:
  ```json
  {
    "to_status": "SANCTIONED",
    "sanctioned_cost": 4400000.00,
    "agency_id": "c4d5e6f7-1111-2222-3333-444455556666",
    "sanction_reference_no": "DM/MPLADS/2026/AS-102",
    "remarks": "Administratively approved after technical scrutiny."
  }
  ```
- **Response 200 OK**: Returns updated project object with recorded status change.

---

## 4. Inspections & Field Verification (`/api/v1/inspections`)

### 4.1 Upload Geotagged Milestone Photo
- **Method**: `POST`
- **Path**: `/api/v1/inspections`
- **Access**: `IMPLEMENTING_AGENCY`, `DISTRICT_COLLECTOR`
- **Form Data**:
  - `project_id`: UUID
  - `physical_progress_pct`: Float (e.g. `65.0`)
  - `photo`: File (JPEG / PNG with EXIF)
  - `photo_latitude`: Float (e.g. `25.3210`)
  - `photo_longitude`: Float (e.g. `82.9870`)
  - `remarks`: String
- **Response 201 Created**:
  ```json
  {
    "inspection_id": "33a1f9e0-...",
    "geo_distance_meters": 24.3,
    "is_verified": true,
    "message": "Inspection photo verified within legitimate boundary tolerance (24.3m)."
  }
  ```
- **Response 422 Unprocessable**: If `geo_distance_meters` exceeds 200m anti-spoofing threshold.

---

## 5. Machine Learning & Predictive Analytics (`/api/v1/ai`)

### 5.1 On-Demand Delay Risk Prediction
- **Method**: `POST`
- **Path**: `/api/v1/ai/predict-delay`
- **Access**: Authenticated
- **Request Body**:
  ```json
  {
    "category": "ROADS_BRIDGES",
    "estimated_cost": 5000000.00,
    "agency_id": "c4d5e6f7-...",
    "target_duration_days": 180,
    "district_id": "a1f87e44-..."
  }
  ```
- **Response 200 OK**:
  ```json
  {
    "predicted_delay_days": 45.2,
    "delay_probability": 0.76,
    "risk_level": "HIGH",
    "top_contributing_factors": [
      { "factor": "Agency Historical Delay Average", "impact": "High" },
      { "factor": "Project Scale (>40 Lakhs)", "impact": "Medium" },
      { "factor": "Monsoon Season Overlap", "impact": "Medium" }
    ]
  }
  ```

### 5.2 Duplicate Work & Overlap Query
- **Method**: `POST`
- **Path**: `/api/v1/ai/detect-duplicates`
- **Access**: Authenticated
- **Request Body**:
  ```json
  {
    "title": "Community Hall in Shivpur",
    "category": "COMMUNITY_INFRASTRUCTURE",
    "latitude": 25.3520,
    "longitude": 82.9780,
    "radius_meters": 500
  }
  ```
- **Response 200 OK**:
  ```json
  {
    "duplicate_found": true,
    "highest_similarity": 0.88,
    "matches": [
      {
        "project_id": "55e2d1...",
        "title": "Construction of Barat Ghar / Community Hall Shivpur",
        "status": "COMPLETED",
        "distance_meters": 110.5,
        "text_similarity_score": 0.88
      }
    ]
  }
  ```

### 5.3 Constituency Fund Lapse Forecaster
- **Method**: `GET`
- **Path**: `/api/v1/ai/fund-forecast/{constituency_id}`
- **Access**: Authenticated
- **Response 200 OK**:
  ```json
  {
    "constituency_id": "b3c94d12-...",
    "fiscal_year": "2026-2027",
    "total_entitlement": 50000000.00,
    "current_expenditure": 18000000.00,
    "forecasted_expenditure_by_march31": 34000000.00,
    "estimated_unspent_lapse_risk": 16000000.00,
    "risk_category": "MODERATE_LAPSE_HAZARD",
    "recommendation": "Expedite sanction of 4 pending proposals in Drinking Water sector to meet annual pacing."
  }
  ```

---

## 6. Citizen Public Portal (`/api/v1/citizen`)

### 6.1 Public Project Search
- **Method**: `GET`
- **Path**: `/api/v1/citizen/search`
- **Access**: Public
- **Query Parameters**: `query` (text search), `pincode`, `constituency_code`, `category`
- **Response 200 OK**: Public card view of assets including completed photo proof and sanctioned amounts.

### 6.2 Submit Citizen Feedback
- **Method**: `POST`
- **Path**: `/api/v1/citizen/feedback`
- **Access**: Public
- **Request Body**:
  ```json
  {
    "project_id": "7f8b3c10-...",
    "citizen_name": "Ramesh Kumar",
    "citizen_phone": "+91-9876543210",
    "rating": 5,
    "comment": "Solar lights are functioning properly every night in our gram panchayat."
  }
  ```
- **Response 201 Created**: `{ "message": "Feedback recorded successfully." }`
