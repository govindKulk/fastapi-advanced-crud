from fastapi import FastAPI,  HTTPException, status
from app.routers import tasks
from pydantic import BaseModel


task_app = FastAPI(
    title="Task Management API",
    description="A simple Task Management API built with FastAPI",
    version="1.0.0",
)

task_app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


class RootResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

@task_app.get(
    "/",
    response_model=RootResponse,
    responses={500: {"model": ErrorResponse, "description": "Internal Server Error"},
               200: {"model": RootResponse, "description": "Successful Response", "name": "govind"}},
    tags=["root"],
)
def read_root() -> RootResponse:
    try:
        return RootResponse(message="Welcome to the Task Management API!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(task_app, host="0.0.0.0", port=8000)
