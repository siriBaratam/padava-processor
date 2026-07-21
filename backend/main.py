from scout.scout import run_scout
from accountant import run_accountant
# from strategist import run_strategist
# from allocator import run_allocator
# # from navigator import run_navigator


def main():

    print("=" * 60)
    print("Running Scout Agent...")
    print("=" * 60)

    scout_output = run_scout()

    print(scout_output)

    print("\n")

    print("=" * 60)
    print("Running Accountant Agent...")
    print("=" * 60)

    accountant_output = run_accountant(scout_output)

    print(accountant_output)

    print("\n")
    print("=" * 60)
    print("Running Strategist Agent...")
    print("=" * 60)
    # strategist_output = run_strategist(
    # scout_output,
    # accountant_output
    # )
    # print(strategist_output)
    # print("\n")
    # print("=" * 60)
    # print("Running Allocator Agent...")
    # print("=" * 60)

    # allocator_output = run_allocator(
    #     scout_output,
    #     accountant_output,
    #     strategist_output
    # )

    # print(allocator_output)
    # print("\n")
    # # navigator_output = run_navigator(
    # #     allocator_output
    # # )


if __name__ == "__main__":
    main()