import json

from .datatypes import ServiceNow


class ServiceNowTicket(ServiceNow):
    active = None
    activity_due = None
    additional_assignee_list = None
    approval = None
    approval_history = None
    approval_set = None
    assigned_to = None
    assignment_group = None
    business_duration = None
    business_service = None
    business_stc = None
    calendar_duration = None
    calendar_stc = None
    caller_id = None
    category = None
    caused_by = None
    child_incidents = None
    close_code = None
    close_notes = None
    closed_at = None
    closed_by = None
    cmdb_ci = None
    comments = None
    comments_and_work_notes = None
    company = None
    contact_type = None
    correlation_display = None
    correlation_id = None
    delivery_plan = None
    delivery_task = None
    description = None
    due_date = None
    escalation = None
    expected_start = None
    follow_up = None
    group_list = None
    impact = None
    incident_state = None
    knowledge = None
    location = None
    made_sla = None
    notify = None
    number = None
    opened_at = None
    opened_by = None
    order = None
    parent = None
    parent_incident = None
    priority = None
    problem_id = None
    reassignment_count = None
    rejection_goto = None
    reopen_count = None
    resolved_at = None
    resolved_by = None
    rfc = None
    severity = None
    short_description = None
    sla_due = None
    state = None
    subcategory = None
    sys_class_name = None
    sys_created_by = None
    sys_created_on = None
    sys_domain = None
    sys_domain_path = None
    sys_id = None
    sys_mod_count = None
    sys_tags = None
    sys_updated_by = None
    sys_updated_on = None
    time_worked = None
    upon_approval = None
    upon_reject = None
    urgency = None
    user_input = None
    watch_list = None
    wf_activity = None
    work_end = None
    work_notes = None
    work_notes_list = None
    work_start = None

    @property
    def number(self):
        return self.sys_id

    def add_property(self, key, value):
        return self.__dict__.update({key: value})

    def to_api(self):
        d = self.to_dict()
        d['number'] = self.number
        return json.dumps(d)
