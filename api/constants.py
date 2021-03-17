from decimal import Decimal
from enum import Enum


class JobGroup(Enum):
    JOB_GROUP_A = "A"
    JOB_GROUP_B = "B"

    HOURLY_PAY = {JOB_GROUP_A: Decimal("20"), JOB_GROUP_B: Decimal("30")}
