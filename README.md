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
    "board_id": 3,
    "title": "Website Redesign",
    "description": "Complete UI/UX overhaul for main company website",
    "visibility": "private",
    "created_by": "Ryan Scott",
    "created_at": "13-08-2025 07:30:26",
    "updated_by": "Unknown",
    "updated_at": "13-08-2025 07:31:43",
    "members": [
      {
        "user_id": 1,
        "full_name": "asus"
      },
      {
        "user_id": 3,
        "full_name": "Vishal Sharma"
      },
      {
        "user_id": 5,
        "full_name": "Rahul Lokesh"
      },
      {
        "user_id": 8,
        "full_name": "John Doe"
      },
      {
        "user_id": 22,
        "full_name": "Ryan Scott"
      }
    ],
    "Tasks Cards": [
      {
        "Task_id": 7,
        "Title": "Q4 Marketing Launch",
        "Description": "Execute holiday marketing campaign",
        "Assigned_to": "John Doe",
        "Created_by": "Ryan Scott",
        "Created_at": "13-08-2025 09:34:02",
        "Updated_by": "None",
        "Updated_at": "13-08-2025 09:34:02",
        "Media_files": {
          "Images": [
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/20250620_OBGA.ChainBridgeBudapest_shutterstock_1153376083_bing.jpg"
            }
          ],
          "Attachments": [
            {
              "attachment_url": "http://127.0.0.1:8000/media/task_attachment/Trello_Task_Management_App_1.docx"
            }
          ]
        },
        "Task Lists": [
          {
            "tasklist_id": 3,
            "task_card": 7,
            "tasklist_title": "Content Creation",
            "tasklist_description": "Write blog posts and social media copy",
            "due_date": "2025-08-15",
            "created_at": "13-08-2025 15:04:02",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:04:02",
            "updated_by": null
          },
          {
            "tasklist_id": 4,
            "task_card": 7,
            "tasklist_title": "Ad Design",
            "tasklist_description": "Create Facebook/Google ads",
            "due_date": "2025-09-13",
            "created_at": "13-08-2025 15:04:02",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:04:02",
            "updated_by": null
          }
        ]
      },
      {
        "Task_id": 8,
        "Title": "Database Upgrade",
        "Description": "Migrate from MySQL to PostgreSQL",
        "Assigned_to": "David Brown",
        "Created_by": "Ryan Scott",
        "Created_at": "13-08-2025 09:35:22",
        "Updated_by": "None",
        "Updated_at": "13-08-2025 09:35:22",
        "Media_files": {
          "Images": [
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/4433065-4d2a8d877c4f4ca39104dd8d1681c265.webp"
            },
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/20250213.jpg"
            }
          ],
          "Attachments": [
            {
              "attachment_url": "http://127.0.0.1:8000/media/task_attachment/Trello_Task_Management_App_1_GRCZXoB.docx"
            }
          ]
        },
        "Task Lists": [
          {
            "tasklist_id": 5,
            "task_card": 8,
            "tasklist_title": "Backup Data",
            "tasklist_description": "Create full database backup",
            "due_date": null,
            "created_at": "13-08-2025 15:05:22",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:05:22",
            "updated_by": null
          },
          {
            "tasklist_id": 6,
            "task_card": 8,
            "tasklist_title": "Schema Migration",
            "tasklist_description": "Convert tables to PostgreSQL format",
            "due_date": null,
            "created_at": "13-08-2025 15:05:22",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:05:22",
            "updated_by": null
          }
        ]
      },
      {
        "Task_id": 9,
        "Title": "Mobile App Feature Update",
        "Description": "Implement new user profile features",
        "Assigned_to": "Olivia Hall",
        "Created_by": "Ryan Scott",
        "Created_at": "13-08-2025 09:47:27",
        "Updated_by": "None",
        "Updated_at": "13-08-2025 09:47:27",
        "Media_files": {
          "Images": [
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/20250213_LHNJ6aF.jpg"
            },
            {
              "image_url": "http://127.0.0.1:8000/media/task_images/20250804_OHR.CaliforniaTidepool_EN-IN9579127212_UHD_bing.jpg"
            }
          ],
          "Attachments": [
            {
              "attachment_url": "http://127.0.0.1:8000/media/task_attachment/Trello_Task_Management_App_1_e18Iamg.docx"
            }
          ]
        },
        "Task Lists": [
          {
            "tasklist_id": 7,
            "task_card": 9,
            "tasklist_title": "Backend API",
            "tasklist_description": "Develop new endpoints for profile data",
            "due_date": "2025-08-15",
            "created_at": "13-08-2025 15:17:27",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:17:27",
            "updated_by": null
          },
          {
            "tasklist_id": 8,
            "task_card": 9,
            "tasklist_title": "UI Implementation",
            "tasklist_description": "Build profile screen in React Native",
            "due_date": "2025-09-12",
            "created_at": "13-08-2025 15:17:27",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:17:27",
            "updated_by": null
          },
          {
            "tasklist_id": 9,
            "task_card": 9,
            "tasklist_title": "Testing",
            "tasklist_description": "Conduct QA testing on new features",
            "due_date": "2025-08-14",
            "created_at": "13-08-2025 15:17:27",
            "created_by": 22,
            "is_completed": false,
            "updated_at": "13-08-2025 15:17:27",
            "updated_by": null
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
