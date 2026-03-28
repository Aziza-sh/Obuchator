from fastapi.responses import JSONResponse


def success_response(data=None):

    return JSONResponse(status_code=200, content={"success": True, "data": data})


def error_response(message: str, status_code: int = 400):

    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"message": message}},
    )
