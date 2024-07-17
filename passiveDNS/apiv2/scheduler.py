from fastapi import APIRouter, Depends, HTTPException

from passiveDNS.utils.channels.send import alert_all
from passiveDNS.apiv2.domain_name import put
from passiveDNS.apiv2.auth import get_current_user
from passiveDNS.models.domain_name import (
    DomainName,
    DomainNameFilterNotFound,
    DomainNameSortNotFound,
)
from passiveDNS.models.user import User
from passiveDNS.db.database import ObjectNotFound

scheduler_router = APIRouter()


@scheduler_router.get("/scheduler/alerts")
async def get_full_dn_list():
    dn_list = DomainName.full_list()
    return {"msg": "full domain name list retrieved", "dn_list": dn_list}


@scheduler_router.post("/scheduler/alerts")
async def alert_all_users_dn_changes(user: User = Depends(get_current_user)):
    username = user.username

    try:
        dn_list = DomainName.list_recent_changes(
            username, 1, "", "domainName", "domainName", 25
        )
    except DomainNameFilterNotFound:
        raise HTTPException(status_code=400, detail="invalid filter field")
    except DomainNameSortNotFound:
        raise HTTPException(status_code=400, detail="invalid sort field")

    try:
        alert_all(dn_list)
    except ObjectNotFound as o:
        raise HTTPException(status_code=404, detail=str(o))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"msg": "alerts are being sent"}


@scheduler_router.put("/scheduler/dn/{domain_name}")
async def update_dn(domain_name):
    # use the same workflow as for the user
    return await put(domain_name)
