# Trello inspired Task Management

This is the Trello inspired Task-Management Backend-API Project using Python, Django Rest Framework, RestAPI

## Register Output demo

```json
{
    "status": "success",
    "message": "User registered successfully.",
    "User Detail": {
        "user_id": 34,
        "full_name": "Jay Shah"
    }
}
```

## Login Output

```json
{
    "status": "Login Successfull",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3Mzk5MDAyLCJpYXQiOjE3NTczMTI2MDIsImp0aSI6ImNkZDkwNzNkYmMwZTQwZmM5YTAxMjhmM2Y1NDRlMWM1IiwidXNlcl9pZCI6IjMifQ.OWfJ68UEBzL9udDPFJn9JL_sFkGMCJA6NbUBXwT5g-4",
    "user": {
        "user_id": 3,
        "username": "@arjun03",
        "full_name": "Arjun Sharma"
    }
}
```

## This is User's Main Task Board(Postman Output)

```json
{
    "status": "success",
    "message": "Board fetched",
    "Board data": {
        "board_id": 3,
        "title": "Marketing Team Board",
        "description": "Q4 Marketing Strategy & Launch",
        "visibility": "team",
        "created_by": "Arjun Sharma",
        "created_at": "26-08-2025 12:30:21",
        "updated_by": "Unknown",
        "updated_at": "26-08-2025 12:30:21",
        "members": [
            {
                "user_id": 3,
                "full_name": "Arjun Sharma"
            },
            {
                "user_id": 6,
                "full_name": "Neha Patel"
            },
            {
                "user_id": 7,
                "full_name": "Rohan Gupta"
            },
            {
                "user_id": 8,
                "full_name": "Sneha Iyer"
            }
        ],
        "Tasks Cards": [
            {
                "Task_id": 1,
                "Title": "Q4 Marketing Launch",
                "Description": "Plan and execute holiday marketing campaign for Q4.",
                "Created_by": "Arjun Sharma",
                "Created_at": "26-08-2025 12:50:30",
                "Updated_by": "Arjun Sharma",
                "Updated_at": "26-08-2025 12:50:30",
                "Task Lists": [
                    {
                        "tasklist_id": 1,
                        "tasklist_title": "Define campaign goals",
                        "tasklist_description": "Set SMART goals for holiday launch.",
                        "priority": "High",
                        "label_color": "red",
                        "due_date": "05-09-2025",
                        "is_completed": false,
                        "assigned_to": "Unassigned",
                        "Media_files": {
                            "Images": [
                                "http://127.0.0.1:8000task_images/20250713_OHR.YoungShark_EN-IN1362768509_UHD_bing.jpg"
                            ],
                            "Attachments": [
                                "http://127.0.0.1:8000task_attachments/20250713_OHR.YoungShark_EN-IN1362768509_UHD_bing.jpg"
                            ]
                        },
                        "comments": [],
                        "checklist_progress": 50.0,
                        "checklist_items": {
                            "title": "Project Checklist",
                            "items": [
                                {
                                    "name": "Setup Backend",
                                    "done": true
                                },
                                {
                                    "name": "Setup Frontend",
                                    "done": true
                                },
                                {
                                    "name": "Create Database",
                                    "done": false
                                },
                                {
                                    "name": "Deploy",
                                    "done": false
                                }
                            ]
                        }
                    },
                    {
                        "tasklist_id": 2,
                        "tasklist_title": "Content planning",
                        "tasklist_description": "Decide creatives, copies, and video ads",
                        "priority": "Medium",
                        "label_color": "blue",
                        "due_date": "12-09-2025",
                        "is_completed": false,
                        "assigned_to": "Arjun Sharma",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0.0,
                        "checklist_items": {
                            "title": "Checklist",
                            "items": [
                                {
                                    "name": "video edit",
                                    "done": false
                                }
                            ]
                        }
                    },
                    {
                        "tasklist_id": 17,
                        "tasklist_title": "video edit",
                        "tasklist_description": "",
                        "priority": "low",
                        "label_color": "green",
                        "due_date": null,
                        "is_completed": false,
                        "assigned_to": "Unassigned",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": {}
                    },
                    {
                        "tasklist_id": 18,
                        "tasklist_title": "Photo edit",
                        "tasklist_description": "",
                        "priority": "low",
                        "label_color": "green",
                        "due_date": null,
                        "is_completed": false,
                        "assigned_to": "Unassigned",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": {}
                    }
                ]
            },
            {
                "Task_id": 2,
                "Title": "Social Media Strategy",
                "Description": "Create Instagram & LinkedIn content calendar for next 3 months.",
                "Created_by": "Arjun Sharma",
                "Created_at": "26-08-2025 12:50:50",
                "Updated_by": "Arjun Sharma",
                "Updated_at": "26-08-2025 12:50:50",
                "Task Lists": [
                    {
                        "tasklist_id": 3,
                        "tasklist_title": "Platform research",
                        "tasklist_description": "Check audience activity on Insta, LinkedIn, Twitter.",
                        "priority": "Medium",
                        "label_color": "green",
                        "due_date": "08-09-2025",
                        "is_completed": false,
                        "assigned_to": "Rahul Verma",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": []
                    },
                    {
                        "tasklist_id": 4,
                        "tasklist_title": "Calendar creation",
                        "tasklist_description": "Schedule daily posts for 3 months.",
                        "priority": "High",
                        "label_color": "yellow",
                        "due_date": "20-09-2025",
                        "is_completed": false,
                        "assigned_to": "Priya Mehta",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": []
                    }
                ]
            },
            {
                "Task_id": 3,
                "Title": "Ad Campaign Setup",
                "Description": "Run Google Ads & Meta Ads targeting festive sales.",
                "Created_by": "Arjun Sharma",
                "Created_at": "26-08-2025 12:51:18",
                "Updated_by": "Arjun Sharma",
                "Updated_at": "26-08-2025 12:51:18",
                "Task Lists": [
                    {
                        "tasklist_id": 5,
                        "tasklist_title": "Audience segmentation",
                        "tasklist_description": "Define age, location, and interest-based targeting.",
                        "priority": "High",
                        "label_color": "orange",
                        "due_date": "12-09-2025",
                        "is_completed": false,
                        "assigned_to": "Priya Mehta",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": []
                    },
                    {
                        "tasklist_id": 6,
                        "tasklist_title": "Ad creatives design",
                        "tasklist_description": "Prepare banners and short videos for ads.",
                        "priority": "Medium",
                        "label_color": "blue",
                        "due_date": "17-09-2025",
                        "is_completed": false,
                        "assigned_to": "Arjun Sharma",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": []
                    }
                ]
            },
            {
                "Task_id": 4,
                "Title": "Customer Feedback Survey",
                "Description": "Prepare and send customer satisfaction survey post-purchase",
                "Created_by": "Arjun Sharma",
                "Created_at": "26-08-2025 12:51:39",
                "Updated_by": "Arjun Sharma",
                "Updated_at": "27-08-2025 10:34:58",
                "Task Lists": [
                    {
                        "tasklist_id": 7,
                        "tasklist_title": "Survey draft",
                        "tasklist_description": "Prepare questions for product feedback.",
                        "priority": "Low",
                        "label_color": "purple",
                        "due_date": "22-09-2025",
                        "is_completed": false,
                        "assigned_to": "Arjun Sharma",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": []
                    },
                    {
                        "tasklist_id": 8,
                        "tasklist_title": "Survey distribution",
                        "tasklist_description": "Send via email & WhatsApp campaign.",
                        "priority": "Medium",
                        "label_color": "cyan",
                        "due_date": "28-09-2025",
                        "is_completed": false,
                        "assigned_to": "Priya Mehta",
                        "Media_files": {
                            "Images": [],
                            "Attachments": []
                        },
                        "comments": [],
                        "checklist_progress": 0,
                        "checklist_items": []
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
    "status": "success",
    "message": "TaskCard fetched",
    "Task card": [
        {
            "is_starred": false,
            "task_id": 1,
            "board": 3,
            "title": "Q4 Marketing Launch",
            "description": "Plan and execute holiday marketing campaign for Q4.",
            "is_completed": "pending",
            "created_at": "26-08-2025 18:20:30",
            "created_by": "@arjun03",
            "updated_at": "26-08-2025 18:20:30",
            "updated_by": "@arjun03",
            "task_lists": [
                {
                    "tasklist_id": 1,
                    "task_card": 1,
                    "tasklist_title": "Define campaign goals",
                    "tasklist_description": "Set SMART goals for holiday launch.",
                    "priority": "High",
                    "label_color": "red",
                    "start_date": "2025-09-01",
                    "due_date": "2025-09-05",
                    "created_at": "27-08-2025 10:09:29",
                    "created_by": "@arjun03",
                    "updated_at": "08-09-2025 10:04:14",
                    "is_completed": false,
                    "updated_by": "@arjun03",
                    "assigned_to": null,
                    "images": [
                        "http://127.0.0.1:8000/media/task_images/20250713_OHR.YoungShark_EN-IN1362768509_UHD_bing.jpg"
                    ],
                    "attachments": [
                        "http://127.0.0.1:8000/media/task_attachments/20250713_OHR.YoungShark_EN-IN1362768509_UHD_bing.jpg"
                    ],
                    "comments": [],
                    "checklist_progress": 50.0,
                    "checklist_items": {
                        "title": "Project Checklist",
                        "items": [
                            {
                                "name": "Setup Backend",
                                "done": true
                            },
                            {
                                "name": "Setup Frontend",
                                "done": true
                            },
                            {
                                "name": "Create Database",
                                "done": false
                            },
                            {
                                "name": "Deploy",
                                "done": false
                            }
                        ]
                    }
                },
                {
                    "tasklist_id": 2,
                    "task_card": 1,
                    "tasklist_title": "Content planning",
                    "tasklist_description": "Decide creatives, copies, and video ads",
                    "priority": "Medium",
                    "label_color": "blue",
                    "start_date": "2025-09-06",
                    "due_date": "2025-09-12",
                    "created_at": "27-08-2025 10:14:16",
                    "created_by": "@arjun03",
                    "updated_at": "03-09-2025 17:13:39",
                    "is_completed": false,
                    "updated_by": null,
                    "assigned_to": {
                        "user_id": 3,
                        "full_name": "Arjun Sharma"
                    },
                    "images": [],
                    "attachments": [],
                    "comments": [],
                    "checklist_progress": 0.0,
                    "checklist_items": {
                        "title": "Checklist",
                        "items": [
                            {
                                "name": "video edit",
                                "done": false
                            }
                        ]
                    }
                },
                {
                    "tasklist_id": 17,
                    "task_card": 1,
                    "tasklist_title": "video edit",
                    "tasklist_description": "",
                    "priority": "low",
                    "label_color": "green",
                    "start_date": null,
                    "due_date": null,
                    "created_at": "02-09-2025 17:40:43",
                    "created_by": "@arjun03",
                    "updated_at": "02-09-2025 17:40:43",
                    "is_completed": false,
                    "updated_by": null,
                    "assigned_to": null,
                    "images": [],
                    "attachments": [],
                    "comments": [],
                    "checklist_progress": 0,
                    "checklist_items": {}
                },
                {
                    "tasklist_id": 18,
                    "task_card": 1,
                    "tasklist_title": "Photo edit",
                    "tasklist_description": "",
                    "priority": "low",
                    "label_color": "green",
                    "start_date": null,
                    "due_date": null,
                    "created_at": "02-09-2025 17:55:03",
                    "created_by": "@arjun03",
                    "updated_at": "02-09-2025 17:55:03",
                    "is_completed": false,
                    "updated_by": null,
                    "assigned_to": null,
                    "images": [],
                    "attachments": [],
                    "comments": [],
                    "checklist_progress": 0,
                    "checklist_items": {}
                }
            ]
        }
    ]
}
```

>>>>>>> 691fd223ebf513a876c2b384200b00a927a55ae9
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>
