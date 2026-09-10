"""Session 1: see how a request moves through a fixed sequence of steps."""


def understand_request(request):
    return request.lower()


def choose_action(request):
    if "delete" in request:
        return "Ask a human for approval"
    return "Continue with the safe workflow"


request = understand_request("Delete an old user account")
action = choose_action(request)
print(action)
