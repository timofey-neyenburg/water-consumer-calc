def get_id():
    from uuid import uuid4
    return str(uuid4())


def timestamp_now() -> int:
    import time
    import datetime

    return (
        int(
            time.mktime(
                datetime.datetime
                .now(datetime.timezone.utc)
                .timetuple()
            )
        )
    )


def is_os_windows():
    import sys
    return "win" in sys.platform.lower()


def is_os_linux():
    import sys
    return "linux" in sys.platform.lower()