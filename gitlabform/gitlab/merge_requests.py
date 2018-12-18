import json

from gitlabform.gitlab.core import GitLabCore


class GitLabMergeRequests(GitLabCore):

    def create_mr(self, project_and_group_name, source_branch, target_branch, title, description=None):
        data = {
            "id": project_and_group_name,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
        }
        return self._make_requests_to_api("projects/%s/merge_requests", project_and_group_name,
                                          method='POST', data=data, expected_codes=201)

    def accept_mr(self, project_and_group_name, mr_iid):
        return self._make_requests_to_api("projects/%s/merge_requests/%s/merge", (project_and_group_name, mr_iid),
                                          method='PUT')

    def update_mr(self, project_and_group_name, mr_iid, data):
        self._make_requests_to_api("projects/%s/merge_requests/%s", (project_and_group_name, mr_iid),
                                   method='PUT', data=data)

    def get_mrs(self, project_and_group_name):
        """
        :param project_and_group_name: like 'group/project'
        :return: get all *open* MRs in given project
        """
        return self._make_requests_to_api("projects/%s/merge_requests?scope=all&state=opened",
                                          project_and_group_name, paginated=True)

    def get_mr(self, project_and_group_name, mr_iid):
        return self._make_requests_to_api("projects/%s/merge_requests/%s", (project_and_group_name, mr_iid))

    def get_mr_approvals(self, project_and_group_name, mr_iid):
        return self._make_requests_to_api("projects/%s/merge_requests/%s/approvals", (project_and_group_name, mr_iid))

    def set_mr_approvers(self, project_and_group_name, mr_iid, approvers, approver_groups):

        # gitlab API expects ids, not names of users and groups, so we need to convert first
        approver_ids = []
        for approver_name in approvers:
            approver_ids.append(self._get_user_id(approver_name))
        approver_group_ids = []
        for group_path in approver_groups:
            approver_group_ids.append(self._get_group_id(group_path))

        # we need to pass data to this gitlab API endpoint as JSON, because when passing as data the JSON converter
        # used by requests lib changes empty arrays into nulls and omits it, which results in
        # {"error":"approver_group_ids is missing"} error from gitlab...
        # TODO: create JSON object directly, omit converting string to JSON
        # for this endpoint GitLab still actually wants pid, not "group/project"...
        pid = self._get_project_id(project_and_group_name)
        data = "{" \
               + '"id":' + str(pid) + ',' \
               + '"merge_request_iid":' + str(mr_iid) + ',' \
               + '"approver_ids": [' + ','.join(str(x) for x in approver_ids) + '],' \
               + '"approver_group_ids": [' + ','.join(str(x) for x in approver_group_ids) + ']' \
               + "}"
        json_data = json.loads(data)

        # for unknown reason code 400
        # & response body: 'b'{"error":"approver_group_ids is missing, approver_group_ids is invalid"}''
        # ..still means that the approvers have been changed!
        return self._make_requests_to_api("projects/%s/merge_requests/%s/approvers", (project_and_group_name, mr_iid),
                                          method='PUT', data=json_data, expected_codes=[200, 400])
