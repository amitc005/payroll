from enum import Enum


class JobGroup(Enum):
    JOB_GROUP_A = "A"
    JOB_GROUP_B = "B"

    HOURLY_PAY = {JOB_GROUP_A: 20, JOB_GROUP_B: 30}
    OVERTIME_PAY = {JOB_GROUP_A: 10, JOB_GROUP_B: 15}
