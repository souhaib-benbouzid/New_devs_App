from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user
from decimal import Decimal

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

# Note: In a real application, properties would be fetched from the database with tenant filtering, but for this we are requested not to change the code structure, so we are using a static mapping.
# eg: SELECT id, name FROM properties WHERE tenant_id = :tenant_id
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
    
    # Verify the property belongs to this tenant
    tenant_props = TENANT_PROPERTIES.get(tenant_id, [])
    if not any(p["id"] == property_id for p in tenant_props):
        raise HTTPException(status_code=403, detail="Property does not belong to your tenant")
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    
    # Round precisely in Decimal (base-10) before converting to float for JSON
    total_revenue = Decimal(revenue_data['total']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
   
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": float(total_revenue),
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
