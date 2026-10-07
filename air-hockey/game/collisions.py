import math


def handle_paddle_collision(puck, paddle):
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    dist = math.hypot(dx, dy)
    min_dist = puck.radius + paddle.radius

    if dist >= min_dist:
        return False

    # Collision normal (paddle -> puck); fall back to the puck's reverse heading
    if dist > 1e-9:
        nx, ny = dx / dist, dy / dist
    else:
        speed = math.hypot(puck.vx, puck.vy) or 1.0
        nx, ny = -puck.vx / speed, -puck.vy / speed

    # 1. Resolve overlap: place the puck exactly on the paddle's surface
    puck.x = paddle.x + nx * min_dist
    puck.y = paddle.y + ny * min_dist

    # 2. Reflect velocity relative to the paddle, only if approaching
    pvx = getattr(paddle, "vx", 0.0)
    pvy = getattr(paddle, "vy", 0.0)
    rvx, rvy = puck.vx - pvx, puck.vy - pvy
    vn = rvx * nx + rvy * ny

    if vn < 0:
        rvx -= 2 * vn * nx
        rvy -= 2 * vn * ny

    puck.vx, puck.vy = rvx + pvx, rvy + pvy
    return True