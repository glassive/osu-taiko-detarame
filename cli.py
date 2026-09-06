from argparse import Namespace, ArgumentParser
from pathlib import Path
from detarame import OsuFile

def optional_prompts(args: Namespace) -> Namespace:
    if args.path is None:
        manual_path = input("Path to .osu file: ").strip().strip('"')
        args.path = Path(manual_path)

    print(f"Loaded {args.path}")

    if args.seed is None:
        manual_seed = input("\n[Optional] Numeric seed\n(Press Enter for a random seed): ").strip()
        if manual_seed:
            try:
                args.seed = int(manual_seed)
            except ValueError:
                raise ValueError("Seed must be an integer")
        else:
            print("Using random seed")

    if args.weight is None:
        raw_weight = input("\n[Optional] Don weight from 0 to 1\n(Press Enter for 0.5): ").strip()
        if raw_weight:
            try:
                args.weight = float(raw_weight)
            except ValueError:
                raise ValueError("Weight must be a number")
        else:
            default_weight = 0.5
            print(f"Using default weight ({default_weight})")
            args.weight = default_weight

    if not 0 <= args.weight <= 1:
        raise ValueError("Weight must be between 0 and 1")

    return args


def main() -> int:
    # -------------------- parse args --------------------
    parser = ArgumentParser(
        description="Randomize osu!taiko hit objects in an .osu beatmap v14 file."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="Path to the .osu file",
    )
    parser.add_argument("--seed", type=int)
    parser.add_argument("--weight", type=float)

    args = parser.parse_args()

    if args.weight is not None and not 0 <= args.weight <= 1:
        parser.error("--weight must be between 0 and 1")


    # ------------- generate file and return -------------
    try:
        args = optional_prompts(args)

        osu_file = OsuFile(args.path)
        osu_file.detarame(args.seed, args.weight)
        osu_file.export()

    except (Exception) as e:
        print(f"Error: {e}")
        input("\nPress Enter to exit...")
        return 1

    print(f"\nSuccess! Seed: {osu_file.seed}")
    input("\nPress Enter to exit...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())