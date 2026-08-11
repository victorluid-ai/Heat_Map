#!/usr/bin/env python3
"""Interactive camera calibration: map camera pixels to floor plan coordinates."""
import argparse
import sys
import numpy as np
import cv2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

INSTRUCTIONS = """
Camera Calibration Tool
=======================
Click 4 corresponding points on the camera frame (left) and floor plan (right).
Press 'r' to reset, 'q' to quit without saving, 's' to save calibration.
"""


def main():
    parser = argparse.ArgumentParser(description="Calibrate camera to floor plan")
    parser.add_argument("--source", required=True, help="Camera source (0, RTSP URL, or file)")
    parser.add_argument("--floor-plan", default="config/floor_plan/store_layout.png")
    parser.add_argument("--output", default="config/calibration.yaml")
    args = parser.parse_args()

    print(INSTRUCTIONS)
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"Cannot open source: {args.source}")
        sys.exit(1)

    ret, cam_frame = cap.read()
    cap.release()
    if not ret:
        print("Could not read frame from source.")
        sys.exit(1)

    floor = cv2.imread(args.floor_plan)
    if floor is None:
        print(f"Floor plan not found: {args.floor_plan}")
        sys.exit(1)

    h = max(cam_frame.shape[0], floor.shape[0])
    cam_resized = cv2.resize(cam_frame, (int(cam_frame.shape[1] * h / cam_frame.shape[0]), h))
    floor_resized = cv2.resize(floor, (int(floor.shape[1] * h / floor.shape[0]), h))
    combined = np.hstack([cam_resized, floor_resized])
    offset_x = cam_resized.shape[1]

    cam_pts, floor_pts = [], []
    colours = [(0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]

    def on_click(event, x, y, flags, _):
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if x < offset_x and len(cam_pts) < 4:
            cam_pts.append((x, y))
            cv2.circle(combined, (x, y), 6, colours[len(cam_pts) - 1], -1)
        elif x >= offset_x and len(floor_pts) < 4:
            floor_pts.append((x - offset_x, y))
            cv2.circle(combined, (x, y), 6, colours[len(floor_pts) - 1], -1)
        cv2.imshow("Calibration", combined)

    cv2.imshow("Calibration", combined)
    cv2.setMouseCallback("Calibration", on_click)

    while True:
        key = cv2.waitKey(50) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r"):
            cam_pts.clear(); floor_pts.clear()
            combined = np.hstack([cam_resized.copy(), floor_resized.copy()])
            cv2.imshow("Calibration", combined)
        if key == ord("s") and len(cam_pts) == 4 and len(floor_pts) == 4:
            import yaml
            data = {"cam_points": cam_pts, "floor_points": floor_pts}
            with open(args.output, "w") as f:
                yaml.dump(data, f)
            print(f"Calibration saved to {args.output}")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
