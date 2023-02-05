#!/usr/bin/env python3

import os
import re
import urllib.parse


def get_toc_data():
    toc = {}

    for path, dirs, files in os.walk("."):
        recipe_name = None
        secion = None
        for file_name in files:
            if re.search('.+\.recipe\.md$', file_name):

                section = path.replace("./", "")
                with open(os.path.join(path, file_name)) as source_file:
                    for line in source_file.readlines():
                        if "# " in line:
                            recipe_name = line.replace("# ", "").strip()
                            break

                data = (recipe_name, file_name)
                if section in toc:
                    toc[section].append(data)
                else:
                    toc[section] = [data]


    sections = list(toc.keys())
    sections.sort()

    final_toc = {}
    for key in sections:
        final_toc[key] = toc[key]
        final_toc[key].sort()

    return final_toc


def get_readme_content():
    head, tail = [], []
    status = 0
    with open("README.md", "r") as readme_file:
        for line in readme_file.readlines():
            if status == 0:
                head.append(line)
                if line == "## Змест ##\n":
                    status = 1
            elif status == 1:
                if line == "---\n":
                    tail.append(line)
                    status = 2
            else:
                tail.append(line)

            if line == "## Змест ##\n":
                status = 1

    if head and tail:
        return (head, tail)
    else:
        raise IOError("There was no TOC in file")



if __name__ == "__main__":
    toc_data = get_toc_data()
    head, tail = get_readme_content()
    readme = head.copy()
    readme_toc = []
    total_count = 0
    for key in toc_data.keys():
        path = urllib.parse.quote(key)
        section_count = len(toc_data[key])
        readme_toc.append(f"- [{key}](./{path}) - {section_count}\n")
        total_count += section_count
        for recipe_name, file_name in toc_data[key]:
            recipe_name.replace("[", "\\" + "[")
            recipe_name.replace("]", "\\" +"]")
            readme_toc.append(f"  - [{recipe_name}]({path}/{urllib.parse.quote(file_name)})\n")

    readme_toc.extend(("\n", f"Агулам рэцэптаў: {total_count}\n\n"))
    readme.extend(readme_toc)
    readme.extend(tail)

    with open("README.md", "w") as readme_file:
        readme_file.writelines(readme)
        readme_file.write("\n")

