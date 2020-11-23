# `ccs-compendium`: Utility for building a compendium for reprocible science 

`compendium` is a python module that helps you build a *compendium* containing the data and scripts needed to reproduce your article, report, or analysis.
Although the module is written in python and uses the python [doit](https://pydoit.org/) tool, it also works if you use R or other tools for your analysis. 
Please see *[website]* for more information. 

# Installation

Use pip to install:

```
pip install ccs-compendium
```

Note: If you prefer to install it in a virtual directory, 
we recommend first creating the github repository for your project, cloning that repository, and installing the environment into that folder directly. 

## Usage

After installing, you can call `compendium` from the command line:

```
compendium COMMAND
```

Where `COMMAND` can be `init`, `check`, or `encrypt` (with `document` coming soon!). 
The next sections will explain these commands one by one. 


## Getting help 

To get help on possible commands, use the `--help` flag on the compendium command or any of the actions:

```
compendium --help
compendium init --help
```

# `init`: Create a new compendium

Probably, the first step is to create a new compendium. 
The init command will interactively create a new compendium in an existing or new folder. 
You can add extra options in the command if desired (such as `--github`), but if you leave those out it will ask you what to do,
so no need to memory any commands. 

`init` will perform these steps, asking before each step and skipping any steps already taken:

1. Create a folder (if needed) and link it to a github repository
2. Create the `data` and `src` folders
3. Add the license, `dodo.py`, and gitignore files
4. Add a python environment (if needed).
5. Write the compendium configuration to a file `.compendium.cfg`

If you call init from within an existing compendium project, it will recognize that file and only ask for missing items. 
If anything goes wrong (e.g., you mistyped the github repository name), *don't panic*, you can just abort and call init again, and it will pick up where it ended.

## The `dodo.py` file

The compendium uses the `doit` tool to automate the installation and reproduction steps. 
This tool uses a file called `dodo.py` to define the various tasks.
By default, the `dodo.py` file installed in the compendium will:

1. Install Python and/or R (if needed)
2. Decrypt private files (if needed and if a password is supplied)
3. Run all processing scripts

To understand your processing scripts, they should contain a header with their input(s) and output(s) so `doit` knows in which order the scripts should be called.
For more information, see **[WEBSITE]**

## `init` from a new or existing github repository

The easiest way to get started is by *cloning* a github repository. 
If this is a new project, we would recommend you to make a github repository first, 
and then running `init` with the name of that new repository.

The repository will be the first question if used interactively, but you can also specify it on the command line:

```
compendium init --github userame/repositor
# for example:
compendium init --github ccs-amsterdam/compendium-example
```

## 2. `init` in an existing folder

If you already have a project folder that you want to turn into a *compendium*, you can also call init on that folder. 

```
compendium init myfolder
```

If you are in that folder, you can also simply call init and it will ask you to use that folder as your project folder:

```
cd myfolder
compendium init
```

If the folder isn't already a github repository, `init` will ask you whether you want to link it to a repository. 

# `encrypt`: Encrypt private files

In many cases, we are not free to share all our data openly, either because it's copyrighted, proprietary, or contains privacy-sensitive details. 
In such cases, you can decide to share the encrypted files, and share the password on request. 
The benefit of this approach is that the data are stored together with the analysis scripts, making it easier to recombine the two.
Of course, encryption is never 100% safe, so depending on how sensitive your data are you may choose not to share them at all. 

Note that regardless of whether you encrypt the private data or not, if at all possible you should publish an anonymized or aggregated version of the data in the `data/intermediate` folder, so people can reproduce as much as possible of your processing and analysis without access to the private data. See **[WEBSITE]** for more information. 

To encrypt your files, call

```
compendium encrypt --password PASSWORD
```

If you omit the password, it will be asked on the command line. 
This will encrypt all files in the `raw-private` folder to the `raw-private-encrypted` folder.

# `check`: Check the consistency of the compendium

You can run `check` to check the consistency of the compendium:

```
compendium check
```

This checks whether the right folders and template files are there.
Moreover, it will check whether the input of each analysis or processing script is included, either as data or as the output of another script. 
