from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()


# Tenant-to-properties mapping (mirrors seed data in database/seed.sql)
TENANT_PROPERTIES = {
    "tenant-a": [
        {"id": "prop-001", "name": "Beach House Alpha"},
        {"id": "prop-002", "name": "City Apartment Downtown"},
        {"id": "prop-003", "name": "Country Villa Estate"},
    ],
    "tenant-b": [
        {"id": "prop-001", "name": "Mountain Lodge Beta"},
        {"id": "prop-004", "name": "Lakeside Cottage"},
        {"id": "prop-005", "name": "Urban Loft Modern"},
    ],
}


@router.get("/dashboard/properties")
async def get_dashboard_properties(
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, str]]:
    """Return only the properties that belong to the current user's tenant."""
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    return TENANT_PROPERTIES.get(tenant_id, [])


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    total_revenue_float = float(revenue_data['total'])
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": total_revenue_float,
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
