import os

from black.trans import defaultdict


def get_lubm_answers():
    queries_answers = defaultdict(list)
    answers_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "lubm",
        "resources",
        "query_answers",
    )
    for i in range(1, 15):
        first_line = True
        with open(os.path.join(answers_path, f"answers_query{i}.txt")) as f:
            for line in f:
                if first_line:
                    first_line = False
                    var_names = line.strip().split()
                else:
                    var_values = line.strip().split()
                    assert len(var_names) == len(var_values)
                    queries_answers[i].append(dict(zip(var_names, var_values)))
    return queries_answers


if __name__ == "__main__":
    answers = get_lubm_answers()
    print(answers[3][0])
