from datetime import datetime


def create_report(
    train_info_rows,
    train_schedule_rows,
    start_time,
    end_time
):

    duration = end_time - start_time

    total_rows = (
        train_info_rows +
        train_schedule_rows
    )

    return {
        "status": "Success",
        "files": 2,
        "train_info_rows": train_info_rows,
        "train_schedule_rows": train_schedule_rows,
        "total_rows": total_rows,
        "duration": str(duration),
        "result": "Completed",
        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
    }