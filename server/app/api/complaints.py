from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_complaint_service
from app.config import settings
from app.schemas.common import PaginatedResponse
from app.schemas.complaint import AIComplaintResponse, ComplaintCreate, ComplaintRead, ComplaintUpdate
from app.services.complaint_service import ComplaintService

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintRead, status_code=status.HTTP_201_CREATED)
def create_complaint(
    payload: ComplaintCreate,
    service: ComplaintService = Depends(get_complaint_service),
) -> ComplaintRead:
    return ComplaintRead.model_validate(service.create(payload))


@router.get("", response_model=PaginatedResponse[ComplaintRead])
def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    status_filter: str | None = Query(None, alias="status"),
    severity: str | None = Query(None),
    service: ComplaintService = Depends(get_complaint_service),
) -> PaginatedResponse[ComplaintRead]:
    items, total = service.list(skip=skip, limit=limit, status=status_filter, severity=severity)
    return PaginatedResponse(
        items=[ComplaintRead.model_validate(item) for item in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{complaint_id}", response_model=AIComplaintResponse)
def get_complaint(
    complaint_id: str,
    service: ComplaintService = Depends(get_complaint_service),
) -> AIComplaintResponse:
    complaint = service.get(complaint_id)
    return service.to_ai_response(complaint)


@router.patch("/{complaint_id}", response_model=ComplaintRead)
def update_complaint(
    complaint_id: str,
    payload: ComplaintUpdate,
    service: ComplaintService = Depends(get_complaint_service),
) -> ComplaintRead:
    return ComplaintRead.model_validate(service.update(complaint_id, payload))
