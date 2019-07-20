from service.service import handle_schedule

routers = {
    "/schedule": ("POST", handle_schedule),
}

