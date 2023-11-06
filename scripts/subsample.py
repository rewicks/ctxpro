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
    parser.add_argument("--maximum_size", type=int, default=5000)
    parser.add_argument("--output_path", type=str, default="merge")
    parser.add_argument("--rule_name", nargs='*', default=None)

    args = parser.parse_args()

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

    size = 0

    output = []
    for rule in examples:
        items = sorted(examples[rule], key=lambda kv: int(kv["document id"].split('/')[1]), reverse=True)
        print(f"Found {len(items)} items for rule {rule}")
        out_items = items[:args.maximum_size]
        output += out_items

    print(f"Subsampled dataset size is {len(output)}")
    with open(args.output_path, 'w') as outfile:
        json.dump(output, outfile, ensure_ascii=False, indent=2)
