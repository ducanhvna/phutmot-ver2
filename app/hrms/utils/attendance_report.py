from datetime import timedelta, datetime
from enum import Enum


class InoutMode:
    In = "In"
    Out = "Out"
    NoneMode = "None"

    @staticmethod
    def to_string(value):
        if value in [InoutMode.In, InoutMode.Out, InoutMode.NoneMode]:
            return value
        elif isinstance(value, str):
            return value
        raise TypeError(f"Invalid InoutMode value: {value}")


class AttendanceAttemptInOut:
    def __init__(self, attempt, inout=None):
        self.attempt = attempt
        self.inout = inout

    @property
    def display_hour(self):
        return self.attempt.hour if self.attempt else 0

    def to_dict(self):
        return {
            "attempt": self.attempt,
            "inout": (
                InoutMode.to_string(self.inout) if self.inout else None
            ),
            "display_hour": self.display_hour,
        }


class KidMode(Enum):
    NONE = "None"
    SBEGIN60 = "SBegin60"
    SBEGIN30SEND30 = "SBegin30SEnd30"
    SEND60 = "SEnd60"
    RBEGIN30REND30 = "RBegin30REnd30"
    RBEGIN60 = "RBegin60"
    REND60 = "REnd60"


class CoupleInout:
    def __init__(self, itemIn, itemOut, typeio=None):
        self.itemIn = itemIn
        self.itemOut = itemOut
        self.atoffice_time = 0
        self.nightWorkTime = 0
        self.holidayWorkTime = 0
        self.nightHolidayWorkTime = 0
        self.typeio = typeio if typeio in ['IO', 'OI', 'II', 'OO'] else "Unknown"

    def to_dict(self):
        return {
            "itemIn": (
                self.itemIn.to_dict()
                if isinstance(self.itemIn, AttendanceAttemptInOut)
                else InoutMode.to_string(self.itemIn)
            ),
            "itemOut": (
                self.itemOut.to_dict()
                if isinstance(self.itemOut, AttendanceAttemptInOut)
                else InoutMode.to_string(self.itemOut)
            ),
            "atoffice_time": self.atoffice_time,
            "nightWorkTime": self.nightWorkTime,
            "holidayWorkTime": self.holidayWorkTime,
            "nightHolidayWorkTime": self.nightHolidayWorkTime,
            "typeio": self.typeio,
        }


def merge_and_split_couples(couple1, couple2, keys_to_check):
    merged_list = couple1 + couple2
    split_list = [[] for _ in range(5)]  # Create a list containing 5 empty lists for each section

    for couple in merged_list:
        item_in = couple.itemIn
        item_out = couple.itemOut

        attempt_in = item_in.attempt
        attempt_out = item_out.attempt
        key_index = 0
        for key in keys_to_check:
            if attempt_in <= key <= attempt_out:
                split_list[key_index].append(CoupleInout(
                    AttendanceAttemptInOut(attempt_in if key_index < 1 else max(attempt_in, split_list[key_index - 1]), InoutMode.In),
                    AttendanceAttemptInOut(key, InoutMode.Out),
                    typeio=couple.typeio
                ))
                if (key_index < 3) and (keys_to_check[key_index + 1] < attempt_out):
                    split_list[key_index + 1].append(CoupleInout(
                        AttendanceAttemptInOut(key, InoutMode.In),
                        AttendanceAttemptInOut(keys_to_check[key_index + 1], InoutMode.Out),
                        typeio=couple.typeio
                    ))
                else:
                    split_list[key_index + 1].append(CoupleInout(
                        AttendanceAttemptInOut(key, InoutMode.In),
                        AttendanceAttemptInOut(attempt_out, InoutMode.Out),
                        typeio=couple.typeio
                    ))
                    break
            elif attempt_in > key:
                if (key_index == 3) or (keys_to_check[key_index + 1] > attempt_out):
                    split_list[key_index + 1].append(CoupleInout(
                        AttendanceAttemptInOut(attempt_in, InoutMode.In),
                        AttendanceAttemptInOut(attempt_out if key_index == 3 else min(attempt_out, keys_to_check[key_index + 1]), InoutMode.Out),
                        typeio=couple.typeio
                    ))
                    break
            elif attempt_out < key:
                if (key_index == 0) or (keys_to_check[key_index - 1] < attempt_in):
                    split_list[key_index].append(CoupleInout(
                        AttendanceAttemptInOut(attempt_in, InoutMode.In),
                        AttendanceAttemptInOut(attempt_out, InoutMode.Out),
                        typeio=couple.typeio
                    ))
                    break

    return split_list


def serialize_datetime(obj):
    """Helper function to convert datetime, CoupleInout, and AttendanceAttemptInOut objects to string or dict."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, CoupleInout):
        return obj.to_dict()
    if isinstance(obj, AttendanceAttemptInOut):
        return obj.to_dict()
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")


def check_leave_valid_type1(type_name, element, shift_start_datetime, shift_end_datetime):
    result = False
    c1 = True if element['request_date_from'] else False
    c2 = True if ['request_date_to'] else False
    if c1 and c2:
        try:
            c3 = not element['request_date_from'].replace(hour=0, minute=0, second=0, microsecond=0) > shift_end_datetime
            c4 = not element['request_date_to'].replace(hour=23, minute=59, second=59, microsecond=999999) < shift_start_datetime
            c5 = type_name in element['holiday_status_name'].lower()
        except Exception as ex:
            print('check_leave_valid_type1: ', ex)
            c3 = False
            c4 = False
            c5 = False
        result = c3 and c4 and c5
    return result


def check_leave_valid_type2(type_name, element, date):
    result = False
    c1 = True if ['attendance_missing_from'] else False
    c2 = True if ['attendance_missing_to'] else False
    if c1 and c2:
        try:
            c3 = not element['request_date_from'].day == date.day
            c4 = not element['request_date_to'].month == date.month
            c5 = type_name in element['holiday_status_name'].lower()
        except Exception as ex:
            print('check_leave_valid_type1: ', ex)
            c3 = False
            c4 = False
            c5 = False
        result = c3 and c4 and c5
    return result


def check_explaination_valid_type2(element, date, reason=None, type_name=None):
    result = False
    c1 = True if ['invalid_date'] else False
    c2 = True if ['attendance_missing_to'] else False
    c5 = True
    c6 = True
    if c1 and c2:
        try:
            c3 = not element['invalid_date'].day == date.day
            c4 = not element['invalid_date'].month == date.month
            if type_name:
                c5 = type_name in element['invalid_type'].lower()
            if reason:
                c6 = reason in element['reason'].lower()
        except Exception as ex:
            print('check_explaination_valid_type2: ', ex)
            c3 = False
            c4 = False
            c5 = False
        result = c3 and c4 and c5 and c6
    return result


def find_in_in_couple(list_attempt, scheduling_record):
    result = []
    stack = []

    for item in list_attempt:
        if item.inout != InoutMode.Out:
            stack.append(item)
        elif stack:
            couple = CoupleInout(itemIn=stack.pop(0), itemOut=item)
            couple.atoffice_time = calculate_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightWorkTime = calculate_night_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.holidayWorkTime = calculate_holiday_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightHolidayWorkTime = calculate_night_holiday_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            result.append(couple)

    if not result and len(list_attempt) > 1:
        result.append(CoupleInout(itemIn=list_attempt[0], itemOut=list_attempt[-1]))

    return result


def find_in_out_couple(list_attempt, scheduling_record):
    result = []
    stack = []

    for item in list_attempt:
        if item.inout == InoutMode.In:
            stack.append(item)
        elif item.inout == InoutMode.Out and stack:
            couple = CoupleInout(itemIn=stack.pop(0), itemOut=item)
            couple.atoffice_time = calculate_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightWorkTime = calculate_night_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.holidayWorkTime = calculate_holiday_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightHolidayWorkTime = calculate_night_holiday_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            result.append(couple)

    if not result and len(list_attempt) > 1:
        result.append(CoupleInout(itemIn=list_attempt[0], itemOut=list_attempt[-1]))

    return result


def get_list_couple_out_in(list_couple_io, scheduling_record):
    result = []
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    include_late_early = False
    if shift_start_datetime and shift_end_datetime and list_couple_io:
        if shift_start_datetime < list_couple_io[0].itemIn.attempt and include_late_early:
            couple = CoupleInout(
                itemIn=AttendanceAttemptInOut(attempt=shift_start_datetime),
                itemOut=AttendanceAttemptInOut(attempt=list_couple_io[0].itemIn.attempt)
            )
            couple.atoffice_time = calculate_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightWorkTime = calculate_night_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.holidayWorkTime = calculate_holiday_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightHolidayWorkTime = calculate_night_holiday_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            result.append(couple)

        for i in range(1, len(list_couple_io)):
            couple = CoupleInout(
                itemIn=AttendanceAttemptInOut(attempt=list_couple_io[i - 1].itemOut.attempt),
                itemOut=AttendanceAttemptInOut(attempt=list_couple_io[i].itemIn.attempt)
            )
            couple.atoffice_time = calculate_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightWorkTime = calculate_night_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.holidayWorkTime = calculate_holiday_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightHolidayWorkTime = calculate_night_holiday_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            result.append(couple)

        if shift_end_datetime > list_couple_io[-1].itemOut.attempt and include_late_early:
            couple = CoupleInout(
                itemIn=AttendanceAttemptInOut(attempt=list_couple_io[-1].itemOut.attempt),
                itemOut=AttendanceAttemptInOut(attempt=shift_end_datetime)
            )
            couple.atoffice_time = calculate_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightWorkTime = calculate_night_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.holidayWorkTime = calculate_holiday_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            couple.nightHolidayWorkTime = calculate_night_holiday_without_inout(couple.itemIn.attempt, couple.itemOut.attempt, scheduling_record)
            result.append(couple)

    return result


def kimode_worktime_without_inout(real_time_in, real_time_out, shift, kidmod, kid_mode_stage1_end_datetime, kid_mode_stage1_datetime, kid_mode_stage2_end_datetime, kid_mode_stage2_datetime, select_off_stage):
    result = [0, 0, 0]
    if shift and kidmod != 'None':
        current_program = (real_time_out if real_time_out <= kid_mode_stage1_end_datetime else kid_mode_stage1_end_datetime) - (real_time_in if real_time_in >= kid_mode_stage1_datetime else kid_mode_stage1_datetime)
        stage_first = max(0, current_program.total_seconds() // 60)

        current_program = (real_time_out if real_time_out <= kid_mode_stage2_end_datetime else kid_mode_stage2_end_datetime) - (real_time_in if real_time_in >= kid_mode_stage2_datetime else kid_mode_stage2_datetime)
        stage_second = max(0, current_program.total_seconds() // 60)

        result = [
            stage_first + stage_second if select_off_stage == 0 else (stage_second if select_off_stage == 2 else stage_first),
            0 if select_off_stage == 2 else stage_first,
            0 if select_off_stage == 1 else stage_second
        ]
    else:
        result = [0, 0, 0]

    return result


def process_leave_item_ho(scheduling_record, leave_item):
    attempt_with_inout_array = scheduling_record['attempt_with_inout_array']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    rest_start_datetime = scheduling_record['rest_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    rest_end_datetime = scheduling_record['rest_end_datetime']
    list_add_item_out = scheduling_record['list_add_item_out']

    for item in attempt_with_inout_array:
        if not item.attempt > leave_item['attendance_missing_to'] and not item.attempt < leave_item['attendance_missing_from']:
            item.inout = InoutMode.In

    if shift_start_datetime:
        if not shift_start_datetime > leave_item['attendance_missing_to'] and not shift_start_datetime < leave_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=shift_start_datetime, inout=InoutMode.In)
            attempt_with_inout_array.append(item)

        if rest_start_datetime and not rest_start_datetime > leave_item['attendance_missing_to'] and not rest_start_datetime < leave_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=rest_start_datetime, inout=InoutMode.Out)
            for in_out_add_item_before in [i for i in list_add_item_out if not i.attempt > item.attempt]:
                in_out_add_item_before.inout = InoutMode.NoneMode
            attempt_with_inout_array.append(item)

        if shift_end_datetime and not shift_end_datetime > leave_item['attendance_missing_to'] and not shift_end_datetime < leave_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=shift_end_datetime, inout=InoutMode.Out)
            for in_out_add_item_before in [i for i in list_add_item_out if not i.attempt > item.attempt]:
                in_out_add_item_before.inout = InoutMode.NoneMode
            attempt_with_inout_array.append(item)

        if rest_end_datetime and not rest_end_datetime > leave_item['attendance_missing_to'] and not rest_end_datetime < leave_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=rest_end_datetime, inout=InoutMode.In)
            attempt_with_inout_array.append(item)


def process_explanation_item_ho(scheduling_record, explaination_item):
    attempt_with_inout_array = scheduling_record['attempt_with_inout_array']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    rest_start_datetime = scheduling_record['rest_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    rest_end_datetime = scheduling_record['rest_end_datetime']
    list_add_item_out = scheduling_record['list_add_item_out']

    for item in attempt_with_inout_array:
        if not item.attempt > explaination_item['attendance_missing_to'] and not item.attempt < explaination_item['attendance_missing_from']:
            item.inout = InoutMode.In

    if shift_start_datetime:
        if not shift_start_datetime > explaination_item['attendance_missing_to'] and not shift_start_datetime < explaination_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=shift_start_datetime, inout=InoutMode.In)
            attempt_with_inout_array.append(item)

        if rest_start_datetime and not rest_start_datetime > explaination_item['attendance_missing_to'] and not rest_start_datetime < explaination_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=rest_start_datetime, inout=InoutMode.Out)
            for in_out_add_item_before in [i for i in list_add_item_out if not i.attempt > item.attempt]:
                in_out_add_item_before.inout = InoutMode.NoneMode
            attempt_with_inout_array.append(item)

        if shift_end_datetime and not shift_end_datetime > explaination_item['attendance_missing_to'] and not shift_end_datetime < explaination_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=shift_end_datetime, inout=InoutMode.Out)
            for in_out_add_item_before in [i for i in list_add_item_out if not i.attempt > item.attempt]:
                in_out_add_item_before.inout = InoutMode.NoneMode
            attempt_with_inout_array.append(item)

        if rest_end_datetime and not rest_end_datetime > explaination_item['attendance_missing_to'] and not rest_end_datetime < explaination_item['attendance_missing_from']:
            item = AttendanceAttemptInOut(attempt=rest_end_datetime, inout=InoutMode.In)
            attempt_with_inout_array.append(item)


def calculate_night_worktime_without_inout(real_timein, real_timeout, scheduling_record):
    is_night_stage_fist = scheduling_record['is_night_stage_fist']
    is_night_stage_last = scheduling_record['is_night_stage_last']
    night_stage_fist_start = scheduling_record['night_stage_fist_start']
    night_stage_fist_end = scheduling_record['night_stage_fist_end']
    night_stage_last_start = scheduling_record['night_stage_last_start']
    night_stage_last_end = scheduling_record['night_stage_last_end']
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    shift = scheduling_record['shift']
    result = 0
    if shift:
        stage_fist_worktime = 0
        stage_last_worktime = 0

        if is_night_stage_fist:
            stageStart = restStartDateTime if restStartDateTime < night_stage_fist_end else night_stage_fist_end
            current_program = (real_timeout.replace(second=0) if real_timeout < stageStart else stageStart) - (real_timein.replace(second=0) if real_timein > night_stage_fist_start else night_stage_fist_start)
            stage_fist = max(0, current_program.total_seconds() // 60)

            stageEnd = restEndDateTime if restEndDateTime > night_stage_fist_start else night_stage_fist_start
            current_program = (real_timeout.replace(second=0) if real_timeout < night_stage_fist_end else night_stage_fist_end) - (real_timein.replace(second=0) if real_timein > stageEnd else stageEnd)
            stage_second = max(0, current_program.total_seconds() // 60)
            stage_fist_worktime = stage_fist + stage_second

        if is_night_stage_last:
            stageStart = restStartDateTime if restStartDateTime < night_stage_last_end else night_stage_last_end
            current_program = (real_timeout.replace(second=0) if real_timeout < stageStart else stageStart) - (real_timein.replace(second=0) if real_timein > night_stage_last_start else night_stage_last_start)
            stage_fist = max(0, current_program.total_seconds() // 60)

            stageEnd = restEndDateTime if restEndDateTime > night_stage_last_start else night_stage_last_start
            current_program = (real_timeout.replace(second=0) if real_timeout < night_stage_last_end else night_stage_last_end) - (real_timein.replace(second=0) if real_timein > stageEnd else stageEnd)
            stage_second = max(0, current_program.total_seconds() // 60)
            stage_last_worktime = stage_fist + stage_second

        result = stage_fist_worktime + stage_last_worktime

    return int(result)


def calculate_worktime_without_inout(real_timein, real_timeout, scheduling_record):
    result = 0
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    shiftStartDateTime = scheduling_record['shift_start_datetime']
    shiftEndDateTime = scheduling_record['shift_end_datetime']
    real_timein = real_timein.replace(second=0)
    real_timeout = real_timeout.replace(second=0)

    # if shift:
    currentProgram = (real_timeout if real_timeout < restStartDateTime else restStartDateTime) - (real_timein if real_timein > shiftStartDateTime else shiftStartDateTime)
    stageFist = max(0, currentProgram.total_seconds() // 60)

    currentProgram = (real_timeout if real_timeout < shiftEndDateTime else shiftEndDateTime) - (real_timein if real_timein > restEndDateTime else restEndDateTime)
    stageSecond = max(0, currentProgram.total_seconds() // 60)

    result = stageFist + stageSecond

    return int(result)


def calculate_holiday_worktime_without_inout(real_timein, real_timeout, scheduling_record):
    holiday_start_datetime = scheduling_record['holiday_start_datetime']
    is_holiday = scheduling_record['is_holiday']
    shift_name = scheduling_record['shift_name']
    holiday_end_datetime = scheduling_record['holiday_end_datetime']
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    shift = scheduling_record['shift']
    # shiftStartDateTime = scheduling_record['shift_start_datetime']
    # shiftEndDateTime = scheduling_record['shift_end_datetime']

    result = 0
    if (shift and is_holiday and (calculate_worktime_without_inout(holiday_start_datetime, holiday_end_datetime, scheduling_record) > 0 or 'PH' in shift_name)):

        stageStart = restStartDateTime if restStartDateTime < holiday_end_datetime else holiday_end_datetime
        current_program = (real_timeout.replace(second=0) if real_timeout < stageStart else stageStart) - (real_timein.replace(second=0) if real_timein > holiday_start_datetime else holiday_start_datetime)
        stage_fist = max(0, int(current_program.total_seconds() // 60))

        stageEnd = restEndDateTime if restEndDateTime > holiday_start_datetime else holiday_start_datetime
        current_program = (real_timeout if real_timeout < holiday_end_datetime else holiday_end_datetime) - (real_timein.replace(second=0) if real_timein > stageEnd else stageEnd)
        stage_second = max(0, int(current_program.total_seconds() // 60))

        result = stage_fist + stage_second
    return result


def calculate_night_holiday_without_inout(real_timein, real_timeout, scheduling_record):
    holiday_night_stage_fist_start_datetime = scheduling_record['holiday_night_stage_fist_start_datetime']
    holiday_night_stage_fist_end_datetime = scheduling_record['holiday_night_stage_fist_end_datetime']
    holiday_night_stage_last_start_datetime = scheduling_record['holiday_night_stage_last_start_datetime']
    holiday_night_stage_last_end_datetime = scheduling_record['holiday_night_stage_last_end_datetime']
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    shift = scheduling_record['shift']
    result = 0
    if shift:
        stageFistWorktime = 0
        stageLastWorktime = 0

        if shift and holiday_night_stage_fist_end_datetime:
            stageStart = restStartDateTime if restStartDateTime < holiday_night_stage_fist_end_datetime else holiday_night_stage_fist_end_datetime
            currentProgram = (real_timeout.replace(second=0) if real_timeout < stageStart else stageStart) - (real_timein.replace(second=0) if real_timein > holiday_night_stage_fist_start_datetime else holiday_night_stage_fist_start_datetime)
            stageFist = max(0, int(currentProgram.total_seconds() // 60))

            stageEnd = restEndDateTime if restEndDateTime > holiday_night_stage_fist_start_datetime else holiday_night_stage_fist_start_datetime
            currentProgram = (real_timeout.replace(second=0) if real_timeout < holiday_night_stage_fist_end_datetime else holiday_night_stage_fist_end_datetime) - (real_timein.replace(second=0) if real_timein > stageEnd else stageEnd)
            stageSecond = max(0, int(currentProgram.total_seconds() // 60))

            stageFistWorktime = stageFist + stageSecond
        else:
            stageFistWorktime = 0

        if shift and holiday_night_stage_last_end_datetime:
            stageStart = restStartDateTime if restStartDateTime < holiday_night_stage_last_end_datetime else holiday_night_stage_last_end_datetime
            currentProgram = (real_timeout.replace(second=0) if real_timeout < stageStart else stageStart) - (real_timein.replace(second=0) if real_timein > holiday_night_stage_last_start_datetime else holiday_night_stage_last_start_datetime)
            stageFist = max(0, int(currentProgram.total_seconds() // 60))

            stageEnd = restEndDateTime if restEndDateTime > holiday_night_stage_last_start_datetime else holiday_night_stage_last_start_datetime
            currentProgram = (real_timeout.replace(second=0) if real_timeout < holiday_night_stage_last_end_datetime else holiday_night_stage_last_end_datetime) - (real_timein.replace(second=0) if real_timein > stageEnd else stageEnd)
            stageSecond = max(0, int(currentProgram.total_seconds() // 60))

            stageLastWorktime = stageFist + stageSecond
        else:
            stageLastWorktime = 0

        result = stageFistWorktime + stageLastWorktime

    return result


def check_last_in_out(scheduling_record):
    attempt_with_inout_array = scheduling_record['attempt_with_inout_array']
    list_addItem_out = scheduling_record['list_addItem_out']
    attempt_with_inout_array.sort(key=lambda x: x.attempt)

    if attempt_with_inout_array:
        if attempt_with_inout_array[-1].inout != InoutMode.Out:
            addItem = AttendanceAttemptInOut(attempt=attempt_with_inout_array[-1].attempt)
            addItem.inout = InoutMode.Out

            for in_out_addItem_before in [item for item in list_addItem_out if item.attempt <= attempt_with_inout_array[-1].attempt]:
                in_out_addItem_before.inout = InoutMode.NoneMode

            list_addItem_out.append(addItem)
            attempt_with_inout_array.append(addItem)

            add_in_item = AttendanceAttemptInOut(attempt=attempt_with_inout_array[-1].attempt + timedelta(milliseconds=10))
            add_in_item.inout = InoutMode.In
            attempt_with_inout_array.append(add_in_item)


def calculate_night_worktime_custom(scheduling_record, real_timein, real_timeout, nightStageStart, nightStageEnd):
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    # Đặt giây của thời gian bằng 0
    nightStageStart = nightStageStart.replace(second=0)
    nightStageEnd = nightStageEnd.replace(second=0)

    stageFistWorktime = 0
    # if shift:
    # Tính toán thời gian bắt đầu giai đoạn
    stageStart = restStartDateTime if restStartDateTime < nightStageEnd else nightStageEnd
    currentProgram = (real_timeout.replace(second=0) if real_timeout < stageStart else stageStart) - (real_timein.replace(second=0) if real_timein > nightStageStart else nightStageStart)
    stageFist = max(0, currentProgram.total_seconds() // 60)

    # Tính toán thời gian kết thúc giai đoạn
    stageEnd = restEndDateTime if restEndDateTime > nightStageStart else nightStageStart
    currentProgram = (real_timeout.replace(second=0) if real_timeout < nightStageEnd else nightStageEnd) - (real_timein.replace(second=0) if real_timein > stageEnd else stageEnd)
    stageSecond = max(0, currentProgram.total_seconds() // 60)

    stageFistWorktime = stageFist + stageSecond

    return int(stageFistWorktime)


def get_list_late_in_leaves(scheduling_record):
    _hrLeaves = scheduling_record['hr_leaves']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    list_late_in_leaves = [
        element for element in _hrLeaves if check_leave_valid_type1('đi muộn', element, shift_start_datetime, shift_end_datetime)
        # element['request_date_from']
        # and element['request_date_to']
        # and not element['request_date_from'].replace(hour=0, minute=0, second=0, microsecond=0) > shift_end_datetime
        # and not element['request_date_to'].replace(hour=23, minute=59, second=59, microsecond=999999) < shift_start_datetime
        # and 'đi muộn' in element['holiday_status_name'].lower()
    ]
    return list_late_in_leaves


def get_list_early_out_leaves(scheduling_record):
    _hrLeaves = scheduling_record['hr_leaves']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    list_early_out_leaves = [
        element for element in _hrLeaves if check_leave_valid_type1('về sớm', element, shift_start_datetime, shift_end_datetime)
        # element['request_date_from']
        # and element['request_date_to']
        # and not element['request_date_from'].replace(hour=0, minute=0, second=0, microsecond=0) > shift_end_datetime
        # and not element['request_date_to'].replace(hour=23, minute=59, second=59, microsecond=999999) < shift_start_datetime
        # and 'đi muộn' in element['holiday_status_name'].lower()
    ]
    return list_early_out_leaves


def check_is_night_stage_fist(scheduling_record):
    scheduling_record['is_night_stage_fist'] = scheduling_record['night_stage_fist_start'] and scheduling_record['night_stage_fist_end']


def check_is_night_stage_last(scheduling_record):
    scheduling_record['is_night_stage_last'] = scheduling_record['night_stage_last_start'] and scheduling_record['night_stage_last_end']


def calculate_night_stage_fist_start(scheduling_record):
    result = None
    shift = scheduling_record['shift']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    date = scheduling_record['date']
    if date and shift:
        fist_night_start = date.replace(hour=22, minute=0, second=0) - timedelta(days=1)
        fist_night_end = date.replace(hour=6, minute=0, second=0)

        if not fist_night_start > shift_end_datetime and not fist_night_end < shift_start_datetime:
            result = shift_start_datetime if fist_night_start < shift_start_datetime else fist_night_start
    scheduling_record['night_stage_fist_start'] = result


def calculate_night_stage_fist_end(scheduling_record):
    result = None
    shift = scheduling_record['shift']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    date = scheduling_record['date']
    if date and shift:
        fist_night_start = date.replace(hour=22, minute=0, second=0) - timedelta(days=1)
        fist_night_end = date.replace(hour=6, minute=0, second=0)

        if not fist_night_start > shift_end_datetime and not fist_night_end < shift_start_datetime:
            result = shift_end_datetime if fist_night_end > shift_end_datetime else fist_night_end
    scheduling_record['night_stage_fist_end'] = result


def calculate_night_stage_last_start(scheduling_record):
    result = None
    shift = scheduling_record['shift']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    date = scheduling_record['date']
    if date and shift:
        last_night_start = date.replace(hour=22, minute=0, second=0)
        last_night_end = date.replace(hour=6, minute=0, second=0) + timedelta(days=1)

        if not last_night_start > shift_end_datetime and not last_night_end < shift_start_datetime:
            result = shift_start_datetime if last_night_start < shift_start_datetime else last_night_start
    scheduling_record['night_stage_last_start'] = result


def calculate_night_stage_last_end(scheduling_record):
    result = None
    shift = scheduling_record['shift']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    date = scheduling_record['date']
    if date and shift:
        last_night_start = date.replace(hour=22, minute=0, second=0)
        last_night_end = date.replace(hour=6, minute=0, second=0) + timedelta(days=1)

        if not last_night_start > shift_end_datetime and not last_night_end < shift_start_datetime:
            result = shift_end_datetime if last_night_end > shift_end_datetime else last_night_end
    scheduling_record['night_stage_last_end'] = result


def calculate_holiday_night_stage_last_end_datetime(scheduling_record):
    result = None
    try:
        is_holiday = scheduling_record['is_holiday']
        is_night_stage_last = scheduling_record['is_night_stage_last']
        holiday_end_datetime = scheduling_record['holiday_end_datetime']
        holiday_start_datetime = scheduling_record['holiday_start_datetime']
        night_stage_last_end = scheduling_record['night_stage_last_end']
        night_stage_last_start = scheduling_record['night_stage_last_start']
        if is_night_stage_last and is_holiday:
            if not night_stage_last_start > holiday_end_datetime and \
               not night_stage_last_end < holiday_start_datetime:
                result = holiday_end_datetime if night_stage_last_end > holiday_end_datetime else night_stage_last_end
    except Exception as ex:
        print('calculate_holiday_night_stage_last_end_datetime: ', ex)
    scheduling_record['holiday_night_stage_last_end_datetime'] = result


def calculate_holiday_night_stage_last_start_datetime(scheduling_record):
    result = None
    try:
        is_holiday = scheduling_record['is_holiday']
        is_night_stage_last = scheduling_record['is_night_stage_last']
        holiday_end_datetime = scheduling_record['holiday_end_datetime']
        holiday_start_datetime = scheduling_record['holiday_start_datetime']
        night_stage_last_end = scheduling_record['night_stage_last_end']
        night_stage_last_start = scheduling_record['night_stage_last_start']
        if is_night_stage_last and is_holiday:
            if not night_stage_last_start > holiday_end_datetime and \
               not night_stage_last_end < holiday_start_datetime:
                result = holiday_start_datetime if night_stage_last_start < holiday_start_datetime else night_stage_last_start
    except Exception as ex:
        print('calculate_holiday_night_stage_last_start_datetime: ', ex)
    scheduling_record['holiday_night_stage_last_start_datetime'] = result


def calculate_holiday_night_stage_fist_start_datetime(scheduling_record):
    result = None
    try:
        is_holiday = scheduling_record['is_holiday']
        is_night_stage_fist = scheduling_record['is_night_stage_fist']
        holiday_end_datetime = scheduling_record['holiday_end_datetime']
        holiday_start_datetime = scheduling_record['holiday_start_datetime']
        night_stage_fist_end = scheduling_record['night_stage_fist_end']
        night_stage_fist_start = scheduling_record['night_stage_fist_start']
        if is_night_stage_fist and is_holiday:
            if not night_stage_fist_start > holiday_end_datetime and \
               not night_stage_fist_end < holiday_start_datetime:
                result = holiday_start_datetime if night_stage_fist_start < holiday_start_datetime else night_stage_fist_start
    except Exception as ex:
        print('calculate_holiday_night_stage_fist_start_datetime: ', ex)
    scheduling_record['holiday_night_stage_fist_start_datetime'] = result


def calculate_holiday_night_stage_fist_end_datetime(scheduling_record):
    result = None
    try:
        is_holiday = scheduling_record['is_holiday']
        is_night_stage_fist = scheduling_record['is_night_stage_fist']
        holiday_end_datetime = scheduling_record['holiday_end_datetime']
        holiday_start_datetime = scheduling_record['holiday_start_datetime']
        night_stage_fist_end = scheduling_record['night_stage_fist_end']
        night_stage_fist_start = scheduling_record['night_stage_fist_start']
        if is_night_stage_fist and is_holiday:
            if not night_stage_fist_start > holiday_end_datetime and \
               not night_stage_fist_end < holiday_start_datetime:
                result = holiday_end_datetime if night_stage_fist_end > holiday_end_datetime else night_stage_fist_end
    except Exception as ex:
        print('calculate_holiday_night_stage_fist_end_datetime: ', ex)
    scheduling_record['holiday_night_stage_fist_end_datetime'] = result


def calculate_holiday_start_datetime(scheduling_record):
    result = None
    try:
        is_holiday = scheduling_record['is_holiday']
        shift_start_datetime = scheduling_record['shift_start_datetime']
        holiday_calendar = scheduling_record['holiday_calendar']
        if is_holiday and shift_start_datetime:
            min_datetime = min(holiday_calendar, key=lambda x: x['date_from'])['date_from']
            result = shift_start_datetime if shift_start_datetime > min_datetime else min_datetime
    except Exception as ex:
        print('calculate_holiday_start_datetime: ', ex)
    scheduling_record['holiday_start_datetime'] = result


def calculate_holiday_end_datetime(scheduling_record):
    result = None
    try:
        is_holiday = scheduling_record['is_holiday']
        shift_end_datetime = scheduling_record['shift_end_datetime']
        holiday_calendar = scheduling_record['holiday_calendar']
        if is_holiday and shift_end_datetime:
            max_datetime = max(holiday_calendar, key=lambda x: x['date_to'])['date_to']
            result = shift_end_datetime if shift_end_datetime < max_datetime else max_datetime
    except Exception as ex:
        print('calculate_holiday_end_datetime: ', ex)
    scheduling_record['holiday_end_datetime'] = result


def check_is_holiday(scheduling_record):
    result = False
    try:
        shift_end_datetime = scheduling_record['shift_end_datetime']
        shift_start_datetime = scheduling_record['shift_start_datetime']
        date = scheduling_record['date']
        holiday_calendar = scheduling_record['holiday_calendar']
        if date and shift_end_datetime and shift_start_datetime:
            for holiday in holiday_calendar:
                if not holiday['date_from'].replace(hour=0, minute=0, second=0) > shift_end_datetime and \
                   not holiday['date_to'].replace(hour=0, minute=0, second=0) < shift_start_datetime:
                    result = True
                    break
    except Exception as ex:
        print('check_is_holiday: ', ex)
    scheduling_record['is_holiday'] = result


def process_leave_records(leave_records, scheduling_record):
    scheduling_record['kidmod'] = KidMode.NONE
    scheduling_record['convert_overtime'] = False
    print('Start process_leave_records: ', leave_records)
    for leave_item in leave_records:
        try:
            leave_item['holidayStatusName'] = leave_item['holiday_status_id'][0] if leave_item['holiday_status_id'][1] else ''
            if leave_item['attendance_missing_to']:
                leave_item['attendance_missing_to'] = datetime.strptime(leave_item['attendance_missing_to'], "%Y-%m-%d %H:%M:%S")
            if leave_item['attendance_missing_from']:
                leave_item['attendance_missing_from'] = datetime.strptime(leave_item['attendance_missing_from'], "%Y-%m-%d %H:%M:%S")
            if leave_item['request_date_from']:
                leave_item['request_date_from'] = datetime.strptime(leave_item['request_date_from'], "%Y-%m-%d")
            if leave_item['request_date_to']:
                leave_item['request_date_to'] = datetime.strptime(leave_item['request_date_to'], "%Y-%m-%d")
        except Exception as ex:
            print('process_leave_records: ', ex)
    scheduling_record['hr_leaves'] = leave_records


def process_explaination_records(explanation, scheduling_record):
    for explanation_item in explanation.explaination_records:
        try:
            if explanation_item['attendance_missing_to']:
                explanation_item['attendance_missing_to'] = datetime.strptime(explanation_item['attendance_missing_to'], "%Y-%m-%d %H:%M:%S")
            if explanation_item['attendance_missing_from']:
                explanation_item['attendance_missing_from'] = datetime.strptime(explanation_item['attendance_missing_from'], "%Y-%m-%d %H:%M:%S")
        except Exception as ex:
            print('process_explaination_records: ', ex)
    scheduling_record['list_explanations'] = explanation.explaination_records


def mergedTimeToScheduling(schedulings, shifts, employee, leave_records, explanation, profile):
    merged_shift = {shift.name.replace('/', '_'): shift for shift in shifts}

    for scheduling in schedulings:
        if scheduling['shift_name'].replace('/', '_') in merged_shift:
            shift = None
            if scheduling['shift_name'].replace('/', '_') in merged_shift:
                shift = merged_shift[scheduling['shift_name'].replace('/', '_')]
            scheduling['shift'] = shift
            date = datetime.strptime(scheduling['date'], "%Y-%m-%d")
            scheduling['shift_start_datetime'] = date.replace(
                hour=shift.start_work_time.hour, minute=shift.start_work_time.minute)
            scheduling['shift_end_datetime'] = date.replace(
                hour=shift.end_work_time.hour, minute=shift.end_work_time.minute)
            scheduling['rest_start_datetime'] = date.replace(
                hour=shift.start_rest_time.hour, minute=shift.start_rest_time.minute)
            scheduling['rest_end_datetime'] = date.replace(
                hour=shift.end_rest_time.hour, minute=shift.end_rest_time.minute)
            process_leave_records(leave_records, scheduling)
            scheduling['date'] = date
            process_explaination_records(explanation, scheduling)
            scheduling['list_add_item_out'] = []
            scheduling['list_early_out_leaves'] = get_list_early_out_leaves(scheduling)
            scheduling['list_late_in_leaves'] = get_list_late_in_leaves(scheduling)
            scheduling['main_contract'] = employee.main_contract
            scheduling['main_info'] = employee.info
            scheduling['stage1_worktime_temp'] = 0
            scheduling['stage2_worktime_temp'] = 0
            scheduling['late_in_time'] = 0
            scheduling['hue_stage1_end'] = None
            scheduling['hue_stage2_start'] = None
            scheduling['total_shift_worktime_calculate'] = 0
            scheduling['list_couple_after_explanation_private'] = []
            shift_name = scheduling['shift_name']
            rest_start_datetime = scheduling['rest_start_datetime']
            shift_start_datetime = scheduling['shift_start_datetime']
            shift_end_datetime = scheduling['shift_end_datetime']
            calculate_night_stage_fist_end(scheduling)
            calculate_night_stage_fist_start(scheduling)
            calculate_night_stage_last_start(scheduling)
            calculate_night_stage_last_end(scheduling)
            check_is_night_stage_fist(scheduling)
            check_is_night_stage_last(scheduling)
            check_is_holiday(scheduling)
            calculate_holiday_end_datetime(scheduling)
            calculate_holiday_start_datetime(scheduling)
            calculate_holiday_night_stage_fist_end_datetime(scheduling)
            calculate_holiday_night_stage_fist_start_datetime(scheduling)
            calculate_holiday_night_stage_last_start_datetime(scheduling)
            calculate_holiday_night_stage_last_end_datetime(scheduling)
            if shift_name:
                if '/' in shift_name and 'PH' in shift_name:
                    main_shift_start_datetime = shift_start_datetime
                    main_shift_end_datetime = shift_end_datetime
                    main_rest_start_datetime = rest_start_datetime
                    temp_worktime_cal = calculate_worktime_without_inout(main_shift_start_datetime, main_shift_end_datetime, scheduling)
                    scheduling['half_stage1_worktime_calculate'] = calculate_worktime_without_inout(main_shift_start_datetime, main_rest_start_datetime, scheduling)
                else:
                    temp_worktime_cal = calculate_worktime_without_inout(shift_start_datetime, shift_end_datetime, scheduling)
                    scheduling['half_stage1_worktime_calculate'] = calculate_worktime_without_inout(shift_start_datetime, rest_start_datetime, scheduling)

                if 370 <= temp_worktime_cal <= 375:
                    scheduling['total_shift_worktime_calculate'] = 371
                elif 441 <= temp_worktime_cal <= 443:
                    scheduling['total_shift_worktime_calculate'] = 442
                else:
                    scheduling['total_shift_worktime_calculate'] = round(temp_worktime_cal / 5) * 5
                if scheduling['main_contract']:
                    scheduling['is_probationary'] = not ('chính thức' in f"{scheduling['main_contract']['contract_type_id']}".lower())


def add_attempt_more_than_limit(listAttendanceTrans, scheduling_record, diffHoursWithNext, diffHoursWithPrev):
    attempt_with_inout_array = []
    attendanceAttemptArray = []
    if scheduling_record['shift_start_datetime']:
        additionTrans = []
        shift_start = scheduling_record['shift_start_datetime']
        shift_end = scheduling_record['shift_end_datetime']
        # Chuyển đổi tất cả thời gian sang định dạng datetime một lần
        for e in listAttendanceTrans:
            e['time_dt'] = datetime.strptime(e['time'], "%Y-%m-%d %H:%M:%S")
        listitemTrans = [
            e for e in listAttendanceTrans
            if shift_start - timedelta(hours=diffHoursWithPrev) < e['time_dt'] < shift_end + timedelta(hours=diffHoursWithNext)
        ]
        listitemTrans.sort(key=lambda e: e['time_dt'])

        if listitemTrans:
            if not listitemTrans[0]['in_out']:
                listitemTrans[0]['in_out'] = 'I'
            if not listitemTrans[-1]['in_out']:
                listitemTrans[-1]['in_out'] = 'O'

        for tran in listitemTrans:
            additem = AttendanceAttemptInOut(attempt=tran['time_dt'])
            additem.inout = InoutMode.In if tran['in_out'] in ['I', 'i'] else InoutMode.Out if tran['in_out'] in ['O', 'o'] else InoutMode.NoneMode
            additionTrans.append(additem)

        attempt_with_inout_array = list(set(additionTrans + attempt_with_inout_array))

        attendanceAttemptArray = list(set(
            [e['time_dt'] for e in listitemTrans if e['time_dt'] not in attendanceAttemptArray and e['time_dt'].replace(second=0) not in attendanceAttemptArray] + attendanceAttemptArray
        ))
        attempt_with_inout_array.sort(key=lambda a: a.attempt)
    scheduling_record['listitemTrans'] = listitemTrans
    scheduling_record['attempt_with_inout_array'] = attempt_with_inout_array
    scheduling_record['attendanceAttemptArray'] = attendanceAttemptArray
    scheduling_record["attendanceAttempt1"] = attendanceAttemptArray[0] if len(attendanceAttemptArray) > 0 else None
    return scheduling_record


def process_missing_attendance(scheduling_record):
    attempt_with_inout_array = scheduling_record['attempt_with_inout_array']
    attendanceAttemptArray = scheduling_record['attendanceAttemptArray']
    list_addItem_out = []
    hrLeaves = scheduling_record['hr_leaves']

    # Chuẩn hóa tên trạng thái ngày nghỉ
    for e in hrLeaves:
        e['holidayStatusName'] = e['holiday_status_id'][0] if e['holiday_status_id'][1] else ''

    # Lọc các phần tử có trạng thái thiếu chấm công
    listMissingLeaves = [
        element for element in hrLeaves
        if 'thiếu chấm công' in f"{element['holidayStatusName']}".lower()
    ]

    shiftStartDateTime = scheduling_record['shift_start_datetime']
    shiftEndDateTime = scheduling_record['shift_end_datetime']

    if shiftStartDateTime:
        additionTrans = []

        for leaveItem in listMissingLeaves:
            scheduling_record["missing_checkin_break"] = False

            def add_to_attempt_array(attendance_time, mode):
                if attendance_time not in attendanceAttemptArray:
                    attendanceAttemptArray.append(attendance_time)

                additem = AttendanceAttemptInOut(attempt=attendance_time)
                additem.inout = mode

                for in_out_addItem_before in [
                    item for item in list_addItem_out
                    if item.attempt <= additem.attempt
                ]:
                    in_out_addItem_before.inout = InoutMode.NoneMode

                additionTrans.append(additem)

            if 'chấm công ra' in f"{leaveItem['holidayStatusName']}".lower() and leaveItem.get('attendance_missing_to'):
                attendance_missing_to = leaveItem['attendance_missing_to']
                if attendance_missing_to.day in {shiftStartDateTime.day, shiftEndDateTime.day}:
                    if attendance_missing_to < shiftStartDateTime:
                        attendance_missing_to += timedelta(days=1)
                    add_to_attempt_array(attendance_missing_to, InoutMode.Out)

            if 'chấm công vào' in f"{leaveItem['holidayStatusName']}".lower() and leaveItem.get('attendance_missing_from'):
                attendanceMissingFrom = leaveItem['attendance_missing_from']
                if attendanceMissingFrom.day in {shiftStartDateTime.day, shiftEndDateTime.day}:
                    if attendanceMissingFrom < (shiftStartDateTime - timedelta(hours=3)):
                        attendanceMissingFrom += timedelta(days=1)
                    add_to_attempt_array(attendanceMissingFrom, InoutMode.In)

            if leaveItem.get('attendance_missing_to') and leaveItem.get('attendance_missing_from'):
                if {leaveItem['attendance_missing_from'].day, leaveItem['attendance_missing_to'].day} & {shiftStartDateTime.day, shiftEndDateTime.day}:
                    attendanceMissingTo = leaveItem['attendance_missing_to']
                    if attendanceMissingTo < (shiftStartDateTime - timedelta(hours=3)):
                        attendanceMissingTo += timedelta(days=1)
                    add_to_attempt_array(attendanceMissingTo, InoutMode.Out)

                    attendanceMissingFrom = leaveItem['attendance_missing_from']
                    if attendanceMissingFrom < shiftStartDateTime:
                        attendanceMissingFrom += timedelta(days=1)
                    add_to_attempt_array(attendanceMissingFrom, InoutMode.In)

        attempt_with_inout_array = list(set(additionTrans + attempt_with_inout_array))
        attempt_with_inout_array.sort(key=lambda a: a.attempt)
    scheduling_record['list_addItem_out'] = list_addItem_out
    attendanceAttemptArray.sort()
    return attempt_with_inout_array, attendanceAttemptArray


def find_attendance_hue4_time_mode(scheduling_record):
    attendanceAttemptArray = scheduling_record['attendanceAttemptArray']
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    shiftStartDateTime = scheduling_record['shift_start_datetime']
    shiftEndDateTime = scheduling_record['shift_end_datetime']
    attendanceAttemptArray.sort()

    beforeRestEndStartIndex = -1
    beforeRestEndEndIndex = -1
    afterRestStartStartIndex = -1
    afterRestStartEndIndex = -1
    HueStage1Start = None
    HueStage1End = None
    HueStage2Start = None
    HueStage2End = None
    stage1WorktimeTemp = None
    stage2WorktimeTemp = None

    if restStartDateTime and restEndDateTime:
        for index in range(len(attendanceAttemptArray)):
            if attendanceAttemptArray[index] <= restEndDateTime:
                if beforeRestEndStartIndex == -1:
                    beforeRestEndStartIndex = index
                if beforeRestEndEndIndex == -1 or (attendanceAttemptArray[index] - attendanceAttemptArray[beforeRestEndEndIndex]).total_seconds() > 1:
                    beforeRestEndEndIndex = index

            if attendanceAttemptArray[index] >= restStartDateTime:
                if afterRestStartStartIndex == -1:
                    afterRestStartStartIndex = index
                if afterRestStartEndIndex == -1 or (attendanceAttemptArray[index] - attendanceAttemptArray[afterRestStartEndIndex]).total_seconds() > 1:
                    afterRestStartEndIndex = index

        HueStage1Start = attendanceAttemptArray[beforeRestEndStartIndex] if beforeRestEndStartIndex > -1 else None
        HueStage2End = attendanceAttemptArray[afterRestStartEndIndex] if afterRestStartEndIndex > -1 else None

        if beforeRestEndEndIndex > afterRestStartStartIndex and afterRestStartStartIndex >= 0:
            HueStage1End = attendanceAttemptArray[afterRestStartStartIndex] if afterRestStartStartIndex > -1 else None
            HueStage2Start = attendanceAttemptArray[beforeRestEndEndIndex]
        elif beforeRestEndEndIndex < afterRestStartStartIndex and beforeRestEndEndIndex >= 0:
            HueStage1End = attendanceAttemptArray[beforeRestEndEndIndex] if beforeRestEndEndIndex > -1 else None
            HueStage2Start = attendanceAttemptArray[afterRestStartStartIndex]
        else:
            if beforeRestEndEndIndex >= 0 and HueStage1Start and HueStage2End:
                tempStart1End = next((e for e in reversed(attendanceAttemptArray) if e > HueStage1Start and e < attendanceAttemptArray[beforeRestEndEndIndex]), None)
                tempStart2Start = next((e for e in attendanceAttemptArray if e < HueStage2End and e > attendanceAttemptArray[beforeRestEndEndIndex]), None)

                stage1WorktimeTemp = calculate_night_worktime_custom(
                    scheduling_record,
                    HueStage1Start,
                    attendanceAttemptArray[beforeRestEndEndIndex],
                    shiftStartDateTime,
                    restStartDateTime,
                ) + (
                    calculate_night_worktime_custom(
                        scheduling_record,
                        tempStart2Start,
                        HueStage2End,
                        restEndDateTime,
                        shiftEndDateTime,
                    )
                    if tempStart2Start
                    else 0
                )
                stage2WorktimeTemp = (
                    calculate_night_worktime_custom(
                        scheduling_record,
                        HueStage1Start,
                        tempStart1End,
                        restEndDateTime,
                        shiftEndDateTime,
                    )
                    if tempStart1End
                    else 0
                ) + calculate_night_worktime_custom(
                    scheduling_record,
                    attendanceAttemptArray[beforeRestEndEndIndex],
                    HueStage2End,
                    restEndDateTime,
                    shiftEndDateTime,
                )

                if stage1WorktimeTemp > stage2WorktimeTemp:
                    HueStage1End = attendanceAttemptArray[beforeRestEndEndIndex]
                    HueStage2Start = tempStart2Start
                else:
                    HueStage1End = tempStart1End
                    HueStage2Start = attendanceAttemptArray[beforeRestEndEndIndex]

    if HueStage1End and HueStage1Start:
        if not HueStage1End > HueStage1Start:
            HueStage1End = None
    if HueStage2End and HueStage2Start:
        if not HueStage2End > HueStage2Start:
            HueStage2Start = None
    if HueStage1Start and HueStage1End and shiftStartDateTime and restStartDateTime:
        stage1WorktimeTemp = calculate_night_worktime_custom(scheduling_record, HueStage1Start, HueStage1End, shiftStartDateTime, restStartDateTime)
    else:
        stage1WorktimeTemp = 0
    if HueStage2Start and HueStage2End and shiftEndDateTime and restEndDateTime:
        stage2WorktimeTemp = calculate_night_worktime_custom(scheduling_record, HueStage2Start, HueStage2End, restEndDateTime, shiftEndDateTime)
    else:
        stage2WorktimeTemp = 0
    check_last_in_out(scheduling_record=scheduling_record)

    scheduling_record["HueStage1Start"] = HueStage1Start,
    scheduling_record["HueStage1End"] = HueStage1End,
    scheduling_record["HueStage2Start"] = HueStage2Start,
    scheduling_record["HueStage2End"] = HueStage2End,
    scheduling_record["stage1WorktimeTemp"] = stage1WorktimeTemp,
    scheduling_record["stage2WorktimeTemp"] = stage2WorktimeTemp


def process_worktime(scheduling_record):
    global totalWorkTime, nightWorkTime, holidayWorkTime, nightHolidayWorkTime
    global real_timein, real_timeout
    global stage1WorktimeTemp, stage2WorktimeTemp
    global selectOffStage, stage1Off, stage2Off, missing_checkin_break
    global totalShiftWorkTime_calculate, real_late_in_minute, real_ealry_out_minute
    global by_hue_shift
    attendanceAttempt1 = scheduling_record['attendanceAttempt1']
    attendanceAttemptArray = scheduling_record['attendanceAttemptArray']
    shift_name = scheduling_record['shift_name']
    shift = scheduling_record['shift']
    HueStage2Start = scheduling_record['HueStage2Start']
    HueStage1End = scheduling_record['HueStage1End']
    restStartDateTime = scheduling_record['rest_start_datetime']
    restEndDateTime = scheduling_record['rest_end_datetime']
    shiftStartDateTime = scheduling_record['shift_start_datetime']
    shiftEndDateTime = scheduling_record['shift_end_datetime']

    if attendanceAttempt1:
        find_attendance_hue4_time_mode(scheduling_record)
        real_timein = attendanceAttempt1
        real_timeout = attendanceAttemptArray[-1]

        for item in attendanceAttemptArray:
            if real_timein > item:
                real_timein = item
            if real_timeout < item:
                real_timeout = item

        if shift_name and shift:
            if '/OFF' not in shift_name and 'OFF/' not in shift_name:
                if by_hue_shift:
                    totalWorkTime = stage1WorktimeTemp + stage2WorktimeTemp
                    if HueStage1End and HueStage2Start:
                        pass
                    elif HueStage1End or HueStage2Start:
                        totalWorkTime = calculate_worktime_without_inout(real_timein, real_timeout, scheduling_record)
                        missing_checkin_break = True
                    else:
                        missing_checkin_break = True
                else:
                    totalWorkTime = calculate_worktime_without_inout(real_timein, real_timeout, scheduling_record)
            else:
                stage1Off = calculate_night_worktime_custom(scheduling_record, real_timein, real_timeout, shiftStartDateTime, restStartDateTime)
                stage1Off = min(stage1Off, 240)
                stage2Off = calculate_night_worktime_custom(scheduling_record, real_timein, real_timeout, restEndDateTime, shiftEndDateTime)
                stage2Off = min(stage2Off, 240)
                totalWorkTime = max(stage2Off, stage1Off)
                selectOffStage = 2 if stage2Off > stage1Off else 1

        if totalShiftWorkTime_calculate > 0:
            if real_timein and shiftStartDateTime:
                real_late_in_minute = calculate_worktime_without_inout(shiftStartDateTime, real_timein, scheduling_record)
            if real_timeout and shiftEndDateTime:
                real_ealry_out_minute = calculate_worktime_without_inout(real_timeout, shiftEndDateTime, scheduling_record)

        nightWorkTime = calculate_night_worktime_without_inout(real_timein, real_timeout, scheduling_record)
        holidayWorkTime = calculate_holiday_worktime_without_inout(real_timein, real_timeout, scheduling_record)
        nightHolidayWorkTime = calculate_night_holiday_without_inout(real_timein, real_timeout, scheduling_record)
    else:
        totalWorkTime = 0
        nightWorkTime = 0
        nightHolidayWorkTime = 0


def process_late_early_leave(scheduling_record):
    global kidModeStage1EndDatetime, kidModeStage2Datetime
    global totalWorkTime, lateinTime, earlyOutTime
    global maxLateEarly
    list_late_in_leaves = scheduling_record['list_late_in_leaves']
    _hrLeaves = scheduling_record['hr_leaves']
    shift = scheduling_record['shift']
    shift_name = scheduling_record['shift_name']
    kidmod = scheduling_record['kidmod']
    shiftStartDateTime = scheduling_record['shift_start_datetime']
    shiftEndDateTime = scheduling_record['shift_end_datetime']
    real_timeout = scheduling_record['real_timeout']
    real_timein = scheduling_record['real_timein']
    convert_overtime = scheduling_record['convert_overtime']
    employee_ho = scheduling_record['main_info']['employee_ho'] if 'employee_ho' in scheduling_record['main_info'] else False
    list_couple = scheduling_record['list_couple']
    lateIn_private = 0
    lateIn_by_work = 0
    lateIn_by_private_num = 0
    earlyOut_private = 0
    earlyOut_by_work = 0

    if real_timein and shiftStartDateTime:
        if convert_overtime:
            lateinTime = 0
            earlyOutTime = 0
        else:
            if employee_ho:
                if list_couple:
                    if kidmod == KidMode.SBEGIN30SEND30:
                        lateinTime = calculate_worktime_without_inout(kidModeStage1EndDatetime, list_couple[0].itemIn.attempt, scheduling_record)
                        earlyOutTime = calculate_worktime_without_inout(list_couple[-1].itemOut.attempt, kidModeStage2Datetime, scheduling_record)
                    elif kidmod == KidMode.SBEGIN60:
                        lateinTime = calculate_worktime_without_inout(kidModeStage1EndDatetime, list_couple[0].itemIn.attempt, scheduling_record)
                        earlyOutTime = calculate_worktime_without_inout(list_couple[-1].itemOut.attempt, shiftEndDateTime, scheduling_record)
                    elif kidmod == KidMode.SEND60:
                        earlyOutTime = calculate_worktime_without_inout(list_couple[-1].itemOut.attempt, kidModeStage2Datetime, scheduling_record)
                        lateinTime = calculate_worktime_without_inout(shiftStartDateTime, list_couple[0].itemIn.attempt, scheduling_record)
                    else:
                        lateinTime = calculate_worktime_without_inout(shiftStartDateTime, list_couple[0].itemIn.attempt, scheduling_record)
                        earlyOutTime = calculate_worktime_without_inout(list_couple[-1].itemOut.attempt, shiftEndDateTime, scheduling_record)
            else:
                if kidmod == KidMode.SBEGIN30SEND30:
                    lateinTime = calculate_worktime_without_inout(kidModeStage1EndDatetime, real_timein, scheduling_record)
                    earlyOutTime = calculate_worktime_without_inout(real_timeout, kidModeStage2Datetime, scheduling_record)
                elif kidmod == KidMode.SBEGIN60:
                    lateinTime = calculate_worktime_without_inout(kidModeStage1EndDatetime, real_timein)
                    earlyOutTime = calculate_worktime_without_inout(real_timeout, shiftEndDateTime, scheduling_record)
                elif kidmod == KidMode.SEND60:
                    earlyOutTime = calculate_worktime_without_inout(real_timeout, kidModeStage2Datetime, scheduling_record)
                    lateinTime = calculate_worktime_without_inout(shiftStartDateTime, real_timein, scheduling_record)
                else:
                    lateinTime = calculate_worktime_without_inout(shiftStartDateTime, real_timein, scheduling_record)
                    earlyOutTime = calculate_worktime_without_inout(real_timeout, shiftEndDateTime, scheduling_record)

        if shift_name and shift:
            if '/OFF' in shift_name or 'OFF/' in shift_name:
                if (lateinTime + totalWorkTime) >= 240:
                    earlyOutTime = 0 if earlyOutTime > lateinTime else earlyOutTime

                if (earlyOutTime + totalWorkTime) >= 240:
                    lateinTime = lateinTime if earlyOutTime > lateinTime else 0

                earlyOutTime = earlyOutTime - 240 if earlyOutTime > 240 else earlyOutTime
                lateinTime = lateinTime - 240 if lateinTime > 240 else lateinTime

        for leaveItem in list_late_in_leaves:
            if real_timein > shiftStartDateTime:
                if leaveItem['for_reasons'] == '1':
                    lateIn_private += min(maxLateEarly, max(leaveItem['minutes'], leaveItem['time_minute']))
                    lateIn_by_private_num += 1
                else:
                    lateIn_by_work += min(maxLateEarly, max(lateinTime, max(leaveItem['minutes'], leaveItem['time_minute'])))

        listEarlyOutLeave = [element for element in _hrLeaves if 'về sớm' in f"{element['holidayStatusName']}".lower() and 'đi muộn' not in f"{element['holidayStatusName']}".lower()]
        for leaveItem in listEarlyOutLeave:
            if real_timeout < shiftEndDateTime:
                if leaveItem['for_reasons'] == '1':
                    earlyOut_private += min(maxLateEarly, max(leaveItem['minutes'], leaveItem['time_minute']))
                else:
                    earlyOut_by_work += min(maxLateEarly, max(earlyOutTime, max(leaveItem['minutes'], leaveItem['time_minute'])))


def is_overtime_leave(leave, shift_start_datetime):
    c1 = True if leave.get('request_date_from') else False
    c2 = True if leave.get('request_date_to') else False
    c3 = leave['request_date_from'].day == shift_start_datetime.day
    c4 = leave['request_date_from'].month == shift_start_datetime.month
    c5 = 'tăng ca' in f"{leave['holiday_status_id']}".lower()
    return c1 and c2 and c3 and c4 and c5


def process_overtime_leave(scheduling_record):
    hr_leaves = scheduling_record['hr_leaves']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    is_probationary = not ('chính thức' in f"{scheduling_record['main_contract']['contract_type_id']}".lower())
    is_holiday = scheduling_record['is_holiday']
    holiday_start_datetime = scheduling_record['holiday_start_datetime']
    holiday_end_datetime = scheduling_record['holiday_end_datetime']
    shift_name = scheduling_record['shift_name']
    overtime_by_leave = 0
    overtime_holiday_by_leave = 0
    overtime_holiday_probationary_by_leave = 0
    overtime_probationary = 0
    overtime_minutes_by_leave = 0
    overtime_wage_by_leave = 0
    total_work_time = None
    convert_overtime = False
    total_increase_date = 0
    total_increase_probationary = 0

    if not shift_start_datetime:
        return

    list_overtime_leaves = list(filter(lambda leave: is_overtime_leave(leave, shift_start_datetime), hr_leaves))

    for leave_item in list_overtime_leaves:
        overtime_minutes_by_leave += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])
        overtime_wage_by_leave += leave_item['multiplied_wage_amount']

        if leave_item['convert_overtime']:
            scheduling_record['convert_overtime'] = leave_item['convert_overtime']
            if scheduling_record['convert_overtime']:
                scheduling_record['total_work_time'] = 0

        if 'phát sinh tăng' in leave_item['reasons'].lower():
            total_increase_date += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])
            if is_probationary:
                total_increase_probationary += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])
        else:
            overtime_by_leave += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])
            if is_holiday and holiday_start_datetime:
                overtime_holiday_by_leave += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])
            if is_probationary:
                overtime_probationary += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])
                if is_holiday and (calculate_worktime_without_inout(holiday_start_datetime, holiday_end_datetime, scheduling_record) > 0 or 'PH' in shift_name):
                    overtime_holiday_probationary_by_leave += max(leave_item['minutes'], leave_item['time_minute']) * max(0, leave_item['multiplier_work_time'])

    return overtime_by_leave, overtime_holiday_by_leave, overtime_holiday_probationary_by_leave, overtime_probationary, overtime_minutes_by_leave, overtime_wage_by_leave, total_work_time, convert_overtime, total_increase_date, total_increase_probationary


def is_increase_leave(leave, shift_start_datetime, shift_end_datetime):
    c1 = True if leave.get('request_date_from') else False
    c2 = True if leave.get('request_date_to') else False
    c3 = not leave['request_date_from'].replace(hour=0, minute=0, second=0) > shift_end_datetime
    c4 = not leave['request_date_to'].replace(hour=23, minute=59, second=59) < shift_start_datetime
    c5 = 'phát sinh tăng' in f"{leave['holiday_status_id']}".lower()
    return c1 and c2 and c3 and c4 and c5


def process_increase_leave(scheduling_record):
    hr_leaves = scheduling_record['hr_leaves']
    date = scheduling_record['date']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    total_shift_worktime_calculate = scheduling_record['total_shift_worktime_calculate']
    shift_name = scheduling_record['shift_name']
    minutes_per_day = scheduling_record['main_contract']['minutes_per_day'] if 'minutes_per_day' in scheduling_record['main_contract'] else False
    is_probationary = scheduling_record['is_probationary']
    total_increase_date = 0
    total_increase_probationary = 0

    if not date or not shift_end_datetime or not shift_start_datetime:
        list_increase_leaves = []
    else:
        list_increase_leaves = list(filter(lambda leave: is_increase_leave(leave, shift_start_datetime, shift_end_datetime), hr_leaves))

    for leave_item in list_increase_leaves:
        total_increase_date += min(
            total_shift_worktime_calculate,
            # total_shift_worktime_calculate == 0 and
            # shift_name not in ['OFF', 'UP', '-'] and
            # shift_name and
            # len(shift_name) > 1 and
            # '/' not in shift_name and
            # minutes_per_day or total_shift_worktime_calculate,
            max(leave_item['minutes'], leave_item['time_minute'])
        )
        if is_probationary:
            total_increase_probationary += max(leave_item['minutes'], leave_item['time_minute'])

    return total_increase_date, total_increase_probationary, shift_name, minutes_per_day


def is_paid_leave(leave, shift_start_datetime, shift_end_datetime):
    c1 = True if leave.get('request_date_from') else False
    c2 = True if leave.get('request_date_to') else False
    c3 = not leave['request_date_from'].replace(hour=0, minute=0, second=0) > shift_end_datetime
    c4 = not leave['request_date_to'].replace(hour=23, minute=59, second=59) < shift_start_datetime
    c5 = 'có tính lương' in f"{leave['holiday_status_id']}".lower()
    return c1 and c2 and c3 and c4 and c5


def process_leave_with_pay(scheduling_record):
    hr_leaves = scheduling_record['hr_leaves']
    date = scheduling_record['date']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    total_shift_worktime_calculate = scheduling_record['total_shift_worktime_calculate']
    shift_name = scheduling_record['shift_name']
    minutes_per_day = scheduling_record['main_contract']['minutes_per_day'] if 'minutes_per_day' in scheduling_record['main_contract'] else False
    total_ncl_date = 0
    total_ncl_hieu_hi_date = 0

    if not date or not shift_end_datetime or not shift_start_datetime:
        list_paided_leaves = []
    else:
        list_paided_leaves = list(filter(lambda leave: is_paid_leave(leave, shift_start_datetime, shift_end_datetime), hr_leaves))

    for leave_item in list_paided_leaves:
        total_ncl_date = min(
            total_shift_worktime_calculate,
            # total_shift_worktime_calculate == 0 and
            # shift_name not in ['OFF', 'UP', '-'] and
            # shift_name and
            # len(shift_name) > 1 and
            # '/' not in shift_name and
            # minutes_per_day or total_shift_worktime_calculate,
            total_ncl_date + max(leave_item['minutes'], leave_item['time_minute'])
        )

        if 'hiếu hỉ' in leave_item['holiday_status_name'].lower():
            total_ncl_hieu_hi_date = min(
                total_shift_worktime_calculate,
                # total_shift_worktime_calculate == 0 and
                # shift_name not in ['OFF', 'UP', '-'] and
                # shift_name and
                # len(shift_name) > 1 and
                # '/' not in shift_name and
                # minutes_per_day or total_shift_worktime_calculate,
                max(leave_item['minutes'], leave_item['time_minute']) - leave_item['used_minute']
            )

    return total_ncl_date, total_ncl_hieu_hi_date, minutes_per_day, shift_name


def process_annual_leave(scheduling_record):
    hr_leaves = scheduling_record['hr_leaves']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    scheduling_record['list_al_leaves'] = list(filter(lambda leave: check_leave_valid_type1('nghỉ phép năm', leave, shift_start_datetime, shift_end_datetime), hr_leaves))
    list_al_leaves = scheduling_record['list_al_leaves']
    total_al_date = 0
    number_al_date = 0

    for leave_item in list_al_leaves:
        total_al_date += max(leave_item['minutes'], leave_item['time_minute'])
        number_al_date += 1

    return total_al_date, number_al_date


def process_casual_leave(scheduling_record):
    is_probationary = scheduling_record['is_probationary']
    hr_leaves = scheduling_record['hr_leaves']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    scheduling_record['list_cl_leaves'] = list(filter(lambda leave: check_leave_valid_type1('nghỉ bù', leave, shift_start_datetime, shift_end_datetime), hr_leaves))
    list_cl_leaves = scheduling_record['list_cl_leaves']
    number_cl_date = 0
    total_cl_date = 0
    total_cl_probationary = 0

    for leave_item in list_cl_leaves:
        total_cl_date += max(leave_item['minutes'], leave_item['time_minute'])
        number_cl_date += 1
        if is_probationary:
            total_cl_probationary += max(leave_item['minutes'], leave_item['time_minute'])

    return total_cl_date, number_cl_date, total_cl_probationary


def process_worktime_ho(scheduling_record):
    rest_start_datetime = scheduling_record['rest_start_datetime']
    rest_end_datetime = scheduling_record['rest_end_datetime']
    # rest_start_datetime = scheduling_record['rest_start_datetime']
    list_couple_after_explanation_private = scheduling_record['list_couple_after_explanation_private']
    find_attendance_hue4_time_mode(scheduling_record)
    date = scheduling_record['date']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    list_explanations = scheduling_record['list_explanations']
    attempt_with_inout_array = scheduling_record['attempt_with_inout_array']
    hr_leaves = scheduling_record['hr_leaves']
    list_add_item_out = scheduling_record['list_add_item_out']
    list_late_in_leaves = scheduling_record['list_late_in_leaves']
    list_early_out_leaves = scheduling_record['list_early_out_leaves']
    # by_hue_shift = scheduling_record['main_contract']['by_hue_shift'] if 'by_hue_shift' in scheduling_record['main_contract'] else False
    # stage1_worktime_temp = scheduling_record['stage1_worktime_temp']
    # stage2_worktime_temp = scheduling_record['stage2_worktime_temp']
    # hue_stage1_end = scheduling_record['hue_stage1_end']
    # hue_stage2_start = scheduling_record['hue_stage2_start']
    # employee_ho = scheduling_record['main_info']['employee_ho'] if 'employee_ho' in scheduling_record['main_info'] else False
    # minutes_per_day = scheduling_record['main_contract']['minutes_per_day'] if 'minutes_per_day' in scheduling_record['main_contract'] else False
    # total_shift_worktime_calculate = scheduling_record['total_shift_worktime_calculate']
    # employee_code = scheduling_record.employee_code
    check_last_in_out(scheduling_record)

    if 'attendanceAttempt1' in scheduling_record:
        list_couple_before_explanation = find_in_out_couple(attempt_with_inout_array, scheduling_record)
        scheduling_record['list_couple_in_in_before_explanation'] = find_in_in_couple(attempt_with_inout_array, scheduling_record)
        scheduling_record['list_couple_out_in_before_explanation'] = get_list_couple_out_in(list_couple_before_explanation, scheduling_record)

    if date and shift_start_datetime and shift_end_datetime:
        for explaination_item in [e for e in list_explanations if e['reason'] == '2' and e['attendance_missing_from'] and e['attendance_missing_to'] and ((e['attendance_missing_from'].day == date.day and e['attendance_missing_from'].month == date.month) or (e['attendance_missing_to'].day == date.day and e['attendance_missing_to'].month == date.month))]:
            process_explanation_item_ho(scheduling_record, explaination_item)

    check_last_in_out(scheduling_record)
    list_workingout_leaves = [element for element in hr_leaves if check_leave_valid_type2('ra ngoài', element, date)]

    for leave_item in [element for element in list_workingout_leaves if element['for_reasons'] == '2']:
        process_leave_item_ho(leave_item, attempt_with_inout_array, shift_start_datetime, rest_start_datetime, shift_end_datetime, rest_end_datetime, list_add_item_out)

    for leave_item in [element for element in list_late_in_leaves if element['for_reasons'] == '2' and element['request_date_from'] and element['request_date_from'].day != shift_start_datetime.day]:
        leave_item['attendance_missing_from'] = shift_start_datetime
        leave_item['attendance_missing_to'] = shift_start_datetime + timedelta(minutes=leave_item.minutes)
        if rest_start_datetime and rest_end_datetime:
            if leave_item['attendance_missing_to'] > rest_start_datetime:
                leave_item['attendance_missing_to'] += rest_end_datetime - rest_start_datetime
        process_leave_item_ho(leave_item, attempt_with_inout_array, shift_start_datetime, rest_start_datetime, shift_end_datetime, rest_end_datetime, list_add_item_out)

    for leave_item in [element for element in list_early_out_leaves if element['for_reasons'] == '2' and element['request_date_from'] and element['request_date_from'].day != shift_start_datetime.day]:
        leave_item['attendance_missing_to'] = shift_end_datetime
        leave_item['attendance_missing_from'] = shift_end_datetime - timedelta(minutes=leave_item.minutes)
        if rest_start_datetime and rest_end_datetime:
            if leave_item['attendance_missing_from'] < rest_end_datetime:
                leave_item['attendance_missing_from'] += rest_start_datetime - rest_end_datetime
        process_leave_item_ho(leave_item, attempt_with_inout_array, shift_start_datetime, rest_start_datetime, shift_end_datetime, rest_end_datetime, list_add_item_out)

    check_last_in_out(scheduling_record)
    if 'attendanceAttempt1' in scheduling_record:
        list_couple_before_explanation_private = find_in_out_couple(attempt_with_inout_array, scheduling_record)
        scheduling_record['list_couple_out_in_before_explanation_private'] = get_list_couple_out_in(list_couple_before_explanation_private, scheduling_record)
        scheduling_record['list_couple_before_explanation_private'] = list_couple_before_explanation_private
        keys_to_check = [scheduling_record['shift_start_datetime']]
        keys_to_check.append(scheduling_record['rest_start_datetime'])
        keys_to_check.append(scheduling_record['shift_start_datetime'])
        keys_to_check.append(scheduling_record['shift_start_datetime'])
        for inout_couple in list_couple_before_explanation_private:
            inout_couple.typeio = 'IO'
        for inout_couple in scheduling_record['list_couple_out_in_before_explanation_private']:
            inout_couple.typeio = 'OI'
        scheduling_record['merge_couples_before_private'] = merge_and_split_couples(list_couple_before_explanation_private, scheduling_record['list_couple_out_in_before_explanation_private'], keys_to_check)
        if list_couple_before_explanation_private:
            real_timein_couple = next((element for element in list_couple_before_explanation_private if element.itemOut.attempt > shift_start_datetime), None)
            real_timein = real_timein_couple.itemIn.attempt if real_timein_couple else None

            real_timeout_couple = next((element for element in reversed(list_couple_before_explanation_private) if element.itemIn.attempt < shift_end_datetime), None)
            real_timeout = real_timein
            if real_timeout_couple:
                real_timeout = real_timein if real_timein_couple is None else real_timeout_couple.itemOut.attempt
            scheduling_record['real_timein'] = real_timein
            scheduling_record['real_timeout'] = real_timeout
    check_last_in_out(scheduling_record)
    for explaination_item in [e for e in list_explanations if e['reason'] == '1' and e['attendance_missing_from'] and e['attendance_missing_to']]:
        process_explanation_item_ho(scheduling_record, explaination_item)

    if 'attendanceAttempt1' in scheduling_record:
        list_couple_after_explanation_private = find_in_out_couple(attempt_with_inout_array, scheduling_record)
        scheduling_record['list_couple_out_in_after_explanation_private'] = get_list_couple_out_in(list_couple_after_explanation_private, scheduling_record)
        scheduling_record['list_couple_after_explanation_private'] = list_couple_after_explanation_private

    for leave_item in [element for element in list_workingout_leaves if element['for_reasons'] == '1' and element['attendance_missing_from'] and element['attendance_missing_to']]:
        process_leave_item_ho(scheduling_record, leave_item)

    scheduling_record['list_couple'] = find_in_out_couple(attempt_with_inout_array, scheduling_record)
    scheduling_record['list_couple_out_in'] = get_list_couple_out_in(scheduling_record['list_couple'], scheduling_record)


def is_business_leave(leave, shift_end_datetime, shift_start_datetime):
    c1 = True if leave.get('request_date_from') else False
    c2 = True if leave.get('request_date_to') else False
    c3 = not leave['request_date_from'].replace(hour=0, minute=0, second=0) > shift_end_datetime
    c4 = not leave['request_date_to'].replace(hour=23, minute=59, second=59) < shift_start_datetime
    c5 = 'công tác' in f"{leave['holiday_status_id']}".lower()
    return c1 and c2 and c3 and c4 and c5


def process_business_leave(scheduling_record):
    # is_probationary = scheduling_record['is_probationary']
    hr_leaves = scheduling_record['hr_leaves']
    shift_name = scheduling_record['shift_name']
    shift_start_datetime = scheduling_record['shift_start_datetime']
    shift_end_datetime = scheduling_record['shift_end_datetime']
    scheduling_record['list_business_leaves'] = list(filter(lambda leave: check_leave_valid_type1('công tác', leave, shift_start_datetime, shift_end_datetime), hr_leaves))
    list_business_leaves = scheduling_record['list_business_leaves']
    total_shift_worktime_calculate = scheduling_record['total_shift_worktime_calculate']
    minutes_per_day = scheduling_record['main_contract']['minutes_per_day'] if 'minutes_per_day' in scheduling_record['main_contract'] else False
    late_in_time = scheduling_record['late_in_time']
    time_business_trip = 0

    for leave_item in list_business_leaves:
        time_business_trip = min((
            total_shift_worktime_calculate == 0 and shift_name not in ['OFF', 'UP', '-'] and shift_name and len(shift_name) > 1 and '/' not in shift_name and minutes_per_day or total_shift_worktime_calculate),
            time_business_trip + max(leave_item['minutes'], leave_item['time_minute']))

        if time_business_trip > late_in_time and time_business_trip > 0:
            late_in_time = 0

    return time_business_trip, late_in_time


def process_child_mode(scheduling_record, select_off_stage, kidmod, kidmode_worktime_without_inout, kidmod_early_out_mid, kidmod_late_in_mid):
    attendance_attempt1 = scheduling_record['attendanceAttempt1']
    kidmod_work_time = 0
    real_time_out = scheduling_record['real_timeout']
    real_time_in = scheduling_record['real_timein']
    late_in_mid = scheduling_record['late_in_mid']
    early_out_mid = scheduling_record['early_out_mid']
    employee_ho = scheduling_record['main_info']['employee_ho'] if 'employee_ho' in scheduling_record['main_info'] else False
    list_couple = scheduling_record['list_couple']
    out_by_private_attendance = scheduling_record['out_by_private_attendance']
    out_by_work_attendance = scheduling_record['out_by_work_attendance']
    if attendance_attempt1 and real_time_in and real_time_out:
        if employee_ho:
            kidmod_work_time = 0
            for couple in list_couple:
                kidmode_tuple = kidmode_worktime_without_inout(couple.itemIn.attempt, couple.itemOut.attempt)
                kidmod_work_time += kidmode_tuple[0]
        else:
            kidmode_tuple = kidmode_worktime_without_inout(real_time_in, real_time_out)
            kidmod_work_time = kidmode_tuple[0]
            if out_by_private_attendance == 0 and out_by_work_attendance == 0:
                early_out_mid = kidmod_early_out_mid()
                late_in_mid = kidmod_late_in_mid()

        if select_off_stage == 2:
            if kidmod in [KidMode.RBegin30REnd30, KidMode.SBegin30SEnd30]:
                pass

    return kidmod_work_time, late_in_mid, early_out_mid


def process_explanation(
    list_explanations,
    scheduling_record,
    employee_ho,
    list_couple_before_explanation_private,
    real_time_in,
    real_time_out,
    kidmod,
    kid_mode_stage1_datetime,
    kid_mode_stage1_end_datetime,
    kid_mode_stage2_datetime,
    kid_mode_stage2_end_datetime,
    early_out_mid,
    late_in_mid,
):
    out_by_private = scheduling_record['out_by_private']
    out_by_private_attendance = scheduling_record['out_by_private_attendance']
    out_by_work = scheduling_record['out_by_work']
    listexplainations_private = [element for element in list_explanations if element['reason'] == '1']

    for explaination_item in [element for element in listexplainations_private if element['attendance_missing_from'] and element['attendance_missing_to']]:
        if employee_ho:
            in_time_leave = 0
            for couple in list_couple_before_explanation_private:
                in_time_leave += calculate_night_worktime_custom(
                    scheduling_record,
                    couple.itemIn.attempt,
                    couple.itemOut.attempt,
                    explaination_item['attendance_missing_from'],
                    explaination_item['attendance_missing_to']
                )
            out_time = calculate_worktime_without_inout(
                explaination_item['attendance_missing_from'],
                explaination_item['attendance_missing_to'],
                scheduling_record
            ) - in_time_leave
            out_by_private += out_time
        else:
            out_time = calculate_worktime_without_inout(
                explaination_item['attendance_missing_from'],
                explaination_item['attendance_missing_to'],
                scheduling_record
            )
            out_by_private += out_time
            if real_time_in and real_time_out:
                if kidmod == 'None':
                    out_by_private_attendance += calculate_night_worktime_custom(
                        scheduling_record,
                        real_time_in,
                        real_time_out,
                        explaination_item['attendance_missing_from'],
                        explaination_item['attendance_missing_to']
                    )
                elif kid_mode_stage1_datetime and kid_mode_stage1_end_datetime and kid_mode_stage2_datetime and kid_mode_stage2_end_datetime:
                    if early_out_mid + late_in_mid == 0:
                        out_by_private_attendance = max(
                            0,
                            calculate_night_worktime_custom(
                                scheduling_record,
                                real_time_in,
                                real_time_out,
                                explaination_item['attendance_missing_from'],
                                explaination_item['attendance_missing_to']
                            ) - calculate_night_worktime_custom(
                                scheduling_record,
                                kid_mode_stage1_datetime,
                                kid_mode_stage1_end_datetime,
                                explaination_item['attendance_missing_from'],
                                explaination_item['attendance_missing_to']
                            ) - calculate_night_worktime_custom(
                                scheduling_record,
                                kid_mode_stage2_datetime,
                                kid_mode_stage2_end_datetime,
                                explaination_item['attendance_missing_from'],
                                explaination_item['attendance_missing_to']
                            )
                        )

    listexplainations_work = [element for element in list_explanations if element['reason'] == '2']

    for explaination_item in [element for element in listexplainations_work if element['attendance_missing_from'] and element['attendance_missing_to']]:
        in_time_leave = 0
        for couple in list_couple_before_explanation_private:
            in_time_leave += calculate_night_worktime_custom(
                scheduling_record,
                couple.itemIn.attempt,
                couple.itemOut.attempt,
                explaination_item['attendance_missing_from'],
                explaination_item['attendance_missing_to']
            )
        out_time = max(0, calculate_worktime_without_inout(
            explaination_item['attendance_missing_from'],
            explaination_item['attendance_missing_to'],
            scheduling_record
        ) - in_time_leave)
        out_by_work += out_time
    return out_by_work


def process_working_out_leave(hr_leaves, scheduling_record, date, real_time_in, real_time_out, kidmod, early_out_mid, late_in_mid, kid_mode_stage1_datetime, kid_mode_stage1_end_datetime, kid_mode_stage2_datetime, kid_mode_stage2_end_datetime, calculate_worktime_without_inout):
    out_by_work_attendance = scheduling_record['out_by_work_attendance']
    out_by_work = scheduling_record['out_by_work']
    out_by_private_attendance = scheduling_record['out_by_private_attendance']
    out_by_private = scheduling_record['out_by_private']
    list_workingout_leaves = [
        element for element in hr_leaves
        if (
            element['attendance_missing_from'] and element['attendance_missing_to'] and (
                (
                    element['attendance_missing_from'].day == date.day and element['attendance_missing_from'].month == date.month
                ) or (
                    element['attendance_missing_to'].day == date.day and element['attendance_missing_to'].month == date.month
                )
            ) and 'ra ngoài' in element['holiday_status_name'].lower())
    ]

    for leave_item in list_workingout_leaves:
        out_time = calculate_worktime_without_inout(
            leave_item['attendance_missing_from'],
            leave_item['attendance_missing_to'],
            scheduling_record
        )
        if leave_item['for_reasons'] == '1':
            out_by_private += out_time
            if real_time_in and real_time_out:
                if kidmod == 'None':
                    out_by_private_attendance += calculate_night_worktime_custom(
                        scheduling_record,
                        real_time_in,
                        real_time_out,
                        leave_item['attendance_missing_from'],
                        leave_item['attendance_missing_to']
                    )
                elif early_out_mid + late_in_mid == 0:
                    out_by_private_attendance = max(
                        0,
                        calculate_night_worktime_custom(
                            scheduling_record,
                            real_time_in,
                            real_time_out,
                            leave_item['attendance_missing_from'],
                            leave_item['attendance_missing_to']
                        ) - calculate_night_worktime_custom(
                            scheduling_record,
                            kid_mode_stage1_datetime,
                            kid_mode_stage1_end_datetime,
                            leave_item['attendance_missing_from'],
                            leave_item['attendance_missing_to']
                        ) - calculate_night_worktime_custom(
                            scheduling_record,
                            kid_mode_stage2_datetime,
                            kid_mode_stage2_end_datetime,
                            leave_item['attendance_missing_from'],
                            leave_item['attendance_missing_to']
                        )
                    )
        elif leave_item['for_reasons'] == '2':
            out_by_work += out_time
            if real_time_in and real_time_out and kidmod != 'None':
                out_by_work_attendance += calculate_night_worktime_custom(
                    scheduling_record,
                    real_time_in,
                    real_time_out,
                    leave_item['attendance_missing_from'],
                    leave_item['attendance_missing_to']
                )


def process_working_out_leave_ho(hr_leaves, scheduling_record, date, list_couple_before_explanation_private, calculate_worktime_without_inout, process_explanation):
    out_by_private = scheduling_record['out_by_private']
    out_by_work = scheduling_record['out_by_work']
    list_workingout_leaves = [
        element for element in hr_leaves
        if (
            element['attendance_missing_from'] and element['attendance_missing_to'] and (
                (
                    element['attendance_missing_from'].day == date.day and element['attendance_missing_from'].month == date.month
                ) or (
                    element['attendance_missing_to'].day == date.day and element['attendance_missing_to'].month == date.month
                )
            ) and 'ra ngoài' in element['holiday_status_name'].lower())
    ]

    for leave_item in list_workingout_leaves:
        in_time_leave = sum([
            calculate_night_worktime_custom(
                scheduling_record,
                couple.itemIn.attempt,
                couple.itemOut.attempt,
                leave_item['attendance_missing_from'],
                leave_item['attendance_missing_to']
            ) for couple in list_couple_before_explanation_private
        ])
        out_time = max(0, calculate_worktime_without_inout(
            leave_item['attendance_missing_from'],
            leave_item['attendance_missing_to'],
            scheduling_record
        ) - in_time_leave)
        if leave_item['for_reasons'] == '1':
            out_by_private += out_time
        elif leave_item['for_reasons'] == '2':
            out_by_work += out_time

    process_explanation()


def process_cl_by_shiftname(shift_name, number_cl_date, number_al_date):
    cl_used_by_clshiftname = 0
    if shift_name == 'CL' and number_cl_date == 0 and number_al_date == 0:
        cl_used_by_clshiftname = 480
    return cl_used_by_clshiftname


def process_al_by_shiftname(shift_name, number_cl_date, number_al_date):
    al_used_by_alshift = 0
    if shift_name == 'AL' and number_cl_date == 0 and number_al_date == 0:
        al_used_by_alshift = 480
    return al_used_by_alshift


def process_personal_holiday(is_holiday, calculate_worktime_without_inout, holiday_start_datetime, holiday_end_datetime, shift_name, shift, minutes_per_day, holiday_work_time_final, employee_ho, total_work_time_final):
    ph_date = 0.0
    half_ph_worktime_part = 0

    if is_holiday and (calculate_worktime_without_inout(holiday_start_datetime, holiday_end_datetime) > 0 or 'PH' in shift_name) and shift:
        if shift_name.startswith('PH') and '/' not in shift_name:
            ph_date = 480 / minutes_per_day if shift_name == 'PHG' else 1.0
        elif '/PH480' in shift_name or 'PH480/' in shift_name:
            half_ph_leave = max(0.5, max(0, (480 - holiday_work_time_final)) / 480)
            half_ph_worktime_part = round((1 - half_ph_leave) * 480)
            ph_date = min(1, half_ph_leave)
        elif '/PH530' in shift_name or 'PH530/' in shift_name:
            half_ph_leave = max(0.5, max(0, (530 - holiday_work_time_final)) / 530)
            half_ph_worktime_part = round((1 - half_ph_leave) * 480)
            ph_date = min(1, half_ph_leave)
        elif '/PH' in shift_name or 'PH/' in shift_name:
            half_ph_leave = max(
                0.5,
                max(0, ((minutes_per_day if employee_ho else 480) - holiday_work_time_final)) / (minutes_per_day if employee_ho else 480)
            )
            half_ph_worktime_part = round((1 - half_ph_leave) * (minutes_per_day if employee_ho else 480))
            ph_date = min(1, half_ph_leave)
        elif employee_ho and total_work_time_final > 0:
            ph_date = min(1, max(0, 1 - total_work_time_final / minutes_per_day))

    return ph_date, half_ph_worktime_part


def process_off_shift(shift, shift_name):
    total_off = 0.0
    if shift:
        if shift_name == 'OFF':
            total_off = 1.0
        elif '/OFF' in shift_name or 'OFF/' in shift_name:
            total_off = 0.5
    return total_off


def process_up_shift(shift, shift_name, list_up_leaves, max_late_early, employee_ho, minutes_per_day):
    total_up = 0.0
    up_by_leave = 0

    if shift:
        if not list_up_leaves:
            if shift_name == 'UP':
                total_up = 1.0
            elif '/UP' in shift_name or 'UP/' in shift_name:
                total_up = 0.5
        else:
            for leave_item in list_up_leaves:
                uptime = min(max_late_early, max(leave_item['minutes'], leave_item['time_minute']))
                if uptime > 0:
                    up_by_leave = int(uptime)
                    absent_morning = leave_item['absent_morning']
                    absent_afternoon = leave_item['absent_afternoon']
            total_up = up_by_leave / (minutes_per_day if employee_ho else 480)

    return total_up, up_by_leave, absent_morning, absent_afternoon


def calculate_worktime_with_inout_standard(scheduling_record):
    process_missing_attendance(scheduling_record)
    process_worktime_ho(scheduling_record)
    # process_overtime_leave(scheduling_record)
    # process_late_early_leave(scheduling_record)
    # process_increase_leave(scheduling_record)
    # process_leave_with_pay(scheduling_record)
    # process_annual_leave(scheduling_record)
    # process_casual_leave(scheduling_record)
    # process_business_leave(scheduling_record)
    # process_child_mode(scheduling_record)
    # process_working_out_leave_ho(scheduling_record)
    # process_cl_by_shiftname(scheduling_record)
    # process_al_by_shiftname(scheduling_record)
    # process_personal_holiday(scheduling_record)
    # process_off_shift(scheduling_record)
    # process_up_shift(scheduling_record)


def collect_data_to_schedulings(scheduling_object):
    scheduling_object['scheduling_records'] = scheduling_object.scheduling_records
