from app.repositories.road_repository import snap_point, batch_snap


async def process_snap(lat, lon):

    result = await snap_point(lat, lon)

    if not result:
        return None

    return {
        "road_id": result["road_id"],
        "snapped_lat": result["lat"],
        "snapped_lon": result["lon"]
    }


async def process_batch_snap(points):

    rows = await batch_snap(points)

    result = []

    for r in rows:

        result.append({
            "id": r["id"],
            "road_id": r["road_id"],
            "road_type": r["road_type"],
            "snapped_lat": r["lat"],
            "snapped_lon": r["lon"]
        })

    return result