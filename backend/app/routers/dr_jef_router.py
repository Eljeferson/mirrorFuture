"""
Backward Compatibility Proxy for Mirror Future Router.
Re-exports router and all route symbols from mirror_future_router.
"""

from app.routers.mirror_future_router import router, analyze_image_forensics, simulate_social_twins, full_photo_simulation

__all__ = ["router", "analyze_image_forensics", "simulate_social_twins", "full_photo_simulation"]
