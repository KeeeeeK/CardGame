import subprocess

diagram = subprocess.run(["fsm_draw_state_diagram", "--class", "light_github_example:Turnstile"],
                         stdout=subprocess.PIPE, text=True).stdout

print(diagram)
