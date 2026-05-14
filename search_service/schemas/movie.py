from pydantic import BaseModel


class MovieNotify(BaseModel):
    id: int
    title: str
    release_year: int
    summary: str
    duration_minutes: int
    age_limit: int


class MovieSearchResult(BaseModel):
    id: int
    title: str
    release_year: int
    summary: str


class SearchResponse(BaseModel):
    query: str
    results: list[MovieSearchResult]
