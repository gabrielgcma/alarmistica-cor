from locust import HttpUser, task, between


class SendLoginUser(HttpUser):
    wait_time = between(0.1, 0.3)

    @task
    def send_login(self):
        self.client.post(
            url="http://127.0.0.1:8000/logar/",
            json={"IP": "10.10.10.1", "CMD": "show ip int brief", "REGEX": "(.)"},
        )
