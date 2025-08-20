# Trello-Task-Management

## Register Output demo

```json
{
  "message": "User registered successfully.",
  "user_id": 8,
  "email": "rajat@gmail.com",
  "username": "@rajat123",
  "full_name": "Rajat Sharma"
}
```

## Login Output

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NDQ3MjUwOCwiaWF0IjoxNzU0Mzg2MTA4LCJqdGkiOiI4YTRhNjFjMTZiYWI0ZjY1ODYxMzkxMDhlZTIwZWE1NyIsInVzZXJfaWQiOiI4In0.DloC73awZLpo5JtEGX_s8KixHkI7B3JS1lzxB_KNJVE",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0Mzg3MzA4LCJpYXQiOjE3NTQzODYxMDgsImp0aSI6IjY1ODVhNzEyYmZiMTQ2ZmU4N2IwMjlkYTRmYTNjZjFjIiwidXNlcl9pZCI6IjgifQ.Ts96NLMEvsiDxISXW5bIr8UR9ZTTJQQ7ErIVY4-IXsY",
  "user": {
    "user_id": 8,
    "username": "@rajat123",
    "email": "rajat@gmail.com",
    "full_name": "Rajat Sharma"
  }
}
```

## This is User's Main Task Board(Postman Output)

```json
{
  "message": "Successfull",
  "Taskboard data": {
    "board_id": 4,
    "title": "Customer Support Training ryan second board",
    "description": "Onboard new support agents with product knowledge",
    "visibility": "team",
    "created_by": "Ryan Scott",
    "created_at": "13-08-2025 09:52:03",
    "updated_by": "Unknown",
    "updated_at": "13-08-2025 09:52:03",
    "members": [
      {
        "user_id": 22,
        "full_name": "Ryan Scott"
      }
    ],
    "Tasks Cards": [
      {
        "Task_id": 10,
        "Title": "Support Team Training",
        "Description": "Onboard new customer support representatives",
        "Created_by": "Ryan Scott",
        "Created_at": "13-08-2025 09:58:40",
        "Updated_by": "Ryan Scott",
        "Updated_at": "20-08-2025 07:31:47",
        "Media_files": {
          "Images": [
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/lake_night_starry_sky_143961_2560x1440_dGHDCZX.jpg"
            }
          ],
          "Attachments": [
            {
              "attachment_url": "http://127.0.0.1:8000/media/task_attachment/20241206_YcuoDFG.jpg"
            }
          ]
        },
        "Task Lists": [
          {
            "tasklist_id": 10,
            "task_card": 10,
            "tasklist_title": "Product Knowledge",
            "tasklist_description": "Train on core product features",
            "priority": "low",
            "label_color": "green",
            "start_date": null,
            "due_date": "2025-08-12",
            "created_at": "13-08-2025 15:28:40",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:28:40",
            "is_completed": false,
            "updated_by": null,
            "comments": [
              {
                "user": {
                  "user_id": 22,
                  "full_name": "Ryan Scott"
                },
                "comment_text": "This is Comment",
                "created_at": "20-08-2025 16:33:23"
              },
              {
                "user": {
                  "user_id": 22,
                  "full_name": "Ryan Scott"
                },
                "comment_text": "This is 2 Comment",
                "created_at": "20-08-2025 16:37:37"
              },
              {
                "user": {
                  "user_id": 5,
                  "full_name": "Rahul Lokesh"
                },
                "comment_text": "This is  Comment from Rahul",
                "created_at": "20-08-2025 18:18:18"
              }
            ],
            "assigned_to": null
          },
          {
            "tasklist_id": 11,
            "task_card": 10,
            "tasklist_title": "CRM Training",
            "tasklist_description": "Teach Zendesk system usage",
            "priority": "low",
            "label_color": "green",
            "start_date": null,
            "due_date": "2025-08-22",
            "created_at": "13-08-2025 15:28:40",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:28:40",
            "is_completed": false,
            "updated_by": null,
            "comments": [],
            "assigned_to": null
          },
          {
            "tasklist_id": 12,
            "task_card": 10,
            "tasklist_title": "Mock Calls",
            "tasklist_description": "Practice handling customer scenarios",
            "priority": "low",
            "label_color": "green",
            "start_date": null,
            "due_date": "2025-09-19",
            "created_at": "13-08-2025 15:28:40",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:28:40",
            "is_completed": false,
            "updated_by": null,
            "comments": [],
            "assigned_to": null
          }
        ]
      },
      {
        "Task_id": 11,
        "Title": "New Office Setup",
        "Description": "Coordinate relocation to new headquarters",
        "Created_by": "Ryan Scott",
        "Created_at": "13-08-2025 10:00:35",
        "Updated_by": "None",
        "Updated_at": "13-08-2025 10:00:35",
        "Media_files": {
          "Images": [
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/2859328_VC7bUbB.jpg"
            }
          ],
          "Attachments": [
            {
              "attachment_url": "http://127.0.0.1:8000/media/task_attachment/Trello_Task_Management_App_1_IJysrEo.docx"
            }
          ]
        },
        "Task Lists": [
          {
            "tasklist_id": 13,
            "task_card": 11,
            "tasklist_title": "Furniture Order",
            "tasklist_description": "Select and purchase office furniture",
            "priority": "low",
            "label_color": "green",
            "start_date": null,
            "due_date": "2025-08-13",
            "created_at": "13-08-2025 15:30:35",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:30:35",
            "is_completed": false,
            "updated_by": null,
            "comments": [],
            "assigned_to": null
          },
          {
            "tasklist_id": 14,
            "task_card": 11,
            "tasklist_title": "IT Infrastructure",
            "tasklist_description": "Set up network and workstations",
            "priority": "low",
            "label_color": "green",
            "start_date": null,
            "due_date": "2025-08-18",
            "created_at": "13-08-2025 15:30:35",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:30:35",
            "is_completed": false,
            "updated_by": null,
            "comments": [],
            "assigned_to": null
          },
          {
            "tasklist_id": 15,
            "task_card": 11,
            "tasklist_title": "Employee Orientation",
            "tasklist_description": "Conduct new office tours",
            "priority": "low",
            "label_color": "green",
            "start_date": null,
            "due_date": "2025-10-15",
            "created_at": "13-08-2025 15:30:35",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:30:35",
            "is_completed": false,
            "updated_by": null,
            "comments": [],
            "assigned_to": null
          }
        ]
      }
    ]
  }
}
```

## This is Task detail format inside the Task Board

```jason
{
    "Task card": [
        {
            "is_starred": false,
            "task_id": 12,
            "board": 5,
            "title": "Fiscal Year Closing",
            "description": "Complete annual financial reporting",
            "is_completed": "pending",
            "created_at": "13-08-2025 15:31:45",
            "created_by": "ryan_scott",
            "updated_at": "13-08-2025 15:31:45",
            "assigned_to": {
                "user_id": 22,
                "full_name": "Ryan Scott"
            },
            "task_lists": [
                {
                    "tasklist_id": 16,
                    "task_card": 12,
                    "tasklist_title": "Accounts Reconciliation",
                    "tasklist_description": "Verify all transactions are recorded",
                    "due_date": "2025-08-19",
                    "created_at": "13-08-2025 15:31:45",
                    "created_by": "ryan_scott",
                    "is_completed": false,
                    "updated_at": "13-08-2025 15:31:45"
                },
                {
                    "tasklist_id": 17,
                    "task_card": 12,
                    "tasklist_title": "Tax Preparation",
                    "tasklist_description": "Compile documents for accountants",
                    "due_date": "2025-08-20",
                    "created_at": "13-08-2025 15:31:45",
                    "created_by": "ryan_scott",
                    "is_completed": false,
                    "updated_at": "13-08-2025 15:31:45"
                },
                {
                    "tasklist_id": 18,
                    "task_card": 12,
                    "tasklist_title": "Budget Planning",
                    "tasklist_description": "Draft next year's department budgets",
                    "due_date": "2025-12-15",
                    "created_at": "13-08-2025 15:31:45",
                    "created_by": "ryan_scott",
                    "is_completed": false,
                    "updated_at": "13-08-2025 15:31:45"
                }
            ]
        }
    ]
}
```

> > > > > > > 691fd223ebf513a876c2b384200b00a927a55ae9
