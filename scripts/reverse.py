import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument("--reverse_list", default="ACC.FEM.SING,ACC.MASC.SING,DAT.FEM.SING,DAT.MASC.SING,NOM.FEM.SING,NOM.MASC.SING")

    args = parser.parse_args()

    reverse_list = args.reverse_list.split(',')

    reversed_data = []
    with open(args.input) as inf:
        data = json.load(inf)
        for example in data:
            if example["rule"] in reverse_list:
                reversed_example = {}
                for key, value in example.items():
                    if "src " in key:
                        if key == "src pronoun":
                            reversed_example["expected"] = value
                        else:
                            reversed_example[key.replace("src ", "ref ")] = value
                    elif "ref " in key:
                        reversed_example[key.replace("ref ", "src ")] = value
                    else:
                        if "expected" == key:
                            reversed_example["src pronoun"] = value
                        else:
                            reversed_example[key] = value
                reversed_data.append(reversed_example)

    with open(args.output, 'w') as outf:
        json.dump(reversed_data, outf, indent=2, ensure_ascii=False)
            
