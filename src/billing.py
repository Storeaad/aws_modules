import logging
from datetime import datetime, timedelta

import boto3

from src.settings.logger import logger_setting

TODAY = datetime.today()
CLIENT = boto3.client("ce")


def billing_summary():
    today = TODAY.strftime("%Y-%m-%d")
    start_date = (TODAY - timedelta(days=TODAY.day - 1)).strftime("%Y-%m-%d")

    total_cost_response = CLIENT.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": today}, Granularity="MONTHLY", Metrics=["UnblendedCost"]
    )

    cost_section = total_cost_response["ResultsByTime"][0]["Total"]["UnblendedCost"]

    total_cost = float(cost_section["Amount"])
    currency = cost_section["Unit"]

    service_cost_response = CLIENT.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": today},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    groups = service_cost_response["ResultsByTime"][0]["Groups"]
    active_services = {g.get("Keys")[0]: g.get("Metrics")["UnblendedCost"]["Amount"] for g in groups}
    active_service_counts = len(groups)

    return {
        "total_cost": total_cost,
        "date_range": f"{start_date} ~ {today}",
        "currency": currency,
        "active_services": active_services,
        "active_service_counts": active_service_counts,
    }


if __name__ == "__main__":
    logger_setting(brand_name="AWS BUDGET REPORT")

    logger = logging.getLogger("")

    summary = billing_summary()
    message = (
        f"** AWS Billing Summary [{summary['date_range']}] 📊 **\n"
        f"  {'-' * 60}\n"
        f"\n   📅 이번 달 총 사용 비용: *{summary['total_cost']:.2f} {summary['currency']}*\n"
        f"\n   ** 🛠️ 활성 서비스 수: {summary['active_service_counts']} 개 **\n"
    )

    for service_name, cost in summary["active_services"].items():
        message += f"\t- {service_name}: ${cost}\n"

    logger.info(message, extra={"notify_slack": True})
