from utilities import get_control_map_color, get_scaled_control_map_color

# resp = get_control_map_color('T001-02', (0,0))
# if resp:
#     print(resp)

resp = get_scaled_control_map_color('T001-02', (0,0))
if resp:
    print(resp)