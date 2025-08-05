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
````

## This is User's Main Task Board(Postman Output)

```json
{
  "message": "User data fatched Successfull",
  "Taskboard data": {
    "board_id": 1,
    "title": "Rahul's Board",
    "description": "This is Rahul's first Dashboard",
    "visibility": "private",
    "created_by": "Rahul Patel",
    "created_at": "2025-08-01T09:43:04.871536Z",
    "updated_by": "Unknown",
    "updated_at": "2025-08-01T09:43:04.871536Z",
    "members": [
      {
        "user_id": 2,
        "full_name": "Rahul Patel"
      },
      {
        "user_id": 3,
        "full_name": "Murli Rajan"
      }
    ],
    "Tasks Cards": [
      {
        "Task_id": 1,
        "Title": "First Task",
        "Description": "This is the First task Description",
        "Task Status": "doing",
        "Due_date": "2025-08-04",
        "Assigned_to": "Rahul Patel",
        "Created_by": "Rahul Patel",
        "Created_at": "2025-08-02T06:57:04.660190Z",
        "Updated_by": "Rahul Patel",
        "Updated_at": "2025-08-02T06:57:04.660190Z",
        "media_files": {
          "images": [
            {
              "id": 1,
              "file_url": "/media/task_images/img1.jpg"
            },
            {
              "id": 2,
              "file_url": "/media/task_images/img2.jpg"
            },
            {
              "id": 3,
              "file_url": "/media/task_images/img3.jpg"
            },
            {
              "id": 4,
              "file_url": "/media/task_images/img4.jpg"
            }
          ],
          "attachments": [
            {
              "id": 1,
              "file_url": "/media/task_attachment/Hello1.txt"
            },
            {
              "id": 2,
              "file_url": "/media/task_attachment/Hello2.txt"
            }
          ]
        }
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
