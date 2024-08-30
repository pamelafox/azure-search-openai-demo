import json
import logging
import os
import random
import subprocess
import time

from azure.identity import AzureDeveloperCliCredential
from dotenv import load_dotenv
from locust import HttpUser, between, task


def load_azd_env():
    """Get path to current azd env file and load file using python-dotenv"""
    result = subprocess.run("azd env list -o json", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Error loading azd env")
    env_json = json.loads(result.stdout)
    env_file_path = None
    for entry in env_json:
        if entry["IsDefault"]:
            env_file_path = entry["DotEnvPath"]
    if not env_file_path:
        raise Exception("No default azd env file found")
    logging.info(f"Loading azd env from {env_file_path}")
    load_dotenv(env_file_path, override=True)


class ChatUser(HttpUser):
    wait_time = between(5, 20)

    @task
    def ask_question(self):
        load_azd_env()
        token = AzureDeveloperCliCredential().get_token(
            f"api://{os.environ['AZURE_SERVER_APP_ID']}/access_as_user",
            tenant_id=os.getenv("AZURE_AUTH_TENANT_ID", os.getenv("AZURE_TENANT_ID")),
        )

        self.client.get("/", headers={"Authorization": f"Bearer {token.token}"})
        time.sleep(5)
        self.client.post(
            "/chat",
            json={
                "messages": [
                    {
                        "content": random.choice(
                            [
                                "What is included in my Northwind Health Plus plan that is not in standard?",
                                "What does a Product Manager do?",
                                "What happens in a performance review?",
                                "Whats your whistleblower policy?",
                            ]
                        ),
                        "role": "user",
                    },
                ],
                "context": {
                    "overrides": {
                        "retrieval_mode": "hybrid",
                        "semantic_ranker": True,
                        "semantic_captions": False,
                        "top": 3,
                        "suggest_followup_questions": False,
                    },
                },
            },
        )
        time.sleep(5)
        self.client.post(
            "/chat",
            json={
                "messages": [
                    {"content": "What happens in a performance review?", "role": "user"},
                    {
                        "content": "During a performance review, employees will receive feedback on their performance over the past year, including both successes and areas for improvement. The feedback will be provided by the employee's supervisor and is intended to help the employee develop and grow in their role [employee_handbook-3.pdf]. The review is a two-way dialogue between the employee and their manager, so employees are encouraged to be honest and open during the process [employee_handbook-3.pdf]. The employee will also have the opportunity to discuss their goals and objectives for the upcoming year [employee_handbook-3.pdf]. A written summary of the performance review will be provided to the employee, which will include a rating of their performance, feedback, and goals and objectives for the upcoming year [employee_handbook-3.pdf].",
                        "role": "assistant",
                    },
                    {"content": "Does my plan cover eye exams?", "role": "user"},
                ],
                "context": {
                    "overrides": {
                        "retrieval_mode": "hybrid",
                        "semantic_ranker": True,
                        "semantic_captions": False,
                        "top": 3,
                        "suggest_followup_questions": False,
                    },
                },
            },
        )


class ChatVisionUser(HttpUser):
    wait_time = between(5, 20)

    @task
    def ask_question(self):
        self.client.get("/")
        time.sleep(5)
        self.client.post(
            "/chat/stream",
            json={
                "messages": [
                    {
                        "content": "Can you identify any correlation between oil prices and stock market trends?",
                        "role": "user",
                    }
                ],
                "context": {
                    "overrides": {
                        "top": 3,
                        "temperature": 0.3,
                        "minimum_reranker_score": 0,
                        "minimum_search_score": 0,
                        "retrieval_mode": "hybrid",
                        "semantic_ranker": True,
                        "semantic_captions": False,
                        "suggest_followup_questions": False,
                        "use_oid_security_filter": False,
                        "use_groups_security_filter": False,
                        "vector_fields": ["embedding", "imageEmbedding"],
                        "use_gpt4v": True,
                        "gpt4v_input": "textAndImages",
                    }
                },
                "session_state": None,
            },
        )
        time.sleep(5)
        self.client.post(
            "/chat/stream",
            json={
                "messages": [
                    {"content": "Compare the impact of interest rates and GDP in financial markets.", "role": "user"}
                ],
                "context": {
                    "overrides": {
                        "top": 3,
                        "temperature": 0.3,
                        "minimum_reranker_score": 0,
                        "minimum_search_score": 0,
                        "retrieval_mode": "hybrid",
                        "semantic_ranker": True,
                        "semantic_captions": False,
                        "suggest_followup_questions": False,
                        "use_oid_security_filter": False,
                        "use_groups_security_filter": False,
                        "vector_fields": ["embedding", "imageEmbedding"],
                        "use_gpt4v": True,
                        "gpt4v_input": "textAndImages",
                    }
                },
                "session_state": None,
            },
        )
