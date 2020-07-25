def separate_ligands(file_path):
    try:
        file = open(file_path).read()
    except TypeError:
        print("No input file!")
        return 1, None
    except FileNotFoundError:
        print("No such file: %s" % file_path)
        return 2, None
    parts = file.split(' } \n} \n')

    intro = parts[0].split("} \n\n")[0]
    intro = "".join([intro, "} \n"])

    parts[0] = parts[0].split("} \n\n")[1]

    titles_file = []

    for i in range(len(parts) - 1):
        title0 = parts[i].split(" :::")[1].split('\n')[1].rstrip()
        title1 = title0.split(":")[-1]
        titles_file.append(title1)

        out = open("ligands/%s.mae" % title1, 'w')
        out.write(intro)
        out.write(parts[i])
        out.write(" } \n} \n")
        out.close()
    return 0, titles_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file with multiple ligands")
    args = parser.parse_args()

    separate_ligands(args.input)