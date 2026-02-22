# NFC Service API Documentation

**Base URL:** `https://nfc-service-wailsalutem-suite.apps.inholland-minor.openshift.eu`

**Authentication:** All endpoints require JWT Bearer token in the Authorization header

---

## 1. Resolve NFC Tag (Scan Tag)

**Endpoint:** `POST /nfc/resolve`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:resolve`

**Allowed Roles:** `CAREGIVER`

**Request Body:**
```json
{
  "tag_id": "NFC123456789"
}
```

**Success Response (200):**
```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

---

## 2. Get NFC Tag by Patient ID

**Endpoint:** `GET /nfc/patient/{patient_id}`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:read`

**Allowed Roles:** `ORG_ADMIN`

**Path Parameters:**
- `patient_id` (string, required): UUID of the patient

**Success Response (200):**
```json
{
  "tag_id": "NFC123456789",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "active"
}
```

---

## 3. Get Single NFC Tag

**Endpoint:** `GET /nfc/{tag_id}`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:read`

**Allowed Roles:** `ORG_ADMIN`

**Path Parameters:**
- `tag_id` (string, required): The NFC tag identifier

**Success Response (200):**
```json
{
  "tag_id": "NFC123456789",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "active"
}
```

---

## 4. List All NFC Tags (with Pagination)

**Endpoint:** `GET /nfc/`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:read`

**Allowed Roles:** `ORG_ADMIN`

**Query Parameters:**
- `limit` (integer, optional): Number of items per page (default: 50, min: 1, max: 100)
- `cursor` (string, optional): Pagination cursor for next page
- `status` (string, optional): Filter by status (e.g., "active", "inactive")
- `search` (string, optional): Search term for filtering tags

**Example Request:**
```
GET /nfc/?limit=20&cursor=abc123&status=active&search=NFC123
```

**Success Response (200):**
```json
{
  "items": [
    {
      "tag_id": "NFC123456789",
      "patient_id": "550e8400-e29b-41d4-a716-446655440000",
      "organization_id": "550e8400-e29b-41d4-a716-446655440001",
      "status": "active"
    },
    {
      "tag_id": "NFC987654321",
      "patient_id": "550e8400-e29b-41d4-a716-446655440002",
      "organization_id": "550e8400-e29b-41d4-a716-446655440001",
      "status": "inactive"
    }
  ],
  "next_cursor": "xyz789"
}
```

---

## 5. Get NFC Statistics

**Endpoint:** `GET /nfc/stats`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:read`

**Allowed Roles:** `ORG_ADMIN`

**Success Response (200):**
```json
{
  "total": 150,
  "active": 120,
  "inactive": 30
}
```

---

## 6. Assign NFC Tag to Patient

**Endpoint:** `POST /nfc/assign`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:assign`

**Allowed Roles:** `ORG_ADMIN`

**Request Body:**
```json
{
  "tag_id": "NFC123456789",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (201):**
```json
{
  "tag_id": "NFC123456789",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "active"
}
```

---

## 7. Deactivate NFC Tag

**Endpoint:** `POST /nfc/deactivate`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:update`

**Allowed Roles:** `ORG_ADMIN`

**Request Body:**
```json
{
  "tag_id": "NFC123456789"
}
```

**Success Response (200):**
```json
{
  "tag_id": "NFC123456789",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "inactive"
}
```

---

## 8. Reactivate NFC Tag

**Endpoint:** `POST /nfc/reactivate`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:update`

**Allowed Roles:** `ORG_ADMIN`

**Request Body:**
```json
{
  "tag_id": "NFC123456789"
}
```

**Success Response (200):**
```json
{
  "tag_id": "NFC123456789",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "active"
}
```

---

## 9. Replace NFC Tag

**Endpoint:** `POST /nfc/replace`

**Required Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Required Permission:** `nfc:update`

**Allowed Roles:** `ORG_ADMIN`

**Request Body:**
```json
{
  "old_tag_id": "NFC123456789",
  "new_tag_id": "NFC987654321"
}
```

**Success Response (200):**
```json
{
  "old_tag_id": "NFC123456789",
  "new_tag_id": "NFC987654321",
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "active"
}
```

---

## 10. Health Check

**Endpoint:** `GET /health`

**Required Headers:** None (Public endpoint)

**Success Response (200):**
```json
{
  "status": "ok"
}
```

---

## Error Responses

All endpoints may return the following error responses:

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Notes for Frontend Implementation:

1. **All UUIDs are strings** - patient_id fields are UUID format
2. **Authorization header format:** `Authorization: Bearer <your_jwt_token>`
3. **Content-Type for POST requests:** `application/json`
4. **Pagination:** Use the `next_cursor` from response to fetch next page
5. **Role-based access:** Ensure user's role has required permissions before showing UI elements
6. **Tag ID format:** Usually alphanumeric strings (e.g., "NFC123456789")

---

## Permission Matrix

| Endpoint | Permission | CAREGIVER | ORG_ADMIN |
|----------|-----------|-----------|-----------|
| POST /nfc/resolve | nfc:resolve | ✅ | ❌ |
| GET /nfc/patient/{patient_id} | nfc:read | ❌ | ✅ |
| GET /nfc/{tag_id} | nfc:read | ❌ | ✅ |
| GET /nfc/ | nfc:read | ❌ | ✅ |
| GET /nfc/stats | nfc:read | ❌ | ✅ |
| POST /nfc/assign | nfc:assign | ❌ | ✅ |
| POST /nfc/deactivate | nfc:update | ❌ | ✅ |
| POST /nfc/reactivate | nfc:update | ❌ | ✅ |
| POST /nfc/replace | nfc:update | ❌ | ✅ |
| GET /health | none | ✅ | ✅ |

---

## Quick Reference: Axios Examples

### Setup Axios with Auth
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://your-domain',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token'); // or your token storage
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Example: Resolve NFC Tag
```javascript
const resolveTag = async (tagId) => {
  try {
    const response = await api.post('/nfc/resolve', {
      tag_id: tagId
    });
    return response.data;
  } catch (error) {
    console.error('Error resolving tag:', error);
    throw error;
  }
};
```

### Example: Get All Tags with Pagination
```javascript
const getAllTags = async (limit = 50, cursor = null, status = null, search = null) => {
  try {
    const params = new URLSearchParams();
    params.append('limit', limit);
    if (cursor) params.append('cursor', cursor);
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    
    const response = await api.get(`/nfc/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching tags:', error);
    throw error;
  }
};
```

### Example: Assign Tag to Patient
```javascript
const assignTag = async (tagId, patientId) => {
  try {
    const response = await api.post('/nfc/assign', {
      tag_id: tagId,
      patient_id: patientId
    });
    return response.data;
  } catch (error) {
    console.error('Error assigning tag:', error);
    throw error;
  }
};
```
