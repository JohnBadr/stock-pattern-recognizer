time_forward = input("How many days ahead do you want to predict? (1-30d): ")
time_forward=int(time_forward[:-1]) if time_forward.endswith('d') else int(time_forward)

time_forward=days_forward(time_forward)
days = parse_time_input(time_input)