from datetime import datetime
from plugins_func.register import register_function, ToolType, ActionResponse, Action

get_calendar_function_desc = {
    "type": "function",
    "function": {
        "name": "get_calendar",
        "description": (
            "Get standard calendar information for specific dates. "
            "Users can specify query content, such as: date information, weekday, day of year, week number, timezone information, etc. "
            "If no query content is specified, it defaults to querying basic date information. "
            "For basic queries like 'what's today's date', 'today's date', please use the information in context directly, don't call this tool."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date to query, format YYYY-MM-DD, for example 2024-01-01. If not provided, uses current date",
                },
                "query": {
                    "type": "string",
                    "description": "Content to query, such as date information, weekday, day of year, week number, timezone information, etc.",
                },
            },
            "required": [],
        },
    },
}


@register_function("get_calendar", get_calendar_function_desc, ToolType.WAIT)
def get_calendar(date=None, query=None):
    """
    Get standard calendar information for specific dates
    """
    from core.utils.cache.manager import cache_manager, CacheType

    # If date parameter is provided, use specified date; otherwise use current date
    if date:
        try:
            now = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return ActionResponse(
                Action.REQLLM,
                f"Date format error, please use YYYY-MM-DD format, for example: 2024-01-01",
                None,
            )
    else:
        now = datetime.now()

    current_date = now.strftime("%Y-%m-%d")

    # If query is None, use default text
    if query is None:
        query = "Default query date information"

    # Try to get date information from cache
    date_cache_key = f"calendar_info_{current_date}"
    cached_date_info = cache_manager.get(CacheType.CALENDAR, date_cache_key)
    if cached_date_info:
        return ActionResponse(Action.REQLLM, cached_date_info, None)

    response_text = f"Based on the following information, respond to the user's query request and provide information related to {query}:\n"

    # Get basic date information
    weekday = now.strftime("%A")
    month_name = now.strftime("%B")
    day_of_year = now.strftime("%j")
    week_number = now.strftime("%U")
    
    response_text += (
        "Calendar information:\n"
        f"Date: {now.strftime('%B %d, %Y')}\n"
        f"Weekday: {weekday}\n"
        f"Day of year: {day_of_year}\n"
        f"Week number: {week_number}\n"
        f"ISO format: {now.strftime('%Y-%m-%d')}\n"
    )

    # Cache calendar information
    cache_manager.set(CacheType.CALENDAR, date_cache_key, response_text)

    return ActionResponse(Action.REQLLM, response_text, None)
