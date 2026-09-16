import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PARAMETERS
# ============================================================

START_ALTITUDE = 700.0

# Values based on the paper
GLIDE_RATIO = 3.25
FORWARD_SPEED = 6.2

# Vertical descent velocity from glide ratio
DESCENT_SPEED = FORWARD_SPEED / GLIDE_RATIO

# Simulation timestep
DT = 0.1

# Maximum bank angle
MAX_BANK_ANGLE = np.radians(35)

# How quickly the parafoil changes bank angle
BANK_RESPONSE = 0.8

# Maximum turn rate
#
# This is derived from bank angle and speed rather than
# arbitrarily rotating the heading.
GRAVITY = 9.81

# Target
TARGET_X = 0.0
TARGET_Y = 0.0
TARGET_Z = 0.0


# ============================================================
# RANDOM START POSITION
# ============================================================

rng = np.random.default_rng()

# Maximum theoretical horizontal range
MAX_RANGE = START_ALTITUDE * GLIDE_RATIO

# Keep starting point comfortably within range
START_RADIUS = 0.7 * MAX_RANGE

r = START_RADIUS * np.sqrt(
    rng.random()
)

angle = rng.uniform(
    0,
    2 * np.pi
)

start_x = r * np.cos(angle)
start_y = r * np.sin(angle)


# ============================================================
# STATE
# ============================================================
#
# x       = horizontal X position
# y       = horizontal Y position
# z       = altitude
#
# heading = direction of travel
# bank    = roll/bank angle
#
# ============================================================

x = start_x
y = start_y
z = START_ALTITUDE

# Initially point toward target
heading = np.arctan2(
    -start_y,
    -start_x
)

bank = 0.0


# ============================================================
# GUIDANCE ALGORITHM
# ============================================================

def guidance_algorithm(x, y, z, heading):

    dx = TARGET_X - x
    dy = TARGET_Y - y

    distance = np.hypot(
        dx,
        dy
    )

    # Desired direction toward target
    desired_heading = np.arctan2(
        dy,
        dx
    )

    # Difference between current and desired heading
    heading_error = np.arctan2(
        np.sin(desired_heading - heading),
        np.cos(desired_heading - heading)
    )

    # --------------------------------------------------------
    # Convert heading error into desired bank
    # --------------------------------------------------------

    # Small heading error -> small bank
    # Large heading error -> larger bank

    K_BANK = 1.5

    desired_bank = (
        K_BANK * heading_error
    )

    desired_bank = np.clip(
        desired_bank,
        -MAX_BANK_ANGLE,
        MAX_BANK_ANGLE
    )

    # --------------------------------------------------------
    # Near the target, reduce bank.
    # --------------------------------------------------------

    if distance < 150:

        desired_bank *= (
            distance / 150
        )

    return desired_bank


# ============================================================
# PHYSICS UPDATE
# ============================================================

def physics_update(
    x,
    y,
    z,
    heading,
    bank,
    desired_bank
):
    # --------------------------------------------------------
    # Bank dynamics
    # --------------------------------------------------------

    bank_error = (
        desired_bank - bank
    )

    bank_change = (
        BANK_RESPONSE
        * bank_error
        * DT
    )

    bank += bank_change

    bank = np.clip(
        bank,
        -MAX_BANK_ANGLE,
        MAX_BANK_ANGLE
    )

    # --------------------------------------------------------
    # Turning physics
    #
    # For a banked glider:
    #
    # turn_rate ≈ g*tan(bank)/V
    # --------------------------------------------------------

    turn_rate = (
        GRAVITY
        * np.tan(bank)
        / FORWARD_SPEED
    )

    # Prevent unrealistically large turn rates
    turn_rate = np.clip(
        turn_rate,
        -np.radians(30),
        np.radians(30)
    )

    # Update heading
    heading += (
        turn_rate * DT
    )

    # --------------------------------------------------------
    # Horizontal movement
    # --------------------------------------------------------

    x += (
        FORWARD_SPEED
        * np.cos(heading)
        * DT
    )

    y += (
        FORWARD_SPEED
        * np.sin(heading)
        * DT
    )

    # --------------------------------------------------------
    # Vertical movement
    # --------------------------------------------------------

    z -= (
        DESCENT_SPEED
        * DT
    )

    if z < 0:
        z = 0

    return (
        x,
        y,
        z,
        heading,
        bank
    )


# ============================================================
# SIMULATION
# ============================================================

trajectory = []

time = 0.0
MAX_TIME = 600.0

while (
    z > 0
    and time < MAX_TIME
):

    # --------------------------------------------------------
    # OUR GUIDANCE
    # --------------------------------------------------------

    desired_bank = guidance_algorithm(
        x,
        y,
        z,
        heading
    )

    # --------------------------------------------------------
    # PHYSICS
    # --------------------------------------------------------

    (
        x,
        y,
        z,
        heading,
        bank
    ) = physics_update(
        x,
        y,
        z,
        heading,
        bank,
        desired_bank
    )

    # Save trajectory
    trajectory.append([
        x,
        y,
        z
    ])

    # --------------------------------------------------------
    # Check target
    # --------------------------------------------------------

    distance = np.hypot(
        x,
        y
    )

    if distance < 5 and z < 10:

        print("TARGET REACHED!")

        x = 0
        y = 0
        z = 0

        trajectory.append([
            x,
            y,
            z
        ])

        break

    time += DT


# ============================================================
# CONVERT TO ARRAY
# ============================================================

trajectory = np.array(
    trajectory
)

x_path = trajectory[:, 0]
y_path = trajectory[:, 1]
z_path = trajectory[:, 2]


# ============================================================
# RESULTS
# ============================================================

final_error = np.hypot(
    x_path[-1],
    y_path[-1]
)

initial_distance = np.hypot(
    start_x,
    start_y
)

print()
print("======================================")
print("PARAFOIL SIMULATION")
print("======================================")

print(
    f"Start position: "
    f"({start_x:.1f}, "
    f"{start_y:.1f}, "
    f"{START_ALTITUDE:.1f})"
)

print(
    f"Initial horizontal distance: "
    f"{initial_distance:.1f} m"
)

print(
    f"Final position: "
    f"({x_path[-1]:.1f}, "
    f"{y_path[-1]:.1f}, "
    f"{z_path[-1]:.1f})"
)

print(
    f"Final horizontal error: "
    f"{final_error:.1f} m"
)

print(
    f"Flight time: "
    f"{time:.1f} s"
)


# ============================================================
# 3D PLOT
# ============================================================

fig = plt.figure(
    figsize=(11, 8)
)

ax = fig.add_subplot(
    111,
    projection="3d"
)

# Parafoil trajectory
ax.plot(
    x_path,
    y_path,
    z_path,
    linewidth=2,
    label="Parafoil path"
)

# Start
ax.scatter(
    start_x,
    start_y,
    START_ALTITUDE,
    s=80,
    label="Start"
)

# Target
ax.scatter(
    0,
    0,
    0,
    s=150,
    marker="*",
    label="Target"
)

ax.set_xlabel(
    "X position (m)"
)

ax.set_ylabel(
    "Y position (m)"
)

ax.set_zlabel(
    "Altitude (m)"
)

ax.set_title(
    "Parafoil Path Finding"
)

ax.legend()

plt.tight_layout()

plt.show()