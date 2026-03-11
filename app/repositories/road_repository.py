from app.core.database import get_pool


async def snap_point(lat, lon):

    query = """
    SELECT
        r.gid AS road_id,
        ST_Y(ST_ClosestPoint(r.geom,gps)) AS lat,
        ST_X(ST_ClosestPoint(r.geom,gps)) AS lon
    FROM road r
    CROSS JOIN (
        SELECT ST_SetSRID(ST_Point($1,$2),4326) AS gps
    ) p
    WHERE ST_DWithin(
        r.geom::geography,
        p.gps::geography,
        20
    )
    ORDER BY r.geom <-> p.gps
    LIMIT 1
    """

    pool = await get_pool()

    async with pool.acquire() as conn:

        row = await conn.fetchrow(query, lon, lat)

    return row



##____batch snap by path selection____##
async def batch_snap(points):

    lats = [float(p["lat"]) for p in points]
    lons = [float(p["lon"]) for p in points]

    query = """
    WITH gps_points AS (
        SELECT 
            row_number() OVER () AS id,
            ST_SetSRID(ST_MakePoint(lon, lat), 4326) AS geom
        FROM UNNEST($1::float8[], $2::float8[]) AS t(lat, lon)
    )

    SELECT
        g.id,
        r.gid AS road_id,
        r.fclass AS road_type,
        ST_Distance(
            g.geom::geography,
            r.geom::geography
        ) AS dist,
        ST_Y(ST_ClosestPoint(r.geom, g.geom)) AS lat,
        ST_X(ST_ClosestPoint(r.geom, g.geom)) AS lon
    FROM gps_points g
    CROSS JOIN LATERAL (
        SELECT gid, geom, fclass
        FROM road
        WHERE ST_DWithin(
            geom::geography,
            g.geom::geography,
            50
        )
        ORDER BY geom <-> g.geom
        LIMIT 5
    ) r
    ORDER BY g.id;
    """

    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, lats, lons)

    # -----------------------------
    # Group candidates per GPS point
    # -----------------------------
    candidates = {}
    for r in rows:
        pid = r["id"]

        if pid not in candidates:
            candidates[pid] = []

        candidates[pid].append(dict(r))

    # -----------------------------
    # Road hierarchy weight
    # -----------------------------
    def hierarchy_weight(rt):

        if rt in ("motorway", "trunk"):
            return 1
        elif rt == "primary":
            return 2
        elif rt == "secondary":
            return 3
        elif rt == "tertiary":
            return 4
        elif rt == "residential":
            return 5
        elif rt == "service":
            return 6
        else:
            return 7

    # -----------------------------
    # Path selection
    # -----------------------------
    best_path = []
    prev_road = None

    for pid in sorted(candidates.keys()):

        best = None
        best_score = float("inf")

        for c in candidates[pid]:

            score = c["dist"]

            # hierarchy penalty
            score += hierarchy_weight(c["road_type"]) * 5

            # continuity bonus
            if prev_road and c["road_id"] == prev_road:
                score -= 20

            if score < best_score:
                best_score = score
                best = c

        best_path.append(best)
        prev_road = best["road_id"]

    return best_path