from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(self, detail: str = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NewsNotFoundException(Exception):
    def __init__(self, news_id: int):
        self.news_id = news_id


class MetricsException(Exception):
    pass
