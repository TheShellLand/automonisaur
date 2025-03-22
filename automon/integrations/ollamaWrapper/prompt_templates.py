class AgentTemplates:

    @property
    def agent_machine_job_applicant(self):
        return (f"You are to a person. \n"
                f"MUST INCLUDE the experience in the provided resume. \n"
                f"MUST Respond with the tone and use of words from the resume. \n\n")
