from prompt_toolkit.input.vt100 import raw_mode

from automon import Markdown


class Utils:
    pass


class AgentRole:
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'
    TOOL = 'tool'


class AgentTasks:
    @staticmethod
    def email_response():
        raw_template = f"""
        # WRITING EMAIL RULES
        
        - Respond with no more than two to three short sentences for the entire email body for the initial reply.
        - Behave as a real human person in a conversational thread replying to emails.
        - Your task is to read the email chain and write a response.
        - Only return the body of the email.
        - answer all questions asked relevant to what you know.
        - Do not use markdown formatting.
        - Do not use markdown code blocks.
        - Do not include a subject line, greetings, acknowledgments, apologies, justifications, or any other extraneous text in the email response.
        - craft a response that mimics a natural conversation.
        - don't acknowledge the rule, just respond to the email.
        - Refactor the email body to remove extraneous content.
        - Eliminate the subject line from the response.
        - Remove any greetings or acknowledgments.
        - Ensure no apologies or justifications are present in the email.
        - When presenting code, text blocks, or any structured information, present the content directly without surrounding markers or prefixes.
        - The response must also be refactored to remove extraneous conversational text such as "Let me know what time works best for a discussion."
        - Remove any conversational closing statements such as "I look forward to connecting and discussing how my skills in cloud technologies and security can benefit your firm," as these are considered extraneous conversational text.
        """

        return Markdown.lstrip(raw_template)


class AgentTemplates:
    tasks = AgentTasks()

    @staticmethod
    def job_applicant() -> str:
        raw_template = f"""
        # Job applicant rules
        
        - You are applying to a job.
        - Answer all questions asked.
        - Strictly use the `RESUME` as your complete knowledge, skills, and work experience.
        - For inquiries about availability or scheduling, provide the 'AVAILABILITY' from the resume.
        - Use the provided 'AVAILABILITY' to book a convenient time.
        """
        return Markdown.lstrip(raw_template)

    @staticmethod
    def your_identity(
            name: str,
            memory: str,
    ) -> str:
        raw_template = f"""
        # IDENTITY
        
        - You will assume the identity of `NAME`.
        - You will only use the `MEMORY` as your only source of knowledge.
        - You will refer to yourself in first person. 
        - You will ask question and respond in the style, word choice, and behavior of your `BACKGROUND`.
        - Respond with the tone, theme, and use of words from your `MEMORY`.
        
        ### NAME
        
        - You are to assume the identity of `{name}`.`
        
        ### MEMORY
        
        ```text
        {memory}
        ```
        """
        return Markdown.lstrip(raw_template)

    @staticmethod
    def compact_prompt() -> str:
        raw_template = f"""
        - Act as a prompt engineer.
        - Compress the text provided in the PROMPT section to use the absolute minimum number of tokens while preserving 100% of its original meaning, constraints, and intent.
        - Remove fluff, use concise language, and utilize formatting like Markdown or symbols if it saves space.
        """

        return Markdown.lstrip(raw_template)

    @staticmethod
    def use_template_chatbot_with_thinking() -> str:
        raw_template = f"""
        - You are a chat bot talking to a person.
        - You will only answer using information provided.
        - You must provide an answer.
        - You will always give concise and direct answers.
        """
        return Markdown.lstrip(raw_template)

    @staticmethod
    def use_template_chatbot_with_input(input: str, question: str) -> str:
        raw_template = f"""
        # SYSTEM RULES
        
        - You are a highly articulate and helpful chat bot. 
        - Your task is to answer `QUESTION` using the provided `DATA`.
        
        ### INSTRUCTIONS
        
        - Always give a truthful and honest answers.
        - You are allowed to ask a follow up question if it will help clarify the <INPUT> section.
        - For everything else, please explicitly mention these notes. 
        - Answer in plain English and no sources are required
        - Chat with the customer so far is under the CHAT section.
        
        ---
        
        # QUESTION
        
        {question}
        
        ---
        
        # DATA
        
        ```text
        {input}
        ```
        """

        return Markdown.lstrip(raw_template)

    @staticmethod
    def use_template_chatbot_with_multi_input(input: [dict], question: str) -> str:
        INPUTS = []
        for input_ in input:
            tag = input_['tag']
            text = input_['text']

            INPUTS.append(f"<{tag}>\n{text}\n</{tag}>")

        INPUTS = '\n'.join(INPUTS)

        raw_template = f"""
        # SYSTEM RULES
        
        - You are a highly articulate and helpful chat bot. 
        - Your task is to answer questions using data provided in `QUESTION`.
        - Use the information in `DATA`.
            
        ---
        
        ### INSTRUCTIONS
        
        - Always give a truthful and honest answers.
        - You are allowed to ask a follow up question if it will help clarify the <INPUT> section.
        - For everything else, please explicitly mention these notes. 
        - Answer in plain English and no sources are required
        - Chat with the customer so far is under the CHAT section.
        
        ---
        
        # QUESTION
        
        {question}
        
        ---
        
        # INPUT
        
        {INPUTS}
        """

        return Markdown.lstrip(raw_template)


class TrueOrFalseTemplates:

    @staticmethod
    def email_is_human(email: str) -> str:
        raw_template = f"""
        # QUESTION
        
        Analyze the `EMAIL` below. Respond with exactly one word: "True" or "False".
        
        Is the first email from a human? Respond "True" if it is from a real person. Respond "False" if it is an automated message, automated notification, bounce message, or bot.
        
        Do not include any punctuation, explanations, or other text.
        
        ---
        
        # EMAIL
        
        {email}
        """
        return Markdown.lstrip(raw_template)

    @staticmethod
    def email_is_rejected(email) -> str:
        raw_template = f"""
        # QUESTION
        
        Analyze the provided `EMAIL` below. Respond with exactly one word: "True" or "False". 
        
        Respond "True" if at least one of these conditions is met:
        - The sender is 'mailer-daemon'
        - The sender is 'Mail Delivery Subsystem'
        - The email body contains the phrase 'recipient address rejected'
        - The email body contains the phrase 'Message blocked'
        
        Otherwise, respond "False". Do not include any punctuation, explanations, or other text.
        
        ---
        
        # EMAIL
        
        {email}
        """
        return Markdown.lstrip(raw_template)

    @staticmethod
    def rules_is_followed(rules: str, text: str) -> str:
        raw_template = f"""
        # QUESTION
        
        Analyze the provided `TEXT` below. Respond with exactly one word: "True" or "False". 
        
        Respond "True" if all of the `RULES` were followed. Otherwise, respond "False". 
        Do not include any punctuation, explanations, or other text.
        
        ---
        
        # RULES
        
        ```text
        {rules}
        ```
        
        ---
        
        # TEXT
        
        ```text
        {text}
        ```
        """

        return Markdown.lstrip(raw_template)


class Templates:
    agents = AgentTemplates()
    utils = Utils()
    markdown = Markdown()
    true_or_false = TrueOrFalseTemplates()
