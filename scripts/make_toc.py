#!/usr/bin/env python3

import os
import re
import urllib.parse

ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_toc_data() -> dict:
    toc = {}

    for path, _, files in os.walk(ROOT_FOLDER):
        recipe_name = None
        section = path.replace(ROOT_FOLDER + os.sep, "")
        for file_name in files:
            if re.search('.+\.recipe\.md$', file_name):
                
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


def save_section_tocs(toc_data: dict) -> None:
    for section_name in toc_data.keys():
        with open(f"{section_name}{os.sep}README.md", "w") as toc_file:
            print(f"# {section_name} #\n\n", file=toc_file)
            print(f"  - [..](..)\n", file=toc_file)
            
            for recipe_name, file_name in toc_data[section_name]:
                file_name = urllib.parse.quote(file_name)
                print(f"  - [{recipe_name}](./{file_name})\n", file=toc_file)
                
            print("\n", f"Агулам рэцэптаў: {len(toc_data[section_name])}\n\n", file=toc_file)


def build_toc(toc_data: dict) -> list:
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

    return readme_toc



def get_readme_content() -> tuple[list, list]:
    head, tail = [], []
    with open(os.path.join(ROOT_FOLDER, "README.md"), "r") as readme_file:
        file_content = readme_file.readlines()

    head = file_content[: file_content.index("## Змест ##\n") + 1]
    tail = file_content[file_content.index("---\n"): ]

    if head and tail:
        return (head, tail)
    else:
        raise IOError("There was no TOC in file")



if __name__ == "__main__":
    toc_data = get_toc_data()
    head, tail = get_readme_content()
    readme = head.copy()
    readme.extend(build_toc(toc_data))
    readme.extend(tail)
    save_section_tocs(toc_data)

    with open(os.path.join(ROOT_FOLDER, "README.md"), "w") as readme_file:
        readme_file.writelines(readme)

