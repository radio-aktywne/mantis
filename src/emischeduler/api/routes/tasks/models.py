from uuid import UUID

from pyscheduler.models import transfer as t

GetIndexResponse = t.TaskIndex

GetTaskIdParameter = UUID
GetTaskResponse = t.GenericTask

GetPendingTaskIdParameter = UUID
GetPendingTaskResponse = t.PendingTask

GetRunningTaskIdParameter = UUID
GetRunningTaskResponse = t.RunningTask

GetCancelledTaskIdParameter = UUID
GetCancelledTaskResponse = t.CancelledTask

GetFailedTaskIdParameter = UUID
GetFailedTaskResponse = t.FailedTask

GetCompletedTaskIdParameter = UUID
GetCompletedTaskResponse = t.CompletedTask

ScheduleTaskRequest = t.ScheduleRequest
ScheduleTaskResponse = t.PendingTask

CancelTaskIdParameter = UUID
CancelTaskResponse = t.CancelledTask

CleanTasksRequest = t.CleanRequest
CleanTasksResponse = t.CleaningResult
