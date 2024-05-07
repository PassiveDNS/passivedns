from time import time

from fastapi import APIRouter
from pydantic import BaseModel

from apiv2.auth import get_current_user
from apiv2.utils import check_admin_user_role
from models.domain_name import DomainNameFilterNotFound, DomainNameSortNotFound, DomainName
from views.domain_name import alert_list_export, alert_list
from views.misc import error_view

alert_router = APIRouter()

class List(BaseModel):
    filter: str
    filter_by: str
    sort_by: str
    limit: str
    days: str
    export: str


@alert_router.get("/alert")
@check_admin_user_role()
def manage_alert(list_data: List):
    try:
        user = get_current_user()
        username = user.username

        input_filter = list_data.filter
        input_filter_by = list_data.filter_by
        sort_by = list_data.sort_by
        limit_str = list_data.limit
        days_str = list_data.days

        export = list_data.export

        if not limit_str.isdigit():
            return error_view(400, 'invalid limit')

        if not days_str.isdigit():
            return error_view(400, 'invalid days count')

        limit = int(limit_str)
        days = int(days_str)

        t1 = time()
        dn_list = DomainName.list_recent_changes(
            username, days, input_filter, input_filter_by, sort_by, limit
        )
        t2 = time()
        transaction_time = round(t2 - t1, 2)

        if export is not None and export != '':
            return alert_list_export(dn_list, export)
        else:
            return alert_list(dn_list, transaction_time)

    except DomainNameFilterNotFound:
        return error_view(400, "invalid filter field")

    except DomainNameSortNotFound:
        return error_view(400, "invalid sort field")