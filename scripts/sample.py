import argparse
import json
import os

def clean_example(input):
    out = {}
    for key, item in input.items():
        if key == "ref pronoun":
            if item == "nôtre":
                if "FEM" in input["rule"] and "SING" in input["rule"]:
                    if "la nôtre" in input["ref segment"]:
                        out["expected"] = "la nôtre"
                    else:
                        return None
                elif "MASC" in input["rule"] and "SING" in input["rule"]:
                    if "le nôtre" in input["ref segment"]:
                        out["expected"] = "le nôtre"
                    else:
                        return None
            elif item == "nôtres":
                if "les nôtres" in input["ref segment"]:
                    out["expected"] = "les nôtres"
                else:
                    return None
            elif item == "vôtre":
                if "FEM" in input["rule"] and "SING" in input["rule"]:
                    if "la vôtre" in input["ref segment"]:
                        out["expected"] = "la vôtre"
                    else:
                        return None
                elif "MASC" in input["rule"] and "SING" in input["rule"]:
                    if "le vôtre" in input["ref segment"]:
                        out["expected"] = "le vôtre"
                    else:
                        return None
            elif item == "vôtres":
                if "les vôtres" in input["ref segment"]:
                    out["expected"] = "les vôtres"
                else:
                    return None
            elif item == "leur":
                if "FEM" in input["rule"] and "SING" in input["rule"]:
                    if "la leur" in input["ref segment"]:
                        out["expected"] = "la leur"
                    else:
                        return None
                elif "MASC" in input["rule"] and "SING" in input["rule"]:
                    if "le leur" in input["ref segment"]:
                        out["expected"] = "le leur"
                    else:
                        return None
            elif item == "leurs":
                if "les leurs" in input["ref segment"]:
                    out["expected"] = "les leurs"
                else:
                    return None
            else:
                out["expected"] = item
        elif key == "document id":
            item = item.replace("/export/fs05/rwicks/MultiPro/", "")
            out[key] = item
        elif key != "errors":
            out[key] = item
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True)
    parser.add_argument("--minimum_test_size", type=int, default=100)
    parser.add_argument("--maximum_test_size", type=int, default=5000)
    parser.add_argument("--ratio", type=str, default="1:1:5")
    parser.add_argument("--output_dir", type=str, default="merge")
    parser.add_argument("--rule_name", nargs='*', default=None)

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    ratios = [int(_) for _ in args.ratio.split(':')]

    with open(args.input_path) as infile:
        input_data = json.load(infile)
    
    examples = {}
    for example in input_data:
        if "rule" not in example:
            print(example)
        if args.rule_name is None or example["rule"] in args.rule_name:
            if example["rule"] not in examples:
                examples[example["rule"]] = []
            cleaned_example = clean_example(example)
            if cleaned_example is not None:
                examples[example["rule"]].append(cleaned_example)

    samples = {}
    for rule in examples:
        samples[rule] = {
            "test": [],
            "devtest": [],
            "dev": []
        }
        items = sorted(examples[rule], key=lambda kv: int(kv["document id"].split('/')[1]), reverse=True)
        size = len(items)
        print(f"Found {size} items for rule {rule}")
        if size <= args.minimum_test_size:
            samples[rule]["test"] = items
            print(f"Using all itmes for test. {size} total.")
        else:
            if int((size*sum(ratios))/ratios[-1]) < args.minimum_test_size:
                test_size = args.minimum_test_size
            else:
                test_size = int(min((size*ratios[-1])/sum(ratios), args.maximum_test_size))

            print(f"Using {test_size} items for test")
            samples[rule]["test"] = items[:test_size]
            items = items[test_size:]

            devtest_size = int((test_size * ratios[1]) / ratios[2])
            samples[rule]["devtest"] = items[:devtest_size]
            items = items[devtest_size:]
            print(f"Using {devtest_size} items for devtest")

            dev_size = int((test_size * ratios[0]) / ratios[2])
            samples[rule]["dev"] = items[:dev_size]
            print(f"Using {dev_size} items for dev")

        prefix = os.path.join(args.output_dir, rule)
        with open(f"{prefix}.test.json", 'w') as outfile:
            json.dump(samples[rule]["test"], outfile, ensure_ascii=False, indent=2)

        with open(f"{prefix}.devtest.json", 'w') as outfile:
            json.dump(samples[rule]["devtest"], outfile, ensure_ascii=False, indent=2)

        with open(f"{prefix}.dev.json", 'w') as outfile:
            json.dump(samples[rule]["dev"], outfile, ensure_ascii=False, indent=2)