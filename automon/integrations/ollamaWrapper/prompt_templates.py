class AgentTemplates:

    @property
    def agent_machine_job_applicant(self):
        return (f"You are to a person. "
                f"Assume the experience in the provided resume. "
                f"Respond with the tone and use of words from the resume. \n\n")
