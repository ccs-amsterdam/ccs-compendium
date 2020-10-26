def document_readme() -> str:
    actions = list(get_actions())
    md = "# Data processing scripts"
    md += "\n\nThis folder contains the following scripts:\n\n"
    for action in actions:
        inputs =  ",".join(f"[{f.name}]({f})" for f in action.inputs)
        targets = ",".join(f"[{f.name}]({f})" for f in action.targets)
        md += f"- [{action.file.name}](action.file): [{inputs} -> {targets}]  \n  {action.headers.get('DESCRIPTION')}  \n  \n"
    return md


def document_process() -> bytes:
    actions = list(get_actions())
    nodes, nodemap, edges = [], {}, []

    def get_node(file):
        file = file.absolute()
        if contained_in(DATA_ENCRYPTED, file):
            shape = "box3d"
            file = file.relative_to(DATA)
        if contained_in(DATA, file):
            shape = "note"
            file = file.relative_to(DATA)
        elif contained_in(SRC_PROCESSING, file):
            shape = "cds"
            file = file.relative_to(SRC_PROCESSING)
        elif contained_in(SRC_ANALYSIS, file):
            shape = "component"
            file = file.relative_to(SRC_ANALYSIS)

        if file not in nodemap:
            name = f"n_{len(nodemap)}"
            nodemap[file] = name
            label = str(file).replace("/", "/\\n")
            nodes.append(f'\n{name} [label="{label}", shape="{shape}"];')
        return nodemap[file]

    for inf in get_files(DATA_ENCRYPTED, ".gpg"):
        outf = DATA_PRIVATE/inf.stem
        node = get_node(inf)
        node2 = get_node(outf)
        edges.append(f'\n{node} -> {node2};')

    for i, action in enumerate(actions):
        node = get_node(action.file)
        for f in action.inputs:
            node2 = get_node(f)
            edges.append(f'\n{node2} -> {node};')
        for f in action.targets:
            node2 = get_node(f)
            edges.append(f'\n{node} -> {node2};')
    nodes = "\n".join(nodes)
    edges = "\n".join(edges)
    dot = f'digraph G {{graph [rankdir="LR"]; \n{nodes}\n\n{edges}\n}}\n'
    return pipe(["dot", "-T", "png"], dot.encode("utf-8"))


def do_document(args):
    filename = args.filename or {"readme": "README.md", "process": "process.png"}[args.what]
    file = Path.cwd()/filename
    if file.exists() and not args.overwrite:
        answer = input(f"File {file} exists, overwrite? [y/N] ")
        answer = answer.lower()[:1]
        if answer == "n":
            return
        elif answer not in ("", "y"):
            print("Could not understand answer, sorry")
            return
    if args.what == "readme":
        text = document_readme()
        with file.open(mode="w") as f:
            f.write(text)
    elif args.what == "process":
        bytes = document_process()
        with file.open(mode="wb") as f:
            f.write(bytes)


def pipe(command, input: bytes, **kargs) -> bytes:
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, **kargs)
    out, _err = proc.communicate(input)
    return out