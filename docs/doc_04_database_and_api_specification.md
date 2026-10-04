# HelpLink — Database & API Specification
**Document ID:** DOC-04  
**Version:** 1.1  
**Status:** Approved Specification  
**Product:** HelpLink (Community Social-Impact Web Platform)  

---

## 1. Database Entity-Relationship Architecture

```
  +------------------+         1:N          +------------------+
  |      users       |--------------------->|    resources     |
  +------------------+                      +------------------+
  | id (PK)          |                      | id (PK)          |
  | email (Unique)   |                      | slug (Unique)    |
  | full_name        |                      | title            |
  | password_hash    |                      | description      |
  | role (user/admin)|                      | url              |
  | is_active        |                      | category_id (FK) |
  | created_at       |                      | resource_type    |
  +------------------+                      | location         |
           |                                | user_id (FK)     |
           | 1:N                            | status           |
           v                                +------------------+
  +------------------+                               |
  | saved_resources  |                               | 1:N
  +------------------+                               v
  | user_id (FK)     |                      +------------------+
  | resource_id (FK) |                      |     reports      |
  +------------------+                      +------------------+
                                            | id (PK)          |
  +------------------+         1:N          | resource_id (FK) |
  |    categories    |--------------------->| user_id (FK)     |
  +------------------+                      | reason           |
  | id (PK)          |                      | details          |
  | name (Unique)    |                      | status           |
  | slug (Unique)    |                      +------------------+
  | description      |
  | icon             |                      +------------------+
  +------------------+                      |  resource_tags   |
                                            +------------------+
  +------------------+                      | resource_id (FK) |
  |      tags        |--------------------->| tag_id (FK)      |
  +------------------+         M:N          +------------------+
  | id (PK), name    |
  +------------------+
```
