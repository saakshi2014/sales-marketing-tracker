# Firestore Database Schema
## Sales & Marketing Performance Tracking System
Last updated: Day 4

---

## Collections Overview

| Collection | Purpose | Seeded |
|-----------|---------|--------|
| users | All user accounts with roles | ✅ Day 3 |
| teams | Team definitions with members subcollection | ✅ Day 4 |
| pipeline_stages | The 13 default pipeline stages | ✅ Day 4 |
| leads | Individual leads managed by employees | Day 5 |
| audit_logs | Every pipeline stage change | Day 6 |
| tasks | Tasks assigned by M1/M2 to employees | Sprint 2 |

---

## users/{userId}

Document ID = Firebase Auth UID

fields:
- uid:          string   — Firebase Auth UID
- email:        string   — user@example.com
- displayName:  string   — Full name
- role:         string   — employee | m1_manager | m2_manager
- teamId:       string   — ID of the team this user belongs to
- isActive:     boolean  — false means deactivated account
- createdAt:    timestamp

---

## teams/{teamId}

Document ID = teamId (e.g. team_001)

fields:
- teamId:       string   — e.g. team_001
- teamName:     string   — e.g. Sales Team Alpha
- m1ManagerUid: string   — UID of the M1 Manager
- m2ManagerUid: string   — UID of the M2 Manager
- isActive:     boolean
- createdAt:    timestamp
- createdBy:    string   — UID of creator

subcollection: members/{uid}
- uid:      string
- email:    string
- role:     string
- joinedAt: timestamp

---

## pipeline_stages/{stageId}

Document ID = stageId (e.g. stage_1_1)

fields:
- stageId:     string   — e.g. stage_1_1
- stageNumber: string   — e.g. 1.1
- stageName:   string   — e.g. Qualified – Pending Outreach
- description: string
- stageOrder:  number   — used to sort stages in correct order
- isDefault:   boolean  — true for the 13 built-in stages
- isActive:    boolean  — false means hidden from UI
- isArchived:  boolean  — true only for stage 6.2
- createdBy:   string   — null for default stages
- createdAt:   timestamp

Default stages (13 total):
1.1  Qualified – Pending Outreach
1.2  Not Qualified
2    Connection Request Sent
2.1  Connected on LinkedIn
2.2  Connection Not Accepted
3    Initial Message Sent
3.1  No Response
4    Initial Reply Received
6.1  Interested – Ready for Meeting
6.2  Not Interested – Archived
6.3  Warm Lead – Needs Nurturing
7    Meeting Scheduled
8    Meeting Completed

---

## leads/{leadId}

Document ID = auto-generated Firestore ID

fields:
- leadId:       string   — auto-generated
- employeeUid:  string   — UID of the employee who owns this lead
- teamId:       string   — team this lead belongs to
- name:         string   — lead full name
- company:      string
- email:        string
- phone:        string
- linkedinUrl:  string
- currentStage: string   — stageId of current pipeline stage
- isArchived:   boolean  — true when at stage 6.2
- createdAt:    timestamp
- updatedAt:    timestamp

---

## audit_logs/{logId}

Document ID = auto-generated Firestore ID

fields:
- logId:       string   — auto-generated
- leadId:      string   — which lead was changed
- employeeUid: string   — who made the change
- fromStage:   string   — stageId before the change
- toStage:     string   — stageId after the change
- changedAt:   timestamp
- notes:       string   — optional note

---

## tasks/{taskId}

Document ID = auto-generated Firestore ID

fields:
- taskId:        string
- title:         string
- description:   string
- assignedToUid: string   — employee who must do this task
- assignedByUid: string   — M1 or M2 who created the task
- teamId:        string
- dueDate:       timestamp
- priority:      string   — low | medium | high
- status:        string   — pending | in_progress | completed | overdue
- createdAt:     timestamp
- completedAt:   timestamp — null until completed
```