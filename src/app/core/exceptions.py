from fastapi import HTTPException, status

class TaskNotFoundError(HTTPException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )

class ValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

class DuplicateError(HTTPException):
    def __init__(self, resource: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} already exists"
        )
