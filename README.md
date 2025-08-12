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
  "message": "User data fatched Successfull",
  "Taskboard data": {
    "board_id": 1,
    "title": "Rajat's Board",
    "description": "This is Rajat's Dashboard",
    "visibility": "Private",
    "created_by": "Rajat Sharma",
    "created_at": "08-08-2025 06:54:44",
    "updated_by": "Rajat",
    "updated_at": "08-08-2025 06:54:44",
    "members": [
      {
        "user_id": 2,
        "full_name": "Rajat Sharma"
      },
      {
        "user_id": 5,
        "full_name": "Rahul Lokesh"
      },
      {
        "user_id": 7,
        "full_name": "Shreyas Iyer"
      }
    ],
    "Tasks Cards": [
      {
        "Task_id": 1,
        "Title": "Rajat's First Task",
        "Description": "Rajat'sDescription",
        "Due_date": "2025-08-11",
        "Assigned_to": "Shreyas Iyer",
        "Created_by": "Rajat Sharma",
        "Created_at": "08-08-2025 06:56:50",
        "Updated_by": "asus",
        "Updated_at": "11-08-2025 05:05:23",
        "media_files": {
          "images": [
            {
              "id": 1,
              "file_url": "/media/task_images/20241206_jGjsCq9.jpg"
            }
          ],
          "attachments": [
            {
              "id": 1,
              "file_url": "/media/task_attachment/lake_night_starry_sky_143961_2560x1440_Nk4qiIN.jpg"
            }
          ]
        },
        "task_lists": []
      },
      {
        "Task_id": 2,
        "Title": "Rajat's Second Task",
        "Description": "Rajat's Description",
        "Due_date": "2025-08-14",
        "Assigned_to": "Unassigned",
        "Created_by": "Rajat Sharma",
        "Created_at": "08-08-2025 06:57:13",
        "Updated_by": "None",
        "Updated_at": "11-08-2025 05:19:38",
        "media_files": {
          "images": [
            {
              "id": 2,
              "file_url": "/media/task_images/20241206_nVWN19y.jpg"
            }
          ],
          "attachments": [
            {
              "id": 2,
              "file_url": "/media/task_attachment/20241206_C5aw4f1.jpg"
            }
          ]
        },
        "task_lists": []
      },
      {
        "Task_id": 6,
        "Title": "Website Redesign",
        "Description": "Redesign Homepage.",
        "Due_date": "2025-08-14",
        "Assigned_to": "Rahul Lokesh",
        "Created_by": "Rajat Sharma",
        "Created_at": "12-08-2025 07:57:24",
        "Updated_by": "None",
        "Updated_at": "12-08-2025 07:57:24",
        "media_files": {
          "images": [],
          "attachments": []
        },
        "task_lists": [
          {
            "tasklist_id": 1,
            "task_card": 6,
            "tasklist_title": "Wireframe",
            "tasklist_description": "Create low-fidelity wireframes for the homepage.",
            "created_at": "12-08-2025 13:27:24",
            "created_by": 2,
            "is_completed": false,
            "updated_at": "12-08-2025 13:27:24",
            "updated_by": null
          },
          {
            "tasklist_id": 2,
            "task_card": 6,
            "tasklist_title": "UI Mockup",
            "tasklist_description": "Design high-fidelity mockups in Figma.",
            "created_at": "12-08-2025 13:27:24",
            "created_by": 2,
            "is_completed": false,
            "updated_at": "12-08-2025 13:27:24",
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
    "Task_title": "First Task",
    "Task_Board": "Rahul's Board",
    "Description": "This is the First task Description",
    "Task_Status": "doing",
    "Assigned_to": "Rahul Patel",
    "Created_by": "Rahul Patel",
    "Created_at": "2025-08-02T06:57:04.660190Z",
    "Updated_by": "Rahul Patel",
    "Updated_at": "2025-08-02T06:57:04.660190Z"
}
```

> > > > > > > 691fd223ebf513a876c2b384200b00a927a55ae9
