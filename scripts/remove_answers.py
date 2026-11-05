import json

if __name__ == "__main__":
    for tutor in range(7 + 1):
        if tutor < 7:
            fp_in = f"tutorials/tutorial_answers/Tutorial{tutor}-complete.ipynb"
            fp_out = f"tutorials/Tutorial{tutor}.ipynb"
        else:
            fp_in = f"tutorials/tutorial_answers/LATW-challenge-problem-complete.ipynb"
            fp_out = f"tutorials/LATW-challenge-problem.ipynb"

        # if tutor not in [3]:
        #     continue

        # Open and read the JSON file
        with open(fp_in, "r") as file:
            data = json.load(file)

        previous_cell_nothing = False
        pop_inds = []
        for i, cell in enumerate(data["cells"]):
            # nbformat allows source as one string; normalise to a list of lines
            if isinstance(cell["source"], str):
                cell["source"] = cell["source"].splitlines(keepends=True)
            remove_cell_contents = False
            for line in cell["source"]:
                if "# clear" in line.lower():
                    remove_cell_contents = True

            if remove_cell_contents:
                cell["source"] = ["\n"]
                if previous_cell_nothing:
                    pop_inds.append(i)
                previous_cell_nothing = True
            else:
                previous_cell_nothing = False

            cell["outputs"] = []

        new_cells = []

        for i in range(len(data["cells"])):
            if i not in pop_inds:
                new_cells.append(data["cells"][i])

        data["cells"] = new_cells

        ### special changes
        if tutor == 3:
            for i, cell in enumerate(data["cells"]):
                run_change = False
                for line in cell["source"]:
                    if "# special clear" in line.lower():
                        run_change = True
                if run_change:
                    for j, line in enumerate(cell["source"]):
                        line_tests = [
                            "new_point = current_point + 0.5 * np.random.randn()",
                            "new_likelihood = log_like_gauss(new_point)",
                            "delta_posterior = new_likelihood - current_likelihood  #  + (new_prior - old_prior)",
                            "accept = delta_posterior > np.log(np.random.rand())",
                            "current_point = new_point",
                            "current_likelihood = new_likelihood",
                        ]
                        for line_test in line_tests:
                            if line_test in line:
                                cell["source"][j] = "\n"

        tmp = json.dumps(data)
        with open(fp_out, "w") as file:
            file.write(tmp)
