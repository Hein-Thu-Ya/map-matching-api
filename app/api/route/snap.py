from fastapi import APIRouter, HTTPException
from app.schemas.snap_schemas import SnapRequest, BatchSnapRequest
from app.service.snap_service import process_snap, process_batch_snap

router = APIRouter()


@router.post("/single_snap")

async def snap_location(data: SnapRequest):

    result = await process_snap(data.lat, data.lon)

    if not result:
        raise HTTPException(status_code=404, detail="No nearby road found")

    return result


@router.post("/batch_snap")

async def snap_batch(data: BatchSnapRequest):

    points = [p.model_dump() for p in data.points]

    result = await process_batch_snap(points)
    if not result:
        raise HTTPException(status_code=404, detail="No nearby road found")

    return {"results": result}