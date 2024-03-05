import random
import time

from locust import HttpUser, between, task


class ChatUser(HttpUser):
    wait_time = between(5, 20)

    @task
    def ask_question(self):
        self.client.get("/")
        time.sleep(5)
        self.client.post(
            "/chat",
            json={
                "messages": [
                    {
                        "content": random.choice(
                            [
                                "What does Pamela do?",
                                "What are good sleep strategies?",
                                "What Python frameworks can be deployed on Azure?",
                                "Is it possible to mock the OpenAI SDK?",
                                "Did Pamela graduate from USC?",
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
                    {"content": "What does Pamela do?", "role": "user"},
                    {
                        "content": "Pamela is currently a Principal Cloud Advocate at Microsoft, focusing on the ways that developers can use Python with Azure services[pamelafox.html]. In the past, she has worked as a lecturer at UC Berkeley, worked for Khan Academy, started up the engineering team at Woebot, attended a Tibetan Buddhism retreat, founded the GirlDevelopIt SF chapter, written code for Coursera, and worked in developer relations for Google [pamelafox.html]",
                        "role": "assistant",
                    },
                    {"content": "Did Pamela graduate from USC?", "role": "user"},
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
